from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_level1_plan"
C0 = 299_792_458.0
FREQ_HZ = 1_200_000_000
FREQ_LABEL = "1p2G"
SENSOR_POINTS = 162
NEARFIELD_COMPONENTS = 3
FARFIELD_THETA = 37
FARFIELD_PHI = 72


LEVEL1_CASES = [
    {"source_type": "short_dipole", "axis": "z", "priority": "required"},
    {"source_type": "halfwave_dipole", "axis": "z", "priority": "required"},
    {"source_type": "short_dipole", "axis": "x", "priority": "recommended"},
    {"source_type": "short_dipole", "axis": "y", "priority": "recommended"},
    {"source_type": "halfwave_dipole", "axis": "x", "priority": "optional"},
    {"source_type": "halfwave_dipole", "axis": "y", "priority": "optional"},
]


def axis_vector(axis: str) -> tuple[float, float, float]:
    return {
        "x": (1.0, 0.0, 0.0),
        "y": (0.0, 1.0, 0.0),
        "z": (0.0, 0.0, 1.0),
    }[axis]


def source_length_m(source_type: str, frequency_hz: float) -> float:
    wavelength = C0 / frequency_hz
    if source_type == "short_dipole":
        return wavelength / 20.0
    if source_type == "halfwave_dipole":
        return wavelength / 2.0
    raise ValueError(source_type)


def sample_id(source_type: str, axis: str) -> str:
    return f"L1_{source_type}_{axis}_{FREQ_LABEL}"


def case_row(source_type: str, axis: str, priority: str) -> dict[str, object]:
    sid = sample_id(source_type, axis)
    freq_mhz = int(round(FREQ_HZ / 1e6))
    return {
        "sample_id": sid,
        "priority": priority,
        "source_config": f"{source_type}_{axis}",
        "source_type": source_type,
        "orientation_axis": axis,
        "frequency_hz": FREQ_HZ,
        "frequency_label": f"{freq_mhz}MHz",
        "carrier_model": "level1_standard_source",
        "working_state": "single_source_on",
        "cst_project": f"CST_{sid}.cst",
        "nearfield_monitor": f"nearfield_hemisphere_{freq_mhz}MHz",
        "farfield_monitor": f"farfield_{freq_mhz}MHz",
        "nearfield_export": f"data/cst_exports/level1/{sid}_nearfield.csv",
        "farfield_export": f"data/cst_exports/level1/{sid}_farfield.csv",
        "phase_format_nearfield_export": f"data/cst_exports/level1/{sid}_nearfield_phase.csv",
        "phase_format_farfield_export": f"data/cst_exports/level1/{sid}_farfield_phase.csv",
        "expected_nearfield_rows": SENSOR_POINTS * NEARFIELD_COMPONENTS,
        "expected_farfield_rows": FARFIELD_THETA * FARFIELD_PHI,
        "status": "planned",
    }


def source_row(source_type: str, axis: str, priority: str) -> dict[str, object]:
    orient = axis_vector(axis)
    length_m = source_length_m(source_type, FREQ_HZ)
    sid = sample_id(source_type, axis)
    return {
        "sample_id": sid,
        "priority": priority,
        "source_type": source_type,
        "source_role": f"{source_type}_{axis}_reference",
        "center_x_m": 0.0,
        "center_y_m": 0.0,
        "center_z_m": 4.0,
        "orientation_x": orient[0],
        "orientation_y": orient[1],
        "orientation_z": orient[2],
        "length_m": length_m,
        "feed_gap_m": min(0.002, length_m / 20.0),
        "relative_amplitude": 1.0,
        "relative_phase_deg": 0.0,
        "boundary_condition": "Open/Add Space or PML",
        "solver_note": "Use a frequency-domain or time-domain setup that exports complex field values.",
    }


def target_row(source_type: str, axis: str, priority: str) -> dict[str, object]:
    sid = sample_id(source_type, axis)
    return {
        "sample_id": sid,
        "priority": priority,
        "min_correlation": 0.95,
        "max_main_lobe_error_deg": 5.0,
        "max_nmse": 1e-2,
        "must_check": "coordinate unit, phase unit, theta/phi definition, source position inside equivalent grid",
    }


def write_readme(out_dir: Path) -> None:
    content = """# CST Level 1 manifest

This folder contains the standard-source execution plan for CS-202614.

## Files

| File | Use |
|---|---|
| `level1_case_manifest.csv` | One row per standard-source CST case and export file. |
| `level1_source_manifest.csv` | Source position, orientation, length, feed gap, and solver notes. |
| `level1_validation_targets.csv` | Pass/fail targets for reconstruction validation. |
| `level1_manifest_summary.json` | Counts and fixed assumptions. |

## Required cases

Run these first:

1. `L1_short_dipole_z_1p2G`
2. `L1_halfwave_dipole_z_1p2G`

If they fail, do not proceed to Level 2. Check coordinate units, phase units, source position, far-field angle definition, and exported polarization.

## Recommended coordinate checks

Then run short dipole x/y:

1. `L1_short_dipole_x_1p2G`
2. `L1_short_dipole_y_1p2G`

These help detect swapped axes or inconsistent polarization definitions.

## Commands after export

If CST exports real/imag columns:

```powershell
python code\\check_cst_export.py --nearfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_nearfield.csv --farfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_farfield.csv
python code\\run_cst_reconstruction.py --nearfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_nearfield.csv --farfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_farfield.csv --sample-id L1_short_dipole_z_1p2G --frequency-hz 1200000000 --out-dir outputs\\cst_reconstruction\\L1_short_dipole_z_1p2G
```

If CST exports magnitude/phase columns, first normalize:

```powershell
python code\\normalize_cst_complex_columns.py --nearfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_nearfield_phase.csv --farfield data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_farfield_phase.csv --nearfield-out data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_nearfield.csv --farfield-out data\\cst_exports\\level1\\L1_short_dipole_z_1p2G_farfield.csv --phase-unit deg
```
"""
    (out_dir / "README_level1_manifest.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CST Level 1 standard-source manifests.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    case_rows = [case_row(**case) for case in LEVEL1_CASES]
    source_rows = [source_row(**case) for case in LEVEL1_CASES]
    target_rows = [target_row(**case) for case in LEVEL1_CASES]

    pd.DataFrame(case_rows).to_csv(out_dir / "level1_case_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(source_rows).to_csv(out_dir / "level1_source_manifest.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(target_rows).to_csv(out_dir / "level1_validation_targets.csv", index=False, encoding="utf-8-sig")

    summary = {
        "stage": "CST_Level1_standard_source",
        "frequency_hz": FREQ_HZ,
        "frequency_label": FREQ_LABEL,
        "case_count": len(case_rows),
        "required_cases": [row["sample_id"] for row in case_rows if row["priority"] == "required"],
        "recommended_cases": [row["sample_id"] for row in case_rows if row["priority"] == "recommended"],
        "optional_cases": [row["sample_id"] for row in case_rows if row["priority"] == "optional"],
        "sensor_points": SENSOR_POINTS,
        "nearfield_components": ["Ex", "Ey", "Ez"],
        "farfield_grid": {"n_theta": FARFIELD_THETA, "n_phi": FARFIELD_PHI},
        "source_center_m": [0.0, 0.0, 4.0],
        "note": "This is a CST execution manifest, not simulation output.",
    }
    (out_dir / "level1_manifest_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir)

    print(f"CST Level 1 manifest written to {out_dir}")
    print(f"cases: {len(case_rows)}")
    print(f"required: {', '.join(summary['required_cases'])}")


if __name__ == "__main__":
    main()
