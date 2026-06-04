from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REQUIRED_CASES = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "level1_required_meshsafe_huygens_cases.csv"
)
DEFAULT_REQUIRED_PROBES = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "level1_local_huygens_probe_points.csv"
)
DEFAULT_OUT_DIR = ROOT / "data" / "cst_meshsafe_huygens_source_family_workpack"
DEFAULT_E_PROJECT_DIR = Path(r"C:\csttmp\huy_sf_e")
DEFAULT_H_PROJECT_DIR = Path(r"C:\csttmp\huy_sf_h")
DEFAULT_E_SOLVE_DIR = Path(r"C:\csttmp\huy_sf_es")
DEFAULT_H_SOLVE_DIR = Path(r"C:\csttmp\huy_sf_hs")
DEFAULT_SOLVER_SUMMARY_DIR = ROOT / "outputs" / "cst_solver_trials" / "meshsafe_huygens_source_family"
DEFAULT_EXPORT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_source_family_export"
EXPORT_ROOT = ROOT / "data" / "cst_exports" / "level1_meshsafe_huygens_source_family"
PRIOR_ID = "level1_local_sphere_r0p35"
FREQUENCY_TAG = "1200MHz"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: str | Path) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT)).replace("/", "\\")
    except Exception:
        return str(candidate)


