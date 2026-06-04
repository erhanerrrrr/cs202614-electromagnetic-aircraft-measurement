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
| Variant | `eh_love_equivalence_plus_j256` |
| Variant family | `eh_love_equivalence_plus` |
| Calibration mode | `real_eh_j_scale_scan` |
| Uses real H-field | `True` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `256.0` |
| Status | `strict_pass` |
| Correlation | `0.9985` |
| Normalized NMSE | `4.5681e-03` |
| Scale-fitted power NMSE | `9.9532e-04` |
| Main-lobe error / deg | `0.00` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.902` |
| Region-lobe min capture | `0.915` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_plus_j256 | real_eh_j_scale_scan | True | 1 | 256.0 | strict_pass | 0.9985 | 4.5681e-03 | 9.9532e-04 | 0.00 | 0.00 | 0.902 | 6.5616e-01 |
| eh_love_equivalence_plus_j384 | real_eh_j_scale_scan | True | 1 | 384.0 | strict_pass | 0.9982 | 5.9574e-03 | 1.2016e-03 | 0.00 | 0.00 | 0.881 | 5.8573e-01 |
| eh_love_equivalence_plus_j512 | real_eh_j_scale_scan | True | 1 | 512.0 | strict_pass | 0.9979 | 7.9068e-03 | 1.3560e-03 | 0.00 | 0.00 | 0.851 | 5.0843e-01 |
| eh_love_equivalence_minus_j16 | real_eh_j_scale_scan | True | 1 | 16.0 | region_shape_pass | 0.9989 | 3.7993e-03 | 6.9529e-04 | 139.52 | 0.00 | 0.919 | 7.2023e-01 |
| eh_love_equivalence_minus_j12 | real_eh_j_scale_scan | True | 1 | 12.0 | region_shape_pass | 0.9989 | 3.7912e-03 | 6.9535e-04 | 139.52 | 0.00 | 0.919 | 7.2049e-01 |
| eh_love_equivalence_minus_j24 | real_eh_j_scale_scan | True | 1 | 24.0 | region_shape_pass | 0.9989 | 3.8150e-03 | 6.9569e-04 | 139.52 | 0.00 | 0.919 | 7.1958e-01 |
| eh_love_equivalence_minus_j8 | real_eh_j_scale_scan | True | 1 | 8.0 | region_shape_pass | 0.9989 | 3.7828e-03 | 6.9559e-04 | 139.52 | 0.00 | 0.919 | 7.2072e-01 |
| eh_love_equivalence_minus_j4 | real_eh_j_scale_scan | True | 1 | 4.0 | region_shape_pass | 0.9989 | 3.7744e-03 | 6.9599e-04 | 139.52 | 0.00 | 0.919 | 7.2091e-01 |
| outgoing_equivalence_minus_eta0p25 | scalar_impedance_scan | False | 0.25 |  | region_shape_pass | 0.9989 | 3.7556e-03 | 6.9621e-04 | 139.52 | 0.00 | 0.919 | 7.2103e-01 |
| eh_love_equivalence_minus_j2 | real_eh_j_scale_scan | True | 1 | 2.0 | region_shape_pass | 0.9989 | 3.7700e-03 | 6.9626e-04 | 139.52 | 0.00 | 0.919 | 7.2099e-01 |
| eh_love_equivalence_minus_j32 | real_eh_j_scale_scan | True | 1 | 32.0 | region_shape_pass | 0.9989 | 3.8299e-03 | 6.9678e-04 | 139.52 | 0.00 | 0.918 | 7.1879e-01 |
| outgoing_equivalence_minus_eta0p5 | scalar_impedance_scan | False | 0.5 |  | region_shape_pass | 0.9989 | 3.7606e-03 | 6.9637e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9989 | 3.7679e-03 | 6.9641e-04 | 139.52 | 0.00 | 0.919 | 7.2102e-01 |
| outgoing_equivalence_minus_eta0p75 | scalar_impedance_scan | False | 0.75 |  | region_shape_pass | 0.9989 | 3.7623e-03 | 6.9643e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9989 | 3.7631e-03 | 6.9646e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_minus_j0p5 | real_eh_j_scale_scan | True | 1 | 0.5 | region_shape_pass | 0.9989 | 3.7668e-03 | 6.9648e-04 | 139.52 | 0.00 | 0.919 | 7.2104e-01 |
| outgoing_equivalence_minus_eta1p5 | scalar_impedance_scan | False | 1.5 |  | region_shape_pass | 0.9989 | 3.7640e-03 | 6.9650e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta2 | scalar_impedance_scan | False | 2 |  | region_shape_pass | 0.9989 | 3.7644e-03 | 6.9651e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_minus_j0p25 | real_eh_j_scale_scan | True | 1 | 0.25 | region_shape_pass | 0.9989 | 3.7662e-03 | 6.9652e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta3 | scalar_impedance_scan | False | 3 |  | region_shape_pass | 0.9989 | 3.7648e-03 | 6.9653e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_minus_eta4 | scalar_impedance_scan | False | 4 |  | region_shape_pass | 0.9989 | 3.7650e-03 | 6.9654e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta4 | scalar_impedance_scan | False | 4 |  | region_shape_pass | 0.9989 | 3.7663e-03 | 6.9659e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta3 | scalar_impedance_scan | False | 3 |  | region_shape_pass | 0.9989 | 3.7665e-03 | 6.9660e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_plus_j0p25 | real_eh_j_scale_scan | True | 1 | 0.25 | region_shape_pass | 0.9989 | 3.7651e-03 | 6.9661e-04 | 139.52 | 0.00 | 0.919 | 7.2106e-01 |
| outgoing_equivalence_plus_eta2 | scalar_impedance_scan | False | 2 |  | region_shape_pass | 0.9989 | 3.7670e-03 | 6.9662e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta1p5 | scalar_impedance_scan | False | 1.5 |  | region_shape_pass | 0.9989 | 3.7674e-03 | 6.9664e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_plus_j0p5 | real_eh_j_scale_scan | True | 1 | 0.5 | region_shape_pass | 0.9989 | 3.7646e-03 | 6.9665e-04 | 139.52 | 0.00 | 0.919 | 7.2107e-01 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9989 | 3.7683e-03 | 6.9668e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| outgoing_equivalence_plus_eta0p75 | scalar_impedance_scan | False | 0.75 |  | region_shape_pass | 0.9989 | 3.7691e-03 | 6.9671e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9989 | 3.7635e-03 | 6.9674e-04 | 139.52 | 0.00 | 0.919 | 7.2109e-01 |
| outgoing_equivalence_plus_eta0p5 | scalar_impedance_scan | False | 0.5 |  | region_shape_pass | 0.9989 | 3.7708e-03 | 6.9679e-04 | 139.52 | 0.00 | 0.919 | 7.2105e-01 |
| eh_love_equivalence_plus_j2 | real_eh_j_scale_scan | True | 1 | 2.0 | region_shape_pass | 0.9989 | 3.7613e-03 | 6.9692e-04 | 139.52 | 0.00 | 0.920 | 7.2111e-01 |
| outgoing_equivalence_plus_eta0p25 | scalar_impedance_scan | False | 0.25 |  | region_shape_pass | 0.9989 | 3.7761e-03 | 6.9705e-04 | 139.52 | 0.00 | 0.920 | 7.2103e-01 |
| eh_love_equivalence_plus_j4 | real_eh_j_scale_scan | True | 1 | 4.0 | region_shape_pass | 0.9989 | 3.7568e-03 | 6.9731e-04 | 139.52 | 0.00 | 0.920 | 7.2116e-01 |
| eh_love_equivalence_plus_j8 | real_eh_j_scale_scan | True | 1 | 8.0 | region_shape_pass | 0.9989 | 3.7478e-03 | 6.9822e-04 | 139.52 | 0.00 | 0.920 | 7.2124e-01 |
| eh_love_equivalence_plus_j12 | real_eh_j_scale_scan | True | 1 | 12.0 | region_shape_pass | 0.9989 | 3.7386e-03 | 6.9930e-04 | 139.52 | 0.00 | 0.920 | 7.2127e-01 |
| eh_love_equivalence_minus_j48 | real_eh_j_scale_scan | True | 1 | 48.0 | region_shape_pass | 0.9989 | 3.9173e-03 | 7.0104e-04 | 134.58 | 0.00 | 0.913 | 7.1673e-01 |
| eh_love_equivalence_plus_j16 | real_eh_j_scale_scan | True | 1 | 16.0 | region_shape_pass | 0.9989 | 3.7292e-03 | 7.0055e-04 | 139.52 | 0.00 | 0.920 | 7.2126e-01 |
| eh_love_equivalence_plus_j24 | real_eh_j_scale_scan | True | 1 | 24.0 | region_shape_pass | 0.9989 | 3.7100e-03 | 7.0354e-04 | 139.52 | 0.00 | 0.921 | 7.2113e-01 |
| eh_love_equivalence_minus_j64 | real_eh_j_scale_scan | True | 1 | 64.0 | region_shape_pass | 0.9989 | 4.0404e-03 | 7.0808e-04 | 134.58 | 0.00 | 0.911 | 7.1408e-01 |
| eh_love_equivalence_plus_j32 | real_eh_j_scale_scan | True | 1 | 32.0 | region_shape_pass | 0.9989 | 3.7069e-03 | 7.0718e-04 | 144.45 | 0.00 | 0.922 | 7.2084e-01 |
| eh_love_equivalence_plus_j48 | real_eh_j_scale_scan | True | 1 | 48.0 | region_shape_pass | 0.9989 | 3.7611e-03 | 7.1636e-04 | 144.45 | 0.00 | 0.921 | 7.1981e-01 |
| eh_love_equivalence_plus_j64 | real_eh_j_scale_scan | True | 1 | 64.0 | region_shape_pass | 0.9989 | 3.8114e-03 | 7.2798e-04 | 144.45 | 0.00 | 0.918 | 7.1816e-01 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9989 | 4.2851e-03 | 7.3034e-04 | 134.58 | 0.00 | 0.909 | 7.0704e-01 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9989 | 3.8993e-03 | 7.5795e-04 | 144.45 | 0.00 | 0.916 | 7.1305e-01 |
| eh_love_equivalence_minus_j128 | real_eh_j_scale_scan | True | 1 | 128.0 | region_shape_pass | 0.9988 | 4.6179e-03 | 7.6302e-04 | 129.63 | 0.00 | 0.903 | 6.9779e-01 |
| eh_love_equivalence_plus_j128 | real_eh_j_scale_scan | True | 1 | 128.0 | region_shape_pass | 0.9988 | 3.9685e-03 | 7.9581e-04 | 144.45 | 0.00 | 0.913 | 7.0562e-01 |
| eh_love_equivalence_minus_j192 | real_eh_j_scale_scan | True | 1 | 192.0 | region_shape_pass | 0.9987 | 5.3997e-03 | 8.5590e-04 | 129.63 | 0.00 | 0.894 | 6.7344e-01 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9987 | 1.0419e-02 | 8.7346e-04 | 134.58 | 0.00 | 0.815 | 3.3837e+05 |
| eh_love_equivalence_plus_j192 | real_eh_j_scale_scan | True | 1 | 192.0 | region_shape_pass | 0.9987 | 4.2379e-03 | 8.8915e-04 | 149.35 | 0.00 | 0.911 | 6.8444e-01 |
| eh_love_equivalence_minus_j256 | real_eh_j_scale_scan | True | 1 | 256.0 | region_shape_pass | 0.9985 | 6.1562e-03 | 9.7687e-04 | 129.63 | 0.00 | 0.880 | 6.4272e-01 |
| eh_love_equivalence_minus_j384 | real_eh_j_scale_scan | True | 1 | 384.0 | region_shape_pass | 0.9981 | 7.4493e-03 | 1.2566e-03 | 129.63 | 0.00 | 0.869 | 5.6973e-01 |
| eh_love_equivalence_minus_j512 | real_eh_j_scale_scan | True | 1 | 512.0 | region_shape_pass | 0.9977 | 8.4214e-03 | 1.5219e-03 | 124.67 | 0.00 | 0.861 | 4.9236e-01 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | region_shape_pass | 0.9977 | 5.1133e-03 | 1.5236e-03 | 149.35 | 0.00 | 0.904 | 4.2897e+05 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_short_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_extrapolation_batch\L1_short_dipole_z_1p2G
```
