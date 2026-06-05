# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `72` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.34976` |
| Tangential/total L2 ratio | `0.9922` |
| Normal/total L2 ratio | `0.1249` |
| Dynamic range / dB | `8.79` |
| H tangential/total L2 ratio | `0.9994` |
| H normal/total L2 ratio | `0.0357` |
| H dynamic range / dB | `10.75` |
| Tangential E/H impedance / ohm | `369.991` |
| Tangential E/H eta0 ratio | `0.9821` |

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
| Correlation | `0.6434` |
| Normalized NMSE | `3.4369e-01` |
| Scale-fitted power NMSE | `1.6824e-01` |
| Main-lobe error / deg | `108.37` |
| Region-lobe error / deg | `83.22` |
| Region-lobe Jaccard | `0.057` |
| Region-lobe min capture | `0.060` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.6434 | 3.4369e-01 | 1.6824e-01 | 108.37 | 83.22 | 0.057 | 1.7687e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.6318 | 3.5503e-01 | 1.7226e-01 | 107.80 | 94.14 | 0.054 | 1.8186e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.6317 | 3.5504e-01 | 1.7230e-01 | 107.80 | 94.14 | 0.054 | 1.8184e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.6316 | 3.5509e-01 | 1.7234e-01 | 107.80 | 94.14 | 0.054 | 1.8184e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.6316 | 3.5509e-01 | 1.7234e-01 | 107.80 | 94.14 | 0.054 | 1.8184e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.6315 | 3.5514e-01 | 1.7238e-01 | 107.80 | 94.14 | 0.054 | 1.8185e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.6315 | 3.5514e-01 | 1.7243e-01 | 107.80 | 94.14 | 0.054 | 1.8183e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.6205 | 3.5115e-01 | 1.7557e-01 | 107.80 | 89.88 | 0.074 | 1.7799e-02 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.5755 | 3.1967e-01 | 2.0938e-01 | 92.32 | 9.99 | 0.176 | 6.2908e+03 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.5564 | 3.4795e-01 | 2.2708e-01 | 91.98 | 14.99 | 0.159 | 6.3499e+03 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_72
```
