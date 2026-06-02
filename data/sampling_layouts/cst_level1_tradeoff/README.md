# CST Level 1 Sampling Tradeoff

This compact evidence table evaluates the sampling candidates from
`data/sampling_layouts/hemisphere_sampling_candidates.csv` on the current local
Level 1 CST exports.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Candidate layouts | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |
| Equivalent-source grid | `[5, 3, 3]` over `{'x': [-0.25, 0.25], 'y': [-0.25, 0.25], 'z': [3.75, 4.25]}` m |

## Candidate Summary

| Candidate | Sensors | Method | Mean Corr | Min Corr | Mean NMSE | Max NMSE |
|---|---:|---|---:|---:|---:|---:|
| full_grid_162 | 162 | full_grid | 0.8065 | 0.7930 | 3.0937e-01 | 3.2036e-01 |
| dictionary_weighted_120 | 120 | dictionary_weighted | 0.6988 | 0.6740 | 4.8976e-01 | 4.9630e-01 |
| fibonacci_snap_120 | 120 | fibonacci_snap | -0.3263 | -0.3585 | 9.4176e-01 | 9.4297e-01 |
| geometric_farthest_120 | 120 | geometric_farthest | -0.4181 | -0.4445 | 9.8989e-01 | 9.9570e-01 |
| dictionary_weighted_81 | 81 | dictionary_weighted | 0.2651 | 0.2568 | 8.5728e-01 | 8.6277e-01 |
| task_driven_48 | 48 | task_driven | 0.2288 | 0.2262 | 6.9674e-01 | 6.9764e-01 |

## Per-Sample Results

| Sample | Candidate | Sensors | Corr | NMSE | Main-lobe error / deg |
|---|---|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | full_grid_162 | 162 | 0.8201 | 2.9838e-01 | 69.95 |
| L1_halfwave_dipole_z_1p2G | dictionary_weighted_120 | 120 | 0.7236 | 4.8322e-01 | 109.90 |
| L1_halfwave_dipole_z_1p2G | fibonacci_snap_120 | 120 | -0.2941 | 9.4297e-01 | 83.45 |
| L1_halfwave_dipole_z_1p2G | geometric_farthest_120 | 120 | -0.3918 | 9.9570e-01 | 82.14 |
| L1_halfwave_dipole_z_1p2G | dictionary_weighted_81 | 81 | 0.2734 | 8.5179e-01 | 57.34 |
| L1_halfwave_dipole_z_1p2G | task_driven_48 | 48 | 0.2314 | 6.9764e-01 | 84.94 |
| L1_short_dipole_z_1p2G | full_grid_162 | 162 | 0.7930 | 3.2036e-01 | 109.90 |
| L1_short_dipole_z_1p2G | dictionary_weighted_120 | 120 | 0.6740 | 4.9630e-01 | 119.88 |
| L1_short_dipole_z_1p2G | fibonacci_snap_120 | 120 | -0.3585 | 9.4055e-01 | 84.90 |
| L1_short_dipole_z_1p2G | geometric_farthest_120 | 120 | -0.4445 | 9.8407e-01 | 86.44 |
| L1_short_dipole_z_1p2G | dictionary_weighted_81 | 81 | 0.2568 | 8.6277e-01 | 75.46 |
| L1_short_dipole_z_1p2G | task_driven_48 | 48 | 0.2262 | 6.9583e-01 | 144.78 |

## Reading

- Full-grid Level 1 reconstruction does not yet meet the current acceptance target
  (`Corr >= 0.95`, `NMSE <= 1e-2`), so this table is a calibration diagnostic
  rather than a final sampling conclusion.
- The next action is to debug source-grid placement, CST near-field extraction,
  phase convention, theta/phi projection, and equivalent-source model settings.
- Candidate ranking below 162 sensors should not be used as the main report claim
  until the full-grid baseline is calibrated.
