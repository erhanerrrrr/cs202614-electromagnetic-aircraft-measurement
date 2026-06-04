# S34 G3 mesh-safe Huygens scalar impedance calibration

## What Changed

- Added scalar `eta_eff/eta0` scanning to `code/run_cst_meshsafe_huygens_extrapolation.py`.
- Kept the original E-only and M-only diagnostic variants, then scanned the outgoing electric/magnetic equivalence variants.
- Rebuilt the two-case real CST mesh-safe batch outputs.
- Updated `code/build_g3_model_dashboard.py` so the G3 matrix recognizes the calibrated proxy as `impedance_region_proxy_batch_pass`.

## Why

S33 showed that the local CST E-field data chain is healthy, but the equivalent-current model still used a fixed free-space impedance assumption:

```text
J ~= -E_t / eta0
M ~= -n x E_t
```

This is useful as a proxy, but it hides the relative weighting between electric and magnetic equivalent currents. S34 makes that assumption explicit by scanning a small scalar impedance grid and recording the selected `eta_eff` for every case.

This is not a final Stratton-Chu/Huygens proof. The scan is calibrated against the current Level 1 far-field reference, so it is evidence about data-chain consistency and impedance sensitivity. Final physics wording still needs either H-field-backed currents or independently stable impedance bounds across more CST cases.

## Main Artifacts

| Path | Meaning | Command |
|---|---|---|
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `--impedance-factors`, per-variant `eta_eff`, and batch impedance statistics. | `python code\run_cst_meshsafe_huygens_extrapolation.py --batch` |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.csv` | Two-case calibrated batch summary, including selected `eta_eff/eta0`. | Inspect or import as CSV |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | Machine-readable evidence for dashboard integration. | Dashboard input |
| `code/build_g3_model_dashboard.py` | Adds `impedance_region_proxy_batch_pass` and the next H-field-backed action. | `python code\build_g3_model_dashboard.py` |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Current G3 status matrix with calibrated proxy status. | Inspect dashboard output |

## Validation

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

Current result:

- Batch completed `2/2` cases with `0` missing or failed exports.
- Both best settings selected `outgoing_equivalence_minus_eta0p25`, so `eta_eff = 0.25 eta0`.
- `L1_short_dipole_z_1p2G`: `region_shape_pass`, correlation about `0.9989`, scaled NMSE about `6.96e-4`, region-lobe error `0 deg`.
- `L1_halfwave_dipole_z_1p2G`: `region_shape_pass`, correlation about `0.9990`, scaled NMSE about `8.48e-4`, region-lobe error `0 deg`.
- Dashboard status is now `impedance_region_proxy_batch_pass`.

## Current Limitation

The selected impedance is reference-calibrated. It improves the real CST two-case proxy, but it is not yet an independent physical measurement of the local wave impedance.

## Next Step

1. Add CST H-field probe export if ResultTree can expose the matching probe curves.
2. If H-field export remains unavailable, stress-test `eta_eff = 0.25 eta0` on additional Level 2/source-family CST exports before using it in report wording.
3. Keep the final claim phrased as a calibrated proxy until H-field-backed currents or stable impedance bounds exist.
