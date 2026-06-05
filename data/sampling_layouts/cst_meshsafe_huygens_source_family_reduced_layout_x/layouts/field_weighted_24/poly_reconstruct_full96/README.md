# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_poly_full96_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_poly_full96_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9874` |
| Normal/total L2 ratio | `0.1585` |
| Dynamic range / dB | `12.33` |
| H tangential/total L2 ratio | `0.9991` |
| H normal/total L2 ratio | `0.0417` |
| H dynamic range / dB | `18.44` |
| Tangential E/H impedance / ohm | `372.906` |
| Tangential E/H eta0 ratio | `0.9898` |

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
| Correlation | `0.9934` |
| Normalized NMSE | `9.0284e-03` |
| Scale-fitted power NMSE | `1.6424e-03` |
| Main-lobe error / deg | `0.00` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.861` |
| Region-lobe min capture | `0.881` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | strict_pass | 0.9934 | 9.0284e-03 | 1.6424e-03 | 0.00 | 0.00 | 0.861 | 2.9865e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9957 | 2.2476e-03 | 1.0725e-03 | 149.72 | 0.00 | 0.945 | 3.0544e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9957 | 2.2444e-03 | 1.0732e-03 | 149.72 | 0.00 | 0.945 | 3.0543e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9957 | 2.2495e-03 | 1.0733e-03 | 149.72 | 0.00 | 0.945 | 3.0543e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9957 | 2.2495e-03 | 1.0733e-03 | 149.72 | 0.00 | 0.945 | 3.0543e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9957 | 2.2547e-03 | 1.0736e-03 | 149.72 | 0.00 | 0.944 | 3.0544e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9957 | 2.2515e-03 | 1.0742e-03 | 149.72 | 0.00 | 0.944 | 3.0542e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9940 | 6.7197e-03 | 1.4785e-03 | 142.26 | 0.00 | 0.898 | 3.0009e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | region_shape_pass | 0.9771 | 2.3003e-02 | 5.5451e-03 | 33.77 | 0.00 | 0.773 | 1.4181e+04 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9761 | 1.7755e-02 | 5.9746e-03 | 126.64 | 0.00 | 0.805 | 1.4248e+04 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24_poly_full96_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_24\poly_reconstruct_full96
```
