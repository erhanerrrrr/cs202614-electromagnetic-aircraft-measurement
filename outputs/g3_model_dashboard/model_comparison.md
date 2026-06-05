# G3 Model Dashboard

This dashboard consolidates the current Level 1 inverse-model evidence.
It separates report-safe sanity checks from diagnostic bottlenecks and true-monitor rerun priorities.

## Executive Decision

- Do not claim final reduced-sampling proof yet.
- The immediate boundary is missing CST true near-field monitor CSVs.
- Export `full_grid_162` true-monitor data first; derive or compare the queued 32/120 layouts after that.
- Mesh-safe Huygens is no longer blocked at CST export: both Level 1 E/H local-field paths are loaded, and the best batch branches now use real H-field currents. A frozen real E/H candidate is now accepted by every current Level 1 case, so the remaining bottleneck is explaining and validating that frozen operator.
- The frozen Huygens rule also has a rotation-covariance operator check; treat it as geometry-rule evidence, not as a substitute for independent CST source-family solves.
- The short x source-family solver-safe pilot now has matched 96-point local E/H artifacts; the active CST gate is ResultTree CSV export plus frozen-rule validation, not solver-runtime repair.

## Evidence Matrix

| Category | Artifact | Status | Trust level | Best setting | Min Corr | Max NMSE | Max lobe / deg | Sensors | Evidence |
|---|---|---|---|---|---:|---:|---:|---:|---|
| data_boundary | true_nearfield_monitor_gate | pending_source | blocked_by_authoritative_monitor_data | queue_rows=18, status_counts={'pending_source': 18} |  |  |  |  | `data\cst_true_nearfield_workpack\gate_report\true_nearfield_gate_summary.json` |
| trusted_sanity | scalar_spherical_nf_ff_baseline | strict_pass | trusted_angle_polarization_check | lmax=4, lambda=0.0, modes=24, ff_complex_l2=0.0316 | 0.9990 | 9.2604e-04 | 0.00 |  | `data\sampling_layouts\spherical_nf_ff_baseline\spherical_nf_ff_summary.json` |
| trusted_sanity | center_source_prior | corr_pass_nmse_near | trusted_data_path_check | full_grid_162, lambda=0.0001, grid=[1, 1, 1] | 0.9926 | 0.0178 | 0.00 | 162 | `data\sampling_layouts\cst_level1_center_source_check\cst_sampling_tradeoff_summary.json` |
| trusted_sanity | meshsafe_huygens_rotation_covariance | rotation_covariance_strict_pass | operator_covariance_not_new_cst_source | eh_love_equivalence_minus_j96; strict=18/18; base_accepted=2/2 | 1.0000 | 4.0382e-29 | 1.21e-06 | 96 | `data\sampling_layouts\cst_meshsafe_huygens_rotation_covariance\huygens_rotation_covariance_summary.json` |
| trusted_sanity | source_model_sweep_best | corr_pass_nmse_near | trusted_for_known_source_only | single_center, lambda=0.001, candidate=full_grid_162 | 0.9926 | 0.0178 | 0.00 |  | `data\sampling_layouts\cst_level1_source_model_sweep\cst_source_model_sweep_summary.json` |
| trusted_sanity | meshsafe_huygens_real_cst_batch | real_eh_frozen_rule_region_pass | real_cst_data_chain_not_final_huygens_proof | L1_short_dipole_z_1p2G:strict_pass/eh_love_equivalence_plus_j256/eta=1.000eta0/J=256.0000/H=loaded; L1_halfwave_dipole_z_1p2G:strict_pass/eh_love_equivalence_minus_j96/eta=1.000eta0/J=96.0000/H=loaded; frozen:frozen_real_eh_mixed_strict_region_pass/eh_love_equivalence_minus_j96/J=96.0000/accepted=2/2/strict=1/2 | 0.9989 | 7.3034e-04 | 0.00 | 96 | `data\sampling_layouts\cst_meshsafe_huygens_extrapolation_batch\meshsafe_huygens_batch_summary.json` |
| rerun_priority | scalar_spherical_nf_ff_reduced_layout | strict_pass | layout_priority_not_final_proof | geometric_farthest_32, lmax=4, lambda=1e-10, ff_complex_l2=0.0347 | 0.9991 | 9.7670e-04 | 0.00 | 32 | `data\sampling_layouts\spherical_nf_ff_tradeoff\spherical_nf_ff_tradeoff_summary.json` |
| rerun_priority | meshsafe_huygens_source_family_solver_safe_pilot | source_family_solver_safe_matched_eh_finished | matched_solver_evidence_not_huygens_proof | target=L1_short_dipole_x_1p2G; artifact_ready=7; ladder=none->efarfield96->efield24->hfield24->efield48->efield96->hfield96 |  |  |  | 96 | `outputs\cst_meshsafe_huygens_source_family_solver_safe_status\solver_safe_status_summary.json` |
| rerun_priority | meshsafe_huygens_source_family_workpack | source_family_solver_pilot_timed_out | historical_timeout_superseded_by_matched_solver_safe_pilot | solver_start_ok=1/1; max_elapsed_s=609.3600; max_time_steps=1457297; real_cst_api_trials=1 |  |  |  | 96 | `outputs\cst_meshsafe_huygens_source_family_solver_status\source_family_solver_status_summary.json` |
| model_bottleneck | generic_equivalent_source_grid | diagnostic_only | diagnostic_only | full_grid_162, lambda=0.0001, grid=[5, 3, 3] | 0.7930 | 0.3204 | 89.93 | 162 | `data\sampling_layouts\cst_level1_tradeoff\cst_sampling_tradeoff_summary.json` |
| model_bottleneck | generic_grid_convention_check | diagnostic_only | diagnostic_only | default_cube_5x3x3, current_phi_sign_flip, lambda=1e-05 | 0.7941 | 0.3184 | 59.96 |  | `data\sampling_layouts\cst_level1_convention_check\cst_convention_check_summary.json` |
| model_bottleneck | group_sparse_equivalent_sources | diagnostic_only | diagnostic_only | default_cube_5x3x3, group_sparse, l2=0.0001, group=0.3 | 0.9283 | 0.0811 | 152.70 |  | `data\sampling_layouts\cst_level1_sparse_calibration\cst_sparse_calibration_summary.json` |
| model_bottleneck | huygens_surface_prior | diagnostic_only | diagnostic_only | huygens_em_minus, field=radiating_dipole, lambda=0.01, smooth=0.0 | 0.7781 | 0.2642 | 166.71 | 162 | `data\sampling_layouts\cst_level1_huygens_baseline\huygens_reconstruction_summary.json` |
| model_bottleneck | meshsafe_huygens_impedance_stability | cross_case_impedance_disagreement | calibration_sensitivity_check | L1_halfwave_dipole_z_1p2G:eta=0.0312eta0/candidate_interior_eta; L1_short_dipole_z_1p2G:eta=0.0625eta0/candidate_interior_eta | 0.9989 | 8.0129e-04 | 0.00 | 96 | `data\sampling_layouts\cst_meshsafe_huygens_impedance_stability\impedance_stability_summary.json` |

