# CST Level 1 Convention Check

This directory tests whether the Level 1 inverse-model bottleneck is caused by
a simple field convention mismatch. It keeps the data and layouts fixed, then
crosses source models with:

- near/far propagation phase signs;
- complex conjugation of measured fields;
- theta/phi polarization sign and channel-label changes.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Candidate layouts | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |

## Best Overall Setting

| Field | Value |
|---|---|
| Source model | `single_center` |
| Convention | `current_phi_sign_flip` |
| Lambda | `1e-04` |
| Status | `corr_pass_nmse_near` |
| Min Corr | `0.9926` |
| Max NMSE | `1.7784e-02` |
| Max main-lobe error / deg | `0.00` |
| Mean near-field residual | `9.883e-01` |

## Current Direct Baseline

| Field | Value |
|---|---|
| Source model | `single_center` |
| Status | `corr_pass_nmse_near` |
| Min Corr | `0.9926` |
| Max NMSE | `1.7784e-02` |
| Max main-lobe error / deg | `0.00` |

## Generic Grid Check

| Field | Current direct | Best generic-grid setting |
|---|---:|---:|
| Convention | `current_direct` | `current_phi_sign_flip` |
| Min Corr | `0.7941` | `0.7941` |
| Max NMSE | `3.1843e-01` | `3.1843e-01` |
| Max lobe error / deg | `109.90` | `59.96` |

## Setting Ranking

| Source model | Convention | Lambda | Status | Min Corr | Max NMSE | Max lobe error / deg | Mean NF residual |
|---|---|---:|---|---:|---:|---:|---:|
| single_center | current_phi_sign_flip | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | current_phi_sign_flip | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | reciprocal_flipped_phi_sign_flip | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | current_direct | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | reciprocal_flipped_complex_conjugate | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | current_direct | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | reciprocal_flipped_complex_conjugate | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.883e-01 |
| single_center | reciprocal_flipped_phi_sign_flip | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | current_complex_conjugate | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | reciprocal_flipped_direct | 1e-04 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | current_complex_conjugate | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | reciprocal_flipped_direct | 1e-05 | corr_pass_nmse_near | 0.9926 | 1.7784e-02 | 0.00 | 9.885e-01 |
| single_center | current_theta_phi_swap | 1e-05 | diagnostic_only | 0.9667 | 1.0000e+00 | 153.55 | 1.000e+00 |
| single_center | current_theta_phi_swap | 1e-04 | diagnostic_only | 0.9667 | 1.0000e+00 | 153.55 | 1.000e+00 |
| single_center | reciprocal_flipped_theta_phi_swap | 1e-05 | diagnostic_only | 0.7999 | 1.0000e+00 | 158.19 | 1.000e+00 |
| single_center | reciprocal_flipped_theta_phi_swap | 1e-04 | diagnostic_only | 0.7998 | 1.0000e+00 | 158.19 | 1.000e+00 |
| default_cube_5x3x3 | current_phi_sign_flip | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 59.96 | 5.558e-01 |
| default_cube_5x3x3 | current_direct | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 109.90 | 5.558e-01 |
| default_cube_5x3x3 | reciprocal_flipped_complex_conjugate | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 109.90 | 5.558e-01 |
| default_cube_5x3x3 | reciprocal_flipped_phi_sign_flip | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 69.95 | 5.547e-01 |
| default_cube_5x3x3 | current_complex_conjugate | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 59.96 | 5.547e-01 |
| default_cube_5x3x3 | reciprocal_flipped_direct | 1e-05 | diagnostic_only | 0.7941 | 3.1843e-01 | 59.96 | 5.547e-01 |
| default_cube_5x3x3 | current_phi_sign_flip | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 59.96 | 5.558e-01 |
| default_cube_5x3x3 | current_direct | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 109.90 | 5.558e-01 |
| default_cube_5x3x3 | reciprocal_flipped_complex_conjugate | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 109.90 | 5.558e-01 |
| default_cube_5x3x3 | reciprocal_flipped_phi_sign_flip | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 69.95 | 5.548e-01 |
| default_cube_5x3x3 | current_complex_conjugate | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 59.96 | 5.548e-01 |
| default_cube_5x3x3 | reciprocal_flipped_direct | 1e-04 | diagnostic_only | 0.7930 | 3.2036e-01 | 59.96 | 5.548e-01 |
| default_cube_5x3x3 | reciprocal_flipped_theta_phi_swap | 1e-05 | diagnostic_only | 0.4465 | 5.8251e-01 | 44.99 | 7.891e-01 |
| default_cube_5x3x3 | current_theta_phi_swap | 1e-05 | diagnostic_only | 0.4465 | 5.8218e-01 | 84.86 | 7.895e-01 |
| default_cube_5x3x3 | reciprocal_flipped_theta_phi_swap | 1e-04 | diagnostic_only | 0.4458 | 5.8191e-01 | 44.99 | 7.891e-01 |
| default_cube_5x3x3 | current_theta_phi_swap | 1e-04 | diagnostic_only | 0.4458 | 5.8158e-01 | 84.86 | 7.895e-01 |

## Reading

- The current em_core convention remains the best overall setting on this Level 1 check.
- Several sign-equivalent settings tie in far-field power metrics, which is expected for these single z-dipole Level 1 cases.
- This argues against a simple global phase-sign, complex-conjugation, or theta/phi label error.
- The generic grid should still be treated as a source-prior/model mismatch problem, not as a solved sampling result.

## Important Boundary

The current Level 1 near-field table is derived from CST FarfieldPlot list
evaluation at the measurement directions. It is a solver-safe angular sample,
not a full-wave near-field monitor export. This check is therefore a convention
and model-risk diagnostic; it is not final proof for reduced sensor layouts.
