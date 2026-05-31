from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from em_core import (
    SourceSet,
    add_complex_noise,
    cartesian_field_response,
    class_templates,
    farfield_grid,
    farfield_pattern,
    jitter_sources,
    make_equivalent_grid,
    make_hemisphere_layout,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "synthetic_cst_dataset"
DEFAULT_FREQUENCIES_HZ = np.array([0.90e9, 1.05e9, 1.20e9, 1.35e9, 1.50e9])


@dataclass(frozen=True)
class DatasetConfig:
    samples_per_class: int
    nearfield_snr_db: float
    seed: int
    n_theta_farfield: int
    n_phi_farfield: int
    layout_radius_m: float
    synthetic_note: str


def spectral_profile(label: str, frequency_hz: float) -> complex:
    freq_ghz = frequency_hz / 1e9
    phase_x = (freq_ghz - 1.2) / 0.3
    if label == "comm_pair":
        amp = 0.92 + 0.22 * np.cos(2.0 * np.pi * (freq_ghz - 0.9) / 0.6)
        phase = 0.25 * phase_x
    elif label == "radar_top":
        amp = 0.45 + 0.95 * np.exp(-0.5 * ((freq_ghz - 1.2) / 0.13) ** 2)
        phase = -0.55 * phase_x
    elif label == "mixed_avionics":
        low_peak = np.exp(-0.5 * ((freq_ghz - 0.98) / 0.10) ** 2)
        high_peak = np.exp(-0.5 * ((freq_ghz - 1.43) / 0.12) ** 2)
        amp = 0.58 + 0.42 * low_peak + 0.54 * high_peak
        phase = 0.80 * phase_x
    elif label == "multi_state_on":
        amp = 0.62 + 0.32 * (freq_ghz - 0.9) / 0.6 + 0.12 * np.sin(3.0 * np.pi * phase_x)
        phase = -0.95 * phase_x + 0.25 * np.sin(np.pi * phase_x)
    else:
        amp = 1.0
        phase = 0.0
    return complex(amp) * np.exp(1j * phase)


def apply_frequency_profile(sources: SourceSet, frequency_hz: float) -> SourceSet:
    scale = spectral_profile(sources.label, frequency_hz)
    phase_ramp = np.exp(
        1j
        * 0.045
        * (frequency_hz - 1.2e9)
        / 1e8
        * np.arange(1, sources.moments.shape[0] + 1)[:, None]
    )
    return SourceSet(
        positions=sources.positions,
        moments=sources.moments * scale * phase_ramp,
        label=sources.label,
    )


def make_label_row(sample_id: str, class_label: str, sample_idx: int, frequencies_hz: np.ndarray) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "class_label": class_label,
        "source_config": class_label,
        "carrier_model": "synthetic_level2_multisource",
        "working_state": f"{class_label}_state",
        "sample_index_in_class": sample_idx,
        "frequencies_hz": ";".join(str(int(freq)) for freq in frequencies_hz),
    }


def build_nearfield_rows(
    layout,
    source: SourceSet,
    sample_id: str,
    frequency_hz: float,
    snr_db: float,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    cart_field = cartesian_field_response(layout.positions, source, frequency_hz)
    cart_field = add_complex_noise(cart_field, snr_db, rng)
    rows: list[dict[str, object]] = []
    for sensor_id, position in enumerate(layout.positions):
        for component_idx, polarization in enumerate(("Ex", "Ey", "Ez")):
            value = cart_field[sensor_id, component_idx]
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
                    "source_config": source.label,
                    "carrier_model": "synthetic_level2_multisource",
                    "working_state": f"{source.label}_state",
                    "cst_project": "synthetic_not_cst.cst",
                    "monitor_name": f"nearfield_hemisphere_{int(round(frequency_hz / 1e6))}MHz",
                }
            )
    return rows


def build_farfield_rows(source: SourceSet, sample_id: str, frequency_hz: float, theta: np.ndarray, phi: np.ndarray) -> list[dict[str, object]]:
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
                "source_config": source.label,
                "carrier_model": "synthetic_level2_multisource",
                "working_state": f"{source.label}_state",
                "cst_project": "synthetic_not_cst.cst",
                "monitor_name": f"farfield_{int(round(frequency_hz / 1e6))}MHz",
            }
        )
    return rows


