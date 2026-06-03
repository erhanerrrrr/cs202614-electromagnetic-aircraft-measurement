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
| `level2_dropout_mitigation_extended/` | Extended missing-channel strategy comparison across all five G2 layouts and dropout-bearing stress families. |
| `level2_structured_dropout/` | Structured missing-channel check for unseen sensor-node, polarization-pair, and angular-sector dropout patterns. |
| `level2_instrument_error/` | Correlated instrument calibration error check for gain drift, sensor bias, frequency slope, polarization imbalance, and mixed amp/phase bias. |

## Regenerate

```powershell
python code\run_cst_recognition_stress_test.py
python code\run_cst_recognition_augmented_stress_test.py
python code\run_cst_recognition_leave_one_family_out.py
python code\run_cst_recognition_seed_stability.py
python code\run_cst_recognition_dropout_mitigation.py
python code\run_cst_recognition_dropout_mitigation.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --held-out-families dropout,combined --out-dir data\recognition_stress_tests\level2_dropout_mitigation_extended
python code\run_cst_recognition_structured_dropout.py
python code\run_cst_recognition_instrument_error.py
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
`level2_dropout_mitigation_extended/` broadens the same strategy comparison to
all five G2 representative layouts and to held-out `dropout` plus `combined`
families. Current result: all 180 rows pass `0.85`; zero-fill and mask-only
both bottom at `0.867`, mask-only can be worse than zero-fill on one
`full_grid_162/dropout_25pct` aggregate, and both frequency/sensor median
imputation variants reach mean/min accuracy `1.000`.
`level2_structured_dropout/` then tests whether that missing-channel conclusion
survives unseen structured patterns: dropping whole sensor nodes, both
polarizations for selected sensor-frequency pairs, and contiguous 60 deg
azimuth sectors. Current result: all 240 rows pass `0.85`; the lowest accuracy
is `0.933`, and both frequency/sensor median imputation variants reach mean/min
accuracy `1.000`.
`level2_instrument_error/` tests a different error family: correlated
instrument calibration bias without zeroing channels. It compares clean-train
and known-perturbation-augmented profiles under global gain drift, per-sensor
gain bias, frequency-response slope, polarization gain imbalance, and mixed
amplitude/phase bias. Current result: all 150 rows pass `0.85`; the tightest
case is `geometric_farthest_32/sensor_gain_bias_3db` with minimum accuracy
`0.933`, and both training profiles have mean accuracy about `0.999`.

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
are covered. The extended mitigation result makes imputation-only the cleaner
current candidate than mask-only features, and the structured-dropout result
checks more realistic missing patterns, but both are still bounded to internal
simulated dropout-bearing perturbations. The instrument-error result adds
correlated calibration-bias evidence, but it is still simulated Level 2
CST-derived evidence, not real measurement calibration.
