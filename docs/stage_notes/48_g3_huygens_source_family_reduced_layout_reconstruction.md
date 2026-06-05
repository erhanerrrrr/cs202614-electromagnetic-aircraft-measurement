# S48 G3 Huygens source-family reduced-layout reconstruction

## What changed

This stage adds a reduced-layout gate on top of the validated short-x CST
source-family matched E/H pilot. It does not rerun CST. It reads the exported
96-point local E/H surface and the CST far-field reference, then tests whether
sparse local samples can support the same frozen Huygens operator after
reconstructing the full local surface.

## Why this matters

Directly deleting local Huygens surface cells is not a valid reduced-sampling
claim for this pilot: all direct-subset frozen rows failed. The deployable chain
that works is:

1. select a geometry-only sparse local layout;
2. fit a complex Cartesian polynomial surface model from the selected E/H
   samples;
3. reconstruct the full 96-node local Huygens surface;
4. run the same frozen `eh_love_equivalence_minus_j96` propagation rule;
5. compare against the CST FarfieldPlot far-field reference.

This keeps the sampling claim tied to sparse measurement plus reconstruction,
not to raw quadrature thinning.

## Key artifacts

| Path | Purpose |
|---|---|
| `code/run_cst_meshsafe_huygens_reduced_layout.py` | Builds deterministic sparse layouts, reconstructs full local E/H surfaces, and reruns the frozen Huygens gate. |
| `data/sampling_layouts/cst_meshsafe_huygens_source_family_reduced_layout_x/reduced_layout_summary.json` | Machine-readable reduced-layout gate summary. |
| `data/sampling_layouts/cst_meshsafe_huygens_source_family_reduced_layout_x/reduced_layout_summary.csv` | Per-layout frozen and best-row metrics. |
| `data/sampling_layouts/cst_meshsafe_huygens_source_family_reduced_layout_x/README.md` | Human-readable result table and interpretation. |
| `data/sampling_layouts/cst_meshsafe_huygens_source_family_reduced_layout_x/layouts/` | Generated sparse inputs, reconstructed full-96 inputs, and per-layout Huygens comparison files. |
| `code/build_cst_source_family_solver_safe_status.py` | Now promotes the short-x pilot to `source_family_solver_safe_reduced_layout_validated` when this gate passes. |
| `code/build_g3_model_dashboard.py` | Now reports the reduced-layout gate and moves the next action to y/off-axis source-family expansion. |

## Result

- Gate status: `reduced_layout_validated`.
- Layout rows tested: `25`.
- Frozen accepted layouts: `13/25`.
- Deployable frozen accepted layouts: `9`.
- Direct-subset frozen accepted layouts: `0`.
- Reconstructed frozen accepted layouts: `12`.
- Smallest deployable frozen pass: `fibonacci_snap_24`.
- Sensor count: `24`.
- Reconstruction degree: `3`.
- Frozen correlation: about `0.9942`.
- Frozen scaled NMSE: about `1.403e-3`.
- Main-lobe region error: about `8.54e-7 deg`.
- Main-lobe region Jaccard: about `0.9095`.
- E/H holdout NRMSE: about `0.0418` / `0.0578`.

## Verification

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_reduced_layout.py
python code\run_cst_meshsafe_huygens_reduced_layout.py
python -m py_compile code\build_cst_source_family_solver_safe_status.py code\build_g3_model_dashboard.py
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

## Boundary and next step

This closes the short-x source-family pilot gate, not the whole source-family
proof. The next engineering step is to run the same CST export, sparse
reconstruction, and frozen-j96 Huygens comparison on y-oriented and off-axis
source-family cases without retuning the operator.
