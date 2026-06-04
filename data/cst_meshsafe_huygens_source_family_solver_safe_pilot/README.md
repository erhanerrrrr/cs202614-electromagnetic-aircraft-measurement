# CST source-family solver-safe pilot

Purpose: diagnose the first source-family CST solver timeout without changing the frozen Huygens rule.

The current blocker is not CST startup. The previous pilot started through the real CST API and populated ResultTree probe entries, but the default time-domain solve did not finish export inside the timeout. This workpack turns that blocker into a short diagnostic ladder.

## Status

- Stage status: `source_family_solver_safe_pilot_plan_ready`
- Target sample: `L1_short_dipole_x_1p2G`
- Full local probe rows: `96`
- Planned CST diagnostic trials: `6`

## Ladder

| Order | Ladder | Probe mode | Probe rows | Timeout / s | Purpose |
|---:|---|---|---:|---:|---|
| 1 | `none` | `none` | 0 | 240 | Geometry, port, near-field monitor, and far-field monitor solve without local probes. |
| 2 | `efarfield96` | `efarfield` | 96 | 300 | Preserve angular sampling with CST far-field probes before local Cartesian E probes. |
| 3 | `efield24` | `efield` | 24 | 360 | Small local Cartesian E-field probe subset on the same 0.35 m Huygens sphere. |
| 4 | `hfield24` | `hfield` | 24 | 360 | Small local Cartesian H-field probe subset using the same sample and nodes as efield24. |
| 5 | `efield48` | `efield` | 48 | 480 | Intermediate local E-field probe count. |
| 6 | `efield96` | `efield` | 96 | 720 | Full local E-field source-family pilot, matching the frozen-rule export contract. |

## Run order

Run the `generate_command` and then the `solve_command` for each ladder row. Stop at the first repeated timeout and summarize with:

```powershell
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

Important files:

- `solver_safe_pilot_case.csv`: one-case CST source-family pilot input.
- `solver_safe_probe_*.csv`: probe subsets used by the ladder.
- `solver_safe_pilot_commands.csv`: ordered generation and solver commands.
- `solver_safe_pilot_plan_summary.json`: machine-readable plan summary.
