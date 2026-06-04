# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes the `96 * 3 = 288` complex Cartesian E-field probe rows exported
through CST `ResultTree` and compares a diagnostic equivalent-current far-field
proxy against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` |
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

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `outgoing_equivalence_minus_eta0p0312` |
| Variant family | `outgoing_equivalence_minus` |
| Calibration mode | `scalar_impedance_scan` |
| Eta_eff / eta0 | `0.03125` |
| Eta_eff / ohm | `11.772822302125` |
| Status | `region_shape_pass` |
| Correlation | `0.9990` |
| Normalized NMSE | `2.4976e-03` |
| Scale-fitted power NMSE | `8.0129e-04` |
| Main-lobe error / deg | `24.98` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.911` |
| Region-lobe min capture | `0.924` |

## Variant Ranking

| Variant | Calibration | Eta/eta0 | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| outgoing_equivalence_minus_eta0p0312 | scalar_impedance_scan | 0.0312 | region_shape_pass | 0.9990 | 2.4976e-03 | 8.0129e-04 | 24.98 | 0.00 | 0.911 | 2.8452e-02 |
| outgoing_equivalence_minus_eta0p0625 | scalar_impedance_scan | 0.0625 | region_shape_pass | 0.9990 | 2.6353e-03 | 8.2164e-04 | 19.99 | 0.00 | 0.912 | 2.8508e-02 |
| outgoing_equivalence_minus_eta0p0156 | scalar_impedance_scan | 0.0156 | region_shape_pass | 0.9990 | 2.5810e-03 | 8.0884e-04 | 139.81 | 0.00 | 0.908 | 2.8248e-02 |
| outgoing_equivalence_minus_eta0p125 | scalar_impedance_scan | 0.125 | region_shape_pass | 0.9990 | 2.7203e-03 | 8.3828e-04 | 19.99 | 0.00 | 0.911 | 2.8525e-02 |
| outgoing_equivalence_minus_eta0p188 | scalar_impedance_scan | 0.188 | region_shape_pass | 0.9990 | 2.7489e-03 | 8.4482e-04 | 19.99 | 0.00 | 0.911 | 2.8529e-02 |
| outgoing_equivalence_minus_eta0p25 | scalar_impedance_scan | 0.25 | region_shape_pass | 0.9990 | 2.7633e-03 | 8.4827e-04 | 19.99 | 0.00 | 0.910 | 2.8531e-02 |
| outgoing_equivalence_minus_eta0p375 | scalar_impedance_scan | 0.375 | region_shape_pass | 0.9990 | 2.7777e-03 | 8.5185e-04 | 19.99 | 0.00 | 0.910 | 2.8532e-02 |
| outgoing_equivalence_minus_eta0p5 | scalar_impedance_scan | 0.5 | region_shape_pass | 0.9990 | 2.7849e-03 | 8.5369e-04 | 19.99 | 0.00 | 0.910 | 2.8533e-02 |
| outgoing_equivalence_minus_eta0p75 | scalar_impedance_scan | 0.75 | region_shape_pass | 0.9990 | 2.7921e-03 | 8.5556e-04 | 19.99 | 0.00 | 0.910 | 2.8534e-02 |
| outgoing_equivalence_minus | fixed_eta0 | 1 | region_shape_pass | 0.9990 | 2.7957e-03 | 8.5651e-04 | 19.99 | 0.00 | 0.910 | 2.8534e-02 |
| outgoing_equivalence_minus_eta1p5 | scalar_impedance_scan | 1.5 | region_shape_pass | 0.9990 | 2.7993e-03 | 8.5746e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta2 | scalar_impedance_scan | 2 | region_shape_pass | 0.9990 | 2.8011e-03 | 8.5794e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta3 | scalar_impedance_scan | 3 | region_shape_pass | 0.9990 | 2.8030e-03 | 8.5842e-04 | 19.99 | 0.00 | 0.911 | 2.8534e-02 |
| outgoing_equivalence_minus_eta4 | scalar_impedance_scan | 4 | region_shape_pass | 0.9990 | 2.8039e-03 | 8.5867e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| magnetic_only_plus | not_used | 1 | region_shape_pass | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| magnetic_only_minus | not_used | 1 | region_shape_pass | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta4 | scalar_impedance_scan | 4 | region_shape_pass | 0.9990 | 2.8093e-03 | 8.6013e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta3 | scalar_impedance_scan | 3 | region_shape_pass | 0.9990 | 2.8102e-03 | 8.6037e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta2 | scalar_impedance_scan | 2 | region_shape_pass | 0.9990 | 2.8120e-03 | 8.6086e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta1p5 | scalar_impedance_scan | 1.5 | region_shape_pass | 0.9990 | 2.8138e-03 | 8.6136e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus | fixed_eta0 | 1 | region_shape_pass | 0.9989 | 2.8175e-03 | 8.6235e-04 | 19.99 | 0.00 | 0.911 | 2.8535e-02 |
| outgoing_equivalence_plus_eta0p75 | scalar_impedance_scan | 0.75 | region_shape_pass | 0.9989 | 2.8211e-03 | 8.6335e-04 | 19.99 | 0.00 | 0.911 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p5 | scalar_impedance_scan | 0.5 | region_shape_pass | 0.9989 | 2.8283e-03 | 8.6538e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p375 | scalar_impedance_scan | 0.375 | region_shape_pass | 0.9989 | 2.8356e-03 | 8.6744e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p25 | scalar_impedance_scan | 0.25 | region_shape_pass | 0.9989 | 2.8502e-03 | 8.7166e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p188 | scalar_impedance_scan | 0.188 | region_shape_pass | 0.9989 | 2.8648e-03 | 8.7600e-04 | 19.99 | 0.00 | 0.910 | 2.8537e-02 |
| outgoing_equivalence_plus_eta0p125 | scalar_impedance_scan | 0.125 | region_shape_pass | 0.9989 | 2.8941e-03 | 8.8507e-04 | 19.99 | 0.00 | 0.910 | 2.8536e-02 |
| outgoing_equivalence_plus_eta0p0625 | scalar_impedance_scan | 0.0625 | region_shape_pass | 0.9989 | 2.9825e-03 | 9.1542e-04 | 19.99 | 0.00 | 0.907 | 2.8530e-02 |
| outgoing_equivalence_plus_eta0p0312 | scalar_impedance_scan | 0.0312 | region_shape_pass | 0.9988 | 3.1620e-03 | 9.9043e-04 | 19.99 | 0.00 | 0.904 | 2.8495e-02 |
| outgoing_equivalence_plus_eta0p0156 | scalar_impedance_scan | 0.0156 | region_shape_pass | 0.9986 | 3.5273e-03 | 1.1994e-03 | 19.99 | 0.00 | 0.892 | 2.8333e-02 |
| electric_only_outgoing | fixed_eta0 | 1 | physics_proxy_pass | 0.9868 | 1.8414e-02 | 1.4090e-02 | 0.00 | 0.00 | 0.729 | 1.3574e+04 |

