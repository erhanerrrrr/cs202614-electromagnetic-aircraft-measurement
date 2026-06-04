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
| Variant | `electric_only_outgoing` |
| Status | `physics_proxy_pass` |
| Correlation | `0.9868` |
| Normalized NMSE | `1.8414e-02` |
| Scale-fitted power NMSE | `1.4090e-02` |
| Main-lobe error / deg | `0.00` |

## Variant Ranking

| Variant | Status | Corr | Norm NMSE | Scaled NMSE | Main-lobe error / deg | Best power scale |
|---|---|---:|---:|---:|---:|---:|
| electric_only_outgoing | physics_proxy_pass | 0.9868 | 1.8414e-02 | 1.4090e-02 | 0.00 | 1.3574e+04 |
| outgoing_equivalence_minus | shape_pass_lobe_ambiguous | 0.9990 | 2.7957e-03 | 8.5651e-04 | 19.99 | 2.8534e-02 |
| magnetic_only_plus | shape_pass_lobe_ambiguous | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 2.8535e-02 |
| magnetic_only_minus | shape_pass_lobe_ambiguous | 0.9990 | 2.8066e-03 | 8.5939e-04 | 19.99 | 2.8535e-02 |
| outgoing_equivalence_plus | shape_pass_lobe_ambiguous | 0.9989 | 2.8175e-03 | 8.6235e-04 | 19.99 | 2.8535e-02 |

## Reading

- This is the first Python gate that uses real CST local Huygens probe values
  instead of the previous FarfieldPlot-derived 13 m near-field surrogate.
- The equivalent-current formulas are deliberately kept as a diagnostic proxy:
  `J ~= -E_t/eta0` and `M = -n x E_t`. They are good enough to expose data
  quality, directionality, and sign conventions, but not final report-level
  Stratton-Chu/Huygens evidence.
- Broad, ring-like, or multi-peak reference patterns can make the single-point
  main-lobe metric stricter than the whole-pattern shape metrics. Treat
  `shape_pass_lobe_ambiguous` as a good data-chain signal, not as a final
  physics pass.
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
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_halfwave_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_extrapolation_batch\L1_halfwave_dipole_z_1p2G
```
