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
| Equivalent-source grid | `[1, 1, 1]` over `{'x': [0.0, 0.0], 'y': [0.0, 0.0], 'z': [4.0, 4.0]}` m |

## Candidate Summary

| Candidate | Sensors | Method | Mean Corr | Min Corr | Mean NMSE | Max NMSE |
|---|---:|---|---:|---:|---:|---:|
| full_grid_162 | 162 | full_grid | 0.9963 | 0.9926 | 8.8929e-03 | 1.7784e-02 |
| geometric_farthest_120 | 120 | geometric_farthest | 0.9956 | 0.9920 | 9.3382e-03 | 1.8161e-02 |
| fibonacci_snap_120 | 120 | fibonacci_snap | 0.9939 | 0.9907 | 1.0538e-02 | 1.9196e-02 |
| dictionary_weighted_120 | 120 | dictionary_weighted | 0.9935 | 0.9896 | 1.0960e-02 | 2.0191e-02 |
| dictionary_weighted_81 | 81 | dictionary_weighted | 0.9958 | 0.9921 | 9.1871e-03 | 1.7991e-02 |
| task_driven_48 | 48 | task_driven | 0.9772 | 0.9770 | 2.4509e-02 | 3.3622e-02 |

## Per-Sample Results

| Sample | Candidate | Sensors | Corr | NMSE | Main-lobe error / deg |
|---|---|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | full_grid_162 | 162 | 0.9926 | 1.7784e-02 | 0.00 |
| L1_halfwave_dipole_z_1p2G | dictionary_weighted_120 | 120 | 0.9896 | 2.0191e-02 | 0.00 |
| L1_halfwave_dipole_z_1p2G | fibonacci_snap_120 | 120 | 0.9907 | 1.9196e-02 | 0.00 |
| L1_halfwave_dipole_z_1p2G | geometric_farthest_120 | 120 | 0.9920 | 1.8161e-02 | 0.00 |
| L1_halfwave_dipole_z_1p2G | dictionary_weighted_81 | 81 | 0.9921 | 1.7991e-02 | 0.00 |
| L1_halfwave_dipole_z_1p2G | task_driven_48 | 48 | 0.9770 | 3.3622e-02 | 0.00 |
| L1_short_dipole_z_1p2G | full_grid_162 | 162 | 1.0000 | 1.2935e-06 | 0.00 |
| L1_short_dipole_z_1p2G | dictionary_weighted_120 | 120 | 0.9974 | 1.7287e-03 | 0.00 |
| L1_short_dipole_z_1p2G | fibonacci_snap_120 | 120 | 0.9971 | 1.8793e-03 | 0.00 |
| L1_short_dipole_z_1p2G | geometric_farthest_120 | 120 | 0.9992 | 5.1530e-04 | 0.00 |
| L1_short_dipole_z_1p2G | dictionary_weighted_81 | 81 | 0.9994 | 3.8289e-04 | 0.00 |
| L1_short_dipole_z_1p2G | task_driven_48 | 48 | 0.9774 | 1.5395e-02 | 133.80 |

## Reading

- Full-grid Level 1 reconstruction has passed the correlation and main-lobe sanity
  checks, but the worst-case NMSE is still above the strict `1e-2` target.
- This is useful CST calibration evidence: the near-field export, theta/phi
  projection, and far-field comparison chain are broadly consistent.
- Treat the sub-162 candidate ranking as calibration evidence for this Level 1
  source prior, not as the final airframe sampling conclusion.