## Reading

- This Python gate uses real CST local Huygens probe values
  instead of the previous FarfieldPlot-derived 13 m near-field surrogate.
- The equivalent-current formulas are deliberately kept as a diagnostic proxy:
  `J ~= -E_t/eta_eff` and `M = -n x E_t`. The scalar impedance scan tunes
  the relative electric/magnetic current weight against the Level 1 far-field
  reference, making it a calibration proxy rather than final report-level
  Stratton-Chu/Huygens evidence.
- Broad, ring-like, or multi-peak reference patterns can make the single-point
  main-lobe metric stricter than the whole-pattern shape metrics. Treat
  `region_shape_pass` or `shape_pass_lobe_ambiguous` as good data-chain
  signals, not as final physics passes.
- Final G3 evidence still needs a stricter vector surface-integral operator
  plus H-field or impedance-backed current estimates.

## Generated Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_field_quality.csv` | Local field completeness and geometry/audit metrics. |
| `meshsafe_huygens_extrapolation_results.csv` | Per-variant far-field comparison metrics. |
| `meshsafe_huygens_best_farfield.csv` | Best diagnostic predicted/reference far-field table. |
| `meshsafe_huygens_extrapolation_summary.json` | Machine-readable summary. |

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_halfwave_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_impedance_lower_scan\L1_halfwave_dipole_z_1p2G
```
