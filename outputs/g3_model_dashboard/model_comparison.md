# G3 Model Dashboard

This dashboard consolidates the current Level 1 inverse-model evidence.
It separates report-safe sanity checks from diagnostic bottlenecks and true-monitor rerun priorities.

## Executive Decision

- Do not claim final reduced-sampling proof yet.
- The immediate boundary is missing CST true near-field monitor CSVs.
- Export `full_grid_162` true-monitor data first; derive or compare the queued 32/120 layouts after that.

## Evidence Matrix

| Category | Artifact | Status | Trust level | Best setting | Min Corr | Max NMSE | Max lobe / deg | Sensors | Evidence |
|---|---|---|---|---|---:|---:|---:|---:|---|
| data_boundary | true_nearfield_monitor_gate | pending_source | blocked_by_authoritative_monitor_data | queue_rows=18, status_counts={'pending_source': 18} |  |  |  |  | `data\cst_true_nearfield_workpack\gate_report\true_nearfield_gate_summary.json` |
| trusted_sanity | scalar_spherical_nf_ff_baseline | strict_pass | trusted_angle_polarization_check | lmax=4, lambda=0.0, modes=24 | 0.9990 | 9.2604e-04 | 0.00 |  | `data\sampling_layouts\spherical_nf_ff_baseline\spherical_nf_ff_summary.json` |
| trusted_sanity | center_source_prior | corr_pass_nmse_near | trusted_data_path_check | full_grid_162, lambda=0.0001, grid=[1, 1, 1] | 0.9926 | 0.0178 | 0.00 | 162 | `data\sampling_layouts\cst_level1_center_source_check\cst_sampling_tradeoff_summary.json` |
| trusted_sanity | source_model_sweep_best | corr_pass_nmse_near | trusted_for_known_source_only | single_center, lambda=0.001, candidate=full_grid_162 | 0.9926 | 0.0178 | 0.00 |  | `data\sampling_layouts\cst_level1_source_model_sweep\cst_source_model_sweep_summary.json` |
| rerun_priority | scalar_spherical_nf_ff_reduced_layout | strict_pass | layout_priority_not_final_proof | geometric_farthest_32, lmax=4, lambda=1e-10 | 0.9991 | 9.7670e-04 | 0.00 | 32 | `data\sampling_layouts\spherical_nf_ff_tradeoff\spherical_nf_ff_tradeoff_summary.json` |
| model_bottleneck | generic_equivalent_source_grid | diagnostic_only | diagnostic_only | full_grid_162, lambda=0.0001, grid=[5, 3, 3] | 0.7930 | 0.3204 | 89.93 | 162 | `data\sampling_layouts\cst_level1_tradeoff\cst_sampling_tradeoff_summary.json` |
| model_bottleneck | generic_grid_convention_check | diagnostic_only | diagnostic_only | default_cube_5x3x3, current_phi_sign_flip, lambda=1e-05 | 0.7941 | 0.3184 | 59.96 |  | `data\sampling_layouts\cst_level1_convention_check\cst_convention_check_summary.json` |
| model_bottleneck | group_sparse_equivalent_sources | diagnostic_only | diagnostic_only | default_cube_5x3x3, group_sparse, l2=0.0001, group=0.3 | 0.9283 | 0.0811 | 152.70 |  | `data\sampling_layouts\cst_level1_sparse_calibration\cst_sparse_calibration_summary.json` |
| model_bottleneck | huygens_surface_prior | diagnostic_only | diagnostic_only | huygens_em_minus, field=radiating_dipole, lambda=0.01, smooth=0.0 | 0.7781 | 0.2642 | 166.71 | 162 | `data\sampling_layouts\cst_level1_huygens_baseline\huygens_reconstruction_summary.json` |

## Interpretation

- `true_nearfield_monitor_gate`: The immediate G3 boundary is data availability: real CST true near-field monitor CSVs are not present yet.
- `scalar_spherical_nf_ff_baseline`: The scalar angular SWE check strongly supports angle, phase, and polarization consistency.
- `center_source_prior`: Known center-source prior validates the current CST/Python angle and far-field comparison chain.
- `source_model_sweep_best`: The scan confirms that the current data chain works under a tight known-source prior.
- `scalar_spherical_nf_ff_reduced_layout`: The 32-point reduced layout is a true-monitor rerun priority, not final vector SWE proof.
- `generic_equivalent_source_grid`: The generic grid fails before reduced-layout comparison, so low-point claims must wait.
- `generic_grid_convention_check`: No simple global phase or theta/phi transform rescues the generic grid.
- `group_sparse_equivalent_sources`: Sparse support improves Corr/NMSE but does not fix the main-lobe/source-convention issue.
- `huygens_surface_prior`: The Huygens workflow is runnable, but current field-model/smoothness axes still miss the physics gate.

## Next Actions

| Priority | Owner | Gate | Action | Proof to close | Blocked by |
|---:|---|---|---|---|---|
| 1 | CST operator | true_monitor | Export authoritative full-grid CST true near-field monitor CSVs for the queued Level 1 cases. | python code\run_true_nearfield_gate.py reports no pending_source rows for full_grid_162. | CST monitor CSVs |
| 2 | Algorithm operator | post_true_monitor | After full-grid monitor CSVs exist, derive queued 32/120 layouts and compare them against the FarfieldPlot-derived reference. | true_nearfield_gate_summary.json reports reference_match or needs_physical_rerun with comparison metrics, not pending_source. | Full-grid monitor CSVs |
| 3 | Algorithm operator | physical_baseline | Rerun source-model, convention, scalar SWE, reduced-layout, and Huygens baselines on true-monitor input if the gate reports needs_physical_rerun. | A full-grid physical baseline reaches strict_pass or an approved near-pass before reduced-layout claims are written. | True-monitor gate comparison result |
| 4 | Report/PPT operator | wording | Use center-source and scalar SWE rows as sanity evidence; keep generic, sparse, and Huygens rows as diagnostic bottleneck evidence. | Reduced-layout claims explicitly say 'priority for true-monitor rerun' until a physical full-grid baseline passes. |  |

## Regenerate

```powershell
python code\build_g3_model_dashboard.py
```
