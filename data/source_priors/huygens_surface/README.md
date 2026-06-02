# Huygens Surface Source Priors

This directory stores candidate Huygens-surface node sets for the next G3
source-prior upgrade. These files define geometry and unknown-vector contracts;
they are not yet final reconstruction results.

## Generated Files

| Prior | Surface | Nodes | Complex unknowns | File |
|---|---|---:|---:|---|
| `level1_local_sphere_r0p35` | `sphere` | 96 | 384 | `level1_local_sphere_r0p35_nodes.csv` |
| `airframe_box_coarse` | `box` | 414 | 1656 | `airframe_box_coarse_nodes.csv` |
| `airframe_box_medium` | `box` | 718 | 2872 | `airframe_box_medium_nodes.csv` |

`huygens_surface_configs.csv` stores the parameters used to generate the node
sets. `huygens_surface_prior_summary.json` stores the same information in a
script-friendly summary.

## Unknown Contract

Each node has four complex tangential current unknowns:

```text
q_i = [J_t1, J_t2, M_t1, M_t2]
```

`J` is the equivalent electric surface current and `M` is the equivalent
magnetic surface current. `tangent1` and `tangent2` are local unit vectors
orthogonal to the outward normal. The future Huygens measurement matrix should
map these unknowns to the same measured vector already used by the CST scripts:

```text
y = [Etheta(sensor_1..N), Ephi(sensor_1..N)]
```

## Current Role

- `level1_local_sphere_r0p35` is the first Level 1 diagnostic prior around the
  known source center at `(0, 0, 4 m)`.
- `airframe_box_coarse` and `airframe_box_medium` are geometry contracts for
  later Level 2/Level 3 structure-aware reconstruction.
- Use these priors only after the CST true near-field monitor gate is checked,
  or state clearly that the input is still FarfieldPlot-derived angular data.
- The first runnable matrix baseline is now in
  `data/sampling_layouts/cst_level1_huygens_baseline/`; it is diagnostic only
  on the current Level 1 export.

## Generation Command

```powershell
python code\prepare_huygens_surface_prior.py
```

## Baseline Command

```powershell
python code\run_cst_huygens_baseline.py
```
