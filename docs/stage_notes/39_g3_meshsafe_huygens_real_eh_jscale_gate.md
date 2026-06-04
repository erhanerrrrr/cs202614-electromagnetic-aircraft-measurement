# S39 G3 mesh-safe Huygens real E/H J-scale gate

## What Changed

- Added a real E/H `J = n x H_t` global scale scan to
  `code/run_cst_meshsafe_huygens_extrapolation.py`.
- Kept the unscaled `J = n x H_t`, `M = -n x E_t` Love-equivalence branch as
  the `real_eh_surface_currents` baseline.
- Added calibrated `real_eh_j_scale_scan` variants that retain the measured CST
  H-field distribution and only change the global electric-current
  normalization.
- Extended the batch summary with a real E/H operator-stability status:
  `real_eh_operator_calibration_status`.
- Refreshed the G3 dashboard so the mesh-safe Huygens line now reports
  `real_eh_strict_batch_calibration_needed` instead of a scalar-proxy bottleneck.

## Why

S38 completed Level 1 H-field coverage and showed that real E/H candidates were
accepted, but the overall best branches still used the scalar `eta_eff` proxy.
The next useful gate was to test whether the real CST H-field current pattern
could become the best branch after a controlled operator-normalization scan.

## Main Result

The default two-case batch now completes with:

- `2/2` cases completed.
- `2/2` cases with real H-field loaded.
- `2/2` best branches using real H-field currents.
- `2/2` best branches reaching `strict_pass`.
- `0/2` best branches using non-eta0 scalar impedance.

Best branches:

| Sample | Best branch | Status | J scale | Scaled power NMSE |
|---|---|---|---:|---:|
| `L1_halfwave_dipole_z_1p2G` | `eh_love_equivalence_minus_j96` | `strict_pass` | `96.0` | `7.131984e-04` |
| `L1_short_dipole_z_1p2G` | `eh_love_equivalence_plus_j256` | `strict_pass` | `256.0` | `9.953152e-04` |

The scan no longer hits the configured upper boundary. The best J-scale values
are `96.0` and `256.0`, giving a cross-case ratio of `2.6667`. The best
plus/minus convention is also source-dependent. Therefore the new status is:

`cross_case_sign_and_scale_disagreement`

## Interpretation

This is a real step forward: the mesh-safe Huygens best branches now use
measured CST E/H currents rather than the scalar impedance proxy. However, this
is not yet a final source-independent Huygens operator. The current evidence
says the real E/H route is capable, but the J-scale normalization and magnetic
current sign convention need a source-family rule or a broader stability test
before propagating the operator to the 13 m measurement shell.

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `--eh-j-scale-factors`, calibrated real E/H variants, and cross-case stability summary fields. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.csv` | Batch table showing both best branches are real E/H `strict_pass`. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | Machine-readable operator-stability status and best J-scale values. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard row for `meshsafe_huygens_real_cst_batch` now reports `real_eh_strict_batch_calibration_needed`. |
| `outputs/g3_model_dashboard/g3_next_actions.csv` | Priority 1 now targets cross-source real E/H J-scale/sign stability. |

## Validation

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

Key evidence:

- `completed 2/2 cases; strict_or_proxy=2; ... hfield=2; real_eh_accepted=2; best_real_hfield=2`
- `real_eh_operator_calibration_status = cross_case_sign_and_scale_disagreement`
- `best_real_eh_j_scale_values = [96.0, 256.0]`
- `case_count_best_real_eh_j_scale_boundary = 0`

## Next Step

1. Add a broader source-family test case or derive a geometry-aware sign/scale
   rule for the current two source types.
2. Re-run the real E/H gate with that rule frozen, not selected independently
   per source.
3. Only after that stability gate passes, propagate the accepted local Huygens
   operator to the 13 m measurement shell and reduced sampling layouts.
