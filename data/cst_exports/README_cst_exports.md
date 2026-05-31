# CST export dropzone

Place real CST exported CSV files here. Do not place synthetic/demo data in this folder.

- `level1/`: standard-source exports for the G2 gate.
- `level2/`: multisource/multistate exports for the G3 gate.

After adding files, rerun:

```powershell
python src\merge_cst_level1_exports.py
python src\merge_cst_level2_exports.py
python src\build_cst_execution_dashboard.py
```