## Interpretation

- `true_nearfield_monitor_gate`: The immediate G3 boundary is data availability: real CST true near-field monitor CSVs are not present yet.
- `scalar_spherical_nf_ff_baseline`: The scalar angular SWE check now includes total complex Etheta/Ephi residuals; it strongly supports angle, phase, and tangential-component consistency.
- `center_source_prior`: Known center-source prior validates the current CST/Python angle and far-field comparison chain.
- `meshsafe_huygens_rotation_covariance`: The frozen real E/H Huygens candidate is now checked under rigid rotations of the measured CST local E/H surface fields. This proves the Python current extraction and far-field operator are coordinate-covariant for the current vector rule; it does not replace real CST x/y, tilted, off-axis, or multi-source exports.
- `source_model_sweep_best`: The scan confirms that the current data chain works under a tight known-source prior.
- `meshsafe_huygens_real_cst_batch`: The mesh-safe route now uses real CST local probe curves for two Level 1 sources and the best diagnostic branches now use real E/H currents rather than the scalar eta_eff proxy (0/2 best settings use non-eta0 eta_eff). Matching H-field is now loaded for 2/2 cases and real E/H candidates are accepted for 2/2 cases; 2/2 best settings currently select a real-H branch, with J-scale values 96.0000, 256.0000, families eh_love_equivalence_minus, eh_love_equivalence_plus, ratio 2.6667, and calibration status cross_case_sign_and_scale_disagreement. The frozen-rule gate selects eh_love_equivalence_minus_j96 with status frozen_real_eh_mixed_strict_region_pass, accepted 2/2, strict 1/2, min Corr 0.9989, and max scaled NMSE 7.3034e-04. This is now an operator-stability question rather than a CST export blocker.
- `scalar_spherical_nf_ff_reduced_layout`: The 32-point reduced layout has strong power-pattern and complex-component sanity metrics; it is a true-monitor rerun priority, not final vector SWE proof.
- `meshsafe_huygens_source_family_solver_safe_pilot`: The short x source-family case now has completed 96-point local E-field and H-field solver evidence with near-field and far-field artifacts. This resolves the earlier runtime gate for the pilot case, but frozen-rule validation still requires ResultTree CSV export and comparison against the CST far-field reference.
- `meshsafe_huygens_source_family_workpack`: The original 600 s source-family solver pilot is now historical timeout evidence: it showed that CST could start and populate probe ResultTree entries, while the long-window solver-safe follow-up has since completed the matched 96-point E/H pilot for the same short x case.
- `generic_equivalent_source_grid`: The generic grid fails before reduced-layout comparison, so low-point claims must wait.
- `generic_grid_convention_check`: No simple global phase or theta/phi transform rescues the generic grid.
- `group_sparse_equivalent_sources`: Sparse support improves Corr/NMSE but does not fix the main-lobe/source-convention issue.
- `huygens_surface_prior`: The Huygens workflow is runnable, but current field-model/smoothness axes still miss the physics gate.
- `meshsafe_huygens_impedance_stability`: The lower-eta extension removed the immediate scan-boundary issue, but the two real CST cases now prefer different eta_eff values. Latest batch H-field coverage is 2/2 loaded and real E/H acceptance is 2/2; 2/2 best settings use a real-H branch; the older stability ResultTree flag is hfield_resulttree_missing. Therefore the scalar impedance route is a source-dependent calibrated proxy, not a single global physical impedance closure.

