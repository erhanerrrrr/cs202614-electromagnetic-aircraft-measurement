# S46 G3 Huygens Source-Family Matched E/H Pilot

## What Changed

- Completed the matching `hfield96` long-window CST pilot for `L1_short_dipole_x_1p2G`.
- Extended the solver-safe status builder with the supplemental `hfield96` row.
- Promoted the current solver-safe stage to `source_family_solver_safe_matched_eh_finished`.
- Refreshed the G3 dashboard so the active CST gate is now matched ResultTree CSV export and frozen-rule validation, not solver-runtime repair.

## Why

S45 proved that the full 96-point local E-field probe solve is runtime-feasible on the short x source-family case, but it still lacked the matched 96-point H-field pilot required for a real E/H Huygens validation. S46 closes that runtime gap.

The original 600 s timeout is now historical evidence of an undersized controller window, not evidence that CST cannot run the case.

## Main Artifacts

| File/directory | Meaning | Use |
|---|---|---|
| `outputs/cst_solver_trials/meshsafe_huygens_source_family_solver_safe/L1_short_dipole_x_1p2G_hfield96_solver_summary.json` | Raw CST solver summary for the matched H-field pilot. | Machine-readable evidence that `hfield96` finished. |
| `outputs/cst_solver_trials/meshsafe_huygens_source_family_solver_safe/L1_short_dipole_x_1p2G_hfield96_stdout.log` | Controller stdout log for the H-field pilot. | Runtime audit trail. |
| `outputs/cst_meshsafe_huygens_source_family_solver_safe_status/` | Refreshed seven-row solver-safe status table and Markdown report. | Current source-family solver-safe status. |
| `outputs/g3_model_dashboard/` | Refreshed G3 dashboard. | Current project-level next action matrix. |

Local CST result cache, intentionally outside Git:

| Local path | Meaning |
|---|---|
| `C:\csttmp\huy_sf_safe_hfield96_s\L1_short_dipole_x_1p2G_hfield96\Result\farfield_1200MHz_1.ffm` | H-field pilot far-field monitor artifact, `23003` bytes. |
| `C:\csttmp\huy_sf_safe_hfield96_s\L1_short_dipole_x_1p2G_hfield96\Result\farfield_1200MHz_1.fme` | H-field pilot far-field metadata artifact, `57592` bytes. |
| `C:\csttmp\huy_sf_safe_hfield96_s\L1_short_dipole_x_1p2G_hfield96\Result\nearfield_local_huygens_r0p35_1200MHz_1,1.m3d` | H-field pilot local near-field monitor artifact, `204793324` bytes. |

## Verification

```powershell
python -m py_compile code\build_cst_source_family_solver_safe_status.py code\build_g3_model_dashboard.py
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

Current status:

- Stage status: `source_family_solver_safe_matched_eh_finished`.
- Tracked CST trials: `7`.
- Finished CST trials: `7`.
- Timed-out CST trials: `0`.
- Matched E/H ready: `True`.
- Full E-field row: `efield96`, `3564.2 s`, `3` artifacts.
- Full H-field row: `hfield96`, `3348.3 s`, `3` artifacts.

## Current Limits

- This is still not a frozen-rule Huygens physics pass.
- The successful E/H pilot proves the short x case can be solved and can write near-field/far-field artifacts under a long controller window.
- The next proof step is ResultTree CSV export from the completed E/H projects, followed by frozen `eh_love_equivalence_minus_j96` validation against the CST far-field reference.
- The broader source-family queue is not closed until the same export and frozen-rule validation succeeds beyond the short x pilot.

## Next Step

1. Export matched local E-field and H-field CSVs from the completed short x pilot.
2. Export or bind the matching far-field reference.
3. Apply `eh_love_equivalence_minus_j96` without retuning.
4. If the pilot passes, expand to the remaining x/y/off-axis source-family cases.
