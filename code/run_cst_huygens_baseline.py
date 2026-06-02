from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, layout_from_nearfield, measurement_vector_from_nearfield, read_table
from huygens_core import (
    HuygensSurface,
    build_huygens_farfield_matrix,
    build_huygens_measurement_matrix,
    load_huygens_surface,
    surface_basis_count,
    surface_unknown_count,
)
from run_cst_sampling_tradeoff import (
    DEFAULT_FARFIELD,
    DEFAULT_LAYOUTS,
    DEFAULT_NEARFIELD,
    ROOT,
    display_path,
    load_candidate_layouts,
    matrix_health,
    select_pairs,
    subset_nearfield,
    validate_inputs,
)
from em_core import pattern_metrics, solve_tikhonov


DEFAULT_SURFACE = ROOT / "data" / "source_priors" / "huygens_surface" / "level1_local_sphere_r0p35_nodes.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_level1_huygens_baseline"
DEFAULT_CANDIDATES = ("full_grid_162",)
DEFAULT_LAMBDAS = (1e-10, 1e-8, 1e-6, 1e-4, 1e-2)
MODEL_VARIANTS = {
    "electric_sheet_only": {"include_magnetic": False, "magnetic_sign": 0.0},
    "huygens_em_plus": {"include_magnetic": True, "magnetic_sign": 1.0},
    "huygens_em_minus": {"include_magnetic": True, "magnetic_sign": -1.0},
}
CENTER_POINT = np.array([0.0, 0.0, 4.0])


def sanitize_metrics(metrics: dict[str, float]) -> dict[str, float]:
    clean = dict(metrics)
    if not math.isfinite(float(clean.get("correlation", math.nan))):
        clean["correlation"] = -1.0
    if not math.isfinite(float(clean.get("nmse", math.nan))):
        clean["nmse"] = math.inf
    if not math.isfinite(float(clean.get("main_lobe_error_deg", math.nan))):
        clean["main_lobe_error_deg"] = math.inf
    return clean


def predicted_power_from_solution(
    surface: HuygensSurface,
    solution: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    frequency_hz: float,
    include_magnetic: bool,
    magnetic_sign: float,
    weight_mode: str,
) -> np.ndarray:
    far_matrix = build_huygens_farfield_matrix(
        surface,
        theta,
        phi,
        frequency_hz,
        include_magnetic=include_magnetic,
        magnetic_sign=magnetic_sign,
        weight_mode=weight_mode,
    )
    predicted = far_matrix @ solution
    n_angles = theta.size
    return np.abs(predicted[:n_angles]) ** 2 + np.abs(predicted[n_angles:]) ** 2


def surface_solution_metrics(surface: HuygensSurface, solution: np.ndarray, include_magnetic: bool) -> dict[str, float | int]:
    basis_per_node = surface_basis_count(include_magnetic)
    coeffs = solution.reshape(surface.positions.shape[0], basis_per_node)
    norms = np.linalg.norm(coeffs, axis=1)
    total = float(np.sum(norms))
    if total <= 1e-30:
        return {
            "active_nodes": 0,
            "active_fraction": 0.0,
            "peak_node_norm": 0.0,
            "peak_x_m": math.nan,
            "peak_y_m": math.nan,
            "peak_z_m": math.nan,
            "peak_center_distance_m": math.nan,
            "top10_node_energy_share": 0.0,
        }
    peak_idx = int(np.argmax(norms))
    active_threshold = float(1e-3 * norms[peak_idx])
    active = int(np.sum(norms >= active_threshold))
    order = np.argsort(norms)[::-1]
    top10 = order[: min(10, order.size)]
    peak_position = surface.positions[peak_idx]
    return {
        "active_nodes": active,
        "active_fraction": float(active / surface.positions.shape[0]),
        "peak_node_norm": float(norms[peak_idx]),
        "peak_x_m": float(peak_position[0]),
        "peak_y_m": float(peak_position[1]),
        "peak_z_m": float(peak_position[2]),
        "peak_center_distance_m": float(np.linalg.norm(peak_position - CENTER_POINT)),
        "top10_node_energy_share": float(np.sum(norms[top10]) / total),
    }


