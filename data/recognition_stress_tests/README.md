# Recognition Stress Tests

This directory stores small, versionable robustness summaries for the
classification/recognition branch. Large CST near-field source tables remain in
`data/cst_exports/` and are ignored by default.

## Subdirectories

| Directory | Purpose |
|---|---|
| `level2_robustness/` | Clean-train/perturbed-test Level 2 recognition stress test for selected G2 layouts. |

## Regenerate

```powershell
python code\run_cst_recognition_stress_test.py
```

## Boundary

These results are recognition robustness evidence. They do not replace the
true CST near-field monitor gate used for reduced-layout reconstruction claims,
and they do not prove full-wave complex-airframe scattering generalization.