def parse_xyz(value: str) -> tuple[float, float, float]:
    parts = [float(item.strip()) for item in str(value).split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected xyz triple, got: {value!r}")
    return parts[0], parts[1], parts[2]


def xyz_text(values: tuple[float, float, float]) -> str:
    return ",".join(f"{value:.15g}" for value in values)


def shifted(values: tuple[float, float, float], delta: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(values[index] + delta[index] for index in range(3))  # type: ignore[return-value]


def spherical_angles(position: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = position
    radius = math.sqrt(x * x + y * y + z * z)
    if radius <= 0.0:
        return 0.0, 0.0, 0.0
    theta = math.degrees(math.acos(max(-1.0, min(1.0, z / radius))))
    phi = math.degrees(math.atan2(y, x)) % 360.0
    return radius, theta, phi


def case_template_by_source(cases: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    templates: dict[str, dict[str, str]] = {}
    for row in cases:
        templates[str(row.get("source_type", "")).strip()] = row
    required = {"short_dipole", "halfwave_dipole"}
    missing = sorted(required - set(templates))
    if missing:
        raise ValueError(f"required case CSV missing source types: {missing}")
    return templates


def axis_vector(axis: str) -> tuple[float, float, float]:
    return {
        "x": (1.0, 0.0, 0.0),
        "y": (0.0, 1.0, 0.0),
        "z": (0.0, 0.0, 1.0),
    }[axis]


def build_axis_case(
    template: dict[str, str],
    execution_order: int,
    sample_id: str,
    axis: str,
    center: tuple[float, float, float],
    validation_role: str,
) -> dict[str, Any]:
    length = float(template["length_m"])
    direction = axis_vector(axis)
    half = length / 2.0
    start = tuple(center[index] - half * direction[index] for index in range(3))  # type: ignore[return-value]
    end = tuple(center[index] + half * direction[index] for index in range(3))  # type: ignore[return-value]
    row = dict(template)
    row.update(
        {
            "execution_order": execution_order,
            "sample_id": sample_id,
            "cst_project": f"CST_{sample_id}_meshsafe_huygens_r0p35.cst",
            "orientation_axis": axis,
            "center_xyz_m": xyz_text(center),
            "start_xyz_m": xyz_text(start),
            "end_xyz_m": xyz_text(end),
            "nearfield_monitor": f"nearfield_local_huygens_r0p35_{FREQUENCY_TAG}",
            "farfield_monitor": f"farfield_{FREQUENCY_TAG}",
            "nearfield_export": (
                f"data/cst_exports/level1_meshsafe_huygens_source_family/"
                f"{sample_id}_{PRIOR_ID}_local_efield.csv"
            ),
            "farfield_export": f"data/cst_exports/level1_meshsafe_huygens_source_family/{sample_id}_farfield.csv",
            "acceptance_thresholds": (
                "frozen_eh_rule=eh_love_equivalence_minus_j96; "
                "no_per_source_retuning; local_huygens_surface_export; "
                "python_extrapolated_compare_to_independent_cst_farfield"
            ),
            "manual_step_summary": (
                f"Source-family validation case: {validation_role}; build axis-aligned {axis}-dipole "
                "from start/end coordinates, export matched local E/H probe CSVs and farfield reference."
            ),
            "workflow_role": "mesh_safe_huygens_source_family_validation",
            "source_prior_id": PRIOR_ID,
            "local_probe_count": 96,
            "local_radius_m": "0.349999773869",
            "validation_role": validation_role,
            "automation_status": "axis_aligned_ready",
        }
    )
    return row


def build_axis_cases(templates: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    base_center = parse_xyz(templates["short_dipole"]["center_xyz_m"])
    specs = [
        ("short_dipole", "L1_short_dipole_x_1p2G", "x", base_center, "orientation_x_short"),
        ("short_dipole", "L1_short_dipole_y_1p2G", "y", base_center, "orientation_y_short"),
        ("halfwave_dipole", "L1_halfwave_dipole_x_1p2G", "x", base_center, "orientation_x_halfwave"),
        ("halfwave_dipole", "L1_halfwave_dipole_y_1p2G", "y", base_center, "orientation_y_halfwave"),
        (
            "short_dipole",
            "L1_short_dipole_z_offset_xp25_1p2G",
            "z",
            shifted(base_center, (0.25, 0.0, 0.0)),
            "off_axis_x_translation_short",
        ),
        (
            "halfwave_dipole",
            "L1_halfwave_dipole_z_offset_yp25_1p2G",
            "z",
            shifted(base_center, (0.0, 0.25, 0.0)),
            "off_axis_y_translation_halfwave",
        ),
    ]
    return [
        build_axis_case(templates[source_type], index, sample_id, axis, center, role)
        for index, (source_type, sample_id, axis, center, role) in enumerate(specs, start=1)
    ]


def translated_probe_rows(
    base_probe_rows: list[dict[str, str]],
    cases: list[dict[str, Any]],
    reference_center: tuple[float, float, float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in cases:
        sample_id = str(case["sample_id"])
        center = parse_xyz(str(case["center_xyz_m"]))
        delta = tuple(center[index] - reference_center[index] for index in range(3))
        for probe in base_probe_rows:
            original_position = parse_xyz(",".join([probe["x_m"], probe["y_m"], probe["z_m"]]))
            position = shifted(original_position, delta)
            radius, theta, phi = spherical_angles(position)
            updated = dict(probe)
            updated.update(
                {
                    "sample_id": sample_id,
                    "x_m": f"{position[0]:.12g}",
                    "y_m": f"{position[1]:.12g}",
                    "z_m": f"{position[2]:.12g}",
                    "radius_m": f"{radius:.12g}",
                    "theta_deg": f"{theta:.12g}",
                    "phi_deg": f"{phi:.12g}",
                    "source_center_x_m": f"{center[0]:.12g}",
                    "source_center_y_m": f"{center[1]:.12g}",
                    "source_center_z_m": f"{center[2]:.12g}",
                    "source_family_role": case["validation_role"],
                }
            )
            rows.append(updated)
    return rows


def validation_matrix(axis_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in axis_cases:
        rows.append(
            {
                "validation_id": case["sample_id"],
                "case_kind": "single_axis_aligned",
                "automation_status": "ready_for_cst_project_generation",
                "case_csv": "level1_source_family_axis_aligned_cases.csv",
                "probe_csv": "level1_source_family_probe_points.csv",
                "proof_role": "independent CST source-family row for frozen E/H Huygens rule",
                "blocker": "",
            }
        )
    rows.extend(
        [
            {
                "validation_id": "L1_short_dipole_tilt_xz45_1p2G",
                "case_kind": "single_tilted",
                "automation_status": "manual_or_next_generator_needed",
                "case_csv": "",
                "probe_csv": "",
                "proof_role": "tests arbitrary-axis source orientation after x/y axis-aligned gate",
                "blocker": "CST cylinder arbitrary-axis history is not yet promoted to automated generation",
            },
            {
                "validation_id": "L1_two_short_dipole_xy_pair_1p2G",
                "case_kind": "multi_source",
                "automation_status": "manual_or_next_generator_needed",
                "case_csv": "",
                "probe_csv": "",
                "proof_role": "tests superposed source interaction under the same frozen Huygens rule",
                "blocker": "single-dipole CST generator must be extended to multiple radiators and ports",
            },
        ]
    )
    return rows


def command_rows(case_csv: Path, probe_csv: Path, cases: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = [
        {
            "step_order": "1",
            "sample_id": "*",
            "field_kind": "*",
            "stage": "refresh_source_family_workpack",
            "command": "python code\\prepare_cst_huygens_source_family_workpack.py",
            "expected_output": rel(DEFAULT_OUT_DIR / "source_family_workpack_summary.json"),
        },
        {
            "step_order": "2",
            "sample_id": "*",
            "field_kind": "e",
            "stage": "generate_axis_aligned_efield_projects",
            "command": (
                "python code\\run_cst_level1_required_automation.py "
                f"--level1-csv {rel(case_csv)} "
                f"--probe-csv {rel(probe_csv)} "
                f"--out-dir {DEFAULT_E_PROJECT_DIR} "
                "--probe-mode efield"
            ),
            "expected_output": str(DEFAULT_E_PROJECT_DIR / "cst_automation_summary.json"),
        },
        {
            "step_order": "3",
            "sample_id": "*",
            "field_kind": "h",
            "stage": "generate_axis_aligned_hfield_projects",
            "command": (
                "python code\\run_cst_level1_required_automation.py "
                f"--level1-csv {rel(case_csv)} "
                f"--probe-csv {rel(probe_csv)} "
                f"--out-dir {DEFAULT_H_PROJECT_DIR} "
                "--probe-mode hfield"
            ),
            "expected_output": str(DEFAULT_H_PROJECT_DIR / "cst_automation_summary.json"),
        },
    ]
    order = 10
    for case in cases:
        sample_id = str(case["sample_id"])
        project_name = str(case["cst_project"])
        for field_kind, project_dir, solve_dir, label in [
            ("e", DEFAULT_E_PROJECT_DIR, DEFAULT_E_SOLVE_DIR, "efield"),
            ("h", DEFAULT_H_PROJECT_DIR, DEFAULT_H_SOLVE_DIR, "hfield"),
        ]:
            trial_name = f"{sample_id}_{label}.cst"
            solved_project = solve_dir / trial_name
            summary_path = DEFAULT_SOLVER_SUMMARY_DIR / f"{sample_id}_{label}_solver_summary.json"
            stdout_path = DEFAULT_SOLVER_SUMMARY_DIR / f"{sample_id}_{label}_stdout.log"
            rows.append(
                {
                    "step_order": str(order),
                    "sample_id": sample_id,
                    "field_kind": field_kind,
                    "stage": f"solve_{label}_project",
                    "command": (
                        "python code\\run_cst_solver_project.py "
                        f"--project {project_dir / 'projects' / project_name} "
                        f"--out-dir {solve_dir} "
                        f"--trial-name {trial_name} "
                        f"--summary-out {rel(summary_path)} "
                        f"--stdout-log {rel(stdout_path)} "
                        "--timeout-seconds 600 --poll-seconds 20"
                    ),
                    "expected_output": rel(summary_path),
                }
            )
            order += 1
            rows.append(
                {
                    "step_order": str(order),
                    "sample_id": sample_id,
                    "field_kind": field_kind,
                    "stage": f"export_local_{label}_probe_csv",
                    "command": (
                        "python code\\export_cst_meshsafe_huygens_results.py "
                        f"--field-kind {field_kind} --attempt-export --overwrite "
                        f"--project {solved_project} "
                        f"--case-csv {rel(case_csv)} "
                        f"--probe-csv {rel(probe_csv)} "
                        f"--sample-id {sample_id} "
                        f"--out-dir {rel(DEFAULT_EXPORT_OUT_DIR / sample_id / field_kind)}"
                    ),
                    "expected_output": rel(
                        Path(str(case["nearfield_export"]).replace("_local_efield.csv", f"_local_{label}.csv"))
                    ),
                }
            )
            order += 1
    return rows


def write_readme(
    out_dir: Path,
    case_csv: Path,
    probe_csv: Path,
    matrix_csv: Path,
    commands_csv: Path,
    summary: dict[str, Any],
) -> None:
    lines = [
        "# CST Huygens Source-Family Workpack",
        "",
        "This workpack is the next independent CST validation gate after the frozen real E/H rule and rotation-covariance check.",
        "",
        "## Current Scope",
        "",
        f"- Automation-ready axis-aligned single-source cases: `{summary['axis_aligned_case_count']}`",
        f"- Case-specific local Huygens probe rows: `{summary['probe_row_count']}`",
        "- Frozen rule to test after export: `eh_love_equivalence_minus_j96`",
        "- Per-source retuning is not allowed for this gate.",
        "",
        "## Files",
        "",
        "| File | Purpose |",
        "|---|---|",
        f"| `{case_csv.name}` | Axis-aligned x/y/off-axis source-family CST cases ready for project generation. |",
        f"| `{probe_csv.name}` | Case-scoped local Huygens probe points; scripts filter rows by `sample_id`. |",
        f"| `{matrix_csv.name}` | Full validation matrix, including tilted and multi-source gates that still need a generator/manual build. |",
        f"| `{commands_csv.name}` | Ordered project-generation, solver, and ResultTree export commands. |",
        "| `source_family_workpack_summary.json` | Machine-readable workpack status. |",
        "",
        "## Interpretation",
        "",
        "Passing the existing rotation-covariance gate proves that the Python operator is coordinate-consistent. This workpack asks a stronger question: does the same frozen E/H rule remain accepted on independent CST solves that were not used to tune the rule?",
        "",
        "The current automation-ready set covers x/y orientation and off-axis translation for the two Level 1 dipole lengths. Tilted and multi-source cases remain listed as explicit next gates rather than silently treated as solved.",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare independent CST Huygens source-family validation workpack.")
    parser.add_argument("--required-cases", type=Path, default=DEFAULT_REQUIRED_CASES)
    parser.add_argument("--required-probes", type=Path, default=DEFAULT_REQUIRED_PROBES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    required_cases = read_csv_rows(args.required_cases)
    required_probes = read_csv_rows(args.required_probes)
    templates = case_template_by_source(required_cases)
    axis_cases = build_axis_cases(templates)
    reference_center = parse_xyz(templates["short_dipole"]["center_xyz_m"])
    probe_rows = translated_probe_rows(required_probes, axis_cases, reference_center)
    matrix_rows = validation_matrix(axis_cases)

    case_csv = out_dir / "level1_source_family_axis_aligned_cases.csv"
    probe_csv = out_dir / "level1_source_family_probe_points.csv"
    matrix_csv = out_dir / "source_family_validation_matrix.csv"
    commands_csv = out_dir / "next_source_family_commands.csv"
    summary_json = out_dir / "source_family_workpack_summary.json"

    case_fields = list(axis_cases[0].keys())
    probe_fields = ["sample_id"] + [field for field in required_probes[0].keys() if field != "sample_id"] + [
        "source_center_x_m",
        "source_center_y_m",
        "source_center_z_m",
        "source_family_role",
    ]
    matrix_fields = [
        "validation_id",
        "case_kind",
        "automation_status",
        "case_csv",
        "probe_csv",
        "proof_role",
        "blocker",
    ]
    command_fields = ["step_order", "sample_id", "field_kind", "stage", "command", "expected_output"]

    write_csv_rows(case_csv, axis_cases, case_fields)
    write_csv_rows(probe_csv, probe_rows, probe_fields)
    write_csv_rows(matrix_csv, matrix_rows, matrix_fields)
    commands = command_rows(case_csv, probe_csv, axis_cases)
    write_csv_rows(commands_csv, commands, command_fields)

    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "stage_status": "source_family_workpack_ready",
        "source_required_cases": rel(args.required_cases),
        "source_required_probes": rel(args.required_probes),
        "out_dir": rel(out_dir),
        "frozen_rule_under_test": "eh_love_equivalence_minus_j96",
        "axis_aligned_case_count": len(axis_cases),
        "probe_count_per_case": len(required_probes),
        "probe_row_count": len(probe_rows),
        "validation_matrix_count": len(matrix_rows),
        "automation_ready_count": sum(
            1 for row in matrix_rows if row["automation_status"] == "ready_for_cst_project_generation"
        ),
        "pending_advanced_count": sum(
            1 for row in matrix_rows if row["automation_status"] != "ready_for_cst_project_generation"
        ),
        "files": {
            "case_csv": rel(case_csv),
            "probe_csv": rel(probe_csv),
            "validation_matrix": rel(matrix_csv),
            "commands_csv": rel(commands_csv),
            "readme": rel(out_dir / "README.md"),
        },
        "next_gate": (
            "Generate E/H CST projects for axis-aligned source-family cases, solve them, export local E/H "
            "probe CSVs and farfield references, then run the frozen Huygens rule without retuning."
        ),
        "boundary": (
            "Tilted and multi-source validation rows are tracked but not claimed as automation-ready in this workpack."
        ),
    }
    write_json(summary_json, summary)
    write_readme(out_dir, case_csv, probe_csv, matrix_csv, commands_csv, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