def solve_case(
    nearfield: pd.DataFrame,
    farfield: pd.DataFrame,
    candidate_name: str,
    candidate_group: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    surface: HuygensSurface,
    surface_path: Path,
    model_variant: str,
    lambda_reg: float,
    weight_mode: str,
) -> tuple[dict[str, object], np.ndarray]:
    variant = MODEL_VARIANTS[model_variant]
    include_magnetic = bool(variant["include_magnetic"])
    magnetic_sign = float(variant["magnetic_sign"])
    sensor_ids_requested = pd.to_numeric(candidate_group["sensor_id"], errors="coerce").dropna().astype(int).to_numpy()
    candidate_nf = subset_nearfield(nearfield, sensor_ids_requested)
    measurement, sensor_ids_used = measurement_vector_from_nearfield(candidate_nf, sample_id, frequency_hz)
    layout = layout_from_nearfield(candidate_nf, sample_id, frequency_hz, sensor_ids_used)
    matrix = build_huygens_measurement_matrix(
        layout,
        surface,
        frequency_hz,
        np.arange(layout.positions.shape[0]),
        include_magnetic=include_magnetic,
        magnetic_sign=magnetic_sign,
        weight_mode=weight_mode,
    )
    solution = solve_tikhonov(matrix, measurement, lam=lambda_reg)
    residual = matrix @ solution - measurement
    theta, phi, true_power, _ = farfield_power_from_table(farfield, sample_id, frequency_hz)
    rec_power = predicted_power_from_solution(
        surface,
        solution,
        theta,
        phi,
        frequency_hz,
        include_magnetic=include_magnetic,
        magnetic_sign=magnetic_sign,
        weight_mode=weight_mode,
    )
    metrics = sanitize_metrics(pattern_metrics(true_power, rec_power, theta, phi))
    row: dict[str, object] = {
        "sample_id": sample_id,
        "frequency_hz": float(frequency_hz),
        "candidate": candidate_name,
        "candidate_method": str(candidate_group["method"].iloc[0]),
        "sensor_count": int(len(sensor_ids_used)),
        "measurement_channels": int(measurement.size),
        "prior_id": surface.prior_id,
        "surface_path": display_path(surface_path),
        "surface_nodes": int(surface.positions.shape[0]),
        "model_variant": model_variant,
        "approximation": "electric_magnetic_dipole_sheet" if include_magnetic else "electric_dipole_sheet",
        "include_magnetic": int(include_magnetic),
        "magnetic_sign": float(magnetic_sign),
        "weight_mode": weight_mode,
        "unknown_count": int(surface_unknown_count(surface, include_magnetic)),
        "channel_unknown_ratio": float(measurement.size / matrix.shape[1]),
        "lambda_reg": float(lambda_reg),
        "relative_residual": float(np.linalg.norm(residual) / max(np.linalg.norm(measurement), 1e-15)),
    }
    row.update(matrix_health(matrix))
    row.update(surface_solution_metrics(surface, solution, include_magnetic))
    row.update(metrics)
    return row, solution


def acceptance_status(row: pd.Series) -> str:
    min_corr = float(row["min_correlation"])
    max_nmse = float(row["max_nmse"])
    max_lobe_error = float(row["max_main_lobe_error_deg"])
    if min_corr >= 0.95 and max_nmse <= 1e-2 and max_lobe_error <= 5.0:
        return "strict_pass"
    if min_corr >= 0.95 and max_nmse <= 3e-2 and max_lobe_error <= 5.0:
        return "corr_pass_nmse_near"
    if min_corr >= 0.95 and max_lobe_error <= 5.0:
        return "corr_lobe_pass_nmse_open"
    return "diagnostic_only"


def status_rank(status: str) -> int:
    return {
        "strict_pass": 0,
        "corr_pass_nmse_near": 1,
        "corr_lobe_pass_nmse_open": 2,
        "diagnostic_only": 3,
    }.get(status, 99)


