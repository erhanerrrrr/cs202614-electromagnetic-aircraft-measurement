# S43 G3 Huygens source-family CST project generation

## What Changed

- Ran the S42 source-family CST project-generation commands for both E-field
  and H-field probe modes.
- Added `code/build_cst_source_family_generation_status.py` to collect local
  `C:\csttmp\huy_sf_e` and `C:\csttmp\huy_sf_h` generation evidence into the
  repository.
- Refreshed the G3 dashboard so the source-family row advances from
  `source_family_workpack_ready` to `source_family_projects_generated`.

## Why

S42 proved that the source-family validation queue was defined. S43 checks the
next concrete question: can those x/y/off-axis cases actually be instantiated
through the local CST API, including separate E-field and H-field project
variants?

The answer is yes for the six automation-ready source-family cases.

## Main Result

Current status:

`source_family_projects_generated`

| Metric | Value |
|---|---:|
| E-field CST projects created | `6/6` |
| H-field CST projects created | `6/6` |
| Total CST project rows | `12` |
| Real CST API used | `true` |
| E-field all cases ok | `true` |
| H-field all cases ok | `true` |

Generated local CST project roots:

| Probe mode | Local project root |
|---|---|
| E-field | `C:\csttmp\huy_sf_e\projects` |
| H-field | `C:\csttmp\huy_sf_h\projects` |

The generated cases cover:

- `L1_short_dipole_x_1p2G`
- `L1_short_dipole_y_1p2G`
- `L1_halfwave_dipole_x_1p2G`
- `L1_halfwave_dipole_y_1p2G`
- `L1_short_dipole_z_offset_xp25_1p2G`
- `L1_halfwave_dipole_z_offset_yp25_1p2G`

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/build_cst_source_family_generation_status.py` | Summarizes local CST project-generation evidence into repository outputs. |
| `outputs/cst_meshsafe_huygens_source_family_generation/source_family_project_generation_summary.json` | Machine-readable status for E/H project generation. |
| `outputs/cst_meshsafe_huygens_source_family_generation/source_family_project_manifest.csv` | Combined 12-row E/H CST project manifest. |
| `outputs/cst_meshsafe_huygens_source_family_generation/source_family_project_generation.md` | Human-readable project-generation report. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard row now reports `source_family_projects_generated`. |

## Validation

```powershell
python -m py_compile code\build_cst_source_family_generation_status.py code\build_g3_model_dashboard.py
python code\build_cst_source_family_generation_status.py
python code\build_g3_model_dashboard.py
```

Key evidence:

- `stage_status = source_family_projects_generated`
- `total_projects_created = 12`
- `total_project_rows = 12`
- Dashboard artifact `meshsafe_huygens_source_family_workpack` now has status
  `source_family_projects_generated`.

## Current Boundary

This stage proves CST-compatible project generation for the independent
source-family cases. It still does not prove electromagnetic correctness,
because the generated projects have not yet completed solver runs, ResultTree
local E/H exports, far-field reference export, or frozen-rule Huygens
evaluation.

## Next Step

1. Start with the short x-oriented case and run the E-field and H-field solver
   commands from `next_source_family_commands.csv`.
2. Export the matched local probe CSVs and far-field reference.
3. If the short x case closes cleanly, repeat for the remaining five cases.
4. Then run the frozen rule `eh_love_equivalence_minus_j96` without retuning.