def write_metadata(out_dir: Path, config: DatasetConfig, class_labels: list[str], sensor_count: int, frequencies_hz: np.ndarray) -> None:
    metadata = {
        "contest": "CS-202614",
        "stage": "G3_synthetic_CST_format_recognition_dataset",
        "warning": config.synthetic_note,
        "config": asdict(config),
        "class_labels": class_labels,
        "frequency_hz": [int(round(freq)) for freq in frequencies_hz],
        "measurement_layout": {
            "type": "2pi upper hemisphere",
            "radius_m": config.layout_radius_m,
            "sensor_points": sensor_count,
            "nearfield_components": ["Ex", "Ey", "Ez"],
            "recognition_projection": "Ex/Ey/Ez can be projected to theta/phi by cst_io.cartesian_to_theta_phi_rows.",
        },
        "output_files": {
            "nearfield": "nearfield_multistate.csv",
            "farfield": "farfield_multistate.csv",
            "labels": "labels.csv",
        },
        "usage": {
            "validate": "python code\\check_cst_export.py --nearfield outputs\\synthetic_cst_dataset\\nearfield_multistate.csv --farfield outputs\\synthetic_cst_dataset\\farfield_multistate.csv",
            "recognize": "python code\\run_cst_recognition.py --nearfield outputs\\synthetic_cst_dataset\\nearfield_multistate.csv --labels outputs\\synthetic_cst_dataset\\labels.csv --out-dir outputs\\cst_recognition_demo",
        },
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a CST-format synthetic multi-source recognition dataset.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--samples-per-class", type=int, default=24, help="Number of samples for each radiation state.")
    parser.add_argument("--nearfield-snr-db", type=float, default=32.0, help="SNR used for synthetic near-field measurements.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    parser.add_argument("--n-theta-farfield", type=int, default=19, help="Far-field theta grid count.")
    parser.add_argument("--n-phi-farfield", type=int, default=36, help="Far-field phi grid count.")
    args = parser.parse_args()

    if args.samples_per_class < 4:
        raise ValueError("--samples-per-class should be at least 4 for stratified recognition.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    layout = make_hemisphere_layout(n_theta=9, n_phi=18, radius_m=13.0)
    grid_positions = make_equivalent_grid(nx=4, ny=3, nz=3)
    templates = class_templates(grid_positions)
    theta_ff, phi_ff, _ = farfield_grid(n_theta=args.n_theta_farfield, n_phi=args.n_phi_farfield)

    nearfield_rows: list[dict[str, object]] = []
    farfield_rows: list[dict[str, object]] = []
    label_rows: list[dict[str, object]] = []

    for template in templates:
        for sample_idx in range(args.samples_per_class):
            sample_id = f"SYN_{template.label}_{sample_idx:03d}"
            jittered = jitter_sources(template, rng, amp_jitter=0.10, phase_jitter_deg=12.0)
            label_rows.append(make_label_row(sample_id, template.label, sample_idx, DEFAULT_FREQUENCIES_HZ))
            for frequency_hz in DEFAULT_FREQUENCIES_HZ:
                profiled = apply_frequency_profile(jittered, frequency_hz)
                nearfield_rows.extend(
                    build_nearfield_rows(
                        layout=layout,
                        source=profiled,
                        sample_id=sample_id,
                        frequency_hz=frequency_hz,
                        snr_db=args.nearfield_snr_db,
                        rng=rng,
                    )
                )
                farfield_rows.extend(build_farfield_rows(profiled, sample_id, frequency_hz, theta_ff, phi_ff))

    nearfield = pd.DataFrame(nearfield_rows)
    farfield = pd.DataFrame(farfield_rows)
    labels = pd.DataFrame(label_rows)

    nearfield.to_csv(out_dir / "nearfield_multistate.csv", index=False, encoding="utf-8-sig")
    farfield.to_csv(out_dir / "farfield_multistate.csv", index=False, encoding="utf-8-sig")
    labels.to_csv(out_dir / "labels.csv", index=False, encoding="utf-8-sig")

    config = DatasetConfig(
        samples_per_class=args.samples_per_class,
        nearfield_snr_db=args.nearfield_snr_db,
        seed=args.seed,
        n_theta_farfield=args.n_theta_farfield,
        n_phi_farfield=args.n_phi_farfield,
        layout_radius_m=layout.radius_m,
        synthetic_note="This dataset is generated by a lightweight dipole model. It validates the CST-format algorithm path but is not CST simulation evidence.",
    )
    write_metadata(
        out_dir=out_dir,
        config=config,
        class_labels=[template.label for template in templates],
        sensor_count=layout.positions.shape[0],
        frequencies_hz=DEFAULT_FREQUENCIES_HZ,
    )

    print(f"Synthetic CST-format dataset written to {out_dir}")
    print(f"nearfield rows: {len(nearfield)}")
    print(f"farfield rows: {len(farfield)}")
    print(f"samples: {len(labels)}")


if __name__ == "__main__":
    main()
