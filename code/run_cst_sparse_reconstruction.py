from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, layout_from_nearfield, measurement_vector_from_nearfield, read_table
from em_core import build_measurement_matrix, farfield_pattern, pattern_metrics, solve_tikhonov, vector_to_source_set
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
from run_cst_source_model_sweep import config_to_grid, select_configs


DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_level1_sparse_calibration"
DEFAULT_CANDIDATES = ("full_grid_162",)
DEFAULT_CONFIGS = ("default_cube_5x3x3", "compact_cube_3x3x3")
DEFAULT_L2_LAMBDAS = (1e-4, 1e-5)
DEFAULT_GROUP_ALPHA_FRACS = (0.3, 0.1, 0.03, 0.01, 0.003, 0.001, 0.0003, 0.0001)
CENTER_POINT = np.array([0.0, 0.0, 4.0])


def group_lambda_max(matrix: np.ndarray, values: np.ndarray, group_count: int) -> float:
    gradient = matrix.conj().T @ values
    group_norms = np.linalg.norm(gradient.reshape(group_count, 3), axis=1)
    return float(np.max(group_norms))


def group_soft_threshold(values: np.ndarray, threshold: float, group_count: int) -> np.ndarray:
    grouped = values.reshape(group_count, 3)
    norms = np.linalg.norm(grouped, axis=1)
    scale = np.maximum(0.0, 1.0 - threshold / np.maximum(norms, 1e-30))
    return (grouped * scale[:, None]).reshape(values.shape)


def solve_group_sparse_fista(
    matrix: np.ndarray,
    values: np.ndarray,
    group_count: int,
    l2_lambda: float,
    group_alpha_frac: float,
    max_iter: int,
    tol: float,
) -> tuple[np.ndarray, dict[str, float | int]]:
    lambda_max = group_lambda_max(matrix, values, group_count)
    group_lambda = float(group_alpha_frac * lambda_max)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    lipschitz = float(singular_values[0] ** 2 + l2_lambda) if singular_values.size else float(l2_lambda)
    lipschitz = max(lipschitz, 1e-30)

    x = np.zeros(matrix.shape[1], dtype=np.complex128)
    y = x.copy()
    momentum = 1.0
    converged = 0
    rel_change = math.inf
    for iteration in range(1, max_iter + 1):
        previous = x.copy()
        residual = matrix @ y - values
        gradient = matrix.conj().T @ residual + l2_lambda * y
        trial = y - gradient / lipschitz
        x = group_soft_threshold(trial, group_lambda / lipschitz, group_count)
        next_momentum = 0.5 * (1.0 + math.sqrt(1.0 + 4.0 * momentum**2))
        y = x + ((momentum - 1.0) / next_momentum) * (x - previous)
        momentum = next_momentum
        denom = max(float(np.linalg.norm(previous)), 1e-12)
        rel_change = float(np.linalg.norm(x - previous) / denom)
        if rel_change < tol:
            converged = 1
            break

    residual_norm = float(np.linalg.norm(matrix @ x - values))
    value_norm = float(np.linalg.norm(values))
    return x, {
        "solver_iterations": int(iteration),
        "solver_converged": int(converged),
        "solver_rel_change": float(rel_change),
        "lambda_max": float(lambda_max),
        "group_lambda": float(group_lambda),
        "lipschitz": float(lipschitz),
        "relative_residual": float(residual_norm / max(value_norm, 1e-15)),
    }


def source_support_metrics(grid_positions: np.ndarray, solution: np.ndarray) -> dict[str, float | int]:
    moments = solution.reshape(grid_positions.shape[0], 3)
    norms = np.linalg.norm(moments, axis=1)
    total = float(np.sum(norms))
    if total <= 1e-30:
        return {
            "active_sources": 0,
            "active_fraction": 0.0,
            "peak_source_norm": 0.0,
            "peak_x_m": math.nan,
            "peak_y_m": math.nan,
            "peak_z_m": math.nan,
            "peak_center_distance_m": math.nan,
            "center_energy_share": 0.0,
        }
    peak_idx = int(np.argmax(norms))
    active_threshold = float(1e-3 * norms[peak_idx])
    active = int(np.sum(norms >= active_threshold))
    center_idx = int(np.argmin(np.linalg.norm(grid_positions - CENTER_POINT[None, :], axis=1)))
    peak_position = grid_positions[peak_idx]
    return {
        "active_sources": active,
        "active_fraction": float(active / grid_positions.shape[0]),
        "peak_source_norm": float(norms[peak_idx]),
        "peak_x_m": float(peak_position[0]),
        "peak_y_m": float(peak_position[1]),
        "peak_z_m": float(peak_position[2]),
        "peak_center_distance_m": float(np.linalg.norm(peak_position - CENTER_POINT)),
        "center_energy_share": float(norms[center_idx] / total),
    }


