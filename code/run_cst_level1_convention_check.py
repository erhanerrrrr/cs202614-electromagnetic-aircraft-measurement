from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, layout_from_nearfield, measurement_vector_from_nearfield, read_table
from em_core import C0, SensorLayout, pattern_metrics, spherical_basis, solve_tikhonov
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


DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_level1_convention_check"
DEFAULT_CANDIDATES = ("full_grid_162",)
DEFAULT_CONFIGS = ("single_center", "default_cube_5x3x3")
DEFAULT_LAMBDAS = (1e-4, 1e-5)
DEFAULT_TRANSFORMS = ("direct", "complex_conjugate", "phi_sign_flip", "theta_phi_swap")
DEFAULT_PHASE_PAIRS = ("current", "reciprocal_flipped")


@dataclass(frozen=True)
class ConventionConfig:
    convention_id: str
    note: str
    near_phase_sign: int
    far_phase_sign: int
    measurement_transform: str


def build_conventions(phase_pairs: list[str], transforms: list[str]) -> list[ConventionConfig]:
    phase_by_name = {
        "current": (-1, 1, "Current em_core convention: near exp(-jkr), far exp(+jk rhat dot r0)."),
        "reciprocal_flipped": (1, -1, "Reciprocal time-sign flip: near exp(+jkr), far exp(-jk rhat dot r0)."),
    }
    transform_notes = {
        "direct": "Use theta/phi complex samples as converted by cst_io.",
        "complex_conjugate": "Complex conjugate the measured theta/phi samples.",
        "phi_sign_flip": "Flip the phi-polarization sign.",
        "theta_sign_flip": "Flip the theta-polarization sign.",
        "theta_phi_swap": "Swap theta and phi polarization channels.",
    }
    missing_phase = sorted(set(phase_pairs) - set(phase_by_name))
    missing_transform = sorted(set(transforms) - set(transform_notes))
    if missing_phase:
        raise ValueError(f"unknown phase pairs: {missing_phase}")
    if missing_transform:
        raise ValueError(f"unknown transforms: {missing_transform}")

    conventions = []
    for phase_name in phase_pairs:
        near_sign, far_sign, phase_note = phase_by_name[phase_name]
        for transform in transforms:
            convention_id = f"{phase_name}_{transform}"
            conventions.append(
                ConventionConfig(
                    convention_id=convention_id,
                    note=f"{phase_note} {transform_notes[transform]}",
                    near_phase_sign=near_sign,
                    far_phase_sign=far_sign,
                    measurement_transform=transform,
                )
            )
    return conventions


def field_from_dipole(
    obs_positions: np.ndarray,
    source_position: np.ndarray,
    moment: np.ndarray,
    frequency_hz: float,
    phase_sign: int,
) -> np.ndarray:
    k = 2.0 * np.pi * frequency_hz / C0
    rel = obs_positions - source_position[None, :]
    distance = np.linalg.norm(rel, axis=1)
    r_hat = rel / np.maximum(distance[:, None], 1e-15)
    transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
    phase = np.exp(phase_sign * 1j * k * distance) / np.maximum(distance, 1e-12)
    return transverse * phase[:, None]


def sensor_response_custom(
    layout: SensorLayout,
    source_position: np.ndarray,
    moment: np.ndarray,
    frequency_hz: float,
    phase_sign: int,
) -> np.ndarray:
    field = field_from_dipole(layout.positions, source_position, moment, frequency_hz, phase_sign)
    theta_pol = np.sum(field * layout.e_theta, axis=1)
    phi_pol = np.sum(field * layout.e_phi, axis=1)
    return np.concatenate([theta_pol, phi_pol])


