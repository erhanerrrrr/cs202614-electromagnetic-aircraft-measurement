from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "cst_real_level1_projects"
RUNBOOK = ROOT / "outputs" / "cst_operator_runbook"
DEFAULT_LEVEL1_CSV = RUNBOOK / "level1_required_operator_steps.csv"
DEFAULT_PROBE_CSV = RUNBOOK / "cst_probe_points_hemisphere_162.csv"
DEFAULT_FARFIELD_GRID = RUNBOOK / "cst_farfield_sampling_grid.csv"
DEFAULT_CST_PYTHON = Path(
    r"D:\Program Files (x86)\CST Studio Suite 2025\Opera\code\bin\python.exe"
)
DEFAULT_CST_LIBRARY_ROOT = Path(r"D:\Program Files (x86)\CST Studio Suite 2025\AMD64")


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


def parse_xyz(value: str) -> tuple[float, float, float]:
    parts = [float(item.strip()) for item in str(value).split(",")]
    if len(parts) != 3:
        raise ValueError(f"Expected xyz triple, got: {value!r}")
    return parts[0], parts[1], parts[2]


def fnum(value: float) -> str:
    return f"{float(value):.15g}"


def vba_str(value: str) -> str:
    return '"' + str(value).replace('"', '""') + '"'


def infer_axis_from_segment(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    tolerance: float = 1e-9,
) -> str:
    delta = [end[index] - start[index] for index in range(3)]
    active = [index for index, value in enumerate(delta) if abs(value) > tolerance]
    if len(active) != 1:
        raise ValueError(
            "run_cst_level1_required_automation.py currently supports only "
            f"axis-aligned single dipoles; start={start}, end={end}"
        )
    return "xyz"[active[0]]


def axis_index(axis: str) -> int:
    key = str(axis).strip().lower()
    if key not in {"x", "y", "z"}:
        raise ValueError(f"unsupported dipole axis {axis!r}; expected x, y, or z")
    return {"x": 0, "y": 1, "z": 2}[key]


def select_case_probes(probes: list[dict[str, str]], sample_id: str) -> list[dict[str, str]]:
    if not probes:
        return []
    has_sample_ids = any(str(row.get("sample_id", "")).strip() for row in probes)
    if not has_sample_ids:
        return probes
    selected = [row for row in probes if str(row.get("sample_id", "")).strip() == sample_id]
    if selected:
        return selected
    global_rows = [row for row in probes if not str(row.get("sample_id", "")).strip()]
    if global_rows:
        return global_rows
    raise ValueError(f"probe CSV has sample_id-scoped rows but none for sample_id={sample_id!r}")


def limit_probes(probes: list[dict[str, str]], max_probes: int) -> list[dict[str, str]]:
    if max_probes <= 0:
        return probes
    has_sample_ids = any(str(row.get("sample_id", "")).strip() for row in probes)
    if not has_sample_ids:
        return probes[:max_probes]
    limited: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for row in probes:
        sample_id = str(row.get("sample_id", "")).strip()
        count = counts.get(sample_id, 0)
        if count < max_probes:
            limited.append(row)
            counts[sample_id] = count + 1
    return limited


