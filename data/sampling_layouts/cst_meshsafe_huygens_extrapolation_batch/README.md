# CST Mesh-Safe Huygens Batch Gate

This directory aggregates the local Huygens extrapolation diagnostics for all
available mesh-safe Level 1 CST exports. Each case keeps its own detailed
single-case report in a child directory, while this folder records the
cross-case pass/fail picture.

## Summary

- Cases requested: `2`
- Cases completed: `2`
- Missing/failed cases: `0`
- Best strict/physics-proxy cases: `1`
- Best strict/physics-proxy/region cases: `2`

## Case Table

| Sample | Best status | Best variant | Corr | Scaled NMSE | Point-lobe error / deg | Region-lobe error / deg | Region Jaccard |
|---|---|---|---:|---:|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | physics_proxy_pass | electric_only_outgoing | 0.9868 | 1.4090e-02 | 0.00 | 0.00 | 0.729 |
| L1_short_dipole_z_1p2G | region_shape_pass | outgoing_equivalence_minus | 0.9989 | 6.9646e-04 | 139.52 | 0.00 | 0.919 |

## Reading

This is a batch data-chain gate, not the final Huygens physics proof. The
region-lobe metrics compare the overlap of the top-power directional regions,
which is more stable than a single argmax for broad or ring-like patterns. Final
claims still require a stricter vector surface-integral operator and H-field or
calibrated impedance support.

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```