def sanitize_metrics(metrics: dict[str, float]) -> dict[str, float]:
    clean = dict(metrics)
    if not math.isfinite(float(clean.get("correlation", math.nan))):
        clean["correlation"] = -1.0
    if not math.isfinite(float(clean.get("nmse", math.nan))):
        clean["nmse"] = math.inf
    return clean


def evaluate_solution(
    farfield: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    candidate_name: str,
    grid_positions: np.ndarray,
    solution: np.ndarray,
) -> dict[str, float]:
    reconstructed = vector_to_source_set(grid_positions, solution, label=f"{sample_id}_{candidate_name}")
    theta, phi, true_power, _ = farfield_power_from_table(farfield, sample_id, frequency_hz)
    rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, frequency_hz)
    return sanitize_metrics(pattern_metrics(true_power, rec_power, theta, phi))


def evaluate_case(
    nearfield: pd.DataFrame,
    farfield: pd.DataFrame,
    candidate_name: str,
    candidate_group: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    config_name: str,
    grid_positions: np.ndarray,
    solver: str,
    l2_lambda: float,
    group_alpha_frac: float,
    max_iter: int,
    tol: float,
) -> dict[str, object]:
    sensor_ids_requested = pd.to_numeric(candidate_group["sensor_id"], errors="coerce").dropna().astype(int).to_numpy()
    candidate_nf = subset_nearfield(nearfield, sensor_ids_requested)
    measurement, sensor_ids_used = measurement_vector_from_nearfield(candidate_nf, sample_id, frequency_hz)
    layout = layout_from_nearfield(candidate_nf, sample_id, frequency_hz, sensor_ids_used)
    matrix = build_measurement_matrix(layout, grid_positions, frequency_hz, np.arange(layout.positions.shape[0]))
    group_count = int(grid_positions.shape[0])

    if solver == "tikhonov":
        solution = solve_tikhonov(matrix, measurement, lam=l2_lambda)
        solver_info: dict[str, float | int] = {
            "solver_iterations": 0,
            "solver_converged": 1,
            "solver_rel_change": 0.0,
            "lambda_max": group_lambda_max(matrix, measurement, group_count),
            "group_lambda": 0.0,
            "lipschitz": math.nan,
            "relative_residual": float(np.linalg.norm(matrix @ solution - measurement) / max(np.linalg.norm(measurement), 1e-15)),
        }
    elif solver == "group_sparse":
        solution, solver_info = solve_group_sparse_fista(
            matrix,
            measurement,
            group_count=group_count,
            l2_lambda=l2_lambda,
            group_alpha_frac=group_alpha_frac,
            max_iter=max_iter,
            tol=tol,
        )
    else:
        raise ValueError(f"unsupported solver: {solver}")

    row: dict[str, object] = {
        "sample_id": sample_id,
        "frequency_hz": float(frequency_hz),
        "candidate": candidate_name,
        "candidate_method": str(candidate_group["method"].iloc[0]),
        "config": config_name,
        "solver": solver,
        "sensor_count": int(len(sensor_ids_used)),
        "measurement_channels": int(measurement.size),
        "equivalent_source_points": group_count,
        "unknown_count": int(matrix.shape[1]),
        "channel_unknown_ratio": float(measurement.size / matrix.shape[1]),
        "l2_lambda": float(l2_lambda),
        "group_alpha_frac": float(group_alpha_frac),
    }
    row.update(matrix_health(matrix))
    row.update(solver_info)
    row.update(source_support_metrics(grid_positions, solution))
    row.update(evaluate_solution(farfield, sample_id, frequency_hz, candidate_name, grid_positions, solution))
    return row


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