def build_case_model(case: dict[str, str]) -> dict[str, Any]:
    frequency_hz = float(case["frequency_hz"])
    frequency_ghz = frequency_hz / 1e9
    center = parse_xyz(case["center_xyz_m"])
    start = parse_xyz(case["start_xyz_m"])
    end = parse_xyz(case["end_xyz_m"])
    length_m = float(case["length_m"])
    feed_gap_m = float(case["feed_gap_m"])
    inferred_axis = infer_axis_from_segment(start, end)
    declared_axis = str(case.get("orientation_axis", inferred_axis)).strip().lower() or inferred_axis
    if declared_axis != inferred_axis:
        raise ValueError(
            f"orientation_axis={declared_axis!r} does not match start/end axis {inferred_axis!r} "
            f"for sample_id={case.get('sample_id', '')!r}"
        )
    axis_i = axis_index(inferred_axis)
    axis_min = min(start[axis_i], end[axis_i])
    axis_max = max(start[axis_i], end[axis_i])
    lower_gap_edge = center[axis_i] - feed_gap_m / 2.0
    upper_gap_edge = center[axis_i] + feed_gap_m / 2.0
    conductor_radius_m = min(0.001, max(0.00025, length_m / 125.0))
    frequency_span = 0.10 * frequency_ghz

    return {
        "sample_id": case["sample_id"],
        "cst_project": case["cst_project"],
        "source_type": case["source_type"],
        "frequency_hz": frequency_hz,
        "frequency_ghz": frequency_ghz,
        "frequency_min_ghz": frequency_ghz - frequency_span,
        "frequency_max_ghz": frequency_ghz + frequency_span,
        "center_xyz_m": center,
        "start_xyz_m": start,
        "end_xyz_m": end,
        "orientation_axis": inferred_axis,
        "axis_index": axis_i,
        "length_m": length_m,
        "feed_gap_m": feed_gap_m,
        "lower_axis_range": (axis_min, lower_gap_edge),
        "upper_axis_range": (upper_gap_edge, axis_max),
        "conductor_radius_m": conductor_radius_m,
        "port_radius_m": conductor_radius_m,
        "nearfield_monitor": case["nearfield_monitor"],
        "farfield_monitor": case["farfield_monitor"],
        "nearfield_export": case["nearfield_export"],
        "farfield_export": case["farfield_export"],
        "acceptance_thresholds": case["acceptance_thresholds"],
    }


def build_units_boundary_history(model: dict[str, Any]) -> str:
    return f"""
With Units
    .SetUnit ("Length", "m")
    .SetUnit ("Frequency", "GHz")
    .SetUnit ("Time", "ns")
End With
Solver.FrequencyRange "{fnum(model['frequency_min_ghz'])}", "{fnum(model['frequency_max_ghz'])}"
With Boundary
    .Xmin ("expanded open")
    .Xmax ("expanded open")
    .Ymin ("expanded open")
    .Ymax ("expanded open")
    .Zmin ("expanded open")
    .Zmax ("expanded open")
    .Xsymmetry ("none")
    .Ysymmetry ("none")
    .Zsymmetry ("none")
    .ApplyInAllDirections (False)
End With
With Background
    .Reset
    .Type ("normal")
    .Epsilon (1.0)
    .Mu (1.0)
    .XminSpace (0.25)
    .XmaxSpace (0.25)
    .YminSpace (0.25)
    .YmaxSpace (0.25)
    .ZminSpace (0.25)
    .ZmaxSpace (0.25)
    .ApplyInAllDirections (False)
End With
""".strip()


def build_geometry_history(model: dict[str, Any]) -> str:
    radius = fnum(model["conductor_radius_m"])
    lower0, lower1 = model["lower_axis_range"]
    upper0, upper1 = model["upper_axis_range"]
    x, y, z = model["center_xyz_m"]
    axis = model["orientation_axis"]
    if axis == "x":
        center_lines = f"""
    .Ycenter ({fnum(y)})
    .Zcenter ({fnum(z)})
"""
        range_cmd = "Xrange"
    elif axis == "y":
        center_lines = f"""
    .Xcenter ({fnum(x)})
    .Zcenter ({fnum(z)})
"""
        range_cmd = "Yrange"
    else:
        center_lines = f"""
    .Xcenter ({fnum(x)})
    .Ycenter ({fnum(y)})
"""
        range_cmd = "Zrange"
    return f"""
With Cylinder
    .Reset
    .Name ("dipole_lower")
    .Component ("radiator")
    .Material ("PEC")
    .Axis ({vba_str(axis)})
    .OuterRadius ({radius})
    .InnerRadius (0.0)
{center_lines}    .{range_cmd} ({fnum(lower0)}, {fnum(lower1)})
    .Segments (24)
    .Create
End With
With Cylinder
    .Reset
    .Name ("dipole_upper")
    .Component ("radiator")
    .Material ("PEC")
    .Axis ({vba_str(axis)})
    .OuterRadius ({radius})
    .InnerRadius (0.0)
{center_lines}    .{range_cmd} ({fnum(upper0)}, {fnum(upper1)})
    .Segments (24)
    .Create
End With
""".strip()


