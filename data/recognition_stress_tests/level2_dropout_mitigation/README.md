# Level 2 Dropout Mitigation Check

This directory stores the focused G5 follow-up for missing-channel
recognition robustness. It keeps the leave-one-stress-family-out
protocol, focuses on held-out dropout or dropout-bearing cases, and
compares zero-fill against lightweight mask-feature and imputation
strategies.

## Current Result

- Seeds: 202614, 202615, 202616.
- Layouts tested: geometric_farthest_32, task_driven_48.
- Held-out families tested: dropout.
- Strategies tested: zero_fill, mask_features, freq_sensor_median_impute, freq_sensor_median_impute_mask.
- Stress cases tested: dropout_10pct, dropout_25pct.
- Total rows: 48.
- All rows pass accuracy >= 0.85: `true`.
- Worst single row: seed `202614`, `geometric_farthest_32` / `zero_fill` / `dropout_25pct` with accuracy `0.867`.
- Best average strategy: `freq_sensor_median_impute` with mean accuracy `1.000`, min accuracy `1.000`, and mean delta vs zero-fill `+0.011`.
- Tightest aggregate row: `geometric_farthest_32` / `zero_fill` / `dropout_25pct`, mean `0.956`, min `0.867`, mean delta vs zero-fill `+0.000`.

## Strategy Summary

| Strategy | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs zero-fill | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| zero_fill | 3 | 12 | 0.989 | 0.867 | 0.964 | 1.000 | +0.000 | true |
| mask_features | 3 | 12 | 0.989 | 0.867 | 0.964 | 1.000 | +0.000 | true |
| freq_sensor_median_impute | 3 | 12 | 1.000 | 1.000 | 1.000 | 1.000 | +0.011 | true |
| freq_sensor_median_impute_mask | 3 | 12 | 1.000 | 1.000 | 1.000 | 1.000 | +0.011 | true |

## Tightest Case Rows

| Candidate | Stress case | Strategy | Mean accuracy | Min accuracy | Mean delta vs zero-fill | Passes 0.85 |
|---|---|---|---:|---:|---:|---|
| geometric_farthest_32 | dropout_25pct | zero_fill | 0.956 | 0.867 | +0.000 | true |
| geometric_farthest_32 | dropout_25pct | mask_features | 0.956 | 0.867 | +0.000 | true |
| geometric_farthest_32 | dropout_10pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| geometric_farthest_32 | dropout_10pct | mask_features | 1.000 | 1.000 | +0.000 | true |
| geometric_farthest_32 | dropout_10pct | freq_sensor_median_impute | 1.000 | 1.000 | +0.000 | true |
| geometric_farthest_32 | dropout_25pct | freq_sensor_median_impute | 1.000 | 1.000 | +0.044 | true |
| geometric_farthest_32 | dropout_10pct | freq_sensor_median_impute_mask | 1.000 | 1.000 | +0.000 | true |
| geometric_farthest_32 | dropout_25pct | freq_sensor_median_impute_mask | 1.000 | 1.000 | +0.044 | true |
| task_driven_48 | dropout_10pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| task_driven_48 | dropout_25pct | zero_fill | 1.000 | 1.000 | +0.000 | true |
| task_driven_48 | dropout_10pct | mask_features | 1.000 | 1.000 | +0.000 | true |
| task_driven_48 | dropout_25pct | mask_features | 1.000 | 1.000 | +0.000 | true |

## Files

| File | Purpose |
|---|---|
| `recognition_dropout_mitigation_metrics.csv` | Per-seed/per-layout/per-strategy stress accuracy and macro-F1. |
| `recognition_dropout_mitigation_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |
| `recognition_dropout_mitigation_by_case.csv` | Aggregate comparison by layout, stress case, and strategy. |
| `recognition_dropout_mitigation_by_layout.csv` | Aggregate comparison by layout and strategy. |
| `recognition_dropout_mitigation_summary.json` | Machine-readable summary, inputs, strategy definitions, and aggregate tables. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_dropout_mitigation.py --layout-candidates geometric_farthest_32,task_driven_48 --held-out-families dropout --strategies zero_fill,mask_features,freq_sensor_median_impute,freq_sensor_median_impute_mask --seeds 202614,202615,202616 --out-dir data\recognition_stress_tests\level2_dropout_mitigation
```

## Boundary

This is a focused Level 2 CST-derived element-library check. It compares
test-time missing-channel handling strategies under internal stochastic
dropout or dropout-bearing compound perturbations. It does not replace
real measurement calibration, full-wave airframe validation, or the true
CST near-field monitor gate.

Zero-valued channels are treated as missing with tolerance `1e-30`.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
