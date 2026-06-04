from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_source_family_generation"
DEFAULT_EFIELD_DIR = Path(r"C:\csttmp\huy_sf_e")
DEFAULT_HFIELD_DIR = Path(r"C:\csttmp\huy_sf_h")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def collect_mode(mode: str, field_kind: str, base_dir: Path) -> dict[str, Any]:
    summary_path = base_dir / "cst_automation_summary.json"
    manifest_path = base_dir / "cst_level1_project_manifest.csv"
    summary = read_json(summary_path)
    manifest = read_csv_rows(manifest_path)
    rows: list[dict[str, Any]] = []
    for row in manifest:
        project_path = Path(row.get("project_path", ""))
        rows.append(
            {
                "field_kind": field_kind,
                "probe_mode": mode,
                "sample_id": row.get("sample_id", ""),
                "source_type": row.get("source_type", ""),
                "orientation_axis": row.get("orientation_axis", ""),
                "project_path": str(project_path),
                "project_exists": str(project_path.exists()),
                "project_size_bytes": project_path.stat().st_size if project_path.exists() else "",
                "probe_count": row.get("probe_count", ""),
                "history_block_count": row.get("history_block_count", ""),
                "status": row.get("status", ""),
                "error": row.get("error", ""),
            }
        )
    return {
        "mode": mode,
        "field_kind": field_kind,
        "base_dir": str(base_dir),
        "summary_path": str(summary_path),
        "manifest_path": str(manifest_path),
        "summary_exists": summary_path.exists(),
        "manifest_exists": manifest_path.exists(),
        "stage_status": summary.get("stage_status", "missing"),
        "real_cst_api_used": bool(summary.get("real_cst_api_used", False)),
        "all_projects_created": bool(summary.get("all_projects_created", False)),
        "all_cases_ok": bool(summary.get("all_cases_ok", False)),
        "case_count": int(summary.get("case_count", len(manifest)) or 0),
        "projects_created": int(summary.get("projects_created", 0) or 0),
        "probe_count": int(summary.get("probe_count", 0) or 0),
        "rows": rows,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "field_kind",
        "probe_mode",
        "sample_id",
        "source_type",
        "orientation_axis",
        "project_path",
        "project_exists",
        "project_size_bytes",
        "probe_count",
        "history_block_count",
        "status",
        "error",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# CST Huygens Source-Family Project Generation",
        "",
        "This report records the local CST API project-generation evidence for the S42 source-family workpack.",
        "",
        "## Status",
        "",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Real CST API used: `{summary['real_cst_api_used']}`",
        f"- E-field projects: `{summary['efield_projects_created']}/{summary['expected_case_count']}`",
        f"- H-field projects: `{summary['hfield_projects_created']}/{summary['expected_case_count']}`",
        f"- Total project rows: `{summary['total_project_rows']}`",
        "",
        "This is still not a solve/export physics pass. The next gate is to solve the generated projects, export matched local E/H probe CSVs, and evaluate the frozen Huygens rule without retuning.",
        "",
        "## Project Rows",
        "",
        "| Field | Sample | Axis | Exists | Bytes | Status |",
        "|---|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['field_kind']} | `{row['sample_id']}` | `{row['orientation_axis']}` | "
            f"`{row['project_exists']}` | {row['project_size_bytes']} | `{row['status']}` |"
        )
    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\build_cst_source_family_generation_status.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_status(args: argparse.Namespace) -> dict[str, Any]:
    efield = collect_mode("efield", "e", Path(args.efield_dir))
    hfield = collect_mode("hfield", "h", Path(args.hfield_dir))
    mode_items = [efield, hfield]
    all_rows = [row for item in mode_items for row in item["rows"]]
    expected_case_count = max((item["case_count"] for item in mode_items), default=0)
    all_generation_complete = all(
        item["stage_status"] == "project_generation_complete"
        and item["real_cst_api_used"]
        and item["all_projects_created"]
        and item["all_cases_ok"]
        and item["projects_created"] == expected_case_count
        for item in mode_items
    )
    all_rows_exist = all(truthy(row["project_exists"]) for row in all_rows) if all_rows else False
    if all_generation_complete and all_rows_exist and expected_case_count > 0:
        stage_status = "source_family_projects_generated"
    elif any(item["summary_exists"] or item["manifest_exists"] for item in mode_items):
        stage_status = "source_family_project_generation_partial"
    else:
        stage_status = "source_family_project_generation_missing"
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage_status": stage_status,
        "real_cst_api_used": all(item["real_cst_api_used"] for item in mode_items),
        "expected_case_count": expected_case_count,
        "efield_projects_created": efield["projects_created"],
        "hfield_projects_created": hfield["projects_created"],
        "total_projects_created": efield["projects_created"] + hfield["projects_created"],
        "total_project_rows": len(all_rows),
        "all_project_generation_complete": all_generation_complete,
        "all_project_files_exist": all_rows_exist,
        "efield_summary": efield,
        "hfield_summary": hfield,
        "next_gate": "solve generated E/H source-family CST projects, export local probe CSVs and farfield references, then run the frozen Huygens rule without retuning",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize CST source-family project generation evidence.")
    parser.add_argument("--efield-dir", type=Path, default=DEFAULT_EFIELD_DIR)
    parser.add_argument("--hfield-dir", type=Path, default=DEFAULT_HFIELD_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_status(args)
    rows = summary["efield_summary"]["rows"] + summary["hfield_summary"]["rows"]

    summary_for_json = dict(summary)
    (out_dir / "source_family_project_generation_summary.json").write_text(
        json.dumps(summary_for_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(out_dir / "source_family_project_manifest.csv", rows)
    write_markdown(out_dir / "source_family_project_generation.md", summary, rows)

    print(json.dumps({
        "stage_status": summary["stage_status"],
        "out_dir": display_path(out_dir),
        "total_projects_created": summary["total_projects_created"],
        "total_project_rows": summary["total_project_rows"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
