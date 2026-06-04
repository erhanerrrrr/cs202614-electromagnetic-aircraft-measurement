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
| `level1_local_huygens_probe_points.csv` | `96` Cartesian local Huygens probe points on `level1_local_sphere_r0p35`. |
| `local_huygens_export_contract.csv` | CSV columns expected from local E-field probe exports. |
| `local_huygens_hfield_export_contract.csv` | CSV columns expected from local H-field probe exports. |
| `next_meshsafe_huygens_commands.csv` | Next executable commands: refresh workpack, generate E/H CST projects, run solver gates, export local probe CSVs. |
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

For the magnetic-field handoff, generate the H-field project separately so it
does not overwrite the already validated E-field project:

```powershell
python code\run_cst_level1_required_automation.py `
  --level1-csv data\cst_meshsafe_huygens_workpack\level1_required_meshsafe_huygens_cases.csv `
  --probe-csv data\cst_meshsafe_huygens_workpack\level1_local_huygens_probe_points.csv `
  --out-dir C:\csttmp\huy_h `
  --probe-mode hfield
```

Then run the solver feasibility gates listed in `next_meshsafe_huygens_commands.csv`.
Use short ASCII CST work paths such as `C:\csttmp\huy_p` for project
generation, `C:\csttmp\huy_s` for the E-field solver trial, and
`C:\csttmp\huy_hs` for the H-field solver trial so CST's internal
result paths stay under its path-length limit. If the gate produces local
`.m3d` nearfield and `.ffm/.fme` farfield artifacts, run the ResultTree export
commands listed in `next_meshsafe_huygens_commands.csv`. They read solved `1D Results` probe
curves and map CST local probe values to `local_huygens_export_contract.csv` or
`local_huygens_hfield_export_contract.csv`; do not use CST's ASCII export from the CST Field
Monitors 3D view for this handoff.

## Current Solver Observation

The short-path `L1_short_dipole_z_1p2G` trial confirms that CST can open the
project and run the HF Time Domain solver without the `4.6` billion-cell mesh
limit. The 600 s gate ended as `aborted_keeping_results`, with CST keeping one
nearfield `.m3d` artifact and one farfield `.ffm/.fme` pair. The ResultTree
controller has now extracted `96 * 3 = 288` complex Cartesian E-field probe
rows from the kept results. The follow-up H-field short-path route has also
extracted the matching `96 * 3 = 288` complex H-field rows for the short-dipole
case. The remaining non-proxy blocker is stricter E/H Huygens operator
calibration and half-wave H-field coverage, not CST startup.

## Boundary

This is not final 13 m near-field evidence. It is a solver-feasible CST
observation package intended to replace the infeasible remote-probe solve.
Final G3 claims still require a stricter H-field-backed vector surface-integral
operator, source-family cross-checks, or an independently stable impedance
closure before the local Huygens route becomes report-level physics evidence.

## Current Export Boundary

The working CST export interface is ResultTree probe-curve extraction. The CST
popup from the `Field Monitors` 3D view is an export-interface limitation, not a
CST solver failure. For the short-dipole case, both local E-field and H-field
contracts are now complete; for remaining cases, repeat the same H-field
project/solver/export route before final Huygens wording.
