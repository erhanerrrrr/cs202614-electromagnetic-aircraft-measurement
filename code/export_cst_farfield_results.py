from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CST_PYTHON = Path(
    r"D:\Program Files (x86)\CST Studio Suite 2025\Opera\code\bin\python.exe"
)
DEFAULT_PROBE_CSV = ROOT / "outputs" / "cst_operator_runbook" / "cst_probe_points_hemisphere_162.csv"
DEFAULT_FARFIELD_GRID = ROOT / "outputs" / "cst_operator_runbook" / "cst_farfield_sampling_grid.csv"
DEFAULT_SUMMARY_OUT = ROOT / "outputs" / "cst_farfield_export" / "export_summary.json"
DEFAULT_STDOUT_LOG = ROOT / "outputs" / "cst_farfield_export" / "cst_python_stdout.log"


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


def fmt_float(value: float) -> float:
    return float(f"{float(value):.16g}")


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def coerce_sequence(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        return [float(item) for item in value]
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list | tuple):
            return [float(item) for item in parsed]
    raise TypeError(f"Cannot coerce CST list value of type {type(value)!r}")


def spherical_to_cartesian(
    theta_deg: float,
    phi_deg: float,
    e_theta_real: float,
    e_theta_imag: float,
    e_phi_real: float,
    e_phi_imag: float,
) -> dict[str, tuple[float, float]]:
    theta = math.radians(theta_deg)
    phi = math.radians(phi_deg)
    e_theta = complex(e_theta_real, e_theta_imag)
    e_phi = complex(e_phi_real, e_phi_imag)

    theta_hat = (
        math.cos(theta) * math.cos(phi),
        math.cos(theta) * math.sin(phi),
        -math.sin(theta),
    )
    phi_hat = (-math.sin(phi), math.cos(phi), 0.0)
    ex = e_theta * theta_hat[0] + e_phi * phi_hat[0]
    ey = e_theta * theta_hat[1] + e_phi * phi_hat[1]
    ez = e_theta * theta_hat[2] + e_phi * phi_hat[2]
    return {
        "Ex": (ex.real, ex.imag),
        "Ey": (ey.real, ey.imag),
        "Ez": (ez.real, ez.imag),
    }


def select_farfield_item(model: Any, farfield_item: str) -> tuple[str, list[str]]:
    items = list(model.get_tree_items())
    farfield_items = [item for item in items if item.startswith("Farfields\\")]
    if farfield_item:
        model.SelectTreeItem(farfield_item)
        return farfield_item, farfield_items
    if not farfield_items:
        raise RuntimeError("No CST Farfields tree item found in the solved project")
    selected = farfield_items[0]
    model.SelectTreeItem(selected)
    return selected, farfield_items


def configure_farfield_plot(ff: Any, frequency_ghz: float) -> None:
    ff.Reset()
    ff.SetPlotMode("Efield")
    ff.SetFrequency(frequency_ghz)
    ff.SetScaleLinear(True)


def evaluate_farfield_points(
    ff: Any,
    points: list[dict[str, float]],
    frequency_ghz: float,
    radius_m: float,
    chunk_size: int,
) -> list[dict[str, float]]:
    components = {
        "e_theta_real": "Spherical linear theta re",
        "e_theta_imag": "Spherical linear theta im",
        "e_phi_real": "Spherical linear phi re",
        "e_phi_imag": "Spherical linear phi im",
    }
    out: list[dict[str, float]] = []
    for start in range(0, len(points), chunk_size):
        chunk = points[start : start + chunk_size]
        configure_farfield_plot(ff, frequency_ghz)
        for point in chunk:
            ff.AddListEvaluationPoint(
                float(point["theta_deg"]),
                float(point["phi_deg"]),
                radius_m,
                "spherical",
                "frequency",
                frequency_ghz,
            )
        ff.CalculateList("")
        values = {key: coerce_sequence(ff.GetList(component)) for key, component in components.items()}
        for key, seq in values.items():
            if len(seq) != len(chunk):
                raise RuntimeError(f"CST returned {len(seq)} values for {key}, expected {len(chunk)}")
        for idx, point in enumerate(chunk):
            row = dict(point)
            for key, seq in values.items():
                row[key] = fmt_float(seq[idx])
            out.append(row)
    return out


def build_probe_points(probe_rows: list[dict[str, str]]) -> list[dict[str, float]]:
    points: list[dict[str, float]] = []
    for row in probe_rows:
        points.append(
            {
                "sensor_id": int(row["sensor_id"]),
                "x_m": float(row["x_m"]),
                "y_m": float(row["y_m"]),
                "z_m": float(row["z_m"]),
                "theta_deg": float(row["theta_deg"]),
                "phi_deg": float(row["phi_deg"]),
                "radius_m": float(row["radius_m"]),
            }
        )
    return points


def build_farfield_grid(grid_rows: list[dict[str, str]]) -> list[dict[str, float]]:
    points: list[dict[str, float]] = []
    for row in grid_rows:
        points.append(
            {
                "grid_index": int(row["grid_index"]),
                "theta_deg": float(row["theta_deg"]),
                "phi_deg": float(row["phi_deg"]),
            }
        )
    return points


