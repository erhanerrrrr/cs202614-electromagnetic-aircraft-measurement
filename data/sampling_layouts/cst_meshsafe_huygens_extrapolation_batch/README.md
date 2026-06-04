# CST Mesh-Safe Huygens Batch Gate

This directory aggregates the local Huygens extrapolation diagnostics for all
available mesh-safe Level 1 CST exports. Each case keeps its own detailed
single-case report in a child directory, while this folder records the
cross-case pass/fail picture.

## Summary

- Cases requested: `2`
- Cases completed: `2`
- Missing/failed cases: `0`
- Best strict/physics-proxy cases: `2`
- Best region-shape cases: `0`
- Best strict/physics-proxy/region cases: `2`
- Cases with real H-field loaded: `2`
- Cases with accepted real-H candidates: `2`
- Cases with accepted real E/H candidates: `2`
- Best variants using real H-field: `2`
- Impedance scan enabled: `True`
- Best non-eta0 impedance cases: `0`
- Real E/H J-scale scan factors: `[0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0, 64.0, 96.0, 128.0, 192.0, 256.0, 384.0, 512.0]`
- Real E/H operator calibration status: `cross_case_sign_and_scale_disagreement`
- Best real E/H J-scale values: `[96.0, 256.0]`
- Best real E/H variant families: `['eh_love_equivalence_minus', 'eh_love_equivalence_plus']`
- Best real E/H J-scale ratio: `2.667`
- Best real E/H boundary cases: `0`

## Case Table

| Sample | H-field | Real E/H accepted | Best status | Best variant | Best real E/H | Eta/eta0 | Corr | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | True | 36/36 | strict_pass | eh_love_equivalence_minus_j96 | strict_pass:eh_love_equivalence_minus_j96/J=96.0 | 1 | 0.9991 | 7.1320e-04 | 0.00 | 0.00 | 0.924 |
| L1_short_dipole_z_1p2G | True | 36/36 | strict_pass | eh_love_equivalence_plus_j256 | strict_pass:eh_love_equivalence_plus_j256/J=256.0 | 1 | 0.9985 | 9.9532e-04 | 0.00 | 0.00 | 0.902 |

## Reading

This is a batch data-chain gate, not the final Huygens physics proof. The
region-lobe metrics compare the overlap of the top-power directional regions,
which is more stable than a single argmax for broad or ring-like patterns. When
matching H-field rows are present, the gate evaluates real dual-field surface
currents `J = n x H_t` and `M = -n x E_t`, plus a controlled global J-scale
scan that keeps the measured H-field distribution but tests the operator
normalization; when H-field rows are missing, it falls back to the older E-only
impedance proxy. Final claims still require a stricter vector surface-integral
operator and source-family cross-checks. The scalar impedance scan remains
visible because it is useful as a calibration baseline against the Level 1
far-field reference.

The best real E/H branches should not be treated as a final source-independent
operator until the J-scale values and plus/minus convention are stable across
source families. A strict or proxy pass with
`cross_case_sign_and_scale_disagreement` is useful algorithm evidence, but it
still calls for a broader CST source-family gate before final wording.

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```
