# Level 2 Leave-One-Stress-Family-Out Recognition Test

This directory stores the next G5 robustness check after full
perturbation-aware training. For each run, one stress family is withheld
from augmentation, models train on clean plus the remaining known
families, and the held-out test split is evaluated on the unseen family.

## Current Result

- Layouts tested: 5.
- Held-out families tested: 4.
- Held-out stress cases: 7.
- Total layout/family/stress rows: 35.
- All rows pass accuracy >= 0.85: `true`.
- Worst case: `geometric_farthest_32` / `dropout` / `dropout_25pct` with accuracy `0.867`.
- Minimum delta vs full augmented training: `-0.133`.

## Held-Out Family Summary

| Held-out family | Stress cases | Rows | Mean accuracy | Worst accuracy | Worst row | Passes 0.85 |
|---|---:|---:|---:|---:|---|---|
| noise | 2 | 10 | 1.000 | 1.000 | full_grid_162/noise_20db | true |
| phase | 2 | 10 | 1.000 | 1.000 | full_grid_162/phase_15deg | true |
| dropout | 2 | 10 | 0.973 | 0.867 | geometric_farthest_32/dropout_25pct | true |
| combined | 1 | 5 | 1.000 | 1.000 | full_grid_162/noise10_phase15_dropout10 | true |

## Layout Summary

| Candidate | Sensors | Recommendation | Worst accuracy | Worst case | Passes 0.85 |
|---|---:|---|---:|---|---|
| full_grid_162 | 162 | reference_anchor | 1.000 | noise/noise_20db | true |
| geometric_farthest_32 | 32 | reconstruction_priority | 0.867 | dropout/dropout_25pct | true |
| fibonacci_snap_120 | 120 | conservative_cross_check | 1.000 | noise/noise_20db | true |
| task_driven_32 | 32 | classification_probe | 1.000 | noise/noise_20db | true |
| task_driven_48 | 48 | classification_probe | 0.867 | dropout/dropout_25pct | true |

## Rows Below 0.85

No tested row falls below the `0.85` threshold.

## Training Manifests

| Held-out family | Augmentation cases used in training |
|---|---|
| noise | clean, phase_15deg, phase_45deg, dropout_10pct, dropout_25pct, noise10_phase15_dropout10 |
| phase | clean, noise_20db, noise_10db, dropout_10pct, dropout_25pct, noise10_phase15_dropout10 |
| dropout | clean, noise_20db, noise_10db, phase_15deg, phase_45deg, noise10_phase15_dropout10 |
| combined | clean, noise_20db, noise_10db, phase_15deg, phase_45deg, dropout_10pct, dropout_25pct |

## Files

| File | Purpose |
|---|---|
| `recognition_leave_one_family_metrics.csv` | Per-layout/per-held-out-family recognition accuracy and macro-F1. |
| `recognition_leave_one_family_summary.json` | Machine-readable summary, training manifests, inputs, and model reports. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_leave_one_family_out.py
```

## Boundary

This is a stronger internal generalization check than full augmentation
because each tested family is unseen during augmentation. It is still
Level 2 CST-derived element-library evidence, not real measurement
calibration, full-wave airframe scattering validation, or a replacement
for the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
- clean_baseline: `data\recognition_stress_tests\level2_robustness\recognition_stress_metrics.csv`
- full_augmented_baseline: `data\recognition_stress_tests\level2_augmented_robustness\recognition_augmented_stress_metrics.csv`
