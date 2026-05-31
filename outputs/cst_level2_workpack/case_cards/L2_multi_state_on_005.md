# L2_multi_state_on_005

Class label: `multi_state_on`  
Variant index: `5`  
Current measurement surface: 2π upper hemisphere.

## CST Project

| Item | Value |
|---|---|
| CST project | `CST_L2_multi_state_on_005.cst` |
| Carrier model | `level2_multisource_no_airframe` |
| Working state | `multi_state_on_state` |
| Source config | `multi_state_on` |
| Frequency count | 5 |
| Near-field export | `data/cst_exports/level2/L2_multi_state_on_005_nearfield.csv` |
| Far-field export | `data/cst_exports/level2/L2_multi_state_on_005_farfield.csv` |
| Expected near-field rows total | 2430 |
| Expected far-field rows total | 3420 |

## Sources

| idx | role | antenna model | x m | y m | z m | ox | oy | oz | amplitude | phase deg |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | `left_top_emitter` | `ideal_dipole_or_small_discrete_port` | -5.5 | 4.5 | 7.0 | 1.0 | 0.0 | 0.0 | 1.160755354372465 | 85.17837849095142 |
| 1 | `right_belly_emitter` | `ideal_dipole_or_small_discrete_port` | 5.5 | -4.5 | 1.0 | 0.0 | 1.0 | 0.0 | 0.9584721457246996 | -44.57997220063375 |
| 2 | `center_avionics` | `ideal_dipole_or_small_discrete_port` | 0.0 | 0.0 | 4.0 | 0.0 | 0.0 | 1.0 | 0.9216570934800894 | 13.318940447354231 |

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
