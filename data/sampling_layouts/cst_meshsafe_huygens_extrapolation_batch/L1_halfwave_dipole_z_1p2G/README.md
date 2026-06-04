# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` |
| Local Huygens H field | `data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1\all_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9866` |
| Normal/total L2 ratio | `0.1633` |
| Dynamic range / dB | `12.61` |
| H tangential/total L2 ratio | `0.9990` |
| H normal/total L2 ratio | `0.0442` |
| H dynamic range / dB | `18.58` |
| Tangential E/H impedance / ohm | `370.381` |
| Tangential E/H eta0 ratio | `0.9831` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `eh_love_equivalence_minus_j96` |
| Variant family | `eh_love_equivalence_minus` |
| Calibration mode | `real_eh_j_scale_scan` |
| Uses real H-field | `True` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `96.0` |
| Status | `strict_pass` |
| Correlation | `0.9991` |
| Normalized NMSE | `2.1511e-03` |
| Scale-fitted power NMSE | `7.1320e-04` |
| Main-lobe error / deg | `0.00` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.924` |
| Region-lobe min capture | `0.935` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | strict_pass | 0.9991 | 2.1511e-03 | 7.1320e-04 | 0.00 | 0.00 | 0.924 | 2.7878e-02 |
| eh_love_equivalence_minus_j128 | real_eh_j_scale_scan | True | 1 | 128.0 | strict_pass | 0.9991 | 2.0657e-03 | 7.2313e-04 | 0.00 | 0.00 | 0.928 | 2.7430e-02 |
| eh_love_equivalence_minus_j192 | real_eh_j_scale_scan | True | 1 | 192.0 | strict_pass | 0.9990 | 2.9286e-03 | 7.8953e-04 | 0.00 | 0.00 | 0.910 | 2.6252e-02 |
| eh_love_equivalence_minus_j256 | real_eh_j_scale_scan | True | 1 | 256.0 | strict_pass | 0.9989 | 3.7210e-03 | 8.9035e-04 | 0.00 | 0.00 | 0.889 | 2.4785e-02 |
| eh_love_equivalence_minus_j384 | real_eh_j_scale_scan | True | 1 | 384.0 | strict_pass | 0.9985 | 4.7636e-03 | 1.1543e-03 | 0.00 | 0.00 | 0.878 | 2.1408e-02 |
| eh_love_equivalence_minus_j512 | real_eh_j_scale_scan | True | 1 | 512.0 | strict_pass | 0.9981 | 5.1149e-03 | 1.5320e-03 | 0.00 | 0.00 | 0.879 | 1.8001e-02 |
| eh_love_equivalence_minus_j64 | real_eh_j_scale_scan | True | 1 | 64.0 | region_shape_pass | 0.9991 | 2.3600e-03 | 7.2727e-04 | 19.99 | 0.00 | 0.919 | 2.8216e-02 |
| eh_love_equivalence_minus_j48 | real_eh_j_scale_scan | True | 1 | 48.0 | region_shape_pass | 0.9991 | 2.4680e-03 | 7.4572e-04 | 19.99 | 0.00 | 0.914 | 2.8342e-02 |
| eh_love_equivalence_minus_j32 | real_eh_j_scale_scan | True | 1 | 32.0 | region_shape_pass | 0.9990 | 2.5785e-03 | 7.7318e-04 | 19.99 | 0.00 | 0.912 | 2.8437e-02 |
| eh_love_equivalence_minus_j24 | real_eh_j_scale_scan | True | 1 | 24.0 | region_shape_pass | 0.9990 | 2.6346e-03 | 7.9062e-04 | 19.99 | 0.00 | 0.912 | 2.8474e-02 |
| eh_love_equivalence_minus_j16 | real_eh_j_scale_scan | True | 1 | 16.0 | region_shape_pass | 0.9990 | 2.6913e-03 | 8.1071e-04 | 19.99 | 0.00 | 0.911 | 2.8502e-02 |
| eh_love_equivalence_minus_j12 | real_eh_j_scale_scan | True | 1 | 12.0 | region_shape_pass | 0.9990 | 2.7199e-03 | 8.2180e-04 | 19.99 | 0.00 | 0.911 | 2.8513e-02 |
| eh_love_equivalence_minus_j8 | real_eh_j_scale_scan | True | 1 | 8.0 | region_shape_pass | 0.9990 | 2.7486e-03 | 8.3359e-04 | 19.99 | 0.00 | 0.911 | 2.8522e-02 |
| eh_love_equivalence_minus_j4 | real_eh_j_scale_scan | True | 1 | 4.0 | region_shape_pass | 0.9990 | 2.7775e-03 | 8.4612e-04 | 19.99 | 0.00 | 0.910 | 2.8529e-02 |
| outgoing_equivalence_minus_eta0p25 | scalar_impedance_scan | False | 0.25 |  | region_shape_pass | 0.9990 | 2.7633e-03 | 8.4827e-04 | 19.99 | 0.00 | 0.910 | 2.8531e-02 |
| eh_love_equivalence_minus_j2 | real_eh_j_scale_scan | True | 1 | 2.0 | region_shape_pass | 0.9990 | 2.7920e-03 | 8.5266e-04 | 19.99 | 0.00 | 0.910 | 2.8532e-02 |
| outgoing_equivalence_minus_eta0p5 | scalar_impedance_scan | False | 0.5 |  | region_shape_pass | 0.9990 | 2.7849e-03 | 8.5369e-04 | 19.99 | 0.00 | 0.910 | 2.8533e-02 |
| outgoing_equivalence_minus_eta0p75 | scalar_impedance_scan | False | 0.75 |  | region_shape_pass | 0.9990 | 2.7921e-03 | 8.5556e-04 | 19.99 | 0.00 | 0.910 | 2.8534e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9990 | 2.7993e-03 | 8.5600e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9990 | 2.7957e-03 | 8.5651e-04 | 19.99 | 0.00 | 0.910 | 2.8534e-02 |
| outgoing_equivalence_minus_eta1p5 | scalar_impedance_scan | False | 1.5 |  | region_shape_pass | 0.9990 | 2.7993e-03 | 8.5746e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| eh_love_equivalence_minus_j0p5 | real_eh_j_scale_scan | True | 1 | 0.5 | region_shape_pass | 0.9990 | 2.8029e-03 | 8.5769e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta2 | scalar_impedance_scan | False | 2 |  | region_shape_pass | 0.9990 | 2.8011e-03 | 8.5794e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta3 | scalar_impedance_scan | False | 3 |  | region_shape_pass | 0.9990 | 2.8030e-03 | 8.5842e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| eh_love_equivalence_minus_j0p25 | real_eh_j_scale_scan | True | 1 | 0.25 | region_shape_pass | 0.9990 | 2.8048e-03 | 8.5854e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta4 | scalar_impedance_scan | False | 4 |  | region_shape_pass | 0.9990 | 2.8039e-03 | 8.5867e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta4 | scalar_impedance_scan | False | 4 |  | region_shape_pass | 0.9990 | 2.8093e-03 | 8.6013e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| eh_love_equivalence_plus_j0p25 | real_eh_j_scale_scan | True | 1 | 0.25 | region_shape_pass | 0.9990 | 2.8084e-03 | 8.6025e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta3 | scalar_impedance_scan | False | 3 |  | region_shape_pass | 0.9990 | 2.8102e-03 | 8.6037e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta2 | scalar_impedance_scan | False | 2 |  | region_shape_pass | 0.9990 | 2.8120e-03 | 8.6086e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| eh_love_equivalence_plus_j0p5 | real_eh_j_scale_scan | True | 1 | 0.5 | region_shape_pass | 0.9990 | 2.8102e-03 | 8.6111e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta1p5 | scalar_impedance_scan | False | 1.5 |  | region_shape_pass | 0.9990 | 2.8138e-03 | 8.6136e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9989 | 2.8175e-03 | 8.6235e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9989 | 2.8139e-03 | 8.6283e-04 | 19.99 | 0.00 | 0.911 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p75 | scalar_impedance_scan | False | 0.75 |  | region_shape_pass | 0.9989 | 2.8211e-03 | 8.6335e-04 | 19.99 | 0.00 | 0.911 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p5 | scalar_impedance_scan | False | 0.5 |  | region_shape_pass | 0.9989 | 2.8283e-03 | 8.6538e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| eh_love_equivalence_plus_j2 | real_eh_j_scale_scan | True | 1 | 2.0 | region_shape_pass | 0.9989 | 2.8212e-03 | 8.6631e-04 | 19.99 | 0.00 | 0.911 | 2.8537e-02 |
| outgoing_equivalence_plus_eta0p25 | scalar_impedance_scan | False | 0.25 |  | region_shape_pass | 0.9989 | 2.8502e-03 | 8.7166e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| eh_love_equivalence_plus_j4 | real_eh_j_scale_scan | True | 1 | 4.0 | region_shape_pass | 0.9989 | 2.8358e-03 | 8.7343e-04 | 19.99 | 0.00 | 0.910 | 2.8538e-02 |
| eh_love_equivalence_plus_j8 | real_eh_j_scale_scan | True | 1 | 8.0 | region_shape_pass | 0.9989 | 2.8652e-03 | 8.8824e-04 | 19.99 | 0.00 | 0.910 | 2.8539e-02 |
| eh_love_equivalence_plus_j12 | real_eh_j_scale_scan | True | 1 | 12.0 | region_shape_pass | 0.9989 | 2.8948e-03 | 9.0385e-04 | 19.99 | 0.00 | 0.910 | 2.8539e-02 |
| eh_love_equivalence_plus_j16 | real_eh_j_scale_scan | True | 1 | 16.0 | region_shape_pass | 0.9989 | 2.9246e-03 | 9.2027e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| eh_love_equivalence_plus_j24 | real_eh_j_scale_scan | True | 1 | 24.0 | region_shape_pass | 0.9989 | 2.9847e-03 | 9.5559e-04 | 19.99 | 0.00 | 0.910 | 2.8525e-02 |
| eh_love_equivalence_plus_j32 | real_eh_j_scale_scan | True | 1 | 32.0 | region_shape_pass | 0.9988 | 3.0456e-03 | 9.9432e-04 | 19.99 | 0.00 | 0.906 | 2.8505e-02 |
| eh_love_equivalence_plus_j48 | real_eh_j_scale_scan | True | 1 | 48.0 | region_shape_pass | 0.9987 | 3.1928e-03 | 1.0825e-03 | 24.98 | 0.00 | 0.899 | 2.8443e-02 |
| eh_love_equivalence_plus_j64 | real_eh_j_scale_scan | True | 1 | 64.0 | region_shape_pass | 0.9986 | 3.3535e-03 | 1.1856e-03 | 24.98 | 0.00 | 0.897 | 2.8350e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9984 | 3.6964e-03 | 1.4391e-03 | 24.98 | 0.00 | 0.889 | 2.8072e-02 |
| eh_love_equivalence_plus_j128 | real_eh_j_scale_scan | True | 1 | 128.0 | region_shape_pass | 0.9981 | 4.0684e-03 | 1.7588e-03 | 24.98 | 0.00 | 0.892 | 2.7679e-02 |
| eh_love_equivalence_plus_j192 | real_eh_j_scale_scan | True | 1 | 192.0 | region_shape_pass | 0.9973 | 4.9002e-03 | 2.5990e-03 | 24.98 | 0.00 | 0.886 | 2.6588e-02 |
| eh_love_equivalence_plus_j256 | real_eh_j_scale_scan | True | 1 | 256.0 | region_shape_pass | 0.9963 | 5.8400e-03 | 3.6838e-03 | 24.98 | 0.00 | 0.894 | 2.5173e-02 |
| eh_love_equivalence_plus_j384 | real_eh_j_scale_scan | True | 1 | 384.0 | region_shape_pass | 0.9938 | 7.9420e-03 | 6.3360e-03 | 24.98 | 0.00 | 0.891 | 2.1810e-02 |
| eh_love_equivalence_plus_j512 | real_eh_j_scale_scan | True | 1 | 512.0 | region_shape_pass | 0.9911 | 1.0107e-02 | 9.1257e-03 | 24.98 | 0.00 | 0.890 | 1.8348e-02 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | physics_proxy_pass | 0.9868 | 1.8414e-02 | 1.4090e-02 | 0.00 | 0.00 | 0.729 | 1.3574e+04 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | physics_proxy_pass | 0.9849 | 1.6520e-02 | 1.5105e-02 | 29.98 | 0.00 | 0.864 | 1.3091e+04 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_halfwave_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_extrapolation_batch\L1_halfwave_dipole_z_1p2G
```
