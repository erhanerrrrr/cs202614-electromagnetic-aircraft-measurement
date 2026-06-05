from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import run_cst_meshsafe_huygens_extrapolation as huygens_gate
from cst_io import read_table


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCAL_EFIELD = (
    ROOT
    / "data"
    / "cst_exports"
    / "level1_meshsafe_huygens_source_family"
    / "L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv"
)
DEFAULT_LOCAL_HFIELD = (
    ROOT
    / "data"
    / "cst_exports"
    / "level1_meshsafe_huygens_source_family"
    / "L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_hfield.csv"
)
DEFAULT_FARFIELD = (
    ROOT
    / "data"
    / "cst_exports"
    / "level1_meshsafe_huygens_source_family"
    / "L1_short_dipole_x_1p2G_farfield.csv"
)
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_source_family_reduced_layout_x"
DEFAULT_COUNTS = (72, 48, 32, 24)
DEFAULT_METHODS = ("geometric_farthest", "fibonacci_snap", "field_weighted")
DEFAULT_FROZEN_VARIANT = "eh_love_equivalence_minus_j96"
E_COMPONENTS = ("Ex", "Ey", "Ez")
H_COMPONENTS = ("Hx", "Hy", "Hz")


@dataclass(frozen=True)
class LayoutSpec:
    name: str
    method: str
    count: int
    indices: np.ndarray
    note: str


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


def parse_csv_ints(value: str) -> list[int]:
    out: list[int] = []
    for item in value.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        parsed = int(stripped)
        if parsed <= 0:
            raise ValueError(f"counts must be positive, got {parsed}")
        if parsed not in out:
            out.append(parsed)
    if not out:
        raise ValueError("at least one count is required")
    return out


def parse_methods(value: str) -> list[str]:
    allowed = set(DEFAULT_METHODS)
    methods: list[str] = []
    for item in value.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        if stripped not in allowed:
            raise ValueError(f"unknown method {stripped!r}; expected one of {sorted(allowed)}")
        if stripped not in methods:
            methods.append(stripped)
    if not methods:
        raise ValueError("at least one layout method is required")
    return methods


