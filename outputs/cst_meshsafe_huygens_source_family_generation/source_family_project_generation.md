# CST Huygens Source-Family Project Generation

This report records the local CST API project-generation evidence for the S42 source-family workpack.

## Status

- Stage status: `source_family_projects_generated`
- Real CST API used: `True`
- E-field projects: `6/6`
- H-field projects: `6/6`
- Total project rows: `12`

This is still not a solve/export physics pass. The next gate is to solve the generated projects, export matched local E/H probe CSVs, and evaluate the frozen Huygens rule without retuning.

## Project Rows

| Field | Sample | Axis | Exists | Bytes | Status |
|---|---|---|---|---:|---|
| e | `L1_short_dipole_x_1p2G` | `x` | `True` | 46233 | `project_saved` |
| e | `L1_short_dipole_y_1p2G` | `y` | `True` | 47239 | `project_saved` |
| e | `L1_halfwave_dipole_x_1p2G` | `x` | `True` | 51006 | `project_saved` |
| e | `L1_halfwave_dipole_y_1p2G` | `y` | `True` | 51272 | `project_saved` |
| e | `L1_short_dipole_z_offset_xp25_1p2G` | `z` | `True` | 47139 | `project_saved` |
| e | `L1_halfwave_dipole_z_offset_yp25_1p2G` | `z` | `True` | 47107 | `project_saved` |
| h | `L1_short_dipole_x_1p2G` | `x` | `True` | 46223 | `project_saved` |
| h | `L1_short_dipole_y_1p2G` | `y` | `True` | 47239 | `project_saved` |
| h | `L1_halfwave_dipole_x_1p2G` | `x` | `True` | 51014 | `project_saved` |
| h | `L1_halfwave_dipole_y_1p2G` | `y` | `True` | 51276 | `project_saved` |
| h | `L1_short_dipole_z_offset_xp25_1p2G` | `z` | `True` | 47133 | `project_saved` |
| h | `L1_halfwave_dipole_z_offset_yp25_1p2G` | `z` | `True` | 47105 | `project_saved` |

## Regenerate

```powershell
python code\build_cst_source_family_generation_status.py
```
