from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, layout_from_nearfield, measurement_vector_from_nearfield, read_table
from em_core import pattern_metrics


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_nearfield.csv"
DEFAULT_FARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_farfield.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "spherical_nf_ff_baseline"
DEFAULT_LMAX_VALUES = (2, 3, 4, 5, 6, 8, 10)
DEFAULT_LAMBDAS = (0.0, 1e-10, 1e-8, 1e-6)


try:
    from scipy.special import sph_harm_y as _sph_harm_y

    def spherical_harmonic(l: int, m: int, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        return _sph_harm_y(l, m, theta, phi)


except ImportError:  # pragma: no cover - compatibility for older SciPy
    from scipy.special import sph_harm as _sph_harm

    def spherical_harmonic(l: int, m: int, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        return _sph_harm(m, l, phi, theta)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def available_pairs(nearfield: pd.DataFrame) -> list[tuple[str, float]]:
    work = nearfield.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    pairs = work[["sample_id", "frequency_hz"]].drop_duplicates().dropna()
    return [(str(row.sample_id), float(row.frequency_hz)) for row in pairs.itertuples(index=False)]


def select_pairs(
    nearfield: pd.DataFrame,
    samples: list[str] | None,
    frequencies_hz: list[float] | None,
) -> list[tuple[str, float]]:
    pairs = available_pairs(nearfield)
    if samples:
        sample_set = set(samples)
        pairs = [pair for pair in pairs if pair[0] in sample_set]
    if frequencies_hz:
        freq_values = [float(value) for value in frequencies_hz]
        pairs = [pair for pair in pairs if any(np.isclose(pair[1], freq) for freq in freq_values)]
    if not pairs:
        raise ValueError("no sample/frequency pairs selected")
    return pairs


def mode_count(lmax: int, include_l0: bool) -> int:
    start = 0 if include_l0 else 1
    return sum(2 * l + 1 for l in range(start, lmax + 1))


def build_scalar_harmonic_matrix(theta: np.ndarray, phi: np.ndarray, lmax: int, include_l0: bool) -> tuple[np.ndarray, list[tuple[int, int]]]:
    modes: list[tuple[int, int]] = []
    columns: list[np.ndarray] = []
    start = 0 if include_l0 else 1
    for l in range(start, lmax + 1):
        for m in range(-l, l + 1):
            modes.append((l, m))
            columns.append(spherical_harmonic(l, m, theta, phi))
    if not columns:
        raise ValueError("empty spherical-harmonic basis")
    matrix = np.column_stack(columns).astype(np.complex128)
    return matrix, modes


def solve_ridge(matrix: np.ndarray, values: np.ndarray, lambda_reg: float) -> np.ndarray:
    if lambda_reg <= 0.0:
        coeffs, *_ = np.linalg.lstsq(matrix, values, rcond=None)
        return coeffs
    n_coeff = matrix.shape[1]
    lhs = np.vstack([matrix, np.sqrt(lambda_reg) * np.eye(n_coeff, dtype=np.complex128)])
    rhs = np.concatenate([values, np.zeros(n_coeff, dtype=np.complex128)])
    coeffs, *_ = np.linalg.lstsq(lhs, rhs, rcond=None)
    return coeffs


def condition_number(matrix: np.ndarray) -> float:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size == 0:
        return float("nan")
    smallest = float(np.min(singular_values))
    largest = float(np.max(singular_values))
    return largest / max(smallest, 1e-15)


def angular_distance_deg(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    va = np.array([np.sin(theta_a) * np.cos(phi_a), np.sin(theta_a) * np.sin(phi_a), np.cos(theta_a)])
    vb = np.array([np.sin(theta_b) * np.cos(phi_b), np.sin(theta_b) * np.sin(phi_b), np.cos(theta_b)])
    dot = float(np.clip(np.dot(va, vb), -1.0, 1.0))
    return float(np.rad2deg(np.arccos(dot)))


def component_relative_error(true_values: np.ndarray, pred_values: np.ndarray) -> float:
    return float(np.linalg.norm(pred_values - true_values) / max(float(np.linalg.norm(true_values)), 1e-30))


def complex_correlation_abs(true_values: np.ndarray, pred_values: np.ndarray) -> float:
    true_norm = float(np.linalg.norm(true_values))
    pred_norm = float(np.linalg.norm(pred_values))
    if true_norm <= 1e-30 and pred_norm <= 1e-30:
        return 1.0
    if true_norm <= 1e-30 or pred_norm <= 1e-30:
        return 0.0
    return float(abs(np.vdot(true_values, pred_values)) / max(true_norm * pred_norm, 1e-30))


def farfield_components_from_table(
    df: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None, np.ndarray | None, np.ndarray, tuple[int, int] | None]:
    theta, phi, power, shape = farfield_power_from_table(df, sample_id, frequency_hz)
    required = {"e_theta_real", "e_theta_imag", "e_phi_real", "e_phi_imag"}
    if not required.issubset(set(df.columns)):
        return theta, phi, None, None, power, shape

    work = df.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    mask = (work["sample_id"] == sample_id) & np.isclose(work["frequency_hz"], frequency_hz)
    sub = work.loc[mask].copy()
    if sub.empty:
        raise ValueError(f"no farfield rows for sample_id={sample_id}, frequency_hz={frequency_hz}")

    true_theta = pd.to_numeric(sub["e_theta_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
        sub["e_theta_imag"], errors="coerce"
    ).to_numpy(dtype=float)
    true_phi = pd.to_numeric(sub["e_phi_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
        sub["e_phi_imag"], errors="coerce"
    ).to_numpy(dtype=float)
    if np.isnan(true_theta).any() or np.isnan(true_phi).any():
        raise ValueError("farfield table contains non-numeric Etheta/Ephi values")
    return theta, phi, true_theta, true_phi, power, shape


def farfield_component_metrics(
    true_theta: np.ndarray | None,
    true_phi: np.ndarray | None,
    pred_theta: np.ndarray,
    pred_phi: np.ndarray,
) -> dict[str, float | str]:
    if true_theta is None or true_phi is None:
        return {
            "farfield_complex_component_status": "missing_complex_farfield_columns",
            "farfield_total_complex_correlation_abs": float("nan"),
            "farfield_total_complex_relative_l2_error": float("nan"),
            "theta_farfield_complex_correlation_abs": float("nan"),
            "phi_farfield_complex_correlation_abs": float("nan"),
            "theta_farfield_error_to_total_norm": float("nan"),
            "phi_farfield_error_to_total_norm": float("nan"),
            "theta_true_energy_fraction": float("nan"),
            "phi_true_energy_fraction": float("nan"),
            "theta_pred_energy_fraction": float("nan"),
            "phi_pred_energy_fraction": float("nan"),
        }

    true_total = np.concatenate([true_theta, true_phi])
    pred_total = np.concatenate([pred_theta, pred_phi])
    total_norm = max(float(np.linalg.norm(true_total)), 1e-30)
    pred_total_norm = max(float(np.linalg.norm(pred_total)), 1e-30)
    theta_true_norm = float(np.linalg.norm(true_theta))
    phi_true_norm = float(np.linalg.norm(true_phi))
    theta_pred_norm = float(np.linalg.norm(pred_theta))
    phi_pred_norm = float(np.linalg.norm(pred_phi))
    return {
        "farfield_complex_component_status": "available",
        "farfield_total_complex_correlation_abs": complex_correlation_abs(true_total, pred_total),
        "farfield_total_complex_relative_l2_error": float(np.linalg.norm(pred_total - true_total) / total_norm),
        "theta_farfield_complex_correlation_abs": complex_correlation_abs(true_theta, pred_theta),
        "phi_farfield_complex_correlation_abs": complex_correlation_abs(true_phi, pred_phi),
        "theta_farfield_error_to_total_norm": float(np.linalg.norm(pred_theta - true_theta) / total_norm),
        "phi_farfield_error_to_total_norm": float(np.linalg.norm(pred_phi - true_phi) / total_norm),
        "theta_true_energy_fraction": float(theta_true_norm**2 / max(total_norm**2, 1e-30)),
        "phi_true_energy_fraction": float(phi_true_norm**2 / max(total_norm**2, 1e-30)),
        "theta_pred_energy_fraction": float(theta_pred_norm**2 / max(pred_total_norm**2, 1e-30)),
        "phi_pred_energy_fraction": float(phi_pred_norm**2 / max(pred_total_norm**2, 1e-30)),
    }


def safe_float(value: object) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(numeric) or np.isinf(numeric):
        return None
    return numeric


def run_one_case(
    nearfield: pd.DataFrame,
    farfield: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    lmax: int,
    lambda_reg: float,
    include_l0: bool,
) -> dict[str, object]:
    layout = layout_from_nearfield(nearfield, sample_id, frequency_hz)
    measurement, sensor_ids = measurement_vector_from_nearfield(nearfield, sample_id, frequency_hz)
    sensor_count = int(sensor_ids.size)
    theta_measurement = measurement[:sensor_count]
    phi_measurement = measurement[sensor_count:]

    basis_nf, modes = build_scalar_harmonic_matrix(layout.theta, layout.phi, lmax, include_l0)
    coeff_theta = solve_ridge(basis_nf, theta_measurement, lambda_reg)
    coeff_phi = solve_ridge(basis_nf, phi_measurement, lambda_reg)
    theta_fit = basis_nf @ coeff_theta
    phi_fit = basis_nf @ coeff_phi
    nearfield_fit_error = component_relative_error(measurement, np.concatenate([theta_fit, phi_fit]))
    theta_fit_error = component_relative_error(theta_measurement, theta_fit)
    phi_fit_error = component_relative_error(phi_measurement, phi_fit)

    theta_ff, phi_ff, true_theta_ff, true_phi_ff, true_power, farfield_shape = farfield_components_from_table(
        farfield,
        sample_id,
        frequency_hz,
    )
    basis_ff, _ = build_scalar_harmonic_matrix(theta_ff, phi_ff, lmax, include_l0)
    pred_theta = basis_ff @ coeff_theta
    pred_phi = basis_ff @ coeff_phi
    pred_power = np.abs(pred_theta) ** 2 + np.abs(pred_phi) ** 2
    metrics = pattern_metrics(true_power, pred_power, theta_ff, phi_ff)
    component_metrics = farfield_component_metrics(true_theta_ff, true_phi_ff, pred_theta, pred_phi)

    true_peak = int(np.argmax(true_power))
    pred_peak = int(np.argmax(pred_power))
    peak_distance = angular_distance_deg(theta_ff[true_peak], phi_ff[true_peak], theta_ff[pred_peak], phi_ff[pred_peak])
    return {
        "sample_id": sample_id,
        "frequency_hz": float(frequency_hz),
        "lmax": int(lmax),
        "lambda_reg": float(lambda_reg),
        "include_l0": bool(include_l0),
        "mode_count": int(len(modes)),
        "sensor_count": sensor_count,
        "nearfield_row_count": int(2 * sensor_count),
        "farfield_row_count": int(theta_ff.size),
        "farfield_shape": "" if farfield_shape is None else f"{farfield_shape[0]}x{farfield_shape[1]}",
        "basis_condition": condition_number(basis_nf),
        "nearfield_fit_relative_error": nearfield_fit_error,
        "theta_fit_relative_error": theta_fit_error,
        "phi_fit_relative_error": phi_fit_error,
        "correlation": metrics["correlation"],
        "nmse": metrics["nmse"],
        "main_lobe_error_deg": metrics["main_lobe_error_deg"],
        "raw_peak_angular_distance_deg": peak_distance,
        "peak_error_db": metrics["peak_error_db"],
        **component_metrics,
        "true_peak_theta_deg": float(np.rad2deg(theta_ff[true_peak])),
        "true_peak_phi_deg": float(np.rad2deg(phi_ff[true_peak])),
        "pred_peak_theta_deg": float(np.rad2deg(theta_ff[pred_peak])),
        "pred_peak_phi_deg": float(np.rad2deg(phi_ff[pred_peak])),
    }


def status_for_row(row: pd.Series) -> str:
    min_corr = float(row["min_correlation"])
    max_nmse = float(row["max_nmse"])
    max_lobe_error = float(row["max_main_lobe_error_deg"])
    max_fit_error = float(row["max_nearfield_fit_relative_error"])
    if min_corr >= 0.98 and max_nmse <= 1e-2 and max_lobe_error <= 5.0 and max_fit_error <= 5e-2:
        return "strict_pass"
    if min_corr >= 0.95 and max_nmse <= 3e-2 and max_lobe_error <= 5.0:
        return "sanity_pass"
    if min_corr >= 0.95 and max_lobe_error <= 5.0:
        return "corr_lobe_pass_nmse_open"
    return "diagnostic_only"


def status_rank(status: str) -> int:
    return {
        "strict_pass": 0,
        "sanity_pass": 1,
        "corr_lobe_pass_nmse_open": 2,
        "diagnostic_only": 3,
    }.get(status, 99)


def summarize(results: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    by_setting = (
        results.groupby(["lmax", "lambda_reg", "include_l0", "mode_count"], as_index=False)
        .agg(
            sample_count=("sample_id", "nunique"),
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_nearfield_fit_relative_error=("nearfield_fit_relative_error", "mean"),
            max_nearfield_fit_relative_error=("nearfield_fit_relative_error", "max"),
            min_farfield_total_complex_correlation_abs=("farfield_total_complex_correlation_abs", "min"),
            max_farfield_total_complex_relative_l2_error=("farfield_total_complex_relative_l2_error", "max"),
            min_theta_farfield_complex_correlation_abs=("theta_farfield_complex_correlation_abs", "min"),
            min_phi_farfield_complex_correlation_abs=("phi_farfield_complex_correlation_abs", "min"),
            max_theta_farfield_error_to_total_norm=("theta_farfield_error_to_total_norm", "max"),
            max_phi_farfield_error_to_total_norm=("phi_farfield_error_to_total_norm", "max"),
            max_basis_condition=("basis_condition", "max"),
        )
    )
    by_setting["status"] = by_setting.apply(status_for_row, axis=1)
    by_setting["status_rank"] = by_setting["status"].map(status_rank)
    by_setting = by_setting.sort_values(
        [
            "status_rank",
            "max_main_lobe_error_deg",
            "max_basis_condition",
            "mode_count",
            "max_nearfield_fit_relative_error",
            "max_nmse",
            "min_correlation",
        ],
        ascending=[True, True, True, True, True, True, False],
    ).drop(columns=["status_rank"])
    by_setting.to_csv(out_dir / "spherical_nf_ff_by_setting.csv", index=False, encoding="utf-8-sig")

    best = by_setting.iloc[0]
    best_filter = (
        (results["lmax"] == best["lmax"])
        & (results["lambda_reg"].astype(float) == float(best["lambda_reg"]))
        & (results["include_l0"] == best["include_l0"])
    )
    best_cases = results.loc[best_filter].sort_values(["sample_id", "frequency_hz"])
    best_cases.to_csv(out_dir / "spherical_nf_ff_best_cases.csv", index=False, encoding="utf-8-sig")

    summary = {
        "generated_by": "code/run_spherical_nf_ff_baseline.py",
        "nearfield": rel(Path(args.nearfield)),
        "farfield": rel(Path(args.farfield)),
        "out_dir": rel(out_dir),
        "basis": "independent scalar spherical-harmonic fit for tangential Etheta/Ephi components",
        "is_full_vector_swe": False,
        "purpose": "NF-FF/SWE sanity baseline for angle, phase, and polarization consistency before reduced sampling claims.",
        "sample_frequency_pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "lmax_values": [int(value) for value in sorted(results["lmax"].unique())],
        "lambda_regs": [float(value) for value in sorted(results["lambda_reg"].unique())],
        "include_l0": bool(args.include_l0),
        "best_setting": {
            "lmax": int(best["lmax"]),
            "lambda_reg": float(best["lambda_reg"]),
            "include_l0": bool(best["include_l0"]),
            "mode_count": int(best["mode_count"]),
            "status": str(best["status"]),
            "min_correlation": float(best["min_correlation"]),
            "max_nmse": float(best["max_nmse"]),
            "max_main_lobe_error_deg": float(best["max_main_lobe_error_deg"]),
            "max_nearfield_fit_relative_error": float(best["max_nearfield_fit_relative_error"]),
            "min_farfield_total_complex_correlation_abs": safe_float(
                best["min_farfield_total_complex_correlation_abs"]
            ),
            "max_farfield_total_complex_relative_l2_error": safe_float(
                best["max_farfield_total_complex_relative_l2_error"]
            ),
            "min_theta_farfield_complex_correlation_abs": safe_float(
                best["min_theta_farfield_complex_correlation_abs"]
            ),
            "min_phi_farfield_complex_correlation_abs": safe_float(best["min_phi_farfield_complex_correlation_abs"]),
            "max_theta_farfield_error_to_total_norm": safe_float(best["max_theta_farfield_error_to_total_norm"]),
            "max_phi_farfield_error_to_total_norm": safe_float(best["max_phi_farfield_error_to_total_norm"]),
            "max_basis_condition": float(best["max_basis_condition"]),
        },
    }
    (out_dir / "spherical_nf_ff_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, by_setting, best_cases, summary)
    return summary


def write_readme(out_dir: Path, by_setting: pd.DataFrame, best_cases: pd.DataFrame, summary: dict[str, object]) -> None:
    best = summary["best_setting"]
    rows = []
    for row in by_setting.head(12).itertuples(index=False):
        rows.append(
            f"| {int(row.lmax)} | {row.lambda_reg:.0e} | {int(row.mode_count)} | {row.status} | "
            f"{row.min_correlation:.4f} | {row.max_nmse:.4e} | {row.max_main_lobe_error_deg:.2f} | "
            f"{row.max_nearfield_fit_relative_error:.4e} | "
            f"{row.min_farfield_total_complex_correlation_abs:.4f} | "
            f"{row.max_farfield_total_complex_relative_l2_error:.4e} | {row.max_basis_condition:.3e} |"
        )
    case_rows = []
    for row in best_cases.itertuples(index=False):
        case_rows.append(
            f"| {row.sample_id} | {row.frequency_hz:.0f} | {row.correlation:.4f} | {row.nmse:.4e} | "
            f"{row.main_lobe_error_deg:.2f} | {row.nearfield_fit_relative_error:.4e} | "
            f"{row.farfield_total_complex_correlation_abs:.4f} | "
            f"{row.farfield_total_complex_relative_l2_error:.4e} | "
            f"({row.true_peak_theta_deg:.1f}, {row.true_peak_phi_deg:.1f}) | "
            f"({row.pred_peak_theta_deg:.1f}, {row.pred_peak_phi_deg:.1f}) |"
        )

    if best["status"] == "strict_pass":
        reading = """- The angular spherical-harmonic baseline passes the current Level 1 sanity gate.
- This supports the coordinate, polarization, and far-field comparison chain for
  the current Level 1 data path.
- It still does not prove reduced 120/81/48/32 sampling layouts; those must be
  rerun after the full-grid physical baseline is frozen."""
    elif best["status"] == "sanity_pass":
        reading = """- The angular spherical-harmonic baseline is good enough as an independent
  sanity check, but at least one strict metric remains open.
- Use it as a convention and data-path check, not as final SWE evidence."""
    else:
        reading = """- The angular spherical-harmonic baseline remains diagnostic.
- Investigate true near-field monitor exports, angular conventions, and a full
  vector SWE/Huygens formulation before using this as report-level proof."""

    content = f"""# Spherical NF-FF Sanity Baseline

This directory stores a lightweight spherical near-field to far-field sanity
baseline for the current CST Level 1 exports.

The method fits the tangential near-field samples, `Etheta` and `Ephi`, with
independent scalar spherical-harmonic expansions and evaluates the fitted field
on the far-field angular grid. This is a useful convention and data-path check,
but it is not a full vector spherical-wave expansion.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |

## Best Setting

| Field | Value |
|---|---|
| Lmax | `{best['lmax']}` |
| Lambda | `{best['lambda_reg']:.0e}` |
| Modes per component | `{best['mode_count']}` |
| Status | `{best['status']}` |
| Min Corr | `{best['min_correlation']:.4f}` |
| Max NMSE | `{best['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best['max_main_lobe_error_deg']:.2f}` |
| Max near-field fit relative error | `{best['max_nearfield_fit_relative_error']:.4e}` |
| Min far-field total complex correlation | `{best['min_farfield_total_complex_correlation_abs']}` |
| Max far-field total complex L2 error | `{best['max_farfield_total_complex_relative_l2_error']}` |
| Min theta-component complex correlation | `{best['min_theta_farfield_complex_correlation_abs']}` |
| Min phi-component complex correlation | `{best['min_phi_farfield_complex_correlation_abs']}` |

## Top Settings

| Lmax | Lambda | Modes | Status | Min power Corr | Max power NMSE | Max lobe error / deg | Max NF fit error | Min FF complex Corr | Max FF complex L2 | Max condition |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Best-Setting Case Results

| Sample | Frequency Hz | Power Corr | Power NMSE | Lobe error / deg | NF fit error | FF complex Corr | FF complex L2 | True peak theta/phi | Pred peak theta/phi |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
{chr(10).join(case_rows)}

## Reading

{reading}

## Boundary

The current near-field input is still FarfieldPlot-derived angular data. Once
true CST near-field monitor exports are available, rerun this script on that
authoritative table before upgrading the wording in the report.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a lightweight spherical NF-FF sanity baseline on CST Level 1 data.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="Far-field CSV/XLSX.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    parser.add_argument("--lmax", action="append", dest="lmax_values", type=int, help="Maximum spherical harmonic degree. Repeatable.")
    parser.add_argument("--lambda-reg", action="append", dest="lambda_regs", type=float, help="Ridge regularization value. Repeatable.")
    parser.add_argument("--include-l0", action="store_true", help="Include l=0 scalar basis functions.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    args = parser.parse_args()
    args.lmax_values = args.lmax_values or list(DEFAULT_LMAX_VALUES)
    args.lambda_regs = args.lambda_regs or list(DEFAULT_LAMBDAS)
    if any(value < 1 for value in args.lmax_values):
        raise ValueError("lmax values must be >= 1")
    return args


def main() -> int:
    args = parse_args()
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)

    rows: list[dict[str, object]] = []
    for sample_id, frequency_hz in pairs:
        for lmax in args.lmax_values:
            for lambda_reg in args.lambda_regs:
                rows.append(
                    run_one_case(
                        nearfield=nearfield,
                        farfield=farfield,
                        sample_id=sample_id,
                        frequency_hz=frequency_hz,
                        lmax=lmax,
                        lambda_reg=lambda_reg,
                        include_l0=bool(args.include_l0),
                    )
                )
    results = pd.DataFrame(rows)
    if results.empty:
        raise ValueError("spherical NF-FF baseline produced no rows")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_dir / "spherical_nf_ff_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, out_dir, args)
    best = summary["best_setting"]
    print(f"spherical NF-FF sanity baseline written to {out_dir}")
    print(
        "best setting: "
        f"lmax={best['lmax']}, lambda={best['lambda_reg']:.0e}, "
        f"status={best['status']}, min_corr={best['min_correlation']:.4f}, max_nmse={best['max_nmse']:.4e}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