def build_port_history(model: dict[str, Any]) -> str:
    p1 = list(model["center_xyz_m"])
    p2 = list(model["center_xyz_m"])
    half_gap = model["feed_gap_m"] / 2.0
    axis_i = int(model["axis_index"])
    p1[axis_i] -= half_gap
    p2[axis_i] += half_gap
    return f"""
With DiscretePort
    .Reset
    .PortNumber "1"
    .Type "Voltage"
    .Impedance "50.0"
    .Voltage "1.0"
    .SetP1 "False", "{fnum(p1[0])}", "{fnum(p1[1])}", "{fnum(p1[2])}"
    .SetP2 "False", "{fnum(p2[0])}", "{fnum(p2[1])}", "{fnum(p2[2])}"
    .InvertDirection "False"
    .LocalCoordinates "False"
    .Monitor "True"
    .Radius "{fnum(model['port_radius_m'])}"
    .Create
End With
""".strip()


def build_monitor_history(model: dict[str, Any]) -> str:
    freq = fnum(model["frequency_ghz"])
    return f"""
With Monitor
    .Reset
    .Name ({vba_str(model['nearfield_monitor'])})
    .Domain ("Frequency")
    .FieldType ("Efield")
    .Frequency ({freq})
    .Create
End With
With Monitor
    .Reset
    .Name ({vba_str(model['farfield_monitor'])})
    .Domain ("Frequency")
    .FieldType ("Farfield")
    .Frequency ({freq})
    .Create
End With
""".strip()


def build_probe_history(probes: list[dict[str, str]], probe_mode: str) -> str:
    blocks: list[str] = []
    for probe in probes:
        probe_id = int(probe["sensor_id"]) + 1
        if probe_mode == "efarfield":
            blocks.append(
                f"""
With Probe
    .Reset
    .ID {probe_id}
    .AutoLabel 1
    .Field ("efarfield")
    .SetCoordinateSystemType ("Spherical")
    .SetPosition1 ({fnum(float(probe['theta_deg']))})
    .SetPosition2 ({fnum(float(probe['phi_deg']))})
    .SetPosition3 ({fnum(float(probe['radius_m']))})
    .Orientation ("All")
    .Origin ("zero")
    .Create
End With
""".strip()
            )
            continue
        probe_field = "hfield" if probe_mode == "hfield" else "efield"
        blocks.append(
            f"""
With Probe
    .Reset
    .ID {probe_id}
    .AutoLabel 1
    .Field ({vba_str(probe_field)})
    .Xpos ({fnum(float(probe['x_m']))})
    .Ypos ({fnum(float(probe['y_m']))})
    .Zpos ({fnum(float(probe['z_m']))})
    .Orientation ("All")
    .SetCoordinateSystemType ("Cartesian")
    .Origin ("zero")
    .Create
End With
""".strip()
        )
    return "\n".join(blocks)


