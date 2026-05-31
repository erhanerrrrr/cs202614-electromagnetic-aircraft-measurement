# CST Level 1 export checklist

1. Use the coordinates in `sensor_layout_hemisphere_for_cst.csv`.
2. Export near-field complex Ex/Ey/Ez at 1.2 GHz.
3. Fill `nearfield_import_template.csv` or create an equivalent CSV with the same columns.
4. Export far-field Etheta/Ephi complex values or gain_db on theta/phi grid.
5. Keep `sample_id` identical between near-field and far-field files.
6. Run:

```powershell
python src\check_cst_export.py --nearfield outputs\cst_templates\nearfield_import_template.csv
```

Template files intentionally contain blank field values and should fail numeric validation until CST values are filled.
Use `nearfield_demo_valid.csv` and `farfield_demo_valid.csv` only to test the Python interface; they are synthetic data, not CST evidence.
