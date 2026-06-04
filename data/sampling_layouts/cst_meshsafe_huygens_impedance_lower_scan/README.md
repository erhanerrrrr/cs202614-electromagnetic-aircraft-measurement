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
- Impedance scan enabled: `True`
- Best non-eta0 impedance cases: `2`

## Case Table

| Sample | Best status | Best variant | Eta/eta0 | Corr | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard |
|---|---|---|---:|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | region_shape_pass | outgoing_equivalence_minus_eta0p0312 | 0.0312 | 0.9990 | 8.0129e-04 | 24.98 | 0.00 | 0.911 |
| L1_short_dipole_z_1p2G | region_shape_pass | outgoing_equivalence_minus_eta0p0625 | 0.0625 | 0.9989 | 6.9594e-04 | 139.52 | 0.00 | 0.919 |

## Reading

This is a batch data-chain gate, not the final Huygens physics proof. The
region-lobe metrics compare the overlap of the top-power directional regions,
which is more stable than a single argmax for broad or ring-like patterns. Final
claims still require a stricter vector surface-integral operator and independent
H-field support. The scalar impedance scan is a calibration proxy: it tunes the
relative weight of electric and magnetic equivalent currents against the current
Level 1 far-field reference and keeps the selected `eta_eff/eta0` visible in
every row.

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```
