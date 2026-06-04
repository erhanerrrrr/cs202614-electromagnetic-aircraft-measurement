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
DEFAULT_CASE_CSV = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "level1_required_meshsafe_huygens_cases.csv"
)
DEFAULT_BATCH_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_extrapolation_batch"
ETA0 = 376.730313668
COMPONENTS = ("Ex", "Ey", "Ez")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


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


def min_angle_to_region_deg(directions: np.ndarray, point_idx: int, region_mask: np.ndarray) -> float:
    if not bool(np.any(region_mask)):
        return 180.0
    dots = np.clip(directions[region_mask] @ directions[int(point_idx)], -1.0, 1.0)
    return float(np.rad2deg(np.arccos(float(np.max(dots)))))


def top_power_region_metrics(
    true_power: np.ndarray,
    predicted_power: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    threshold: float = 0.75,
) -> dict[str, float]:
    true_norm = true_power / max(float(np.max(true_power)), 1e-30)
    pred_norm = predicted_power / max(float(np.max(predicted_power)), 1e-30)
    true_region = true_norm >= threshold
    pred_region = pred_norm >= threshold
    intersection = true_region & pred_region
    union = true_region | pred_region
    true_lobe_power = float(np.sum(true_norm[true_region]))
    pred_lobe_power = float(np.sum(pred_norm[pred_region]))
    reference_capture = float(np.sum(true_norm[intersection]) / max(true_lobe_power, 1e-30))
    prediction_precision = float(np.sum(pred_norm[intersection]) / max(pred_lobe_power, 1e-30))
    true_peak = int(np.argmax(true_norm))
    pred_peak = int(np.argmax(pred_norm))
    directions, _, _ = spherical_basis(theta, phi)
    true_peak_to_pred_region = min_angle_to_region_deg(directions, true_peak, pred_region)
    pred_peak_to_true_region = min_angle_to_region_deg(directions, pred_peak, true_region)
    return {
        "main_lobe_region_threshold": float(threshold),
        "reference_lobe_region_points": int(np.sum(true_region)),
        "predicted_lobe_region_points": int(np.sum(pred_region)),
        "main_lobe_region_jaccard": float(np.sum(intersection) / max(int(np.sum(union)), 1)),
        "reference_lobe_region_capture": reference_capture,
        "predicted_lobe_region_precision": prediction_precision,
        "main_lobe_region_min_capture": float(min(reference_capture, prediction_precision)),
        "true_peak_to_pred_region_error_deg": true_peak_to_pred_region,
        "pred_peak_to_true_region_error_deg": pred_peak_to_true_region,
        "main_lobe_region_error_deg": float(max(true_peak_to_pred_region, pred_peak_to_true_region)),
    }


def combined_pattern_metrics(
    true_power: np.ndarray,
    predicted_power: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
) -> dict[str, float]:
    metrics = pattern_metrics(true_power, predicted_power, theta, phi)
    metrics.update(top_power_region_metrics(true_power, predicted_power, theta, phi))
    return metrics


def acceptance_status(row: dict[str, Any]) -> str:
    corr = float(row["correlation"])
    nmse = float(row["nmse"])
    lobe = float(row["main_lobe_error_deg"])
    scaled_nmse = float(row["scaled_power_nmse"])
    region_error = float(row.get("main_lobe_region_error_deg", lobe))
    region_capture = float(row.get("main_lobe_region_min_capture", 0.0))
    region_pass = region_error <= 5.0 and region_capture >= 0.75
    if corr >= 0.95 and nmse <= 1e-2 and scaled_nmse <= 1e-2 and lobe <= 5.0:
        return "strict_pass"
    if corr >= 0.95 and scaled_nmse <= 1e-2 and region_pass:
        return "region_shape_pass"
    if corr >= 0.95 and scaled_nmse <= 1e-2:
        return "shape_pass_lobe_ambiguous"
    if corr >= 0.90 and scaled_nmse <= 5e-2 and (lobe <= 10.0 or region_pass):
        return "physics_proxy_pass"
    if corr >= 0.75 and lobe <= 20.0:
        return "shape_diagnostic"
    return "diagnostic_only"


def status_rank(status: str) -> int:
    return {
        "strict_pass": 0,
        "physics_proxy_pass": 1,
        "region_shape_pass": 2,
        "shape_pass_lobe_ambiguous": 3,
        "shape_diagnostic": 3,
        "diagnostic_only": 3,
    }.get(status, 99)


def parse_sample_ids(value: str) -> set[str]:
    return {item.strip() for item in value.split(",") if item.strip()}


