# Recognition Stress Tests

This directory stores small, versionable robustness summaries for the
classification/recognition branch. Large CST near-field source tables remain in
`data/cst_exports/` and are ignored by default.

## Subdirectories

| Directory | Purpose |
|---|---|
| `level2_robustness/` | Clean-train/perturbed-test Level 2 recognition stress test for selected G2 layouts. |
| `level2_augmented_robustness/` | Perturbation-aware training follow-up on the same layouts, split, and stress cases. |
| `level2_leave_one_family_out/` | Leave-one-stress-family-out generalization check for unseen noise/phase/dropout/combined families. |
| `level2_seed_stability/` | Repeated-seed stability check for focused leave-one-family noise/dropout perturbations. |
| `level2_dropout_mitigation/` | Focused missing-channel strategy comparison for the tightest held-out dropout layouts. |

## Regenerate

```powershell
python code\run_cst_recognition_stress_test.py
python code\run_cst_recognition_augmented_stress_test.py
python code\run_cst_recognition_leave_one_family_out.py
python code\run_cst_recognition_seed_stability.py
python code\run_cst_recognition_dropout_mitigation.py
```

`level2_robustness/` should be read first because it exposes the clean-train
boundary under compound measurement errors. `level2_augmented_robustness/`
then checks whether the same held-out cases recover when the known
noise/phase/dropout perturbation families are included in training.
`level2_leave_one_family_out/` is the stricter follow-up: it hides one stress
family during augmentation and tests that unseen family. Current result: all
rows remain above `0.85`, but held-out `dropout_25pct` is the tightest margin
at about `0.867` for two layouts. `level2_seed_stability/` repeats the focused
noise/dropout version of that check across three seeds; all 60 rows pass
`0.85`, and `geometric_farthest_32/dropout_25pct` remains the tightest case
with mean accuracy about `0.933` and minimum accuracy about `0.867`.
`level2_dropout_mitigation/` compares zero-fill with missing-mask features and
frequency/sensor median imputation on the two tightest layouts. Current result:
all 48 rows pass `0.85`; mask features alone match zero-fill, while median
imputation raises the tightest `geometric_farthest_32/dropout_25pct` aggregate
from mean accuracy about `0.956` and minimum `0.867` to mean/min `1.000`.

## Boundary

These results are recognition robustness evidence. They do not replace the
true CST near-field monitor gate used for reduced-layout reconstruction claims,
and they do not prove full-wave complex-airframe scattering generalization. The
augmented result proves recovery for known perturbation profiles in the current
Level 2 CST-derived element-library setting, not for arbitrary future
measurement or installation errors. The leave-one-family result is stronger
than full augmentation but is still an internal perturbation-family check, not
real instrument calibration. The seed-stability result reduces dependence on a
single random split/draw, but it is still small-sample internal evidence. The
dropout-mitigation result is a candidate preprocessing/calibration step for
missing channels, not proof that arbitrary sensor failures or real instruments
are covered.
