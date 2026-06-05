# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_72_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_72_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `72` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349802` |
| Tangential/total L2 ratio | `0.9841` |
| Normal/total L2 ratio | `0.1778` |
| Dynamic range / dB | `10.86` |
| H tangential/total L2 ratio | `0.9996` |
| H normal/total L2 ratio | `0.0290` |
| H dynamic range / dB | `16.57` |
| Tangential E/H impedance / ohm | `369.788` |
| Tangential E/H eta0 ratio | `0.9816` |

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
| Correlation | `0.4402` |
| Normalized NMSE | `5.6968e-01` |
| Scale-fitted power NMSE | `3.2746e-01` |
| Main-lobe error / deg | `152.71` |
| Region-lobe error / deg | `9.99` |
| Region-lobe Jaccard | `0.014` |
| Region-lobe min capture | `0.014` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4402 | 5.6968e-01 | 3.2746e-01 | 152.71 | 9.99 | 0.014 | 4.4057e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.4256 | 3.9679e-01 | 2.1040e-01 | 158.19 | 54.33 | 0.056 | 1.9391e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4163 | 5.8865e-01 | 3.4319e-01 | 152.71 | 9.99 | 0.014 | 4.3389e+03 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.3673 | 4.1172e-01 | 2.2662e-01 | 64.73 | 56.23 | 0.054 | 2.1022e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.3672 | 4.1177e-01 | 2.2666e-01 | 64.73 | 56.23 | 0.054 | 2.1021e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.3664 | 4.1213e-01 | 2.2705e-01 | 64.73 | 56.23 | 0.054 | 2.1026e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.3664 | 4.1213e-01 | 2.2705e-01 | 64.73 | 56.23 | 0.054 | 2.1026e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.3656 | 4.1249e-01 | 2.2744e-01 | 64.73 | 56.23 | 0.055 | 2.1031e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.3655 | 4.1253e-01 | 2.2748e-01 | 64.73 | 56.23 | 0.055 | 2.1030e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.2833 | 4.4173e-01 | 2.8492e-01 | 63.80 | 47.79 | 0.059 | 2.0091e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_72_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\geometric_farthest_72
```
