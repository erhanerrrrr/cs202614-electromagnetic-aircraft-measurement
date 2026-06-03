# Level 2 Instrument Error Check

This directory stores the G5 recognition follow-up for instrument-like
calibration errors. It is separate from missing-channel/dropout tests:
fields are not zeroed; instead, correlated amplitude and phase biases are
applied by sample, sensor, frequency, and polarization groups.

## Current Result

- Seeds: 202614, 202615, 202616.
- Layouts tested: fibonacci_snap_120, full_grid_162, geometric_farthest_32, task_driven_32, task_driven_48.
- Training profiles: clean_train, known_perturbation_augmented.
- Instrument cases tested: frequency_slope_3db, global_gain_drift_3db, mixed_amp_phase_bias, polarization_imbalance_2db, sensor_gain_bias_3db.
- Total rows: 150.
- All rows pass accuracy >= 0.85: `true`.
- Worst single row: seed `202614`, `geometric_farthest_32` / `clean_train` / `sensor_gain_bias_3db` with accuracy `0.933`.
- Best average training profile: `clean_train` with mean accuracy `0.999`, min accuracy `0.933`, and mean delta vs clean-train profile `+0.000`.
- Tightest aggregate row: `geometric_farthest_32` / `clean_train` / `sensor_gain_bias_3db`, mean `0.978`, min `0.933`, mean delta vs clean-train profile `+0.000`.

## Training Profile Summary

| Training profile | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs clean-train profile | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| clean_train | 3 | 75 | 0.999 | 0.933 | 0.997 | 1.000 | +0.000 | true |
| known_perturbation_augmented | 3 | 75 | 0.999 | 0.933 | 0.997 | 1.000 | +0.000 | true |

## Tightest Case Rows

| Candidate | Training profile | Stress case | Mean accuracy | Min accuracy | Mean delta vs clean-train profile | Passes 0.85 |
|---|---|---|---:|---:|---:|---|
| geometric_farthest_32 | clean_train | sensor_gain_bias_3db | 0.978 | 0.933 | +0.000 | true |
| geometric_farthest_32 | known_perturbation_augmented | sensor_gain_bias_3db | 0.978 | 0.933 | +0.000 | true |
| full_grid_162 | clean_train | global_gain_drift_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | known_perturbation_augmented | global_gain_drift_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | clean_train | sensor_gain_bias_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | known_perturbation_augmented | sensor_gain_bias_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | clean_train | frequency_slope_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | known_perturbation_augmented | frequency_slope_3db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | clean_train | polarization_imbalance_2db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | known_perturbation_augmented | polarization_imbalance_2db | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | clean_train | mixed_amp_phase_bias | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | known_perturbation_augmented | mixed_amp_phase_bias | 1.000 | 1.000 | +0.000 | true |

## Files

| File | Purpose |
|---|---|
| `recognition_instrument_error_metrics.csv` | Per-seed/per-layout/per-profile/per-case accuracy and macro-F1. |
| `recognition_instrument_error_by_profile.csv` | Aggregate comparison of clean-train and known-perturbation-augmented training profiles. |
| `recognition_instrument_error_by_case.csv` | Aggregate comparison by layout, profile, and instrument error case. |
| `recognition_instrument_error_by_layout.csv` | Aggregate comparison by layout and profile. |
| `recognition_instrument_error_summary.json` | Machine-readable summary, inputs, cases, and aggregate tables. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_instrument_error.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --instrument-cases global_gain_drift_3db,sensor_gain_bias_3db,frequency_slope_3db,polarization_imbalance_2db,mixed_amp_phase_bias --seeds 202614,202615,202616 --out-dir data\recognition_stress_tests\level2_instrument_error
```

## Boundary

This is a Level 2 CST-derived element-library instrument-error check.
It tests simulated correlated gain/phase calibration biases. It does not
replace real instrument calibration, full-wave airframe validation, or
the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
