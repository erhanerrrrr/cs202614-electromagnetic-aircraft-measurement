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
from em_core import spherical_basis
from run_cst_meshsafe_huygens_extrapolation import (
    ACCEPTED_VECTOR_GATE_STATUSES,
    DEFAULT_CASE_CSV,
    DEFAULT_FARFIELD,
    ETA0,
    align_hfield_surface,
    combined_pattern_metrics,
    equivalent_currents,
    farfield_from_currents,
    field_quality,
    infer_hfield_path,
    load_local_field,
    scaled_power_nmse,
    acceptance_status,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_rotation_covariance"


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


def json_scalar(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def rotation_matrix(axis: tuple[float, float, float], angle_deg: float) -> np.ndarray:
    axis_arr = np.asarray(axis, dtype=float)
    norm = float(np.linalg.norm(axis_arr))
    if norm <= 0.0:
        raise ValueError("rotation axis must be non-zero")
    x, y, z = axis_arr / norm
    angle = math.radians(float(angle_deg))
    c = math.cos(angle)
    s = math.sin(angle)
    one_c = 1.0 - c
    return np.array(
        [
            [c + x * x * one_c, x * y * one_c - z * s, x * z * one_c + y * s],
            [y * x * one_c + z * s, c + y * y * one_c, y * z * one_c - x * s],
            [z * x * one_c - y * s, z * y * one_c + x * s, c + z * z * one_c],
        ],
        dtype=float,
    )


def default_rotations() -> dict[str, np.ndarray]:
    rz45 = rotation_matrix((0.0, 0.0, 1.0), 45.0)
    ry30 = rotation_matrix((0.0, 1.0, 0.0), 30.0)
    return {
        "identity": np.eye(3, dtype=float),
        "yaw_z_45": rz45,
        "yaw_z_90": rotation_matrix((0.0, 0.0, 1.0), 90.0),
        "yaw_z_180": rotation_matrix((0.0, 0.0, 1.0), 180.0),
        "pitch_y_30": ry30,
        "pitch_y_60": rotation_matrix((0.0, 1.0, 0.0), 60.0),
        "roll_x_45": rotation_matrix((1.0, 0.0, 0.0), 45.0),
        "roll_x_90": rotation_matrix((1.0, 0.0, 0.0), 90.0),
        "compound_z45_y30": ry30 @ rz45,
    }


def selected_rotations(value: str) -> dict[str, np.ndarray]:
    rotations = default_rotations()
    selected = [item.strip() for item in value.split(",") if item.strip()]
    if not selected:
        return rotations
    missing = sorted(set(selected) - set(rotations))
    if missing:
        raise ValueError(f"unknown rotations: {missing}; available: {sorted(rotations)}")
    return {name: rotations[name] for name in selected}


def rotate_vectors(vectors: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    return np.asarray(vectors) @ matrix.T


def rotate_arrays(arrays: dict[str, np.ndarray], matrix: np.ndarray, center: np.ndarray) -> dict[str, np.ndarray]:
    rotated: dict[str, np.ndarray] = {
        "positions": center[None, :] + rotate_vectors(arrays["positions"] - center[None, :], matrix),
        "normals": rotate_vectors(arrays["normals"], matrix),
        "weights": arrays["weights"].copy(),
        "tangential": rotate_vectors(arrays["tangential"], matrix),
    }
    if "h_tangential" in arrays:
        rotated["h_tangential"] = rotate_vectors(arrays["h_tangential"], matrix)
    return rotated


def directions_to_angles(directions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    unit = np.asarray(directions, dtype=float)
    norms = np.linalg.norm(unit, axis=1)
    unit = unit / np.maximum(norms[:, None], 1e-15)
    theta = np.arccos(np.clip(unit[:, 2], -1.0, 1.0))
    phi = np.mod(np.arctan2(unit[:, 1], unit[:, 0]), 2.0 * np.pi)
    return theta, phi


def fixed_variant_label(variant_family: str, j_scale: float) -> str:
    if math.isclose(j_scale, 1.0, rel_tol=1e-9, abs_tol=1e-12):
        return variant_family
    text = f"{j_scale:.6g}".replace("-", "m").replace(".", "p")
    return f"{variant_family}_j{text}"


def covariance_status(row: dict[str, Any]) -> str:
    corr = float(row["correlation"])
    nmse = float(row["nmse"])
    scaled_nmse = float(row["scaled_power_nmse"])
    lobe = float(row["main_lobe_error_deg"])
    region_error = float(row.get("main_lobe_region_error_deg", lobe))
    if corr >= 0.999999 and nmse <= 1e-10 and scaled_nmse <= 1e-10 and region_error <= 1e-5:
        return "rotation_covariance_strict_pass"
    if corr >= 0.9999 and nmse <= 1e-6 and scaled_nmse <= 1e-6 and region_error <= 1e-3:
        return "rotation_covariance_pass"
    if corr >= 0.999 and scaled_nmse <= 1e-4:
        return "rotation_covariance_near"
    return "rotation_covariance_diagnostic"


def max_normalized_abs_error(reference_power: np.ndarray, predicted_power: np.ndarray) -> float:
    ref_norm = reference_power / max(float(np.max(reference_power)), 1e-30)
    pred_norm = predicted_power / max(float(np.max(predicted_power)), 1e-30)
    return float(np.max(np.abs(ref_norm - pred_norm)))


def load_case(
    case: dict[str, Any],
    farfield: pd.DataFrame,
    variant_family: str,
    j_scale: float,
) -> tuple[dict[str, Any], dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    sample_id = str(case.get("sample_id", "")).strip()
    frequency_hz = float(case.get("frequency_hz"))
    nearfield_path = resolve_path(str(case.get("nearfield_export", "")))
    hfield_path = infer_hfield_path(nearfield_path)
    if not nearfield_path.exists():
        raise FileNotFoundError(f"missing local E-field export: {nearfield_path}")
    if not hfield_path.exists():
        raise FileNotFoundError(f"missing local H-field export: {hfield_path}")

    local_field = load_local_field(nearfield_path, sample_id, frequency_hz, field_kind="e")
    hfield_surface = load_local_field(hfield_path, sample_id, frequency_hz, field_kind="h")
    hfield_surface = align_hfield_surface(local_field, hfield_surface)
    quality, arrays = field_quality(local_field, hfield_surface)
    theta, phi, true_power, farfield_shape = farfield_power_from_table(farfield, sample_id, frequency_hz)

    electric_current, magnetic_current, magnetic_sign, model_note = equivalent_currents(
        arrays,
        variant_family,
        ETA0,
        j_scale,
    )
    predicted_power, predicted_e_theta, predicted_e_phi = farfield_from_currents(
        arrays["positions"],
        arrays["weights"],
        electric_current,
        magnetic_current,
        theta,
        phi,
        frequency_hz,
        magnetic_sign,
    )
    metrics = combined_pattern_metrics(true_power, predicted_power, theta, phi)
    scale, scaled_nmse = scaled_power_nmse(true_power, predicted_power)
    base_row: dict[str, Any] = {
        "sample_id": sample_id,
        "frequency_hz": frequency_hz,
        "variant": fixed_variant_label(variant_family, j_scale),
        "variant_family": variant_family,
        "hfield_j_scale": float(j_scale),
        "reference_type": "real_cst_farfield",
        "rotation": "identity",
        "sensor_count": int(quality["sensor_count"]),
        "farfield_points": int(theta.size),
        "farfield_shape": "" if farfield_shape is None else f"{farfield_shape[0]}x{farfield_shape[1]}",
        "local_nearfield": display_path(nearfield_path),
        "local_hfield": display_path(hfield_path),
        "model_note": model_note,
        "best_power_scale": scale,
        "scaled_power_nmse": scaled_nmse,
        "max_normalized_abs_error": max_normalized_abs_error(true_power, predicted_power),
    }
    base_row.update(metrics)
    base_row["status"] = acceptance_status(base_row)

    arrays = dict(arrays)
    arrays["fixed_electric_current"] = electric_current
    arrays["fixed_magnetic_current"] = magnetic_current
    arrays["fixed_magnetic_sign"] = np.array([magnetic_sign], dtype=float)
    arrays["fixed_predicted_power"] = predicted_power
    arrays["fixed_predicted_e_theta"] = predicted_e_theta
    arrays["fixed_predicted_e_phi"] = predicted_e_phi
    return base_row, arrays, theta, phi, true_power, np.asarray(
        [
            float(quality["center_x_m"]),
            float(quality["center_y_m"]),
            float(quality["center_z_m"]),
        ],
        dtype=float,
    )


def evaluate_rotation(
    sample_id: str,
    frequency_hz: float,
    arrays: dict[str, np.ndarray],
    theta: np.ndarray,
    phi: np.ndarray,
    center: np.ndarray,
    rotation_name: str,
    matrix: np.ndarray,
    variant_family: str,
    j_scale: float,
) -> dict[str, Any]:
    r_hat, _, _ = spherical_basis(theta, phi)
    inverse_directions = r_hat @ matrix
    ref_theta, ref_phi = directions_to_angles(inverse_directions)
    magnetic_sign = float(arrays["fixed_magnetic_sign"][0])
    reference_power, _, _ = farfield_from_currents(
        arrays["positions"],
        arrays["weights"],
        arrays["fixed_electric_current"],
        arrays["fixed_magnetic_current"],
        ref_theta,
        ref_phi,
        frequency_hz,
        magnetic_sign,
    )

    rotated_arrays = rotate_arrays(arrays, matrix, center)
    electric_current, magnetic_current, rotated_magnetic_sign, model_note = equivalent_currents(
        rotated_arrays,
        variant_family,
        ETA0,
        j_scale,
    )
    predicted_power, _, _ = farfield_from_currents(
        rotated_arrays["positions"],
        rotated_arrays["weights"],
        electric_current,
        magnetic_current,
        theta,
        phi,
        frequency_hz,
        rotated_magnetic_sign,
    )
    metrics = combined_pattern_metrics(reference_power, predicted_power, theta, phi)
    scale, scaled_nmse = scaled_power_nmse(reference_power, predicted_power)
    row: dict[str, Any] = {
        "sample_id": sample_id,
        "frequency_hz": frequency_hz,
        "variant": fixed_variant_label(variant_family, j_scale),
        "variant_family": variant_family,
        "hfield_j_scale": float(j_scale),
        "reference_type": "operator_rotation_covariance",
        "rotation": rotation_name,
        "sensor_count": int(arrays["positions"].shape[0]),
        "farfield_points": int(theta.size),
        "best_power_scale": scale,
        "scaled_power_nmse": scaled_nmse,
        "max_normalized_abs_error": max_normalized_abs_error(reference_power, predicted_power),
        "model_note": model_note,
    }
    row.update(metrics)
    row["status"] = covariance_status(row)
    return row


def summarize(base_rows: pd.DataFrame, covariance_rows: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    if covariance_rows.empty:
        status = "missing"
        strict_count = 0
        pass_count = 0
        near_count = 0
    else:
        strict_count = int(covariance_rows["status"].eq("rotation_covariance_strict_pass").sum())
        pass_count = int(covariance_rows["status"].isin(["rotation_covariance_strict_pass", "rotation_covariance_pass"]).sum())
        near_count = int(
            covariance_rows["status"]
            .isin(["rotation_covariance_strict_pass", "rotation_covariance_pass", "rotation_covariance_near"])
            .sum()
        )
        if strict_count == int(covariance_rows.shape[0]):
            status = "rotation_covariance_strict_pass"
        elif pass_count == int(covariance_rows.shape[0]):
            status = "rotation_covariance_pass"
        elif near_count == int(covariance_rows.shape[0]):
            status = "rotation_covariance_near"
        else:
            status = "rotation_covariance_diagnostic"

    base_accepted = 0
    if not base_rows.empty:
        base_accepted = int(base_rows["status"].isin(ACCEPTED_VECTOR_GATE_STATUSES).sum())
    summary = {
        "generated_at": now_iso(),
        "generated_by": "code/run_cst_huygens_rotation_covariance.py",
        "case_csv": display_path(resolve_path(args.case_csv)),
        "farfield": display_path(resolve_path(args.farfield)),
        "out_dir": display_path(out_dir),
        "variant_family": str(args.variant_family),
        "hfield_j_scale": float(args.j_scale),
        "variant": fixed_variant_label(str(args.variant_family), float(args.j_scale)),
        "status": status,
        "base_case_count": int(base_rows.shape[0]),
        "base_real_cst_accepted_count": base_accepted,
        "rotation_count": int(covariance_rows["rotation"].nunique()) if not covariance_rows.empty else 0,
        "covariance_test_count": int(covariance_rows.shape[0]),
        "covariance_strict_count": strict_count,
        "covariance_pass_count": pass_count,
        "covariance_near_count": near_count,
        "min_covariance_correlation": float(covariance_rows["correlation"].min()) if not covariance_rows.empty else math.nan,
        "max_covariance_nmse": float(covariance_rows["nmse"].max()) if not covariance_rows.empty else math.nan,
        "max_covariance_scaled_power_nmse": float(covariance_rows["scaled_power_nmse"].max()) if not covariance_rows.empty else math.nan,
        "max_covariance_main_lobe_error_deg": float(covariance_rows["main_lobe_error_deg"].max())
        if not covariance_rows.empty
        else math.nan,
        "max_covariance_region_error_deg": float(covariance_rows["main_lobe_region_error_deg"].max())
        if not covariance_rows.empty
        else math.nan,
        "max_covariance_normalized_abs_error": float(covariance_rows["max_normalized_abs_error"].max())
        if not covariance_rows.empty
        else math.nan,
        "min_base_real_cst_correlation": float(base_rows["correlation"].min()) if not base_rows.empty else math.nan,
        "max_base_real_cst_scaled_power_nmse": float(base_rows["scaled_power_nmse"].max()) if not base_rows.empty else math.nan,
        "max_base_real_cst_region_error_deg": float(base_rows["main_lobe_region_error_deg"].max()) if not base_rows.empty else math.nan,
        "interpretation": (
            "The frozen real E/H Huygens rule is checked under rigid rotations of the measured CST local "
            "E/H surface fields. The comparison reference is the unrotated Huygens prediction evaluated "
            "at inverse-rotated far-field directions, so this gate proves coordinate covariance of the "
            "operator implementation. It is not a replacement for real CST x/y/off-axis source exports."
        ),
        "output_files": {
            "summary_json": display_path(out_dir / "huygens_rotation_covariance_summary.json"),
            "base_cst_agreement": display_path(out_dir / "huygens_rotation_base_cst_agreement.csv"),
            "covariance_cases": display_path(out_dir / "huygens_rotation_covariance_cases.csv"),
            "readme": display_path(out_dir / "README.md"),
        },
    }
    return {key: json_scalar(value) for key, value in summary.items()}


def write_readme(out_dir: Path, summary: dict[str, Any], rotations: list[str]) -> None:
    content = f"""# CST Huygens rotation covariance gate

This folder records a coordinate-covariance stress test for the frozen real E/H
mesh-safe Huygens rule.

## Scope

- Frozen rule: `{summary['variant']}`
- Real CST base cases: `{summary['base_case_count']}`
- Rotations per case: `{summary['rotation_count']}`
- Covariance tests: `{summary['covariance_test_count']}`
- Status: `{summary['status']}`

The test rotates the measured local CST E/H surface fields and the local
Huygens sphere geometry, then compares the rotated prediction against the
unrotated prediction evaluated at inverse-rotated far-field directions. This
checks whether the Python Huygens operator is tied to a physical vector rule
rather than an accidental global coordinate convention.

## Rotations

`{', '.join(rotations)}`

## Results

- Covariance strict count: `{summary['covariance_strict_count']}/{summary['covariance_test_count']}`
- Covariance pass count: `{summary['covariance_pass_count']}/{summary['covariance_test_count']}`
- Minimum covariance correlation: `{summary['min_covariance_correlation']:.12g}`
- Maximum covariance scaled power NMSE: `{summary['max_covariance_scaled_power_nmse']:.12g}`
- Maximum covariance normalized absolute error: `{summary['max_covariance_normalized_abs_error']:.12g}`
- Base real-CST accepted cases: `{summary['base_real_cst_accepted_count']}/{summary['base_case_count']}`

## Files

| File | Meaning |
|---|---|
| `huygens_rotation_base_cst_agreement.csv` | Fixed-rule agreement against real CST far-field references before synthetic rotations. |
| `huygens_rotation_covariance_cases.csv` | Per-case/per-rotation covariance rows. |
| `huygens_rotation_covariance_summary.json` | Machine-readable summary for the G3 dashboard. |

## Reading

This is operator evidence, not new CST source-family evidence. A pass means the
frozen sign/J-scale rule behaves consistently when the measured vector fields
and surface geometry are rigidly rotated. The next proof step is still to run
or ingest real CST source-family exports, such as x/y-oriented, tilted,
off-axis, or multi-source Level 1 cases.

## Regenerate

```powershell
python code\\run_cst_huygens_rotation_covariance.py
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = resolve_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case_table = read_table(resolve_path(args.case_csv))
    farfield = read_table(resolve_path(args.farfield))
    rotations = selected_rotations(args.rotations)
    selected_ids = {item.strip() for item in str(args.sample_ids).split(",") if item.strip()}

    base_rows: list[dict[str, Any]] = []
    covariance_rows: list[dict[str, Any]] = []
    skipped_rows: list[dict[str, Any]] = []
    for case in case_table.to_dict(orient="records"):
        sample_id = str(case.get("sample_id", "")).strip()
        if selected_ids and sample_id not in selected_ids:
            continue
        try:
            base_row, arrays, theta, phi, _true_power, center = load_case(
                case,
                farfield,
                str(args.variant_family),
                float(args.j_scale),
            )
            base_rows.append(base_row)
            for rotation_name, matrix in rotations.items():
                covariance_rows.append(
                    evaluate_rotation(
                        sample_id,
                        float(case.get("frequency_hz")),
                        arrays,
                        theta,
                        phi,
                        center,
                        rotation_name,
                        matrix,
                        str(args.variant_family),
                        float(args.j_scale),
                    )
                )
        except Exception as exc:  # noqa: BLE001 - batch diagnostics should report every case.
            skipped_rows.append(
                {
                    "sample_id": sample_id,
                    "status": "failed",
                    "error": repr(exc),
                }
            )

    base_df = pd.DataFrame(base_rows)
    covariance_df = pd.DataFrame(covariance_rows)
    skipped_df = pd.DataFrame(skipped_rows)
    base_df.to_csv(out_dir / "huygens_rotation_base_cst_agreement.csv", index=False, encoding="utf-8-sig")
    covariance_df.to_csv(out_dir / "huygens_rotation_covariance_cases.csv", index=False, encoding="utf-8-sig")
    skipped_df.to_csv(out_dir / "huygens_rotation_covariance_skipped_cases.csv", index=False, encoding="utf-8-sig")
    summary = summarize(base_df, covariance_df, out_dir, args)
    summary["skipped_case_count"] = int(skipped_df.shape[0])
    summary["skipped_cases"] = [json_scalar(item) for item in skipped_df.to_dict(orient="records")]
    write_json(out_dir / "huygens_rotation_covariance_summary.json", summary)
    write_readme(out_dir, summary, list(rotations))
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check rotation covariance of the frozen real E/H CST Huygens operator."
    )
    parser.add_argument("--case-csv", type=Path, default=DEFAULT_CASE_CSV)
    parser.add_argument("--farfield", type=Path, default=DEFAULT_FARFIELD)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--variant-family", default="eh_love_equivalence_minus")
    parser.add_argument("--j-scale", type=float, default=96.0)
    parser.add_argument(
        "--rotations",
        default="",
        help="Comma-separated subset of default rotations. Empty means all rotations.",
    )
    parser.add_argument("--sample-ids", default="", help="Optional comma-separated subset of sample_id values.")
    return parser.parse_args()


def main() -> int:
    summary = run(parse_args())
    print(f"CST Huygens rotation covariance gate written to {summary['out_dir']}")
    print(
        f"status={summary['status']}; "
        f"strict={summary['covariance_strict_count']}/{summary['covariance_test_count']}; "
        f"base_accepted={summary['base_real_cst_accepted_count']}/{summary['base_case_count']}"
    )
    return 0 if str(summary["status"]).endswith("_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
