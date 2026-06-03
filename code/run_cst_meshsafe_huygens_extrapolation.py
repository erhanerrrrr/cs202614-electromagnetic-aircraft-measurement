from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, read_table
from em_core import pattern_metrics, spherical_basis
from huygens_core import electric_dipole_far_field, magnetic_current_far_field


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_NEARFIELD = (
    ROOT
    / "data"
    / "cst_exports"
    / "level1_meshsafe_huygens"
    / "L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv"
)
DEFAULT_FARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_farfield.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_extrapolation"
ETA0 = 376.730313668
COMPONENTS = ("Ex", "Ey", "Ez")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_numeric(work: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = work.copy()
    for column in columns:
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def load_local_field(path: Path, sample_id: str, frequency_hz: float) -> pd.DataFrame:
    required = {
        "sample_id",
        "frequency_hz",
        "sensor_id",
        "node_id",
        "prior_id",
        "x_m",
        "y_m",
        "z_m",
        "normal_x",
        "normal_y",
        "normal_z",
        "tangent1_x",
        "tangent1_y",
        "tangent1_z",
        "tangent2_x",
        "tangent2_y",
        "tangent2_z",
        "weight_m2",
        "polarization",
        "e_real",
        "e_imag",
    }
    table = read_table(path)
    missing = sorted(required - set(table.columns))
    if missing:
        raise ValueError(f"local Huygens CSV missing required columns: {missing}")

    numeric_columns = [
        "frequency_hz",
        "sensor_id",
        "node_id",
        "x_m",
        "y_m",
        "z_m",
        "normal_x",
        "normal_y",
        "normal_z",
        "tangent1_x",
        "tangent1_y",
        "tangent1_z",
        "tangent2_x",
        "tangent2_y",
        "tangent2_z",
        "weight_m2",
        "e_real",
        "e_imag",
    ]
    work = as_numeric(table, numeric_columns)
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["polarization"] = work["polarization"].astype(str).str.strip()
    mask = (work["sample_id"] == sample_id) & np.isclose(work["frequency_hz"], frequency_hz)
    sub = work.loc[mask].copy()
    if sub.empty:
        raise ValueError(f"no local Huygens rows for sample_id={sample_id}, frequency_hz={frequency_hz}")
    if sub[numeric_columns].isna().any().any():
        bad_columns = sorted(column for column in numeric_columns if sub[column].isna().any())
        raise ValueError(f"local Huygens CSV has non-numeric values in: {bad_columns}")

    duplicate_count = int(sub.duplicated(["sensor_id", "polarization"]).sum())
    if duplicate_count:
        raise ValueError(f"local Huygens CSV has {duplicate_count} duplicate sensor/component rows")

    index_columns = [
        "sample_id",
        "frequency_hz",
        "sensor_id",
        "node_id",
        "prior_id",
        "x_m",
        "y_m",
        "z_m",
        "normal_x",
        "normal_y",
        "normal_z",
        "tangent1_x",
        "tangent1_y",
        "tangent1_z",
        "tangent2_x",
        "tangent2_y",
        "tangent2_z",
        "weight_m2",
    ]
    sub["e_complex"] = sub["e_real"].to_numpy(dtype=float) + 1j * sub["e_imag"].to_numpy(dtype=float)
    pivot = sub.pivot(index=index_columns, columns="polarization", values="e_complex").reset_index()
    missing_components = [component for component in COMPONENTS if component not in pivot.columns]
    if missing_components:
        raise ValueError(f"local Huygens CSV missing components: {missing_components}")
    pivot = pivot.sort_values("sensor_id").reset_index(drop=True)
    return pivot


def field_quality(surface: pd.DataFrame) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    positions = surface[["x_m", "y_m", "z_m"]].to_numpy(dtype=float)
    normals = surface[["normal_x", "normal_y", "normal_z"]].to_numpy(dtype=float)
    tangent1 = surface[["tangent1_x", "tangent1_y", "tangent1_z"]].to_numpy(dtype=float)
    tangent2 = surface[["tangent2_x", "tangent2_y", "tangent2_z"]].to_numpy(dtype=float)
    weights = surface["weight_m2"].to_numpy(dtype=float)
    field = np.column_stack([surface["Ex"].to_numpy(), surface["Ey"].to_numpy(), surface["Ez"].to_numpy()]).astype(
        np.complex128
    )
    normal_component = np.sum(field * normals, axis=1)
    tangential = field - normal_component[:, None] * normals
    t1_component = np.sum(tangential * tangent1, axis=1)
    t2_component = np.sum(tangential * tangent2, axis=1)
    total_norm = float(np.linalg.norm(field))
    tangential_norm = float(np.linalg.norm(tangential))
    normal_norm = float(np.linalg.norm(normal_component))
    amplitudes = np.linalg.norm(field, axis=1)
    center = np.mean(positions, axis=0)
    local_radii = np.linalg.norm(positions - center[None, :], axis=1)
    quality = {
        "sensor_count": int(surface.shape[0]),
        "component_rows_expected": int(surface.shape[0] * len(COMPONENTS)),
        "prior_id": str(surface["prior_id"].iloc[0]),
        "center_x_m": float(center[0]),
        "center_y_m": float(center[1]),
        "center_z_m": float(center[2]),
        "mean_local_radius_m": float(np.mean(local_radii)),
        "min_local_radius_m": float(np.min(local_radii)),
        "max_local_radius_m": float(np.max(local_radii)),
        "total_field_l2": total_norm,
        "tangential_field_l2": tangential_norm,
        "normal_field_l2": normal_norm,
        "normal_to_total_l2_ratio": float(normal_norm / max(total_norm, 1e-30)),
        "tangential_to_total_l2_ratio": float(tangential_norm / max(total_norm, 1e-30)),
        "min_sensor_field_abs": float(np.min(amplitudes)),
        "max_sensor_field_abs": float(np.max(amplitudes)),
        "median_sensor_field_abs": float(np.median(amplitudes)),
        "dynamic_range_db": float(
            20.0 * math.log10(max(float(np.max(amplitudes)), 1e-30) / max(float(np.min(amplitudes)), 1e-30))
        ),
    }
    arrays = {
        "positions": positions,
        "normals": normals,
        "weights": weights,
        "field": field,
        "tangential": tangential,
        "t1_component": t1_component,
        "t2_component": t2_component,
    }
    return quality, arrays


def equivalent_currents(arrays: dict[str, np.ndarray], variant: str) -> tuple[np.ndarray, np.ndarray, float, str]:
    normals = arrays["normals"]
    tangential = arrays["tangential"]
    magnetic_current = -np.cross(normals, tangential)
    electric_current = -tangential / ETA0
    zeros = np.zeros_like(tangential)
    if variant == "electric_only_outgoing":
        return electric_current, zeros, 1.0, "J=-E_t/eta0, M=0"
    if variant == "magnetic_only_plus":
        return zeros, magnetic_current, 1.0, "J=0, M=-n_cross_E_t"
    if variant == "magnetic_only_minus":
        return zeros, magnetic_current, -1.0, "J=0, M sign flipped"
    if variant == "outgoing_equivalence_plus":
        return electric_current, magnetic_current, 1.0, "J=-E_t/eta0, M=-n_cross_E_t"
    if variant == "outgoing_equivalence_minus":
        return electric_current, magnetic_current, -1.0, "J=-E_t/eta0, M sign flipped"
    raise ValueError(f"unknown equivalent-current variant: {variant}")


def farfield_from_currents(
    positions: np.ndarray,
    weights: np.ndarray,
    electric_current: np.ndarray,
    magnetic_current: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    frequency_hz: float,
    magnetic_sign: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r_hat, e_theta, e_phi = spherical_basis(theta, phi)
    field = np.zeros((theta.size, 3), dtype=np.complex128)
    for position, weight, j_vec, m_vec in zip(positions, weights, electric_current, magnetic_current):
        if np.linalg.norm(j_vec) > 0.0:
            field += electric_dipole_far_field(r_hat, position, j_vec * weight, frequency_hz)
        if np.linalg.norm(m_vec) > 0.0:
            field += magnetic_current_far_field(r_hat, position, m_vec * weight, frequency_hz, sign=magnetic_sign)
    e_theta_value = np.sum(field * e_theta, axis=1)
    e_phi_value = np.sum(field * e_phi, axis=1)
    power = np.abs(e_theta_value) ** 2 + np.abs(e_phi_value) ** 2
    return power, e_theta_value, e_phi_value


def scaled_power_nmse(true_power: np.ndarray, predicted_power: np.ndarray) -> tuple[float, float]:
    denom = float(np.sum(predicted_power**2))
    if denom <= 1e-30:
        return 0.0, math.inf
    scale = float(np.sum(true_power * predicted_power) / denom)
    nmse = float(np.sum((true_power - scale * predicted_power) ** 2) / max(float(np.sum(true_power**2)), 1e-30))
    return scale, nmse


def acceptance_status(row: dict[str, Any]) -> str:
    corr = float(row["correlation"])
    nmse = float(row["nmse"])
    lobe = float(row["main_lobe_error_deg"])
    scaled_nmse = float(row["scaled_power_nmse"])
    if corr >= 0.95 and nmse <= 1e-2 and scaled_nmse <= 1e-2 and lobe <= 5.0:
        return "strict_pass"
    if corr >= 0.95 and scaled_nmse <= 1e-2:
        return "shape_pass_lobe_ambiguous"
    if corr >= 0.90 and scaled_nmse <= 5e-2 and lobe <= 10.0:
        return "physics_proxy_pass"
    if corr >= 0.75 and lobe <= 20.0:
        return "shape_diagnostic"
    return "diagnostic_only"


def status_rank(status: str) -> int:
    return {
        "strict_pass": 0,
        "physics_proxy_pass": 1,
        "shape_pass_lobe_ambiguous": 2,
        "shape_diagnostic": 3,
        "diagnostic_only": 3,
    }.get(status, 99)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    local_field = load_local_field(Path(args.local_nearfield), args.sample_id, float(args.frequency_hz))
    quality, arrays = field_quality(local_field)
    farfield = read_table(args.farfield)
    theta, phi, true_power, farfield_shape = farfield_power_from_table(farfield, args.sample_id, float(args.frequency_hz))

    variants = [
        "electric_only_outgoing",
        "magnetic_only_plus",
        "magnetic_only_minus",
        "outgoing_equivalence_plus",
        "outgoing_equivalence_minus",
    ]
    result_rows: list[dict[str, Any]] = []
    prediction_cache: dict[str, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for variant in variants:
        electric_current, magnetic_current, magnetic_sign, model_note = equivalent_currents(arrays, variant)
        predicted_power, e_theta_value, e_phi_value = farfield_from_currents(
            arrays["positions"],
            arrays["weights"],
            electric_current,
            magnetic_current,
            theta,
            phi,
            float(args.frequency_hz),
            magnetic_sign,
        )
        metrics = pattern_metrics(true_power, predicted_power, theta, phi)
        if not math.isfinite(float(metrics.get("correlation", math.nan))):
            metrics["correlation"] = -1.0
        scale, scaled_nmse = scaled_power_nmse(true_power, predicted_power)
        row: dict[str, Any] = {
            "sample_id": args.sample_id,
            "frequency_hz": float(args.frequency_hz),
            "variant": variant,
            "model_note": model_note,
            "sensor_count": int(quality["sensor_count"]),
            "farfield_points": int(theta.size),
            "farfield_shape": "" if farfield_shape is None else f"{farfield_shape[0]}x{farfield_shape[1]}",
            "electric_current_l2": float(np.linalg.norm(electric_current)),
            "magnetic_current_l2": float(np.linalg.norm(magnetic_current)),
            "predicted_peak_power": float(np.max(predicted_power)),
            "reference_peak_power": float(np.max(true_power)),
            "best_power_scale": scale,
            "scaled_power_nmse": scaled_nmse,
        }
        row.update(metrics)
        row["status"] = acceptance_status(row)
        result_rows.append(row)
        prediction_cache[variant] = (predicted_power, e_theta_value, e_phi_value)

    results = pd.DataFrame(result_rows)
    results["status_rank"] = results["status"].map(status_rank)
    results = results.sort_values(
        ["status_rank", "correlation", "scaled_power_nmse", "nmse", "main_lobe_error_deg"],
        ascending=[True, False, True, True, True],
    ).drop(columns=["status_rank"])
    best = results.iloc[0].to_dict()
    best_power, best_e_theta, best_e_phi = prediction_cache[str(best["variant"])]

    pd.DataFrame([quality]).to_csv(out_dir / "meshsafe_huygens_field_quality.csv", index=False, encoding="utf-8-sig")
    results.to_csv(out_dir / "meshsafe_huygens_extrapolation_results.csv", index=False, encoding="utf-8-sig")
    farfield_rows = pd.DataFrame(
        {
            "sample_id": args.sample_id,
            "frequency_hz": float(args.frequency_hz),
            "theta_deg": np.rad2deg(theta),
            "phi_deg": np.rad2deg(phi),
            "reference_power": true_power,
            "predicted_power": best_power,
            "reference_power_norm": true_power / max(float(np.max(true_power)), 1e-30),
            "predicted_power_norm": best_power / max(float(np.max(best_power)), 1e-30),
            "predicted_e_theta_real": np.real(best_e_theta),
            "predicted_e_theta_imag": np.imag(best_e_theta),
            "predicted_e_phi_real": np.real(best_e_phi),
            "predicted_e_phi_imag": np.imag(best_e_phi),
        }
    )
    farfield_rows.to_csv(out_dir / "meshsafe_huygens_best_farfield.csv", index=False, encoding="utf-8-sig")

    summary = {
        "generated_at": now_iso(),
        "generated_by": "code/run_cst_meshsafe_huygens_extrapolation.py",
        "local_nearfield": display_path(Path(args.local_nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "out_dir": display_path(out_dir),
        "sample_id": args.sample_id,
        "frequency_hz": float(args.frequency_hz),
        "quality": quality,
        "best_setting": best,
        "variant_count": int(results.shape[0]),
        "interpretation": (
            "diagnostic Huygens/Kirchhoff proxy; use to verify the real CST local probe export and directionality, "
            "then replace with a stricter vector surface-integral operator before final report claims"
        ),
    }
    write_json(out_dir / "meshsafe_huygens_extrapolation_summary.json", summary)
    write_readme(out_dir, summary, results)
    return summary


def write_readme(out_dir: Path, summary: dict[str, Any], results: pd.DataFrame) -> None:
    best = summary["best_setting"]
    quality = summary["quality"]
    rows = []
    for row in results.itertuples(index=False):
        rows.append(
            f"| {row.variant} | {row.status} | {row.correlation:.4f} | {row.nmse:.4e} | "
            f"{row.scaled_power_nmse:.4e} | {row.main_lobe_error_deg:.2f} | {row.best_power_scale:.4e} |"
        )
    content = f"""# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates the first real CST local Huygens-surface probe export.
It consumes the `96 * 3 = 288` complex Cartesian E-field probe rows exported
through CST `ResultTree` and compares a diagnostic equivalent-current far-field
proxy against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `{summary['local_nearfield']}` |
| Far-field reference | `{summary['farfield']}` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `{quality['sensor_count']}` |
| Prior | `{quality['prior_id']}` |
| Mean local radius / m | `{quality['mean_local_radius_m']:.6g}` |
| Tangential/total L2 ratio | `{quality['tangential_to_total_l2_ratio']:.4f}` |
| Normal/total L2 ratio | `{quality['normal_to_total_l2_ratio']:.4f}` |
| Dynamic range / dB | `{quality['dynamic_range_db']:.2f}` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `{best['variant']}` |
| Status | `{best['status']}` |
| Correlation | `{best['correlation']:.4f}` |
| Normalized NMSE | `{best['nmse']:.4e}` |
| Scale-fitted power NMSE | `{best['scaled_power_nmse']:.4e}` |
| Main-lobe error / deg | `{best['main_lobe_error_deg']:.2f}` |

## Variant Ranking

| Variant | Status | Corr | Norm NMSE | Scaled NMSE | Main-lobe error / deg | Best power scale |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

- This is the first Python gate that uses real CST local Huygens probe values
  instead of the previous FarfieldPlot-derived 13 m near-field surrogate.
- The equivalent-current formulas are deliberately kept as a diagnostic proxy:
  `J ~= -E_t/eta0` and `M = -n x E_t`. They are good enough to expose data
  quality, directionality, and sign conventions, but not final report-level
  Stratton-Chu/Huygens evidence.
- The short-dipole reference has broad/ring-like high-power regions, so the
  single-point main-lobe error can be large even when whole-pattern correlation
  and scale-fitted NMSE are strong. Treat `shape_pass_lobe_ambiguous` as a good
  data-chain signal, not as a final physics pass.
- Final G3 evidence still needs a stricter vector surface-integral operator,
  an H-field or impedance-backed current estimate, and repetition on the
  second Level 1 source case.

## Generated Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_field_quality.csv` | Local field completeness and geometry/audit metrics. |
| `meshsafe_huygens_extrapolation_results.csv` | Per-variant far-field comparison metrics. |
| `meshsafe_huygens_best_farfield.csv` | Best diagnostic predicted/reference far-field table. |
| `meshsafe_huygens_extrapolation_summary.json` | Machine-readable summary. |

## Command

```powershell
python code\\run_cst_meshsafe_huygens_extrapolation.py
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CST mesh-safe local Huygens extrapolation gate.")
    parser.add_argument("--local-nearfield", type=Path, default=DEFAULT_LOCAL_NEARFIELD)
    parser.add_argument("--farfield", type=Path, default=DEFAULT_FARFIELD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-id", default="L1_short_dipole_z_1p2G")
    parser.add_argument("--frequency-hz", type=float, default=1.2e9)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run(args)
    best = summary["best_setting"]
    print(f"CST mesh-safe Huygens extrapolation written to {summary['out_dir']}")
    print(
        f"best diagnostic variant: {best['variant']} "
        f"({best['status']}, corr={best['correlation']:.4f}, scaled_nmse={best['scaled_power_nmse']:.4e})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
