# CST Mesh-Safe Huygens Result Export

Purpose: audit the local Huygens CST result package and decide whether `E-Field` probe curves can be converted into the local CSV contract.

## Current Status

- Controller status: `target_contract_complete`
- Sample: `L1_short_dipole_x_1p2G`
- Field kind: `e` / `E-Field`
- Target CSV: `data\cst_exports\level1_meshsafe_huygens_source_family\L1_short_dipole_x_1p2G_level1_local_sphere_r0p35_local_efield.csv`
- Target CSV exists: `True`
- Expected contract rows: `288`
- Artifact count: `22`
- Nearfield binary present: `True`
- Farfield binary present: `True`
- Exportable local result-tree candidates: `773`

## Interpretation

A `.m3d` local nearfield artifact proves CST kept a binary field result, but it is not the same thing as a parsed CSV. The algorithm pipeline should only consume `data/cst_exports/level1_meshsafe_huygens/*_local_efield.csv` or `*_local_hfield.csv` after this controller reports a complete target contract.

If only binary artifacts are present, the next step is to open the short-path project in CST and expose solved local `E-Field` table/result items, or add a CST-API path that reads the binary result through an official result accessor.

When `--attempt-export` is used, this controller reads 1D probe curves through `ResultTree.GetResultFromTreeItem(...).GetYRe/GetYIm` and writes the local Huygens CSV only after all Cartesian component probe values are available.

## Files

| File | Purpose |
|---|---|
| `meshsafe_huygens_export_summary.json` | Machine-readable controller summary. |
| `meshsafe_huygens_artifact_inventory.csv` | Binary/log/metadata artifact list from the CST result directory. |
| `meshsafe_huygens_export_task_plan.csv` | Contract row target, blockers, and current completion state. |
| `meshsafe_huygens_tree_inspection.json` | CST result-tree snapshot when `--inspect-tree` is used. |
| `cst_meshsafe_huygens_export_stdout.log` | CST worker stdout/stderr. |
