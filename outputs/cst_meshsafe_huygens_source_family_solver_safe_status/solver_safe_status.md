# CST source-family solver-safe status

This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.

## Status

- Stage status: `source_family_solver_safe_matched_eh_finished`
- Tracked trials: `7`
- Solver-safe ladder trials: `6`
- Supplemental matched-field trials: `1`
- Executed trials: `7`
- Finished trials: `7`
- Timed-out trials: `0`
- Matched E/H ready: `True`

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

Next gate: matched 96-point local E/H probe solves are now runtime-feasible on the short x case; next export matched local E/H CSVs and far-field references, then apply the frozen eh_love_equivalence_minus_j96 Huygens rule without retuning.

```powershell
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```
