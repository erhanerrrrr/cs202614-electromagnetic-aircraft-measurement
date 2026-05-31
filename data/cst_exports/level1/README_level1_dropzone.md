# Level 1 real CST export dropzone

Immediate G2 required files:

- `data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv` and `data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv`
- `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv` and `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv`

Rules:

- Use meters for coordinates.
- Keep `sample_id` and `frequency_hz` exactly as listed in the manifest.
- Export complex fields as real/imag columns when possible.
- If CST exports magnitude/phase, use the `_phase.csv` filenames and then run `normalize_cst_complex_columns.py`.
