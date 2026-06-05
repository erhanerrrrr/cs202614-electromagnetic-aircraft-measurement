# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_72_local_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_72_local_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `72` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.349916` |
| Tangential/total L2 ratio | `0.9886` |
| Normal/total L2 ratio | `0.1506` |
| Dynamic range / dB | `10.89` |
| H tangential/total L2 ratio | `0.9995` |
| H normal/total L2 ratio | `0.0310` |
| H dynamic range / dB | `16.64` |
| Tangential E/H impedance / ohm | `370.483` |
| Tangential E/H eta0 ratio | `0.9834` |

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
| Correlation | `0.4039` |
| Normalized NMSE | `5.8272e-01` |
| Scale-fitted power NMSE | `2.9274e-01` |
| Main-lobe error / deg | `159.85` |
| Region-lobe error / deg | `153.05` |
| Region-lobe Jaccard | `0.010` |
| Region-lobe min capture | `0.009` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| electric_only_outgoing | fixed_eta0 | False | 1 |  | diagnostic_only | 0.4039 | 5.8272e-01 | 2.9274e-01 | 159.85 | 153.05 | 0.010 | 6.1166e+03 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | diagnostic_only | 0.3877 | 6.0796e-01 | 2.8937e-01 | 159.85 | 153.05 | 0.008 | 6.1275e+03 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.0961 | 4.6414e-01 | 2.9868e-01 | 119.88 | 49.97 | 0.000 | 2.0550e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | diagnostic_only | 0.0751 | 4.6922e-01 | 3.0457e-01 | 50.23 | 19.74 | 0.005 | 2.0217e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0727 | 4.5201e-01 | 3.0823e-01 | 119.88 | 30.05 | 0.011 | 2.0840e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0727 | 4.5206e-01 | 3.0829e-01 | 119.88 | 30.05 | 0.011 | 2.0839e-02 |
| magnetic_only_plus | not_used | False | 1 |  | diagnostic_only | 0.0726 | 4.5185e-01 | 3.0831e-01 | 119.88 | 30.05 | 0.011 | 2.0837e-02 |
| magnetic_only_minus | not_used | False | 1 |  | diagnostic_only | 0.0726 | 4.5185e-01 | 3.0831e-01 | 119.88 | 30.05 | 0.011 | 2.0837e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | diagnostic_only | 0.0725 | 4.5163e-01 | 3.0834e-01 | 119.88 | 30.05 | 0.011 | 2.0836e-02 |
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | diagnostic_only | 0.0724 | 4.5168e-01 | 3.0839e-01 | 119.88 | 30.05 | 0.011 | 2.0835e-02 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_72_local_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\fibonacci_snap_72\direct_subset
```