def build_measurement_matrix_custom(
    layout: SensorLayout,
    grid_positions: np.ndarray,
    frequency_hz: float,
    phase_sign: int,
) -> np.ndarray:
    n_sensors = layout.positions.shape[0]
    n_grid = grid_positions.shape[0]
    matrix = np.zeros((2 * n_sensors, 3 * n_grid), dtype=np.complex128)
    basis = np.eye(3)
    for source_idx, source_position in enumerate(grid_positions):
        for component_idx, moment in enumerate(basis):
            col = 3 * source_idx + component_idx
            matrix[:, col] = sensor_response_custom(
                layout,
                source_position,
                moment.astype(np.complex128),
                frequency_hz,
                phase_sign,
            )
    return matrix


def farfield_pattern_custom(
    grid_positions: np.ndarray,
    solution: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    frequency_hz: float,
    phase_sign: int,
) -> np.ndarray:
    k = 2.0 * np.pi * frequency_hz / C0
    r_hat, e_theta, e_phi = spherical_basis(theta, phi)
    moments = solution.reshape(grid_positions.shape[0], 3)
    field = np.zeros((theta.size, 3), dtype=np.complex128)
    for source_position, moment in zip(grid_positions, moments):
        phase = np.exp(phase_sign * 1j * k * (r_hat @ source_position))
        transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
        field += transverse * phase[:, None]
    theta_pol = np.sum(field * e_theta, axis=1)
    phi_pol = np.sum(field * e_phi, axis=1)
    return np.abs(theta_pol) ** 2 + np.abs(phi_pol) ** 2


def transform_measurement(measurement: np.ndarray, n_sensors: int, transform: str) -> np.ndarray:
    theta = measurement[:n_sensors]
    phi = measurement[n_sensors:]
    if transform == "direct":
        return measurement
    if transform == "complex_conjugate":
        return np.conjugate(measurement)
    if transform == "phi_sign_flip":
        return np.concatenate([theta, -phi])
    if transform == "theta_sign_flip":
        return np.concatenate([-theta, phi])
    if transform == "theta_phi_swap":
        return np.concatenate([phi, theta])
    raise ValueError(f"unsupported measurement transform: {transform}")


def finite_metrics(metrics: dict[str, float]) -> dict[str, float]:
    clean = dict(metrics)
    if not math.isfinite(float(clean.get("correlation", math.nan))):
        clean["correlation"] = -1.0
    if not math.isfinite(float(clean.get("nmse", math.nan))):
        clean["nmse"] = math.inf
    return clean


def nearfield_power_nmse(measurement: np.ndarray, prediction: np.ndarray, n_sensors: int) -> float:
    meas_power = np.abs(measurement[:n_sensors]) ** 2 + np.abs(measurement[n_sensors:]) ** 2
    pred_power = np.abs(prediction[:n_sensors]) ** 2 + np.abs(prediction[n_sensors:]) ** 2
    meas_norm = meas_power / np.maximum(np.max(meas_power), 1e-30)
    pred_norm = pred_power / np.maximum(np.max(pred_power), 1e-30)
    return float(np.sum((meas_norm - pred_norm) ** 2) / np.maximum(np.sum(meas_norm**2), 1e-30))


