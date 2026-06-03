# Level 2 Compound Instrument-Dropout Check

This directory stores the G5 severe compound stress follow-up for Level 2
recognition. Models are trained with the existing clean, noise, phase,
random-dropout, and combined perturbation profiles, then tested on unseen
compound cases that apply correlated instrument bias and structured
missing-channel patterns together.

## Current Result

- Seeds: 202614, 202615, 202616.
- Layouts tested: fibonacci_snap_120, full_grid_162, geometric_farthest_32, task_driven_32, task_driven_48.
- Strategies tested: zero_fill, mask_features, freq_sensor_median_impute, freq_sensor_median_impute_mask.
- Compound cases tested: mixed_amp_phase_azimuth_sector60deg, mixed_amp_phase_sensor_node_dropout25pct, polarization_imbalance_pair_dropout10pct, sensor_gain3db_sensor_node_dropout25pct.
- Total rows: 240.
- All rows pass accuracy >= 0.85: `false`.
- Worst row: `full_grid_162` / `zero_fill` / `sensor_gain3db_sensor_node_dropout25pct` at accuracy `0.733`.
- Tightest aggregate: `full_grid_162` / `zero_fill` / `sensor_gain3db_sensor_node_dropout25pct` with mean accuracy `0.867` and minimum `0.733`.

## Strategy Summary

| Strategy | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs zero-fill | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---|
| zero_fill | 0.939 | 0.733 | 0.921 | 0.957 | +0.000 | false |
| mask_features | 0.940 | 0.733 | 0.923 | 0.957 | +0.001 | false |
| freq_sensor_median_impute | 0.993 | 0.867 | 0.987 | 0.999 | +0.054 | true |
| freq_sensor_median_impute_mask | 0.990 | 0.867 | 0.983 | 0.997 | +0.051 | true |

## Tightest Case Rows

| Candidate | Stress case | Strategy | Mean accuracy | Min accuracy | Mean delta vs zero-fill | Passes 0.85 |
|---|---|---|---:|---:|---:|---|
| full_grid_162 | sensor_gain3db_sensor_node_dropout25pct | zero_fill | 0.867 | 0.733 | +0.000 | false |
| full_grid_162 | mixed_amp_phase_azimuth_sector60deg | mask_features | 0.867 | 0.733 | -0.022 | false |
| fibonacci_snap_120 | sensor_gain3db_sensor_node_dropout25pct | zero_fill | 0.867 | 0.733 | +0.000 | false |
| full_grid_162 | mixed_amp_phase_azimuth_sector60deg | zero_fill | 0.889 | 0.733 | +0.000 | false |
| task_driven_48 | mixed_amp_phase_sensor_node_dropout25pct | mask_features | 0.889 | 0.733 | -0.022 | false |
| full_grid_162 | sensor_gain3db_sensor_node_dropout25pct | mask_features | 0.867 | 0.800 | +0.000 | false |
| fibonacci_snap_120 | sensor_gain3db_sensor_node_dropout25pct | mask_features | 0.889 | 0.800 | +0.022 | false |
| task_driven_48 | mixed_amp_phase_sensor_node_dropout25pct | zero_fill | 0.911 | 0.800 | +0.000 | false |
| geometric_farthest_32 | mixed_amp_phase_sensor_node_dropout25pct | zero_fill | 0.889 | 0.867 | +0.000 | true |
| geometric_farthest_32 | mixed_amp_phase_azimuth_sector60deg | zero_fill | 0.889 | 0.867 | +0.000 | true |
| fibonacci_snap_120 | mixed_amp_phase_azimuth_sector60deg | mask_features | 0.889 | 0.867 | -0.022 | true |
| geometric_farthest_32 | mixed_amp_phase_sensor_node_dropout25pct | mask_features | 0.911 | 0.867 | +0.022 | true |

## Files

| File | Purpose |
|---|---|
| `recognition_compound_stress_metrics.csv` | Per-seed/per-layout/per-strategy compound stress accuracy and macro-F1. |
| `recognition_compound_stress_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |
| `recognition_compound_stress_by_case.csv` | Aggregate comparison by layout, compound case, and strategy. |
| `recognition_compound_stress_by_layout.csv` | Aggregate comparison by layout and strategy. |
| `recognition_compound_stress_summary.json` | Machine-readable summary, inputs, compound cases, strategy definitions, and aggregate tables. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_compound_stress.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --compound-cases sensor_gain3db_sensor_node_dropout25pct,mixed_amp_phase_sensor_node_dropout25pct,mixed_amp_phase_azimuth_sector60deg,polarization_imbalance_pair_dropout10pct --strategies zero_fill,mask_features,freq_sensor_median_impute,freq_sensor_median_impute_mask --seeds 202614,202615,202616 --out-dir data\recognition_stress_tests\level2_compound_stress
```

## Boundary

This is a Level 2 CST-derived element-library compound stress check.
It tests simulated correlated instrument bias plus structured missing
channels. It does not replace real instrument calibration, full-wave
airframe validation, or the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
