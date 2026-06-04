# CST Huygens Source-Family Solver Pilot Status

This report records the first real CST solver pilot for the independent source-family workpack.

## Status

- Stage status: `source_family_solver_pilot_timed_out`
- Trial summaries found: `1`
- Timed-out trials: `1`
- Completed trials: `0`
- Solver starts OK: `1/1`

The current evidence shows a CST runtime/settings bottleneck, not a CST project-generation failure. The pilot started through the real CST API and populated ResultTree probe entries, but it did not finish cleanly enough to export matched local E/H CSVs or far-field references.

## Trial Rows

| Sample | Field | Status | Elapsed / s | Timeout / s | Probe results | Max time steps | Artifact count |
|---|---|---|---:|---:|---:|---:|---:|
| `L1_short_dipole_x_1p2G` | `efield` | `timed_out` | 609.36 | 600 | 770 | 1457297 | 0 |

## Next Gate

Build a solver-safe pilot before running the full 12-project queue. The immediate target is the same short x-oriented case with adjusted CST solver settings or a frequency-domain/fast-path variant, followed by ResultTree export validation.

## Regenerate

```powershell
python code\build_cst_source_family_solver_status.py
```
