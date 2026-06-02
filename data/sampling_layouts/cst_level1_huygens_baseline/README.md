# CST Level 1 Huygens Surface Baseline

This directory evaluates the first Huygens-style surface-source prior against
the current Level 1 CST near/far-field export. The implementation uses a compact
electric/magnetic dipole-sheet approximation: each surface node has two
tangential electric-current coefficients and, for the Huygens variants, two
tangential magnetic-current coefficients. It is a runnable diagnostic baseline,
not a final Stratton-Chu/Huygens integral solver.

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
| Status | `diagnostic_only` |
| Min Corr | `0.7781` |
| Max NMSE | `2.6423e-01` |
| Max main-lobe error / deg | `166.71` |
| Mean relative residual | `6.1942e-01` |
| Mean active nodes | `96.0` |
| Mean top-10 node energy share | `0.297` |

## Best Cases

| Sample | Frequency / Hz | Corr | NMSE | Main-lobe error / deg | Relative residual | Active nodes |
|---|---:|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | 1.2e+09 | 0.8135 | 2.5379e-01 | 35.21 | 6.1467e-01 | 96 |
| L1_short_dipole_z_1p2G | 1.2e+09 | 0.7781 | 2.6423e-01 | 166.71 | 6.2418e-01 | 96 |

## Setting Ranking

| Prior | Variant | Candidate | Lambda | Status | Min Corr | Max NMSE | Max lobe / deg | Mean residual | Mean active nodes |
|---|---|---|---:|---|---:|---:|---:|---:|---:|
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-02 | diagnostic_only | 0.7781 | 2.6423e-01 | 166.71 | 6.1942e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-02 | diagnostic_only | 0.7781 | 2.6423e-01 | 166.71 | 6.1942e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-04 | diagnostic_only | 0.7263 | 5.2019e-01 | 133.26 | 5.0729e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-04 | diagnostic_only | 0.7053 | 5.1717e-01 | 144.78 | 2.5222e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-04 | diagnostic_only | 0.7053 | 5.1717e-01 | 144.78 | 2.5222e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-02 | diagnostic_only | 0.6377 | 2.7751e-01 | 134.24 | 8.2362e-01 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-06 | diagnostic_only | 0.5776 | 7.4394e-01 | 144.78 | 2.9073e-02 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-06 | diagnostic_only | 0.5776 | 7.4394e-01 | 144.78 | 2.9073e-02 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-10 | diagnostic_only | 0.5734 | 7.3176e-01 | 171.89 | 1.5187e-04 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-10 | diagnostic_only | 0.5734 | 7.3176e-01 | 171.89 | 1.5187e-04 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_minus | full_grid_162 | 1e-08 | diagnostic_only | 0.5734 | 7.3316e-01 | 171.89 | 1.4819e-03 | 96.0 |
| level1_local_sphere_r0p35 | huygens_em_plus | full_grid_162 | 1e-08 | diagnostic_only | 0.5734 | 7.3316e-01 | 171.89 | 1.4819e-03 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-06 | diagnostic_only | 0.5581 | 7.3769e-01 | 165.56 | 4.1293e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-08 | diagnostic_only | 0.5557 | 7.3894e-01 | 165.56 | 4.1147e-01 | 96.0 |
| level1_local_sphere_r0p35 | electric_sheet_only | full_grid_162 | 1e-10 | diagnostic_only | 0.5557 | 7.3894e-01 | 165.56 | 4.1147e-01 | 96.0 |

## Reading

- The Huygens-style surface prior is still diagnostic on the current CST export.
- Treat the result as a measurement-matrix smoke test. The next physics step is true near-field monitor data and a fuller electric/magnetic surface Green-function convention check.

## Generated Files

| File | Role |
|---|---|
| `huygens_reconstruction_results.csv` | Per sample/frequency/model/lambda reconstruction metrics. |
| `huygens_reconstruction_by_setting.csv` | Aggregated setting ranking. |
| `huygens_reconstruction_best_cases.csv` | Per-case rows for the best setting. |
| `huygens_surface_solution_best_setting.csv` | Best-setting node coefficients for later visualization and support analysis. |
| `huygens_reconstruction_summary.json` | Script-friendly summary. |

## Command

```powershell
python code\run_cst_huygens_baseline.py
```
