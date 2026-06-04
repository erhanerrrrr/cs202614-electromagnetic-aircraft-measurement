# CST Mesh-Safe Huygens Impedance Stability Gate

## Status

Overall status: `cross_case_impedance_disagreement`

This gate checks whether the scalar `eta_eff/eta0` calibration used by the
mesh-safe Huygens proxy has an interior, cross-case stable optimum. A best value
on a scan boundary is treated as a limitation, even when the far-field shape
metrics are strong.

## Case Summary

| Sample | Best eta/eta0 | Boundary | NMSE | Corr | Recommendation |
|---|---:|---|---:|---:|---|
| L1_halfwave_dipole_z_1p2G | 0.03125 | no | 0.000801291 | 0.998999 | candidate_interior_eta |
| L1_short_dipole_z_1p2G | 0.0625 | no | 0.000695935 | 0.998945 | candidate_interior_eta |


## H-Field ResultTree Readiness

| Result export | E-field hits | H-field hits | Status |
|---|---:|---:|---|
| `outputs\cst_meshsafe_huygens_result_export` | 236 | 0 | hfield_resulttree_missing |
| `outputs\cst_meshsafe_huygens_result_export_halfwave` | 236 | 0 | hfield_resulttree_missing |


## Interpretation

The current CST route is runnable for the mesh-safe projects. The remaining
issue is evidence quality: current cached ResultTree exports expose E-field
probe curves, while matching H-field probe curves have not been found. Until
H-field-backed currents or an interior stable `eta_eff` bound exist, this route
should be described as a calibrated proxy rather than final Stratton-Chu or
Huygens proof.

## Command

```powershell
python code\run_cst_impedance_stability_gate.py
```
