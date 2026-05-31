from __future__ import annotations

import argparse
import json
from pathlib import Path

from cst_io import read_table, validate_farfield, validate_nearfield, validate_pair


def print_report(title: str, report) -> None:
    print(f"\n[{title}]")
    print(f"ok: {report.ok}")
    if report.summary:
        print("summary:")
        print(json.dumps(report.summary, ensure_ascii=False, indent=2))
    if report.errors:
        print("errors:")
        for item in report.errors:
            print(f"- {item}")
    if report.warnings:
        print("warnings:")
        for item in report.warnings:
            print(f"- {item}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CST near-field/far-field CSV exports for CS-202614 workflow.")
    parser.add_argument("--nearfield", required=True, help="Path to CST near-field export CSV/XLSX.")
    parser.add_argument("--farfield", help="Optional path to CST far-field truth CSV/XLSX.")
    parser.add_argument("--json-out", help="Optional path to write validation summary JSON.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    if not nearfield_path.exists():
        raise FileNotFoundError(nearfield_path)
    nearfield = read_table(nearfield_path)
    nf_report = validate_nearfield(nearfield)
    print_report("nearfield", nf_report)

    reports = {"nearfield": nf_report}
    exit_ok = nf_report.ok

    if args.farfield:
        farfield_path = Path(args.farfield)
        if not farfield_path.exists():
            raise FileNotFoundError(farfield_path)
        farfield = read_table(farfield_path)
        ff_report = validate_farfield(farfield)
        pair_report = validate_pair(nearfield, farfield) if nf_report.ok and ff_report.ok else None
        print_report("farfield", ff_report)
        reports["farfield"] = ff_report
        exit_ok = exit_ok and ff_report.ok
        if pair_report is not None:
            print_report("nearfield/farfield pair", pair_report)
            reports["pair"] = pair_report
            exit_ok = exit_ok and pair_report.ok

    if args.json_out:
        payload = {
            key: {
                "ok": report.ok,
                "errors": report.errors,
                "warnings": report.warnings,
                "summary": report.summary,
            }
            for key, report in reports.items()
            if report is not None
        }
        Path(args.json_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0 if exit_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