def solution_records(
    surface: HuygensSurface,
    solution: np.ndarray,
    sample_id: str,
    frequency_hz: float,
    candidate: str,
    model_variant: str,
    lambda_reg: float,
    weight_mode: str,
) -> list[dict[str, object]]:
    include_magnetic = bool(MODEL_VARIANTS[model_variant]["include_magnetic"])
    basis_per_node = surface_basis_count(include_magnetic)
    coeffs = solution.reshape(surface.positions.shape[0], basis_per_node)
    rows: list[dict[str, object]] = []
    for node_idx, values in enumerate(coeffs):
        jt1 = values[0]
        jt2 = values[1]
        mt1 = values[2] if include_magnetic else 0.0j
        mt2 = values[3] if include_magnetic else 0.0j
        rows.append(
            {
                "sample_id": sample_id,
                "frequency_hz": float(frequency_hz),
                "candidate": candidate,
                "model_variant": model_variant,
                "lambda_reg": float(lambda_reg),
                "weight_mode": weight_mode,
                "prior_id": surface.prior_id,
                "node_index": int(node_idx),
                "x_m": float(surface.positions[node_idx, 0]),
                "y_m": float(surface.positions[node_idx, 1]),
                "z_m": float(surface.positions[node_idx, 2]),
                "normal_x": float(surface.normals[node_idx, 0]),
                "normal_y": float(surface.normals[node_idx, 1]),
                "normal_z": float(surface.normals[node_idx, 2]),
                "weight_m2": float(surface.weights_m2[node_idx]),
                "J_t1_real": float(np.real(jt1)),
                "J_t1_imag": float(np.imag(jt1)),
                "J_t2_real": float(np.real(jt2)),
                "J_t2_imag": float(np.imag(jt2)),
                "M_t1_real": float(np.real(mt1)),
                "M_t1_imag": float(np.imag(mt1)),
                "M_t2_real": float(np.real(mt2)),
                "M_t2_imag": float(np.imag(mt2)),
                "node_coeff_norm": float(np.linalg.norm(values)),
            }
        )
    return rows


def run_sweep(args: argparse.Namespace) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)
    candidate_names = None if args.all_candidates else (args.candidates or list(DEFAULT_CANDIDATES))
    layouts = load_candidate_layouts(Path(args.layouts), candidate_names)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)
    surface_paths = args.surfaces or [DEFAULT_SURFACE]
    model_variants = args.model_variants or list(MODEL_VARIANTS)
    lambda_values = args.lambdas or list(DEFAULT_LAMBDAS)

    rows: list[dict[str, object]] = []
    solutions: list[dict[str, object]] = []
    for surface_path in surface_paths:
        surface = load_huygens_surface(Path(surface_path))
        for sample_id, frequency_hz in pairs:
            for candidate_name, candidate_group in layouts.items():
                for model_variant in model_variants:
                    for lambda_reg in lambda_values:
                        row, solution = solve_case(
                            nearfield,
                            farfield,
                            candidate_name,
                            candidate_group,
                            sample_id,
                            frequency_hz,
                            surface,
                            Path(surface_path),
                            model_variant,
                            float(lambda_reg),
                            args.weight_mode,
                        )
                        rows.append(row)
                        solutions.append(
                            {
                                "row": row,
                                "surface": surface,
                                "solution": solution,
                            }
                        )
    return pd.DataFrame(rows), solutions


