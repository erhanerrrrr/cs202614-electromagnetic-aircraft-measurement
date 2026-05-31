# CST Level 2 workpack

This folder converts the Level 2 multi-source manifest into CST execution assets.

Current selected measurement surface: 2π upper hemisphere.

Sensor layout source:

```text
outputs\cst_templates\sensor_layout_hemisphere_for_cst.csv
```

## Files

| File | Use |
|---|---|
| `level2_cst_sample_work_items.csv` | One row per CST sample/project. |
| `level2_cst_frequency_tasks.csv` | One row per sample-frequency monitor/export task. |
| `level2_cst_export_checklist.csv` | Project/export/audit/screenshot checklist. |
| `level2_class_summary.csv` | Class-level sample and source summary. |
| `case_cards/<sample_id>.md` | Human-readable CST task card for each sample. |

Planned samples: 48  
Sample-frequency tasks: 240

## Required Commands After Export

```powershell
python src\merge_cst_level2_exports.py
python src\merge_cst_level2_exports.py --strict
python src\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
python src\run_cst_recognition_ablation.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_ablation
```

Run Level 2 only after Level 1 required cases pass.