def build_nearfield_rows(
    sample_id: str,
    source_config: str,
    carrier_model: str,
    working_state: str,
    frequency_hz: float,
    project_path: Path,
    farfield_item: str,
    probe_points: list[dict[str, float]],
    evaluated: list[dict[str, float]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    eval_by_sensor = {int(row["sensor_id"]): row for row in evaluated}
    for point in probe_points:
        sensor_id = int(point["sensor_id"])
        field = eval_by_sensor[sensor_id]
        cart = spherical_to_cartesian(
            point["theta_deg"],
            point["phi_deg"],
            field["e_theta_real"],
            field["e_theta_imag"],
            field["e_phi_real"],
            field["e_phi_imag"],
        )
        for pol, value in cart.items():
            rows.append(
                {
                    "sample_id": sample_id,
                    "sensor_id": sensor_id,
                    "x_m": fmt_float(point["x_m"]),
                    "y_m": fmt_float(point["y_m"]),
                    "z_m": fmt_float(point["z_m"]),
                    "theta_deg": fmt_float(point["theta_deg"]),
                    "phi_deg": fmt_float(point["phi_deg"]),
                    "radius_m": fmt_float(point["radius_m"]),
                    "frequency_hz": int(round(frequency_hz)),
                    "polarization": pol,
                    "e_real": fmt_float(value[0]),
                    "e_imag": fmt_float(value[1]),
                    "source_config": source_config,
                    "carrier_model": carrier_model,
                    "working_state": working_state,
                    "cst_project": str(project_path),
                    "cst_farfield_item": farfield_item,
                    "extraction_method": "FarfieldPlot linear E-field, spherical-to-Cartesian at measurement radius",
                }
            )
    return rows


def build_farfield_rows(
    sample_id: str,
    source_config: str,
    carrier_model: str,
    working_state: str,
    frequency_hz: float,
    project_path: Path,
    farfield_item: str,
    radius_m: float,
    evaluated: list[dict[str, float]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in evaluated:
        power = row["e_theta_real"] ** 2 + row["e_theta_imag"] ** 2 + row["e_phi_real"] ** 2 + row["e_phi_imag"] ** 2
        rows.append(
            {
                "sample_id": sample_id,
                "grid_index": int(row["grid_index"]),
                "theta_deg": fmt_float(row["theta_deg"]),
                "phi_deg": fmt_float(row["phi_deg"]),
                "radius_m": fmt_float(radius_m),
                "frequency_hz": int(round(frequency_hz)),
                "e_theta_real": fmt_float(row["e_theta_real"]),
                "e_theta_imag": fmt_float(row["e_theta_imag"]),
                "e_phi_real": fmt_float(row["e_phi_real"]),
                "e_phi_imag": fmt_float(row["e_phi_imag"]),
                "power": fmt_float(power),
                "source_config": source_config,
                "carrier_model": carrier_model,
                "working_state": working_state,
                "cst_project": str(project_path),
                "cst_farfield_item": farfield_item,
                "extraction_method": "FarfieldPlot linear E-field list evaluation",
            }
        )
    return rows


def worker_run(args: argparse.Namespace) -> int:
    import cst.interface

    project = resolve_path(args.project)
    probe_csv = resolve_path(args.probe_csv)
    grid_csv = resolve_path(args.farfield_grid)
    nearfield_out = resolve_path(args.nearfield_out)
    farfield_out = resolve_path(args.farfield_out)
    summary_out = resolve_path(args.summary_out)

    frequency_hz = float(args.frequency_hz)
    frequency_ghz = frequency_hz / 1.0e9
    radius_m = float(args.radius_m)

    started_at = now_iso()
    probe_points = build_probe_points(read_csv_rows(probe_csv))
    farfield_grid = build_farfield_grid(read_csv_rows(grid_csv))

    de = cst.interface.DesignEnvironment()
    prj = de.open_project(str(project))
    try:
        model = prj.model3d
        selected_farfield_item, farfield_items = select_farfield_item(model, args.farfield_item)
        ff = model.FarfieldPlot
        probe_eval_input = [
            {
                "sensor_id": point["sensor_id"],
                "theta_deg": point["theta_deg"],
                "phi_deg": point["phi_deg"],
            }
            for point in probe_points
        ]
        probe_eval = evaluate_farfield_points(ff, probe_eval_input, frequency_ghz, radius_m, args.chunk_size)
        grid_eval = evaluate_farfield_points(ff, farfield_grid, frequency_ghz, radius_m, args.chunk_size)

        nearfield_rows = build_nearfield_rows(
            args.sample_id,
            args.source_config,
            args.carrier_model,
            args.working_state,
            frequency_hz,
            project,
            selected_farfield_item,
            probe_points,
            probe_eval,
        )
        farfield_rows = build_farfield_rows(
            args.sample_id,
            args.source_config,
            args.carrier_model,
            args.working_state,
            frequency_hz,
            project,
            selected_farfield_item,
            radius_m,
            grid_eval,
        )
        write_csv_rows(
            nearfield_out,
            nearfield_rows,
            [
                "sample_id",
                "sensor_id",
                "x_m",
                "y_m",
                "z_m",
                "theta_deg",
                "phi_deg",
                "radius_m",
                "frequency_hz",
                "polarization",
                "e_real",
                "e_imag",
                "source_config",
                "carrier_model",
                "working_state",
                "cst_project",
                "cst_farfield_item",
                "extraction_method",
            ],
        )
        write_csv_rows(
            farfield_out,
            farfield_rows,
            [
                "sample_id",
                "grid_index",
                "theta_deg",
                "phi_deg",
                "radius_m",
                "frequency_hz",
                "e_theta_real",
                "e_theta_imag",
                "e_phi_real",
                "e_phi_imag",
                "power",
                "source_config",
                "carrier_model",
                "working_state",
                "cst_project",
                "cst_farfield_item",
                "extraction_method",
            ],
        )
        summary = {
            "created_at": started_at,
            "completed_at": now_iso(),
            "status": "export_complete",
            "real_cst_api_used": True,
            "sample_id": args.sample_id,
            "project": str(project),
            "project_exists": project.exists(),
            "selected_farfield_item": selected_farfield_item,
            "available_farfield_items": farfield_items,
            "frequency_hz": int(round(frequency_hz)),
            "frequency_ghz": frequency_ghz,
            "radius_m": radius_m,
            "probe_csv": str(probe_csv),
            "farfield_grid": str(grid_csv),
            "nearfield_out": str(nearfield_out),
            "farfield_out": str(farfield_out),
            "probe_points": len(probe_points),
            "farfield_grid_points": len(farfield_grid),
            "nearfield_rows": len(nearfield_rows),
            "farfield_rows": len(farfield_rows),
            "chunk_size": args.chunk_size,
            "assumption": (
                "Nearfield rows are farfield-derived equivalent fields at the 13 m hemisphere: "
                "Etheta/Ephi are taken from CST FarfieldPlot in linear E-field mode and converted to Ex/Ey/Ez."
            ),
        }
        write_json(summary_out, summary)
    finally:
        try:
            prj.close()
        except Exception:
            pass
    return 0


def controller_run(args: argparse.Namespace) -> int:
    if not args.cst_python.exists():
        write_json(
            resolve_path(args.summary_out),
            {
                "created_at": now_iso(),
                "status": "failed",
                "real_cst_api_used": False,
                "error": f"CST Python not found: {args.cst_python}",
            },
        )
        return 1

    stdout_log = resolve_path(args.stdout_log)
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(args.cst_python),
        str(Path("src") / Path(__file__).name),
        "--worker",
        "--project",
        str(args.project),
        "--sample-id",
        args.sample_id,
        "--frequency-hz",
        str(args.frequency_hz),
        "--source-config",
        args.source_config,
        "--carrier-model",
        args.carrier_model,
        "--working-state",
        args.working_state,
        "--probe-csv",
        str(args.probe_csv),
        "--farfield-grid",
        str(args.farfield_grid),
        "--nearfield-out",
        str(args.nearfield_out),
        "--farfield-out",
        str(args.farfield_out),
        "--summary-out",
        str(args.summary_out),
        "--radius-m",
        str(args.radius_m),
        "--chunk-size",
        str(args.chunk_size),
    ]
    if args.farfield_item:
        command.extend(["--farfield-item", args.farfield_item])
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
    stdout_log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        summary_path = resolve_path(args.summary_out)
        previous = {}
        if summary_path.exists():
            try:
                previous = json.loads(summary_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                previous = {}
        previous.update(
            {
                "completed_at": now_iso(),
                "status": "failed",
                "controller_returncode": completed.returncode,
                "stdout_log": str(stdout_log),
            }
        )
        write_json(summary_path, previous)
    return completed.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export solved CST FarfieldPlot data to workflow nearfield/farfield CSV files."
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--project", required=True, help="Solved CST project path.")
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--frequency-hz", type=float, default=1.2e9)
    parser.add_argument("--source-config", default="")
    parser.add_argument("--carrier-model", default="level1_standard_source")
    parser.add_argument("--working-state", default="single_source_on")
    parser.add_argument("--probe-csv", type=Path, default=DEFAULT_PROBE_CSV)
    parser.add_argument("--farfield-grid", type=Path, default=DEFAULT_FARFIELD_GRID)
    parser.add_argument("--nearfield-out", required=True)
    parser.add_argument("--farfield-out", required=True)
    parser.add_argument("--summary-out", default=str(DEFAULT_SUMMARY_OUT))
    parser.add_argument("--stdout-log", default=str(DEFAULT_STDOUT_LOG))
    parser.add_argument("--farfield-item", default="")
    parser.add_argument("--radius-m", type=float, default=13.0)
    parser.add_argument("--chunk-size", type=int, default=250)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.worker:
        return worker_run(args)
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
