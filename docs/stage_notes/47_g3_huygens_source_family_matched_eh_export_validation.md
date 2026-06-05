# S47 G3 Huygens source-family matched E/H export validation

## What changed

The short x-oriented source-family pilot `L1_short_dipole_x_1p2G` has moved from
"matched E/H CST solver evidence exists" to a closed pilot data gate:

- The 96-point local E-field ResultTree export is complete.
- The matching 96-point local H-field ResultTree export is complete.
- The CST FarfieldPlot far-field reference for the same x-oriented source is exported.
- The Python Huygens extrapolation gate has been run on the matched local E/H CSVs.

This means the current CST issue is no longer "CST cannot run" or "the pilot
cannot produce data". The remaining work is operator strictness, reduced-layout
testing, and source-family generalization.

## Evidence

| Evidence | Path | Current value |
|---|---|---:|
| Local E-field CSV | `data/cst_exports/level1_meshsafe_huygens_source_family/L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv` | 288 rows |
| Local H-field CSV | `data/cst_exports/level1_meshsafe_huygens_source_family/L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_hfield.csv` | 288 rows |
| CST far-field reference | `data/cst_exports/level1_meshsafe_huygens_source_family/L1_short_dipole_x_1p2G_farfield.csv` | 2664 rows |
| Huygens validation summary | `data/sampling_layouts/cst_meshsafe_huygens_source_family_matched_eh_x/meshsafe_huygens_extrapolation_summary.json` | complete |
| Huygens validation table | `data/sampling_layouts/cst_meshsafe_huygens_source_family_matched_eh_x/meshsafe_huygens_extrapolation_results.csv` | 10 variants |

Best real E/H validation result:

- Variant: `eh_love_equivalence_minus`
- Status: `region_shape_pass`
- Correlation: `0.9966187532`
- Scaled power NMSE: `8.179603314e-4`
- Region main-lobe error: `0 deg`
- Region Jaccard: `0.9440809042`
- Reference region capture: `0.9550079866`
- Predicted region precision: `0.9984346816`

Frozen `j96` rule check:

- Variant: `eh_love_equivalence_minus_j96`
- Status: `region_shape_pass`
- Correlation: `0.9953722661`
- Scaled power NMSE: `1.118942244e-3`
- Region main-lobe error: `0 deg`
- Region Jaccard: `0.9034564958`
- Reference region capture: `0.9185691479`
- Predicted region precision: `1.0`

The pointwise argmax main-lobe angle is still unstable for this broad
ring-shaped pattern, so the report-safe gate should use the region-lobe metrics
already tracked by `main_lobe_region_*`.

## Commands

```powershell
python code\export_cst_meshsafe_huygens_results.py --project "C:\csttmp\huy_sf_safe_efield96_s\L1_short_dipole_x_1p2G_efield96.cst" --case-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_pilot_case.csv --probe-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_probe_96.csv --sample-id L1_short_dipole_x_1p2G --field-kind e --out-dir outputs\cst_meshsafe_huygens_source_family_efield96_export --inspect-tree --attempt-export --overwrite --inspect-timeout-seconds 300
python code\export_cst_meshsafe_huygens_results.py --project "C:\csttmp\huy_sf_safe_hfield96_s\L1_short_dipole_x_1p2G_hfield96.cst" --case-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_pilot_case.csv --probe-csv data\cst_meshsafe_huygens_source_family_solver_safe_pilot\solver_safe_probe_96.csv --sample-id L1_short_dipole_x_1p2G --field-kind h --out-dir outputs\cst_meshsafe_huygens_source_family_hfield96_export --inspect-tree --attempt-export --overwrite --inspect-timeout-seconds 300
python code\export_cst_farfield_results.py --project "C:\csttmp\huy_sf_safe_efield96_s\L1_short_dipole_x_1p2G_efield96.cst" --sample-id L1_short_dipole_x_1p2G --frequency-hz 1200000000 --source-config orientation_x_short --carrier-model level1_source_family_meshsafe_huygens --working-state single_source_on --nearfield-out data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfieldplot_13m_nearfield.csv --farfield-out data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv --summary-out outputs\cst_farfield_export\source_family\L1_short_dipole_x_1p2G_export_summary.json --stdout-log outputs\cst_farfield_export\source_family\L1_short_dipole_x_1p2G_stdout.log --timeout-seconds 900
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv --local-hfield data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_hfield.csv --farfield data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_matched_eh_x --impedance-factors 1 --eh-j-scale-factors 96
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

## Interpretation

The solver-safe CST path has now proven the following for the source-family
pilot:

1. CST can solve the mesh-safe local Huygens configuration under a long enough
   time window.
2. CST ResultTree curves can be parsed into the local E/H CSV contract.
3. A same-source far-field reference can be exported through FarfieldPlot.
4. The current real E/H Huygens diagnostic and its frozen `j96` check both
   preserve the main-lobe region shape.

This is still a pilot, not final reduced-sampling proof. The next stage should
reuse the frozen operator without retuning and test:

- reduced local layouts derived from the 96-point shell,
- additional x/y/off-axis source-family cases,
- stricter vector surface-integral conventions before report-level Huygens
  claims.
