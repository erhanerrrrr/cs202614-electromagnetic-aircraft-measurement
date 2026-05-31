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
DEFAULT_LEVEL2_CASES = ROOT / "outputs" / "cst_level2_plan" / "level2_case_manifest.csv"
DEFAULT_LEVEL2_SOURCES = ROOT / "outputs" / "cst_level2_plan" / "level2_source_manifest.csv"
DEFAULT_ELEMENT_DIR = ROOT / "outputs" / "cst_level2_element_trials"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_level2_superposed_export"
C0 = 299_792_458.0


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


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


def coerce_sequence(value: Any) -> list[float]:
    if isinstance(value, (list, tuple)):
        return [float(item) for item in value]
    if isinstance(value, str):
        parsed = ast.literal_eval(value)
        if isinstance(parsed, (list, tuple)):
            return [float(item) for item in parsed]
    raise TypeError(f"Cannot coerce CST list value of type {type(value)!r}")


def spherical_basis(theta_rad: float, phi_rad: float) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    sin_t = math.sin(theta_rad)
    cos_t = math.cos(theta_rad)
    sin_p = math.sin(phi_rad)
    cos_p = math.cos(phi_rad)
    r_hat = (sin_t * cos_p, sin_t * sin_p, cos_t)
    e_theta = (cos_t * cos_p, cos_t * sin_p, -sin_t)
    e_phi = (-sin_p, cos_p, 0.0)
    return r_hat, e_theta, e_phi


