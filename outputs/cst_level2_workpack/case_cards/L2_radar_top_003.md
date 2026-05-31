# L2_radar_top_003

Class label: `radar_top`  
Variant index: `3`  
Current measurement surface: 2π upper hemisphere.

## CST Project

| Item | Value |
|---|---|
| CST project | `CST_L2_radar_top_003.cst` |
| Carrier model | `level2_multisource_no_airframe` |
| Working state | `radar_top_state` |
| Source config | `radar_top` |
| Frequency count | 5 |
| Near-field export | `data/cst_exports/level2/L2_radar_top_003_nearfield.csv` |
| Far-field export | `data/cst_exports/level2/L2_radar_top_003_farfield.csv` |
| Expected near-field rows total | 2430 |
| Expected far-field rows total | 3420 |

## Sources

| idx | role | antenna model | x m | y m | z m | ox | oy | oz | amplitude | phase deg |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `front_top_radar` | `ideal_dipole_or_small_discrete_port` | 0.0 | -4.5 | 7.0 | 0.0 | 0.0 | 1.0 | 1.18361948762975 | 6.654926651230961 |
| 1 | `rear_top_radar` | `ideal_dipole_or_small_discrete_port` | 0.0 | 4.5 | 7.0 | 0.0 | 0.0 | 1.0 | 0.8409016130331353 | -34.531223552780574 |

## Frequency Tasks

| frequency Hz | label | near-field monitor | far-field monitor |
|---:|---|---|---|
| 900000000 | `900MHz` | `nearfield_hemisphere_900MHz` | `farfield_900MHz` |
| 1050000000 | `1050MHz` | `nearfield_hemisphere_1050MHz` | `farfield_1050MHz` |
| 1200000000 | `1200MHz` | `nearfield_hemisphere_1200MHz` | `farfield_1200MHz` |
| 1350000000 | `1350MHz` | `nearfield_hemisphere_1350MHz` | `farfield_1350MHz` |
| 1500000000 | `1500MHz` | `nearfield_hemisphere_1500MHz` | `farfield_1500MHz` |

## After Export

```powershell
python src\merge_cst_level2_exports.py
```

Only after all planned samples are complete:

```powershell
python src\merge_cst_level2_exports.py --strict
python src\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
python src\run_cst_recognition_ablation.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_ablation
```

## Manual Checks

- The CST project uses the 2π upper-hemisphere sensor layout.
- Every listed source has matching position, orientation, relative amplitude, and phase.
- Near-field exports include all 5 frequencies in one sample-level CSV.
- Far-field exports include all 5 frequencies in one sample-level CSV.
- `sample_id` and `frequency_hz` are present and match the manifest exactly.
