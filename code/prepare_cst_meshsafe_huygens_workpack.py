from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEVEL1_CSV = ROOT / "outputs" / "cst_operator_runbook" / "level1_required_operator_steps.csv"
DEFAULT_PRIOR_NODES = ROOT / "data" / "source_priors" / "huygens_surface" / "level1_local_sphere_r0p35_nodes.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "cst_meshsafe_huygens_workpack"
DEFAULT_SOLVER_SUMMARY_DIR = ROOT / "outputs" / "cst_solver_trials" / "meshsafe_huygens_required_shortpath"
DEFAULT_SHORTPATH_PROJECT_DIR = Path(r"C:\csttmp\huy_p")
DEFAULT_SHORTPATH_TRIAL_DIR = Path(r"C:\csttmp\huy_s")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def fnum(value: float) -> float:
    return float(f"{float(value):.12g}")


def spherical_from_global_xyz(x: float, y: float, z: float) -> tuple[float, float, float]:
    radius = math.sqrt(x * x + y * y + z * z)
    if radius <= 0.0:
        return 0.0, 0.0, 0.0
    theta = math.degrees(math.acos(max(-1.0, min(1.0, z / radius))))
    phi = math.degrees(math.atan2(y, x)) % 360.0
    return radius, theta, phi


def infer_prior_metadata(nodes: list[dict[str, str]]) -> dict[str, Any]:
    if not nodes:
        raise ValueError("prior node CSV is empty")
    prior_id = nodes[0]["prior_id"]
    surface_type = nodes[0]["surface_type"]
    xs = [float(row["x_m"]) for row in nodes]
    ys = [float(row["y_m"]) for row in nodes]
    zs = [float(row["z_m"]) for row in nodes]
    center = (sum(xs) / len(xs), sum(ys) / len(ys), sum(zs) / len(zs))
    local_radii = [
        math.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2 + (z - center[2]) ** 2)
        for x, y, z in zip(xs, ys, zs)
    ]
    return {
        "prior_id": prior_id,
        "surface_type": surface_type,
        "node_count": len(nodes),
        "center_x_m": fnum(center[0]),
        "center_y_m": fnum(center[1]),
        "center_z_m": fnum(center[2]),
        "mean_local_radius_m": fnum(sum(local_radii) / len(local_radii)),
        "min_local_radius_m": fnum(min(local_radii)),
        "max_local_radius_m": fnum(max(local_radii)),
    }


def build_probe_rows(nodes: list[dict[str, str]], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cx = float(metadata["center_x_m"])
    cy = float(metadata["center_y_m"])
    cz = float(metadata["center_z_m"])
    for sensor_id, row in enumerate(nodes):
        x = float(row["x_m"])
        y = float(row["y_m"])
        z = float(row["z_m"])
        radius, theta, phi = spherical_from_global_xyz(x, y, z)
        local_radius = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)
        rows.append(
            {
                "sensor_id": sensor_id,
                "node_id": int(row["node_id"]),
                "prior_id": row["prior_id"],
                "surface_type": row["surface_type"],
                "x_m": fnum(x),
                "y_m": fnum(y),
                "z_m": fnum(z),
                "radius_m": fnum(radius),
                "theta_deg": fnum(theta),
                "phi_deg": fnum(phi),
                "local_radius_m": fnum(local_radius),
                "normal_x": fnum(float(row["normal_x"])),
                "normal_y": fnum(float(row["normal_y"])),
                "normal_z": fnum(float(row["normal_z"])),
                "tangent1_x": fnum(float(row["tangent1_x"])),
                "tangent1_y": fnum(float(row["tangent1_y"])),
                "tangent1_z": fnum(float(row["tangent1_z"])),
                "tangent2_x": fnum(float(row["tangent2_x"])),
                "tangent2_y": fnum(float(row["tangent2_y"])),
                "tangent2_z": fnum(float(row["tangent2_z"])),
                "weight_m2": fnum(float(row["weight_m2"])),
                "cst_probe_field": "efield",
                "cst_coordinate_system": "Cartesian",
                "workflow_role": "local_huygens_surface_observation",
            }
        )
    return rows


