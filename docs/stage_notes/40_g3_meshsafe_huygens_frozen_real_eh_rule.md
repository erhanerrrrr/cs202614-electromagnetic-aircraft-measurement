# S40 G3 mesh-safe Huygens frozen real E/H rule gate

## What Changed

- Added a frozen real E/H rule gate to
  `code/run_cst_meshsafe_huygens_extrapolation.py`.
- The gate ranks each single `eh_love_equivalence_{plus/minus}_jX` candidate
  under a stricter rule: the same plus/minus convention and the same J-scale
  must be used for every completed Level 1 case.
- Added two batch artifacts:
  - `meshsafe_huygens_frozen_real_eh_rule_summary.csv`
  - `meshsafe_huygens_frozen_real_eh_rule_cases.csv`
- Refreshed the G3 dashboard so the mesh-safe Huygens row now reports
  `real_eh_frozen_rule_region_pass`.

## Why

S39 proved that the best diagnostic branches can use measured CST E/H currents,
but the per-case best choices still disagreed: the half-wave case preferred a
minus-sign branch with `J = 96`, while the short-dipole case preferred a
plus-sign branch with `J = 256`. That was a source-by-source calibration risk.

S40 asks a stricter question: if the operator is frozen before looking at the
individual source, is there still a real E/H candidate that covers the current
Level 1 batch?

## Main Result

The best frozen candidate is:

`eh_love_equivalence_minus_j96`

It uses the same sign convention and the same `J = 96 * (n x H_t)` global
normalization for both Level 1 cases.

| Metric | Value |
|---|---:|
| Present cases | `2/2` |
| Accepted cases | `2/2` |
| Strict cases | `1/2` |
| Worst status | `region_shape_pass` |
| Minimum correlation | `0.9988956628` |
| Maximum scaled power NMSE | `7.303417569844e-04` |
| Maximum main-lobe region error | `0 deg` |

Per-case rows for the frozen rule:

| Sample | Frozen rule status | Correlation | Scaled power NMSE |
|---|---|---:|---:|
| `L1_halfwave_dipole_z_1p2G` | `strict_pass` | `0.9990868550` | `7.131984075472e-04` |
| `L1_short_dipole_z_1p2G` | `region_shape_pass` | `0.9988956628` | `7.303417569844e-04` |

## Interpretation

This is a stronger gate than S39. The current Level 1 mesh-safe Huygens evidence
no longer requires each source to choose its own sign/J-scale candidate in order
to obtain an accepted real E/H pass. A single frozen candidate covers both
cases with high pattern correlation and low scale-fitted NMSE.

It is still not final report-level physics proof. The frozen candidate must now
be explained as a geometry/physics rule and tested on a broader CST source
family before propagating it to the 13 m measurement shell.

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds the frozen real E/H rule aggregation. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_frozen_real_eh_rule_summary.csv` | Ranked global frozen real E/H candidates. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_frozen_real_eh_rule_cases.csv` | Per-case rows for the selected frozen candidate. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | Batch summary with `frozen_real_eh_rule_status`. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard status now reports `real_eh_frozen_rule_region_pass`. |

## Validation

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

Key evidence:

- `frozen_real_eh_rule_status = frozen_real_eh_mixed_strict_region_pass`
- `frozen_real_eh_best_rule.variant = eh_love_equivalence_minus_j96`
- `accepted_case_count = 2`
- `strict_case_count = 1`
- Dashboard status: `real_eh_frozen_rule_region_pass`

## Next Step

1. Promote `eh_love_equivalence_minus_j96` from a frozen diagnostic candidate
   into an explicit geometry/physics rule.
2. Add or reuse a broader Level 1 source-family set to test whether the frozen
   sign/J-scale rule remains accepted.
3. After that validation, propagate the accepted local Huygens operator toward
   the 13 m measurement shell and reduced sampling layouts.
