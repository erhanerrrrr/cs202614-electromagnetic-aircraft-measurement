# CST workspace notes

This folder is the GitHub-visible index for CST modeling, CST automation, and
true near-field monitor handoff material. Large `.cst` projects, `Result/`
caches, solver scratch folders, and generated binary/runtime files are kept out
of Git by default. The tracked files point to the reproducible manifests,
operator packets, and CSV contracts that teammates should use.

## Current CST entry points

| Area | Current path | Purpose |
|---|---|---|
| CST templates | `outputs/cst_templates/` | Hemisphere sampling points, nearfield/farfield demo exports, and template CSVs. |
| CST macro templates | `outputs/cst_macro_templates/` | Level 1/Level 2 VBA skeletons, parameter tables, and pilot queues. |
| Operator runbook | `outputs/cst_operator_runbook/` | Manual CST steps for probe points, far-field grids, export contracts, and validation. |
| Level 1 workpack | `outputs/cst_level1_workpack/` | Standard-source modeling cards and export checks. |
| Level 2 workpack | `outputs/cst_level2_workpack/` | Multi-source/multi-state sample cards and category lists. |
| True monitor workpack | `data/cst_true_nearfield_workpack/` | Tracked G3 true near-field monitor queue, CSV contract, gate report, and CST task packet. |
| Required true monitor operator packet | `data/cst_true_nearfield_workpack/operator_packet/` | GitHub-visible task cards for the two required Level 1 full-grid true near-field exports. |
| Real CST CSV exports | `data/cst_exports/` | Python-consumable nearfield/farfield CSVs used by reconstruction and recognition scripts. |
| Local CST projects and solver traces | `outputs/cst_real_level1_projects/`, `outputs/cst_solver_ready_level1_projects/`, `outputs/cst_solver_trials/`, `outputs/cst_level2_element_library/` | Generated projects and solver traces; large caches are ignored by Git. |

## Current G3 blocker

The G3 true-monitor gate is waiting for two required full-grid CST true
near-field monitor CSV files:

- `data\cst_exports\level1_true_nearfield\L1_short_dipole_z_1p2G_true_nearfield.csv`
- `data\cst_exports\level1_true_nearfield\L1_halfwave_dipole_z_1p2G_true_nearfield.csv`

Each file must contain 486 rows: 162 sensor points times the three Cartesian
components `Ex`, `Ey`, and `Ez`. The exact CST task cards are in
`data/cst_true_nearfield_workpack/operator_packet/required_full_grid_task_cards.md`.

## Python-to-CST workflow

1. Use `code/prepare_cst_level*_manifest.py` to fix sample ids, frequencies,
   source parameters, and export contracts.
2. Use `code/run_cst_level1_required_automation.py` or
   `code/run_cst_level2_element_library.py` to generate CST projects when the
   local CST COM environment is available.
3. Solve single projects with `code/run_cst_solver_project.py`, or follow the
   manual CST operator runbook when COM automation is unavailable.
4. Export results with `code/export_cst_farfield_results.py`,
   `code/export_cst_level2_superposed_results.py`, or the true-monitor task
   cards in `data/cst_true_nearfield_workpack/operator_packet/`.
5. Validate and merge exports with `code/check_cst_export.py`,
   `code/merge_cst_level*_exports.py`, and for G3 true-monitor data:
   `code/check_true_nearfield_dropzone.py --required-only --full-grid-only`.
