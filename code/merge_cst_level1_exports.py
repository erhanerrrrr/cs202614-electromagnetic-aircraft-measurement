from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from cst_io import read_table, validate_farfield, validate_nearfield, validate_pair


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "cst_exports" / "level1"
DEFAULT_REPORT_DIR = ROOT / "outputs" / "cst_level1_merge_report"


def resolve_path(path_text: object, base_dir: Path) -> Path | None:
    text = str(path_text).strip()
    if not text or text.lower() == "nan":
        return None
    path = Path(text)
    if path.is_absolute():
        return path
    return base_dir / path


def file_status(path: Path | None) -> str:
    if path is None:
        return "not_listed"
    return "exists" if path.exists() else "missing"


def read_optional_table(path: Path | None) -> tuple[pd.DataFrame | None, str]:
    if path is None:
        return None, "not_listed"
    if not path.exists():
        return None, "missing"
    try:
        return read_table(path), "read"
    except Exception as exc:  # noqa: BLE001
        return None, f"read_error: {exc}"


def report_validation(prefix: str, report) -> dict[str, object]:
    return {
        f"{prefix}_ok": bool(report.ok),
        f"{prefix}_errors": " | ".join(report.errors),
        f"{prefix}_warnings": " | ".join(report.warnings),
    }


def count_rows(df: pd.DataFrame | None, sample_id: str, frequency_hz: float) -> int:
    if df is None or df.empty or "sample_id" not in df.columns or "frequency_hz" not in df.columns:
        return 0
    sample = df["sample_id"].astype(str).str.strip()
    freq = pd.to_numeric(df["frequency_hz"], errors="coerce").astype(float)
    return int(((sample == sample_id) & (freq == float(frequency_hz))).sum())


def command_path(path: Path | None, base_dir: Path) -> str:
    if path is None:
        return ""
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        return str(path)


def analyze_case(row: pd.Series, base_dir: Path) -> tuple[pd.DataFrame | None, pd.DataFrame | None, dict[str, object]]:
    sample_id = str(row["sample_id"]).strip()
    frequency_hz = float(pd.to_numeric(row["frequency_hz"], errors="raise"))
    expected_nearfield_rows = int(pd.to_numeric(row["expected_nearfield_rows"], errors="raise"))
    expected_farfield_rows = int(pd.to_numeric(row["expected_farfield_rows"], errors="raise"))

    nearfield_path = resolve_path(row["nearfield_export"], base_dir)
    farfield_path = resolve_path(row["farfield_export"], base_dir)
    phase_nearfield_path = resolve_path(row.get("phase_format_nearfield_export", ""), base_dir)
    phase_farfield_path = resolve_path(row.get("phase_format_farfield_export", ""), base_dir)

    nearfield, nearfield_status = read_optional_table(nearfield_path)
    farfield, farfield_status = read_optional_table(farfield_path)

    summary: dict[str, object] = {
        "sample_id": sample_id,
        "priority": str(row.get("priority", "")).strip(),
        "source_config": str(row.get("source_config", "")).strip(),
        "frequency_hz": int(round(frequency_hz)),
        "nearfield_path": command_path(nearfield_path, base_dir),
        "farfield_path": command_path(farfield_path, base_dir),
        "phase_nearfield_path": command_path(phase_nearfield_path, base_dir),
        "phase_farfield_path": command_path(phase_farfield_path, base_dir),
        "nearfield_file_status": nearfield_status,
        "farfield_file_status": farfield_status,
        "phase_nearfield_file_status": file_status(phase_nearfield_path),
        "phase_farfield_file_status": file_status(phase_farfield_path),
        "expected_nearfield_rows": expected_nearfield_rows,
        "expected_farfield_rows": expected_farfield_rows,
    }

    nearfield_ok = False
    farfield_ok = False
    if nearfield is not None:
        nf_report = validate_nearfield(nearfield)
        summary.update(report_validation("nearfield", nf_report))
        nearfield_ok = nf_report.ok
    else:
        summary.update({"nearfield_ok": False, "nearfield_errors": nearfield_status, "nearfield_warnings": ""})

    if farfield is not None:
        ff_report = validate_farfield(farfield)
        summary.update(report_validation("farfield", ff_report))
        farfield_ok = ff_report.ok
    else:
        summary.update({"farfield_ok": False, "farfield_errors": farfield_status, "farfield_warnings": ""})

    if nearfield is not None and farfield is not None and nearfield_ok and farfield_ok:
        pair_report = validate_pair(nearfield, farfield)
        summary.update(report_validation("pair", pair_report))
    else:
        summary.update({"pair_ok": False, "pair_errors": "nearfield/farfield not both valid", "pair_warnings": ""})

    nearfield_rows = count_rows(nearfield, sample_id, frequency_hz)
    farfield_rows = count_rows(farfield, sample_id, frequency_hz)
    summary["nearfield_rows"] = nearfield_rows
    summary["farfield_rows"] = farfield_rows
    summary["nearfield_rows_complete"] = bool(nearfield_rows == expected_nearfield_rows)
    summary["farfield_rows_complete"] = bool(farfield_rows == expected_farfield_rows)
    summary["nearfield_complete"] = bool(summary["nearfield_ok"] and summary["nearfield_rows_complete"])
    summary["farfield_complete"] = bool(summary["farfield_ok"] and summary["farfield_rows_complete"])
    summary["case_complete"] = bool(summary["nearfield_complete"] and summary["farfield_complete"] and summary["pair_ok"])

    if not summary["nearfield_complete"] and summary["phase_nearfield_file_status"] == "exists":
        summary["nearfield_action"] = "run normalize_cst_complex_columns.py for phase nearfield export"
    else:
        summary["nearfield_action"] = ""
    if not summary["farfield_complete"] and summary["phase_farfield_file_status"] == "exists":
        summary["farfield_action"] = "run normalize_cst_complex_columns.py for phase farfield export"
    else:
        summary["farfield_action"] = ""

    return nearfield, farfield, summary