def evaluate_case(
    nearfield: pd.DataFrame,
    farfield: pd.DataFrame,
    candidate_name: str,
    candidate_group: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    source_model: str,
    grid_positions: np.ndarray,
    lambda_reg: float,
    convention: ConventionConfig,
) -> dict[str, object]:
    sensor_ids_requested = pd.to_numeric(candidate_group["sensor_id"], errors="coerce").dropna().astype(int).to_numpy()
    candidate_nf = subset_nearfield(nearfield, sensor_ids_requested)
    measurement_raw, sensor_ids_used = measurement_vector_from_nearfield(candidate_nf, sample_id, frequency_hz)
    layout = layout_from_nearfield(candidate_nf, sample_id, frequency_hz, sensor_ids_used)
    n_sensors = int(len(sensor_ids_used))
    measurement = transform_measurement(measurement_raw, n_sensors, convention.measurement_transform)

    matrix = build_measurement_matrix_custom(layout, grid_positions, frequency_hz, convention.near_phase_sign)
    solution = solve_tikhonov(matrix, measurement, lam=lambda_reg)
    prediction = matrix @ solution
    residual = float(np.linalg.norm(prediction - measurement) / max(float(np.linalg.norm(measurement)), 1e-15))
    theta, phi, true_power, _ = farfield_power_from_table(farfield, sample_id, frequency_hz)
    rec_power = farfield_pattern_custom(grid_positions, solution, theta, phi, frequency_hz, convention.far_phase_sign)

    row: dict[str, object] = {
        "sample_id": sample_id,
        "frequency_hz": float(frequency_hz),
        "candidate": candidate_name,
        "candidate_method": str(candidate_group["method"].iloc[0]),
        "source_model": source_model,
        "grid_points": int(grid_positions.shape[0]),
        "unknown_count": int(matrix.shape[1]),
        "sensor_count": n_sensors,
        "measurement_channels": int(measurement.size),
        "channel_unknown_ratio": float(measurement.size / matrix.shape[1]),
        "lambda_reg": float(lambda_reg),
        "convention_id": convention.convention_id,
        "measurement_transform": convention.measurement_transform,
        "near_phase_sign": int(convention.near_phase_sign),
        "far_phase_sign": int(convention.far_phase_sign),
        "convention_note": convention.note,
        "nearfield_relative_residual": residual,
        "nearfield_power_nmse": nearfield_power_nmse(measurement, prediction, n_sensors),
    }
    if "extraction_method" in candidate_nf.columns:
        row["nearfield_extraction_method"] = "; ".join(sorted({str(value) for value in candidate_nf["extraction_method"].dropna().unique()}))
    if "extraction_method" in farfield.columns:
        row["farfield_extraction_method"] = "; ".join(sorted({str(value) for value in farfield["extraction_method"].dropna().unique()}))
    row.update(matrix_health(matrix))
    row.update(finite_metrics(pattern_metrics(true_power, rec_power, theta, phi)))
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


