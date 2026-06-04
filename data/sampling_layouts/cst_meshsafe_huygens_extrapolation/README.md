# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\cst_exports\level1_meshsafe_huygens\L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` |
| Local Huygens H field | `data\cst_exports\level1_meshsafe_huygens\L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1\all_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9913` |
| Normal/total L2 ratio | `0.1313` |
| Dynamic range / dB | `12.54` |
| H tangential/total L2 ratio | `0.9995` |
| H normal/total L2 ratio | `0.0322` |
| H dynamic range / dB | `16.96` |
| Tangential E/H impedance / ohm | `425.357` |
| Tangential E/H eta0 ratio | `1.1291` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `outgoing_equivalence_minus_eta0p25` |
| Variant family | `outgoing_equivalence_minus` |
| Calibration mode | `scalar_impedance_scan` |
| Uses real H-field | `False` |
| Eta_eff / eta0 | `0.25` |
| Eta_eff / ohm | `94.182578417` |
| Status | `region_shape_pass` |
| Correlation | `0.9989` |
| Normalized NMSE | `3.7556e-03` |
| Scale-fitted power NMSE | `6.9621e-04` |
| Main-lobe error / deg | `139.52` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.919` |
| Region-lobe min capture | `0.930` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| outgoing_equivalence_minus_eta0p25 | scalar_impedance_scan | False | 0.25 | region_shape_pass | 0.9989 | 3.7556e-03 | 6.9621e-04 | 139.52 | 0.00 | 0.919 | 7.2103e-01 |
| outgoing_equivalence_minus_eta0p5 | scalar_impedance_scan | False | 0.5 | region_shape_pass | 0.9989 | 3.7606e-03 | 6.9637e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | region_shape_pass | 0.9989 | 3.7679e-03 | 6.9641e-04 | 139.52 | 0.00 | 0.919 | 7.2102e-01 |
| outgoing_equivalence_minus_eta0p75 | scalar_impedance_scan | False | 0.75 | region_shape_pass | 0.9989 | 3.7623e-03 | 6.9643e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 | region_shape_pass | 0.9989 | 3.7631e-03 | 6.9646e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta1p5 | scalar_impedance_scan | False | 1.5 | region_shape_pass | 0.9989 | 3.7640e-03 | 6.9650e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta2 | scalar_impedance_scan | False | 2 | region_shape_pass | 0.9989 | 3.7644e-03 | 6.9651e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta3 | scalar_impedance_scan | False | 3 | region_shape_pass | 0.9989 | 3.7648e-03 | 6.9653e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta4 | scalar_impedance_scan | False | 4 | region_shape_pass | 0.9989 | 3.7650e-03 | 6.9654e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| magnetic_only_plus | not_used | False | 1 | region_shape_pass | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| magnetic_only_minus | not_used | False | 1 | region_shape_pass | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta4 | scalar_impedance_scan | False | 4 | region_shape_pass | 0.9989 | 3.7663e-03 | 6.9659e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta3 | scalar_impedance_scan | False | 3 | region_shape_pass | 0.9989 | 3.7665e-03 | 6.9660e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta2 | scalar_impedance_scan | False | 2 | region_shape_pass | 0.9989 | 3.7670e-03 | 6.9662e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta1p5 | scalar_impedance_scan | False | 1.5 | region_shape_pass | 0.9989 | 3.7674e-03 | 6.9664e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 | region_shape_pass | 0.9989 | 3.7683e-03 | 6.9668e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta0p75 | scalar_impedance_scan | False | 0.75 | region_shape_pass | 0.9989 | 3.7691e-03 | 6.9671e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | region_shape_pass | 0.9989 | 3.7635e-03 | 6.9674e-04 | 139.52 | 0.00 | 0.919 | 7.2109e-01 |
| outgoing_equivalence_plus_eta0p5 | scalar_impedance_scan | False | 0.5 | region_shape_pass | 0.9989 | 3.7708e-03 | 6.9679e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta0p25 | scalar_impedance_scan | False | 0.25 | region_shape_pass | 0.9989 | 3.7761e-03 | 6.9705e-04 | 139.52 | 0.00 | 0.920 | 7.2103e-01 |
| electric_only_outgoing | fixed_eta0 | False | 1 | region_shape_pass | 0.9987 | 1.0419e-02 | 8.7346e-04 | 134.58 | 0.00 | 0.815 | 3.3837e+05 |
| hfield_electric_only | real_hfield_only | True | 1 | region_shape_pass | 0.9977 | 5.1133e-03 | 1.5236e-03 | 149.35 | 0.00 | 0.904 | 4.2897e+05 |

## Reading

- This Python gate consumes matched real CST local E-field and H-field probe values.
- Real dual-field variants evaluate `J = n x H_t` and `M = -n x E_t`, while the older E-only impedance scan remains as a calibration baseline.
- The equivalent-current formulas are still a diagnostic Huygens/Kirchhoff
  operator rather than final report-level Stratton-Chu evidence. Treat the
  scalar impedance scan as a calibration baseline and the real E/H variants as
  the next physics gate to refine.
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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_short_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_extrapolation
```
