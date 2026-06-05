# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `48` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349985` |
| Tangential/total L2 ratio | `0.9871` |
| Normal/total L2 ratio | `0.1604` |
| Dynamic range / dB | `9.93` |
| H tangential/total L2 ratio | `0.9998` |
| H normal/total L2 ratio | `0.0192` |
| H dynamic range / dB | `12.70` |
| Tangential E/H impedance / ohm | `369.627` |
| Tangential E/H eta0 ratio | `0.9811` |

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
| Correlation | `0.4774` |
| Normalized NMSE | `5.0000e-01` |
| Scale-fitted power NMSE | `2.7202e-01` |
| Main-lobe error / deg | `154.56` |
| Region-lobe error / deg | `29.65` |
| Region-lobe Jaccard | `0.011` |
| Region-lobe min capture | `0.011` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4774 | 5.0000e-01 | 2.7202e-01 | 154.56 | 29.65 | 0.011 | 2.8928e+03 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.4729 | 5.1941e-01 | 2.7158e-01 | 154.56 | 29.65 | 0.011 | 2.8719e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.3493 | 4.1138e-01 | 3.2740e-01 | 95.98 | 14.99 | 0.178 | 1.0597e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.3016 | 4.0032e-01 | 3.0109e-01 | 101.35 | 9.99 | 0.091 | 1.2433e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.3016 | 4.0031e-01 | 3.0110e-01 | 101.35 | 9.99 | 0.091 | 1.2433e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.3009 | 4.0051e-01 | 3.0098e-01 | 101.35 | 9.99 | 0.090 | 1.2447e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.3009 | 4.0051e-01 | 3.0098e-01 | 101.35 | 9.99 | 0.090 | 1.2447e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.3002 | 4.0070e-01 | 3.0086e-01 | 101.35 | 9.99 | 0.090 | 1.2460e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.3002 | 4.0069e-01 | 3.0087e-01 | 101.35 | 9.99 | 0.090 | 1.2460e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.2196 | 4.6667e-01 | 3.1603e-01 | 23.10 | 12.26 | 0.046 | 1.2779e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_48
```
