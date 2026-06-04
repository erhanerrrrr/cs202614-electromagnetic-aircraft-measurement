# S42 G3 Huygens source-family CST workpack

## What Changed

- Added `code/prepare_cst_huygens_source_family_workpack.py`.
- Extended `code/run_cst_level1_required_automation.py` so the Level 1 CST
  generator can build axis-aligned `x`, `y`, and `z` dipoles from each case
  segment instead of hard-coding the `z` axis.
- Extended `code/export_cst_meshsafe_huygens_results.py` so case-scoped probe
  CSVs are filtered by `sample_id` before ResultTree export checks.
- Generated `data/cst_meshsafe_huygens_source_family_workpack/`.
- Refreshed the G3 dashboard so the source-family workpack appears as a
  separate `meshsafe_huygens_source_family_workpack` row.

## Why

S41 proved that the frozen real E/H Huygens rule is coordinate-covariant inside
the Python operator. The next proof must be stronger: run independent CST
electromagnetic solves that were not used to tune the rule, export their local
E/H Huygens surface fields, and test the same frozen rule without per-source
retuning.

This stage turns that next proof into an executable handoff.

## Main Result

Current status:

`source_family_workpack_ready`

| Metric | Value |
|---|---:|
| Frozen rule under test | `eh_love_equivalence_minus_j96` |
| Automation-ready axis-aligned cases | `6` |
| Probe points per case | `96` |
| Case-scoped probe rows | `576` |
| Validation matrix rows | `8` |
| Advanced rows tracked but not automated | `2` |

Automation-ready CST cases:

| Case | Purpose |
|---|---|
| `L1_short_dipole_x_1p2G` | x-oriented short dipole |
| `L1_short_dipole_y_1p2G` | y-oriented short dipole |
| `L1_halfwave_dipole_x_1p2G` | x-oriented half-wave dipole |
| `L1_halfwave_dipole_y_1p2G` | y-oriented half-wave dipole |
| `L1_short_dipole_z_offset_xp25_1p2G` | off-axis short z dipole |
| `L1_halfwave_dipole_z_offset_yp25_1p2G` | off-axis half-wave z dipole |

Tracked advanced gates:

| Gate | Current boundary |
|---|---|
| tilted dipole | arbitrary-axis CST cylinder history is not yet promoted to automation |
| two-source pilot | current generator is still single radiator / single port |

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/prepare_cst_huygens_source_family_workpack.py` | Builds the source-family validation workpack and command queue. |
| `data/cst_meshsafe_huygens_source_family_workpack/level1_source_family_axis_aligned_cases.csv` | Six CST cases ready for E/H project generation. |
| `data/cst_meshsafe_huygens_source_family_workpack/level1_source_family_probe_points.csv` | Case-scoped local Huygens probe points with `sample_id`. |
| `data/cst_meshsafe_huygens_source_family_workpack/source_family_validation_matrix.csv` | Full matrix, including the two advanced rows not yet automated. |
| `data/cst_meshsafe_huygens_source_family_workpack/next_source_family_commands.csv` | Ordered CST generation, solve, and export commands. |
| `data/cst_meshsafe_huygens_source_family_workpack/source_family_workpack_summary.json` | Machine-readable workpack status. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard row `meshsafe_huygens_source_family_workpack`. |

## Validation

```powershell
python -m py_compile code\run_cst_level1_required_automation.py code\export_cst_meshsafe_huygens_results.py code\prepare_cst_huygens_source_family_workpack.py code\build_g3_model_dashboard.py
python code\prepare_cst_huygens_source_family_workpack.py
python code\build_g3_model_dashboard.py
```

Key evidence:

- `stage_status = source_family_workpack_ready`
- `axis_aligned_case_count = 6`
- `probe_row_count = 576`
- `automation_ready_count = 6`
- `pending_advanced_count = 2`

## Current Boundary

This is not yet an independent CST physics pass. It is the execution package
needed to produce that pass. The next proof still requires CST project
generation, solving, ResultTree export, and a frozen-rule Huygens evaluation on
the new source-family E/H CSVs.

The recent CST popup does not mean CST is globally unusable. It points to a
specific ASCII export path mismatch for a Field Monitor object. The mesh-safe
source-family route continues to use the shorter local probe / ResultTree path
that has already worked for the two current Level 1 E/H cases.

## Next Step

1. Run the commands listed in
   `data/cst_meshsafe_huygens_source_family_workpack/next_source_family_commands.csv`.
2. Confirm each new case has matched local E-field and H-field CSVs.
3. Add the exported rows to the frozen-rule Huygens gate without retuning
   `eh_love_equivalence_minus_j96`.
4. Only after those rows remain accepted should the rule be promoted toward the
   13 m measurement shell and reduced sampling workflow.