def vector_to_angles(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = vector
    radius = math.sqrt(x * x + y * y + z * z)
    theta = math.degrees(math.acos(max(-1.0, min(1.0, z / max(radius, 1e-15)))))
    phi = math.degrees(math.atan2(y, x)) % 360.0
    return theta, phi, radius


def spherical_field_to_cartesian(
    theta_deg: float,
    phi_deg: float,
    e_theta: complex,
    e_phi: complex,
) -> tuple[complex, complex, complex]:
    _, theta_hat, phi_hat = spherical_basis(math.radians(theta_deg), math.radians(phi_deg))
    ex = e_theta * theta_hat[0] + e_phi * phi_hat[0]
    ey = e_theta * theta_hat[1] + e_phi * phi_hat[1]
    ez = e_theta * theta_hat[2] + e_phi * phi_hat[2]
    return ex, ey, ez


def axis_from_orientation(source: dict[str, str]) -> str:
    values = [
        abs(float(source["orientation_x"])),
        abs(float(source["orientation_y"])),
        abs(float(source["orientation_z"])),
    ]
    return ["x", "y", "z"][max(range(3), key=lambda idx: values[idx])]


def frequency_label(frequency_hz: int) -> str:
    return f"{int(round(frequency_hz / 1e6))}MHz"


def build_level2_farfield_grid() -> list[dict[str, float]]:
    theta_values = [2.0 + idx * (86.0 / 18.0) for idx in range(19)]
    phi_values = [idx * 10.0 for idx in range(36)]
    rows: list[dict[str, float]] = []
    grid_index = 0
    for theta in theta_values:
        for phi in phi_values:
            rows.append({"grid_index": grid_index, "theta_deg": theta, "phi_deg": phi})
            grid_index += 1
    return rows


def build_probe_points(rows: list[dict[str, str]]) -> list[dict[str, float]]:
    out: list[dict[str, float]] = []
    for row in rows:
        out.append(
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
    return out


def project_for_axis(element_dir: Path, axis: str) -> Path:
    return element_dir / f"{axis}_solver_safe" / f"CST_L2_element_short_dipole_{axis}_5freq_solver_safe.cst"


class ElementProject:
    def __init__(self, env: Any, path: Path, axis: str) -> None:
        self.axis = axis
        self.path = path
        self.project = env.open_project(str(path))
        self.model = self.project.model3d
        self.ff = self.model.FarfieldPlot
        self.cache: dict[tuple[int, str], list[dict[str, float]]] = {}

    def close(self) -> None:
        try:
            self.project.close()
        except Exception:
            pass

    def evaluate(
        self,
        frequency_hz: int,
        points: list[dict[str, float]],
        chunk_size: int,
    ) -> list[dict[str, float]]:
        cache_key = (frequency_hz, json.dumps(points, sort_keys=True))
        if cache_key in self.cache:
            return self.cache[cache_key]
        label = frequency_label(frequency_hz)
        tree_item = f"Farfields\\farfield_{label} [1]"
        frequency_ghz = frequency_hz / 1e9
        components = {
            "e_theta_real": "Spherical linear theta re",
            "e_theta_imag": "Spherical linear theta im",
            "e_phi_real": "Spherical linear phi re",
            "e_phi_imag": "Spherical linear phi im",
        }
        out: list[dict[str, float]] = []
        self.model.SelectTreeItem(tree_item)
        for start in range(0, len(points), chunk_size):
            chunk = points[start : start + chunk_size]
            self.ff.Reset()
            self.ff.SetPlotMode("Efield")
            self.ff.SetFrequency(frequency_ghz)
            self.ff.SetScaleLinear(True)
            for point in chunk:
                self.ff.AddListEvaluationPoint(
                    float(point["theta_deg"]),
                    float(point["phi_deg"]),
                    float(point["radius_m"]),
                    "spherical",
                    "frequency",
                    frequency_ghz,
                )
            self.ff.CalculateList("")
            values = {key: coerce_sequence(self.ff.GetList(component)) for key, component in components.items()}
            for key, seq in values.items():
                if len(seq) != len(chunk):
                    raise RuntimeError(f"CST returned {len(seq)} values for {key}, expected {len(chunk)}")
            for idx, point in enumerate(chunk):
                row = dict(point)
                for key, seq in values.items():
                    row[key] = float(seq[idx])
                out.append(row)
        self.cache[cache_key] = out
        return out


def filter_sample_rows(rows: list[dict[str, str]], sample_id: str) -> list[dict[str, str]]:
    return [row for row in rows if row["sample_id"].strip() == sample_id]


def manifest_sample_ids(rows: list[dict[str, str]]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for row in rows:
        sample_id = row["sample_id"].strip()
        if sample_id and sample_id not in seen:
            seen.add(sample_id)
            out.append(sample_id)
    return out


def selected_sample_ids(args: argparse.Namespace, case_rows_all: list[dict[str, str]]) -> list[str]:
    planned = manifest_sample_ids(case_rows_all)
    planned_set = set(planned)
    if args.all_samples:
        selected = planned
    elif args.sample_ids:
        selected = [item.strip() for item in args.sample_ids.split(",") if item.strip()]
    elif args.sample_id:
        selected = [args.sample_id.strip()]
    else:
        raise ValueError("Provide --sample-id, --sample-ids, or --all-samples.")

    unknown = [sample_id for sample_id in selected if sample_id not in planned_set]
    if unknown:
        raise ValueError(f"Unknown sample_id values: {', '.join(unknown)}")

    if args.missing_only:
        missing: list[str] = []
        for sample_id in selected:
            case_rows = filter_sample_rows(case_rows_all, sample_id)
            metadata = sample_metadata(case_rows)
            nearfield_out = resolve_path(metadata["nearfield_export"])
            farfield_out = resolve_path(metadata["farfield_export"])
            if not (nearfield_out.exists() and farfield_out.exists()):
                missing.append(sample_id)
        selected = missing
    if args.limit > 0:
        selected = selected[: args.limit]
    return selected


def sample_metadata(case_rows: list[dict[str, str]]) -> dict[str, str]:
    if not case_rows:
        raise ValueError("sample has no case rows")
    first = case_rows[0]
    return {
        "sample_id": first["sample_id"],
        "class_label": first["class_label"],
        "carrier_model": first["carrier_model"],
        "working_state": first["working_state"],
        "nearfield_export": first["nearfield_export"],
        "farfield_export": first["farfield_export"],
    }


def source_weight(source: dict[str, str]) -> complex:
    amp = float(source["relative_amplitude"])
    phase = math.radians(float(source["relative_phase_deg"]))
    return amp * complex(math.cos(phase), math.sin(phase))


def build_nearfield_for_frequency(
    frequency_hz: int,
    sources: list[dict[str, str]],
    probe_points: list[dict[str, float]],
    projects: dict[str, ElementProject],
    chunk_size: int,
) -> list[dict[str, complex]]:
    sums = [{"Ex": 0j, "Ey": 0j, "Ez": 0j} for _ in probe_points]
    for source in sources:
        axis = axis_from_orientation(source)
        project = projects[axis]
        sx = float(source["x_m"])
        sy = float(source["y_m"])
        sz = float(source["z_m"])
        eval_points: list[dict[str, float]] = []
        for point in probe_points:
            theta_deg, phi_deg, radius_m = vector_to_angles(
                (point["x_m"] - sx, point["y_m"] - sy, point["z_m"] - sz)
            )
            eval_points.append({"theta_deg": theta_deg, "phi_deg": phi_deg, "radius_m": radius_m})
        evaluated = project.evaluate(frequency_hz, eval_points, chunk_size)
        weight = source_weight(source)
        for idx, row in enumerate(evaluated):
            e_theta = complex(row["e_theta_real"], row["e_theta_imag"]) * weight
            e_phi = complex(row["e_phi_real"], row["e_phi_imag"]) * weight
            ex, ey, ez = spherical_field_to_cartesian(row["theta_deg"], row["phi_deg"], e_theta, e_phi)
            sums[idx]["Ex"] += ex
            sums[idx]["Ey"] += ey
            sums[idx]["Ez"] += ez
    return sums


def build_farfield_for_frequency(
    frequency_hz: int,
    sources: list[dict[str, str]],
    farfield_grid: list[dict[str, float]],
    projects: dict[str, ElementProject],
    radius_m: float,
    chunk_size: int,
) -> list[dict[str, complex]]:
    k = 2.0 * math.pi * frequency_hz / C0
    sums = [{"Etheta": 0j, "Ephi": 0j} for _ in farfield_grid]
    for source in sources:
        axis = axis_from_orientation(source)
        project = projects[axis]
        eval_points = [
            {"theta_deg": point["theta_deg"], "phi_deg": point["phi_deg"], "radius_m": radius_m}
            for point in farfield_grid
        ]
        evaluated = project.evaluate(frequency_hz, eval_points, chunk_size)
        base_weight = source_weight(source)
        sx = float(source["x_m"])
        sy = float(source["y_m"])
        sz = float(source["z_m"])
        for idx, row in enumerate(evaluated):
            r_hat, _, _ = spherical_basis(math.radians(row["theta_deg"]), math.radians(row["phi_deg"]))
            translation_phase = k * (r_hat[0] * sx + r_hat[1] * sy + r_hat[2] * sz)
            weight = base_weight * complex(math.cos(translation_phase), math.sin(translation_phase))
            sums[idx]["Etheta"] += complex(row["e_theta_real"], row["e_theta_imag"]) * weight
            sums[idx]["Ephi"] += complex(row["e_phi_real"], row["e_phi_imag"]) * weight
    return sums


def build_output_rows(
    metadata: dict[str, str],
    case_rows: list[dict[str, str]],
    sources: list[dict[str, str]],
    probe_points: list[dict[str, float]],
    farfield_grid: list[dict[str, float]],
    projects: dict[str, ElementProject],
    chunk_size: int,
    farfield_radius_m: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nearfield_rows: list[dict[str, Any]] = []
    farfield_rows: list[dict[str, Any]] = []
    for case in case_rows:
        frequency_hz = int(float(case["frequency_hz"]))
        nf_values = build_nearfield_for_frequency(frequency_hz, sources, probe_points, projects, chunk_size)
        ff_values = build_farfield_for_frequency(
            frequency_hz, sources, farfield_grid, projects, farfield_radius_m, chunk_size
        )
        for point, values in zip(probe_points, nf_values):
            for pol in ["Ex", "Ey", "Ez"]:
                value = values[pol]
                nearfield_rows.append(
                    {
                        "sample_id": metadata["sample_id"],
                        "sensor_id": int(point["sensor_id"]),
                        "x_m": fmt_float(point["x_m"]),
                        "y_m": fmt_float(point["y_m"]),
                        "z_m": fmt_float(point["z_m"]),
                        "theta_deg": fmt_float(point["theta_deg"]),
                        "phi_deg": fmt_float(point["phi_deg"]),
                        "radius_m": fmt_float(point["radius_m"]),
                        "frequency_hz": frequency_hz,
                        "polarization": pol,
                        "e_real": fmt_float(value.real),
                        "e_imag": fmt_float(value.imag),
                        "source_config": metadata["class_label"],
                        "carrier_model": metadata["carrier_model"],
                        "working_state": metadata["working_state"],
                        "extraction_method": "CST element-library FarfieldPlot superposition at sensor positions",
                    }
                )
        for point, values in zip(farfield_grid, ff_values):
            e_theta = values["Etheta"]
            e_phi = values["Ephi"]
            power = abs(e_theta) ** 2 + abs(e_phi) ** 2
            farfield_rows.append(
                {
                    "sample_id": metadata["sample_id"],
                    "grid_index": int(point["grid_index"]),
                    "theta_deg": fmt_float(point["theta_deg"]),
                    "phi_deg": fmt_float(point["phi_deg"]),
                    "radius_m": fmt_float(farfield_radius_m),
                    "frequency_hz": frequency_hz,
                    "e_theta_real": fmt_float(e_theta.real),
                    "e_theta_imag": fmt_float(e_theta.imag),
                    "e_phi_real": fmt_float(e_phi.real),
                    "e_phi_imag": fmt_float(e_phi.imag),
                    "power": fmt_float(power),
                    "source_config": metadata["class_label"],
                    "carrier_model": metadata["carrier_model"],
                    "working_state": metadata["working_state"],
                    "extraction_method": "CST element-library FarfieldPlot superposition with source translation phase",
                }
            )
    return nearfield_rows, farfield_rows


def worker_run(args: argparse.Namespace) -> int:
    import cst.interface

    case_rows_all = read_csv_rows(resolve_path(args.case_manifest))
    source_rows_all = read_csv_rows(resolve_path(args.source_manifest))
    sample_ids = selected_sample_ids(args, case_rows_all)
    summary_out = resolve_path(args.summary_out)
    if not sample_ids:
        write_json(
            summary_out,
            {
                "created_at": now_iso(),
                "status": "nothing_to_export",
                "real_cst_api_used": False,
                "sample_count": 0,
                "selected_sample_ids": [],
                "completed_samples": 0,
                "failed_samples": 0,
            },
        )
        return 0
    probe_points = build_probe_points(read_csv_rows(resolve_path(args.probe_csv)))
    farfield_grid = build_level2_farfield_grid()
    element_dir = resolve_path(args.element_dir)

    selected_source_rows = [row for row in source_rows_all if row["sample_id"].strip() in set(sample_ids)]
    required_axes = sorted({axis_from_orientation(source) for source in selected_source_rows})
    env = cst.interface.DesignEnvironment()
    projects: dict[str, ElementProject] = {}
    sample_results: list[dict[str, Any]] = []
    try:
        for axis in required_axes:
            project_path = project_for_axis(element_dir, axis)
            if not project_path.exists():
                raise FileNotFoundError(project_path)
            projects[axis] = ElementProject(env, project_path, axis)

        for sample_id in sample_ids:
            case_rows = filter_sample_rows(case_rows_all, sample_id)
            source_rows = filter_sample_rows(source_rows_all, sample_id)
            metadata = sample_metadata(case_rows)
            nearfield_out = resolve_path(metadata["nearfield_export"])
            farfield_out = resolve_path(metadata["farfield_export"])
            try:
                nearfield_rows, farfield_rows = build_output_rows(
                    metadata,
                    case_rows,
                    source_rows,
                    probe_points,
                    farfield_grid,
                    projects,
                    args.chunk_size,
                    args.farfield_radius_m,
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
                        "extraction_method",
                    ],
                )
                sample_results.append(
                    {
                        "sample_id": sample_id,
                        "status": "export_complete",
                        "class_label": metadata["class_label"],
                        "source_count": len(source_rows),
                        "frequency_count": len(case_rows),
                        "frequencies_hz": [int(float(row["frequency_hz"])) for row in case_rows],
                        "required_axes": sorted({axis_from_orientation(source) for source in source_rows}),
                        "nearfield_out": str(nearfield_out),
                        "farfield_out": str(farfield_out),
                        "nearfield_rows": len(nearfield_rows),
                        "farfield_rows": len(farfield_rows),
                    }
                )
            except Exception as exc:
                sample_results.append(
                    {
                        "sample_id": sample_id,
                        "status": "failed",
                        "error": repr(exc),
                        "nearfield_out": str(nearfield_out),
                        "farfield_out": str(farfield_out),
                    }
                )
                if args.stop_on_error:
                    raise

        all_ok = bool(sample_results) and all(row["status"] == "export_complete" for row in sample_results)
        total_nearfield_rows = sum(int(row.get("nearfield_rows", 0) or 0) for row in sample_results)
        total_farfield_rows = sum(int(row.get("farfield_rows", 0) or 0) for row in sample_results)
        summary = {
            "created_at": now_iso(),
            "status": "export_complete" if len(sample_results) == 1 and all_ok else ("batch_export_complete" if all_ok else "failed"),
            "real_cst_api_used": True,
            "sample_count": len(sample_results),
            "selected_sample_ids": sample_ids,
            "completed_samples": sum(1 for row in sample_results if row["status"] == "export_complete"),
            "failed_samples": sum(1 for row in sample_results if row["status"] != "export_complete"),
            "required_axes": required_axes,
            "element_projects": {axis: str(projects[axis].path) for axis in required_axes},
            "nearfield_rows": total_nearfield_rows,
            "farfield_rows": total_farfield_rows,
            "probe_points": len(probe_points),
            "farfield_grid_points_per_frequency": len(farfield_grid),
            "samples": sample_results,
            "assumption": (
                "Level 2 pilot is CST-derived by linear superposition of compact x/y/z element-library "
                "FarfieldPlot results with manifest source positions, amplitudes, and phases."
            ),
        }
        if len(sample_results) == 1:
            summary.update(sample_results[0])
        write_json(summary_out, summary)
    finally:
        for project in projects.values():
            project.close()
    return 0


def controller_run(args: argparse.Namespace) -> int:
    stdout_log = resolve_path(args.stdout_log)
    summary_out = resolve_path(args.summary_out)
    command = [
        str(args.cst_python),
        str(Path("src") / Path(__file__).name),
        "--worker",
        "--case-manifest",
        str(args.case_manifest),
        "--source-manifest",
        str(args.source_manifest),
        "--probe-csv",
        str(args.probe_csv),
        "--element-dir",
        str(args.element_dir),
        "--summary-out",
        str(args.summary_out),
        "--chunk-size",
        str(args.chunk_size),
        "--farfield-radius-m",
        str(args.farfield_radius_m),
    ]
    if args.sample_id:
        command.extend(["--sample-id", args.sample_id])
    if args.sample_ids:
        command.extend(["--sample-ids", args.sample_ids])
    if args.all_samples:
        command.append("--all-samples")
    if args.missing_only:
        command.append("--missing-only")
    if args.stop_on_error:
        command.append("--stop-on-error")
    if args.limit:
        command.extend(["--limit", str(args.limit)])
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
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    stdout_log.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        summary: dict[str, Any] = {}
        if summary_out.exists():
            try:
                summary = json.loads(summary_out.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                summary = {}
        summary.update(
            {
                "completed_at": now_iso(),
                "status": "failed",
                "controller_returncode": completed.returncode,
                "stdout_log": str(stdout_log),
            }
        )
        write_json(summary_out, summary)
    return completed.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Level 2 pilot CSVs from CST element-library superposition.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--sample-id", default="")
    parser.add_argument("--sample-ids", default="", help="Comma-separated sample IDs.")
    parser.add_argument("--all-samples", action="store_true", help="Export all samples in the Level 2 manifest.")
    parser.add_argument("--missing-only", action="store_true", help="When selecting multiple samples, export only missing nearfield/farfield pairs.")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop the batch on the first sample export error.")
    parser.add_argument("--limit", type=int, default=0, help="Optional maximum number of selected samples to export.")
    parser.add_argument("--case-manifest", type=Path, default=DEFAULT_LEVEL2_CASES)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_LEVEL2_SOURCES)
    parser.add_argument("--probe-csv", type=Path, default=DEFAULT_PROBE_CSV)
    parser.add_argument("--element-dir", type=Path, default=DEFAULT_ELEMENT_DIR)
    parser.add_argument("--summary-out", default=str(DEFAULT_OUT_DIR / "level2_superposed_export_summary.json"))
    parser.add_argument("--stdout-log", default=str(DEFAULT_OUT_DIR / "level2_superposed_export_stdout.log"))
    parser.add_argument("--chunk-size", type=int, default=250)
    parser.add_argument("--farfield-radius-m", type=float, default=13.0)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not (args.sample_id or args.sample_ids or args.all_samples):
        raise SystemExit("Provide --sample-id, --sample-ids, or --all-samples.")
    if args.worker:
        return worker_run(args)
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
