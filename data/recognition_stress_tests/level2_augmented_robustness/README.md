# Level 2 Augmented Recognition Stress Test

This directory stores the perturbation-aware training follow-up to the
clean-train Level 2 stress test. The held-out test split and stress cases
are unchanged; only the training set is expanded with clean, noise, phase
jitter, dropout, and combined perturbation variants of the training samples.

## Current Result

- Layouts tested: 5.
- Stress cases per layout: 8.
- Augmentation profiles per layout: 8.
- All rows pass accuracy >= 0.85: `true`.
- Worst case: `full_grid_162` / `clean` with accuracy `1.000`.
- Mean accuracy delta vs clean-train baseline: `+0.060`.

## Layout Summary

| Candidate | Sensors | Recommendation | Clean accuracy | Worst accuracy | Worst case | Passes 0.85 |
|---|---:|---|---:|---:|---|---|
| full_grid_162 | 162 | reference_anchor | 1.000 | 1.000 | clean | true |
| geometric_farthest_32 | 32 | reconstruction_priority | 1.000 | 1.000 | clean | true |
| fibonacci_snap_120 | 120 | conservative_cross_check | 1.000 | 1.000 | clean | true |
| task_driven_32 | 32 | classification_probe | 1.000 | 1.000 | clean | true |
| task_driven_48 | 48 | classification_probe | 1.000 | 1.000 | clean | true |

## Rows Below 0.85

No tested row falls below the `0.85` threshold.

## Files

| File | Purpose |
|---|---|
| `recognition_augmented_stress_metrics.csv` | Per-layout/per-stress accuracy and macro-F1 after perturbation-aware training. |
| `recognition_augmented_stress_summary.json` | Machine-readable summary, inputs, augmentation profiles, and detailed model reports. |
| `README.md` | Human-facing interpretation and claim boundary. |

## Regenerate

```powershell
python code\run_cst_recognition_augmented_stress_test.py
```

## Boundary

This is an augmentation experiment on Level 2 CST-derived element-library
data. It is evidence that compound measurement-error sensitivity can be
reduced by perturbation-aware training. It is not full-wave complex-airframe
validation and does not replace the true CST near-field monitor gate.

## Inputs

- nearfield: `data\cst_exports\level2\all_nearfield.csv`
- labels: `outputs\cst_level2_plan\level2_labels.csv`
- layouts: `data\sampling_layouts\hemisphere_sampling_candidates.csv`
- decision_matrix: `data\sampling_layouts\sampling_decision_matrix\sampling_decision_matrix.csv`
- clean_baseline: `data\recognition_stress_tests\level2_robustness\recognition_stress_metrics.csv`
