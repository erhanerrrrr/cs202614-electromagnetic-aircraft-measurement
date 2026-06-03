# CST Mesh-Safe Huygens Extrapolation Gate

This directory evaluates the first real CST local Huygens-surface probe export.
It consumes the `96 * 3 = 288` complex Cartesian E-field probe rows exported
through CST `ResultTree` and compares a diagnostic equivalent-current far-field
proxy against the existing Level 1 CST far-field reference.

## Inputs

| Item | Path |
|---|---|
| Local Huygens E field | `data\cst_exports\level1_meshsafe_huygens\L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` |
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

## Best Diagnostic Variant

| Field | Value |
|---|---|
| Variant | `outgoing_equivalence_minus` |
| Status | `shape_pass_lobe_ambiguous` |
| Correlation | `0.9989` |
| Normalized NMSE | `3.7631e-03` |
| Scale-fitted power NMSE | `6.9646e-04` |
| Main-lobe error / deg | `139.52` |

## Variant Ranking

| Variant | Status | Corr | Norm NMSE | Scaled NMSE | Main-lobe error / deg | Best power scale |
|---|---|---:|---:|---:|---:|---:|
| outgoing_equivalence_minus | shape_pass_lobe_ambiguous | 0.9989 | 3.7631e-03 | 6.9646e-04 | 139.52 | 7.2105e-01 |
| magnetic_only_plus | shape_pass_lobe_ambiguous | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 7.2105e-01 |
| magnetic_only_minus | shape_pass_lobe_ambiguous | 0.9989 | 3.7657e-03 | 6.9657e-04 | 139.52 | 7.2105e-01 |
| outgoing_equivalence_plus | shape_pass_lobe_ambiguous | 0.9989 | 3.7683e-03 | 6.9668e-04 | 139.52 | 7.2105e-01 |
| electric_only_outgoing | shape_pass_lobe_ambiguous | 0.9987 | 1.0419e-02 | 8.7346e-04 | 134.58 | 3.3837e+05 |

## Reading

- This is the first Python gate that uses real CST local Huygens probe values
  instead of the previous FarfieldPlot-derived 13 m near-field surrogate.
- The equivalent-current formulas are deliberately kept as a diagnostic proxy:
  `J ~= -E_t/eta0` and `M = -n x E_t`. They are good enough to expose data
  quality, directionality, and sign conventions, but not final report-level
  Stratton-Chu/Huygens evidence.
- The short-dipole reference has broad/ring-like high-power regions, so the
  single-point main-lobe error can be large even when whole-pattern correlation
  and scale-fitted NMSE are strong. Treat `shape_pass_lobe_ambiguous` as a good
  data-chain signal, not as a final physics pass.
- Final G3 evidence still needs a stricter vector surface-integral operator,
  an H-field or impedance-backed current estimate, and repetition on the
  second Level 1 source case.

## Generated Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_field_quality.csv` | Local field completeness and geometry/audit metrics. |
| `meshsafe_huygens_extrapolation_results.csv` | Per-variant far-field comparison metrics. |
| `meshsafe_huygens_best_farfield.csv` | Best diagnostic predicted/reference far-field table. |
| `meshsafe_huygens_extrapolation_summary.json` | Machine-readable summary. |

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py
```
