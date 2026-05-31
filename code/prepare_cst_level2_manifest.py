from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_level2_plan"
DEFAULT_FREQUENCIES_HZ = [900_000_000, 1_050_000_000, 1_200_000_000, 1_350_000_000, 1_500_000_000]


LEVEL2_CLASSES = {
    "comm_pair": [
        {"role": "left_comm", "position_m": (-5.5, -4.5, 4.0), "orientation": (1.0, 0.0, 0.0), "base_amp": 1.00, "base_phase_deg": 0.0},
        {"role": "right_comm", "position_m": (5.5, 4.5, 4.0), "orientation": (0.0, 1.0, 0.0), "base_amp": 0.90, "base_phase_deg": 35.0},
    ],
    "radar_top": [
        {"role": "front_top_radar", "position_m": (0.0, -4.5, 7.0), "orientation": (0.0, 0.0, 1.0), "base_amp": 1.20, "base_phase_deg": 0.0},
        {"role": "rear_top_radar", "position_m": (0.0, 4.5, 7.0), "orientation": (0.0, 0.0, 1.0), "base_amp": 0.95, "base_phase_deg": -40.0},
    ],
    "mixed_avionics": [
        {"role": "belly_nav", "position_m": (-2.75, 1.5, 1.0), "orientation": (1.0, 0.0, 0.0), "base_amp": 0.85, "base_phase_deg": 10.0},
        {"role": "top_link", "position_m": (2.75, -1.5, 7.0), "orientation": (0.0, 1.0, 0.0), "base_amp": 1.05, "base_phase_deg": 75.0},
        {"role": "side_beacon", "position_m": (0.0, 4.5, 4.0), "orientation": (0.0, 0.0, 1.0), "base_amp": 0.70, "base_phase_deg": -25.0},
    ],
    "multi_state_on": [
        {"role": "left_top_emitter", "position_m": (-5.5, 4.5, 7.0), "orientation": (1.0, 0.0, 0.0), "base_amp": 1.05, "base_phase_deg": 95.0},
        {"role": "right_belly_emitter", "position_m": (5.5, -4.5, 1.0), "orientation": (0.0, 1.0, 0.0), "base_amp": 0.90, "base_phase_deg": -60.0},
        {"role": "center_avionics", "position_m": (0.0, 0.0, 4.0), "orientation": (0.0, 0.0, 1.0), "base_amp": 0.95, "base_phase_deg": 20.0},
    ],
}


