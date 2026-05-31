from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "cst_level2_element_library"
DEFAULT_CST_PYTHON = Path(
    r"D:\Program Files (x86)\CST Studio Suite 2025\Opera\code\bin\python.exe"
)
DEFAULT_CST_LIBRARY_ROOT = Path(r"D:\Program Files (x86)\CST Studio Suite 2025\AMD64")
DEFAULT_FREQUENCIES_HZ = [900_000_000, 1_050_000_000, 1_200_000_000, 1_350_000_000, 1_500_000_000]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv_rows(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fnum(value: float) -> str:
    return f"{float(value):.15g}"


def vba_str(value: str) -> str:
    return '"' + str(value).replace('"', '""') + '"'


def frequency_label(frequency_hz: int) -> str:
    return f"{int(round(frequency_hz / 1e6))}MHz"


def build_units_boundary_history(frequencies_hz: list[int]) -> str:
    min_ghz = min(frequencies_hz) / 1e9 * 0.90
    max_ghz = max(frequencies_hz) / 1e9 * 1.10
    return f"""
With Units
    .SetUnit ("Length", "m")
    .SetUnit ("Frequency", "GHz")
    .SetUnit ("Time", "ns")
End With
Solver.FrequencyRange "{fnum(min_ghz)}", "{fnum(max_ghz)}"
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


def build_geometry_history(axis: str, length_m: float, feed_gap_m: float, radius_m: float) -> str:
    half_len = length_m / 2.0
    half_gap = feed_gap_m / 2.0
    lower = (-half_len, -half_gap)
    upper = (half_gap, half_len)
    common = f"""
    .Reset
    .Component ("radiator")
    .Material ("PEC")
    .Axis ({vba_str(axis)})
    .OuterRadius ({fnum(radius_m)})
    .InnerRadius (0.0)
    .Segments (24)
"""
    if axis == "x":
        centers = """
    .Ycenter (0.0)
    .Zcenter (0.0)
"""
        range_cmd = "Xrange"
    elif axis == "y":
        centers = """
    .Xcenter (0.0)
    .Zcenter (0.0)
"""
        range_cmd = "Yrange"
    else:
        centers = """
    .Xcenter (0.0)
    .Ycenter (0.0)
"""
        range_cmd = "Zrange"
    return f"""
With Cylinder
{common}    .Name ("dipole_{axis}_lower")
{centers}    .{range_cmd} ({fnum(lower[0])}, {fnum(lower[1])})
    .Create
End With
With Cylinder
{common}    .Name ("dipole_{axis}_upper")
{centers}    .{range_cmd} ({fnum(upper[0])}, {fnum(upper[1])})
    .Create
End With
""".strip()


def build_port_history(axis: str, feed_gap_m: float, radius_m: float) -> str:
    half_gap = feed_gap_m / 2.0
    p1 = {"x": (-half_gap, 0.0, 0.0), "y": (0.0, -half_gap, 0.0), "z": (0.0, 0.0, -half_gap)}[axis]
    p2 = {"x": (half_gap, 0.0, 0.0), "y": (0.0, half_gap, 0.0), "z": (0.0, 0.0, half_gap)}[axis]
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
    .Radius "{fnum(radius_m)}"
    .Create
End With
""".strip()


def build_monitor_history(frequencies_hz: list[int]) -> str:
    blocks: list[str] = []
    for frequency_hz in frequencies_hz:
        label = frequency_label(frequency_hz)
        freq_ghz = frequency_hz / 1e9
        blocks.append(
            f"""
With Monitor
    .Reset
    .Name ({vba_str(f"farfield_{label}")})
    .Domain ("Frequency")
    .FieldType ("Farfield")
    .Frequency ({fnum(freq_ghz)})
    .Create
End With
""".strip()
        )
    return "\n".join(blocks)


def build_histories(axis: str, frequencies_hz: list[int]) -> list[tuple[str, str]]:
    lambda_min = 299_792_458.0 / max(frequencies_hz)
    length_m = lambda_min / 20.0
    feed_gap_m = min(0.002, length_m / 20.0)
    radius_m = min(0.001, max(0.00025, length_m / 125.0))
    return [
        ("01_units_boundary_background", build_units_boundary_history(frequencies_hz)),
        ("02_dipole_geometry", build_geometry_history(axis, length_m, feed_gap_m, radius_m)),
        ("03_discrete_feed_port", build_port_history(axis, feed_gap_m, radius_m)),
        ("04_farfield_monitors", build_monitor_history(frequencies_hz)),
    ]


def write_vba_recipe(path: Path, axis: str, histories: list[tuple[str, str]]) -> None:
    lines = [
        "' CST VBA history recipe generated by run_cst_level2_element_library.py",
        f"' Element axis: {axis}",
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
    worker_add_cst_paths(Path(config["cst_library_root"]))

    import cst.interface as ci  # type: ignore[import-not-found]

    project_dir = Path(config["project_dir"])
    recipe_dir = Path(config["recipe_dir"])
    axes = list(config["axes"])
    frequencies_hz = [int(value) for value in config["frequencies_hz"]]
    results: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "real_cst_api_used": True,
        "axes": axes,
        "frequencies_hz": frequencies_hz,
        "cases": results,
    }

    de = None
    try:
        de = ci.DesignEnvironment.new()
        for axis in axes:
            project_path = project_dir / f"CST_L2_element_short_dipole_{axis}_5freq.cst"
            recipe_path = recipe_dir / f"element_short_dipole_{axis}_history.bas"
            histories = build_histories(axis, frequencies_hz)
            status = "started"
            error = ""
            history_blocks_added = 0
            print(f"BUILD_START axis={axis} -> {project_path}")
            try:
                prj = de.new_mws()
                for name, history in histories:
                    print(f"ADD_HISTORY axis={axis} {name}")
                    prj.model3d.add_to_history(name, history)
                    history_blocks_added += 1
                project_dir.mkdir(parents=True, exist_ok=True)
                prj.save(str(project_path.resolve()), True)
                write_vba_recipe(recipe_path, axis, histories)
                status = "project_saved"
                print(f"BUILD_DONE axis={axis}")
            except Exception as exc:  # pragma: no cover - depends on CST runtime.
                error = repr(exc)
                if project_path.exists() and history_blocks_added == len(histories):
                    write_vba_recipe(recipe_path, axis, histories)
                    status = "project_exists_after_runtime_warning"
                    print(f"BUILD_WARNING axis={axis} {error}")
                else:
                    status = "failed"
                    print(f"BUILD_FAILED axis={axis} {error}")
            results.append(
                {
                    "axis": axis,
                    "project_path": str(project_path),
                    "project_exists": project_path.exists(),
                    "project_size_bytes": project_path.stat().st_size if project_path.exists() else 0,
                    "recipe_path": str(recipe_path),
                    "recipe_exists": recipe_path.exists(),
                    "history_block_count": len(histories),
                    "status": status,
                    "error": error,
                }
            )
    finally:
        if de is not None:
            try:
                de.close()
            except Exception as exc:  # pragma: no cover
                summary["close_error"] = repr(exc)

    summary.update(
        {
            "completed_at": now_iso(),
            "projects_created": sum(1 for row in results if row["project_exists"]),
            "all_projects_created": bool(results) and all(row["project_exists"] for row in results),
            "all_cases_ok": bool(results) and all(row["status"] != "failed" for row in results),
        }
    )
    write_json(summary_path, summary)
    return 0 if summary["all_cases_ok"] else 1


def build_readme(summary: dict[str, Any]) -> str:
    axes = ", ".join(summary.get("axes", []))
    freqs = ", ".join(str(freq) for freq in summary.get("frequencies_hz", []))
    return f"""# CST Level 2 element library

This folder stores solver-safe CST element projects used for Level 2 multi-source superposition.

## Why this exists

Putting all Level 2 sources at the full 12 m x 10 m x 8 m scale in one CST air-domain can make the mesh too large for the local workstation. The element-library route solves compact x/y/z short-dipole elements in CST, then combines their linear fields according to Level 2 source position, amplitude, and phase.

## Current run

- Axes: {axes}
- Frequencies Hz: {freqs}
- Real CST API used: {summary.get("real_cst_api_used")}
- Projects created: {summary.get("projects_created")}/{len(summary.get("axes", []))}

## Use

1. Solve the generated projects with `code/run_cst_solver_project.py`.
2. Export Level 2 pilot CSV files with `code/export_cst_level2_superposed_results.py`.
3. Validate with `code/merge_cst_level2_exports.py`.
"""


def controller_run(args: argparse.Namespace) -> int:
    out_dir = args.out_dir
    project_dir = out_dir / "projects"
    recipe_dir = out_dir / "vba_history"
    input_dir = out_dir / "input_snapshots"
    input_dir.mkdir(parents=True, exist_ok=True)
    config_path = out_dir / "worker_config.json"
    worker_summary_path = out_dir / "worker_summary.json"
    summary_path = out_dir / "element_library_summary.json"
    stdout_path = out_dir / "cst_python_stdout.log"
    manifest_path = out_dir / "element_project_manifest.csv"

    axes = [axis.strip().lower() for axis in args.axes.split(",") if axis.strip()]
    frequencies_hz = [int(item.strip()) for item in args.frequencies_hz.split(",") if item.strip()]
    config = {
        "created_at": now_iso(),
        "cst_library_root": str(args.cst_library_root),
        "project_dir": str(project_dir),
        "recipe_dir": str(recipe_dir),
        "axes": axes,
        "frequencies_hz": frequencies_hz,
    }
    write_json(config_path, config)

    command = [
        str(args.cst_python),
        str(Path("src") / Path(__file__).name),
        "--worker",
        str(config_path),
        str(worker_summary_path),
    ]
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
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    worker_summary = {}
    if worker_summary_path.exists():
        worker_summary = json.loads(worker_summary_path.read_text(encoding="utf-8"))

    manifest_rows = [
        {
            "axis": row.get("axis", ""),
            "project_path": row.get("project_path", ""),
            "project_exists": row.get("project_exists", False),
            "project_size_bytes": row.get("project_size_bytes", 0),
            "recipe_path": row.get("recipe_path", ""),
            "status": row.get("status", ""),
            "error": row.get("error", ""),
        }
        for row in worker_summary.get("cases", [])
    ]
    write_csv_rows(
        manifest_path,
        manifest_rows,
        ["axis", "project_path", "project_exists", "project_size_bytes", "recipe_path", "status", "error"],
    )
    summary = {
        "created_at": config["created_at"],
        "completed_at": now_iso(),
        "stage_status": "project_generation_complete"
        if completed.returncode == 0 and worker_summary.get("all_projects_created")
        else "failed_or_incomplete",
        "real_cst_api_used": bool(worker_summary.get("real_cst_api_used", False)),
        "controller_returncode": completed.returncode,
        "axes": axes,
        "frequencies_hz": frequencies_hz,
        "projects_created": int(worker_summary.get("projects_created", 0) or 0),
        "all_projects_created": bool(worker_summary.get("all_projects_created", False)),
        "manifest": str(manifest_path),
        "project_dir": str(project_dir),
        "recipe_dir": str(recipe_dir),
        "stdout_log": str(stdout_path),
        "worker_summary": str(worker_summary_path),
    }
    write_json(summary_path, summary)
    (out_dir / "README_cst_level2_element_library.md").write_text(build_readme(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["stage_status"] == "project_generation_complete" else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate solver-safe CST element-library projects for Level 2.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("worker_config", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("worker_summary", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--cst-library-root", type=Path, default=DEFAULT_CST_LIBRARY_ROOT)
    parser.add_argument("--out-dir", type=Path, default=OUT)
    parser.add_argument("--axes", default="x,y,z")
    parser.add_argument("--frequencies-hz", default=",".join(str(freq) for freq in DEFAULT_FREQUENCIES_HZ))
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
