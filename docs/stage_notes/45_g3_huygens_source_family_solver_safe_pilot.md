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

- `source_family_solver_safe_full_efield_finished`.
- Planned diagnostic trials: `6`.
- Executed diagnostic trials: `6`.
- Finished diagnostic trials: `6`.
- Timed-out diagnostic trials: `0`.
- Completed rows: `none` in `78.7 s`, `efarfield96` in `114.0 s`, `efield24` in `343.4 s`, `hfield24` in `333.3 s`, `efield48` in `946.5 s`, and `efield96` in `3564.2 s`.
- The `efield48` retry wrote the expected artifacts but carried an `aborted_keeping_results` warning; the full `efield96` row completed cleanly with far-field and near-field artifacts.
- G3 dashboard now keeps the S44 timeout row and adds a separate S45 solver-safe row with full E-field completion.

## Current Limits

- This is not a frozen-rule Huygens physics pass; matched local E/H CSV and far-field references are still required.
- The current evidence proves that full local E-field probes are runtime-feasible for the short x case, but the matched 96-point H-field case still needs a long-window pilot before expanding the full source-family queue.
- The first successful full E-field run needed about 56 minutes, so future full-probe CST runs need a wider controller timeout than the original 600-second wrapper.

## Next Step

1. Add a matching long-window `hfield96` pilot for `L1_short_dipole_x_1p2G`.
2. Export matched local E/H data plus far-field references from the successful short x case.
3. Apply the frozen `eh_love_equivalence_minus_j96` Huygens rule without retuning.
4. Only after the matched E/H gate passes, expand from the short x pilot to the remaining source-family cases.
