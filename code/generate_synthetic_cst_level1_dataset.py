from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from em_core import SourceSet, add_complex_noise, cartesian_field_response, farfield_grid, farfield_pattern, make_hemisphere_layout


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_OUT = ROOT / "outputs" / "synthetic_cst_level1_dataset"


@dataclass(frozen=True)
class SyntheticLevel1Config:
    nearfield_snr_db: float
    seed: int
    n_theta_farfield: int
    n_phi_farfield: int
    layout_radius_m: float
    warning: str


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, encoding="utf-8-sig")


def axis_vector(axis: str) -> np.ndarray:
    axis = axis.strip().lower()
    vectors = {
        "x": np.array([1.0, 0.0, 0.0]),
        "y": np.array([0.0, 1.0, 0.0]),
        "z": np.array([0.0, 0.0, 1.0]),
    }
    if axis not in vectors:
        raise ValueError(f"unsupported orientation_axis: {axis}")
    return vectors[axis]


def source_from_manifest(case_row: pd.Series, source_row: pd.Series) -> SourceSet:
    axis = axis_vector(str(case_row["orientation_axis"]))
    center = np.array(
        [
            float(source_row["center_x_m"]),
            float(source_row["center_y_m"]),
            float(source_row["center_z_m"]),
        ]
    )
    source_type = str(case_row["source_type"])
    length_m = float(source_row["length_m"])
    if source_type == "halfwave_dipole":
        amplitude = 1.25
        phase = np.deg2rad(10.0)
        # Keep the surrogate reconstruction-friendly while still recording the physical length.
        positions = center[None, :]
    else:
        amplitude = 1.0
        phase = 0.0
        positions = center[None, :]

    cross_pol = np.roll(axis, 1) * (0.025 + 0.015j)
    moment = amplitude * np.exp(1j * phase) * axis.astype(np.complex128) + cross_pol
    # A tiny length-dependent phase makes the two standard-source types non-identical
    # without pretending to be a full-wave dipole model.
    moment = moment * np.exp(1j * 0.15 * length_m)
    return SourceSet(
        positions=positions,
        moments=moment[None, :],
        label=str(case_row["source_config"]),
    )


