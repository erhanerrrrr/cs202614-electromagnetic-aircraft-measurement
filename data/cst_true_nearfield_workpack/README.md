# CST true near-field monitor workpack

This folder is a collaboration package for replacing the current
FarfieldPlot-derived Level 1 angular samples with true CST near-field monitor
samples on the same upper-hemisphere shell.

It is not simulation evidence yet. It defines the CST task, CSV contract, and
comparison checklist that must be executed before stronger NF-FF/SWE claims are
made in the report.

## Files

| File | Purpose |
|---|---|
| `true_nearfield_monitor_cases.csv` | One row per Level 1 case with source coordinates, monitor name, export paths, and validation command. |
| `true_nearfield_sensor_shell.csv` | The 162-point upper-hemisphere shell to sample from the true near-field monitor. |
| `true_nearfield_export_contract.csv` | Required CSV columns for true near-field exports. |
| `true_nearfield_vs_farfieldplot_checklist.csv` | Operator and algorithm checklist for the comparison run. |
| `cst_true_nearfield_monitor_template.bas` | CST VBA skeleton for building/exporting the monitor. |
| `true_nearfield_workpack_summary.json` | Machine-readable counts and source paths. |

## Immediate gate

Run the required cases first:

```text
L1_short_dipole_z_1p2G, L1_halfwave_dipole_z_1p2G
```

For each case, export `Ex`, `Ey`, and `Ez` as complex values at every sensor in
`true_nearfield_sensor_shell.csv`. The expected row count per case is
`486`.

After export, compare the true near-field monitor table against the existing
FarfieldPlot-derived table. The current FarfieldPlot-derived table is useful as
a solver-safe angular baseline, but it should not be described as a full-wave
near-field monitor.

Use this command pattern after each case export:

```powershell
python code\compare_true_nearfield_exports.py --true-nearfield <true-monitor-csv> --reference-nearfield <farfieldplot-derived-csv> --out-dir data\cst_true_nearfield_workpack\comparison\<sample-id>
```

## Acceptance logic

1. If true-monitor samples match the current baseline closely, keep the current
   reconstruction diagnostics and upgrade the wording from angular sample
   baseline to monitor-confirmed baseline.
2. If they differ in amplitude only, add an amplitude normalization step before
   rerunning source-model and sampling tradeoff scripts.
3. If they differ in phase, polarization, or main-lobe direction, use the true
   monitor export as the authoritative Level 1 baseline and rerun G3 before
   claiming reduced sampling performance.
