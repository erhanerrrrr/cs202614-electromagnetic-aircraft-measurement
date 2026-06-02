# Spherical NF-FF Reduced-Layout Tradeoff

This directory stores a reduced-layout extension of the spherical near-field to
far-field sanity baseline. It fits each candidate sensor subset with scalar
spherical-harmonic expansions for tangential `Etheta` and `Ephi`, then evaluates
the fitted field on the far-field angular grid.

This is not a full vector spherical-wave expansion. Its job is to rank reduced
sampling layouts before spending CST time on true near-field monitor reruns.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |
| Layout table | `data\sampling_layouts\hemisphere_sampling_candidates.csv` |

## Best Candidate Per Layout

| Candidate | Sensors | Method | Lmax | Lambda | Modes | Status | Min Corr | Max NMSE | Max lobe error / deg | Max NF fit error | Max condition |
|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| geometric_farthest_32 | 32 | geometric_farthest | 4 | 1e-10 | 24 | strict_pass | 0.9991 | 9.7670e-04 | 0.00 | 1.4911e-02 | 7.398e+01 |
| dictionary_weighted_32 | 32 | dictionary_weighted | 4 | 1e-10 | 24 | strict_pass | 0.9992 | 1.0891e-03 | 0.00 | 1.5122e-02 | 7.843e+01 |
| dictionary_weighted_48 | 48 | dictionary_weighted | 4 | 1e-10 | 24 | strict_pass | 0.9994 | 9.1960e-04 | 0.00 | 1.3170e-02 | 7.451e+01 |
| geometric_farthest_48 | 48 | geometric_farthest | 4 | 1e-10 | 24 | strict_pass | 0.9994 | 6.1010e-04 | 0.00 | 1.3413e-02 | 7.689e+01 |
| fibonacci_snap_81 | 81 | fibonacci_snap | 4 | 0e+00 | 24 | strict_pass | 0.9996 | 2.9256e-04 | 0.00 | 1.2049e-02 | 7.397e+01 |
| task_driven_81 | 81 | task_driven | 4 | 0e+00 | 24 | strict_pass | 0.9995 | 4.0858e-04 | 0.00 | 1.5481e-02 | 7.785e+01 |
| geometric_farthest_81 | 81 | geometric_farthest | 4 | 1e-10 | 24 | strict_pass | 0.9995 | 4.3342e-04 | 0.00 | 1.5676e-02 | 8.423e+01 |
| dictionary_weighted_81 | 81 | dictionary_weighted | 4 | 1e-10 | 24 | strict_pass | 0.9994 | 9.7645e-04 | 0.00 | 1.6670e-02 | 9.223e+01 |
| fibonacci_snap_120 | 120 | fibonacci_snap | 4 | 0e+00 | 24 | strict_pass | 0.9996 | 2.7067e-04 | 0.00 | 1.3327e-02 | 6.745e+01 |
| task_driven_120 | 120 | task_driven | 4 | 0e+00 | 24 | strict_pass | 0.9996 | 2.8082e-04 | 0.00 | 1.2793e-02 | 6.916e+01 |
| geometric_farthest_120 | 120 | geometric_farthest | 4 | 1e-10 | 24 | strict_pass | 0.9996 | 2.8219e-04 | 0.00 | 1.3211e-02 | 6.981e+01 |
| dictionary_weighted_120 | 120 | dictionary_weighted | 4 | 1e-10 | 24 | strict_pass | 0.9995 | 5.9773e-04 | 0.00 | 1.7524e-02 | 9.157e+01 |
| full_grid_162 | 162 | full_grid | 4 | 0e+00 | 24 | strict_pass | 0.9990 | 9.2604e-04 | 0.00 | 2.5766e-02 | 1.051e+02 |
| fibonacci_snap_32 | 32 | fibonacci_snap | 8 | 0e+00 | 80 | diagnostic_only | 0.4020 | 5.5378e-01 | 67.14 | 1.7624e-15 | 2.136e+00 |
| task_driven_32 | 32 | task_driven | 5 | 0e+00 | 35 | diagnostic_only | 0.9739 | 1.0673e-01 | 79.94 | 2.1761e-15 | 1.103e+03 |
| fibonacci_snap_48 | 48 | fibonacci_snap | 3 | 0e+00 | 15 | diagnostic_only | 0.9784 | 1.6099e-02 | 17.39 | 5.0304e-02 | 1.918e+01 |
| task_driven_48 | 48 | task_driven | 8 | 0e+00 | 80 | diagnostic_only | 0.8311 | 3.3350e-01 | 79.81 | 1.9173e-15 | 2.085e+01 |

## Reading

- The smallest strict reduced layout is `geometric_farthest_32` with 32 sensors, `lmax=4`, and `lambda=1e-10`.
- Promote this layout, plus one conservative 120-sensor layout, into the next true CST near-field monitor workpack.
- Keep the full 162-point grid as the physical reference and report anchor.

## Files

| File | Purpose |
|---|---|
| `spherical_nf_ff_tradeoff_results.csv` | Raw case-level results across candidates, samples, `lmax`, and regularization. |
| `spherical_nf_ff_tradeoff_by_setting.csv` | Aggregated setting-level results for each candidate. |
| `spherical_nf_ff_tradeoff_best_by_candidate.csv` | One best setting per candidate layout. |
| `spherical_nf_ff_tradeoff_summary.json` | Machine-readable summary and recommended reduced candidate. |

## Command

```powershell
python code\run_spherical_nf_ff_tradeoff.py
```

## Boundary

This is a scalar angular NF-FF diagnostic on the current FarfieldPlot-derived near-field table. Use it to rank sampling layouts before true CST near-field monitor reruns, not as final vector SWE proof.
