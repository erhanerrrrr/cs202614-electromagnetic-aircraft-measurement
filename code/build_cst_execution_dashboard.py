from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_execution_dashboard"
DEFAULT_LEVEL1_MACRO = ROOT / "outputs" / "cst_macro_templates" / "level1_macro_parameters.csv"
DEFAULT_LEVEL2_PILOT = ROOT / "outputs" / "cst_macro_templates" / "level2_pilot_cases.csv"
DEFAULT_LEVEL2_SOURCES = ROOT / "outputs" / "cst_macro_templates" / "level2_macro_source_parameters.csv"
DEFAULT_LEVEL1_SUMMARY = ROOT / "outputs" / "cst_level1_merge_report" / "level1_merge_summary.json"
DEFAULT_LEVEL2_SUMMARY = ROOT / "outputs" / "cst_level2_merge_report" / "level2_merge_summary.json"
DEFAULT_COMPLETION_SUMMARY = ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_LEVEL1_PROJECT_SUMMARY = ROOT / "outputs" / "cst_real_level1_projects" / "cst_automation_summary.json"
DEFAULT_LEVEL1_PROJECT_MANIFEST = ROOT / "outputs" / "cst_real_level1_projects" / "cst_level1_project_manifest.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    try:
        return str(full.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(full)


def path_exists(path: str | Path) -> bool:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    return full.exists()


def command_check(nearfield: str, farfield: str, sample_id: str) -> str:
    return (
        "python code\\check_cst_export.py "
        f"--nearfield {nearfield} "
        f"--farfield {farfield} "
        f"--json-out outputs\\cst_reconstruction\\{sample_id}_validation.json"
    )


def command_reconstruct(nearfield: str, farfield: str, sample_id: str, frequency_hz: int) -> str:
    return (
        "python code\\run_cst_reconstruction.py "
        f"--nearfield {nearfield} "
        f"--farfield {farfield} "
        f"--sample-id {sample_id} "
        f"--frequency-hz {frequency_hz} "
        f"--out-dir outputs\\cst_reconstruction\\{sample_id}"
    )


def build_level1_required_actions(level1_macro: pd.DataFrame, level1_project_manifest: pd.DataFrame) -> pd.DataFrame:
    if level1_macro.empty:
        return pd.DataFrame()
    required = level1_macro[level1_macro["priority"].astype(str).eq("required")].copy()
    project_lookup: dict[str, dict[str, object]] = {}
    if not level1_project_manifest.empty:
        project_lookup = {
            str(row.sample_id): row._asdict()
            for row in level1_project_manifest.itertuples(index=False)
        }
    rows: list[dict[str, object]] = []
    for order, row in enumerate(required.itertuples(index=False), start=1):
        nearfield = str(row.nearfield_export)
        farfield = str(row.farfield_export)
        sample_id = str(row.sample_id)
        frequency_hz = int(row.frequency_hz)
        project_row = project_lookup.get(sample_id, {})
        generated_project = str(project_row.get("project_path", ""))
        rows.append(
            {
                "execution_order": order,
                "sample_id": sample_id,
                "priority": row.priority,
                "cst_project": row.cst_project,
                "frequency_hz": frequency_hz,
                "frequency_label": row.frequency_label,
                "source_type": row.source_type,
                "orientation_axis": row.orientation_axis,
                "center_xyz_m": f"{row.center_x_m},{row.center_y_m},{row.center_z_m}",
                "start_xyz_m": f"{row.start_x_m},{row.start_y_m},{row.start_z_m}",
                "end_xyz_m": f"{row.end_x_m},{row.end_y_m},{row.end_z_m}",
                "length_m": row.length_m,
                "feed_gap_m": row.feed_gap_m,
                "nearfield_export": nearfield,
                "farfield_export": farfield,
                "phase_nearfield_export": row.phase_format_nearfield_export,
                "phase_farfield_export": row.phase_format_farfield_export,
                "expected_nearfield_rows": int(row.expected_nearfield_rows),
                "expected_farfield_rows": int(row.expected_farfield_rows),
                "nearfield_exists": path_exists(nearfield),
                "farfield_exists": path_exists(farfield),
                "generated_cst_project": generated_project,
                "generated_cst_project_exists": path_exists(generated_project) if generated_project else False,
                "generated_cst_project_status": project_row.get("status", ""),
                "validation_command": command_check(nearfield, farfield, sample_id),
                "reconstruction_command": command_reconstruct(nearfield, farfield, sample_id, frequency_hz),
                "required_screenshots": (
                    f"submission/05_cst/screenshots/level1/{sample_id}_model.png; "
                    f"submission/05_cst/screenshots/level1/{sample_id}_monitors.png; "
                    f"submission/05_cst/screenshots/level1/{sample_id}_exports.png"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_level2_pilot_actions(level2_pilot: pd.DataFrame, level2_sources: pd.DataFrame) -> pd.DataFrame:
    if level2_pilot.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    for order, row in enumerate(level2_pilot.itertuples(index=False), start=1):
        sample_id = str(row.sample_id)
        sources = level2_sources[level2_sources["sample_id"].astype(str).eq(sample_id)]
        source_roles = ";".join(sources["source_role"].astype(str).tolist()) if not sources.empty else ""
        source_positions = ";".join(
            f"{src.source_role}@({src.x_m},{src.y_m},{src.z_m})" for src in sources.itertuples(index=False)
        )
        nearfield = str(row.nearfield_export)
        farfield = str(row.farfield_export)
        rows.append(
            {
                "execution_order_after_g2": order,
                "sample_id": sample_id,
                "class_label": row.class_label,
                "variant_index": int(row.variant_index),
                "cst_project": row.cst_project,
                "source_count": int(row.source_count),
                "source_roles": source_roles,
                "source_positions_m": source_positions,
                "frequency_hz_list": row.frequency_hz_list,
                "frequency_label_list": row.frequency_label_list,
                "nearfield_export": nearfield,
                "farfield_export": farfield,
                "expected_nearfield_rows_total": int(row.expected_nearfield_rows_total),
                "expected_farfield_rows_total": int(row.expected_farfield_rows_total),
                "nearfield_exists": path_exists(nearfield),
                "farfield_exists": path_exists(farfield),
                "post_export_merge_command": "python code\\merge_cst_level2_exports.py",
                "post_pilot_recognition_command": (
                    "python code\\run_cst_recognition.py "
                    "--nearfield data\\cst_exports\\level2\\all_nearfield.csv "
                    "--labels outputs\\cst_level2_plan\\level2_labels.csv "
                    "--out-dir outputs\\cst_recognition_level2"
                ),
            }
        )
    return pd.DataFrame(rows)


def build_missing_file_table(level1_actions: pd.DataFrame, level2_pilot_actions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in level1_actions.iterrows():
        for kind, path_col in [("nearfield", "nearfield_export"), ("farfield", "farfield_export")]:
            path = str(row[path_col])
            rows.append(
                {
                    "gate": "G2_Level1_required",
                    "required_now": True,
                    "sample_id": row["sample_id"],
                    "file_type": kind,
                    "expected_path": path,
                    "exists": path_exists(path),
                    "expected_rows": row[f"expected_{kind}_rows"],
                }
            )
    for _, row in level2_pilot_actions.iterrows():
        for kind, path_col, rows_col in [
            ("nearfield", "nearfield_export", "expected_nearfield_rows_total"),
            ("farfield", "farfield_export", "expected_farfield_rows_total"),
        ]:
            path = str(row[path_col])
            rows.append(
                {
                    "gate": "G3_Level2_pilot",
                    "required_now": False,
                    "sample_id": row["sample_id"],
                    "file_type": kind,
                    "expected_path": path,
                    "exists": path_exists(path),
                    "expected_rows": row[rows_col],
                }
            )
    return pd.DataFrame(rows)


def write_dropzone_readmes(level1_actions: pd.DataFrame, level2_pilot_actions: pd.DataFrame) -> None:
    base = ROOT / "data" / "cst_exports"
    level1_dir = base / "level1"
    level2_dir = base / "level2"
    level1_dir.mkdir(parents=True, exist_ok=True)
    level2_dir.mkdir(parents=True, exist_ok=True)

    level1_files = "\n".join(
        f"- `{row.nearfield_export}` and `{row.farfield_export}`"
        for row in level1_actions.itertuples(index=False)
    )
    level2_files = "\n".join(
        f"- `{row.nearfield_export}` and `{row.farfield_export}`"
        for row in level2_pilot_actions.itertuples(index=False)
    )

    (base / "README_cst_exports.md").write_text(
        """# CST export dropzone

Place real CST exported CSV files here. Do not place synthetic/demo data in this folder.

- `level1/`: standard-source exports for the G2 gate.
- `level2/`: multisource/multistate exports for the G3 gate.

After adding files, rerun:

```powershell
python code\\merge_cst_level1_exports.py
python code\\merge_cst_level2_exports.py
python code\\build_cst_execution_dashboard.py
```
""",
        encoding="utf-8",
    )

    (level1_dir / "README_level1_dropzone.md").write_text(
        f"""# Level 1 real CST export dropzone

Immediate G2 required files:

{level1_files}

Rules:

- Use meters for coordinates.
- Keep `sample_id` and `frequency_hz` exactly as listed in the manifest.
- Export complex fields as real/imag columns when possible.
- If CST exports magnitude/phase, use the `_phase.csv` filenames and then run `normalize_cst_complex_columns.py`.
""",
        encoding="utf-8",
    )

    (level2_dir / "README_level2_dropzone.md").write_text(
        f"""# Level 2 real CST export dropzone

Run these pilot files after G2 passes:

{level2_files}

Full Level 2 requires all 48 sample exports listed in `outputs/cst_level2_plan/level2_case_manifest.csv`.
Do not start final recognition until `python code\\merge_cst_level2_exports.py --strict` passes.
""",
        encoding="utf-8",
    )


def write_dashboard(
    out_dir: Path,
    level1_actions: pd.DataFrame,
    level2_pilot_actions: pd.DataFrame,
    missing_files: pd.DataFrame,
    summaries: dict[str, dict[str, object]],
) -> None:
    level1_summary = summaries["level1"]
    level2_summary = summaries["level2"]
    completion = summaries["completion"]
    level1_projects = summaries["level1_projects"]
    sensor_count = int(len(read_csv(DEFAULT_SENSOR_LAYOUT))) if DEFAULT_SENSOR_LAYOUT.exists() else 0
    required_missing = missing_files[missing_files["required_now"].eq(True) & missing_files["exists"].eq(False)]
    pilot_missing = missing_files[missing_files["gate"].eq("G3_Level2_pilot") & missing_files["exists"].eq(False)]

    level1_rows = "\n".join(
        (
            f"| {row.execution_order} | `{row.sample_id}` | `{row.source_type}` | `{row.frequency_label}` | "
            f"`{row.generated_cst_project_exists}` | `{row.nearfield_export}` | `{row.farfield_export}` | {row.nearfield_exists}/{row.farfield_exists} |"
        )
        for row in level1_actions.itertuples(index=False)
    )
    level2_rows = "\n".join(
        (
            f"| {row.execution_order_after_g2} | `{row.sample_id}` | {row.class_label} | "
            f"{row.frequency_label_list} | {row.source_count} | `{row.nearfield_export}` | `{row.farfield_export}` |"
        )
        for row in level2_pilot_actions.itertuples(index=False)
    )

    content = f"""# CST execution dashboard

This dashboard is generated from the current workspace. It tracks real CST execution only; synthetic/demo data does not close G2 or G3.

## Current Gate Status

| Gate | Requirement | Status |
|---|---|---|
| G2 | Level 1 required CST standard sources complete and reconstructed | {level1_summary.get("required_complete_cases", 0)}/{level1_summary.get("required_cases", 0)} required complete |
| G2-projects | Level 1 required CST projects generated through CST API | {level1_projects.get("projects_created", 0)}/{level1_projects.get("case_count", 0)} projects created |
| G3 | Level 2 multisource CST samples complete | {level2_summary.get("complete_samples", 0)}/{level2_summary.get("planned_samples", 0)} samples complete |
| Completion audit | Overall objective proven | `{completion.get("completion_proven", False)}` |
| Next blocking gate | First missing gate | `{completion.get("next_blocking_gate", "unknown")}` |

Selected measurement surface: `2pi_upper_hemisphere`  
Sensor count: `{sensor_count}`  
Required-now missing files: `{len(required_missing)}`  
Level 2 pilot missing files: `{len(pilot_missing)}`

## Do First: G2 Level 1 Required Cases

| Order | sample_id | Source | Frequency | CST project exists | Nearfield export | Farfield export | NF/FF exists |
|---:|---|---|---|---|---|---|---|
{level1_rows}

Generated CST projects are under `outputs/cst_real_level1_projects/projects`. After solving and exporting the two required cases:

```powershell
python code\\merge_cst_level1_exports.py --strict
python code\\run_cst_level1_batch_reconstruction.py --require-cases
python code\\build_completion_audit.py
```

## Then: G3 Level 2 Pilot Cases

Run one sample per class before launching all 48 Level 2 samples.

| Order | sample_id | Class | Frequencies | Source count | Nearfield export | Farfield export |
|---:|---|---|---|---:|---|---|
{level2_rows}

After pilot files are exported, run:

```powershell
python code\\merge_cst_level2_exports.py
```

Full Level 2 recognition should wait until:

```powershell
python code\\merge_cst_level2_exports.py --strict
```

passes for all 48 samples.

## Operator Files

| File | Use |
|---|---|
| `level1_required_action_sheet.csv` | Exact Level 1 required parameters, filenames, validation commands and screenshot targets. |
| `level2_pilot_action_sheet.csv` | Four pilot samples, one per class, with sources and expected rows. |
| `missing_real_cst_files.csv` | Current missing nearfield/farfield files for G2 and Level 2 pilot. |
| `outputs/cst_operator_runbook/README_cst_operator_runbook.md` | Step-by-step G2 CST operator package with probe points, farfield grid, export contract and screenshots. |
| `outputs/cst_real_level1_projects/README_cst_level1_automation.md` | Real CST API project-generation evidence and generated `.cst` project manifest. |
| `outputs/level1_analytic_reference` | Analytic dipole far-field sanity references for Level 1. |
| `data/cst_exports/README_cst_exports.md` | Dropzone rules for real CST exports. |

## Important Rule

Do not rename files after export. The merge scripts use the manifest paths as the contract.
"""
    (out_dir / "cst_execution_dashboard.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a dashboard for real CST execution status and next actions.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    level1_macro = read_csv(DEFAULT_LEVEL1_MACRO)
    level1_project_manifest = read_csv(DEFAULT_LEVEL1_PROJECT_MANIFEST)
    level2_pilot = read_csv(DEFAULT_LEVEL2_PILOT)
    level2_sources = read_csv(DEFAULT_LEVEL2_SOURCES)
    level1_actions = build_level1_required_actions(level1_macro, level1_project_manifest)
    level2_pilot_actions = build_level2_pilot_actions(level2_pilot, level2_sources)
    missing_files = build_missing_file_table(level1_actions, level2_pilot_actions)

    level1_actions.to_csv(out_dir / "level1_required_action_sheet.csv", index=False, encoding="utf-8-sig")
    level2_pilot_actions.to_csv(out_dir / "level2_pilot_action_sheet.csv", index=False, encoding="utf-8-sig")
    missing_files.to_csv(out_dir / "missing_real_cst_files.csv", index=False, encoding="utf-8-sig")

    write_dropzone_readmes(level1_actions, level2_pilot_actions)
    summaries = {
        "level1": read_json(DEFAULT_LEVEL1_SUMMARY),
        "level1_projects": read_json(DEFAULT_LEVEL1_PROJECT_SUMMARY),
        "level2": read_json(DEFAULT_LEVEL2_SUMMARY),
        "completion": read_json(DEFAULT_COMPLETION_SUMMARY),
    }
    write_dashboard(out_dir, level1_actions, level2_pilot_actions, missing_files, summaries)

    summary = {
        "out_dir": rel(out_dir),
        "level1_required_actions": int(len(level1_actions)),
        "level2_pilot_actions": int(len(level2_pilot_actions)),
        "missing_required_now_files": int(
            len(missing_files[missing_files["required_now"].eq(True) & missing_files["exists"].eq(False)])
        ),
        "missing_level2_pilot_files": int(
            len(missing_files[missing_files["gate"].eq("G3_Level2_pilot") & missing_files["exists"].eq(False)])
        ),
        "level1_generated_projects": int(read_json(DEFAULT_LEVEL1_PROJECT_SUMMARY).get("projects_created", 0) or 0),
        "level1_project_generation_complete": bool(
            read_json(DEFAULT_LEVEL1_PROJECT_SUMMARY).get("all_projects_created", False)
        ),
        "real_cst_project_dir": rel(ROOT / "outputs" / "cst_real_level1_projects" / "projects"),
        "dropzone": rel(ROOT / "data" / "cst_exports"),
        "is_simulation_evidence": False,
    }
    (out_dir / "cst_execution_dashboard_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"CST execution dashboard written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
