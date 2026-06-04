# S37 G3 mesh-safe Huygens real E/H extrapolation

## What Changed

- Ran the H-field mesh-safe CST route for `L1_short_dipole_z_1p2G`.
- Exported the short-dipole local H-field ResultTree probe CSV:
  `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv`.
- Upgraded `code/run_cst_meshsafe_huygens_extrapolation.py` from E-only
  impedance proxy mode to optional real E/H mode.
- Added automatic `_local_hfield.csv` discovery, E/H geometry alignment checks,
  H-field quality metrics, and real dual-field equivalent-current variants:
  `J = n x H_t` and `M = -n x E_t`.
- Regenerated the single short-dipole gate and the two-case batch gate.

## Why

S36 prepared the H-field workpack but still treated H-field as a missing
handoff. This stage closes that gap for the short-dipole case. The CST popup
about unavailable ASCII export did not indicate a general CST failure; it came
from using the wrong export surface for a Field Monitor view. The working route
is CST `ResultTree` probe-curve extraction.

The main problem has therefore moved from CST execution to Huygens operator
calibration: the real E/H branch works and passes the region-shape gate, but the
current simplified far-field kernel still ranks the scalar impedance proxy
slightly ahead of the true E/H branch.

## Main Artifacts

| Path | Meaning |
|---|---|
| `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` | Real CST local H-field probe export, `96 * 3 = 288` rows. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Now auto-loads matching H-field rows and evaluates real E/H surface-current variants. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation/` | Short-dipole single-case E/H diagnostic gate. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | Two-case batch gate with H-field availability and real-H usage columns. |
| `C:\csttmp\huy_hs\h_short_hfield.cst` | Local short-path solved H-field CST project cache; not a Git payload. |

## Validation

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py
python code\run_cst_meshsafe_huygens_extrapolation.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```

Current result:

- Syntax validation passed.
- Short-dipole single gate loads H-field successfully:
  `hfield_available = True`.
- Short-dipole local E/H quality is physically plausible:
  tangential E/H impedance is about `425.36 ohm`, or `1.129 eta0`.
- Best short-dipole overall branch is still
  `outgoing_equivalence_minus_eta0p25`, with `region_shape_pass`,
  correlation about `0.9989`, and scale-fitted NMSE about `6.96e-04`.
- The best real E/H branch, `eh_love_equivalence_minus`, also reaches
  `region_shape_pass`, correlation about `0.9989`, scale-fitted NMSE about
  `6.96e-04`, region error `0 deg`, and region Jaccard about `0.919`.
- Batch gate completes `2/2` cases, with `1/2` real H-field loaded and `0/2`
  best variants using real H-field.

## Current Interpretation

CST is not the current blocker. It can generate short-path projects, run the
mesh-safe solver, retain binary field results, expose ResultTree probe curves,
and export contract CSVs. The earlier Field Monitor ASCII popup is an export
adapter mismatch.

The current blocker is algorithmic calibration. The simplified diagnostic
kernel treats magnetic/electric surface current contributions with a compact
dipole-sum approximation, so the real E/H branch needs stricter Green-function
normalization, sign convention checks, and source-family repetition before it
can replace the scalar impedance proxy in report-level claims.

## Next Step

1. Run the same H-field solve/export path for `L1_halfwave_dipole_z_1p2G`.
2. Add a stricter vector surface-integral/Huygens operator, then compare
   `eh_love_equivalence_plus/minus` against the current impedance proxy.
3. Use the measured tangential E/H impedance as a diagnostic prior, not as the
   final calibration constant.
4. After both Level 1 sources have real E/H rows, propagate the local Huygens
   prediction toward the 13 m measurement shell and evaluate reduced-layout
   sampling stability.
