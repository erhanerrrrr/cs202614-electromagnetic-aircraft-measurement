# True near-field comparison

This folder contains comparison metrics between a candidate CST true
near-field monitor export and the current FarfieldPlot-derived Level 1
near-field table.

## Files

| File | Purpose |
|---|---|
| `nearfield_export_comparison_by_group.csv` | Per sample, frequency, and polarization comparison metrics. Rows with `polarization=all` concatenate Ex/Ey/Ez. |
| `nearfield_export_comparison_summary.json` | Machine-readable worst-case summary. |

## Current summary

- Common rows: 972
- Missing candidate rows: 0
- Missing reference rows: 0
- Minimum all-component complex correlation: 1.000000
- Maximum all-component relative L2 error: 0.000000e+00
- Maximum all-component scaled relative L2 error: 0.000000e+00

Use this as a diagnostic gate, not as final sampling evidence. If a real CST
true-monitor export differs from the FarfieldPlot-derived baseline, rerun the
Level 1 source-model and sampling diagnostics with the true-monitor table.
