# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `24` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349418` |
| Tangential/total L2 ratio | `0.9897` |
| Normal/total L2 ratio | `0.1432` |
| Dynamic range / dB | `6.28` |
| H tangential/total L2 ratio | `0.9990` |
| H normal/total L2 ratio | `0.0454` |
| H dynamic range / dB | `6.73` |
| Tangential E/H impedance / ohm | `372.189` |
| Tangential E/H eta0 ratio | `0.9879` |

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
| Correlation | `0.4186` |
| Normalized NMSE | `6.1864e-01` |
| Scale-fitted power NMSE | `4.2790e-01` |
| Main-lobe error / deg | `81.24` |
| Region-lobe error / deg | `11.94` |
| Region-lobe Jaccard | `0.041` |
| Region-lobe min capture | `0.041` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4186 | 6.1864e-01 | 4.2790e-01 | 81.24 | 11.94 | 0.041 | 8.3058e+02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4183 | 6.1816e-01 | 4.2684e-01 | 81.24 | 11.94 | 0.042 | 8.2235e+02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | -0.1147 | 6.0315e-01 | 4.6931e-01 | 105.15 | 15.16 | 0.020 | 7.6652e-03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | -0.1519 | 5.6398e-01 | 4.5285e-01 | 99.60 | 15.68 | 0.026 | 7.7573e-03 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | -0.1848 | 5.9583e-01 | 4.9525e-01 | 22.02 | 12.26 | 0.029 | 7.9546e-03 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | -0.1848 | 5.9585e-01 | 4.9531e-01 | 22.02 | 12.26 | 0.029 | 7.9542e-03 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | -0.1850 | 5.9575e-01 | 4.9515e-01 | 22.02 | 12.26 | 0.029 | 7.9553e-03 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | -0.1850 | 5.9575e-01 | 4.9515e-01 | 22.02 | 12.26 | 0.029 | 7.9553e-03 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | -0.1852 | 5.9563e-01 | 4.9499e-01 | 22.02 | 12.26 | 0.029 | 7.9563e-03 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | -0.1852 | 5.9565e-01 | 4.9505e-01 | 22.02 | 12.26 | 0.029 | 7.9560e-03 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24
```
