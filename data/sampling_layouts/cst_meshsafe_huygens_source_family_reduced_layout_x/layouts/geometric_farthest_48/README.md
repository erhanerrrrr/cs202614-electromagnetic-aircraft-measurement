# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_48_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_48_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `48` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349431` |
| Tangential/total L2 ratio | `0.9852` |
| Normal/total L2 ratio | `0.1713` |
| Dynamic range / dB | `10.64` |
| H tangential/total L2 ratio | `0.9995` |
| H normal/total L2 ratio | `0.0325` |
| H dynamic range / dB | `15.50` |
| Tangential E/H impedance / ohm | `369.789` |
| Tangential E/H eta0 ratio | `0.9816` |

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
| Correlation | `0.2195` |
| Normalized NMSE | `6.2545e-01` |
| Scale-fitted power NMSE | `4.3280e-01` |
| Main-lobe error / deg | `48.53` |
| Region-lobe error / deg | `35.54` |
| Region-lobe Jaccard | `0.020` |
| Region-lobe min capture | `0.020` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.2195 | 6.2545e-01 | 4.3280e-01 | 48.53 | 35.54 | 0.020 | 3.4824e+03 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.2172 | 6.1429e-01 | 4.3083e-01 | 48.53 | 35.54 | 0.023 | 3.6059e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.0584 | 4.8422e-01 | 3.2249e-01 | 142.66 | 56.38 | 0.015 | 1.4366e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.0457 | 4.9109e-01 | 3.4556e-01 | 70.29 | 25.07 | 0.027 | 1.4592e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0438 | 4.6776e-01 | 3.3287e-01 | 142.66 | 25.07 | 0.032 | 1.4986e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0437 | 4.6778e-01 | 3.3288e-01 | 142.66 | 25.07 | 0.032 | 1.4986e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.0437 | 4.6751e-01 | 3.3301e-01 | 142.66 | 25.07 | 0.032 | 1.4987e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.0437 | 4.6751e-01 | 3.3301e-01 | 142.66 | 25.07 | 0.032 | 1.4987e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0436 | 4.6723e-01 | 3.3314e-01 | 142.66 | 25.07 | 0.032 | 1.4988e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0435 | 4.6726e-01 | 3.3315e-01 | 142.66 | 25.07 | 0.032 | 1.4989e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_48_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_48
```
