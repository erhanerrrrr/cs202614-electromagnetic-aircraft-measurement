# CST Mesh-Safe Huygens Workpack

This workpack converts the current G3 route from a remote 13 m Cartesian-probe
solve into a local Huygens-surface observation solve.

## Why This Exists

The previous true-nearfield CST trial proved that CST itself can start, but the
13 m probe shell expands the full-wave problem to about `4.6` billion mesh
cells and requires at least `3` MPI cluster nodes. This folder defines the next
mesh-safe route: CST observes a compact local surface near the Level 1 source;
Python extrapolates that local evidence to the 13 m measurement shell.

## Files

| File | Purpose |
|---|---|
| `level1_required_meshsafe_huygens_cases.csv` | Level 1 required cases rewritten to use mesh-safe local Huygens exports. |
| `level1_local_huygens_probe_points.csv` | `96` Cartesian E-field probe points on `level1_local_sphere_r0p35`. |
| `local_huygens_export_contract.csv` | CSV columns expected from local Huygens probe exports. |
| `next_meshsafe_huygens_commands.csv` | Next executable commands: refresh workpack, generate CST projects, run first solver gate, export local probe CSV. |
| `meshsafe_huygens_workpack_summary.json` | Machine-readable counts, source paths, and next gates. |

## Surface

- Prior: `level1_local_sphere_r0p35`
- Surface type: `sphere`
- Nodes/probes: `96`
- Inferred center: `(0.00021393736249, 0.000270103717902, 4.0) m`
- Mean local radius: `0.349999773869` m

## Execution

```powershell
python code\run_cst_level1_required_automation.py `
  --level1-csv data\cst_meshsafe_huygens_workpack\level1_required_meshsafe_huygens_cases.csv `
  --probe-csv data\cst_meshsafe_huygens_workpack\level1_local_huygens_probe_points.csv `
  --out-dir C:\csttmp\huy_p `
  --probe-mode efield
```

Then run the first solver feasibility gate listed in `next_meshsafe_huygens_commands.csv`.
Use short ASCII CST work paths such as `C:\csttmp\huy_p` for project
generation and `C:\csttmp\huy_s` for the solver trial so CST's
internal result paths stay under its path-length limit. If the gate produces
local `.m3d` nearfield and `.ffm/.fme` farfield artifacts, run the ResultTree
export command listed in `next_meshsafe_huygens_commands.csv`. It reads solved `1D Results`
E-field probe curves and maps CST local probe values to `local_huygens_export_contract.csv`;
do not use CST's ASCII export from the `Field Monitors` view for this handoff.

## Current Solver Observation

The short-path `L1_short_dipole_z_1p2G` trial confirms that CST can open the
project and run the HF Time Domain solver without the `4.6` billion-cell mesh
limit. The 600 s gate ended as `aborted_keeping_results`, with CST keeping one
nearfield `.m3d` artifact and one farfield `.ffm/.fme` pair. The ResultTree
controller has now extracted `96 * 3 = 288` complex Cartesian E-field probe
rows from the kept results, so the immediate blocker has moved from CST
startup/export to Python Huygens extrapolation and reference comparison.

## Boundary

This is not final 13 m near-field evidence. It is a solver-feasible CST
observation package intended to replace the infeasible remote-probe solve.
Final G3 claims still require Python extrapolation to the 13 m shell, comparison
against the existing FarfieldPlot-derived reference, and repetition on the
second Level 1 source case before the local Huygens route becomes report-level
evidence.

## Current Export Boundary

The cached CST ResultTree inspections currently expose local E-field probe
curves, but no matching H-field probe curves. Do not use ASCII export from the
`Field Monitors` 3D view as the handoff path; the CST popup for that view is an
export-interface limitation, not a CST solver failure. Use ResultTree probe
curves for the current E-field handoff, then add H-field probes or run the
impedance stability gate before final Huygens wording.

The latest lower-eta stability check reports source-dependent proxy calibration:
the half-wave dipole prefers about `0.03125 eta0`, while the short dipole
prefers about `0.0625 eta0`. Treat this as a cross-case disagreement, not as a
single physical impedance measurement.
