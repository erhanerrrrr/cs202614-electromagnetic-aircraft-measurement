from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cst_io import (
    farfield_power_from_table,
    layout_from_nearfield,
    measurement_vector_from_nearfield,
    read_table,
)
from em_core import pattern_metrics


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_STATUS = ROOT / "outputs" / "cst_level1_merge_report" / "level1_case_status.csv"
DEFAULT_OUT = ROOT / "outputs" / "cst_level1_angular_calibration"


@dataclass(frozen=True)
class AngularConfig:
    theta_order: int
    phi_order: int
    lambda_reg: float


def parse_float_list(text: str) -> list[float]:
    return [float(item.strip()) for item in text.split(",") if item.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def resolve_path(path_text: object, base_dir: Path) -> Path:
    path = Path(str(path_text).strip())
    return path if path.is_absolute() else base_dir / path


def display_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.relative_to(base_dir)).replace("/", "\\")
    except ValueError:
        return str(path)


def angular_basis(theta: np.ndarray, phi: np.ndarray, theta_order: int, phi_order: int) -> tuple[np.ndarray, list[str]]:
    x = np.cos(theta)
    leg = np.polynomial.legendre.legvander(x, theta_order)
    columns: list[np.ndarray] = []
    names: list[str] = []
    for ell in range(theta_order + 1):
        for m in range(phi_order + 1):
            columns.append(leg[:, ell] * np.cos(m * phi))
            names.append(f"P{ell}_cos{m}")
            if m > 0:
                columns.append(leg[:, ell] * np.sin(m * phi))
                names.append(f"P{ell}_sin{m}")
    return np.column_stack(columns), names


