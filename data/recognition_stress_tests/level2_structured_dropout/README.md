# Level 2 Structured Dropout Check

This directory stores the G5 follow-up for structured missing-channel
recognition robustness. Models are trained with the existing clean,
noise, phase-jitter, random dropout, and combined augmentation profiles,
then tested on unseen structured dropout patterns.

## Current Result

- Seeds: 202614, 202615, 202616.
- Layouts tested: fibonacci_snap_120, full_grid_162, geometric_farthest_32, task_driven_32, task_driven_48.
- Strategies tested: zero_fill, mask_features, freq_sensor_median_impute, freq_sensor_median_impute_mask.
- Structured cases tested: azimuth_sector_dropout_60deg, polarization_pair_dropout_10pct, sensor_node_dropout_10pct, sensor_node_dropout_25pct.
- Total rows: 240.
- All rows pass accuracy >= 0.85: `true`.
- Worst single row: seed `202614`, `geometric_farthest_32` / `mask_features` / `sensor_node_dropout_25pct` with accuracy `0.933`.
- Best average strategy: `freq_sensor_median_impute` with mean accuracy `1.000`, min accuracy `1.000`, and mean delta vs zero-fill `+0.004`.
- Tightest aggregate row: `geometric_farthest_32` / `mask_features` / `sensor_node_dropout_25pct`, mean `0.933`, min `0.933`, mean delta vs zero-fill `-0.022`.

## Strategy Summary

| Strategy | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs zero-fill | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| zero_fill | 3 | 60 | 0.996 | 0.933 | 0.991 | 1.000 | +0.000 | true |
| mask_features | 3 | 60 | 0.994 | 0.933 | 0.990 | 0.999 | -0.001 | true |
| freq_sensor_median_impute | 3 | 60 | 1.000 | 1.000 | 1.000 | 1.000 | +0.004 | true |
| freq_sensor_median_impute_mask | 3 | 60 | 1.000 | 1.000 | 1.000 | 1.000 | +0.004 | true |

## Tightest Case Rows

| Candidate | Stress case | Strategy | Mean accuracy | Min accuracy | Mean delta vs zero-fill | Passes 0.85 |
|---|---|---|---:|---:|---:|---|
| geometric_farthest_32 | sensor_node_dropout_25pct | mask_features | 0.933 | 0.933 | -0.022 | true |
| geometric_farthest_32 | sensor_node_dropout_25pct | zero_fill | 0.956 | 0.933 | +0.000 | true |
| full_grid_162 | azimuth_sector_dropout_60deg | zero_fill | 0.978 | 0.933 | +0.000 | true |
| full_grid_162 | azimuth_sector_dropout_60deg | mask_features | 0.978 | 0.933 | +0.000 | true |
| geometric_farthest_32 | sensor_node_dropout_10pct | zero_fill | 0.978 | 0.933 | +0.000 | true |
| geometric_farthest_32 | sensor_node_dropout_10pct | mask_features | 0.978 | 0.933 | +0.000 | true |
| full_grid_162 | sensor_node_dropout_10pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | sensor_node_dropout_25pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | polarization_pair_dropout_10pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | sensor_node_dropout_10pct | mask_features | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | sensor_node_dropout_25pct | mask_features | 1.000 | 1.000 | +0.000 | true |
| full_grid_162 | polarization_pair_dropout_10pct | mask_features | 1.000 | 1.000 | +0.000 | true |

## Files

| File | Purpose |
|---|---|
| `recognition_structured_dropout_metrics.csv` | Per-seed/per-layout/per-strategy structured dropout accuracy and macro-F1. |
| `recognition_structured_dropout_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |
| `recognition_structured_dropout_by_case.csv` | Aggregate comparison by layout, structured dropout case, and strategy. |
| `recognition_structured_dropout_by_layout.csv` | Aggregate comparison by layout and strategy. |
| `recognition_structured_dropout_summary.json` | Machine-readable summary, inputs, strategy definitions, structured cases, and aggregate tables. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_structured_dropout.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --structured-cases sensor_node_dropout_10pct,sensor_node_dropout_25pct,polarization_pair_dropout_10pct,azimuth_sector_dropout_60deg --strategies zero_fill,mask_features,freq_sensor_median_impute,freq_sensor_median_impute_mask --seeds 202614,202615,202616 --out-dir data\recognition_stress_tests\level2_structured_dropout
```

## Boundary

This is a Level 2 CST-derived element-library structured dropout check.
It tests internal simulated sensor-node, polarization-pair, and angular-sector
missing-channel patterns. It does not replace real measurement calibration,
full-wave airframe validation, or the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
