# G3 Source-Model Calibration Plan

This note turns the broad G3 goal in `docs/future_engineering_plan.md` into the
next engineering steps that can be assigned inside the GitHub repository.

## Current Diagnosis

The current CST Level 1 data path is credible under the known center-source
prior: `data/sampling_layouts/cst_level1_center_source_check/` reaches high
correlation and zero main-lobe error on the current two standard-source cases.

The generic equivalent-source grid is not yet calibrated:
`data/sampling_layouts/cst_level1_tradeoff/` shows that full 162-point
reconstruction drops to about `Corr = 0.806`, `NMSE = 0.309`. Lower-count
sampling claims must wait until the full-grid baseline is stable.

## New Reproducible Check

Run:

```powershell
python code\run_cst_source_model_sweep.py
```

The script writes `data/sampling_layouts/cst_level1_source_model_sweep/` with:

- `cst_source_model_sweep_results.csv`
- `cst_source_model_sweep_by_model.csv`
- `cst_source_model_sweep_summary.json`
- `README.md`

The sweep currently varies equivalent-source support and Tikhonov
regularization while keeping the candidate layout fixed to `full_grid_162`.
This is deliberate: first make the full measurement baseline credible, then
evaluate compressed layouts.

## Current Sweep Result

The current sweep selected `single_center` as the best Level 1 model:

| Metric | Value |
|---|---:|
| Status | `corr_pass_nmse_near` |
| Min correlation | `0.9926` |
| Max NMSE | `1.7784e-02` |
| Max main-lobe error / deg | `0.00` |

The default 5 x 3 x 3 grid, compact cube, z-line, xy-plane, and wider cube all
remain `diagnostic_only` on the full-grid baseline. This means the next
algorithm step should not be "add more unconstrained equivalent-source points".
It should focus on source priors, phase/amplitude convention checks, and sparse
or structure-aware regularization.

## Decision Rule

Use this sequence for the next round:

1. If a scanned model reaches `strict_pass`, freeze it as the Level 1
   reconstruction baseline and rerun `run_cst_sampling_tradeoff.py`.
2. If the best model reaches `corr_pass_nmse_near`, investigate NMSE through
   phase/reference convention, amplitude normalization, and regularization.
3. If only `diagnostic_only` models remain, expand the model family before
   making sampling claims.

## Next Algorithm Upgrades

| Upgrade | Purpose | Suggested artifact |
|---|---|---|
| Sparse / ElasticNet equivalent sources | Reduce over-free source grids and suppress nonphysical energy leakage. | `code/run_cst_sparse_reconstruction.py` |
| Phase / polarization convention check | Test whether phase sign, complex conjugation, or theta/phi labeling explains the Level 1 bottleneck. | `code/run_cst_level1_convention_check.py` |
| True near-field monitor workpack | Separate real CST near-field monitor evidence from the current FarfieldPlot-derived angular baseline. | `code/prepare_cst_true_nearfield_workpack.py` |
| Group sparsity across frequencies | Share source support for multi-frequency samples. | `outputs/model_comparison/reconstruction_metrics.csv` |
| Huygens-surface source prior | Move from point-source grids toward structure-aware equivalent currents. | `docs/huygens_surface_model_note.md`, `code/prepare_huygens_surface_prior.py` |
| Spherical NF-FF sanity check | Detect coordinate, phase, and polarization convention errors independently of equivalent sources. | `code/run_spherical_nf_ff_baseline.py` |
| Spherical reduced-layout tradeoff | Rank 162/120/81/48/32 candidate layouts under the scalar angular NF-FF diagnostic before true-monitor reruns. | `code/run_spherical_nf_ff_tradeoff.py` |

## Report Wording

Use cautious wording for now:

- The project has a reproducible CST/Python calibration chain.
- Level 1 center-source results validate the data path.
- Generic source-model calibration is the current bottleneck.
- Non-redundant 120/81/48/32 point layouts are candidate plans, not final CST
  evidence, until the full 162-point baseline passes under the chosen model.

## Sparse Calibration Entry Point

Run:

```powershell
python code\run_cst_sparse_reconstruction.py
```

This writes `data/sampling_layouts/cst_level1_sparse_calibration/`. The sparse
solver uses a group penalty over each source point's three complex dipole
moments, so it directly tests whether the generic grid can collapse back toward
a small number of physical source locations instead of spreading energy across
the volume.

The current sparse run is diagnostic rather than a pass. The best setting is
`default_cube_5x3x3` with group sparsity at `group_alpha_frac = 0.3`: min
correlation improves to about `0.928`, max NMSE improves to about `0.081`, and
the mean active source count drops to `2`. However, the max main-lobe error is
still about `153 deg` and center energy share is `0`, so sparsity alone is not
enough. The next step should be phase/amplitude convention checks and a more
physical source prior, not just stronger L1 regularization.

## Convention Check Entry Point

Run:

```powershell
python code\run_cst_level1_convention_check.py
```

This writes `data/sampling_layouts/cst_level1_convention_check/`. The script
crosses the current near/far propagation phase signs with a reciprocal time-sign
flip, then tests direct samples, complex conjugation, phi sign flip, and
theta/phi channel swap.

The current result is a diagnostic rather than a fix. The center-source prior
still reaches `corr_pass_nmse_near`, and several sign-equivalent settings tie
in far-field power metrics. For the generic `default_cube_5x3x3` grid, however,
the best convention still stays near `Corr = 0.794` and `NMSE = 0.318`; it does
not become a valid reduced-sampling baseline. This argues against a simple
global phase-sign or polarization-label error. The next real model upgrade is a
more physical source prior: Huygens surface, spherical-wave sanity baseline, or
known-source/structure-aware constraints.