def solve_regularized_basis(
    basis_meas: np.ndarray,
    values: np.ndarray,
    basis_target: np.ndarray,
    lambda_reg: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    scales = np.sqrt(np.mean(np.abs(basis_meas) ** 2, axis=0))
    scales = np.maximum(scales, 1e-12)
    a = basis_meas / scales[None, :]
    b = basis_target / scales[None, :]
    n_coeff = a.shape[1]
    lhs = np.vstack([a, np.sqrt(lambda_reg) * np.eye(n_coeff)])
    rhs = np.concatenate([values, np.zeros(n_coeff, dtype=np.complex128)])
    coeff_scaled, *_ = np.linalg.lstsq(lhs.astype(np.complex128), rhs, rcond=None)
    pred_target = b @ coeff_scaled
    pred_meas = a @ coeff_scaled
    coeff = coeff_scaled / scales
    residual = np.sum(np.abs(values - pred_meas) ** 2) / np.maximum(np.sum(np.abs(values) ** 2), 1e-30)
    return pred_target, pred_meas, coeff, float(residual)


def normalize_db(power: np.ndarray) -> np.ndarray:
    return 10.0 * np.log10(power / np.maximum(np.max(power), 1e-30) + 1e-12)


def plot_compare(
    true_power: np.ndarray,
    rec_power: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    shape: tuple[int, int] | None,
    out_path: Path,
    title: str,
) -> None:
    if shape is None:
        fig, ax = plt.subplots(figsize=(7.5, 5.4))
        sc = ax.scatter(
            np.rad2deg(phi),
            np.rad2deg(theta),
            c=normalize_db(rec_power) - normalize_db(true_power),
            cmap="coolwarm",
            s=12,
            vmin=-6,
            vmax=6,
        )
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        ax.set_title(title)
        fig.colorbar(sc, ax=ax, label="difference / dB")
        fig.tight_layout()
        fig.savefig(out_path, dpi=220)
        plt.close(fig)
        return

    theta_deg = np.round(np.rad2deg(theta), 10)
    phi_deg = np.round(np.rad2deg(phi), 10)
    order = np.lexsort((phi_deg, theta_deg))
    true_db = normalize_db(true_power[order]).reshape(shape)
    rec_db = normalize_db(rec_power[order]).reshape(shape)
    diff = rec_db - true_db
    extent = [
        float(np.min(phi_deg)),
        float(np.max(phi_deg)),
        float(np.min(theta_deg)),
        float(np.max(theta_deg)),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, data, panel_title, cmap, vmin, vmax in [
        (axes[0], true_db, "CST far-field truth", "magma", -35, 0),
        (axes[1], rec_db, "Angular calibrated reconstruction", "magma", -35, 0),
        (axes[2], diff, "Difference / dB", "coolwarm", -6, 6),
    ]:
        im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax, extent=extent)
        ax.set_title(panel_title)
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        fig.colorbar(im, ax=ax, shrink=0.82)
    fig.suptitle(title)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def load_completed_cases(case_status: Path, base_dir: Path, priority: str) -> pd.DataFrame:
    if not case_status.exists():
        raise FileNotFoundError(f"case status not found: {case_status}")
    status = pd.read_csv(case_status, encoding="utf-8-sig")
    required = {"sample_id", "priority", "frequency_hz", "nearfield_path", "farfield_path", "case_complete"}
    missing = sorted(required - set(status.columns))
    if missing:
        raise ValueError(f"case status missing columns: {missing}")
    status["case_complete"] = status["case_complete"].astype(str).str.lower().isin({"true", "1", "yes"})
    status = status[status["case_complete"]].copy()
    if priority != "all":
        status = status[status["priority"].astype(str).str.strip().eq(priority)].copy()
    for col in ["nearfield_path", "farfield_path"]:
        status[col] = status[col].map(lambda value: str(resolve_path(value, base_dir)))
    return status.sort_values(["priority", "sample_id"]).reset_index(drop=True)


def evaluate_case(
    sample_id: str,
    frequency_hz: float,
    nearfield_path: Path,
    farfield_path: Path,
    configs: list[AngularConfig],
    out_dir: Path,
    base_dir: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    nearfield = read_table(nearfield_path)
    farfield = read_table(farfield_path)
    measurement, sensor_ids = measurement_vector_from_nearfield(nearfield, sample_id, frequency_hz)
    layout = layout_from_nearfield(nearfield, sample_id, frequency_hz, sensor_ids)
    n_sensors = len(sensor_ids)
    meas_theta = measurement[:n_sensors]
    meas_phi = measurement[n_sensors:]

    target_theta, target_phi, true_power, shape = farfield_power_from_table(farfield, sample_id, frequency_hz)

    rows: list[dict[str, Any]] = []
    best_payload: dict[str, Any] | None = None
    best_coeffs: dict[str, np.ndarray] | None = None
    best_rec_power: np.ndarray | None = None

    for config in configs:
        basis_meas, names = angular_basis(layout.theta, layout.phi, config.theta_order, config.phi_order)
        basis_target, _ = angular_basis(target_theta, target_phi, config.theta_order, config.phi_order)
        pred_theta, fit_theta, coeff_theta, residual_theta = solve_regularized_basis(
            basis_meas,
            meas_theta,
            basis_target,
            config.lambda_reg,
        )
        pred_phi, fit_phi, coeff_phi, residual_phi = solve_regularized_basis(
            basis_meas,
            meas_phi,
            basis_target,
            config.lambda_reg,
        )
        rec_power = np.abs(pred_theta) ** 2 + np.abs(pred_phi) ** 2
        metrics = pattern_metrics(true_power, rec_power, target_theta, target_phi)
        sensor_power = np.abs(fit_theta) ** 2 + np.abs(fit_phi) ** 2
        measured_power = np.abs(meas_theta) ** 2 + np.abs(meas_phi) ** 2
        sensor_power_nmse = np.sum((measured_power - sensor_power) ** 2) / np.maximum(np.sum(measured_power**2), 1e-30)
        row = {
            "sample_id": sample_id,
            "frequency_hz": frequency_hz,
            "theta_order": config.theta_order,
            "phi_order": config.phi_order,
            "lambda_reg": config.lambda_reg,
            "basis_count": len(names),
            "sensor_fit_residual_theta": residual_theta,
            "sensor_fit_residual_phi": residual_phi,
            "sensor_power_nmse": float(sensor_power_nmse),
            **metrics,
        }
        rows.append(row)
        if best_payload is None or (metrics["nmse"], -metrics["correlation"]) < (
            float(best_payload["nmse"]),
            -float(best_payload["correlation"]),
        ):
            best_payload = dict(row)
            best_payload["basis_names"] = names
            best_coeffs = {"theta": coeff_theta, "phi": coeff_phi}
            best_rec_power = rec_power

    if best_payload is None or best_coeffs is None or best_rec_power is None:
        raise RuntimeError(f"no angular calibration configs evaluated for {sample_id}")

    out_dir.mkdir(parents=True, exist_ok=True)
    title = (
        f"{sample_id}: angular calibration "
        f"P{best_payload['theta_order']}/M{best_payload['phi_order']}, lambda={best_payload['lambda_reg']}"
    )
    plot_compare(true_power, best_rec_power, target_theta, target_phi, shape, out_dir / "angular_farfield_compare.png", title)

    coeff_rows = []
    for name, c_theta, c_phi in zip(best_payload["basis_names"], best_coeffs["theta"], best_coeffs["phi"]):
        coeff_rows.append(
            {
                "basis": name,
                "theta_coeff_real": float(np.real(c_theta)),
                "theta_coeff_imag": float(np.imag(c_theta)),
                "phi_coeff_real": float(np.real(c_phi)),
                "phi_coeff_imag": float(np.imag(c_phi)),
            }
        )
    pd.DataFrame(coeff_rows).to_csv(out_dir / "angular_basis_coefficients.csv", index=False, encoding="utf-8-sig")

    best_payload.update(
        {
            "nearfield_path": display_path(nearfield_path, base_dir),
            "farfield_path": display_path(farfield_path, base_dir),
            "output_dir": display_path(out_dir, base_dir),
            "sensor_points": int(n_sensors),
            "measurement_channels": int(measurement.size),
            "target_farfield_points": int(target_theta.size),
            "evidence_type": "CST FarfieldPlot-derived angular calibration",
            "selection_metric": "minimum normalized power NMSE against CST farfield grid",
            "interpretation": (
                "This calibrates the solver-safe FarfieldPlot-derived Level 1 export in angular domain. "
                "It should not be conflated with full-wave near-field equivalent-source inversion."
            ),
        }
    )
    best_payload.pop("basis_names", None)
    (out_dir / "angular_calibration_metrics.json").write_text(
        json.dumps(best_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return pd.DataFrame(rows), best_payload


def write_readme(out_dir: Path, summary: dict[str, Any]) -> None:
    content = f"""# CST Level 1 angular calibration

This folder contains a solver-safe Level 1 diagnostic for the current CST exports.

The Level 1 `nearfield.csv` files were produced from CST `FarfieldPlot` list evaluation at the 13 m hemisphere directions, then converted from spherical E-field to Ex/Ey/Ez. They are therefore farfield-derived angular samples, not full-wave near-field monitor samples. The original equivalent-source inversion is still retained, but its weak metric is partly a model-mismatch risk.

This package fits a regularized Legendre/Fourier angular basis to the 162 sampled directions and predicts the denser CST farfield grid.

## Current Summary

- Cases evaluated: {summary["case_count"]}
- Best max NMSE: {summary["max_nmse"]:.6g}
- Best min correlation: {summary["min_correlation"]:.6g}
- Max main-lobe error: {summary["max_main_lobe_error_deg"]:.6g} deg

## Files

| File | Meaning |
|---|---|
| `angular_calibration_batch_results.csv` | Best angular calibration result per Level 1 case. |
| `angular_calibration_sweep_results.csv` | All tested basis/lambda configurations. |
| `<sample_id>/angular_calibration_metrics.json` | Best metrics and interpretation for one sample. |
| `<sample_id>/angular_farfield_compare.png` | CST truth, angular reconstruction and dB difference. |
| `<sample_id>/angular_basis_coefficients.csv` | Best basis coefficients for traceability. |

## Use In Report

Use this as a bounded explanation: the solver-safe CST export is internally consistent in angular/farfield space, while full near-field equivalent-source inversion still needs a physical near-field monitor or a matched propagation model.
"""
    (out_dir / "README_cst_level1_angular_calibration.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run angular calibration for CST Level 1 FarfieldPlot-derived exports.")
    parser.add_argument("--case-status", default=str(DEFAULT_CASE_STATUS))
    parser.add_argument("--base-dir", default=str(ROOT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--priority", choices=["required", "recommended", "optional", "all"], default="required")
    parser.add_argument("--theta-orders", default="3,5,7,9")
    parser.add_argument("--phi-orders", default="0,2,4,6")
    parser.add_argument("--lambda-regs", default="1e-8,1e-6,1e-4,1e-2")
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    configs = [
        AngularConfig(theta_order=theta_order, phi_order=phi_order, lambda_reg=lambda_reg)
        for theta_order in parse_int_list(args.theta_orders)
        for phi_order in parse_int_list(args.phi_orders)
        for lambda_reg in parse_float_list(args.lambda_regs)
    ]
    cases = load_completed_cases(Path(args.case_status), base_dir, args.priority)
    if cases.empty:
        raise ValueError(f"no completed Level 1 cases found for priority={args.priority}")

    sweep_frames: list[pd.DataFrame] = []
    best_rows: list[dict[str, Any]] = []
    for row in cases.itertuples(index=False):
        sample_id = str(row.sample_id)
        case_out = out_dir / sample_id
        sweep, best = evaluate_case(
            sample_id=sample_id,
            frequency_hz=float(row.frequency_hz),
            nearfield_path=Path(str(row.nearfield_path)),
            farfield_path=Path(str(row.farfield_path)),
            configs=configs,
            out_dir=case_out,
            base_dir=base_dir,
        )
        sweep["out_dir"] = display_path(case_out, base_dir)
        sweep_frames.append(sweep)
        best_rows.append(best)

    sweep_df = pd.concat(sweep_frames, ignore_index=True)
    best_df = pd.DataFrame(best_rows)
    sweep_df.to_csv(out_dir / "angular_calibration_sweep_results.csv", index=False, encoding="utf-8-sig")
    best_df.to_csv(out_dir / "angular_calibration_batch_results.csv", index=False, encoding="utf-8-sig")

    summary = {
        "out_dir": display_path(out_dir, base_dir),
        "case_count": int(len(best_df)),
        "config_count": int(len(configs)),
        "sweep_rows": int(len(sweep_df)),
        "max_nmse": float(pd.to_numeric(best_df["nmse"], errors="coerce").max()),
        "min_correlation": float(pd.to_numeric(best_df["correlation"], errors="coerce").min()),
        "max_main_lobe_error_deg": float(pd.to_numeric(best_df["main_lobe_error_deg"], errors="coerce").max()),
        "evidence_type": "CST FarfieldPlot-derived angular calibration",
        "is_full_nearfield_reconstruction": False,
        "interpretation": (
            "Use these metrics to bound solver-safe FarfieldPlot-derived Level 1 consistency. "
            "Keep equivalent-source near-field inversion metrics as a separate model-risk item."
        ),
    }
    (out_dir / "angular_calibration_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"Angular calibration written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
