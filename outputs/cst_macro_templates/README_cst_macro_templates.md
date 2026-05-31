# CST macro templates

This folder turns the existing Level 1 and Level 2 manifests into CST macro inputs.
It is an execution aid, not CST simulation evidence.

## Why this exists

The current blocking gate is real CST execution. These files reduce manual copying:

- Level 1 required standard sources can be run first for G2.
- Level 2 pilot samples can be run one per class before launching the full 48-sample batch for G3.
- Export filenames and expected row counts stay synchronized with the Python audit scripts.

## Files

| File | Meaning |
|---|---|
| `level1_macro_parameters.csv` | One row per Level 1 source, including source endpoints, monitors, exports, and expected rows. |
| `level1_required_launch_order.csv` | The two required G2 cases to execute first. |
| `level2_macro_sample_parameters.csv` | One row per Level 2 sample, with frequency list and total expected export rows. |
| `level2_macro_source_parameters.csv` | One row per Level 2 source/feed, including amplitude and phase. |
| `level2_pilot_cases.csv` | One sample per class for a CST pilot run before the full batch. |
| `cst_macro_execution_checklist.csv` | Operator checklist linking each macro/action to evidence files. |
| `cst_level1_standard_source_template.bas` | CST VBA macro skeleton for Level 1. |
| `cst_level2_multisource_template.bas` | CST VBA macro skeleton for Level 2. |
| `cst_export_contract_template.bas` | Required near-field/far-field CSV column contract. |

## Current counts

- Level 1 cases: 6
- Level 1 required cases: 2
- Level 2 samples: 48
- Level 2 source rows: 120
- Sensor points on 2π hemisphere: 162

## Immediate use

1. Open CST and create or clone the first required project from `level1_required_launch_order.csv`.
2. Import or manually apply the corresponding row in `level1_macro_parameters.csv`.
3. Keep export paths exactly as listed.
4. After exporting, run:

```powershell
python src\merge_cst_level1_exports.py --strict
python src\run_cst_level1_batch_reconstruction.py --require-cases
```

After G2 passes, use `level2_pilot_cases.csv` to run one sample per class before the full Level 2 batch.