def source_rows_for_sample(
    class_label: str,
    sample_id: str,
    variant_idx: int,
    rng: np.random.Generator,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source_idx, source in enumerate(LEVEL2_CLASSES[class_label]):
        position = source["position_m"]
        orientation = np.asarray(source["orientation"], dtype=float)
        amp_scale = float(source["base_amp"] * (1.0 + 0.08 * rng.standard_normal()))
        phase_deg = float(source["base_phase_deg"] + rng.normal(0.0, 10.0))
        rows.append(
            {
                "sample_id": sample_id,
                "class_label": class_label,
                "variant_index": variant_idx,
                "source_index": source_idx,
                "source_role": source["role"],
                "antenna_model": "ideal_dipole_or_small_discrete_port",
                "x_m": float(position[0]),
                "y_m": float(position[1]),
                "z_m": float(position[2]),
                "orientation_x": float(orientation[0]),
                "orientation_y": float(orientation[1]),
                "orientation_z": float(orientation[2]),
                "relative_amplitude": amp_scale,
                "relative_phase_deg": phase_deg,
                "implementation_note": "In CST, use the listed position/orientation as the feed or ideal source reference; keep amplitude and phase in the excitation table.",
            }
        )
    return rows


def frequency_case_rows(sample_id: str, class_label: str, variant_idx: int, frequencies_hz: list[int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    project_name = f"CST_L2_{class_label}_{variant_idx:03d}.cst"
    for freq in frequencies_hz:
        freq_mhz = int(round(freq / 1e6))
        rows.append(
            {
                "sample_id": sample_id,
                "class_label": class_label,
                "variant_index": variant_idx,
                "frequency_hz": int(freq),
                "frequency_label": f"{freq_mhz}MHz",
                "carrier_model": "level2_multisource_no_airframe",
                "working_state": f"{class_label}_state",
                "cst_project": project_name,
                "nearfield_monitor": f"nearfield_hemisphere_{freq_mhz}MHz",
                "farfield_monitor": f"farfield_{freq_mhz}MHz",
                "nearfield_export": f"data/cst_exports/level2/{sample_id}_nearfield.csv",
                "farfield_export": f"data/cst_exports/level2/{sample_id}_farfield.csv",
                "expected_nearfield_rows_per_frequency": 162 * 3,
                "expected_farfield_rows_per_frequency": 19 * 36,
                "status": "planned",
            }
        )
    return rows


def write_readme(out_dir: Path, variants_per_class: int, frequencies_hz: list[int]) -> None:
    frequencies_text = ", ".join(f"{freq / 1e9:.2f} GHz" for freq in frequencies_hz)
    content = f"""# CST Level 2 manifest

This folder contains the planned CST multi-source/multi-frequency recognition cases for CS-202614.

## Files

| File | Use |
|---|---|
| `level2_case_manifest.csv` | One row per sample/frequency pair. Use it to configure monitors and file names. |
| `level2_source_manifest.csv` | One row per source in each sample. Use it to configure source position, orientation, amplitude, and phase. |
| `level2_labels.csv` | One row per sample_id for `code/run_cst_recognition.py`. |
| `level2_manifest_summary.json` | Counts and fixed assumptions. |

## Fixed plan

- Classes: comm_pair, radar_top, mixed_avionics, multi_state_on.
- Variants per class: {variants_per_class}.
- Frequencies: {frequencies_text}.
- Measurement surface: 13 m upper hemisphere, 162 spatial points.
- Near-field export: Ex/Ey/Ez complex field at every sensor point.
- Far-field export: Etheta/Ephi complex field or gain on a 19 x 36 theta/phi grid.

## CST handoff

For each `sample_id`, build or duplicate the CST project listed in `cst_project`.
For every frequency row, create/enable the named near-field and far-field monitors.
After export, concatenate rows into the CSV names listed in `nearfield_export` and `farfield_export`.
Then run:

```powershell
python code\\check_cst_export.py --nearfield data\\cst_exports\\level2\\<sample_id>_nearfield.csv --farfield data\\cst_exports\\level2\\<sample_id>_farfield.csv
python code\\run_cst_recognition.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2
```
"""
    (out_dir / "README_level2_manifest.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CST Level 2 multi-source recognition manifests.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--variants-per-class", type=int, default=12, help="Number of amplitude/phase variants per class.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    if args.variants_per_class < 2:
        raise ValueError("--variants-per-class should be at least 2")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    case_rows: list[dict[str, object]] = []
    source_rows: list[dict[str, object]] = []
    label_rows: list[dict[str, object]] = []

    for class_label in LEVEL2_CLASSES:
        for variant_idx in range(args.variants_per_class):
            sample_id = f"L2_{class_label}_{variant_idx:03d}"
            case_rows.extend(frequency_case_rows(sample_id, class_label, variant_idx, DEFAULT_FREQUENCIES_HZ))
            source_rows.extend(source_rows_for_sample(class_label, sample_id, variant_idx, rng))
            label_rows.append(
                {
                    "sample_id": sample_id,
                    "class_label": class_label,
                    "source_config": class_label,
                    "carrier_model": "level2_multisource_no_airframe",
                    "working_state": f"{class_label}_state",
                    "frequencies_hz": ";".join(str(freq) for freq in DEFAULT_FREQUENCIES_HZ),
                }
            )

    case_df = pd.DataFrame(case_rows)
    source_df = pd.DataFrame(source_rows)
    label_df = pd.DataFrame(label_rows)
    case_df.to_csv(out_dir / "level2_case_manifest.csv", index=False, encoding="utf-8-sig")
    source_df.to_csv(out_dir / "level2_source_manifest.csv", index=False, encoding="utf-8-sig")
    label_df.to_csv(out_dir / "level2_labels.csv", index=False, encoding="utf-8-sig")

    summary = {
        "stage": "CST_Level2_multisource_recognition",
        "classes": list(LEVEL2_CLASSES.keys()),
        "variants_per_class": args.variants_per_class,
        "sample_count": int(len(label_df)),
        "sample_frequency_rows": int(len(case_df)),
        "source_rows": int(len(source_df)),
        "frequencies_hz": DEFAULT_FREQUENCIES_HZ,
        "sensor_points": 162,
        "nearfield_components": ["Ex", "Ey", "Ez"],
        "farfield_grid": {"n_theta": 19, "n_phi": 36},
        "note": "This is a CST execution manifest, not simulation output. Fill the listed export files with CST-generated complex fields.",
    }
    (out_dir / "level2_manifest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, args.variants_per_class, DEFAULT_FREQUENCIES_HZ)

    print(f"CST Level 2 manifest written to {out_dir}")
    print(f"samples: {len(label_df)}")
    print(f"sample-frequency rows: {len(case_df)}")
    print(f"source rows: {len(source_df)}")


if __name__ == "__main__":
    main()
