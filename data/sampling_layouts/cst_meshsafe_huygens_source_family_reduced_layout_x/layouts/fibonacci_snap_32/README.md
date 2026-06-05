# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_32_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_32_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `32` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349829` |
| Tangential/total L2 ratio | `0.9870` |
| Normal/total L2 ratio | `0.1605` |
| Dynamic range / dB | `10.86` |
| H tangential/total L2 ratio | `0.9993` |
| H normal/total L2 ratio | `0.0363` |
| H dynamic range / dB | `16.57` |
| Tangential E/H impedance / ohm | `373.056` |
| Tangential E/H eta0 ratio | `0.9902` |

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
| Correlation | `0.3497` |
| Normalized NMSE | `6.4912e-01` |
| Scale-fitted power NMSE | `4.2247e-01` |
| Main-lobe error / deg | `6.90` |
| Region-lobe error / deg | `2.39` |
| Region-lobe Jaccard | `0.007` |
| Region-lobe min capture | `0.007` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.3497 | 6.4912e-01 | 4.2247e-01 | 6.90 | 2.39 | 0.007 | 1.7137e+03 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.3415 | 6.4777e-01 | 4.2354e-01 | 6.90 | 2.39 | 0.005 | 1.7169e+03 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.1543 | 4.6747e-01 | 3.3958e-01 | 65.72 | 40.15 | 0.004 | 9.3771e-03 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0521 | 5.0405e-01 | 3.5698e-01 | 46.03 | 40.15 | 0.000 | 9.8390e-03 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0520 | 5.0411e-01 | 3.5699e-01 | 46.03 | 40.15 | 0.000 | 9.8390e-03 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.0511 | 5.0475e-01 | 3.5733e-01 | 46.03 | 40.15 | 0.000 | 9.8370e-03 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.0511 | 5.0475e-01 | 3.5733e-01 | 46.03 | 40.15 | 0.000 | 9.8370e-03 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0501 | 5.0538e-01 | 3.5767e-01 | 46.03 | 40.15 | 0.000 | 9.8348e-03 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0501 | 5.0544e-01 | 3.5768e-01 | 46.03 | 40.15 | 0.000 | 9.8347e-03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | -0.0204 | 5.5580e-01 | 3.9975e-01 | 46.03 | 40.42 | 0.001 | 9.0367e-03 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_32_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_32
```