def unit_rows(values: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(values, axis=1)
    return values / np.maximum(norms[:, None], 1e-30)


def local_directions(surface: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    positions = surface[["x_m", "y_m", "z_m"]].to_numpy(dtype=float)
    center = np.mean(positions, axis=0)
    directions = unit_rows(positions - center[None, :])
    return positions, center, directions


def angular_distance_matrix(directions: np.ndarray) -> np.ndarray:
    dots = np.clip(directions @ directions.T, -1.0, 1.0)
    return np.rad2deg(np.arccos(dots))


def spatial_metrics(surface: pd.DataFrame, indices: np.ndarray) -> dict[str, float]:
    _, center, directions = local_directions(surface)
    selected = directions[indices]
    if len(indices) <= 1:
        nearest = np.asarray([0.0])
    else:
        distances = angular_distance_matrix(selected)
        np.fill_diagonal(distances, np.inf)
        nearest = np.min(distances, axis=1)
    z_axis = np.array([0.0, 0.0, 1.0])
    theta = np.rad2deg(np.arccos(np.clip(selected @ z_axis, -1.0, 1.0)))
    weights = surface.iloc[indices]["weight_m2"].to_numpy(dtype=float)
    return {
        "center_x_m": float(center[0]),
        "center_y_m": float(center[1]),
        "center_z_m": float(center[2]),
        "min_angular_sep_deg": float(np.min(nearest)),
        "median_nn_angular_sep_deg": float(np.median(nearest)),
        "mean_theta_deg": float(np.mean(theta)),
        "theta_span_deg": float(np.max(theta) - np.min(theta)),
        "selected_weight_sum_m2": float(np.sum(weights)),
    }


def farthest_point_subset(directions: np.ndarray, count: int, seed_idx: int | None = None) -> np.ndarray:
    if count >= directions.shape[0]:
        return np.arange(directions.shape[0], dtype=int)
    if seed_idx is None:
        x_axis = np.array([1.0, 0.0, 0.0])
        seed_idx = int(np.argmax(directions @ x_axis))
    selected = [int(seed_idx)]
    min_distance = np.linalg.norm(directions - directions[selected[0]], axis=1)
    while len(selected) < count:
        min_distance[np.asarray(selected, dtype=int)] = -1.0
        idx = int(np.argmax(min_distance))
        selected.append(idx)
        new_distance = np.linalg.norm(directions - directions[idx], axis=1)
        min_distance = np.minimum(min_distance, new_distance)
    return np.asarray(selected, dtype=int)


def fibonacci_sphere_directions(count: int) -> np.ndarray:
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    k = np.arange(count, dtype=float)
    z = 1.0 - 2.0 * (k + 0.5) / count
    radius = np.sqrt(np.maximum(1.0 - z**2, 0.0))
    phi = (k * golden_angle) % (2.0 * math.pi)
    return np.column_stack([radius * np.cos(phi), radius * np.sin(phi), z])


def nearest_unique_snap(directions: np.ndarray, targets: np.ndarray, count: int) -> np.ndarray:
    selected: list[int] = []
    used: set[int] = set()
    for target in targets:
        order = np.argsort(-(directions @ target))
        for idx in order:
            candidate = int(idx)
            if candidate not in used:
                selected.append(candidate)
                used.add(candidate)
                break
    if len(selected) < count:
        filler = farthest_point_subset(directions, count, selected[0] if selected else None)
        for idx in filler:
            candidate = int(idx)
            if candidate not in used:
                selected.append(candidate)
                used.add(candidate)
            if len(selected) >= count:
                break
    return np.asarray(selected[:count], dtype=int)


def weighted_farthest_subset(directions: np.ndarray, weights: np.ndarray, count: int) -> np.ndarray:
    if count >= directions.shape[0]:
        return np.arange(directions.shape[0], dtype=int)
    weights = np.asarray(weights, dtype=float)
    weights = weights - np.min(weights)
    if np.max(weights) > 0.0:
        weights = weights / np.max(weights)
    else:
        weights = np.ones_like(weights)
    selected = [int(np.argmax(weights))]
    min_distance = np.linalg.norm(directions - directions[selected[0]], axis=1)
    while len(selected) < count:
        score = min_distance * (0.65 + 0.35 * weights)
        score[np.asarray(selected, dtype=int)] = -1.0
        idx = int(np.argmax(score))
        selected.append(idx)
        new_distance = np.linalg.norm(directions - directions[idx], axis=1)
        min_distance = np.minimum(min_distance, new_distance)
    return np.asarray(selected, dtype=int)


def monomial_powers(max_degree: int) -> list[tuple[int, int, int]]:
    powers: list[tuple[int, int, int]] = []
    for total in range(max_degree + 1):
        for px in range(total + 1):
            for py in range(total - px + 1):
                pz = total - px - py
                powers.append((px, py, pz))
    return powers


def basis_size(max_degree: int) -> int:
    return len(monomial_powers(max_degree))


def choose_polynomial_degree(sensor_count: int, max_degree: int) -> int:
    degree = 0
    for candidate in range(max_degree + 1):
        if basis_size(candidate) <= max(1, int(0.85 * sensor_count)):
            degree = candidate
    return degree


def polynomial_basis(directions: np.ndarray, powers: list[tuple[int, int, int]]) -> np.ndarray:
    x = directions[:, 0]
    y = directions[:, 1]
    z = directions[:, 2]
    columns = [(x**px) * (y**py) * (z**pz) for px, py, pz in powers]
    return np.column_stack(columns).astype(float)


def fit_predict_complex(
    full_basis: np.ndarray,
    selected_indices: np.ndarray,
    values: np.ndarray,
    ridge: float,
    preserve_selected: bool = True,
) -> np.ndarray:
    basis_scale = np.sqrt(np.mean(full_basis**2, axis=0))
    scaled_full = full_basis / np.maximum(basis_scale[None, :], 1e-12)
    selected_basis = scaled_full[selected_indices]
    gram = selected_basis.conj().T @ selected_basis
    penalty = float(ridge) * np.trace(gram).real / max(float(gram.shape[0]), 1.0)
    coef = np.linalg.solve(gram + penalty * np.eye(gram.shape[0]), selected_basis.conj().T @ values[selected_indices])
    predicted = scaled_full @ coef
    if preserve_selected:
        predicted[selected_indices] = values[selected_indices]
    return predicted


def reconstructed_surface(
    surface: pd.DataFrame,
    selected_indices: np.ndarray,
    components: tuple[str, str, str],
    degree: int,
    ridge: float,
) -> pd.DataFrame:
    _, _, directions = local_directions(surface)
    powers = monomial_powers(degree)
    basis = polynomial_basis(directions, powers)
    out = surface.copy()
    for component in components:
        values = out[component].to_numpy(dtype=np.complex128)
        out[component] = fit_predict_complex(basis, selected_indices, values, ridge)
    return out


def complex_matrix(surface: pd.DataFrame, components: tuple[str, str, str]) -> np.ndarray:
    return np.column_stack([surface[component].to_numpy(dtype=np.complex128) for component in components])


def normalized_complex_correlation(reference: np.ndarray, predicted: np.ndarray) -> float:
    ref = reference.reshape(-1)
    pred = predicted.reshape(-1)
    denom = float(np.linalg.norm(ref) * np.linalg.norm(pred))
    if denom <= 1e-30:
        return math.nan
    return float(abs(np.vdot(ref, pred)) / denom)


def reconstruction_error_metrics(
    reference: pd.DataFrame,
    reconstructed: pd.DataFrame,
    components: tuple[str, str, str],
    selected_indices: np.ndarray,
    prefix: str,
) -> dict[str, float]:
    reference_values = complex_matrix(reference, components)
    reconstructed_values = complex_matrix(reconstructed, components)
    all_error = np.linalg.norm(reconstructed_values - reference_values) / max(float(np.linalg.norm(reference_values)), 1e-30)
    mask = np.ones(reference_values.shape[0], dtype=bool)
    mask[selected_indices] = False
    if bool(np.any(mask)):
        holdout_reference = reference_values[mask]
        holdout_reconstructed = reconstructed_values[mask]
        holdout_error = np.linalg.norm(holdout_reconstructed - holdout_reference) / max(
            float(np.linalg.norm(holdout_reference)),
            1e-30,
        )
        holdout_corr = normalized_complex_correlation(holdout_reference, holdout_reconstructed)
    else:
        holdout_error = math.nan
        holdout_corr = math.nan
    return {
        f"{prefix}_reconstruction_all_nrmse": float(all_error),
        f"{prefix}_reconstruction_holdout_nrmse": float(holdout_error),
        f"{prefix}_reconstruction_holdout_correlation": float(holdout_corr),
    }


def pivot_to_long_template(
    template_table: pd.DataFrame,
    reconstructed: pd.DataFrame,
    components: tuple[str, str, str],
    real_column: str,
    imag_column: str,
    layout: LayoutSpec,
    selected_sensor_ids: list[str],
    model: str,
    degree: int,
    out_path: Path,
) -> None:
    selected_set = set(selected_sensor_ids)
    value_map: dict[tuple[str, str], complex] = {}
    for row in reconstructed.itertuples(index=False):
        sensor_id = str(getattr(row, "sensor_id"))
        for component in components:
            value_map[(sensor_id, component)] = complex(getattr(row, component))
    work = template_table.copy()
    work["sensor_id"] = work["sensor_id"].astype(str)
    values = [value_map[(str(row.sensor_id), str(row.polarization))] for row in work.itertuples(index=False)]
    work[real_column] = [float(np.real(value)) for value in values]
    work[imag_column] = [float(np.imag(value)) for value in values]
    work["layout_candidate"] = layout.name
    work["layout_method"] = layout.method
    work["layout_sensor_count"] = int(layout.count)
    work["selected_for_measurement"] = work["sensor_id"].isin(selected_set)
    work["reconstruction_model"] = model
    work["reconstruction_degree"] = int(degree)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    work.to_csv(out_path, index=False, encoding="utf-8-sig")


def field_selection_weights(surface: pd.DataFrame, hfield_surface: pd.DataFrame) -> np.ndarray:
    _, arrays = huygens_gate.field_quality(surface, hfield_surface)
    e_strength = np.linalg.norm(arrays["tangential"], axis=1)
    h_strength = np.linalg.norm(arrays["h_tangential"], axis=1) * huygens_gate.ETA0
    combined = e_strength + h_strength
    return combined / max(float(np.max(combined)), 1e-30)


def make_layouts(surface: pd.DataFrame, hfield_surface: pd.DataFrame, counts: list[int], methods: list[str]) -> list[LayoutSpec]:
    _, _, directions = local_directions(surface)
    n_total = int(surface.shape[0])
    layouts = [
        LayoutSpec(
            name=f"full_{n_total}",
            method="full",
            count=n_total,
            indices=np.arange(n_total, dtype=int),
            note="Full exported 96-point local sphere baseline.",
        )
    ]
    field_weights = field_selection_weights(surface, hfield_surface)
    for count in counts:
        if count >= n_total:
            continue
        if "geometric_farthest" in methods:
            layouts.append(
                LayoutSpec(
                    name=f"geometric_farthest_{count}",
                    method="geometric_farthest",
                    count=count,
                    indices=farthest_point_subset(directions, count),
                    note="Geometry-only farthest-point coverage on the local CST sphere.",
                )
            )
        if "fibonacci_snap" in methods:
            layouts.append(
                LayoutSpec(
                    name=f"fibonacci_snap_{count}",
                    method="fibonacci_snap",
                    count=count,
                    indices=nearest_unique_snap(directions, fibonacci_sphere_directions(count), count),
                    note="Low-discrepancy sphere directions snapped to exported CST probes.",
                )
            )
        if "field_weighted" in methods:
            layouts.append(
                LayoutSpec(
                    name=f"field_weighted_{count}",
                    method="field_weighted",
                    count=count,
                    indices=weighted_farthest_subset(directions, field_weights, count),
                    note="Diagnostic field-energy weighted subset; useful for bounds, not a blind deployment layout.",
                )
            )
    return layouts


def sensor_ids_for_layout(surface: pd.DataFrame, layout: LayoutSpec) -> list[str]:
    values = surface.iloc[layout.indices]["sensor_id"].astype(str).to_list()
    return [str(value) for value in values]


def aggregate_quadrature_weights(surface: pd.DataFrame, layout: LayoutSpec) -> dict[str, float]:
    _, _, directions = local_directions(surface)
    selected_dirs = directions[layout.indices]
    assignments = np.argmax(directions @ selected_dirs.T, axis=1)
    base_weights = surface["weight_m2"].to_numpy(dtype=float)
    selected_ids = sensor_ids_for_layout(surface, layout)
    weights = {sensor_id: 0.0 for sensor_id in selected_ids}
    for sensor_idx, assigned_idx in enumerate(assignments):
        sensor_id = selected_ids[int(assigned_idx)]
        weights[sensor_id] += float(base_weights[sensor_idx])
    return weights


def subset_table(
    table: pd.DataFrame,
    selected_sensor_ids: list[str],
    layout: LayoutSpec,
    quadrature_weights: dict[str, float],
    out_path: Path,
) -> dict[str, float]:
    work = table.copy()
    work["sensor_id"] = work["sensor_id"].astype(str)
    selected = work.loc[work["sensor_id"].isin(set(selected_sensor_ids))].copy()
    if selected.empty:
        raise ValueError(f"layout {layout.name} selected no rows")
    missing_weights = sorted(set(selected_sensor_ids) - set(quadrature_weights))
    if missing_weights:
        raise ValueError(f"layout {layout.name} missing quadrature weights for sensors: {missing_weights}")
    order = {sensor_id: idx for idx, sensor_id in enumerate(selected_sensor_ids)}
    selected["selection_order"] = selected["sensor_id"].map(order).astype(int)
    selected["layout_candidate"] = layout.name
    selected["layout_method"] = layout.method
    selected["layout_sensor_count"] = int(layout.count)
    selected["weighting_model"] = "nearest_full96_cell_aggregation"
    selected["weight_m2"] = selected["sensor_id"].map(quadrature_weights).astype(float)
    selected = selected.sort_values(["selection_order", "polarization"]).reset_index(drop=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    selected.to_csv(out_path, index=False, encoding="utf-8-sig")
    values = np.asarray([quadrature_weights[sensor_id] for sensor_id in selected_sensor_ids], dtype=float)
    return {
        "quadrature_weight_sum_m2": float(np.sum(values)),
        "quadrature_weight_min_m2": float(np.min(values)),
        "quadrature_weight_max_m2": float(np.max(values)),
        "quadrature_weight_std_m2": float(np.std(values)),
    }


def fixed_variant_row(results_path: Path, frozen_variant: str) -> dict[str, Any]:
    results = read_table(results_path)
    match = results.loc[results["variant"].astype(str).eq(frozen_variant)]
    if match.empty:
        return {"frozen_variant": frozen_variant, "frozen_status": "missing"}
    row = match.iloc[0].to_dict()
    return {
        "frozen_variant": frozen_variant,
        "frozen_status": str(row.get("status", "")),
        "frozen_correlation": float(row.get("correlation", math.nan)),
        "frozen_scaled_power_nmse": float(row.get("scaled_power_nmse", math.nan)),
        "frozen_nmse": float(row.get("nmse", math.nan)),
        "frozen_main_lobe_region_error_deg": float(row.get("main_lobe_region_error_deg", math.nan)),
        "frozen_main_lobe_region_jaccard": float(row.get("main_lobe_region_jaccard", math.nan)),
        "frozen_main_lobe_region_capture": float(row.get("main_lobe_region_min_capture", math.nan)),
        "frozen_peak_error_db": float(row.get("peak_error_db", math.nan)),
        "frozen_best_power_scale": float(row.get("best_power_scale", math.nan)),
    }


def layout_summary_row(
    layout: LayoutSpec,
    mode: str,
    surface: pd.DataFrame,
    selected_sensor_ids: list[str],
    weight_stats: dict[str, float],
    summary: dict[str, Any],
    frozen: dict[str, Any],
    case_out_dir: Path,
    reconstruction_degree: int | None = None,
    reconstruction_metrics: dict[str, float] | None = None,
) -> dict[str, Any]:
    best = summary.get("best_setting", {})
    metrics = spatial_metrics(surface, layout.indices)
    frozen_status = str(frozen.get("frozen_status", ""))
    deployable = layout.method in {"full", "geometric_farthest", "fibonacci_snap"}
    row = {
        "layout": layout.name,
        "mode": mode,
        "method": layout.method,
        "sensor_count": int(layout.count),
        "deployable_without_field_prior": bool(deployable),
        "reconstruction_degree": "" if reconstruction_degree is None else int(reconstruction_degree),
        "weighting_model": "nearest_full96_cell_aggregation",
        "selected_sensor_ids": " ".join(selected_sensor_ids),
        "note": layout.note,
        "out_dir": display_path(case_out_dir),
        "best_variant": str(best.get("variant", "")),
        "best_status": str(best.get("status", "")),
        "best_correlation": float(best.get("correlation", math.nan)),
        "best_scaled_power_nmse": float(best.get("scaled_power_nmse", math.nan)),
        "best_nmse": float(best.get("nmse", math.nan)),
        "best_region_error_deg": float(best.get("main_lobe_region_error_deg", math.nan)),
        "best_region_jaccard": float(best.get("main_lobe_region_jaccard", math.nan)),
        "best_region_capture": float(best.get("main_lobe_region_min_capture", math.nan)),
        "frozen_accepted": frozen_status in huygens_gate.ACCEPTED_VECTOR_GATE_STATUSES,
    }
    row.update(metrics)
    row.update(weight_stats)
    if reconstruction_metrics:
        row.update(reconstruction_metrics)
    row.update(frozen)
    return row


def gate_summary(rows: pd.DataFrame, frozen_variant: str) -> dict[str, Any]:
    if rows.empty:
        return {
            "status": "missing",
            "frozen_variant": frozen_variant,
            "layout_count": 0,
            "frozen_accepted_count": 0,
            "deployable_frozen_accepted_count": 0,
        }
    accepted = rows["frozen_accepted"].fillna(False).astype(bool)
    deployable = rows["deployable_without_field_prior"].fillna(False).astype(bool)
    reconstructed_or_full = rows["mode"].astype(str).isin(["poly_reconstruct_full96", "direct_subset_full"])
    deployable_rows = rows.loc[deployable & reconstructed_or_full].copy()
    deployable_accepted = deployable_rows.loc[deployable_rows["frozen_accepted"].fillna(False).astype(bool)]
    smallest_deployable = {}
    if not deployable_accepted.empty:
        smallest = deployable_accepted.sort_values(
            ["sensor_count", "frozen_scaled_power_nmse", "frozen_correlation"],
            ascending=[True, True, False],
        ).iloc[0]
        smallest_deployable = smallest.to_dict()
    status = "diagnostic_only"
    if not deployable_accepted.empty and int(deployable_accepted["sensor_count"].min()) <= 48:
        status = "reduced_layout_validated"
    elif not deployable_accepted.empty:
        status = "reduced_layout_partial"
    elif bool(accepted.any()):
        status = "field_prior_only"
    return {
        "status": status,
        "frozen_variant": frozen_variant,
        "layout_count": int(rows.shape[0]),
        "frozen_accepted_count": int(accepted.sum()),
        "deployable_frozen_accepted_count": int((accepted & deployable & reconstructed_or_full).sum()),
        "direct_subset_frozen_accepted_count": int((accepted & rows["mode"].astype(str).eq("direct_subset")).sum()),
        "reconstructed_frozen_accepted_count": int(
            (accepted & rows["mode"].astype(str).eq("poly_reconstruct_full96")).sum()
        ),
        "smallest_deployable_frozen_pass": smallest_deployable,
        "counts_tested": sorted(int(value) for value in rows["sensor_count"].dropna().unique().tolist()),
        "methods_tested": sorted(str(value) for value in rows["method"].dropna().unique().tolist()),
        "modes_tested": sorted(str(value) for value in rows["mode"].dropna().unique().tolist()),
    }


def write_readme(out_dir: Path, rows: pd.DataFrame, summary: dict[str, Any]) -> None:
    table_rows = []
    for row in rows.sort_values(["sensor_count", "mode", "method"]).itertuples(index=False):
        table_rows.append(
            "| {layout} | {mode} | {method} | {sensor_count} | {frozen_status} | {corr:.4f} | {nmse:.4g} | "
            "{region:.3g} | {jaccard:.4f} | {e_holdout} | {h_holdout} | {accepted} |".format(
                layout=row.layout,
                mode=row.mode,
                method=row.method,
                sensor_count=int(row.sensor_count),
                frozen_status=row.frozen_status,
                corr=float(row.frozen_correlation),
                nmse=float(row.frozen_scaled_power_nmse),
                region=float(row.frozen_main_lobe_region_error_deg),
                jaccard=float(row.frozen_main_lobe_region_jaccard),
                e_holdout=(
                    ""
                    if pd.isna(getattr(row, "e_reconstruction_holdout_nrmse", math.nan))
                    else f"{float(row.e_reconstruction_holdout_nrmse):.3g}"
                ),
                h_holdout=(
                    ""
                    if pd.isna(getattr(row, "h_reconstruction_holdout_nrmse", math.nan))
                    else f"{float(row.h_reconstruction_holdout_nrmse):.3g}"
                ),
                accepted=bool(row.frozen_accepted),
            )
        )
    table = (
        "| Layout | Mode | Method | Sensors | Frozen status | Corr | Scaled NMSE | Region error / deg | Region Jaccard | E holdout NRMSE | H holdout NRMSE | Accepted |\n"
        "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|\n"
        + "\n".join(table_rows)
        + "\n"
    )
    gate = summary["gate"]
    smallest = gate.get("smallest_deployable_frozen_pass", {})
    smallest_text = (
        f"`{smallest.get('layout')}` with `{int(float(smallest.get('sensor_count', 0)))}` sensors"
        if smallest
        else "none"
    )
    content = f"""# CST Mesh-Safe Huygens Reduced Layout Gate

This directory tests whether the validated short-x matched E/H source-family pilot
survives deterministic thinning of the exported 96-point local CST sphere.

The run does not rerun CST. It subsets the already-exported local E/H probe CSVs,
assigns each original 96-point surface cell to the nearest retained probe for
quadrature weighting, and reruns the same Huygens extrapolation gate. The
decision metric is the frozen `{gate['frozen_variant']}` row, not a per-layout
retuned best row.

## Gate

- Status: `{gate['status']}`
- Frozen accepted layouts: `{gate['frozen_accepted_count']}/{gate['layout_count']}`
- Deployable frozen accepted layouts: `{gate['deployable_frozen_accepted_count']}`
- Reconstructed frozen accepted layouts: `{gate['reconstructed_frozen_accepted_count']}`
- Smallest deployable frozen pass: {smallest_text}

## Frozen-Operator Results

{table}
## Interpretation

- `geometric_farthest` and `fibonacci_snap` are deployment-style layouts because
  they use geometry only.
- `field_weighted` is a diagnostic lower-bound layout because it uses measured
  E/H field energy from the full 96-point pilot.
- A pass here supports the sampling-plan claim that the local Huygens surface can
  be sampled sparsely and reconstructed before propagation to the 13 m
  measurement shell, provided the same fixed operator is used on additional
  source orientations.

## Files

| File | Purpose |
|---|---|
| `reduced_layout_summary.csv` | Per-layout frozen and best-row metrics plus aggregated quadrature weights. |
| `reduced_layout_summary.json` | Machine-readable gate summary. |
| `layouts/*_local_efield.csv` | Generated subset E-field inputs. |
| `layouts/*_local_hfield.csv` | Generated subset H-field inputs. |
| `layouts/*_poly_full96_efield.csv` | Polynomially reconstructed full 96-point E-field inputs. |
| `layouts/*_poly_full96_hfield.csv` | Polynomially reconstructed full 96-point H-field inputs. |
| `layouts/*/meshsafe_huygens_extrapolation_results.csv` | Per-layout Huygens variant metrics. |
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts = parse_csv_ints(args.counts)
    methods = parse_methods(args.methods)
    local_efield = Path(args.local_efield)
    local_hfield = Path(args.local_hfield)
    efield_table = read_table(local_efield)
    hfield_table = read_table(local_hfield)
    surface = huygens_gate.load_local_field(local_efield, args.sample_id, float(args.frequency_hz), field_kind="e")
    hfield_surface = huygens_gate.load_local_field(local_hfield, args.sample_id, float(args.frequency_hz), field_kind="h")
    hfield_surface = huygens_gate.align_hfield_surface(surface, hfield_surface)

    rows: list[dict[str, Any]] = []
    for layout in make_layouts(surface, hfield_surface, counts, methods):
        selected_sensor_ids = sensor_ids_for_layout(surface, layout)
        quadrature_weights = aggregate_quadrature_weights(surface, layout)
        direct_dir = out_dir / "layouts" / layout.name / "direct_subset"
        subset_efield = out_dir / "layouts" / f"{layout.name}_local_efield.csv"
        subset_hfield = out_dir / "layouts" / f"{layout.name}_local_hfield.csv"
        weight_stats = subset_table(efield_table, selected_sensor_ids, layout, quadrature_weights, subset_efield)
        subset_table(hfield_table, selected_sensor_ids, layout, quadrature_weights, subset_hfield)
        direct_summary = huygens_gate.run(
            argparse.Namespace(
                local_nearfield=subset_efield,
                local_hfield=subset_hfield,
                disable_hfield=False,
                farfield=Path(args.farfield),
                out_dir=direct_dir,
                sample_id=args.sample_id,
                frequency_hz=float(args.frequency_hz),
                impedance_factors=args.impedance_factors,
                eh_j_scale_factors=args.eh_j_scale_factors,
            )
        )
        direct_frozen = fixed_variant_row(direct_dir / "meshsafe_huygens_extrapolation_results.csv", args.frozen_variant)
        rows.append(
            layout_summary_row(
                layout,
                "direct_subset_full" if layout.count == surface.shape[0] else "direct_subset",
                surface,
                selected_sensor_ids,
                weight_stats,
                direct_summary,
                direct_frozen,
                direct_dir,
            )
        )
        if layout.count < surface.shape[0] and bool(args.reconstruct_full_surface):
            degree = choose_polynomial_degree(layout.count, int(args.max_degree))
            reconstructed_dir = out_dir / "layouts" / layout.name / "poly_reconstruct_full96"
            reconstructed_efield = out_dir / "layouts" / f"{layout.name}_poly_full96_efield.csv"
            reconstructed_hfield = out_dir / "layouts" / f"{layout.name}_poly_full96_hfield.csv"
            reconstructed_e = reconstructed_surface(surface, layout.indices, E_COMPONENTS, degree, float(args.ridge))
            reconstructed_h = reconstructed_surface(hfield_surface, layout.indices, H_COMPONENTS, degree, float(args.ridge))
            reconstruction_metrics = {}
            reconstruction_metrics.update(
                reconstruction_error_metrics(surface, reconstructed_e, E_COMPONENTS, layout.indices, "e")
            )
            reconstruction_metrics.update(
                reconstruction_error_metrics(hfield_surface, reconstructed_h, H_COMPONENTS, layout.indices, "h")
            )
            reconstruction_metrics["reconstruction_basis_size"] = basis_size(degree)
            pivot_to_long_template(
                efield_table,
                reconstructed_e,
                E_COMPONENTS,
                "e_real",
                "e_imag",
                layout,
                selected_sensor_ids,
                "complex_cartesian_polynomial_on_sphere",
                degree,
                reconstructed_efield,
            )
            pivot_to_long_template(
                hfield_table,
                reconstructed_h,
                H_COMPONENTS,
                "h_real",
                "h_imag",
                layout,
                selected_sensor_ids,
                "complex_cartesian_polynomial_on_sphere",
                degree,
                reconstructed_hfield,
            )
            reconstructed_summary = huygens_gate.run(
                argparse.Namespace(
                    local_nearfield=reconstructed_efield,
                    local_hfield=reconstructed_hfield,
                    disable_hfield=False,
                    farfield=Path(args.farfield),
                    out_dir=reconstructed_dir,
                    sample_id=args.sample_id,
                    frequency_hz=float(args.frequency_hz),
                    impedance_factors=args.impedance_factors,
                    eh_j_scale_factors=args.eh_j_scale_factors,
                )
            )
            reconstructed_frozen = fixed_variant_row(
                reconstructed_dir / "meshsafe_huygens_extrapolation_results.csv",
                args.frozen_variant,
            )
            rows.append(
                layout_summary_row(
                    layout,
                    "poly_reconstruct_full96",
                    surface,
                    selected_sensor_ids,
                    {
                        "quadrature_weight_sum_m2": float(surface["weight_m2"].sum()),
                        "quadrature_weight_min_m2": float(surface["weight_m2"].min()),
                        "quadrature_weight_max_m2": float(surface["weight_m2"].max()),
                        "quadrature_weight_std_m2": float(surface["weight_m2"].std()),
                    },
                    reconstructed_summary,
                    reconstructed_frozen,
                    reconstructed_dir,
                    reconstruction_degree=degree,
                    reconstruction_metrics=reconstruction_metrics,
                )
            )

    rows_df = pd.DataFrame(rows)
    rows_df = rows_df.sort_values(
        ["sensor_count", "mode", "deployable_without_field_prior", "method"],
        ascending=[True, True, False, True],
    ).reset_index(drop=True)
    rows_df.to_csv(out_dir / "reduced_layout_summary.csv", index=False, encoding="utf-8-sig")
    summary = {
        "generated_at": now_iso(),
        "generated_by": "code/run_cst_meshsafe_huygens_reduced_layout.py",
        "local_efield": display_path(local_efield),
        "local_hfield": display_path(local_hfield),
        "farfield": display_path(Path(args.farfield)),
        "out_dir": display_path(out_dir),
        "sample_id": args.sample_id,
        "frequency_hz": float(args.frequency_hz),
        "counts_requested": counts,
        "methods_requested": methods,
        "impedance_factors": args.impedance_factors,
        "eh_j_scale_factors": args.eh_j_scale_factors,
        "reconstruct_full_surface": bool(args.reconstruct_full_surface),
        "max_degree": int(args.max_degree),
        "ridge": float(args.ridge),
        "weighting": "each original 96-point local-sphere cell is assigned to the nearest retained probe",
        "gate": gate_summary(rows_df, args.frozen_variant),
    }
    write_json(out_dir / "reduced_layout_summary.json", summary)
    write_readme(out_dir, rows_df, summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run reduced-layout checks for the matched CST local E/H Huygens pilot.")
    parser.add_argument("--local-efield", type=Path, default=DEFAULT_LOCAL_EFIELD)
    parser.add_argument("--local-hfield", type=Path, default=DEFAULT_LOCAL_HFIELD)
    parser.add_argument("--farfield", type=Path, default=DEFAULT_FARFIELD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-id", default="L1_short_dipole_x_1p2G")
    parser.add_argument("--frequency-hz", type=float, default=1.2e9)
    parser.add_argument("--counts", default=",".join(str(value) for value in DEFAULT_COUNTS))
    parser.add_argument("--methods", default=",".join(DEFAULT_METHODS))
    parser.add_argument("--impedance-factors", default="1")
    parser.add_argument("--eh-j-scale-factors", default="96")
    parser.add_argument("--frozen-variant", default=DEFAULT_FROZEN_VARIANT)
    parser.add_argument("--reconstruct-full-surface", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max-degree", type=int, default=5)
    parser.add_argument("--ridge", type=float, default=1e-8)
    return parser.parse_args()


def main() -> None:
    summary = run(parse_args())
    print(
        json.dumps(
            {
                "status": summary["gate"]["status"],
                "out_dir": summary["out_dir"],
                "frozen_variant": summary["gate"]["frozen_variant"],
                "frozen_accepted_count": summary["gate"]["frozen_accepted_count"],
                "layout_count": summary["gate"]["layout_count"],
                "smallest_deployable_frozen_pass": summary["gate"]["smallest_deployable_frozen_pass"].get("layout"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
