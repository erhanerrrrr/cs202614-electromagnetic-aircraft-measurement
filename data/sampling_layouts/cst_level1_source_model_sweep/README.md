# CST Level 1 Source-Model Sweep

This directory stores a compact calibration sweep for the Level 1 CST exports.
It tests whether the full 162-point measurement baseline can be explained by
different equivalent-source grids and Tikhonov regularization values.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Candidate layouts | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |

## Best Model

| Field | Value |
|---|---|
| Model | `single_center` |
| Candidate | `full_grid_162` |
| Lambda | `1e-03` |
| Status | `corr_pass_nmse_near` |
| Min Corr | `0.9926` |
| Max NMSE | `1.7784e-02` |
| Max main-lobe error / deg | `0.00` |

## Model Ranking

| Model | Candidate | Lambda | Grid points | Status | Min Corr | Max NMSE | Max lobe error / deg |
|---|---|---:|---:|---|---:|---:|---:|
| single_center | full_grid_162 | 1e-03 | 1 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 |
| single_center | full_grid_162 | 1e-04 | 1 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 |
| single_center | full_grid_162 | 1e-02 | 1 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 |
| single_center | full_grid_162 | 1e-05 | 1 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 |
| default_cube_5x3x3 | full_grid_162 | 1e-05 | 45 | diagnostic_only | 0.7941 | 3.1843e-01 | 109.90 |
| default_cube_5x3x3 | full_grid_162 | 1e-04 | 45 | diagnostic_only | 0.7930 | 3.2036e-01 | 109.90 |
| default_cube_5x3x3 | full_grid_162 | 1e-03 | 45 | diagnostic_only | 0.7920 | 3.2657e-01 | 109.90 |
| compact_cube_3x3x3 | full_grid_162 | 1e-05 | 27 | diagnostic_only | 0.7838 | 3.3000e-01 | 39.97 |
| default_cube_5x3x3 | full_grid_162 | 1e-02 | 45 | diagnostic_only | 0.7826 | 3.3313e-01 | 69.95 |
| compact_cube_3x3x3 | full_grid_162 | 1e-04 | 27 | diagnostic_only | 0.7522 | 3.4766e-01 | 39.97 |
| z_line_3 | full_grid_162 | 1e-05 | 3 | diagnostic_only | 0.7106 | 2.3560e-01 | 139.12 |
| z_line_3 | full_grid_162 | 1e-04 | 3 | diagnostic_only | 0.7106 | 2.3561e-01 | 139.12 |
| z_line_3 | full_grid_162 | 1e-03 | 3 | diagnostic_only | 0.7105 | 2.3567e-01 | 139.12 |
| z_line_3 | full_grid_162 | 1e-02 | 3 | diagnostic_only | 0.7097 | 2.3633e-01 | 139.12 |
| compact_cube_3x3x3 | full_grid_162 | 1e-03 | 27 | diagnostic_only | 0.7066 | 2.8457e-01 | 49.97 |
| compact_cube_3x3x3 | full_grid_162 | 1e-02 | 27 | diagnostic_only | 0.4929 | 3.3211e-01 | 84.97 |
| wide_cube_5x5x3 | full_grid_162 | 1e-02 | 75 | diagnostic_only | 0.3936 | 8.1772e-01 | 154.56 |
| wide_cube_5x5x3 | full_grid_162 | 1e-03 | 75 | diagnostic_only | 0.3888 | 8.4603e-01 | 55.62 |
| wide_cube_5x5x3 | full_grid_162 | 1e-04 | 75 | diagnostic_only | 0.3878 | 8.5121e-01 | 55.62 |
| wide_cube_5x5x3 | full_grid_162 | 1e-05 | 75 | diagnostic_only | 0.3870 | 8.5177e-01 | 55.62 |
| xy_plane_3x3 | full_grid_162 | 1e-02 | 9 | diagnostic_only | 0.2758 | 6.6718e-01 | 52.62 |
| xy_plane_3x3 | full_grid_162 | 1e-03 | 9 | diagnostic_only | 0.2744 | 6.6875e-01 | 52.62 |
| xy_plane_3x3 | full_grid_162 | 1e-04 | 9 | diagnostic_only | 0.2742 | 6.6891e-01 | 52.62 |
| xy_plane_3x3 | full_grid_162 | 1e-05 | 9 | diagnostic_only | 0.2742 | 6.6893e-01 | 52.62 |

## Reading

- The best model passes correlation and main-lobe checks, but worst-case NMSE
  is still slightly above the strict target.
- The current data path is credible; the next work is NMSE-focused calibration
  through source priors, regularization, and phase/reference checks.