def chunks(rows: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
    return [rows[index : index + size] for index in range(0, len(rows), size)]


def build_case_histories(
    model: dict[str, Any], probes: list[dict[str, str]], probe_mode: str
) -> list[tuple[str, str]]:
    histories: list[tuple[str, str]] = [
        ("01_units_boundary_background", build_units_boundary_history(model)),
        ("02_dipole_geometry", build_geometry_history(model)),
        ("03_discrete_feed_port", build_port_history(model)),
        ("04_field_and_farfield_monitors", build_monitor_history(model)),
    ]
    if probe_mode != "none":
        for index, probe_chunk in enumerate(chunks(probes, 40), start=1):
            histories.append(
                (
                    f"05_{probe_mode}_probe_chunk_{index:02d}",
                    build_probe_history(probe_chunk, probe_mode),
                )
            )
    return histories


def write_vba_recipe(path: Path, histories: list[tuple[str, str]]) -> None:
    lines: list[str] = [
        "' CST VBA history recipe generated by run_cst_level1_required_automation.py",
        "' Use the generated .cst project as the primary artifact.",
        "",
    ]
    for name, code in histories:
        lines.append(f"' History block: {name}")
        lines.append(code)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def worker_add_cst_paths(cst_library_root: Path) -> None:
    sys.path.insert(0, str(cst_library_root / "python_cst_libraries"))
    sys.path.insert(0, str(cst_library_root))


def worker_run(config_path: Path, summary_path: Path) -> int:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    cst_library_root = Path(config["cst_library_root"])
    worker_add_cst_paths(cst_library_root)

    import cst.interface as ci  # type: ignore[import-not-found]

    probes: list[dict[str, str]] = config["probes"]
    project_dir = Path(config["project_dir"])
    recipe_dir = Path(config["recipe_dir"])
    run_solver = bool(config.get("run_solver", False))
    probe_mode = str(config.get("probe_mode", "efield"))
    cases: list[dict[str, str]] = config["cases"]
    results: list[dict[str, Any]] = []
    de = None
    worker_summary: dict[str, Any] = {
        "created_at": now_iso(),
        "real_cst_api_used": True,
        "run_solver": run_solver,
        "probe_mode": probe_mode,
        "probe_count": len(probes),
        "case_count": len(cases),
        "cases": results,
    }

    try:
        de = ci.DesignEnvironment.new()
        for case in cases:
            model = build_case_model(case)
            case_probes = select_case_probes(probes, model["sample_id"])
            project_path = project_dir / model["cst_project"]
            recipe_path = recipe_dir / f"{model['sample_id']}_model_history.bas"
            status = "started"
            error = ""
            histories = build_case_histories(model, case_probes, probe_mode)
            print(f"BUILD_START {model['sample_id']} -> {project_path}")
            try:
                prj = de.new_mws()
                for name, history_code in histories:
                    print(f"ADD_HISTORY {model['sample_id']} {name}")
                    prj.model3d.add_to_history(name, history_code)
                if run_solver:
                    print(f"RUN_SOLVER {model['sample_id']}")
                    prj.model3d.RunSolver()
                project_dir.mkdir(parents=True, exist_ok=True)
                prj.save(str(project_path.resolve()), True)
                write_vba_recipe(recipe_path, histories)
                status = "solved_project_saved" if run_solver else "project_saved"
                print(f"BUILD_DONE {model['sample_id']}")
            except Exception as exc:  # pragma: no cover - depends on CST runtime.
                status = "failed"
                error = repr(exc)
                print(f"BUILD_FAILED {model['sample_id']} {error}")
            results.append(
                {
                    "sample_id": model["sample_id"],
                    "source_type": model["source_type"],
                    "frequency_ghz": model["frequency_ghz"],
                    "project_path": str(project_path),
                    "project_exists": project_path.exists(),
                    "project_size_bytes": project_path.stat().st_size
                    if project_path.exists()
                    else 0,
                    "recipe_path": str(recipe_path),
                    "recipe_exists": recipe_path.exists(),
                    "orientation_axis": model["orientation_axis"],
                    "probe_count": len(case_probes),
                    "history_block_count": len(histories),
                    "conductor_radius_m": model["conductor_radius_m"],
                    "feed_gap_m": model["feed_gap_m"],
                    "nearfield_export_contract": model["nearfield_export"],
                    "farfield_export_contract": model["farfield_export"],
                    "acceptance_thresholds": model["acceptance_thresholds"],
                    "status": status,
                    "error": error,
                }
            )
    finally:
        if de is not None:
            try:
                de.close()
            except Exception as exc:  # pragma: no cover - depends on CST runtime.
                worker_summary["close_error"] = repr(exc)

    all_created = bool(results) and all(row["project_exists"] for row in results)
    all_ok = all_created and all(row["status"] != "failed" for row in results)
    worker_summary.update(
        {
            "completed_at": now_iso(),
            "all_projects_created": all_created,
            "all_cases_ok": all_ok,
            "projects_created": sum(1 for row in results if row["project_exists"]),
        }
    )
    write_json(summary_path, worker_summary)
    return 0 if all_ok else 1


def build_readme(summary: dict[str, Any], manifest_path: Path) -> str:
    projects_created = summary.get("projects_created", 0)
    case_count = summary.get("case_count", 0)
    probe_count = summary.get("probe_count", 0)
    solver_note = (
        "This run also requested solver execution."
        if summary.get("run_solver")
        else "This run generated solver-ready CST projects only; nearfield/farfield CSV exports are still the next gate."
    )
    lines = [
        "# CST Level 1 Required Project Automation",
        "",
        "Purpose: generate real CST project files for the two Level 1 required standard-source cases from the operator runbook.",
        "",
        f"- Real CST API used: {summary.get('real_cst_api_used')}",
        f"- Projects created: {projects_created}/{case_count}",
        f"- Hemisphere nearfield probes inserted per project: {probe_count}",
        f"- Probe mode: `{summary.get('probe_mode')}`",
        f"- Solver requested: {summary.get('run_solver')}",
        f"- Manifest: `{manifest_path.name}`",
        f"- Status: `{summary.get('stage_status')}`",
        "",
        solver_note,
        "",
        "Important files:",
        "",
        "- `projects/*.cst`: CST Studio Suite project files generated through `cst.interface`.",
        "- `vba_history/*.bas`: exact VBA history blocks injected into CST, kept for review and manual replay.",
        "- `input_snapshots/*.csv`: copied source tables used for this generation run.",
        "- `cst_automation_summary.json`: machine-readable run summary.",
        "- `cst_automation_stdout.txt`: raw CST Python stdout/stderr log.",
        "",
        "Next required gate: open/run these projects in CST, solve them, and export the contracted Level 1 nearfield/farfield CSV files under `data/cst_exports/level1`.",
        "",
    ]
    return "\n".join(lines)


def controller_run(args: argparse.Namespace) -> int:
    out_dir = args.out_dir.resolve()
    project_dir = out_dir / "projects"
    recipe_dir = out_dir / "vba_history"
    input_dir = out_dir / "input_snapshots"
    summary_path = out_dir / "cst_automation_summary.json"
    worker_summary_path = out_dir / "cst_worker_summary.json"
    config_path = out_dir / "cst_worker_input.json"
    stdout_path = out_dir / "cst_automation_stdout.txt"
    manifest_path = out_dir / "cst_level1_project_manifest.csv"
    readme_path = out_dir / "README_cst_level1_automation.md"

    out_dir.mkdir(parents=True, exist_ok=True)
    input_dir.mkdir(parents=True, exist_ok=True)
    for source in [args.level1_csv, args.probe_csv, DEFAULT_FARFIELD_GRID]:
        if source.exists():
            shutil.copy2(source, input_dir / source.name)

    cases = read_csv_rows(args.level1_csv)
    probes = read_csv_rows(args.probe_csv)
    if args.max_probes:
        probes = limit_probes(probes, args.max_probes)

    config = {
        "created_at": now_iso(),
        "cst_library_root": str(args.cst_library_root),
        "project_dir": str(project_dir),
        "recipe_dir": str(recipe_dir),
        "cases": cases,
        "probes": probes,
        "run_solver": args.run_solver,
        "probe_mode": args.probe_mode,
    }
    write_json(config_path, config)

    if not args.cst_python.exists():
        summary = {
            "created_at": now_iso(),
            "stage_status": "failed",
            "error": f"CST Python not found: {args.cst_python}",
            "cst_python": str(args.cst_python),
            "real_cst_api_used": False,
            "run_solver": args.run_solver,
            "probe_mode": args.probe_mode,
            "case_count": len(cases),
            "probe_count": len(probes),
        }
        write_json(summary_path, summary)
        readme_path.write_text(build_readme(summary, manifest_path), encoding="utf-8")
        return 1

    command = [
        str(args.cst_python),
        str(Path(__file__).resolve()),
        "--worker",
        str(config_path),
        str(worker_summary_path),
    ]
    started_at = now_iso()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=args.timeout_seconds,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")

    worker_summary: dict[str, Any] = {}
    if worker_summary_path.exists():
        worker_summary = json.loads(worker_summary_path.read_text(encoding="utf-8"))

    case_results = worker_summary.get("cases", [])
    manifest_rows: list[dict[str, Any]] = []
    for row in case_results:
        manifest_rows.append(
            {
                "sample_id": row.get("sample_id", ""),
                "source_type": row.get("source_type", ""),
                "frequency_ghz": row.get("frequency_ghz", ""),
                "orientation_axis": row.get("orientation_axis", ""),
                "project_path": row.get("project_path", ""),
                "project_exists": row.get("project_exists", False),
                "project_size_bytes": row.get("project_size_bytes", 0),
                "recipe_path": row.get("recipe_path", ""),
                "probe_count": row.get("probe_count", 0),
                "history_block_count": row.get("history_block_count", 0),
                "feed_gap_m": row.get("feed_gap_m", ""),
                "conductor_radius_m": row.get("conductor_radius_m", ""),
                "nearfield_export_contract": row.get("nearfield_export_contract", ""),
                "farfield_export_contract": row.get("farfield_export_contract", ""),
                "status": row.get("status", ""),
                "error": row.get("error", ""),
            }
        )
    if manifest_rows:
        write_csv_rows(
            manifest_path,
            manifest_rows,
            [
                "sample_id",
                "source_type",
                "frequency_ghz",
                "orientation_axis",
                "project_path",
                "project_exists",
                "project_size_bytes",
                "recipe_path",
                "probe_count",
                "history_block_count",
                "feed_gap_m",
                "conductor_radius_m",
                "nearfield_export_contract",
                "farfield_export_contract",
                "status",
                "error",
            ],
        )

    projects_created = int(worker_summary.get("projects_created", 0))
    stage_status = (
        "project_generation_complete"
        if completed.returncode == 0 and projects_created == len(cases)
        else "failed_or_incomplete"
    )
    summary = {
        "created_at": started_at,
        "completed_at": now_iso(),
        "stage_status": stage_status,
        "real_cst_api_used": bool(worker_summary.get("real_cst_api_used", False)),
        "cst_python": str(args.cst_python),
        "cst_library_root": str(args.cst_library_root),
        "controller_returncode": completed.returncode,
        "run_solver": args.run_solver,
        "probe_mode": args.probe_mode,
        "case_count": len(cases),
        "probe_count": len(probes),
        "projects_created": projects_created,
        "all_projects_created": bool(worker_summary.get("all_projects_created", False)),
        "all_cases_ok": bool(worker_summary.get("all_cases_ok", False)),
        "manifest": str(manifest_path),
        "stdout_log": str(stdout_path),
        "worker_summary": str(worker_summary_path),
        "project_dir": str(project_dir),
        "recipe_dir": str(recipe_dir),
        "input_snapshots": str(input_dir),
        "next_blocking_gate": "solve_and_export_level1_nearfield_farfield_csv",
        "notes": [
            "Generated .cst projects are real CST API artifacts.",
            "This does not yet prove final numerical Level 1 metrics until CST solves and CSV exports are completed.",
        ],
    }
    write_json(summary_path, summary)
    readme_path.write_text(build_readme(summary, manifest_path), encoding="utf-8")

    return 0 if stage_status == "project_generation_complete" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Level 1 required CST projects through CST Python API."
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("worker_config", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("worker_summary", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--cst-library-root", type=Path, default=DEFAULT_CST_LIBRARY_ROOT)
    parser.add_argument("--level1-csv", type=Path, default=DEFAULT_LEVEL1_CSV)
    parser.add_argument("--probe-csv", type=Path, default=DEFAULT_PROBE_CSV)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    parser.add_argument("--max-probes", type=int, default=0)
    parser.add_argument(
        "--probe-mode",
        choices=["efield", "hfield", "efarfield", "none"],
        default="efield",
        help=(
            "efield uses Cartesian E-field probes and may enlarge the mesh; "
            "hfield uses Cartesian H-field probes on the same probe CSV; "
            "efarfield preserves hemisphere angular sampling without meshing the measurement radius."
        ),
    )
    parser.add_argument("--run-solver", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.worker:
        if not args.worker_config or not args.worker_summary:
            raise SystemExit("--worker requires config and summary paths")
        return worker_run(Path(args.worker_config), Path(args.worker_summary))
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