def summarize(results: pd.DataFrame, solutions: list[dict[str, object]], out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    by_setting = (
        results.groupby(
            [
                "prior_id",
                "surface_path",
                "model_variant",
                "approximation",
                "include_magnetic",
                "magnetic_sign",
                "weight_mode",
                "candidate",
                "candidate_method",
                "lambda_reg",
                "surface_nodes",
                "unknown_count",
                "sensor_count",
            ],
            as_index=False,
        )
        .agg(
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_relative_residual=("relative_residual", "mean"),
            max_relative_residual=("relative_residual", "max"),
            mean_active_nodes=("active_nodes", "mean"),
            mean_top10_node_energy_share=("top10_node_energy_share", "mean"),
            mean_stable_condition=("stable_condition", "mean"),
        )
    )
    by_setting["status"] = by_setting.apply(acceptance_status, axis=1)
    by_setting["status_rank"] = by_setting["status"].map(status_rank)
    by_setting = by_setting.sort_values(
        [
            "status_rank",
            "min_correlation",
            "max_nmse",
            "max_relative_residual",
            "mean_top10_node_energy_share",
            "max_main_lobe_error_deg",
        ],
        ascending=[True, False, True, True, False, True],
    ).drop(columns=["status_rank"])
    by_setting.to_csv(out_dir / "huygens_reconstruction_by_setting.csv", index=False, encoding="utf-8-sig")

    best = by_setting.iloc[0]
    best_mask = (
        (results["prior_id"] == best["prior_id"])
        & (results["surface_path"] == best["surface_path"])
        & (results["model_variant"] == best["model_variant"])
        & (results["weight_mode"] == best["weight_mode"])
        & (results["candidate"] == best["candidate"])
        & np.isclose(results["lambda_reg"], float(best["lambda_reg"]))
    )
    best_cases = results.loc[best_mask].sort_values(["sample_id", "frequency_hz"])
    best_cases.to_csv(out_dir / "huygens_reconstruction_best_cases.csv", index=False, encoding="utf-8-sig")

    best_solution_rows: list[dict[str, object]] = []
    for item in solutions:
        row = item["row"]
        if (
            row["prior_id"] == best["prior_id"]
            and row["surface_path"] == best["surface_path"]
            and row["model_variant"] == best["model_variant"]
            and row["weight_mode"] == best["weight_mode"]
            and row["candidate"] == best["candidate"]
            and math.isclose(float(row["lambda_reg"]), float(best["lambda_reg"]), rel_tol=1e-12, abs_tol=0.0)
        ):
            best_solution_rows.extend(
                solution_records(
                    item["surface"],
                    item["solution"],
                    str(row["sample_id"]),
                    float(row["frequency_hz"]),
                    str(row["candidate"]),
                    str(row["model_variant"]),
                    float(row["lambda_reg"]),
                    str(row["weight_mode"]),
                )
            )
    pd.DataFrame(best_solution_rows).to_csv(out_dir / "huygens_surface_solution_best_setting.csv", index=False, encoding="utf-8-sig")

    summary = {
        "generated_by": "code/run_cst_huygens_baseline.py",
        "nearfield": display_path(Path(args.nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "layouts": display_path(Path(args.layouts)),
        "out_dir": display_path(out_dir),
        "surface_count": int(results["prior_id"].nunique()),
        "pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "candidate_count": int(results["candidate"].nunique()),
        "model_variant_count": int(results["model_variant"].nunique()),
        "weight_mode": args.weight_mode,
        "best_setting": {
            "prior_id": str(best["prior_id"]),
            "model_variant": str(best["model_variant"]),
            "candidate": str(best["candidate"]),
            "lambda_reg": float(best["lambda_reg"]),
            "status": str(best["status"]),
            "min_correlation": float(best["min_correlation"]),
            "max_nmse": float(best["max_nmse"]),
            "max_main_lobe_error_deg": float(best["max_main_lobe_error_deg"]),
            "mean_relative_residual": float(best["mean_relative_residual"]),
            "mean_active_nodes": float(best["mean_active_nodes"]),
            "mean_top10_node_energy_share": float(best["mean_top10_node_energy_share"]),
        },
    }
    (out_dir / "huygens_reconstruction_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(out_dir, by_setting, best_cases, summary)
    return summary


def write_markdown_summary(out_dir: Path, by_setting: pd.DataFrame, best_cases: pd.DataFrame, summary: dict[str, object]) -> None:
    rows = []
    for row in by_setting.itertuples(index=False):
        rows.append(
            f"| {row.prior_id} | {row.model_variant} | {row.candidate} | {row.lambda_reg:.0e} | "
            f"{row.status} | {row.min_correlation:.4f} | {row.max_nmse:.4e} | "
            f"{row.max_main_lobe_error_deg:.2f} | {row.mean_relative_residual:.4e} | {row.mean_active_nodes:.1f} |"
        )

    case_rows = []
    for row in best_cases.itertuples(index=False):
        case_rows.append(
            f"| {row.sample_id} | {row.frequency_hz:.6g} | {row.correlation:.4f} | "
            f"{row.nmse:.4e} | {row.main_lobe_error_deg:.2f} | {row.relative_residual:.4e} | "
            f"{row.active_nodes} |"
        )

    best = summary["best_setting"]
    if best["status"] == "strict_pass":
        reading = """- The Huygens-style surface prior reaches the strict Level 1 gate on the current CST export.
- Keep this as the first physical source-prior baseline, while still replacing the current FarfieldPlot-derived angular near-field with true CST monitor data before making the final sampling claim."""
    elif best["status"] in {"corr_pass_nmse_near", "corr_lobe_pass_nmse_open"}:
        reading = """- The Huygens-style surface prior passes the angular correlation and main-lobe checks, but the strict NMSE gate is not fully closed.
- This is useful as a physical-prior prototype and a bridge toward true monitor data, not yet the final sampling proof."""
    else:
        reading = """- The Huygens-style surface prior is still diagnostic on the current CST export.
- Treat the result as a measurement-matrix smoke test. The next physics step is true near-field monitor data and a fuller electric/magnetic surface Green-function convention check."""

    content = f"""# CST Level 1 Huygens Surface Baseline

This directory evaluates the first Huygens-style surface-source prior against
the current Level 1 CST near/far-field export. The implementation uses a compact
electric/magnetic dipole-sheet approximation: each surface node has two
tangential electric-current coefficients and, for the Huygens variants, two
tangential magnetic-current coefficients. It is a runnable diagnostic baseline,
not a final Stratton-Chu/Huygens integral solver.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Candidate layouts | `{summary['layouts']}` |

## Best Setting

| Field | Value |
|---|---|
| Prior | `{best['prior_id']}` |
| Model variant | `{best['model_variant']}` |
| Candidate | `{best['candidate']}` |
| Lambda | `{best['lambda_reg']:.0e}` |
| Status | `{best['status']}` |
| Min Corr | `{best['min_correlation']:.4f}` |
| Max NMSE | `{best['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best['max_main_lobe_error_deg']:.2f}` |
| Mean relative residual | `{best['mean_relative_residual']:.4e}` |
| Mean active nodes | `{best['mean_active_nodes']:.1f}` |
| Mean top-10 node energy share | `{best['mean_top10_node_energy_share']:.3f}` |

## Best Cases

| Sample | Frequency / Hz | Corr | NMSE | Main-lobe error / deg | Relative residual | Active nodes |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(case_rows)}

## Setting Ranking

| Prior | Variant | Candidate | Lambda | Status | Min Corr | Max NMSE | Max lobe / deg | Mean residual | Mean active nodes |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

{reading}

## Generated Files

| File | Role |
|---|---|
| `huygens_reconstruction_results.csv` | Per sample/frequency/model/lambda reconstruction metrics. |
| `huygens_reconstruction_by_setting.csv` | Aggregated setting ranking. |
| `huygens_reconstruction_best_cases.csv` | Per-case rows for the best setting. |
| `huygens_surface_solution_best_setting.csv` | Best-setting node coefficients for later visualization and support analysis. |
| `huygens_reconstruction_summary.json` | Script-friendly summary. |

## Command

```powershell
python code\\run_cst_huygens_baseline.py
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Huygens-style CST Level 1 reconstruction baseline.")
    parser.add_argument("--nearfield", type=Path, default=DEFAULT_NEARFIELD)
    parser.add_argument("--farfield", type=Path, default=DEFAULT_FARFIELD)
    parser.add_argument("--layouts", type=Path, default=DEFAULT_LAYOUTS)
    parser.add_argument("--surface", dest="surfaces", type=Path, action="append")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--candidate", dest="candidates", action="append")
    parser.add_argument("--all-candidates", action="store_true")
    parser.add_argument("--sample", dest="samples", action="append")
    parser.add_argument("--frequency-hz", dest="frequencies_hz", action="append", type=float)
    parser.add_argument("--lambda-reg", dest="lambdas", action="append", type=float)
    parser.add_argument("--model-variant", dest="model_variants", choices=sorted(MODEL_VARIANTS), action="append")
    parser.add_argument("--weight-mode", choices=("sqrt_area", "area", "none"), default="sqrt_area")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results, solutions = run_sweep(args)
    if results.empty:
        raise ValueError("Huygens baseline produced no rows")
    results.to_csv(out_dir / "huygens_reconstruction_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, solutions, out_dir, args)
    best = summary["best_setting"]
    print(f"CST Huygens baseline written to {out_dir}")
    print(f"best setting: {best['prior_id']} {best['model_variant']} ({best['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
