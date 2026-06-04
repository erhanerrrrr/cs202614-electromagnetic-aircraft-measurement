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

## Case Table

| Sample | Best status | Best variant | Corr | Scaled NMSE | Main-lobe error / deg |
|---|---|---|---:|---:|---:|
| L1_halfwave_dipole_z_1p2G | physics_proxy_pass | electric_only_outgoing | 0.9868 | 1.4090e-02 | 0.00 |
| L1_short_dipole_z_1p2G | shape_pass_lobe_ambiguous | outgoing_equivalence_minus | 0.9989 | 6.9646e-04 | 139.52 |

## Reading

This is a batch data-chain gate, not the final Huygens physics proof. A case is
useful here when the local CST probe CSV is complete, the farfield reference can
be matched, and the diagnostic equivalent-current variants preserve the main
directional structure. Final claims still require a stricter vector
surface-integral operator and H-field or calibrated impedance support.

## Command

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```
