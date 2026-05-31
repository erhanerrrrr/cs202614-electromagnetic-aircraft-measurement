# CST Level 2 manifest

This folder contains the planned CST multi-source/multi-frequency recognition cases for CS-202614.

## Files

| File | Use |
|---|---|
| `level2_case_manifest.csv` | One row per sample/frequency pair. Use it to configure monitors and file names. |
| `level2_source_manifest.csv` | One row per source in each sample. Use it to configure source position, orientation, amplitude, and phase. |
| `level2_labels.csv` | One row per sample_id for `src/run_cst_recognition.py`. |
| `level2_manifest_summary.json` | Counts and fixed assumptions. |

## Fixed plan

- Classes: comm_pair, radar_top, mixed_avionics, multi_state_on.
- Variants per class: 12.
- Frequencies: 0.90 GHz, 1.05 GHz, 1.20 GHz, 1.35 GHz, 1.50 GHz.
- Measurement surface: 13 m upper hemisphere, 162 spatial points.
- Near-field export: Ex/Ey/Ez complex field at every sensor point.
- Far-field export: Etheta/Ephi complex field or gain on a 19 x 36 theta/phi grid.

## CST handoff

For each `sample_id`, build or duplicate the CST project listed in `cst_project`.
For every frequency row, create/enable the named near-field and far-field monitors.
After export, concatenate rows into the CSV names listed in `nearfield_export` and `farfield_export`.
Then run:

```powershell
python src\check_cst_export.py --nearfield data\cst_exports\level2\<sample_id>_nearfield.csv --farfield data\cst_exports\level2\<sample_id>_farfield.csv
python src\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
```
