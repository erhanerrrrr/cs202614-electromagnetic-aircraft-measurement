# S44 G3 Huygens source-family solver pilot

## What Changed

- Ran the first real CST solver pilot for the S43 generated source-family
  projects.
- Added `code/build_cst_source_family_solver_status.py` to collect solver
  summary JSON files into an auditable source-family solver status report.
- Prepared the G3 dashboard to distinguish project-generation success from a
  CST solver/runtime settings bottleneck.

## Why

S43 proved that the x/y/off-axis source-family projects can be generated
through the real CST API. The next question was whether the generated projects
can be solved and exported cleanly enough to feed the frozen Huygens rule.

The first pilot shows that CST is not failing at startup or project load. The
solver starts, builds ResultTree probe entries, and reaches CST output logs, but
the default time-domain setup is too slow for the current 600 second automation
timeout.

## Main Result

Current status:

`source_family_solver_pilot_timed_out`

| Metric | Value |
|---|---:|
| Trial summaries found | `1` |
| Timed-out trials | `1` |
| Completed trials | `0` |
| Real CST API used | `true` |
| Solver start OK | `true` |
| Elapsed time | `609.36 s` |
| Timeout setting | `600 s` |
| Poll count | `31` |
| ResultTree count after run | `788` |
| E-field probe ResultTree entries | `770` |
| Max time steps reported by CST | `1457297` |
| Steady-state accuracy limit | `-40 dB` |
| Export artifacts produced | `0` |

Pilot case:

| Field | Sample | Trial project |
|---|---|---|
| E-field | `L1_short_dipole_x_1p2G` | `C:\csttmp\huy_sf_es\L1_short_dipole_x_1p2G_efield.cst` |

## Main Artifacts

| Path | Meaning |
|---|---|
| `outputs/cst_solver_trials/meshsafe_huygens_source_family/L1_short_dipole_x_1p2G_efield_solver_summary.json` | Raw CST solver pilot summary. |
| `code/build_cst_source_family_solver_status.py` | Summarizes source-family solver trial evidence. |
| `outputs/cst_meshsafe_huygens_source_family_solver_status/source_family_solver_status_summary.json` | Machine-readable solver gate status. |
| `outputs/cst_meshsafe_huygens_source_family_solver_status/source_family_solver_trials.csv` | Trial-level audit table. |
| `outputs/cst_meshsafe_huygens_source_family_solver_status/source_family_solver_status.md` | Human-readable solver pilot report. |

## Interpretation

This is a solver gate, not a modeling gate:

- CST project generation is already proven for all 12 E/H source-family
  projects.
- The pilot run starts through the real CST API and creates CST result-tree
  entries.
- The run does not finish cleanly, and no local E/H CSV or far-field reference
  can be exported from this pilot.
- Therefore the frozen Huygens rule still has no independent source-family
  physics proof.

The practical bottleneck is the CST solver setup. The log shows the time-domain
solver using a `-40 dB` steady-state criterion and `1457297` maximum time steps,
which is too expensive for the current automation window.

## Validation

```powershell
python code\build_cst_source_family_solver_status.py
python code\build_g3_model_dashboard.py
```

Expected dashboard status for `meshsafe_huygens_source_family_workpack`:

`source_family_solver_pilot_timed_out`

## Current Boundary

Do not run the remaining 11 source-family solve commands blindly with the same
settings. That would likely consume time without producing export-ready
artifacts.

## Next Step

1. Keep `L1_short_dipole_x_1p2G` as the solver-safe pilot case.
2. Test an adjusted CST solver setup: less expensive time-domain convergence,
   explicit max-step control, or a validated frequency-domain/fast-path
   variant.
3. Only after the pilot produces exportable local E/H probe CSVs and a far-field
   reference, continue to the remaining source-family cases.
4. Then run the frozen Huygens rule `eh_love_equivalence_minus_j96` without
   retuning.
