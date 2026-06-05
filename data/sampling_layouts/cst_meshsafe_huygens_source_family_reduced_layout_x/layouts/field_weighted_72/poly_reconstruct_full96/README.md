# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_poly_full96_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_poly_full96_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9873` |
| Normal/total L2 ratio | `0.1586` |
| Dynamic range / dB | `12.49` |
| H tangential/total L2 ratio | `0.9994` |
| H normal/total L2 ratio | `0.0343` |
| H dynamic range / dB | `15.36` |
| Tangential E/H impedance / ohm | `370.427` |
| Tangential E/H eta0 ratio | `0.9833` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `outgoing_equivalence_minus` |
| Variant family | `outgoing_equivalence_minus` |
| Calibration mode | `fixed_eta0` |
| Uses real H-field | `False` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `` |
| Status | `region_shape_pass` |
| Correlation | `0.9967` |
| Normalized NMSE | `2.1218e-03` |
| Scale-fitted power NMSE | `8.1173e-04` |
| Main-lobe error / deg | `152.11` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.954` |
| Region-lobe min capture | `0.962` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9967 | 2.1218e-03 | 8.1173e-04 | 152.11 | 0.00 | 0.954 | 3.1096e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9967 | 2.1346e-03 | 8.1258e-04 | 152.11 | 0.00 | 0.954 | 3.1097e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9967 | 2.1598e-03 | 8.1328e-04 | 152.11 | 0.00 | 0.953 | 3.1097e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9967 | 2.1598e-03 | 8.1328e-04 | 152.11 | 0.00 | 0.953 | 3.1097e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9967 | 2.1852e-03 | 8.1408e-04 | 152.11 | 0.00 | 0.952 | 3.1097e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9967 | 2.1983e-03 | 8.1497e-04 | 152.11 | 0.00 | 0.951 | 3.1098e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9950 | 5.5725e-03 | 1.2133e-03 | 142.26 | 0.00 | 0.913 | 3.0473e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9943 | 1.0342e-02 | 1.3671e-03 | 156.89 | 0.00 | 0.860 | 3.0443e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | region_shape_pass | 0.9786 | 2.8087e-02 | 5.3840e-03 | 34.71 | 0.00 | 0.738 | 1.3924e+04 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9749 | 2.4614e-02 | 6.5085e-03 | 40.86 | 0.00 | 0.732 | 1.4214e+04 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_poly_full96_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72\poly_reconstruct_full96
```
