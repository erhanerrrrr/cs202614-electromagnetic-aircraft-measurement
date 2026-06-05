# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_24_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_24_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `24` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.34951` |
| Tangential/total L2 ratio | `0.9873` |
| Normal/total L2 ratio | `0.1586` |
| Dynamic range / dB | `10.64` |
| H tangential/total L2 ratio | `0.9998` |
| H normal/total L2 ratio | `0.0203` |
| H dynamic range / dB | `15.24` |
| Tangential E/H impedance / ohm | `369.759` |
| Tangential E/H eta0 ratio | `0.9815` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `electric_only_outgoing` |
| Variant family | `electric_only_outgoing` |
| Calibration mode | `fixed_eta0` |
| Uses real H-field | `False` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `` |
| Status | `diagnostic_only` |
| Correlation | `0.4122` |
| Normalized NMSE | `6.4850e-01` |
| Scale-fitted power NMSE | `3.8443e-01` |
| Main-lobe error / deg | `115.25` |
| Region-lobe error / deg | `5.53` |
| Region-lobe Jaccard | `0.015` |
| Region-lobe min capture | `0.016` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4122 | 6.4850e-01 | 3.8443e-01 | 115.25 | 5.53 | 0.015 | 1.1788e+03 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4016 | 6.5254e-01 | 3.9172e-01 | 115.25 | 109.22 | 0.014 | 1.1271e+03 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | -0.3001 | 7.0403e-01 | 5.9847e-01 | 93.78 | 79.94 | 0.001 | 5.3946e-03 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | -0.3752 | 7.0400e-01 | 6.0126e-01 | 93.78 | 79.88 | 0.000 | 5.8876e-03 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | -0.3753 | 7.0400e-01 | 6.0129e-01 | 93.78 | 79.88 | 0.000 | 5.8874e-03 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | -0.3757 | 7.0381e-01 | 6.0109e-01 | 93.78 | 79.88 | 0.000 | 5.8919e-03 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | -0.3757 | 7.0381e-01 | 6.0109e-01 | 93.78 | 79.88 | 0.000 | 5.8919e-03 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | -0.3762 | 7.0361e-01 | 6.0089e-01 | 93.78 | 79.88 | 0.000 | 5.8963e-03 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | -0.3762 | 7.0361e-01 | 6.0091e-01 | 93.78 | 79.88 | 0.000 | 5.8961e-03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | -0.3849 | 6.7024e-01 | 5.6255e-01 | 98.35 | 69.91 | 0.000 | 6.1678e-03 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_24_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_24\direct_subset
```