## True Near-Field Monitor Gate

Run:

```powershell
python code\prepare_cst_true_nearfield_workpack.py
```

This writes `data/cst_true_nearfield_workpack/`, including the 162-point
spherical shell, CST monitor export contract, macro skeleton, and comparison
checklist. The paired comparison script is:

```powershell
python code\compare_true_nearfield_exports.py --true-nearfield <true-monitor-csv> --reference-nearfield <farfieldplot-derived-csv> --out-dir data\cst_true_nearfield_workpack\comparison\<sample-id>
```

This is now the immediate data-boundary gate before SWE/Huygens work. If true
monitor exports differ materially from the FarfieldPlot-derived baseline, rerun
the Level 1 source-model, sparse, convention, and sampling diagnostics on the
true-monitor table before making any reduced-sampling claim.

## Huygens Surface Prior Workpack

Run:

```powershell
python code\prepare_huygens_surface_prior.py
```

This writes `data/source_priors/huygens_surface/`. The workpack contains
surface nodes, outward normals, local tangential bases, area weights, and the
four-complex-unknown contract `J_t1,J_t2,M_t1,M_t2` for each node. The detailed
model note is `docs/huygens_surface_model_note.md`.

This is a geometry and interface contract, not a completed Huygens
reconstruction result. The next coding step is to implement a Huygens
measurement matrix with shape `2 * sensor_count` by `4 * surface_node_count`,
then compare its full-grid Level 1 metrics against the center-source, generic
grid, group-sparse, convention, and spherical baselines.

## Huygens Baseline Entry Point

Run:

```powershell
python code\run_cst_huygens_baseline.py
```

This writes `data/sampling_layouts/cst_level1_huygens_baseline/`. The script
uses the `level1_local_sphere_r0p35` surface prior and tests three first-order
variants: `electric_sheet_only`, `huygens_em_plus`, and `huygens_em_minus`.
The electric/magnetic versions are a compact dipole-sheet approximation, not a
full Stratton-Chu/Huygens surface-integral implementation.

The current result is diagnostic only. The best setting is
`huygens_em_minus`, `lambda = 1e-2`, with min correlation about `0.778`, max
NMSE about `0.264`, mean near-field residual about `0.619`, and a large
main-lobe error. This confirms that the surface-prior workflow is runnable, but
the simplified Green-function and current-normalization model is not yet good
enough to replace the center-source or spherical NF-FF sanity baselines.

Next action: keep the Huygens outputs as model-calibration evidence, then rerun
the same script on true near-field monitor data and/or upgrade the Huygens
operator to a fuller electric/magnetic surface-current Green function with
surface smoothness regularization.

## Spherical NF-FF Sanity Baseline

Run:

```powershell
python code\run_spherical_nf_ff_baseline.py
```

This writes `data/sampling_layouts/spherical_nf_ff_baseline/`. The current
implementation is intentionally lightweight: it fits `Etheta` and `Ephi` with
independent scalar spherical-harmonic expansions and compares the predicted
angular power against the CST far-field table. It is not a full vector SWE
implementation.

The stable best setting is `lmax = 4`, `lambda = 0`, with 24 modes per
component. On the two current Level 1 z-dipole cases it reaches `strict_pass`:
min correlation `0.9990`, max NMSE `9.2604e-04`, zero main-lobe error, and max
near-field fit relative error about `2.58e-02`. This strengthens the data-path
argument: the angular, polarization, and far-field comparison conventions are
internally consistent. It does not remove the need for true near-field monitor
exports or a more physical Huygens/source-prior model.

## Spherical NF-FF Reduced-Layout Tradeoff

Run:

```powershell
python code\run_spherical_nf_ff_tradeoff.py
```

This writes `data/sampling_layouts/spherical_nf_ff_tradeoff/`. It applies the
same scalar spherical-harmonic NF-FF diagnostic to every candidate layout in
`data/sampling_layouts/hemisphere_sampling_candidates.csv` and stores both raw
case results and one best setting per candidate.

Current result: `geometric_farthest_32` is the smallest reduced candidate with
`strict_pass` under this check (`lmax = 4`, `lambda = 1e-10`, min correlation
about `0.9991`, max NMSE about `9.77e-04`, zero main-lobe error, max near-field
fit relative error about `1.49e-02`). This is a good next CST true-monitor
priority, especially alongside one conservative 120-point layout and the full
162-point reference.

The true-monitor workpack has now encoded that rerun order in
`data/cst_true_nearfield_workpack/true_nearfield_priority_layout_queue.csv`:
`full_grid_162` first, then `geometric_farthest_32`, then the conservative
`fibonacci_snap_120` cross-check. Use
`true_nearfield_priority_sensor_subsets.csv` to derive reduced-layout exports
from the full 162-point monitor table when possible.

The derivation step is now scripted by
`code/derive_true_nearfield_layout_exports.py`, so a CST operator can export the
full 162-point true-monitor shell first and the algorithm operator can derive
the queued 32/120 CSVs without reopening CST.

Boundary: the result is still based on FarfieldPlot-derived angular samples and
a scalar, not full vector, SWE approximation. It should not be written as final
reduced-sampling proof until the true near-field monitor and physical Huygens
or vector SWE baseline agree.