def build_case_rows(cases: list[dict[str, str]], metadata: dict[str, Any]) -> list[dict[str, Any]]:
    prior_id = str(metadata["prior_id"])
    radius_tag = "r0p35" if "r0p35" in prior_id else prior_id.replace(".", "p")
    case_rows: list[dict[str, Any]] = []
    for case in cases:
        sample_id = case["sample_id"]
        updated = dict(case)
        updated["cst_project"] = f"CST_{sample_id}_meshsafe_huygens_{radius_tag}.cst"
        updated["nearfield_monitor"] = f"nearfield_local_huygens_{radius_tag}_{int(float(case['frequency_hz']) / 1e6)}MHz"
        updated["nearfield_export"] = (
            f"data/cst_exports/level1_meshsafe_huygens/{sample_id}_{prior_id}_local_efield.csv"
        )
        updated["farfield_export"] = f"data/cst_exports/level1_meshsafe_huygens/{sample_id}_farfield.csv"
        updated["acceptance_thresholds"] = (
            "mesh_feasibility_gate; local_huygens_surface_export; "
            "python_extrapolated_13m_compare_to_farfieldplot_reference"
        )
        updated["manual_step_summary"] = (
            "Build dipole from start/end coordinates; add feed/port and farfield monitor; "
            f"insert {metadata['node_count']} local Cartesian E-field probes on {prior_id}; "
            "solve locally before Python extrapolates fields to the 13 m measurement shell."
        )
        updated["workflow_role"] = "mesh_safe_local_huygens_observation"
        updated["source_prior_id"] = prior_id
        updated["local_probe_count"] = metadata["node_count"]
        updated["local_radius_m"] = metadata["mean_local_radius_m"]
        case_rows.append(updated)
    return case_rows


def build_export_contract() -> list[dict[str, str]]:
    return [
        ("sample_id", "string", "Level 1 case id."),
        ("frequency_hz", "integer", "Solved monitor frequency in Hz."),
        ("sensor_id", "integer", "Local Huygens probe id from level1_local_huygens_probe_points.csv."),
        ("node_id", "integer", "Huygens surface node id from the source-prior CSV."),
        ("prior_id", "string", "Huygens prior id, for this workpack level1_local_sphere_r0p35."),
        ("x_m", "float", "Cartesian probe x coordinate in meters."),
        ("y_m", "float", "Cartesian probe y coordinate in meters."),
        ("z_m", "float", "Cartesian probe z coordinate in meters."),
        ("normal_x", "float", "Outward surface normal x component."),
        ("normal_y", "float", "Outward surface normal y component."),
        ("normal_z", "float", "Outward surface normal z component."),
        ("tangent1_x", "float", "First local tangent x component."),
        ("tangent1_y", "float", "First local tangent y component."),
        ("tangent1_z", "float", "First local tangent z component."),
        ("tangent2_x", "float", "Second local tangent x component."),
        ("tangent2_y", "float", "Second local tangent y component."),
        ("tangent2_z", "float", "Second local tangent z component."),
        ("weight_m2", "float", "Surface quadrature weight associated with this node."),
        ("polarization", "string", "One of Ex, Ey, Ez; keep Cartesian fields for audit."),
        ("e_real", "float", "Real part of the electric field component."),
        ("e_imag", "float", "Imaginary part of the electric field component."),
        ("cst_project", "string", "CST project that produced the row."),
        ("cst_probe_item", "string", "CST result-tree item or probe label used for extraction."),
        (
            "extraction_method",
            "string",
            "Use 'CST local Cartesian E-field probe on mesh-safe Huygens surface'.",
        ),
    ]


