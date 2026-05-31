# Run from the project root after real CST Level 1 exports exist.

# Optional only if CST exported magnitude/phase files for L1_short_dipole_z_1p2G
python src\normalize_cst_complex_columns.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield_phase.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield_phase.csv --nearfield-out data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield-out data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --phase-unit deg --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_phase_conversion.json

# Validate and reconstruct L1_short_dipole_z_1p2G
python src\check_cst_export.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_validation.json
python src\run_cst_reconstruction.py --nearfield data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv --sample-id L1_short_dipole_z_1p2G --frequency-hz 1200000000 --out-dir outputs\cst_reconstruction\L1_short_dipole_z_1p2G

# Optional only if CST exported magnitude/phase files for L1_halfwave_dipole_z_1p2G
python src\normalize_cst_complex_columns.py --nearfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield_phase.csv --farfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield_phase.csv --nearfield-out data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv --farfield-out data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv --phase-unit deg --json-out outputs\cst_reconstruction\L1_halfwave_dipole_z_1p2G_phase_conversion.json

# Validate and reconstruct L1_halfwave_dipole_z_1p2G
python src\check_cst_export.py --nearfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv --json-out outputs\cst_reconstruction\L1_halfwave_dipole_z_1p2G_validation.json
python src\run_cst_reconstruction.py --nearfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv --farfield data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv --sample-id L1_halfwave_dipole_z_1p2G --frequency-hz 1200000000 --out-dir outputs\cst_reconstruction\L1_halfwave_dipole_z_1p2G

# Strict G2 gate check after both required cases are exported.
python src\merge_cst_level1_exports.py --strict
python src\run_cst_level1_batch_reconstruction.py --require-cases
python src\build_scorecard.py
python src\build_completion_audit.py
python src\build_master_dashboard.py
