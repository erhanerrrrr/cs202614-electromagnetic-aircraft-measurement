from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cst_io import farfield_power_from_table, read_table


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_SOURCES = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_OUT = ROOT / "outputs" / "level1_analytic_reference"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def spherical_basis(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    r_hat = np.column_stack(
        [
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ]
    )
    e_theta = np.column_stack(
        [
            np.cos(theta) * np.cos(phi),
            np.cos(theta) * np.sin(phi),
            -np.sin(theta),
        ]
    )
    e_phi = np.column_stack([-np.sin(phi), np.cos(phi), np.zeros_like(phi)])
    return r_hat, e_theta, e_phi


def normalized_power(power: np.ndarray) -> np.ndarray:
    power = np.asarray(power, dtype=float)
    peak = float(np.nanmax(power)) if len(power) else 0.0
    if not np.isfinite(peak) or peak <= 0:
        return np.zeros_like(power)
    return power / peak


def dipole_amplitude(source_type: str, cos_alpha: np.ndarray) -> np.ndarray:
    cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
    sin_alpha = np.sqrt(np.maximum(1.0 - cos_alpha**2, 0.0))
    if source_type == "halfwave_dipole":
        amp = np.zeros_like(sin_alpha)
        good = sin_alpha > 1e-8
        amp[good] = np.cos(0.5 * np.pi * cos_alpha[good]) / sin_alpha[good]
        return amp
    return sin_alpha


def analytic_farfield_for_case(case: pd.Series, source: pd.Series, theta_deg: np.ndarray, phi_deg: np.ndarray) -> pd.DataFrame:
    theta_grid, phi_grid = np.meshgrid(np.deg2rad(theta_deg), np.deg2rad(phi_deg), indexing="ij")
    theta_flat = theta_grid.ravel()
    phi_flat = phi_grid.ravel()
    r_hat, e_theta, e_phi = spherical_basis(theta_flat, phi_flat)

    axis = np.array(
        [
            float(source["orientation_x"]),
            float(source["orientation_y"]),
            float(source["orientation_z"]),
        ],
        dtype=float,
    )
    axis_norm = np.linalg.norm(axis)
    if axis_norm <= 0:
        raise ValueError(f"invalid orientation for {case['sample_id']}")
    axis = axis / axis_norm

    cos_alpha = r_hat @ axis
    transverse = axis[None, :] - cos_alpha[:, None] * r_hat
    transverse_norm = np.linalg.norm(transverse, axis=1)
    direction = np.zeros_like(transverse)
    good = transverse_norm > 1e-12
    direction[good] = transverse[good] / transverse_norm[good, None]
    amp = dipole_amplitude(str(source["source_type"]), cos_alpha)
    e_cart = direction * amp[:, None]
    e_theta_complex = e_cart[:, 0] * e_theta[:, 0] + e_cart[:, 1] * e_theta[:, 1] + e_cart[:, 2] * e_theta[:, 2]
    e_phi_complex = e_cart[:, 0] * e_phi[:, 0] + e_cart[:, 1] * e_phi[:, 1] + e_cart[:, 2] * e_phi[:, 2]
    power = np.abs(e_theta_complex) ** 2 + np.abs(e_phi_complex) ** 2
    power_norm = normalized_power(power)
    gain_db_norm = 10.0 * np.log10(np.maximum(power_norm, 1e-12))

    return pd.DataFrame(
        {
            "sample_id": str(case["sample_id"]),
            "theta_deg": np.rad2deg(theta_flat),
            "phi_deg": np.rad2deg(phi_flat),
            "frequency_hz": int(case["frequency_hz"]),
            "e_theta_real": np.real(e_theta_complex),
            "e_theta_imag": np.zeros_like(e_theta_complex, dtype=float),
            "e_phi_real": np.real(e_phi_complex),
            "e_phi_imag": np.zeros_like(e_phi_complex, dtype=float),
            "power_norm": power_norm,
            "gain_db_norm": gain_db_norm,
            "source_type": str(source["source_type"]),
            "orientation_axis": str(case["orientation_axis"]),
            "reference_type": "analytic_dipole_pattern",
        }
    )


def angular_separation_deg(theta_a: float, phi_a: float, theta_b: float, phi_b: float) -> float:
    ta, pa, tb, pb = map(np.deg2rad, [theta_a, phi_a, theta_b, phi_b])
    va = np.array([np.sin(ta) * np.cos(pa), np.sin(ta) * np.sin(pa), np.cos(ta)])
    vb = np.array([np.sin(tb) * np.cos(pb), np.sin(tb) * np.sin(pb), np.cos(tb)])
    dot = float(np.clip(va @ vb, -1.0, 1.0))
    return float(np.rad2deg(np.arccos(dot)))


def compare_power(reference: pd.DataFrame, candidate: pd.DataFrame, sample_id: str, frequency_hz: float) -> dict[str, object]:
    theta, phi, power, _ = farfield_power_from_table(candidate, sample_id, frequency_hz)
    cand = pd.DataFrame(
        {
            "theta_key": np.round(np.rad2deg(theta), 10),
            "phi_key": np.round(np.rad2deg(phi), 10),
            "candidate_power_norm": normalized_power(power),
        }
    )
    ref = reference.copy()
    ref["theta_key"] = np.round(ref["theta_deg"].astype(float), 10)
    ref["phi_key"] = np.round(ref["phi_deg"].astype(float), 10)
    merged = ref.merge(cand, on=["theta_key", "phi_key"], how="inner")
    if merged.empty:
        return {
            "sample_id": sample_id,
            "status": "no_common_grid",
            "nmse": "",
            "correlation": "",
            "main_lobe_error_deg": "",
            "common_points": 0,
        }
    ref_power = merged["power_norm"].to_numpy(dtype=float)
    cand_power = merged["candidate_power_norm"].to_numpy(dtype=float)
    diff = cand_power - ref_power
    nmse = float(np.sum(diff**2) / max(np.sum(ref_power**2), 1e-15))
    if np.std(ref_power) <= 1e-15 or np.std(cand_power) <= 1e-15:
        corr = 0.0
    else:
        corr = float(np.corrcoef(ref_power, cand_power)[0, 1])

    ref_peak = merged.iloc[int(np.argmax(ref_power))]
    cand_peak = merged.iloc[int(np.argmax(cand_power))]
    lobe_error = angular_separation_deg(
        float(ref_peak["theta_deg"]),
        float(ref_peak["phi_deg"]),
        float(cand_peak["theta_deg"]),
        float(cand_peak["phi_deg"]),
    )
    return {
        "sample_id": sample_id,
        "status": "compared",
        "nmse": nmse,
        "correlation": corr,
        "main_lobe_error_deg": lobe_error,
        "common_points": int(len(merged)),
    }


def plot_case(reference: pd.DataFrame, out_dir: Path, sample_id: str) -> None:
    pivot = reference.pivot_table(index="theta_deg", columns="phi_deg", values="gain_db_norm", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 4.8), constrained_layout=True)
    mesh = ax.imshow(
        pivot.to_numpy(),
        aspect="auto",
        origin="lower",
        extent=[float(pivot.columns.min()), float(pivot.columns.max()), float(pivot.index.min()), float(pivot.index.max())],
        vmin=-30,
        vmax=0,
        cmap="viridis",
    )
    ax.set_title(f"{sample_id} analytic normalized far-field")
    ax.set_xlabel("phi (deg)")
    ax.set_ylabel("theta (deg)")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("normalized gain (dB)")
    fig.savefig(out_dir / f"{sample_id}_analytic_farfield_heatmap.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.2), constrained_layout=True)
    for phi_cut in [0.0, 90.0, 180.0, 270.0]:
        cut = reference[np.isclose(reference["phi_deg"].astype(float), phi_cut)]
        if not cut.empty:
            ax.plot(cut["theta_deg"], cut["gain_db_norm"], label=f"phi={phi_cut:.0f} deg")
    ax.set_title(f"{sample_id} analytic theta cuts")
    ax.set_xlabel("theta (deg)")
    ax.set_ylabel("normalized gain (dB)")
    ax.set_ylim(-35, 1)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.savefig(out_dir / f"{sample_id}_analytic_theta_cuts.png", dpi=180)
    plt.close(fig)


def summary_rows(reference: pd.DataFrame) -> dict[str, object]:
    idx = int(reference["power_norm"].astype(float).idxmax())
    peak = reference.loc[idx]
    return {
        "sample_id": str(peak["sample_id"]),
        "source_type": str(peak["source_type"]),
        "orientation_axis": str(peak["orientation_axis"]),
        "peak_theta_deg_one_grid_point": float(peak["theta_deg"]),
        "peak_phi_deg_one_grid_point": float(peak["phi_deg"]),
        "peak_gain_db_norm": float(peak["gain_db_norm"]),
        "min_gain_db_norm": float(reference["gain_db_norm"].astype(float).min()),
        "row_count": int(len(reference)),
    }


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    content = f"""# Level 1 analytic reference

This folder contains analytic far-field references for the Level 1 dipole standard-source cases.
It is a physics sanity check for CST exports, not a replacement for real CST evidence.

## Files

| File | Meaning |
|---|---|
| `level1_analytic_farfield_reference.csv` | Analytic upper-hemisphere far-field table for all Level 1 cases. |
| `level1_analytic_reference_summary.csv` | One-row summary per case. |
| `level1_analytic_compare_status.csv` | Comparison status against real CST farfield files if present. |
| `*_analytic_farfield_heatmap.png` | Normalized analytic gain heatmap. |
| `*_analytic_theta_cuts.png` | Theta cuts at phi = 0/90/180/270 deg. |

## Current counts

- Analytic cases: {summary["case_count"]}
- Required analytic cases: {summary["required_case_count"]}
- Far-field rows per case: {summary["rows_per_case"]}
- Real CST comparisons completed: {summary["real_cst_compared_cases"]}

## How to use after CST export

1. Place real CST farfield files under `data/cst_exports/level1`.
2. Run `python code\\build_level1_analytic_reference.py`.
3. Check `level1_analytic_compare_status.csv`.

Pass/fail should still be based on the main Level 1 reconstruction audit. This analytic reference only helps catch axis, phase, polarization, and gross pattern mistakes early.
"""
    (out_dir / "README_level1_analytic_reference.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build analytic far-field references for Level 1 standard dipole cases.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--sources", default=str(DEFAULT_SOURCES))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--theta-min", type=float, default=2.0)
    parser.add_argument("--theta-max", type=float, default=88.0)
    parser.add_argument("--theta-count", type=int, default=37)
    parser.add_argument("--phi-step", type=float, default=5.0)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cases = read_table(args.cases)
    sources = read_table(args.sources).set_index("sample_id")
    theta_deg = np.linspace(args.theta_min, args.theta_max, args.theta_count)
    phi_deg = np.arange(0.0, 360.0, args.phi_step)

    reference_tables: list[pd.DataFrame] = []
    summary: list[dict[str, object]] = []
    compare_rows: list[dict[str, object]] = []
    for case in cases.itertuples(index=False):
        case_series = pd.Series(case._asdict())
        sample_id = str(case_series["sample_id"])
        source = sources.loc[sample_id]
        ref = analytic_farfield_for_case(case_series, source, theta_deg, phi_deg)
        reference_tables.append(ref)
        summary.append(summary_rows(ref))
        plot_case(ref, out_dir, sample_id)

        farfield_path = ROOT / str(case_series["farfield_export"])
        if farfield_path.exists():
            try:
                candidate = read_table(farfield_path)
                compare_rows.append(compare_power(ref, candidate, sample_id, float(case_series["frequency_hz"])))
            except Exception as exc:  # keep dashboard generation alive and expose the issue
                compare_rows.append(
                    {
                        "sample_id": sample_id,
                        "status": "compare_error",
                        "nmse": "",
                        "correlation": "",
                        "main_lobe_error_deg": "",
                        "common_points": 0,
                        "error": str(exc),
                    }
                )
        else:
            compare_rows.append(
                {
                    "sample_id": sample_id,
                    "status": "missing_real_cst_farfield",
                    "nmse": "",
                    "correlation": "",
                    "main_lobe_error_deg": "",
                    "common_points": 0,
                    "error": "",
                }
            )

    reference = pd.concat(reference_tables, ignore_index=True)
    summary_df = pd.DataFrame(summary)
    compare_df = pd.DataFrame(compare_rows)
    reference.to_csv(out_dir / "level1_analytic_farfield_reference.csv", index=False, encoding="utf-8-sig")
    summary_df.to_csv(out_dir / "level1_analytic_reference_summary.csv", index=False, encoding="utf-8-sig")
    compare_df.to_csv(out_dir / "level1_analytic_compare_status.csv", index=False, encoding="utf-8-sig")

    payload = {
        "case_count": int(len(cases)),
        "required_case_count": int(cases["priority"].astype(str).eq("required").sum()),
        "rows_per_case": int(len(theta_deg) * len(phi_deg)),
        "theta_min_deg": float(theta_deg.min()),
        "theta_max_deg": float(theta_deg.max()),
        "theta_count": int(len(theta_deg)),
        "phi_step_deg": float(args.phi_step),
        "phi_count": int(len(phi_deg)),
        "real_cst_compared_cases": int(compare_df["status"].astype(str).eq("compared").sum()),
        "is_cst_evidence": False,
        "output_dir": rel(out_dir),
    }
    (out_dir / "level1_analytic_reference_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, payload)
    print(f"Level 1 analytic reference written to {out_dir}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
