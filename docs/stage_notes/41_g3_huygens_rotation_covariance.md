# S41 G3 Huygens rotation covariance gate

## What Changed

- Added `code/run_cst_huygens_rotation_covariance.py`.
- The script freezes the current real E/H Huygens candidate:
  `eh_love_equivalence_minus_j96`.
- It rotates the measured CST local E/H surface fields as rigid vector fields
  and checks whether the Huygens far-field prediction rotates consistently.
- Refreshed `outputs/g3_model_dashboard/` so the G3 dashboard now has a
  `meshsafe_huygens_rotation_covariance` evidence row.

## Why

S40 selected one frozen real E/H candidate across the current two Level 1 CST
cases. The next risk was implementation geometry: a valid surface-integral
operator should be coordinate-covariant. If the measured local surface and
field vectors are rigidly rotated, the predicted far-field power pattern should
match the unrotated prediction evaluated at inverse-rotated observation
directions.

This gate checks that property before spending more CST time on independent
source-family runs.

## Main Result

Current status:

`rotation_covariance_strict_pass`

| Metric | Value |
|---|---:|
| Base real E/H CST cases | `2` |
| Base cases accepted against CST far field | `2/2` |
| Rigid rotations per case | `9` |
| Covariance tests | `18` |
| Strict covariance passes | `18/18` |
| Minimum covariance correlation | `0.9999999999999998` |
| Maximum covariance scaled power NMSE | `4.038192571773e-29` |
| Maximum covariance normalized absolute error | `2.742250870824e-14` |
| Maximum covariance region-lobe error | `1.207418269726e-06 deg` |

The base CST agreement under the same frozen rule remains:

| Metric | Value |
|---|---:|
| Minimum base CST correlation | `0.9988956628` |
| Maximum base CST scaled power NMSE | `7.303417569845e-04` |
| Maximum base CST region-lobe error | `0 deg` |

## Interpretation

This is a strong implementation sanity check. It shows that the frozen real E/H
Huygens operator behaves correctly under coordinate rotations of the measured
surface data.

It is not a replacement for independent CST source-family validation. The
rotation reference is generated from the unrotated Huygens prediction, not from
new CST solves for x-oriented, y-oriented, tilted, off-axis, or multi-source
cases. The next proof must still use independent CST exports.

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/run_cst_huygens_rotation_covariance.py` | Rotation-covariance stress test for the frozen real E/H Huygens rule. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_covariance_summary.json` | Summary status and headline metrics. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_base_cst_agreement.csv` | Base agreement of the frozen rule against real CST far-field rows. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_covariance_cases.csv` | Per-case, per-rotation covariance metrics. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard now includes `meshsafe_huygens_rotation_covariance`. |

## Validation

```powershell
python -m py_compile code\run_cst_huygens_rotation_covariance.py code\build_g3_model_dashboard.py
python code\run_cst_huygens_rotation_covariance.py
python code\build_g3_model_dashboard.py
```

Key evidence:

- `status = rotation_covariance_strict_pass`
- `covariance_strict_count = 18`
- `covariance_test_count = 18`
- `base_real_cst_accepted_count = 2`
- Dashboard row: `meshsafe_huygens_rotation_covariance`

## Next Step

1. Keep `eh_love_equivalence_minus_j96` frozen.
2. Generate or export independent CST source-family cases: x/y dipoles,
   tilted dipoles, off-axis dipoles, and a small multi-source pilot.
3. Run the same frozen rule on those new exports without per-source retuning.
4. If the rule remains accepted, move the local Huygens operator toward the
   13 m propagation shell and reduced sampling workflow.