def build_nearfield_rows(
    layout,
    source: SourceSet,
    case_row: pd.Series,
    frequency_hz: float,
    snr_db: float,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    sample_id = str(case_row["sample_id"])
    field = cartesian_field_response(layout.positions, source, frequency_hz)
    if np.isfinite(snr_db):
        field = add_complex_noise(field, snr_db, rng)

    rows: list[dict[str, object]] = []
    for sensor_id, position in enumerate(layout.positions):
        for component_idx, polarization in enumerate(("Ex", "Ey", "Ez")):
            value = field[sensor_id, component_idx]
            rows.append(
                {
                    "sample_id": sample_id,
                    "sensor_id": sensor_id,
                    "x_m": float(position[0]),
                    "y_m": float(position[1]),
                    "z_m": float(position[2]),
                    "theta_deg": float(np.rad2deg(layout.theta[sensor_id])),
                    "phi_deg": float(np.rad2deg(layout.phi[sensor_id])),
                    "frequency_hz": int(round(frequency_hz)),
                    "polarization": polarization,
                    "e_real": float(np.real(value)),
                    "e_imag": float(np.imag(value)),
                    "source_config": str(case_row["source_config"]),
                    "carrier_model": "synthetic_level1_standard_source",
                    "working_state": "single_source_on",
                    "cst_project": "synthetic_not_cst.cst",
                    "monitor_name": str(case_row["nearfield_monitor"]),
                }
            )
    return rows


def build_farfield_rows(source: SourceSet, case_row: pd.Series, frequency_hz: float, theta: np.ndarray, phi: np.ndarray) -> list[dict[str, object]]:
    sample_id = str(case_row["sample_id"])
    power, e_theta, e_phi = farfield_pattern(source, theta, phi, frequency_hz)
    gain_db = 10.0 * np.log10(power / np.maximum(np.max(power), 1e-15) + 1e-12)
    rows: list[dict[str, object]] = []
    for idx in range(theta.size):
        rows.append(
            {
                "sample_id": sample_id,
                "theta_deg": float(np.rad2deg(theta[idx])),
                "phi_deg": float(np.rad2deg(phi[idx])),
                "frequency_hz": int(round(frequency_hz)),
                "e_theta_real": float(np.real(e_theta[idx])),
                "e_theta_imag": float(np.imag(e_theta[idx])),
                "e_phi_real": float(np.real(e_phi[idx])),
                "e_phi_imag": float(np.imag(e_phi[idx])),
                "gain_db": float(gain_db[idx]),
                "source_config": str(case_row["source_config"]),
                "carrier_model": "synthetic_level1_standard_source",
                "working_state": "single_source_on",
                "cst_project": "synthetic_not_cst.cst",
                "monitor_name": str(case_row["farfield_monitor"]),
            }
        )
    return rows


def synthetic_export_path(out_dir: Path, sample_id: str, suffix: str) -> Path:
    return out_dir / "exports" / f"{sample_id}_{suffix}.csv"


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def write_metadata(out_dir: Path, config: SyntheticLevel1Config, manifest: pd.DataFrame) -> None:
    metadata = {
        "contest": "CS-202614",
        "stage": "G2_synthetic_Level1_manifest_shaped_dataset",
        "warning": config.warning,
        "config": asdict(config),
        "case_count": int(len(manifest)),
        "required_cases": manifest.loc[manifest["priority"].eq("required"), "sample_id"].astype(str).tolist(),
        "output_files": {
            "manifest": "level1_case_manifest.csv",
            "exports": "exports/<sample_id>_nearfield.csv and exports/<sample_id>_farfield.csv",
        },
        "usage": {
            "audit": "python code\\merge_cst_level1_exports.py --manifest outputs\\synthetic_cst_level1_dataset\\level1_case_manifest.csv --report-dir outputs\\synthetic_cst_level1_dataset\\merge_report --out-dir outputs\\synthetic_cst_level1_dataset\\merged",
            "batch_reconstruct": "python code\\run_cst_level1_batch_reconstruction.py --case-status outputs\\synthetic_cst_level1_dataset\\merge_report\\level1_case_status.csv --out-root outputs\\synthetic_cst_level1_dataset\\reconstruction --batch-dir outputs\\synthetic_cst_level1_dataset\\reconstruction_batch --priority all",
        },
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate manifest-shaped synthetic CST Level 1 standard-source exports.")
    parser.add_argument("--case-manifest", default=str(DEFAULT_CASE_MANIFEST), help="Path to level1_case_manifest.csv.")
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST), help="Path to level1_source_manifest.csv.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--nearfield-snr-db", type=float, default=60.0, help="Synthetic near-field SNR. Use inf for no noise.")
    parser.add_argument("--seed", type=int, default=20261401, help="Random seed.")
    parser.add_argument("--n-theta-farfield", type=int, default=37, help="Far-field theta grid count.")
    parser.add_argument("--n-phi-farfield", type=int, default=72, help="Far-field phi grid count.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    export_dir = out_dir / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    case_manifest = read_table(Path(args.case_manifest))
    source_manifest = read_table(Path(args.source_manifest))
    source_manifest = source_manifest.set_index(source_manifest["sample_id"].astype(str))
    layout = make_hemisphere_layout(n_theta=9, n_phi=18, radius_m=13.0)
    theta_ff, phi_ff, _ = farfield_grid(n_theta=args.n_theta_farfield, n_phi=args.n_phi_farfield)
    rng = np.random.default_rng(args.seed)

    manifest_out = case_manifest.copy()
    row_counts: list[dict[str, object]] = []
    for idx, case_row in case_manifest.iterrows():
        sample_id = str(case_row["sample_id"])
        if sample_id not in source_manifest.index:
            raise ValueError(f"source manifest missing sample_id={sample_id}")
        frequency_hz = float(case_row["frequency_hz"])
        source = source_from_manifest(case_row, source_manifest.loc[sample_id])
        nearfield_rows = build_nearfield_rows(layout, source, case_row, frequency_hz, args.nearfield_snr_db, rng)
        farfield_rows = build_farfield_rows(source, case_row, frequency_hz, theta_ff, phi_ff)

        nearfield_path = synthetic_export_path(out_dir, sample_id, "nearfield")
        farfield_path = synthetic_export_path(out_dir, sample_id, "farfield")
        pd.DataFrame(nearfield_rows).to_csv(nearfield_path, index=False, encoding="utf-8-sig")
        pd.DataFrame(farfield_rows).to_csv(farfield_path, index=False, encoding="utf-8-sig")

        manifest_out.loc[idx, "nearfield_export"] = rel(nearfield_path)
        manifest_out.loc[idx, "farfield_export"] = rel(farfield_path)
        manifest_out.loc[idx, "phase_format_nearfield_export"] = ""
        manifest_out.loc[idx, "phase_format_farfield_export"] = ""
        manifest_out.loc[idx, "expected_nearfield_rows"] = len(nearfield_rows)
        manifest_out.loc[idx, "expected_farfield_rows"] = len(farfield_rows)
        manifest_out.loc[idx, "status"] = "synthetic_generated"
        row_counts.append(
            {
                "sample_id": sample_id,
                "nearfield_rows": len(nearfield_rows),
                "farfield_rows": len(farfield_rows),
            }
        )

    manifest_out.to_csv(out_dir / "level1_case_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(row_counts).to_csv(out_dir / "synthetic_row_counts.csv", index=False, encoding="utf-8-sig")
    config = SyntheticLevel1Config(
        nearfield_snr_db=float(args.nearfield_snr_db),
        seed=int(args.seed),
        n_theta_farfield=int(args.n_theta_farfield),
        n_phi_farfield=int(args.n_phi_farfield),
        layout_radius_m=float(layout.radius_m),
        warning="Synthetic surrogate data validates the Level 1 CST-format pipeline only; it is not CST full-wave evidence.",
    )
    write_metadata(out_dir, config, manifest_out)

    print(f"Synthetic Level 1 CST-format dataset written to {out_dir}")
    print(f"cases: {len(manifest_out)}")
    print(f"nearfield rows total: {int(sum(row['nearfield_rows'] for row in row_counts))}")
    print(f"farfield rows total: {int(sum(row['farfield_rows'] for row in row_counts))}")


if __name__ == "__main__":
    main()
