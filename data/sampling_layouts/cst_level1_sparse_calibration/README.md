# CST Level 1 Sparse Source Calibration

This directory tests whether group-sparse equivalent sources improve the
generic Level 1 source grids. Each source point has three complex dipole moment
components, and the sparse solver shrinks those three components as one group.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Candidate layouts | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |

## Best Setting

| Field | Value |
|---|---|
| Config | `default_cube_5x3x3` |
| Solver | `group_sparse` |
| Candidate | `full_grid_162` |
| L2 lambda | `1e-04` |
| Group alpha fraction | `3e-01` |
| Status | `diagnostic_only` |
| Min Corr | `0.9283` |
| Max NMSE | `8.1110e-02` |
| Max main-lobe error / deg | `152.70` |
| Mean active sources | `2.0` |
| Mean center energy share | `0.000` |

## Setting Ranking

| Config | Solver | L2 lambda | Group alpha frac | Status | Min Corr | Max NMSE | Mean active sources | Mean center energy share |
|---|---|---:|---:|---|---:|---:|---:|---:|
| default_cube_5x3x3 | group_sparse | 1e-04 | 3e-01 | diagnostic_only | 0.9283 | 8.1110e-02 | 2.0 | 0.000 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 3e-01 | diagnostic_only | 0.9283 | 8.1114e-02 | 2.0 | 0.000 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 1e-01 | diagnostic_only | 0.8300 | 2.2708e-01 | 24.0 | 0.067 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 1e-01 | diagnostic_only | 0.8300 | 2.2707e-01 | 24.0 | 0.067 |
| default_cube_5x3x3 | tikhonov | 1e-05 | 0e+00 | diagnostic_only | 0.7941 | 3.1843e-01 | 45.0 | 0.026 |
| default_cube_5x3x3 | tikhonov | 1e-04 | 0e+00 | diagnostic_only | 0.7930 | 3.2036e-01 | 45.0 | 0.020 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 1e-04 | diagnostic_only | 0.7924 | 3.2022e-01 | 45.0 | 0.019 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 3e-04 | diagnostic_only | 0.7924 | 3.2179e-01 | 45.0 | 0.017 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 3e-04 | diagnostic_only | 0.7923 | 3.2259e-01 | 45.0 | 0.016 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 1e-04 | diagnostic_only | 0.7923 | 3.2112e-01 | 45.0 | 0.018 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 1e-03 | diagnostic_only | 0.7920 | 3.2656e-01 | 45.0 | 0.015 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 1e-03 | diagnostic_only | 0.7920 | 3.2703e-01 | 45.0 | 0.015 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 3e-03 | diagnostic_only | 0.7877 | 3.3354e-01 | 45.0 | 0.017 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 3e-03 | diagnostic_only | 0.7875 | 3.3371e-01 | 45.0 | 0.017 |
| compact_cube_3x3x3 | tikhonov | 1e-05 | 0e+00 | diagnostic_only | 0.7838 | 3.3000e-01 | 27.0 | 0.076 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 1e-02 | diagnostic_only | 0.7673 | 3.3973e-01 | 45.0 | 0.036 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 3e-02 | diagnostic_only | 0.7673 | 3.2575e-01 | 39.0 | 0.058 |
| default_cube_5x3x3 | group_sparse | 1e-05 | 3e-02 | diagnostic_only | 0.7673 | 3.2576e-01 | 39.0 | 0.058 |
| default_cube_5x3x3 | group_sparse | 1e-04 | 1e-02 | diagnostic_only | 0.7672 | 3.3972e-01 | 45.0 | 0.036 |
| compact_cube_3x3x3 | tikhonov | 1e-04 | 0e+00 | diagnostic_only | 0.7522 | 3.4766e-01 | 27.0 | 0.068 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 1e-03 | diagnostic_only | 0.7397 | 3.3984e-01 | 27.0 | 0.073 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 3e-04 | diagnostic_only | 0.7395 | 3.4951e-01 | 27.0 | 0.071 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 1e-04 | diagnostic_only | 0.7393 | 3.5229e-01 | 27.0 | 0.070 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 3e-03 | diagnostic_only | 0.7384 | 3.1434e-01 | 27.0 | 0.085 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 1e-03 | diagnostic_only | 0.7359 | 3.3299e-01 | 27.0 | 0.075 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 3e-04 | diagnostic_only | 0.7358 | 3.4253e-01 | 27.0 | 0.072 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 1e-04 | diagnostic_only | 0.7357 | 3.4527e-01 | 27.0 | 0.071 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 3e-03 | diagnostic_only | 0.7344 | 3.0770e-01 | 27.0 | 0.087 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 1e-02 | diagnostic_only | 0.7091 | 2.5563e-01 | 27.0 | 0.131 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 1e-02 | diagnostic_only | 0.7031 | 2.5195e-01 | 27.0 | 0.133 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 3e-02 | diagnostic_only | 0.6192 | 2.5742e-01 | 19.0 | 0.241 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 3e-02 | diagnostic_only | 0.6154 | 2.5930e-01 | 19.0 | 0.238 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 1e-01 | diagnostic_only | 0.4366 | 3.7463e-01 | 23.0 | 0.221 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 1e-01 | diagnostic_only | 0.4357 | 3.7523e-01 | 23.0 | 0.220 |
| compact_cube_3x3x3 | group_sparse | 1e-04 | 3e-01 | diagnostic_only | 0.0331 | 5.5675e-01 | 2.0 | 0.469 |
| compact_cube_3x3x3 | group_sparse | 1e-05 | 3e-01 | diagnostic_only | 0.0330 | 5.5679e-01 | 2.0 | 0.469 |

## Reading

- Sparse calibration did not yet pass the Level 1 gate, but it is informative:
  the best sparse setting improves min correlation from `0.7941`
  to `0.9283` and reduces the mean active source count
  from `45.0` to `2.0`.
- The remaining blocker is not only sparsity: max main-lobe error is still
  `152.70` deg and center energy share is
  `0.000`.
- Move next to phase/amplitude convention checks and more physical
  Huygens-surface or known-source priors.
