# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_poly_full96_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_poly_full96_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9873` |
| Normal/total L2 ratio | `0.1587` |
| Dynamic range / dB | `12.06` |
| H tangential/total L2 ratio | `0.9998` |
| H normal/total L2 ratio | `0.0181` |
| H dynamic range / dB | `16.91` |
| Tangential E/H impedance / ohm | `369.616` |
| Tangential E/H eta0 ratio | `0.9811` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `eh_love_equivalence_plus_j96` |
| Variant family | `eh_love_equivalence_plus` |
| Calibration mode | `real_eh_j_scale_scan` |
| Uses real H-field | `True` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `96.0` |
| Status | `strict_pass` |
| Correlation | `0.9944` |
| Normalized NMSE | `6.4615e-03` |
| Scale-fitted power NMSE | `1.3431e-03` |
| Main-lobe error / deg | `0.00` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.890` |
| Region-lobe min capture | `0.907` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | strict_pass | 0.9944 | 6.4615e-03 | 1.3431e-03 | 0.00 | 0.00 | 0.890 | 3.0773e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9964 | 1.7498e-03 | 8.6617e-04 | 106.65 | 0.00 | 0.952 | 3.1335e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9964 | 1.7568e-03 | 8.6729e-04 | 106.65 | 0.00 | 0.952 | 3.1335e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9964 | 1.7672e-03 | 8.6779e-04 | 106.65 | 0.00 | 0.952 | 3.1336e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9964 | 1.7672e-03 | 8.6779e-04 | 106.65 | 0.00 | 0.952 | 3.1336e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9964 | 1.7776e-03 | 8.6839e-04 | 106.65 | 0.00 | 0.951 | 3.1336e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9964 | 1.7847e-03 | 8.6952e-04 | 106.65 | 0.00 | 0.951 | 3.1336e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9949 | 4.7513e-03 | 1.2315e-03 | 139.90 | 0.00 | 0.915 | 3.0633e-02 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9804 | 2.3625e-02 | 4.9340e-03 | 36.13 | 0.00 | 0.749 | 1.4358e+04 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | shape_pass_lobe_ambiguous | 0.9779 | 3.3655e-02 | 5.4590e-03 | 33.77 | 0.00 | 0.674 | 1.4235e+04 |

## Reading

- This Python gate consumes matched real CST local E-field and H-field probe values.
- Real dual-field variants evaluate `J = n x H_t` and `M = -n x E_t`; J-scale variants keep the measured H-field distribution and scan only a global operator normalization.
- The older E-only impedance scan remains as a calibration baseline.
- The equivalent-current formulas are still a diagnostic Huygens/Kirchhoff
  operator rather than final report-level Stratton-Chu evidence. Treat the
  scalar impedance scan as a calibration baseline and the real E/H J-scale
  variants as the next operator-normalization gate to refine.
- Broad, ring-like, or multi-peak reference patterns can make the single-point
  main-lobe metric stricter than the whole-pattern shape metrics. Treat
  `region_shape_pass` or `shape_pass_lobe_ambiguous` as good data-chain
  signals, not as final physics passes.
- Final G3 evidence still needs a stricter vector surface-integral operator,
  source-family cross-checks, and reduced-layout propagation to the 13 m
  measurement shell.

## Generated Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_field_quality.csv` | Local field completeness and geometry/audit metrics. |
| `meshsafe_huygens_extrapolation_results.csv` | Per-variant far-field comparison metrics. |
| `meshsafe_huygens_best_farfield.csv` | Best diagnostic predicted/reference far-field table. |
| `meshsafe_huygens_extrapolation_summary.json` | Machine-readable summary. |

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_poly_full96_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48\poly_reconstruct_full96
```
