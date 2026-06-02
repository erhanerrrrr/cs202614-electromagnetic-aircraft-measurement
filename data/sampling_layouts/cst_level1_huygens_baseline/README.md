# CST Level 1 Huygens Surface Baseline

This directory evaluates the first Huygens-style surface-source prior against
the current Level 1 CST near/far-field export. The implementation uses a compact
electric/magnetic dipole-sheet approximation: each surface node has two
tangential electric-current coefficients and, for the Huygens variants, two
tangential magnetic-current coefficients. The runner also sweeps a local
surface smoothness penalty through `--smooth-lambda`. It is a runnable
diagnostic baseline, not a final Stratton-Chu/Huygens integral solver.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Candidate layouts | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |

## Best Setting

| Field | Value |
|---|---|
| Prior | `level1_local_sphere_r0p35` |
| Model variant | `huygens_em_minus` |
| Candidate | `full_grid_162` |
| Lambda | `1e-02` |
| Smooth lambda | `0e+00` |
| Smooth neighbors | `6` |
| Status | `diagnostic_only` |
| Min Corr | `0.7781` |
| Max NMSE | `2.6423e-01` |
| Max main-lobe error / deg | `166.71` |
| Mean relative residual | `6.1942e-01` |
| Mean smoothness relative jump | `2.3931e+00` |
| Mean active nodes | `96.0` |
| Mean top-10 node energy share | `0.297` |

## Best Cases

| Sample | Frequency / Hz | Corr | NMSE | Main-lobe error / deg | Relative residual | Active nodes |
|---|---:|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | 1.2e+09 | 0.8135 | 2.5379e-01 | 35.21 | 6.1467e-01 | 96 |
| L1_short_dipole_z_1p2G | 1.2e+09 | 0.7781 | 2.6423e-01 | 166.71 | 6.2418e-01 | 96 |

## Setting Ranking

