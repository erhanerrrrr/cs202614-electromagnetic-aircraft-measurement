' CST export contract template for CS-202614
' Use these columns when configuring or post-processing CST exports.

Option Explicit

' Near-field required columns:
' sample_id, frequency_hz, sensor_id, x_m, y_m, z_m,
' Ex_real, Ex_imag, Ey_real, Ey_imag, Ez_real, Ez_imag
'
' Far-field required columns:
' sample_id, frequency_hz, theta_deg, phi_deg,
' Etheta_real, Etheta_imag, Ephi_real, Ephi_imag
' Optional but useful: gain_db
'
' If CST exports magnitude/phase, keep the filenames ending in _phase.csv and run:
' python src\normalize_cst_complex_columns.py --phase-unit deg ...
