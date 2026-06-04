# S36 G3 mesh-safe Huygens H-field workpack

## What Changed

- Extended `code/export_cst_meshsafe_huygens_results.py` from E-field-only to
  `--field-kind e|h`.
- Added the H-field CSV contract
  `data/cst_meshsafe_huygens_workpack/local_huygens_hfield_export_contract.csv`.
- Extended `code/run_cst_level1_required_automation.py` with
  `--probe-mode hfield`.
- Regenerated `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv`
  so the workpack has explicit E/H project-generation, solver-gate, and
  ResultTree export commands.

## Why

The S35 impedance stability gate showed that the scalar impedance proxy does
not yet provide a single stable cross-case physics closure. The next useful
upgrade is therefore not another general CST startup test; it is a local
H-field probe handoff that can pair with the already exported local E-field
data and support E/H equivalent-current validation.

This stage keeps the CST diagnosis clear:

1. CST is runnable on the mesh-safe route.
2. The earlier popup came from CST Field Monitors 3D ASCII export, which is the
   wrong handoff path for these local probe curves.
3. The current blocker is missing solved H-field probe evidence, not CST
   inability to open, solve, or expose E-field ResultTree curves.

## Main Artifacts

| Path | Meaning |
|---|---|
| `code/export_cst_meshsafe_huygens_results.py` | Field-aware ResultTree audit/export controller. |
| `code/run_cst_level1_required_automation.py` | CST project generator now accepts `--probe-mode hfield`. |
| `code/prepare_cst_meshsafe_huygens_workpack.py` | Workpack generator now writes E/H export contracts and command queue. |
| `data/cst_meshsafe_huygens_workpack/local_huygens_export_contract.csv` | Local E-field export contract. |
| `data/cst_meshsafe_huygens_workpack/local_huygens_hfield_export_contract.csv` | Local H-field export contract. |
| `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv` | Seven-step executable queue, including H-field steps 5-7. |
| `data/cst_meshsafe_huygens_workpack/README.md` | Human-readable CST/algorithm handoff note. |

## Validation

```powershell
python -m py_compile code\export_cst_meshsafe_huygens_results.py code\prepare_cst_meshsafe_huygens_workpack.py code\run_cst_level1_required_automation.py
python code\prepare_cst_meshsafe_huygens_workpack.py
python code\export_cst_meshsafe_huygens_results.py
python code\export_cst_meshsafe_huygens_results.py --field-kind h
```

Current result:

- E-field default export reports `target_contract_complete` with `288` rows.
- H-field default export reports `blocked` because
  `C:\csttmp\huy_hs\h_short_hfield.cst` does not exist yet.
- That H-field `blocked` status is expected until steps 5-7 in
  `next_meshsafe_huygens_commands.csv` are run.

## Next Step

1. Run the H-field project-generation command from
   `next_meshsafe_huygens_commands.csv`.
2. Solve the H-field short-path project as `C:\csttmp\huy_hs\h_short_hfield.cst`.
3. Run
   `python code\export_cst_meshsafe_huygens_results.py --field-kind h --attempt-export --project C:\csttmp\huy_hs\h_short_hfield.cst`.
4. After `*_local_hfield.csv` exists, replace the scalar impedance proxy with
   E/H-backed equivalent-current validation in the Python Huygens gate.
