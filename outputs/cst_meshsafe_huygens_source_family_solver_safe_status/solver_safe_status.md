# CST source-family solver-safe status

This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.

## Status

- Stage status: `source_family_solver_safe_ladder_partial`
- Planned trials: `6`
- Executed trials: `4`
- Finished trials: `4`
- Timed-out trials: `0`

## Trial rows

| Order | Ladder | Mode | Probes | Status | Elapsed / s | Artifacts |
|---:|---|---|---:|---|---:|---:|
| 1 | `none` | `none` | 0 | `finished` | 78.7 | 3 |
| 2 | `efarfield96` | `efarfield` | 96 | `finished` | 114.0 | 3 |
| 3 | `efield24` | `efield` | 24 | `finished` | 343.4 | 3 |
| 4 | `hfield24` | `hfield` | 24 | `finished` | 333.3 | 3 |
| 5 | `efield48` | `efield` | 48 | `not_run` |  | 0 |
| 6 | `efield96` | `efield` | 96 | `not_run` |  | 0 |

## Next command

Next diagnostic row: `efield48`.

```powershell
python code\run_cst_level1_required_automation.py --level1-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_pilot_case.csv --probe-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_probe_48.csv --out-dir C:\csttmp\huy_sf_safe_efield48 --probe-mode efield --timeout-seconds 900
python code\run_cst_solver_project.py --project C:\csttmp\huy_sf_safe_efield48\projects\CST_L1_short_dipole_x_1p2G_meshsafe_huygens_r0p35.cst --out-dir C:\csttmp\huy_sf_safe_efield48_s --trial-name L1_short_dipole_x_1p2G_efield48.cst --summary-out outputs\cst_solver_trials\meshsafe_huygens_source_family_solver_safe\L1_short_dipole_x_1p2G_efield48_solver_summary.json --stdout-log outputs\cst_solver_trials\meshsafe_huygens_source_family_solver_safe\L1_short_dipole_x_1p2G_efield48_stdout.log --timeout-seconds 480 --poll-seconds 10
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```
