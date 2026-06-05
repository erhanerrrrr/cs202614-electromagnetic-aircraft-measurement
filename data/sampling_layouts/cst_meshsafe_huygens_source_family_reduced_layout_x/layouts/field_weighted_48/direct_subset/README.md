# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `48` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349346` |
| Tangential/total L2 ratio | `0.9920` |
| Normal/total L2 ratio | `0.1264` |
| Dynamic range / dB | `8.79` |
| H tangential/total L2 ratio | `0.9991` |
| H normal/total L2 ratio | `0.0413` |
| H dynamic range / dB | `10.75` |
| Tangential E/H impedance / ohm | `369.566` |
| Tangential E/H eta0 ratio | `0.9810` |

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
| Status | `diagnostic_only` |
| Correlation | `0.5053` |
| Normalized NMSE | `4.8765e-01` |
| Scale-fitted power NMSE | `2.2464e-01` |
| Main-lobe error / deg | `102.82` |
| Region-lobe error / deg | `96.87` |
| Region-lobe Jaccard | `0.030` |
| Region-lobe min capture | `0.031` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.5053 | 4.8765e-01 | 2.2464e-01 | 102.82 | 96.87 | 0.030 | 1.3835e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.4427 | 4.9982e-01 | 2.5296e-01 | 102.28 | 95.88 | 0.032 | 1.4414e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4426 | 4.9980e-01 | 2.5295e-01 | 102.28 | 95.88 | 0.032 | 1.4415e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.4420 | 4.9996e-01 | 2.5328e-01 | 102.28 | 95.88 | 0.032 | 1.4413e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.4420 | 4.9996e-01 | 2.5328e-01 | 102.28 | 95.88 | 0.032 | 1.4413e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4414 | 5.0011e-01 | 2.5361e-01 | 102.28 | 95.88 | 0.032 | 1.4412e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.4413 | 5.0009e-01 | 2.5361e-01 | 102.28 | 95.88 | 0.032 | 1.4413e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4133 | 5.7634e-01 | 3.7241e-01 | 78.22 | 72.79 | 0.030 | 2.7087e+03 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4100 | 5.7564e-01 | 3.7485e-01 | 78.22 | 73.81 | 0.030 | 2.7698e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.3877 | 5.0042e-01 | 2.7904e-01 | 102.28 | 8.72 | 0.038 | 1.3907e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48\direct_subset
```
