# L1_short_dipole_z_1p2G

Priority: `required`  
Purpose: CST Level 1 standard-source validation case.

## CST Project

| Item | Value |
|---|---|
| CST project | `CST_L1_short_dipole_z_1p2G.cst` |
| Frequency | `1200000000` Hz (`1200MHz`) |
| Boundary | `Open/Add Space or PML` |
| Solver note | Use a frequency-domain or time-domain setup that exports complex field values. |
| Current measurement surface | 2π upper hemisphere |
| Near-field monitor | `nearfield_hemisphere_1200MHz` |
| Far-field monitor | `farfield_1200MHz` |

## Source Parameters

| Item | Value |
|---|---:|
| Source type | `short_dipole` |
| Orientation axis | `z` |
| Center x/y/z m | `0.0`, `0.0`, `4.0` |
| Orientation vector | `0.0`, `0.0`, `1.0` |
| Length m | `0.0124913524166666` |
| Feed gap m | `0.0006245676208333` |
| Relative amplitude | `1.0` |
| Relative phase deg | `0.0` |
| Start x/y/z m | `0.0`, `0.0`, `3.993754323791667` |
| End x/y/z m | `0.0`, `0.0`, `4.006245676208334` |

## Export Targets

| Export | Path | Expected rows |
|---|---|---:|
| Near-field real/imag | `data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv` | 486 |
| Far-field real/imag | `data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv` | 2664 |
| Near-field magnitude/phase fallback | `data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield_phase.csv` | 486 |
| Far-field magnitude/phase fallback | `data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield_phase.csv` | 2664 |

Required sensor points: `162` on the selected 2π upper-hemisphere layout.

## Acceptance Targets

| Metric | Threshold |
|---|---:|
| Correlation | >= 0.95 |
| Main-lobe error deg | <= 5.0 |
| NMSE | <= 0.01 |

## Commands After Export

```powershell
python src\check_cst_export.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_validation.json
python src\run_cst_reconstruction.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --sample-id L1_short_dipole_z_1p2G --frequency-hz 1200000000 --out-dir outputs\cst_reconstruction\L1_short_dipole_z_1p2G
```

If CST exports magnitude/phase instead of real/imag:

```powershell
python src\normalize_cst_complex_columns.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield_phase.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield_phase.csv --nearfield-out data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield-out data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --phase-unit deg
```

## Manual Checks

- `sample_id`, `frequency_hz`, and export filenames match this card exactly.
- Coordinates are in meters, not millimeters.
- Near-field rows include complete `Ex`, `Ey`, `Ez` values for all upper-hemisphere sensor ids.
- Far-field rows include complex `e_theta`/`e_phi` or at least `gain_db`/`power`.
- Screenshots of model, source, boundary, monitors, and export dialog are saved.