def batch_summary_row(summary: dict[str, Any], local_nearfield: Path, out_dir: Path) -> dict[str, Any]:
    best = summary["best_setting"]
    quality = summary["quality"]
    return {
        "sample_id": summary["sample_id"],
        "frequency_hz": summary["frequency_hz"],
        "status": "ok",
        "local_nearfield": display_path(local_nearfield),
        "out_dir": display_path(out_dir),
        "sensor_count": quality["sensor_count"],
        "tangential_to_total_l2_ratio": quality["tangential_to_total_l2_ratio"],
        "normal_to_total_l2_ratio": quality["normal_to_total_l2_ratio"],
        "dynamic_range_db": quality["dynamic_range_db"],
        "best_variant": best["variant"],
        "best_status": best["status"],
        "correlation": best["correlation"],
        "nmse": best["nmse"],
        "scaled_power_nmse": best["scaled_power_nmse"],
        "main_lobe_error_deg": best["main_lobe_error_deg"],
        "main_lobe_region_error_deg": best.get("main_lobe_region_error_deg", ""),
        "main_lobe_region_jaccard": best.get("main_lobe_region_jaccard", ""),
        "main_lobe_region_min_capture": best.get("main_lobe_region_min_capture", ""),
        "best_power_scale": best["best_power_scale"],
    }


def write_batch_readme(out_dir: Path, rows: pd.DataFrame, summary: dict[str, Any]) -> None:
    if rows.empty:
        table = "| Sample | Status |\n|---|---|\n"
    else:
        table_rows = []
        for row in rows.itertuples(index=False):
            if row.status != "ok":
                table_rows.append(f"| {row.sample_id} | {row.status} | - | - | - | - | - | - |")
                continue
            table_rows.append(
                f"| {row.sample_id} | {row.best_status} | {row.best_variant} | "
                f"{row.correlation:.4f} | {row.scaled_power_nmse:.4e} | "
                f"{row.main_lobe_error_deg:.2f} | {row.main_lobe_region_error_deg:.2f} | "
                f"{row.main_lobe_region_jaccard:.3f} |"
            )
        table = (
            "| Sample | Best status | Best variant | Corr | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard |\n"
            "|---|---|---|---:|---:|---:|---:|---:|\n"
            + "\n".join(table_rows)
            + "\n"
        )
    content = f"""# CST Mesh-Safe Huygens Batch Gate

This directory aggregates the local Huygens extrapolation diagnostics for all
available mesh-safe Level 1 CST exports. Each case keeps its own detailed
single-case report in a child directory, while this folder records the
cross-case pass/fail picture.

## Summary

- Cases requested: `{summary['case_count_requested']}`
- Cases completed: `{summary['case_count_completed']}`
- Missing/failed cases: `{summary['case_count_missing_or_failed']}`
- Best strict/physics-proxy cases: `{summary['case_count_strict_or_proxy']}`
- Best strict/physics-proxy/region cases: `{summary['case_count_strict_proxy_or_region']}`

## Case Table

{table}
## Reading

This is a batch data-chain gate, not the final Huygens physics proof. The
region-lobe metrics compare the overlap of the top-power directional regions,
which is more stable than a single argmax for broad or ring-like patterns. Final
claims still require a stricter vector surface-integral operator and H-field or
calibrated impedance support.

## Command

```powershell
python code\\run_cst_meshsafe_huygens_extrapolation.py --batch
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def run_batch(args: argparse.Namespace) -> dict[str, Any]:
    batch_out_dir = resolve_path(args.batch_out_dir)
    batch_out_dir.mkdir(parents=True, exist_ok=True)
    case_table = read_table(resolve_path(args.case_csv))
    selected_ids = parse_sample_ids(args.sample_ids)
    rows: list[dict[str, Any]] = []
    completed_summaries: list[dict[str, Any]] = []

    for case in case_table.to_dict(orient="records"):
        sample_id = str(case.get("sample_id", "")).strip()
        if selected_ids and sample_id not in selected_ids:
            continue
        frequency_hz = float(case.get("frequency_hz", args.frequency_hz))
        local_nearfield = resolve_path(str(case.get("nearfield_export", "")))
        case_out_dir = batch_out_dir / sample_id
        if not local_nearfield.exists():
            rows.append(
                {
                    "sample_id": sample_id,
                    "frequency_hz": frequency_hz,
                    "status": "missing_local_nearfield",
                    "local_nearfield": display_path(local_nearfield),
                    "out_dir": display_path(case_out_dir),
                }
            )
            continue
        case_args = argparse.Namespace(
            local_nearfield=local_nearfield,
            farfield=resolve_path(args.farfield),
            out_dir=case_out_dir,
            sample_id=sample_id,
            frequency_hz=frequency_hz,
        )
        try:
            case_summary = run(case_args)
            rows.append(batch_summary_row(case_summary, local_nearfield, case_out_dir))
            completed_summaries.append(case_summary)
        except Exception as exc:  # noqa: BLE001 - batch mode should report all cases.
            rows.append(
                {
                    "sample_id": sample_id,
                    "frequency_hz": frequency_hz,
                    "status": "failed",
                    "local_nearfield": display_path(local_nearfield),
                    "out_dir": display_path(case_out_dir),
                    "error": repr(exc),
                }
            )

    rows_df = pd.DataFrame(rows)
    if not rows_df.empty and "best_status" in rows_df.columns:
        rows_df["_status_rank"] = rows_df["best_status"].fillna("").map(status_rank).fillna(99)
        rows_df = rows_df.sort_values(["_status_rank", "sample_id"]).drop(columns=["_status_rank"])
    rows_df.to_csv(batch_out_dir / "meshsafe_huygens_batch_summary.csv", index=False, encoding="utf-8-sig")

    ok_rows = rows_df.loc[rows_df.get("status", pd.Series(dtype=str)) == "ok"] if not rows_df.empty else rows_df
    strict_or_proxy = 0
    strict_proxy_or_region = 0
    if not ok_rows.empty and "best_status" in ok_rows.columns:
        strict_or_proxy = int(ok_rows["best_status"].isin(["strict_pass", "physics_proxy_pass"]).sum())
        strict_proxy_or_region = int(
            ok_rows["best_status"].isin(["strict_pass", "physics_proxy_pass", "region_shape_pass"]).sum()
        )
    summary = {
        "generated_at": now_iso(),
        "generated_by": "code/run_cst_meshsafe_huygens_extrapolation.py --batch",
        "case_csv": display_path(resolve_path(args.case_csv)),
        "farfield": display_path(resolve_path(args.farfield)),
        "out_dir": display_path(batch_out_dir),
        "case_count_requested": int(len(rows)),
        "case_count_completed": int(len(completed_summaries)),
        "case_count_missing_or_failed": int(len(rows) - len(completed_summaries)),
        "case_count_strict_or_proxy": strict_or_proxy,
        "case_count_strict_proxy_or_region": strict_proxy_or_region,
        "case_summaries": completed_summaries,
    }
    write_json(batch_out_dir / "meshsafe_huygens_batch_summary.json", summary)
    write_batch_readme(batch_out_dir, rows_df, summary)
    return summary


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
        metrics = combined_pattern_metrics(true_power, predicted_power, theta, phi)
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
    command = (
        "python code\\run_cst_meshsafe_huygens_extrapolation.py "
        f"--local-nearfield {summary['local_nearfield']} "
        f"--sample-id {summary['sample_id']} "
        f"--out-dir {summary['out_dir']}"
    )
    rows = []
    for row in results.itertuples(index=False):
        rows.append(
            f"| {row.variant} | {row.status} | {row.correlation:.4f} | {row.nmse:.4e} | "
            f"{row.scaled_power_nmse:.4e} | {row.main_lobe_error_deg:.2f} | "
            f"{row.main_lobe_region_error_deg:.2f} | {row.main_lobe_region_jaccard:.3f} | "
            f"{row.best_power_scale:.4e} |"
        )
    content = f"""# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
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
| Region-lobe error / deg | `{best['main_lobe_region_error_deg']:.2f}` |
| Region-lobe Jaccard | `{best['main_lobe_region_jaccard']:.3f}` |
| Region-lobe min capture | `{best['main_lobe_region_min_capture']:.3f}` |

