# CST operator runbook

This package is for real CST execution. It is not simulation evidence by itself.

## Immediate Goal

Close G2 by exporting the two required Level 1 standard-source cases and then running strict audit/reconstruction.

## Required Cases

| Order | sample_id | CST project | Source | Frequency | Nearfield export | Farfield export |
|---:|---|---|---|---|---|---|
| 1 | `L1_short_dipole_z_1p2G` | `CST_L1_short_dipole_z_1p2G.cst` | `short_dipole` | `1200MHz` | `data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv` | `data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv` |
| 2 | `L1_halfwave_dipole_z_1p2G` | `CST_L1_halfwave_dipole_z_1p2G.cst` | `halfwave_dipole` | `1200MHz` | `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv` | `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv` |

## Geometry and Sampling Contract

- Measurement surface: `2pi_upper_hemisphere`
- Probe radius: `13 m`
- Probe count: `162`
- Nearfield rows per case: `486` (`Ex`, `Ey`, `Ez` at each probe)
- Farfield grid rows per case: `2664`
- Enclosed carrier volume requirement from the problem statement: at least `12m x 10m x 8m`

## Operator Sequence

1. In CST, use meter units and preserve the global coordinate axes.
2. Create or clone the project named in `level1_required_operator_steps.csv`.
3. Build the dipole using the listed start/end coordinates and feed gap.
4. Use open/add-space or PML boundaries.
5. Add the 162 nearfield probe points from `cst_probe_points_hemisphere_162.csv`.
6. Export complex `Ex`, `Ey`, `Ez` at each probe into the exact nearfield CSV path.
7. Export farfield over the theta/phi grid in `cst_farfield_sampling_grid.csv` into the exact farfield CSV path.
8. Save required screenshots listed in `cst_level1_required_screenshot_manifest.csv`.
9. Run `post_export_level1_validation_commands.ps1` from the project root.

## Files

| File | Meaning |
|---|---|
| `level1_required_operator_steps.csv` | One row per required case with geometry, solver, monitor and export instructions. |
| `cst_probe_points_hemisphere_162.csv` | The exact 162 half-sphere probe coordinates to use in CST. |
| `cst_farfield_sampling_grid.csv` | The exact theta/phi farfield sampling grid expected by Python. |
| `cst_level1_required_export_contract.csv` | Required columns, expected rows, fallback phase paths and validation commands. |
| `cst_level1_required_screenshot_manifest.csv` | Screenshots needed to prove CST setup and exports. |
| `post_export_level1_validation_commands.ps1` | Commands to convert phase exports if needed, validate files, reconstruct farfield and refresh gates. |
| `README_cst_operator_runbook.md` | Human-readable runbook. |

## Failure Rules

- If filenames differ from this package, fix filenames before running merge scripts.
- If coordinates are exported in millimeters, convert them to meters before validation.
- If magnitude/phase columns are exported, run the phase conversion command before `check_cst_export.py`.
- If `merge_cst_level1_exports.py --strict` fails, do not start full Level 2 execution yet.