def command_rows(out_dir: Path, project_out_dir: Path, case_csv: Path, probe_csv: Path) -> list[dict[str, str]]:
    short_project = project_out_dir / "projects" / "CST_L1_short_dipole_z_1p2G_meshsafe_huygens_r0p35.cst"
    short_summary = DEFAULT_SOLVER_SUMMARY_DIR / "h_short_solver_summary.json"
    short_stdout = DEFAULT_SOLVER_SUMMARY_DIR / "h_short_stdout.log"
    local_export = (
        ROOT
        / "data"
        / "cst_exports"
        / "level1_meshsafe_huygens"
        / "L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv"
    )
    return [
        {
            "step_order": "1",
            "stage": "refresh_workpack",
            "command": "python code\\prepare_cst_meshsafe_huygens_workpack.py",
            "expected_output": rel(out_dir / "meshsafe_huygens_workpack_summary.json"),
        },
        {
            "step_order": "2",
            "stage": "generate_cst_projects",
            "command": (
                "python code\\run_cst_level1_required_automation.py "
                f"--level1-csv {rel(case_csv)} "
                f"--probe-csv {rel(probe_csv)} "
                f"--out-dir {rel(project_out_dir)} "
                "--probe-mode efield"
            ),
            "expected_output": rel(project_out_dir / "cst_automation_summary.json"),
        },
        {
            "step_order": "3",
            "stage": "short_path_solver_gate",
            "command": (
                "python code\\run_cst_solver_project.py "
                f"--project {rel(short_project)} "
                f"--out-dir {DEFAULT_SHORTPATH_TRIAL_DIR} "
                "--trial-name h_short.cst "
                f"--summary-out {rel(short_summary)} "
                f"--stdout-log {rel(short_stdout)} "
                "--timeout-seconds 600 --poll-seconds 20"
            ),
            "expected_output": rel(short_summary),
        },
        {
            "step_order": "4",
            "stage": "result_tree_local_probe_export",
            "command": "python code\\export_cst_meshsafe_huygens_results.py --attempt-export",
            "expected_output": rel(local_export),
        },
    ]


