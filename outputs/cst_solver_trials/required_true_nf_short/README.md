# CST solver trial diagnostic

- Status: `solver_mesh_limit`
- Source project: `outputs\cst_real_level1_projects\projects\CST_L1_short_dipole_z_1p2G.cst`
- Trial project: `outputs\cst_solver_trials\required_true_nf_short\CST_L1_short_dipole_z_1p2G_solver_trial.cst`
- CST API start result: `{'ok': True, 'value': True}`
- Result-tree child items after solve: `0`
- Parsed mesh size: `4.6` billion cells
- Parsed MPI requirement: `3` cluster nodes

Interpretation: CST could start the solver, but the full-wave setup is too large for the local machine.
The 13 m measurement shell should be treated as a Python-side extrapolation target, not as a remote probe mesh inside this CST solve.

## Key log lines

- `2026-06-03 22:17:16   *** Error ***`
- `Simulation setup for 4.6 billion mesh cells requires:`
- `Simulation cannot be started.`
- `2026-06-03 22:22:44   *** Error ***`
- `2026-06-03 22:24:03   *** Error ***`
- `ERROR:`
- `1 error occurred.`
- `Error while opening parameter storage module:`
- `CST::Exception: Expecting local encoding but found utf8 multibyte.`
- `CST::FileError: Source file for copy db.parmap not found`
