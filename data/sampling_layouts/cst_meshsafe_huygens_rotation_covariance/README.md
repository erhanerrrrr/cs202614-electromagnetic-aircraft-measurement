# CST Huygens rotation covariance gate

This folder records a coordinate-covariance stress test for the frozen real E/H
mesh-safe Huygens rule.

## Scope

- Frozen rule: `eh_love_equivalence_minus_j96`
- Real CST base cases: `2`
- Rotations per case: `9`
- Covariance tests: `18`
- Status: `rotation_covariance_strict_pass`

The test rotates the measured local CST E/H surface fields and the local
Huygens sphere geometry, then compares the rotated prediction against the
unrotated prediction evaluated at inverse-rotated far-field directions. This
checks whether the Python Huygens operator is tied to a physical vector rule
rather than an accidental global coordinate convention.

## Rotations

`identity, yaw_z_45, yaw_z_90, yaw_z_180, pitch_y_30, pitch_y_60, roll_x_45, roll_x_90, compound_z45_y30`

## Results

- Covariance strict count: `18/18`
- Covariance pass count: `18/18`
- Minimum covariance correlation: `1`
- Maximum covariance scaled power NMSE: `4.03819257177e-29`
- Maximum covariance normalized absolute error: `2.74225087082e-14`
- Base real-CST accepted cases: `2/2`

## Files

| File | Meaning |
|---|---|
| `huygens_rotation_base_cst_agreement.csv` | Fixed-rule agreement against real CST far-field references before synthetic rotations. |
| `huygens_rotation_covariance_cases.csv` | Per-case/per-rotation covariance rows. |
| `huygens_rotation_covariance_summary.json` | Machine-readable summary for the G3 dashboard. |

## Reading

This is operator evidence, not new CST source-family evidence. A pass means the
frozen sign/J-scale rule behaves consistently when the measured vector fields
and surface geometry are rigidly rotated. The next proof step is still to run
or ingest real CST source-family exports, such as x/y-oriented, tilted,
off-axis, or multi-source Level 1 cases.

## Regenerate

```powershell
python code\run_cst_huygens_rotation_covariance.py
```
