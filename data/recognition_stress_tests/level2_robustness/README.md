# Level 2 Recognition Stress Test

This directory stores the G5 robustness check for the current Level 2
CST-derived recognition pipeline. Models are trained on clean training
samples and evaluated on clean or perturbed held-out samples.

## Current Result

- Layouts tested: 5.
- Stress cases per layout: 8.
- All rows pass accuracy >= 0.85: `false`.
- Worst case: `full_grid_162` / `noise10_phase15_dropout10` with accuracy `0.467`.

## Layout Summary

| Candidate | Sensors | Recommendation | Clean accuracy | Worst accuracy | Worst case | Passes 0.85 |
|---|---:|---|---:|---:|---|---|
| full_grid_162 | 162 | reference_anchor | 1.000 | 0.467 | noise10_phase15_dropout10 | false |
| geometric_farthest_32 | 32 | reconstruction_priority | 1.000 | 0.800 | noise10_phase15_dropout10 | false |
| fibonacci_snap_120 | 120 | conservative_cross_check | 1.000 | 0.800 | noise10_phase15_dropout10 | false |
| task_driven_32 | 32 | classification_probe | 1.000 | 0.667 | noise10_phase15_dropout10 | false |
| task_driven_48 | 48 | classification_probe | 1.000 | 0.533 | noise10_phase15_dropout10 | false |

## Rows Below 0.85

| Candidate | Stress case | Accuracy | Macro-F1 | Best model |
|---|---|---:|---:|---|
| full_grid_162 | noise10_phase15_dropout10 | 0.467 | 0.357 | random_forest |
| task_driven_48 | noise10_phase15_dropout10 | 0.533 | 0.496 | random_forest |
| task_driven_32 | noise10_phase15_dropout10 | 0.667 | 0.684 | random_forest |
| task_driven_32 | dropout_25pct | 0.733 | 0.722 | random_forest |
| geometric_farthest_32 | noise10_phase15_dropout10 | 0.800 | 0.791 | random_forest |
| fibonacci_snap_120 | noise10_phase15_dropout10 | 0.800 | 0.798 | random_forest |
| task_driven_48 | dropout_25pct | 0.800 | 0.764 | random_forest |

## Files

| File | Purpose |
|---|---|
| `recognition_stress_metrics.csv` | Per-layout/per-stress accuracy and macro-F1 for clean-trained models. |
| `recognition_stress_summary.json` | Machine-readable summary, inputs, and layout-level worst cases. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_stress_test.py
```

## Boundary

This is a Level 2 CST-derived element-library robustness check. It
strengthens the recognition/generalization evidence, but it is not a
full-wave complex-airframe scattering validation and does not replace the
true CST near-field monitor gate used for reduced-layout reconstruction
claims.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