def run_sweep(args: argparse.Namespace) -> pd.DataFrame:
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)
    layouts = load_candidate_layouts(Path(args.layouts), args.candidates)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)
    configs = select_configs(args.configs)

    rows: list[dict[str, object]] = []
    for config in configs:
        grid_positions = config_to_grid(config)
        for sample_id, frequency_hz in pairs:
            for candidate_name, candidate_group in layouts.items():
                for l2_lambda in args.l2_lambdas:
                    rows.append(
                        evaluate_case(
                            nearfield,
                            farfield,
                            candidate_name,
                            candidate_group,
                            sample_id,
                            frequency_hz,
                            config.model_id,
                            grid_positions,
                            "tikhonov",
                            l2_lambda,
                            0.0,
                            args.max_iter,
                            args.tol,
                        )
                    )
                    for group_alpha_frac in args.group_alpha_fracs:
                        rows.append(
                            evaluate_case(
                                nearfield,
                                farfield,
                                candidate_name,
                                candidate_group,
                                sample_id,
                                frequency_hz,
                                config.model_id,
                                grid_positions,
                                "group_sparse",
                                l2_lambda,
                                group_alpha_frac,
                                args.max_iter,
                                args.tol,
                            )
                        )
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    by_setting = (
        results.groupby(["config", "solver", "candidate", "l2_lambda", "group_alpha_frac", "equivalent_source_points"], as_index=False)
        .agg(
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_active_sources=("active_sources", "mean"),
            mean_center_energy_share=("center_energy_share", "mean"),
            max_peak_center_distance_m=("peak_center_distance_m", "max"),
            mean_relative_residual=("relative_residual", "mean"),
        )
    )
    by_setting["status"] = by_setting.apply(acceptance_status, axis=1)
    by_setting["status_rank"] = by_setting["status"].map(status_rank)
    by_setting = by_setting.sort_values(
        ["status_rank", "min_correlation", "max_nmse", "mean_active_sources", "max_main_lobe_error_deg"],
        ascending=[True, False, True, True, True],
    ).drop(columns=["status_rank"])
    by_setting.to_csv(out_dir / "cst_sparse_calibration_by_setting.csv", index=False, encoding="utf-8-sig")

    best = by_setting.iloc[0]
    summary = {
        "generated_by": "code/run_cst_sparse_reconstruction.py",
        "nearfield": display_path(Path(args.nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "layouts": display_path(Path(args.layouts)),
        "out_dir": display_path(out_dir),
        "pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "candidate_count": int(results["candidate"].nunique()),
        "config_count": int(results["config"].nunique()),
        "solver_count": int(results["solver"].nunique()),
        "best_setting": {
            "config": str(best["config"]),
            "solver": str(best["solver"]),
            "candidate": str(best["candidate"]),
            "l2_lambda": float(best["l2_lambda"]),
            "group_alpha_frac": float(best["group_alpha_frac"]),
            "status": str(best["status"]),
            "min_correlation": float(best["min_correlation"]),
            "max_nmse": float(best["max_nmse"]),
            "max_main_lobe_error_deg": float(best["max_main_lobe_error_deg"]),
            "mean_active_sources": float(best["mean_active_sources"]),
            "mean_center_energy_share": float(best["mean_center_energy_share"]),
        },
    }
    (out_dir / "cst_sparse_calibration_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(out_dir, by_setting, summary)
    return summary


def write_markdown_summary(out_dir: Path, by_setting: pd.DataFrame, summary: dict[str, object]) -> None:
    rows = []
    for row in by_setting.itertuples(index=False):
        rows.append(
            f"| {row.config} | {row.solver} | {row.l2_lambda:.0e} | {row.group_alpha_frac:.0e} | "
            f"{row.status} | {row.min_correlation:.4f} | {row.max_nmse:.4e} | "
            f"{row.mean_active_sources:.1f} | {row.mean_center_energy_share:.3f} |"
        )

    best = summary["best_setting"]
    if best["status"] == "strict_pass":
        reading = """- The sparse equivalent-source calibration meets the strict Level 1 target.
- Use this setting as the next baseline for reduced-layout CST tradeoff tests."""
    elif best["status"] == "corr_pass_nmse_near":
        reading = """- Sparse calibration reaches the same practical gate as the known center-source
  prior: correlation and main-lobe checks pass, while worst-case NMSE remains
  slightly above the strict target.
- This supports the diagnosis that unconstrained Tikhonov overfits distributed
  nonphysical source energy on generic grids."""
    else:
        tikhonov_rows = by_setting[by_setting["solver"] == "tikhonov"]
        if best["solver"] == "group_sparse" and len(tikhonov_rows):
            tikhonov_best = tikhonov_rows.sort_values(["min_correlation", "max_nmse"], ascending=[False, True]).iloc[0]
            reading = f"""- Sparse calibration did not yet pass the Level 1 gate, but it is informative:
  the best sparse setting improves min correlation from `{tikhonov_best['min_correlation']:.4f}`
  to `{best['min_correlation']:.4f}` and reduces the mean active source count
  from `{tikhonov_best['mean_active_sources']:.1f}` to `{best['mean_active_sources']:.1f}`.
- The remaining blocker is not only sparsity: max main-lobe error is still
  `{best['max_main_lobe_error_deg']:.2f}` deg and center energy share is
  `{best['mean_center_energy_share']:.3f}`.
- Move next to phase/amplitude convention checks and more physical
  Huygens-surface or known-source priors."""
        else:
            reading = """- Sparse calibration did not yet pass the Level 1 gate.
- Keep using the result as a diagnostic and move to phase/amplitude convention
  checks or more physical Huygens-surface priors."""

    content = f"""# CST Level 1 Sparse Source Calibration

This directory tests whether group-sparse equivalent sources improve the
generic Level 1 source grids. Each source point has three complex dipole moment
components, and the sparse solver shrinks those three components as one group.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Candidate layouts | `{summary['layouts']}` |

## Best Setting

| Field | Value |
|---|---|
| Config | `{best['config']}` |
| Solver | `{best['solver']}` |
| Candidate | `{best['candidate']}` |
| L2 lambda | `{best['l2_lambda']:.0e}` |
| Group alpha fraction | `{best['group_alpha_frac']:.0e}` |
| Status | `{best['status']}` |
| Min Corr | `{best['min_correlation']:.4f}` |
| Max NMSE | `{best['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best['max_main_lobe_error_deg']:.2f}` |
| Mean active sources | `{best['mean_active_sources']:.1f}` |
| Mean center energy share | `{best['mean_center_energy_share']:.3f}` |

## Setting Ranking

| Config | Solver | L2 lambda | Group alpha frac | Status | Min Corr | Max NMSE | Mean active sources | Mean center energy share |
|---|---|---:|---:|---|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

{reading}
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sparse equivalent-source calibration on CST Level 1 exports.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="CST near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="CST far-field CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    parser.add_argument("--candidate", action="append", dest="candidates", help="Candidate layout to include. Repeatable.")
    parser.add_argument("--config", action="append", dest="configs", help="Source grid config id. Repeatable.")
    parser.add_argument("--l2-lambda", action="append", dest="l2_lambdas", type=float, help="L2 regularization. Repeatable.")
    parser.add_argument("--group-alpha-frac", action="append", dest="group_alpha_fracs", type=float, help="Fraction of group lambda max. Repeatable.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    parser.add_argument("--max-iter", type=int, default=500, help="Maximum FISTA iterations.")
    parser.add_argument("--tol", type=float, default=1e-6, help="Relative-change convergence tolerance.")
    args = parser.parse_args()
    args.candidates = args.candidates or list(DEFAULT_CANDIDATES)
    args.configs = args.configs or list(DEFAULT_CONFIGS)
    args.l2_lambdas = args.l2_lambdas or list(DEFAULT_L2_LAMBDAS)
    args.group_alpha_fracs = args.group_alpha_fracs or list(DEFAULT_GROUP_ALPHA_FRACS)
    return args


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = run_sweep(args)
    if results.empty:
        raise ValueError("sparse calibration produced no rows")
    results.to_csv(out_dir / "cst_sparse_calibration_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, out_dir, args)
    print(f"CST sparse calibration written to {out_dir}")
    best = summary["best_setting"]
    print(f"best setting: {best['config']} {best['solver']} ({best['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
