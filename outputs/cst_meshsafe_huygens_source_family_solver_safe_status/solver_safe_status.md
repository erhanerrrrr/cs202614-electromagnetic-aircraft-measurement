# CST source-family solver-safe status

This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.

## Status

- Stage status: `source_family_solver_safe_reduced_layout_validated`
- Tracked trials: `7`
- Solver-safe ladder trials: `6`
- Supplemental matched-field trials: `1`
- Executed trials: `7`
- Finished trials: `7`
- Timed-out trials: `0`
- Matched E/H ready: `True`
- Matched E/H export ready: `True`
- Matched E/H Huygens validation ready: `True`
- Reduced-layout reconstruction ready: `True`

## Export and Huygens gate

- E-field CSV rows: `288` (data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv)
- H-field CSV rows: `288` (data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_hfield.csv)
- Far-field CSV rows: `2664` (data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv)
- Best real E/H validation: `eh_love_equivalence_minus` / `region_shape_pass`, corr `0.9966187532119293`, scaled NMSE `0.0008179603314047596`, region error deg `0.0`, region Jaccard `0.9440809042236764`
- Frozen j96 validation: `eh_love_equivalence_minus_j96` / `region_shape_pass`, corr `0.9953722660993981`, scaled NMSE `0.001118942244285282`, region error deg `0.0`, region Jaccard `0.9034564958283671`

## Reduced layout reconstruction gate

- Gate status: `reduced_layout_validated`
- Result rows: `25` (data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\reduced_layout_summary.csv)
- Frozen accepted layouts: `13` / `25`
- Deployable frozen accepted layouts: `9`
- Direct-subset frozen accepted layouts: `0`
- Smallest deployable frozen pass: `fibonacci_snap_24` / `poly_reconstruct_full96`, sensors `24`, degree `3`
- Smallest pass metrics: corr `0.9942109460499295`, scaled NMSE `0.0014029945844148`, region Jaccard `0.9095238095238096`, E/H holdout NRMSE `0.041840717963852865` / `0.05781390926075293`

## Trial rows

| Order | Ladder | Mode | Probes | Timeout / s | Status | Elapsed / s | Artifacts | Abort warn |
|---:|---|---|---:|---:|---|---:|---:|---|
| 1 | `none` | `none` | 0 | 240 | `finished` | 78.7 | 3 |  |
| 2 | `efarfield96` | `efarfield` | 96 | 300 | `finished` | 114.0 | 3 |  |
| 3 | `efield24` | `efield` | 24 | 360 | `finished` | 343.4 | 3 |  |
| 4 | `hfield24` | `hfield` | 24 | 360 | `finished` | 333.3 | 3 |  |
| 5 | `efield48` | `efield` | 48 | 1800 | `finished` | 946.5 | 3 | yes |
| 6 | `efield96` | `efield` | 96 | 3600 | `finished` | 3564.2 | 3 |  |
| 7 | `hfield96` | `hfield` | 96 | 5400 | `finished` | 3348.3 | 3 |  |

## Next command

All planned diagnostic rows have a trial summary.

Next gate: short x source-family pilot has completed matched 96-point local E/H CST solves, ResultTree CSV export, CST far-field reference export, frozen E/H Huygens validation, and a sparse reconstruction gate down to a deployable 24-point Fibonacci layout; next apply the same export/reconstruction/frozen-j96 chain to y-oriented and off-axis source-family cases without retuning.

```powershell
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```
