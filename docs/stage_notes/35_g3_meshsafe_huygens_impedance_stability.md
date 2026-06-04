# S35 G3 mesh-safe Huygens impedance stability gate

## What Changed

- Added `code/run_cst_impedance_stability_gate.py`.
- Added a new G3 dashboard row for `meshsafe_huygens_impedance_stability`.
- Recorded cached CST ResultTree readiness for H-field probe curves.
- Wrote machine-readable next commands for lower-eta scans or H-field-backed closure.

## Why

The S34 scalar impedance calibration improved the two real CST mesh-safe
Huygens proxy cases, but both cases selected the lowest scanned value
(`eta_eff = 0.25 eta0`). A boundary optimum is not an independent physics
closure; it means the grid is still telling us to either look below the boundary
or replace the proxy with real H-field-backed equivalent currents.

This stage separates two facts that were easy to blur together:

1. CST is runnable on the mesh-safe route: short-path projects solve and
   ResultTree E-field probe export works.
2. The current blocker is evidence quality: 3D Field Monitor ASCII export is
   not the right handoff path, and cached result-tree inspections do not expose
   matching H-field probe curves yet.

## Main Artifacts

| Path | Meaning | Command |
|---|---|---|
| `code/run_cst_impedance_stability_gate.py` | Reads mesh-safe Huygens batch CSVs, checks boundary/interior eta stability, and records H-field tree readiness. | `python code\run_cst_impedance_stability_gate.py` |
| `data/sampling_layouts/cst_meshsafe_huygens_impedance_stability/impedance_stability_summary.json` | Machine-readable overall status, case summaries, and H-field readiness. | Dashboard input |
| `data/sampling_layouts/cst_meshsafe_huygens_impedance_stability/impedance_stability_case_summary.csv` | Per-case best eta, boundary flags, plateau width, and recommendation. | Inspect or import as CSV |
| `data/sampling_layouts/cst_meshsafe_huygens_impedance_stability/hfield_resulttree_readiness.csv` | Cached CST result-tree E/H-field availability check. | Inspect or import as CSV |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard now includes the impedance stability bottleneck row. | `python code\build_g3_model_dashboard.py` |

## Validation

```powershell
python -m py_compile code\run_cst_impedance_stability_gate.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch --batch-out-dir data\sampling_layouts\cst_meshsafe_huygens_impedance_lower_scan --impedance-factors 0.015625,0.03125,0.0625,0.125,0.1875,0.25,0.375,0.5,0.75,1.0,1.5,2.0,3.0,4.0
python code\run_cst_impedance_stability_gate.py --batch-dir data\sampling_layouts\cst_meshsafe_huygens_impedance_lower_scan
python code\build_g3_model_dashboard.py
```

Current result after the lower-eta extension:

- Lower scan completed `2/2` cases with the region-shape gate still passing.
- `L1_halfwave_dipole_z_1p2G` selected `eta_eff = 0.03125 eta0`.
- `L1_short_dipole_z_1p2G` selected `eta_eff = 0.0625 eta0`.
- The stability gate status is `cross_case_impedance_disagreement`, not a
  single global impedance closure.
- Cached tree inspections report E-field probe entries but `0` H-field entries,
  so the next physics step is still H-field export or additional source-family
  validation.

## Current Limitation

The current cached CST result-tree inspections show E-field probe curves but no
matching H-field probe curves. The existing `Field Monitor` ASCII export popup
is therefore an export-path mismatch, not evidence that CST itself cannot run.

## Next Step

1. If CST can expose H-field probe curves, export `*_local_hfield.csv` and use
   it to replace the scalar impedance proxy.
2. If H-field export remains unavailable, run the lower-eta command listed in
   `next_impedance_stability_commands.csv`.
3. Keep report wording at calibrated-proxy level until H-field-backed currents
   or an interior stable impedance bound exists.
