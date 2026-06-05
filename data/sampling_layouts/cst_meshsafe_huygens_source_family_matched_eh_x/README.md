# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv` |
| Local Huygens H field | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9868` |
| Normal/total L2 ratio | `0.1622` |
| Dynamic range / dB | `10.89` |
| H tangential/total L2 ratio | `0.9994` |
| H normal/total L2 ratio | `0.0339` |
| H dynamic range / dB | `16.64` |
| Tangential E/H impedance / ohm | `370.499` |
| Tangential E/H eta0 ratio | `0.9835` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `eh_love_equivalence_minus` |
| Variant family | `eh_love_equivalence_minus` |
| Calibration mode | `real_eh_surface_currents` |
| Uses real H-field | `True` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `1.0` |
| Status | `region_shape_pass` |
| Correlation | `0.9966` |
| Normalized NMSE | `2.0014e-03` |
| Scale-fitted power NMSE | `8.1796e-04` |
| Main-lobe error / deg | `66.97` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.944` |
| Region-lobe min capture | `0.955` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9966 | 2.0014e-03 | 8.1796e-04 | 66.97 | 0.00 | 0.944 | 3.1037e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9966 | 2.0044e-03 | 8.1940e-04 | 69.35 | 0.00 | 0.944 | 3.1036e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9966 | 2.0068e-03 | 8.1971e-04 | 69.35 | 0.00 | 0.944 | 3.1037e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9966 | 2.0068e-03 | 8.1971e-04 | 69.35 | 0.00 | 0.944 | 3.1037e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9966 | 2.0127e-03 | 8.2017e-04 | 66.97 | 0.00 | 0.944 | 3.1039e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9966 | 2.0127e-03 | 8.2157e-04 | 69.35 | 0.00 | 0.944 | 3.1037e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9954 | 5.7561e-03 | 1.1189e-03 | 19.11 | 0.00 | 0.903 | 3.0408e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9940 | 1.1688e-02 | 1.4590e-03 | 159.28 | 0.00 | 0.828 | 3.0405e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | region_shape_pass | 0.9793 | 2.8018e-02 | 5.0476e-03 | 158.70 | 0.00 | 0.739 | 1.4047e+04 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | shape_pass_lobe_ambiguous | 0.9728 | 2.6369e-02 | 6.9563e-03 | 40.86 | 0.00 | 0.686 | 1.4237e+04 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_matched_eh_x
```
