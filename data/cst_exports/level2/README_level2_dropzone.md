# Level 2 real CST export dropzone

Run these pilot files after G2 passes:

- `data/cst_exports/level2/L2_comm_pair_000_nearfield.csv` and `data/cst_exports/level2/L2_comm_pair_000_farfield.csv`
- `data/cst_exports/level2/L2_mixed_avionics_000_nearfield.csv` and `data/cst_exports/level2/L2_mixed_avionics_000_farfield.csv`
- `data/cst_exports/level2/L2_multi_state_on_000_nearfield.csv` and `data/cst_exports/level2/L2_multi_state_on_000_farfield.csv`
- `data/cst_exports/level2/L2_radar_top_000_nearfield.csv` and `data/cst_exports/level2/L2_radar_top_000_farfield.csv`

Full Level 2 requires all 48 sample exports listed in `outputs/cst_level2_plan/level2_case_manifest.csv`.
Do not start final recognition until `python src\merge_cst_level2_exports.py --strict` passes.
