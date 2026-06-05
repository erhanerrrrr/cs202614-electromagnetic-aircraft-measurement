# CST Mesh-Safe Huygens Reduced Layout Gate

This directory tests whether the validated short-x matched E/H source-family pilot
survives deterministic thinning of the exported 96-point local CST sphere.

The run does not rerun CST. It subsets the already-exported local E/H probe CSVs,
assigns each original 96-point surface cell to the nearest retained probe for
quadrature weighting, and reruns the same Huygens extrapolation gate. The
decision metric is the frozen `eh_love_equivalence_minus_j96` row, not a per-layout
retuned best row.

## Gate

- Status: `reduced_layout_validated`
- Frozen accepted layouts: `13/25`
- Deployable frozen accepted layouts: `9`
- Reconstructed frozen accepted layouts: `12`
- Smallest deployable frozen pass: `fibonacci_snap_24` with `24` sensors

## Frozen-Operator Results

| Layout | Mode | Method | Sensors | Frozen status | Corr | Scaled NMSE | Region error / deg | Region Jaccard | E holdout NRMSE | H holdout NRMSE | Accepted |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| fibonacci_snap_24 | direct_subset | fibonacci_snap | 24 | diagnostic_only | -0.3819 | 0.615 | 63.4 | 0.0123 |  |  | False |
| field_weighted_24 | direct_subset | field_weighted | 24 | diagnostic_only | -0.1519 | 0.4528 | 15.7 | 0.0265 |  |  | False |
| geometric_farthest_24 | direct_subset | geometric_farthest | 24 | diagnostic_only | -0.3849 | 0.5625 | 69.9 | 0.0000 |  |  | False |
| fibonacci_snap_24 | poly_reconstruct_full96 | fibonacci_snap | 24 | region_shape_pass | 0.9942 | 0.001403 | 8.54e-07 | 0.9095 | 0.0418 | 0.0578 | True |
| field_weighted_24 | poly_reconstruct_full96 | field_weighted | 24 | region_shape_pass | 0.9940 | 0.001479 | 8.54e-07 | 0.8982 | 0.049 | 0.07 | True |
| geometric_farthest_24 | poly_reconstruct_full96 | geometric_farthest | 24 | region_shape_pass | 0.9927 | 0.001783 | 8.54e-07 | 0.9322 | 0.0467 | 0.0644 | True |
| fibonacci_snap_32 | direct_subset | fibonacci_snap | 32 | diagnostic_only | -0.0204 | 0.3997 | 40.4 | 0.0012 |  |  | False |
| field_weighted_32 | direct_subset | field_weighted | 32 | diagnostic_only | 0.2035 | 0.3212 | 11.9 | 0.0583 |  |  | False |
| geometric_farthest_32 | direct_subset | geometric_farthest | 32 | diagnostic_only | -0.2717 | 0.4367 | 69.9 | 0.0012 |  |  | False |
| fibonacci_snap_32 | poly_reconstruct_full96 | fibonacci_snap | 32 | region_shape_pass | 0.9950 | 0.001219 | 0 | 0.9058 | 0.0428 | 0.0594 | True |
| field_weighted_32 | poly_reconstruct_full96 | field_weighted | 32 | region_shape_pass | 0.9943 | 0.001393 | 8.54e-07 | 0.9155 | 0.0453 | 0.0618 | True |
| geometric_farthest_32 | poly_reconstruct_full96 | geometric_farthest | 32 | region_shape_pass | 0.9943 | 0.00139 | 0 | 0.9143 | 0.042 | 0.0522 | True |
| fibonacci_snap_48 | direct_subset | fibonacci_snap | 48 | diagnostic_only | 0.3493 | 0.3274 | 15 | 0.1779 |  |  | False |
| field_weighted_48 | direct_subset | field_weighted | 48 | diagnostic_only | 0.3877 | 0.279 | 8.72 | 0.0381 |  |  | False |
| geometric_farthest_48 | direct_subset | geometric_farthest | 48 | diagnostic_only | 0.0584 | 0.3225 | 56.4 | 0.0153 |  |  | False |
| fibonacci_snap_48 | poly_reconstruct_full96 | fibonacci_snap | 48 | region_shape_pass | 0.9949 | 0.001231 | 0 | 0.9149 | 0.0449 | 0.0625 | True |
| field_weighted_48 | poly_reconstruct_full96 | field_weighted | 48 | region_shape_pass | 0.9952 | 0.001177 | 8.54e-07 | 0.9070 | 0.0447 | 0.0639 | True |
| geometric_farthest_48 | poly_reconstruct_full96 | geometric_farthest | 48 | region_shape_pass | 0.9948 | 0.001249 | 0 | 0.9052 | 0.0421 | 0.0611 | True |
| fibonacci_snap_72 | direct_subset | fibonacci_snap | 72 | diagnostic_only | 0.0961 | 0.2987 | 50 | 0.0000 |  |  | False |
| field_weighted_72 | direct_subset | field_weighted | 72 | diagnostic_only | 0.6205 | 0.1756 | 89.9 | 0.0739 |  |  | False |
| geometric_farthest_72 | direct_subset | geometric_farthest | 72 | diagnostic_only | 0.4256 | 0.2104 | 54.3 | 0.0560 |  |  | False |
| fibonacci_snap_72 | poly_reconstruct_full96 | fibonacci_snap | 72 | region_shape_pass | 0.9946 | 0.001305 | 0 | 0.9184 | 0.0547 | 0.0909 | True |
| field_weighted_72 | poly_reconstruct_full96 | field_weighted | 72 | region_shape_pass | 0.9950 | 0.001213 | 8.54e-07 | 0.9130 | 0.0769 | 0.0797 | True |
| geometric_farthest_72 | poly_reconstruct_full96 | geometric_farthest | 72 | region_shape_pass | 0.9943 | 0.001384 | 0 | 0.9054 | 0.0431 | 0.0679 | True |
| full_96 | direct_subset_full | full | 96 | region_shape_pass | 0.9954 | 0.001119 | 0 | 0.9035 |  |  | True |

## Interpretation

- `geometric_farthest` and `fibonacci_snap` are deployment-style layouts because
  they use geometry only.
- `field_weighted` is a diagnostic lower-bound layout because it uses measured
  E/H field energy from the full 96-point pilot.
- A pass here supports the sampling-plan claim that the local Huygens surface can
  be sampled sparsely and reconstructed before propagation to the 13 m
  measurement shell, provided the same fixed operator is used on additional
  source orientations.

## Files

| File | Purpose |
|---|---|
| `reduced_layout_summary.csv` | Per-layout frozen and best-row metrics plus aggregated quadrature weights. |
| `reduced_layout_summary.json` | Machine-readable gate summary. |
| `layouts/*_local_efield.csv` | Generated subset E-field inputs. |
| `layouts/*_local_hfield.csv` | Generated subset H-field inputs. |
| `layouts/*_poly_full96_efield.csv` | Polynomially reconstructed full 96-point E-field inputs. |
| `layouts/*_poly_full96_hfield.csv` | Polynomially reconstructed full 96-point H-field inputs. |
| `layouts/*/meshsafe_huygens_extrapolation_results.csv` | Per-layout Huygens variant metrics. |
