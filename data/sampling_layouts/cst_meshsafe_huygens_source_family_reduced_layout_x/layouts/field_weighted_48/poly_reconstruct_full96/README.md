# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates one real CST local Huygens-surface probe export.
It consumes matched complex Cartesian probe rows exported through CST
`ResultTree` and compares diagnostic equivalent-current far-field predictions
against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_poly_full96_efield.csv` |
| Local Huygens H field | `data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_poly_full96_hfield.csv` |
| H-field load status | `loaded` |
| Far-field reference | `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_farfield.csv` |

## Field Quality

| Metric | Value |
|---|---:|
| Sensors | `96` |
| Prior | `level1_local_sphere_r0p35` |
| Mean local radius / m | `0.35` |
| Tangential/total L2 ratio | `0.9872` |
| Normal/total L2 ratio | `0.1593` |
| Dynamic range / dB | `12.53` |
| H tangential/total L2 ratio | `0.9993` |
| H normal/total L2 ratio | `0.0370` |
| H dynamic range / dB | `15.68` |
| Tangential E/H impedance / ohm | `369.894` |
| Tangential E/H eta0 ratio | `0.9819` |

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `outgoing_equivalence_plus` |
| Variant family | `outgoing_equivalence_plus` |
| Calibration mode | `fixed_eta0` |
| Uses real H-field | `False` |
| Eta_eff / eta0 | `1.0` |
| Eta_eff / ohm | `376.730313668` |
| H-field J scale | `` |
| Status | `region_shape_pass` |
| Correlation | `0.9966` |
| Normalized NMSE | `1.7619e-03` |
| Scale-fitted power NMSE | `8.3277e-04` |
| Main-lobe error / deg | `154.04` |
| Region-lobe error / deg | `0.00` |
| Region-lobe Jaccard | `0.946` |
| Region-lobe min capture | `0.957` |

## Variant Ranking

| Variant | Calibration | Real H | Eta/eta0 | J scale | Status | Corr | Norm NMSE | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard | Best power scale |
|---|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| outgoing_equivalence_plus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9966 | 1.7619e-03 | 8.3277e-04 | 154.04 | 0.00 | 0.946 | 3.0987e-02 |
| eh_love_equivalence_minus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9966 | 1.7017e-03 | 8.3290e-04 | 149.72 | 0.00 | 0.948 | 3.0986e-02 |
| magnetic_only_plus | not_used | False | 1 |  | region_shape_pass | 0.9966 | 1.7236e-03 | 8.3380e-04 | 154.04 | 0.00 | 0.948 | 3.0986e-02 |
| magnetic_only_minus | not_used | False | 1 |  | region_shape_pass | 0.9966 | 1.7236e-03 | 8.3380e-04 | 154.04 | 0.00 | 0.948 | 3.0986e-02 |
| eh_love_equivalence_plus | real_eh_surface_currents | True | 1 | 1.0 | region_shape_pass | 0.9966 | 1.7510e-03 | 8.3481e-04 | 154.04 | 0.00 | 0.947 | 3.0986e-02 |
| outgoing_equivalence_minus | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9966 | 1.6910e-03 | 8.3497e-04 | 149.72 | 0.00 | 0.948 | 3.0984e-02 |
| eh_love_equivalence_minus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9952 | 5.1618e-03 | 1.1774e-03 | 142.26 | 0.00 | 0.907 | 3.0337e-02 |
| eh_love_equivalence_plus_j96 | real_eh_j_scale_scan | True | 1 | 96.0 | region_shape_pass | 0.9944 | 8.5282e-03 | 1.3660e-03 | 159.28 | 0.00 | 0.868 | 3.0378e-02 |
| electric_only_outgoing | fixed_eta0 | False | 1 |  | region_shape_pass | 0.9760 | 2.2506e-02 | 6.0698e-03 | 38.49 | 0.00 | 0.742 | 1.4379e+04 |
| hfield_electric_only | real_hfield_only | True | 1 | 1.0 | shape_pass_lobe_ambiguous | 0.9751 | 4.2442e-02 | 6.3881e-03 | 36.13 | 0.00 | 0.605 | 1.4026e+04 |

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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48_poly_full96_efield.csv --sample-id L1_short_dipole_x_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_source_family_reduced_layout_x\layouts\field_weighted_48\poly_reconstruct_full96
```
