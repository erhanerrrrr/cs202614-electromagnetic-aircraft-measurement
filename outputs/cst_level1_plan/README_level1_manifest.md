# CST Level 1 manifest

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
python src\check_cst_export.py --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv
python src\run_cst_reconstruction.py --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv --sample-id L1_short_dipole_z_1p2G --frequency-hz 1200000000 --out-dir outputs\cst_reconstruction\L1_short_dipole_z_1p2G
```

If CST exports magnitude/phase columns, first normalize:

```powershell
python src\normalize_cst_complex_columns.py --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield_phase.csv --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield_phase.csv --nearfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv --farfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv --phase-unit deg
```
