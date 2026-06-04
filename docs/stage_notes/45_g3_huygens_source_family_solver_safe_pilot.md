# S45 G3 Huygens Source-Family Solver-Safe Pilot

## What Changed

- Added a solver-safe diagnostic ladder for the first source-family CST solver timeout.
- Kept the target fixed to `L1_short_dipole_x_1p2G` so the next CST runs isolate runtime behavior rather than changing the physics case.
- Split the next execution into six ordered gates: `none`, `efarfield96`, `efield24`, `hfield24`, `efield48`, and `efield96`.
- Added a status builder so the G3 dashboard can distinguish plan-ready, partially executed, timed-out, and full-pilot-finished states.

## Why

The previous S44 solver pilot proved that CST can open the generated source-family project, start the solver through the real CST API, and populate ResultTree probe entries. It did not finish export inside the 600 s timeout. The new workpack avoids treating that as a generic CST failure. It asks a narrower question: whether the timeout comes from the base solve, far-field monitor/probe setup, or local Cartesian Huygens probe count.

## Main Artifacts

| File/directory | Meaning | Use |
|---|---|---|
| `code/prepare_cst_source_family_solver_safe_pilot.py` | Generates the one-case solver-safe diagnostic workpack. | Run before executing the CST ladder. |
| `code/build_cst_source_family_solver_safe_status.py` | Summarizes ladder execution results. | Run after each diagnostic trial. |
| `data/cst_meshsafe_huygens_source_family_solver_safe_pilot/` | One-case input CSVs, probe subsets, command queue, README, and plan summary. | Main operator handoff for the next CST solver trials. |
| `outputs/cst_meshsafe_huygens_source_family_solver_safe_status/` | Status summary, trial table, and Markdown report. | Evidence consumed by the G3 dashboard. |
| `outputs/g3_model_dashboard/` | Dashboard now has a separate `meshsafe_huygens_source_family_solver_safe_pilot` row. | Use for current source-family gate status. |

## Verification

```powershell
python -m py_compile code\prepare_cst_source_family_solver_safe_pilot.py code\build_cst_source_family_solver_safe_status.py code\build_g3_model_dashboard.py
python code\prepare_cst_source_family_solver_safe_pilot.py
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

Current status:

- `source_family_solver_safe_ladder_partial`.
- Planned diagnostic trials: `6`.
- Executed diagnostic trials: `4`.
- Finished diagnostic trials: `4`.
- Timed-out diagnostic trials: `0`.
- Completed rows: `none` in `78.7 s`, `efarfield96` in `114.0 s`, `efield24` in `343.4 s`, and `hfield24` in `333.3 s`.
- G3 dashboard now keeps the S44 timeout row and adds a separate S45 solver-safe plan row.

## Current Limits

- The 48-probe and 96-probe local E-field rows have not been executed yet.
- This is not a frozen-rule Huygens physics pass; matched local E/H CSV and far-field references are still required.
- The full 96-probe E-field retry should only run after the cheaper ladder rows have given a clear runtime signal.

## Next Step

1. Run the `efield48` ladder row from `solver_safe_status.md`.
2. Rebuild `solver_safe_status_summary.json` and the G3 dashboard.
3. If `efield48` finishes within the timeout, decide whether to attempt `efield96` or first tune probe export/runtime settings.
4. Stop at the first repeated timeout and decide whether to tune CST solver settings, switch to a validated frequency-domain path, or split export responsibilities.
