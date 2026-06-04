# CST Huygens Source-Family Workpack

This workpack is the next independent CST validation gate after the frozen real E/H rule and rotation-covariance check.

## Current Scope

- Automation-ready axis-aligned single-source cases: `6`
- Case-specific local Huygens probe rows: `576`
- Frozen rule to test after export: `eh_love_equivalence_minus_j96`
- Per-source retuning is not allowed for this gate.

## Files

| File | Purpose |
|---|---|
| `level1_source_family_axis_aligned_cases.csv` | Axis-aligned x/y/off-axis source-family CST cases ready for project generation. |
| `level1_source_family_probe_points.csv` | Case-scoped local Huygens probe points; scripts filter rows by `sample_id`. |
| `source_family_validation_matrix.csv` | Full validation matrix, including tilted and multi-source gates that still need a generator/manual build. |
| `next_source_family_commands.csv` | Ordered project-generation, solver, and ResultTree export commands. |
| `source_family_workpack_summary.json` | Machine-readable workpack status. |

## Interpretation

Passing the existing rotation-covariance gate proves that the Python operator is coordinate-consistent. This workpack asks a stronger question: does the same frozen E/H rule remain accepted on independent CST solves that were not used to tune the rule?

The current automation-ready set covers x/y orientation and off-axis translation for the two Level 1 dipole lengths. Tilted and multi-source cases remain listed as explicit next gates rather than silently treated as solved.