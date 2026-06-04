# CST source-family solver-safe status

This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.

## Status

- Stage status: `source_family_solver_safe_full_efield_finished`
- Planned trials: `6`
- Executed trials: `6`
- Finished trials: `6`
- Timed-out trials: `0`

## Trial rows

| Order | Ladder | Mode | Probes | Timeout / s | Status | Elapsed / s | Artifacts | Abort warn |
|---:|---|---|---:|---:|---|---:|---:|---|
| 1 | `none` | `none` | 0 | 240 | `finished` | 78.7 | 3 |  |
| 2 | `efarfield96` | `efarfield` | 96 | 300 | `finished` | 114.0 | 3 |  |
| 3 | `efield24` | `efield` | 24 | 360 | `finished` | 343.4 | 3 |  |
| 4 | `hfield24` | `hfield` | 24 | 360 | `finished` | 333.3 | 3 |  |
| 5 | `efield48` | `efield` | 48 | 1800 | `finished` | 946.5 | 3 | yes |
| 6 | `efield96` | `efield` | 96 | 3600 | `finished` | 3564.2 | 3 |  |

## Next command

All planned diagnostic rows have a trial summary.

Next gate: full local E-field probe solve is now runtime-feasible on the short x case; next run a matching long-window H-field pilot for the same sample, then export matched E/H and far-field references before applying the frozen Huygens rule.

```powershell
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```