def run_check(args: argparse.Namespace) -> pd.DataFrame:
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)
    layouts = load_candidate_layouts(Path(args.layouts), args.candidates)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)
    configs = select_configs(args.configs)
    conventions = build_conventions(args.phase_pairs, args.transforms)

    rows: list[dict[str, object]] = []
    for config in configs:
        grid_positions = config_to_grid(config)
        for sample_id, frequency_hz in pairs:
            for candidate_name, candidate_group in layouts.items():
                for lambda_reg in args.lambda_regs:
                    for convention in conventions:
                        rows.append(
                            evaluate_case(
                                nearfield=nearfield,
                                farfield=farfield,
                                candidate_name=candidate_name,
                                candidate_group=candidate_group,
                                sample_id=sample_id,
                                frequency_hz=frequency_hz,
                                source_model=config.model_id,
                                grid_positions=grid_positions,
                                lambda_reg=lambda_reg,
                                convention=convention,
                            )
                        )
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    group_cols = [
        "source_model",
        "candidate",
        "lambda_reg",
        "convention_id",
        "measurement_transform",
        "near_phase_sign",
        "far_phase_sign",
        "grid_points",
    ]
    by_setting = (
        results.groupby(group_cols, as_index=False)
        .agg(
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_nearfield_relative_residual=("nearfield_relative_residual", "mean"),
            mean_nearfield_power_nmse=("nearfield_power_nmse", "mean"),
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
            "max_main_lobe_error_deg",
            "mean_nearfield_relative_residual",
        ],
        ascending=[True, False, True, True, True],
    ).drop(columns=["status_rank"])
    by_setting.to_csv(out_dir / "cst_convention_check_by_setting.csv", index=False, encoding="utf-8-sig")

    best = by_setting.iloc[0]
    current_direct = by_setting[by_setting["convention_id"] == "current_direct"]
    best_current = current_direct.iloc[0] if len(current_direct) else best
    default_cube = by_setting[by_setting["source_model"] == "default_cube_5x3x3"]
    best_default_cube = default_cube.iloc[0] if len(default_cube) else best
    default_current = default_cube[default_cube["convention_id"] == "current_direct"]
    best_default_current = default_current.iloc[0] if len(default_current) else best_default_cube

    nearfield_methods = sorted(
        {
            str(value)
            for value in results.get("nearfield_extraction_method", pd.Series(dtype=str)).dropna().unique()
            if str(value)
        }
    )
    farfield_methods = sorted(
        {
            str(value)
            for value in results.get("farfield_extraction_method", pd.Series(dtype=str)).dropna().unique()
            if str(value)
        }
    )
    summary = {
        "generated_by": "code/run_cst_level1_convention_check.py",
        "nearfield": display_path(Path(args.nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "layouts": display_path(Path(args.layouts)),
        "out_dir": display_path(out_dir),
        "pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "candidate_count": int(results["candidate"].nunique()),
        "source_model_count": int(results["source_model"].nunique()),
        "convention_count": int(results["convention_id"].nunique()),
        "best_setting": row_payload(best),
        "best_current_direct": row_payload(best_current),
        "best_default_cube": row_payload(best_default_cube),
        "best_default_cube_current_direct": row_payload(best_default_current),
        "nearfield_extraction_methods": nearfield_methods,
        "farfield_extraction_methods": farfield_methods,
    }
    (out_dir / "cst_convention_check_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown_summary(out_dir, by_setting, summary)
    return summary


def row_payload(row: pd.Series) -> dict[str, object]:
    return {
        "source_model": str(row["source_model"]),
        "candidate": str(row["candidate"]),
        "lambda_reg": float(row["lambda_reg"]),
        "convention_id": str(row["convention_id"]),
        "measurement_transform": str(row["measurement_transform"]),
        "near_phase_sign": int(row["near_phase_sign"]),
        "far_phase_sign": int(row["far_phase_sign"]),
        "status": str(row["status"]),
        "min_correlation": float(row["min_correlation"]),
        "max_nmse": float(row["max_nmse"]),
        "max_main_lobe_error_deg": float(row["max_main_lobe_error_deg"]),
        "mean_nearfield_relative_residual": float(row["mean_nearfield_relative_residual"]),
        "mean_nearfield_power_nmse": float(row["mean_nearfield_power_nmse"]),
    }


def write_markdown_summary(out_dir: Path, by_setting: pd.DataFrame, summary: dict[str, object]) -> None:
    rows = []
    for row in by_setting.itertuples(index=False):
        rows.append(
            f"| {row.source_model} | {row.convention_id} | {row.lambda_reg:.0e} | "
            f"{row.status} | {row.min_correlation:.4f} | {row.max_nmse:.4e} | "
            f"{row.max_main_lobe_error_deg:.2f} | {row.mean_nearfield_relative_residual:.3e} |"
        )

    best = summary["best_setting"]
    best_current = summary["best_current_direct"]
    best_default = summary["best_default_cube"]
    best_default_current = summary["best_default_cube_current_direct"]
    current_is_best = best["convention_id"] == "current_direct"
    default_gain = float(best_default["min_correlation"]) - float(best_default_current["min_correlation"])
    current_delta = abs(float(best["min_correlation"]) - float(best_current["min_correlation"])) + abs(
        float(best["max_nmse"]) - float(best_current["max_nmse"])
    )

    if current_is_best or current_delta < 1e-6:
        reading = """- The current em_core convention remains the best overall setting on this Level 1 check.
- Several sign-equivalent settings tie in far-field power metrics, which is expected for these single z-dipole Level 1 cases.
- This argues against a simple global phase-sign, complex-conjugation, or theta/phi label error.
- The generic grid should still be treated as a source-prior/model mismatch problem, not as a solved sampling result."""
    elif default_gain > 0.05:
        reading = f"""- A non-current convention improves the generic grid by about `{default_gain:.3f}` in worst-case correlation.
- Inspect the CST export sign, time convention, and polarization labels before adding more reconstruction complexity."""
    else:
        reading = """- A non-current convention ranks first, but the generic-grid gain is small.
- Treat this as diagnostic evidence rather than proof of a global convention mismatch."""

    content = f"""# CST Level 1 Convention Check

This directory tests whether the Level 1 inverse-model bottleneck is caused by
a simple field convention mismatch. It keeps the data and layouts fixed, then
crosses source models with:

- near/far propagation phase signs;
- complex conjugation of measured fields;
- theta/phi polarization sign and channel-label changes.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Candidate layouts | `{summary['layouts']}` |

## Best Overall Setting

| Field | Value |
|---|---|
| Source model | `{best['source_model']}` |
| Convention | `{best['convention_id']}` |
| Lambda | `{best['lambda_reg']:.0e}` |
| Status | `{best['status']}` |
| Min Corr | `{best['min_correlation']:.4f}` |
| Max NMSE | `{best['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best['max_main_lobe_error_deg']:.2f}` |
| Mean near-field residual | `{best['mean_nearfield_relative_residual']:.3e}` |

## Current Direct Baseline

| Field | Value |
|---|---|
| Source model | `{best_current['source_model']}` |
| Status | `{best_current['status']}` |
| Min Corr | `{best_current['min_correlation']:.4f}` |
| Max NMSE | `{best_current['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best_current['max_main_lobe_error_deg']:.2f}` |

## Generic Grid Check

| Field | Current direct | Best generic-grid setting |
|---|---:|---:|
| Convention | `{best_default_current['convention_id']}` | `{best_default['convention_id']}` |
| Min Corr | `{best_default_current['min_correlation']:.4f}` | `{best_default['min_correlation']:.4f}` |
| Max NMSE | `{best_default_current['max_nmse']:.4e}` | `{best_default['max_nmse']:.4e}` |
| Max lobe error / deg | `{best_default_current['max_main_lobe_error_deg']:.2f}` | `{best_default['max_main_lobe_error_deg']:.2f}` |

## Setting Ranking

| Source model | Convention | Lambda | Status | Min Corr | Max NMSE | Max lobe error / deg | Mean NF residual |
|---|---|---:|---|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

{reading}

## Important Boundary

The current Level 1 near-field table is derived from CST FarfieldPlot list
evaluation at the measurement directions. It is a solver-safe angular sample,
not a full-wave near-field monitor export. This check is therefore a convention
and model-risk diagnostic; it is not final proof for reduced sensor layouts.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_csv_arg(values: list[str] | None, defaults: tuple[str, ...]) -> list[str]:
    if not values:
        return list(defaults)
    parsed: list[str] = []
    for value in values:
        parsed.extend(item.strip() for item in value.split(",") if item.strip())
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check CST Level 1 phase and polarization conventions.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="CST near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="CST far-field CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    parser.add_argument("--candidate", action="append", dest="candidates", help="Candidate layout to include. Repeatable.")
    parser.add_argument("--config", action="append", dest="configs", help="Source model config id. Repeatable.")
    parser.add_argument("--lambda-reg", action="append", dest="lambda_regs", type=float, help="Tikhonov lambda. Repeatable.")
    parser.add_argument("--phase-pair", action="append", dest="phase_pairs", help="Phase pair id or comma-list.")
    parser.add_argument("--transform", action="append", dest="transforms", help="Measurement transform id or comma-list.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    args = parser.parse_args()
    args.candidates = args.candidates or list(DEFAULT_CANDIDATES)
    args.configs = args.configs or list(DEFAULT_CONFIGS)
    args.lambda_regs = args.lambda_regs or list(DEFAULT_LAMBDAS)
    args.phase_pairs = parse_csv_arg(args.phase_pairs, DEFAULT_PHASE_PAIRS)
    args.transforms = parse_csv_arg(args.transforms, DEFAULT_TRANSFORMS)
    return args


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = run_check(args)
    if results.empty:
        raise ValueError("convention check produced no rows")
    results.to_csv(out_dir / "cst_convention_check_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, out_dir, args)
    best = summary["best_setting"]
    print(f"CST convention check written to {out_dir}")
    print(f"best setting: {best['source_model']} {best['convention_id']} ({best['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
