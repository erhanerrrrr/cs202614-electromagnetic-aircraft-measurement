from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_execution_logs"


def write_readme(out_dir: Path) -> None:
    content = """# CST execution log templates

This folder contains editable log templates for real CST execution.

Use these files when the CST owner starts real simulations. They are deliberately separate from synthetic/demo outputs.

## Files

| File | Use |
|---|---|
| `level1_execution_log.csv` | Record each Level 1 standard-source CST run, export, audit, and reconstruction result. |
| `level2_execution_log.csv` | Record each Level 2 multi-source CST sample, export, merge, and recognition readiness. |
| `cst_issue_log.csv` | Track simulation/export issues and fixes. |
| `screenshot_inventory.csv` | Track CST screenshots needed for report/PPT/video. |

## Rule

Do not mark a case as complete by hand unless the corresponding Python audit passes:

```powershell
python code\\merge_cst_level1_exports.py --strict
python code\\merge_cst_level2_exports.py --strict
```
"""
    (out_dir / "README_cst_execution_logs.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CST execution log templates.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    level1_cols = [
        "sample_id",
        "priority",
        "cst_project_path",
        "operator",
        "run_date",
        "solver",
        "frequency_hz",
        "hemisphere_sensor_layout_confirmed",
        "nearfield_export_path",
        "farfield_export_path",
        "check_cst_export_ok",
        "merge_case_complete",
        "reconstruction_done",
        "nmse",
        "correlation",
        "main_lobe_error_deg",
        "screenshots_done",
        "notes",
    ]
    level2_cols = [
        "sample_id",
        "class_label",
        "variant_index",
        "cst_project_path",
        "operator",
        "run_date",
        "frequency_count",
        "source_count",
        "hemisphere_sensor_layout_confirmed",
        "nearfield_export_path",
        "farfield_export_path",
        "merge_sample_complete",
        "recognition_ready",
        "screenshots_done",
        "notes",
    ]
    issue_cols = [
        "issue_id",
        "date",
        "stage",
        "sample_id",
        "severity",
        "symptom",
        "suspected_cause",
        "fix_action",
        "owner",
        "status",
        "verification_command",
    ]
    screenshot_cols = [
        "stage",
        "sample_id",
        "screenshot_type",
        "expected_path",
        "captured",
        "used_in_report",
        "used_in_ppt",
        "notes",
    ]

    pd.DataFrame(columns=level1_cols).to_csv(out_dir / "level1_execution_log.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=level2_cols).to_csv(out_dir / "level2_execution_log.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=issue_cols).to_csv(out_dir / "cst_issue_log.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=screenshot_cols).to_csv(out_dir / "screenshot_inventory.csv", index=False, encoding="utf-8-sig")

    summary = {
        "stage": "CST_real_execution_logging",
        "out_dir": str(out_dir),
        "files": [
            "level1_execution_log.csv",
            "level2_execution_log.csv",
            "cst_issue_log.csv",
            "screenshot_inventory.csv",
            "README_cst_execution_logs.md",
        ],
        "note": "Templates only. Completion is still determined by merge/reconstruction/recognition scripts.",
    }
    (out_dir / "execution_log_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir)

    print(f"CST execution log templates written to {out_dir}")
    print(f"files: {len(summary['files'])}")


if __name__ == "__main__":
    main()