def write_if_available(frames: list[pd.DataFrame], out_path: Path) -> int:
    if not frames:
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    return int(len(merged))


def build_reconstruction_queue(case_report: pd.DataFrame, base_dir: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    columns = ["sample_id", "priority", "source_config", "frequency_hz", "out_dir", "command"]
    for row in case_report.loc[case_report["case_complete"]].itertuples(index=False):
        sample_id = str(row.sample_id)
        out_dir = Path("outputs") / "cst_reconstruction" / sample_id
        command = (
            "python code\\run_cst_reconstruction.py "
            f"--nearfield {row.nearfield_path} "
            f"--farfield {row.farfield_path} "
            f"--sample-id {sample_id} "
            f"--frequency-hz {int(row.frequency_hz)} "
            f"--out-dir {out_dir}"
        )
        rows.append(
            {
                "sample_id": sample_id,
                "priority": row.priority,
                "source_config": row.source_config,
                "frequency_hz": int(row.frequency_hz),
                "out_dir": str(out_dir),
                "command": command,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def priority_summary(case_report: pd.DataFrame) -> dict[str, object]:
    summary: dict[str, object] = {}
    for priority in ["required", "recommended", "optional"]:
        mask = case_report["priority"].astype(str).str.strip().eq(priority)
        summary[f"{priority}_cases"] = int(mask.sum())
        summary[f"{priority}_complete_cases"] = int(case_report.loc[mask, "case_complete"].sum())
        summary[f"{priority}_all_complete"] = bool(mask.any() and case_report.loc[mask, "case_complete"].all())
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge and audit CST Level 1 standard-source exports.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to level1_case_manifest.csv.")
    parser.add_argument("--base-dir", default=str(ROOT), help="Base directory used to resolve relative export paths.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directory for all_nearfield.csv/all_farfield.csv.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for audit CSV/JSON reports.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if required cases are incomplete.")
    parser.add_argument("--strict-all", action="store_true", help="Return non-zero if any planned case is incomplete.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    base_dir = Path(args.base_dir)
    out_dir = Path(args.out_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_table(manifest_path)
    required = {
        "sample_id",
        "priority",
        "frequency_hz",
        "nearfield_export",
        "farfield_export",
        "expected_nearfield_rows",
        "expected_farfield_rows",
    }
    missing = sorted(required - set(manifest.columns))
    if missing:
        raise ValueError(f"manifest missing required columns: {missing}")

    nearfield_frames: list[pd.DataFrame] = []
    farfield_frames: list[pd.DataFrame] = []
    case_rows: list[dict[str, object]] = []
    for _, row in manifest.iterrows():
        nearfield, farfield, summary = analyze_case(row, base_dir)
        if nearfield is not None:
            nearfield_frames.append(nearfield)
        if farfield is not None:
            farfield_frames.append(farfield)
        case_rows.append(summary)

    case_report = pd.DataFrame(case_rows)
    case_report.to_csv(report_dir / "level1_case_status.csv", index=False, encoding="utf-8-sig")

    reconstruction_queue = build_reconstruction_queue(case_report, base_dir)
    reconstruction_queue.to_csv(report_dir / "level1_reconstruction_queue.csv", index=False, encoding="utf-8-sig")

    nearfield_out = out_dir / "all_nearfield.csv"
    farfield_out = out_dir / "all_farfield.csv"
    merged_nearfield_rows = write_if_available(nearfield_frames, nearfield_out)
    merged_farfield_rows = write_if_available(farfield_frames, farfield_out)

    all_complete = bool(case_report["case_complete"].all()) if len(case_report) else False
    required_mask = case_report["priority"].astype(str).str.strip().eq("required")
    required_complete = bool(required_mask.any() and case_report.loc[required_mask, "case_complete"].all())
    strict_mode = bool(args.strict or args.strict_all)
    strict_scope = "all" if args.strict_all else "required"
    scoped_complete = all_complete if args.strict_all else required_complete

    summary = {
        "manifest": str(manifest_path),
        "base_dir": str(base_dir),
        "planned_cases": int(case_report.shape[0]),
        "complete_cases": int(case_report["case_complete"].sum()) if len(case_report) else 0,
        "merged_nearfield_rows": merged_nearfield_rows,
        "merged_farfield_rows": merged_farfield_rows,
        "nearfield_out": str(nearfield_out) if merged_nearfield_rows else "",
        "farfield_out": str(farfield_out) if merged_farfield_rows else "",
        "all_complete": all_complete,
        "required_complete": required_complete,
        "strict_mode": strict_mode,
        "strict_scope": strict_scope,
        "reconstruction_queue_rows": int(len(reconstruction_queue)),
        "next_commands_if_required_complete": [
            "python code\\merge_cst_level1_exports.py --strict",
            "Run each command listed in outputs\\cst_level1_merge_report\\level1_reconstruction_queue.csv",
        ],
    } | priority_summary(case_report)
    (report_dir / "level1_merge_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Level 1 merge/audit report written to {report_dir}")
    print(f"planned cases: {summary['planned_cases']}")
    print(f"complete cases: {summary['complete_cases']}")
    print(f"required complete: {summary['required_complete']}")
    print(f"merged nearfield rows: {merged_nearfield_rows}")
    print(f"merged farfield rows: {merged_farfield_rows}")
    if strict_mode and not scoped_complete:
        print(f"strict mode ({strict_scope}): incomplete exports detected")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
