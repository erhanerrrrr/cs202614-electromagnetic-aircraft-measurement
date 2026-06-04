# S38 G3 mesh-safe Huygens full H-field coverage

## What Changed

- Solved the `L1_halfwave_dipole_z_1p2G` mesh-safe H-field CST project through
  the short-path solver gate.
- Exported the half-wave local H-field ResultTree probe CSV:
  `data/cst_exports/level1_meshsafe_huygens/L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv`.
- Added a sample-id inference guard to `code/export_cst_meshsafe_huygens_results.py`
  so a project path such as `h_halfwave_hfield.cst` maps to the half-wave sample
  instead of silently defaulting to the short-dipole target.
- Added vector-gate statistics to `code/run_cst_meshsafe_huygens_extrapolation.py`
  so batch reports distinguish "best branch uses the scalar proxy" from "real
  E/H candidates are accepted."
- Refreshed the G3 dashboard wording: CST export is no longer the mesh-safe
  Huygens blocker; operator calibration is.

## Why

S37 proved that the short-dipole real E/H route works, but the half-wave H-field
row was still missing. That made the dashboard sound as if the current problem
was still H-field export coverage. After this stage, both Level 1 mesh-safe
sources have matched local E/H probe CSVs, so the remaining issue is the
Huygens/Love-equivalence operator calibration against the CST far-field
reference.

## Main Artifacts

| Path | Meaning |
|---|---|
| `data/cst_exports/level1_meshsafe_huygens/L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` | Real CST local H-field probe export, `96 * 3 = 288` rows. |
| `outputs/cst_solver_trials/meshsafe_huygens_required_shortpath/h_halfwave_hfield_solver_summary.json` | Local solver evidence; CST finished successfully and preserved `.m3d/.ffm/.fme` results. |
| `code/export_cst_meshsafe_huygens_results.py` | Now infers sample id from project path when `--sample-id` is omitted and refuses ambiguous matches. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `vector_gate` summary fields and batch counts for accepted real-H and real E/H candidates. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | Two-case batch gate refreshed with `hfield=2/2` and `real_eh_accepted=2/2`. |
| `outputs/g3_model_dashboard/` | Dashboard refreshed with the updated interpretation and next action. |

## Validation

```powershell
python -m py_compile code\export_cst_meshsafe_huygens_results.py code\run_cst_meshsafe_huygens_extrapolation.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
python code\export_cst_meshsafe_huygens_results.py --field-kind h --project C:\csttmp\huy_hs\h_halfwave_hfield.cst
```

Current result:

- CST H-field solve for the half-wave case finished successfully.
- The half-wave H-field CSV contains the expected `288` contract rows.
- The export controller inferred `sample_id = L1_halfwave_dipole_z_1p2G`
  from `C:\csttmp\huy_hs\h_halfwave_hfield.cst` without an explicit
  `--sample-id`.
- Batch gate completes `2/2` cases, with `2/2` H-field loaded.
- Real E/H candidates are accepted for `2/2` cases; both best real E/H
  candidates are `eh_love_equivalence_minus / region_shape_pass`.
- The overall best branch is still the scalar impedance proxy
  `outgoing_equivalence_minus_eta0p25` for `2/2` cases, so the real E/H branch
  is accepted but not yet the top-ranked calibrated operator.

## Current Interpretation

CST is running normally for this mesh-safe route. The remaining blocker is not
solver execution, project opening, or ResultTree export. It is the algorithmic
physics closure: the simplified Love-equivalence surface-current operator needs
normalization, sign-convention, and broader source-family calibration before it
can replace the scalar `eta_eff` proxy in report-level wording.

## Next Step

1. Calibrate the real E/H Love-equivalence operator against the two Level 1 CST
   far-field references.
2. Rerun the impedance/stability gate through the accepted real E/H branch,
   keeping scalar `eta_eff` as a transparent proxy baseline.
3. Propagate the accepted local Huygens prediction toward the 13 m measurement
   shell, then evaluate reduced sampling layouts on that propagated field.
