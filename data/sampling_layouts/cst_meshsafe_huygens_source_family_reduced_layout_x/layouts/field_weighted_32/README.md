# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_32_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_32_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `32` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.34995` |
| Tangential/total L2 ratio | `0.9897` |
| Normal/total L2 ratio | `0.1434` |
| Dynamic range / dB | `8.79` |
| H tangential/total L2 ratio | `0.9992` |
| H normal/total L2 ratio | `0.0409` |
| H dynamic range / dB | `10.75` |
| Tangential E/H impedance / ohm | `372.64` |
| Tangential E/H eta0 ratio | `0.9891` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `hfield_electric_only` |
| Variant family | `hfield_electric_only` |
| Calibration mode | `real_hfield_only` |
| Uses real H-field | `True` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `1.0` |
| Status | `diagnostic_only` |
| Correlation | `0.4258` |
| Normalized NMSE | `6.9809e-01` |
| Scale-fitted power NMSE | `4.1720e-01` |
| Main-lobe error / deg | `123.93` |
| Region-lobe error / deg | `120.13` |
| Region-lobe Jaccard | `0.010` |
| Region-lobe min capture | `0.009` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4258 | 6.9809e-01 | 4.1720e-01 | 123.93 | 120.13 | 0.010 | 1.3116e+03 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4228 | 7.0135e-01 | 4.2199e-01 | 123.93 | 120.13 | 0.010 | 1.3088e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.2035 | 4.5308e-01 | 3.2119e-01 | 57.86 | 11.94 | 0.058 | 1.1855e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.2030 | 5.0825e-01 | 3.6965e-01 | 107.12 | 55.52 | 0.057 | 1.0358e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.1728 | 4.9783e-01 | 3.6134e-01 | 60.20 | 14.33 | 0.054 | 1.1623e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.1728 | 4.9827e-01 | 3.6188e-01 | 60.20 | 14.33 | 0.054 | 1.1606e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.1727 | 4.9807e-01 | 3.6162e-01 | 60.20 | 14.33 | 0.054 | 1.1615e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.1727 | 4.9807e-01 | 3.6162e-01 | 60.20 | 14.33 | 0.054 | 1.1615e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.1727 | 4.9786e-01 | 3.6137e-01 | 60.20 | 14.33 | 0.054 | 1.1623e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.1727 | 4.9830e-01 | 3.6190e-01 | 60.20 | 14.33 | 0.054 | 1.1607e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_32_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_32
```
