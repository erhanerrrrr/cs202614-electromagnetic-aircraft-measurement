# CST True Near-Field Monitor Export

Purpose: make the G3 true-monitor blocker executable and auditable.

This run attempted to open CST projects through CST Python.

The worker records `Field Monitors`/`Probes` definition nodes for diagnosis, but ASCII export is attempted only on solved result-tree nodes under `1D Results`, `2D/3D Results`, or `Tables`.

## Current Summary

- Selected tasks: 2
- Ready tasks: 2
- Target CSVs already present: 0
- CST Python exists: True
- Controller status: `incomplete`

## Files

| File | Purpose |
|---|---|
| `true_nearfield_export_task_plan.csv` | Selected required CST projects, target CSVs, blockers, and current file status. |
| `true_nearfield_export_summary.json` | Machine-readable controller summary. |
| `true_nearfield_export_stdout.log` | CST worker stdout/stderr when a non-dry run is attempted. |
| `worker_case_results.csv` | Per-case worker result, created after CST worker execution. |

After target CSVs are written, run:

```powershell
python code\check_true_nearfield_dropzone.py --required-only --full-grid-only
python code\run_true_nearfield_gate.py --required-only --candidate full_grid_162
python code\run_true_nearfield_workflow_decision.py
```