| Prior | Variant | Candidate | Lambda | Smooth lambda | Status | Min Corr | Max NMSE | Max lobe / deg | Mean residual | Mean smooth jump | Mean active nodes |
|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-02 | 0e+00 | diagnostic_only | 0.7781 | 2.6423e-01 | 166.71 | 6.1942e-01 | 2.3931e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-02 | 0e+00 | diagnostic_only | 0.7781 | 2.6423e-01 | 166.71 | 6.1942e-01 | 2.3931e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-02 | 1e-06 | diagnostic_only | 0.7781 | 2.6420e-01 | 166.71 | 6.1949e-01 | 2.3929e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-02 | 1e-06 | diagnostic_only | 0.7781 | 2.6420e-01 | 166.71 | 6.1949e-01 | 2.3929e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-02 | 1e-04 | diagnostic_only | 0.7776 | 2.6229e-01 | 162.64 | 6.2630e-01 | 2.3674e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-02 | 1e-04 | diagnostic_only | 0.7776 | 2.6229e-01 | 162.64 | 6.2630e-01 | 2.3674e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-04 | 1e-06 | diagnostic_only | 0.7269 | 5.0995e-01 | 133.26 | 5.0888e-01 | 2.2747e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-04 | 0e+00 | diagnostic_only | 0.7263 | 5.2019e-01 | 133.26 | 5.0729e-01 | 2.2803e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-04 | 1e-04 | diagnostic_only | 0.7188 | 4.1666e-01 | 149.74 | 3.6871e-01 | 1.8975e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-04 | 1e-04 | diagnostic_only | 0.7188 | 4.1666e-01 | 149.74 | 3.6871e-01 | 1.8975e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-06 | 1e-04 | diagnostic_only | 0.7162 | 4.4524e-01 | 149.74 | 3.5601e-01 | 1.3385e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-06 | 1e-04 | diagnostic_only | 0.7162 | 4.4524e-01 | 149.74 | 3.5601e-01 | 1.3385e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-08 | 1e-04 | diagnostic_only | 0.7162 | 4.4609e-01 | 144.78 | 3.5586e-01 | 1.3139e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-08 | 1e-04 | diagnostic_only | 0.7162 | 4.4609e-01 | 144.78 | 3.5586e-01 | 1.3139e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-10 | 1e-04 | diagnostic_only | 0.7162 | 4.4610e-01 | 144.78 | 3.5586e-01 | 1.3136e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-10 | 1e-04 | diagnostic_only | 0.7162 | 4.4610e-01 | 144.78 | 3.5586e-01 | 1.3136e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-04 | 1e-04 | diagnostic_only | 0.7158 | 3.3851e-01 | 171.22 | 5.8370e-01 | 2.0376e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-06 | 1e-04 | diagnostic_only | 0.7146 | 3.4244e-01 | 94.92 | 5.7389e-01 | 1.9973e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-08 | 1e-04 | diagnostic_only | 0.7146 | 3.4257e-01 | 94.92 | 5.7379e-01 | 1.9968e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-10 | 1e-04 | diagnostic_only | 0.7146 | 3.4257e-01 | 94.92 | 5.7379e-01 | 1.9968e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-04 | 1e-06 | diagnostic_only | 0.7061 | 5.1128e-01 | 144.78 | 2.5600e-01 | 2.6241e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-04 | 1e-06 | diagnostic_only | 0.7061 | 5.1128e-01 | 144.78 | 2.5600e-01 | 2.6241e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-04 | 0e+00 | diagnostic_only | 0.7053 | 5.1717e-01 | 144.78 | 2.5222e-01 | 2.6372e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-04 | 0e+00 | diagnostic_only | 0.7053 | 5.1717e-01 | 144.78 | 2.5222e-01 | 2.6372e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-02 | 0e+00 | diagnostic_only | 0.6377 | 2.7751e-01 | 134.24 | 8.2362e-01 | 2.4000e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-02 | 1e-06 | diagnostic_only | 0.6376 | 2.7749e-01 | 134.24 | 8.2368e-01 | 2.3998e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-02 | 1e-04 | diagnostic_only | 0.6293 | 2.7596e-01 | 134.24 | 8.2903e-01 | 2.3785e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-06 | 1e-06 | diagnostic_only | 0.6254 | 6.9169e-01 | 144.78 | 1.0241e-01 | 2.4431e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-06 | 1e-06 | diagnostic_only | 0.6254 | 6.9169e-01 | 144.78 | 1.0241e-01 | 2.4431e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-10 | 1e-06 | diagnostic_only | 0.6231 | 6.9602e-01 | 144.78 | 9.2870e-02 | 2.0859e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-10 | 1e-06 | diagnostic_only | 0.6231 | 6.9602e-01 | 144.78 | 9.2870e-02 | 2.0859e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-08 | 1e-06 | diagnostic_only | 0.6231 | 6.9597e-01 | 144.78 | 9.2988e-02 | 2.1004e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-08 | 1e-06 | diagnostic_only | 0.6231 | 6.9597e-01 | 144.78 | 9.2988e-02 | 2.1004e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-06 | 1e-06 | diagnostic_only | 0.5908 | 7.1921e-01 | 132.64 | 4.2603e-01 | 2.0460e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-08 | 1e-06 | diagnostic_only | 0.5851 | 7.2188e-01 | 165.56 | 4.2252e-01 | 2.0222e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-10 | 1e-06 | diagnostic_only | 0.5851 | 7.2194e-01 | 165.56 | 4.2248e-01 | 2.0219e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-06 | 0e+00 | diagnostic_only | 0.5776 | 7.4394e-01 | 144.78 | 2.9073e-02 | 2.6259e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-06 | 0e+00 | diagnostic_only | 0.5776 | 7.4394e-01 | 144.78 | 2.9073e-02 | 2.6259e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-10 | 0e+00 | diagnostic_only | 0.5734 | 7.3176e-01 | 171.89 | 1.5187e-04 | 2.5882e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-10 | 0e+00 | diagnostic_only | 0.5734 | 7.3176e-01 | 171.89 | 1.5187e-04 | 2.5882e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-08 | 0e+00 | diagnostic_only | 0.5734 | 7.3316e-01 | 171.89 | 1.4819e-03 | 2.5913e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-08 | 0e+00 | diagnostic_only | 0.5734 | 7.3316e-01 | 171.89 | 1.4819e-03 | 2.5913e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-06 | 0e+00 | diagnostic_only | 0.5581 | 7.3769e-01 | 165.56 | 4.1293e-01 | 2.0383e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-08 | 0e+00 | diagnostic_only | 0.5557 | 7.3894e-01 | 165.56 | 4.1147e-01 | 2.0000e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-10 | 0e+00 | diagnostic_only | 0.5557 | 7.3894e-01 | 165.56 | 4.1147e-01 | 1.9995e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-10 | 1e-02 | diagnostic_only | 0.4953 | 4.0592e-01 | 137.82 | 7.6325e-01 | 6.8249e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-10 | 1e-02 | diagnostic_only | 0.4953 | 4.0592e-01 | 137.82 | 7.6325e-01 | 6.8249e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-08 | 1e-02 | diagnostic_only | 0.4953 | 4.0592e-01 | 137.82 | 7.6325e-01 | 6.8250e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-08 | 1e-02 | diagnostic_only | 0.4953 | 4.0592e-01 | 137.82 | 7.6325e-01 | 6.8250e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-06 | 1e-02 | diagnostic_only | 0.4952 | 4.0589e-01 | 137.82 | 7.6327e-01 | 6.8314e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-06 | 1e-02 | diagnostic_only | 0.4952 | 4.0589e-01 | 137.82 | 7.6327e-01 | 6.8314e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-04 | 1e-02 | diagnostic_only | 0.4882 | 4.0322e-01 | 137.82 | 7.6466e-01 | 7.4123e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-04 | 1e-02 | diagnostic_only | 0.4882 | 4.0322e-01 | 137.82 | 7.6466e-01 | 7.4123e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-02 | 1e-02 | diagnostic_only | 0.4668 | 3.7290e-01 | 136.08 | 8.1494e-01 | 1.4991e+00 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-02 | 1e-02 | diagnostic_only | 0.4668 | 3.7290e-01 | 136.08 | 8.1494e-01 | 1.4991e+00 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-10 | 1e-02 | diagnostic_only | 0.3798 | 4.1251e-01 | 69.95 | 9.2158e-01 | 7.6386e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-08 | 1e-02 | diagnostic_only | 0.3798 | 4.1251e-01 | 69.95 | 9.2158e-01 | 7.6387e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-06 | 1e-02 | diagnostic_only | 0.3797 | 4.1257e-01 | 69.95 | 9.2159e-01 | 7.6399e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-04 | 1e-02 | diagnostic_only | 0.3655 | 4.1883e-01 | 69.95 | 9.2197e-01 | 7.7602e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-02 | 1e-02 | diagnostic_only | 0.1699 | 5.9435e-01 | 81.29 | 9.4450e-01 | 1.4603e+00 | 96.0 |

## Reading

- The Huygens-style surface prior is still diagnostic on the current CST export.
- The surface smoothness sweep is useful for regularization diagnostics, but it does not close the current Level 1 physics gate.
- Treat the result as a measurement-matrix smoke test. The next physics step is true near-field monitor data and a fuller electric/magnetic surface Green-function convention check.

## Generated Files

| File | Role |
|---|---|
| `huygens_reconstruction_results.csv` | Per sample/frequency/model/lambda reconstruction metrics. |
| `huygens_reconstruction_by_setting.csv` | Aggregated setting ranking, including the surface smoothness sweep. |
| `huygens_reconstruction_best_cases.csv` | Per-case rows for the best setting. |
| `huygens_surface_solution_best_setting.csv` | Best-setting node coefficients for later visualization and support analysis. |
| `huygens_reconstruction_summary.json` | Script-friendly summary. |

## Command

```powershell
python code\run_cst_huygens_baseline.py
```
