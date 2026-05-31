# CST Level 1 workpack

This folder converts the Level 1 manifest into execution assets for the CST owner.

## Files

| File | Use |
|---|---|
| `level1_cst_work_items.csv` | One row per CST case with source endpoints, monitor names, exports, and validation thresholds. |
| `level1_cst_export_checklist.csv` | Per-case checklist for project, export, audit, reconstruction, and screenshots. |
| `case_cards/<sample_id>.md` | Human-readable CST task card for each standard source. |
| `level1_workpack_summary.json` | Counts, required gate, and command hints. |

## Immediate gate

Run the 2 required cases first. The full pack contains 6 cases.

Current selected measurement surface: 2π upper hemisphere.

Sensor layout source:

```text
outputs\cst_templates\sensor_layout_hemisphere_for_cst.csv
```

After CST exports are placed under `data/cst_exports/level1`, run:

```powershell
python src\merge_cst_level1_exports.py --strict
python src\run_cst_level1_batch_reconstruction.py --require-cases
```

If the required cases pass, run the recommended x/y short dipoles before Level 2 whenever schedule allows.