## Next Actions

| Priority | Owner | Gate | Action | Proof to close | Blocked by |
|---:|---|---|---|---|---|
| 1 | Independent workflow | meshsafe_huygens_physics | Export matched local E/H CSVs and far-field references from the completed short x 96-point E/H pilot, then evaluate the frozen eh_love_equivalence_minus_j96 Huygens rule without retuning before expanding to the remaining source-family cases. | Six automation-ready source-family rows have matched local E/H exports, far-field references, and the same frozen Huygens rule remains accepted without retuning. |  |
| 2 | CST operator | true_monitor | Use outputs\cst_true_nearfield_handoff\expected_true_monitor_files.csv, then export authoritative full-grid CST true near-field monitor CSVs for the queued Level 1 cases. | python code\run_true_nearfield_gate.py reports no pending_source rows for full_grid_162. | CST monitor CSVs |
| 3 | Algorithm operator | post_true_monitor | After full-grid monitor CSVs exist, derive queued 32/120 layouts and compare them against the FarfieldPlot-derived reference. | true_nearfield_gate_summary.json reports reference_match or needs_physical_rerun with comparison metrics, not pending_source. | Full-grid monitor CSVs |
| 4 | Algorithm operator | physical_baseline | Rerun source-model, convention, scalar SWE, reduced-layout, and Huygens baselines on true-monitor input if the gate reports needs_physical_rerun. | A full-grid physical baseline reaches strict_pass or an approved near-pass before reduced-layout claims are written. | True-monitor gate comparison result |
| 5 | Report/PPT operator | wording | Use center-source and scalar SWE rows as sanity evidence; keep generic, sparse, and Huygens rows as diagnostic bottleneck evidence. | Reduced-layout claims explicitly say 'priority for true-monitor rerun' until a physical full-grid baseline passes. |  |

## Regenerate

```powershell
python code\build_g3_model_dashboard.py
```