def write_readme(
    out_dir: Path,
    metadata: dict[str, Any],
    case_csv: Path,
    probe_csv: Path,
    contract_csv: Path,
    commands_csv: Path,
    project_out_dir: Path,
) -> None:
    content = f"""# CST Mesh-Safe Huygens Workpack

This workpack converts the current G3 route from a remote 13 m Cartesian-probe
solve into a local Huygens-surface observation solve.

## Why This Exists

The previous true-nearfield CST trial proved that CST itself can start, but the
13 m probe shell expands the full-wave problem to about `4.6` billion mesh
cells and requires at least `3` MPI cluster nodes. This folder defines the next
mesh-safe route: CST observes a compact local surface near the Level 1 source;
Python extrapolates that local evidence to the 13 m measurement shell.

## Files

| File | Purpose |
|---|---|
| `{case_csv.name}` | Level 1 required cases rewritten to use mesh-safe local Huygens exports. |
| `{probe_csv.name}` | `{metadata['node_count']}` Cartesian E-field probe points on `{metadata['prior_id']}`. |
| `{contract_csv.name}` | CSV columns expected from local Huygens probe exports. |
| `{commands_csv.name}` | Next executable commands: refresh workpack, generate CST projects, run first solver gate, export local probe CSV. |
| `meshsafe_huygens_workpack_summary.json` | Machine-readable counts, source paths, and next gates. |

## Surface

- Prior: `{metadata['prior_id']}`
- Surface type: `{metadata['surface_type']}`
- Nodes/probes: `{metadata['node_count']}`
- Inferred center: `({metadata['center_x_m']}, {metadata['center_y_m']}, {metadata['center_z_m']}) m`
- Mean local radius: `{metadata['mean_local_radius_m']}` m

## Execution

```powershell
python code\\run_cst_level1_required_automation.py `
  --level1-csv {rel(case_csv)} `
  --probe-csv {rel(probe_csv)} `
  --out-dir {rel(project_out_dir)} `
  --probe-mode efield
```

Then run the first solver feasibility gate listed in `{commands_csv.name}`.
Use short ASCII CST work paths such as `{project_out_dir}` for project
generation and `{DEFAULT_SHORTPATH_TRIAL_DIR}` for the solver trial so CST's
internal result paths stay under its path-length limit. If the gate produces
local `.m3d` nearfield and `.ffm/.fme` farfield artifacts, run the ResultTree
export command listed in `{commands_csv.name}`. It reads solved `1D Results`
E-field probe curves and maps CST local probe values to `{contract_csv.name}`;
do not use CST's ASCII export from the `Field Monitors` view for this handoff.

## Current Solver Observation

The short-path `L1_short_dipole_z_1p2G` trial confirms that CST can open the
project and run the HF Time Domain solver without the `4.6` billion-cell mesh
limit. The 600 s gate ended as `aborted_keeping_results`, with CST keeping one
nearfield `.m3d` artifact and one farfield `.ffm/.fme` pair. The ResultTree
controller has now extracted `96 * 3 = 288` complex Cartesian E-field probe
rows from the kept results, so the immediate blocker has moved from CST
startup/export to Python Huygens extrapolation and reference comparison.

## Boundary

This is not final 13 m near-field evidence. It is a solver-feasible CST
observation package intended to replace the infeasible remote-probe solve.
Final G3 claims still require Python extrapolation to the 13 m shell, comparison
against the existing FarfieldPlot-derived reference, and repetition on the
second Level 1 source case before the local Huygens route becomes report-level
evidence.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a mesh-safe CST/Huygens Level 1 workpack.")
    parser.add_argument("--level1-csv", type=Path, default=DEFAULT_LEVEL1_CSV)
    parser.add_argument("--prior-nodes", type=Path, default=DEFAULT_PRIOR_NODES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--project-out-dir", type=Path, default=DEFAULT_SHORTPATH_PROJECT_DIR)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = read_csv_rows(args.level1_csv)
    nodes = read_csv_rows(args.prior_nodes)
    metadata = infer_prior_metadata(nodes)
    probe_rows = build_probe_rows(nodes, metadata)
    case_rows = build_case_rows(cases, metadata)

    probe_csv = out_dir / "level1_local_huygens_probe_points.csv"
    case_csv = out_dir / "level1_required_meshsafe_huygens_cases.csv"
    contract_csv = out_dir / "local_huygens_export_contract.csv"
    commands_csv = out_dir / "next_meshsafe_huygens_commands.csv"
    summary_json = out_dir / "meshsafe_huygens_workpack_summary.json"

    probe_fields = list(probe_rows[0].keys()) if probe_rows else []
    case_fields = list(case_rows[0].keys()) if case_rows else []
    write_csv_rows(probe_csv, probe_rows, probe_fields)
    write_csv_rows(case_csv, case_rows, case_fields)
    write_csv_rows(
        contract_csv,
        [
            {"column_name": column_name, "type": column_type, "meaning": meaning}
            for column_name, column_type, meaning in build_export_contract()
        ],
        ["column_name", "type", "meaning"],
    )
    commands = command_rows(out_dir, args.project_out_dir, case_csv, probe_csv)
    write_csv_rows(commands_csv, commands, ["step_order", "stage", "command", "expected_output"])

    summary = {
        "created_at": now_iso(),
        "stage_status": "workpack_ready",
        "source_level1_csv": rel(args.level1_csv),
        "source_prior_nodes": rel(args.prior_nodes),
        "out_dir": rel(out_dir),
        "project_out_dir": rel(args.project_out_dir),
        "case_count": len(case_rows),
        "probe_count": len(probe_rows),
        "expected_rows_per_case_if_component_long": len(probe_rows) * 3,
        "surface": metadata,
        "files": {
            "case_csv": rel(case_csv),
            "probe_csv": rel(probe_csv),
            "export_contract": rel(contract_csv),
            "commands_csv": rel(commands_csv),
            "readme": rel(out_dir / "README.md"),
        },
        "next_gate": "run_result_tree_local_probe_export_then_huygens_extrapolation_gate",
        "mesh_limit_context": {
            "remote_probe_status": "solver_mesh_limit",
            "remote_probe_mesh_cell_count_billion": 4.6,
            "remote_probe_required_mpi_nodes": 3,
            "decision": "keep_13m_shell_as_python_extrapolation_target_not_cst_mesh_probe_set",
        },
    }
    write_json(summary_json, summary)
    write_readme(out_dir, metadata, case_csv, probe_csv, contract_csv, commands_csv, args.project_out_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
