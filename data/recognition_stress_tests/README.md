# Recognition Stress Tests

This directory stores small, versionable robustness summaries for the
classification/recognition branch. Large CST near-field source tables remain in
`data/cst_exports/` and are ignored by default.

## Subdirectories

| Directory | Purpose |
|---|---|
| `level2_robustness/` | Clean-train/perturbed-test Level 2 recognition stress test for selected G2 layouts. |
| `level2_augmented_robustness/` | Perturbation-aware training follow-up on the same layouts, split, and stress cases. |

## Regenerate

```powershell
python code\run_cst_recognition_stress_test.py
python code\run_cst_recognition_augmented_stress_test.py
```

`level2_robustness/` should be read first because it exposes the clean-train
boundary under compound measurement errors. `level2_augmented_robustness/`
then checks whether the same held-out cases recover when the known
noise/phase/dropout perturbation families are included in training.

## Boundary

These results are recognition robustness evidence. They do not replace the
true CST near-field monitor gate used for reduced-layout reconstruction claims,
and they do not prove full-wave complex-airframe scattering generalization. The
augmented result proves recovery for known perturbation profiles in the current
Level 2 CST-derived element-library setting, not for arbitrary future
measurement or installation errors.