## Variant Ranking

| Variant | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

- This Python gate uses real CST local Huygens probe values
  instead of the previous FarfieldPlot-derived 13 m near-field surrogate.
- The equivalent-current formulas are deliberately kept as a diagnostic proxy:
  `J ~= -E_t/eta0` and `M = -n x E_t`. They are good enough to expose data
  quality, directionality, and sign conventions, but not final report-level
  Stratton-Chu/Huygens evidence.
- Broad, ring-like, or multi-peak reference patterns can make the single-point
  main-lobe metric stricter than the whole-pattern shape metrics. Treat
  `region_shape_pass` or `shape_pass_lobe_ambiguous` as good data-chain
  signals, not as final physics passes.
- Final G3 evidence still needs a stricter vector surface-integral operator
  plus H-field or impedance-backed current estimates.

## Generated Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_field_quality.csv` | Local field completeness and geometry/audit metrics. |
| `meshsafe_huygens_extrapolation_results.csv` | Per-variant far-field comparison metrics. |
| `meshsafe_huygens_best_farfield.csv` | Best diagnostic predicted/reference far-field table. |
| `meshsafe_huygens_extrapolation_summary.json` | Machine-readable summary. |

## Command

```powershell
{command}
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
    parser.add_argument("--batch", action="store_true", help="Run every available mesh-safe case from --case-csv.")
    parser.add_argument("--case-csv", type=Path, default=DEFAULT_CASE_CSV)
    parser.add_argument("--batch-out-dir", type=Path, default=DEFAULT_BATCH_OUT_DIR)
    parser.add_argument("--sample-ids", default="", help="Optional comma-separated subset for --batch.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.batch:
        summary = run_batch(args)
        print(f"CST mesh-safe Huygens batch gate written to {summary['out_dir']}")
        print(
            f"completed {summary['case_count_completed']}/{summary['case_count_requested']} cases; "
            f"strict_or_proxy={summary['case_count_strict_or_proxy']}; "
            f"strict_proxy_or_region={summary['case_count_strict_proxy_or_region']}"
        )
        return 0 if summary["case_count_missing_or_failed"] == 0 else 1
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
