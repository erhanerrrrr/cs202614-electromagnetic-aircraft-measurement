# CST Mesh-Safe Huygens Batch Gate

This directory aggregates the local Huygens extrapolation diagnostics for all
available mesh-safe Level 1 CST exports. Each case keeps its own detailed
single-case report in a child directory, while this folder records the
cross-case pass/fail picture.

## Summary

- Cases requested: `2`
- Cases completed: `2`
- Missing/failed cases: `0`
- Best strict/physics-proxy cases: `0`
- Best region-shape cases: `2`
- Best strict/physics-proxy/region cases: `2`
- Cases with real H-field loaded: `2`
- Cases with accepted real-H candidates: `2`
- Cases with accepted real E/H candidates: `2`
- Best variants using real H-field: `0`
- Impedance scan enabled: `True`
- Best non-eta0 impedance cases: `2`

## Case Table

| Sample | H-field | Real E/H accepted | Best status | Best variant | Best real E/H | Eta/eta0 | Corr | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard |
|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | True | 2/2 | region_shape_pass | outgoing_equivalence_minus_eta0p25 | region_shape_pass:eh_love_equivalence_minus | 0.25 | 0.9990 | 8.4827e-04 | 19.99 | 0.00 | 0.910 |
| L1_short_dipole_z_1p2G | True | 2/2 | region_shape_pass | outgoing_equivalence_minus_eta0p25 | region_shape_pass:eh_love_equivalence_minus | 0.25 | 0.9989 | 6.9621e-04 | 139.52 | 0.00 | 0.919 |

## Reading

This is a batch data-chain gate, not the final Huygens physics proof. The
region-lobe metrics compare the overlap of the top-power directional regions,
which is more stable than a single argmax for broad or ring-like patterns. When
matching H-field rows are present, the gate evaluates real dual-field surface
currents `J = n x H_t` and `M = -n x E_t`; when H-field rows are missing, it
falls back to the older E-only impedance proxy. Final claims still require a
stricter vector surface-integral operator and source-family cross-checks. The
scalar impedance scan remains visible because it is useful as a calibration
baseline against the Level 1 far-field reference.

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```
