from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "cst_operator_runbook"
LEVEL1_ACTIONS = ROOT / "outputs" / "cst_execution_dashboard" / "level1_required_action_sheet.csv"
SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
FARFIELD_TEMPLATE = ROOT / "outputs" / "cst_templates" / "farfield_truth_template.csv"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path | str) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    try:
        return str(full.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(full)


def command_validate_case(sample_id: str, nearfield: str, farfield: str) -> str:
    return (
        "python code\\check_cst_export.py "
        f"--nearfield {nearfield} "
        f"--farfield {farfield} "
        f"--json-out outputs\\cst_reconstruction\\{sample_id}_validation.json"
    )


def command_phase_convert(sample_id: str, phase_nearfield: str, phase_farfield: str, nearfield: str, farfield: str) -> str:
    return (
        "python code\\normalize_cst_complex_columns.py "
        f"--nearfield {phase_nearfield} "
        f"--farfield {phase_farfield} "
        f"--nearfield-out {nearfield} "
        f"--farfield-out {farfield} "
        "--phase-unit deg "
        f"--json-out outputs\\cst_reconstruction\\{sample_id}_phase_conversion.json"
    )


def command_reconstruct_case(sample_id: str, nearfield: str, farfield: str, frequency_hz: int) -> str:
    return (
        "python code\\run_cst_reconstruction.py "
        f"--nearfield {nearfield} "
        f"--farfield {farfield} "
        f"--sample-id {sample_id} "
        f"--frequency-hz {frequency_hz} "
        f"--out-dir outputs\\cst_reconstruction\\{sample_id}"
    )


def build_probe_points(sensor_layout: pd.DataFrame) -> pd.DataFrame:
    probe = sensor_layout.copy()
    probe["cst_probe_name"] = probe["sensor_id"].astype(int).map(lambda value: f"NF_HEMI_{value:03d}")
    probe["coordinate_unit"] = "m"
    probe["field_components"] = "Ex;Ey;Ez"
    probe["monitor_use"] = "sample complex E-field at this point for the 2pi upper-hemisphere measurement surface"
    columns = [
        "cst_probe_name",
        "sensor_id",
        "x_m",
        "y_m",
        "z_m",
        "theta_deg",
        "phi_deg",
        "radius_m",
        "coordinate_unit",
        "field_components",
        "monitor_use",
    ]
    return probe[columns]


def build_farfield_grid(farfield_template: pd.DataFrame) -> pd.DataFrame:
    if farfield_template.empty:
        return pd.DataFrame()
    grid = farfield_template[["theta_deg", "phi_deg"]].drop_duplicates().copy()
    grid["theta_deg"] = grid["theta_deg"].astype(float).round(6)
    grid["phi_deg"] = grid["phi_deg"].astype(float).round(6)
    grid = grid.sort_values(["theta_deg", "phi_deg"]).reset_index(drop=True)
    grid["grid_index"] = range(len(grid))
    grid["coordinate_system"] = "spherical_farfield"
    grid["required_outputs"] = "Etheta(real,imag);Ephi(real,imag);gain_db(optional)"
    return grid[["grid_index", "theta_deg", "phi_deg", "coordinate_system", "required_outputs"]]


def build_export_contract(actions: pd.DataFrame, sensor_count: int, farfield_rows: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    nearfield_columns = "sample_id,sensor_id,x_m,y_m,z_m,theta_deg,phi_deg,frequency_hz,polarization,e_real,e_imag"
    farfield_columns = "sample_id,theta_deg,phi_deg,frequency_hz,e_theta_real,e_theta_imag,e_phi_real,e_phi_imag,gain_db"
    for action in actions.itertuples(index=False):
        sample_id = str(action.sample_id)
        rows.append(
            {
                "sample_id": sample_id,
                "file_type": "nearfield",
                "expected_path": action.nearfield_export,
                "expected_rows": int(action.expected_nearfield_rows),
                "row_basis": f"{sensor_count} sensor points x 3 components",
                "required_columns": nearfield_columns,
                "fallback_phase_path": action.phase_nearfield_export,
                "acceptance_check": command_validate_case(sample_id, action.nearfield_export, action.farfield_export),
            }
        )
        rows.append(
            {
                "sample_id": sample_id,
                "file_type": "farfield",
                "expected_path": action.farfield_export,
                "expected_rows": int(action.expected_farfield_rows),
                "row_basis": f"{farfield_rows} theta/phi samples",
                "required_columns": farfield_columns,
                "fallback_phase_path": action.phase_farfield_export,
                "acceptance_check": command_validate_case(sample_id, action.nearfield_export, action.farfield_export),
            }
        )
    return pd.DataFrame(rows)


def build_screenshot_manifest(actions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    required_views = [
        ("model", "dipole geometry, feed/port, coordinate axes and 12m x 10m x 8m reference envelope if shown"),
        ("boundary", "open/PML boundary and background/units"),
        ("monitors", "nearfield and farfield monitors at 1.2 GHz"),
        ("probe_layout", "162 upper-hemisphere probe points or imported point list"),
        ("farfield_grid", "theta/phi farfield export settings"),
        ("exports", "CSV export dialog or result tree showing final filenames"),
    ]
    for action in actions.itertuples(index=False):
        sample_id = str(action.sample_id)
        for view, description in required_views:
            rows.append(
                {
                    "sample_id": sample_id,
                    "view": view,
                    "target_path": f"submission/05_cst/screenshots/level1/{sample_id}_{view}.png",
                    "description": description,
                    "required_for_gate": "G2",
                }
            )
    return pd.DataFrame(rows)


def build_post_export_commands(actions: pd.DataFrame) -> list[str]:
    commands: list[str] = []
    commands.append("# Run from the project root after real CST Level 1 exports exist.")
    for action in actions.itertuples(index=False):
        sample_id = str(action.sample_id)
        frequency_hz = int(action.frequency_hz)
        commands.append("")
        commands.append(f"# Optional only if CST exported magnitude/phase files for {sample_id}")
        commands.append(
            command_phase_convert(
                sample_id,
                str(action.phase_nearfield_export),
                str(action.phase_farfield_export),
                str(action.nearfield_export),
                str(action.farfield_export),
            )
        )
        commands.append("")
        commands.append(f"# Validate and reconstruct {sample_id}")
        commands.append(command_validate_case(sample_id, str(action.nearfield_export), str(action.farfield_export)))
        commands.append(
            command_reconstruct_case(
                sample_id,
                str(action.nearfield_export),
                str(action.farfield_export),
                frequency_hz,
            )
        )
    commands.extend(
        [
            "",
            "# Strict G2 gate check after both required cases are exported.",
            "python code\\merge_cst_level1_exports.py --strict",
            "python code\\run_cst_level1_batch_reconstruction.py --require-cases",
            "python code\\build_scorecard.py",
            "python code\\build_completion_audit.py",
            "python code\\build_master_dashboard.py",
        ]
    )
    return commands


def write_readme(actions: pd.DataFrame, probe_points: pd.DataFrame, farfield_grid: pd.DataFrame) -> None:
    action_rows = "\n".join(
        (
            f"| {row.execution_order} | `{row.sample_id}` | `{row.cst_project}` | "
            f"`{row.source_type}` | `{row.frequency_label}` | `{row.nearfield_export}` | `{row.farfield_export}` |"
        )
        for row in actions.itertuples(index=False)
    )
    content = f"""# CST operator runbook

This package is for real CST execution. It is not simulation evidence by itself.

## Immediate Goal

Close G2 by exporting the two required Level 1 standard-source cases and then running strict audit/reconstruction.

## Required Cases

| Order | sample_id | CST project | Source | Frequency | Nearfield export | Farfield export |
|---:|---|---|---|---|---|---|
{action_rows}

## Geometry and Sampling Contract

- Measurement surface: `2pi_upper_hemisphere`
- Probe radius: `13 m`
- Probe count: `{len(probe_points)}`
- Nearfield rows per case: `{len(probe_points) * 3}` (`Ex`, `Ey`, `Ez` at each probe)
- Farfield grid rows per case: `{len(farfield_grid)}`
- Enclosed carrier volume requirement from the problem statement: at least `12m x 10m x 8m`

## Operator Sequence

1. In CST, use meter units and preserve the global coordinate axes.
2. Create or clone the project named in `level1_required_operator_steps.csv`.
3. Build the dipole using the listed start/end coordinates and feed gap.
4. Use open/add-space or PML boundaries.
5. Add the 162 nearfield probe points from `cst_probe_points_hemisphere_162.csv`.
6. Export complex `Ex`, `Ey`, `Ez` at each probe into the exact nearfield CSV path.
7. Export farfield over the theta/phi grid in `cst_farfield_sampling_grid.csv` into the exact farfield CSV path.
8. Save required screenshots listed in `cst_level1_required_screenshot_manifest.csv`.
9. Run `post_export_level1_validation_commands.ps1` from the project root.

## Files

| File | Meaning |
|---|---|
| `level1_required_operator_steps.csv` | One row per required case with geometry, solver, monitor and export instructions. |
| `cst_probe_points_hemisphere_162.csv` | The exact 162 half-sphere probe coordinates to use in CST. |
| `cst_farfield_sampling_grid.csv` | The exact theta/phi farfield sampling grid expected by Python. |
| `cst_level1_required_export_contract.csv` | Required columns, expected rows, fallback phase paths and validation commands. |
| `cst_level1_required_screenshot_manifest.csv` | Screenshots needed to prove CST setup and exports. |
| `post_export_level1_validation_commands.ps1` | Commands to convert phase exports if needed, validate files, reconstruct farfield and refresh gates. |
| `README_cst_operator_runbook.md` | Human-readable runbook. |

## Failure Rules

- If filenames differ from this package, fix filenames before running merge scripts.
- If coordinates are exported in millimeters, convert them to meters before validation.
- If magnitude/phase columns are exported, run the phase conversion command before `check_cst_export.py`.
- If `merge_cst_level1_exports.py --strict` fails, do not start full Level 2 execution yet.
"""
    (OUT / "README_cst_operator_runbook.md").write_text(content, encoding="utf-8")


def build_operator_steps(actions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for action in actions.itertuples(index=False):
        sample_id = str(action.sample_id)
        rows.append(
            {
                "execution_order": int(action.execution_order),
                "sample_id": sample_id,
                "cst_project": action.cst_project,
                "unit": "m",
                "frequency_hz": int(action.frequency_hz),
                "boundary": "Open/Add Space or PML",
                "source_type": action.source_type,
                "orientation_axis": action.orientation_axis,
                "center_xyz_m": action.center_xyz_m,
                "start_xyz_m": action.start_xyz_m,
                "end_xyz_m": action.end_xyz_m,
                "length_m": action.length_m,
                "feed_gap_m": action.feed_gap_m,
                "nearfield_monitor": f"nearfield_hemisphere_{action.frequency_label}",
                "farfield_monitor": f"farfield_{action.frequency_label}",
                "nearfield_export": action.nearfield_export,
                "farfield_export": action.farfield_export,
                "acceptance_thresholds": "correlation>=0.95; main_lobe_error_deg<=5; nmse<=0.01",
                "manual_step_summary": (
                    "build dipole from start/end coordinates; add feed/port at center; "
                    "set open boundary; add 162 hemisphere probes; export complex nearfield and farfield CSV"
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    actions = read_csv(LEVEL1_ACTIONS)
    sensor_layout = read_csv(SENSOR_LAYOUT)
    farfield_template = read_csv(FARFIELD_TEMPLATE)

    probe_points = build_probe_points(sensor_layout)
    farfield_grid = build_farfield_grid(farfield_template)
    operator_steps = build_operator_steps(actions)
    export_contract = build_export_contract(actions, len(probe_points), len(farfield_grid))
    screenshot_manifest = build_screenshot_manifest(actions)
    commands = build_post_export_commands(actions)

    operator_steps.to_csv(OUT / "level1_required_operator_steps.csv", index=False, encoding="utf-8-sig")
    probe_points.to_csv(OUT / "cst_probe_points_hemisphere_162.csv", index=False, encoding="utf-8-sig")
    farfield_grid.to_csv(OUT / "cst_farfield_sampling_grid.csv", index=False, encoding="utf-8-sig")
    export_contract.to_csv(OUT / "cst_level1_required_export_contract.csv", index=False, encoding="utf-8-sig")
    screenshot_manifest.to_csv(OUT / "cst_level1_required_screenshot_manifest.csv", index=False, encoding="utf-8-sig")
    (OUT / "post_export_level1_validation_commands.ps1").write_text("\n".join(commands) + "\n", encoding="utf-8")
    write_readme(actions, probe_points, farfield_grid)

    summary = {
        "out_dir": rel(OUT),
        "required_case_count": int(len(actions)),
        "probe_point_count": int(len(probe_points)),
        "nearfield_rows_per_case": int(len(probe_points) * 3),
        "farfield_rows_per_case": int(len(farfield_grid)),
        "screenshot_count": int(len(screenshot_manifest)),
        "is_final": False,
        "is_simulation_evidence": False,
        "next_gate": "G2",
    }
    (OUT / "cst_operator_runbook_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"CST operator runbook written to {OUT}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
