# Level 2 Recognition Seed Stability

This directory stores the repeated-seed follow-up for the G5
leave-one-stress-family-out recognition check. The default run repeats
held-out noise and dropout families across three random seeds, varying
the stratified split and the stochastic perturbation draws.

## Current Result

- Seeds: 202614, 202615, 202616.
- Layouts tested: 5.
- Held-out families tested: 2.
- Stress cases tested: 4.
- Total rows: 60.
- All rows pass accuracy >= 0.85: `true`.
- Worst single row: seed `202616`, `geometric_farthest_32` / `dropout` / `dropout_25pct` with accuracy `0.867`.
- Tightest case summary: `geometric_farthest_32` / `dropout` / `dropout_25pct`, mean `0.933`, min `0.867`, 95% CI approx [`0.768`, `1.000`].

## Family Summary

| Held-out family | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---:|---|
| noise | 3 | 30 | 0.998 | 0.933 | 0.993 | 1.000 | true |
| dropout | 3 | 30 | 0.991 | 0.867 | 0.981 | 1.000 | true |

## Tightest Case Rows

| Candidate | Family | Stress case | Seeds | Mean accuracy | Std | Min | 95% CI low | 95% CI high | Passes 0.85 |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| geometric_farthest_32 | dropout | dropout_25pct | 3 | 0.933 | 0.067 | 0.867 | 0.768 | 1.000 | true |
| task_driven_32 | dropout | dropout_25pct | 3 | 0.978 | 0.038 | 0.933 | 0.882 | 1.000 | true |
| task_driven_48 | noise | noise_10db | 3 | 0.978 | 0.038 | 0.933 | 0.882 | 1.000 | true |
| full_grid_162 | dropout | dropout_10pct | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| full_grid_162 | dropout | dropout_25pct | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| geometric_farthest_32 | noise | noise_20db | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| geometric_farthest_32 | noise | noise_10db | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| full_grid_162 | noise | noise_20db | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| geometric_farthest_32 | dropout | dropout_10pct | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |
| fibonacci_snap_120 | noise | noise_20db | 3 | 1.000 | 0.000 | 1.000 | 1.000 | 1.000 | true |

## Layout Summary

| Candidate | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Passes 0.85 |
|---|---:|---:|---:|---:|---:|---:|---|
| full_grid_162 | 3 | 12 | 1.000 | 1.000 | 1.000 | 1.000 | true |
| geometric_farthest_32 | 3 | 12 | 0.983 | 0.867 | 0.957 | 1.000 | true |
| fibonacci_snap_120 | 3 | 12 | 1.000 | 1.000 | 1.000 | 1.000 | true |
| task_driven_32 | 3 | 12 | 0.994 | 0.933 | 0.982 | 1.000 | true |
| task_driven_48 | 3 | 12 | 0.994 | 0.933 | 0.982 | 1.000 | true |

## Files

| File | Purpose |
|---|---|
| `recognition_seed_stability_metrics.csv` | Per-seed/per-layout/per-stress accuracy and macro-F1. |
| `recognition_seed_stability_by_case.csv` | Aggregated mean/std/min/95% CI by layout and stress case. |
| `recognition_seed_stability_by_family.csv` | Aggregated stability by held-out family. |
| `recognition_seed_stability_by_layout.csv` | Aggregated stability by layout. |
| `recognition_seed_stability_summary.json` | Machine-readable summary, inputs, and aggregate tables. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_seed_stability.py
```

## Boundary

This is still Level 2 CST-derived element-library evidence. It improves
the statistical confidence of the internal perturbation checks, but it
does not replace real measurement calibration, full-wave airframe
validation, or the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
