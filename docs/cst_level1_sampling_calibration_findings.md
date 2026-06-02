# CST Level 1 Sampling Calibration Findings

This note records the current CST-based sampling diagnostics so the team can
use the GitHub repository without over-reading the evidence.

## What Was Added

`code/run_cst_sampling_tradeoff.py` benchmarks the sampling-layout candidates
from `data/sampling_layouts/hemisphere_sampling_candidates.csv` against the
current Level 1 CST near-field and far-field exports:

- `data/cst_exports/level1/all_nearfield.csv`
- `data/cst_exports/level1/all_farfield.csv`

It writes compact CSV/JSON/README outputs for candidate comparison.

## Evidence Directories

| Directory | Source model | Current role |
|---|---|---|
| `data/sampling_layouts/cst_level1_tradeoff/` | 5 x 3 x 3 equivalent-source grid around `(0, 0, 4 m)` | Calibration diagnostic. Full 162-point reconstruction is not yet strong enough, so this cannot support final sampling claims. |
| `data/sampling_layouts/cst_level1_center_source_check/` | Single equivalent source at `(0, 0, 4 m)` | Level 1 sanity check. Correlation and main-lobe location are good, showing the CST export and comparison chain are broadly consistent. |
| `data/sampling_layouts/cst_level1_source_model_sweep/` | Multiple Level 1 source supports and Tikhonov regularization values | Full-grid model-calibration sweep. Use it to choose the next baseline before judging lower-count layouts. |

## Current Reading

The generic 5 x 3 x 3 equivalent-source grid gives only about `Corr = 0.806`
and `NMSE = 0.309` for the full 162-point baseline. That means the inverse
model is not calibrated enough for final sampling conclusions.

The center-source Level 1 check gives a much stronger baseline: full-grid mean
correlation is about `0.996`, with zero main-lobe error on the current two
standard-source cases. Several 120-point and 81-point layouts remain near the
full-grid correlation under this source prior. The half-wave case still has
worst-case NMSE above `1e-2`, so this is not a final acceptance proof yet.

`code/run_cst_source_model_sweep.py` now makes this diagnosis reproducible by
scanning several Level 1 source supports and regularization values on the
full-grid baseline. The current rule is simple: calibrate the full 162-point
model first, then use the same model to compare reduced sampling layouts.

The current sweep selects `single_center` as the best model with
`corr_pass_nmse_near`: min correlation `0.9926`, max NMSE `1.7784e-02`, and
zero main-lobe error. The generic multi-point source grids remain diagnostic
only, so they should not be used as final reduced-sampling evidence yet.

`code/run_cst_sparse_reconstruction.py` adds a group-sparse check on the generic
Level 1 grids. It improves the default-grid diagnostic from roughly
`Corr = 0.794`, `NMSE = 0.318` to `Corr = 0.928`, `NMSE = 0.081`, while reducing
the active source count to about `2`. The main-lobe error remains large, so the
result confirms that sparsity helps but does not replace source-prior and
phase/amplitude calibration.

## Engineering Implication

Do not claim that the 120-point or 81-point CST sampling plan is final. The
repo now supports a clearer next step:

1. Lock down the Level 1 source prior and phase convention.
2. Calibrate the equivalent-source grid, regularization, and source sparsity.
3. Re-run the same tradeoff script after the full 162-point baseline meets the
   chosen acceptance metric.
4. Only then use the lower-count layouts as report-level evidence.

This is still useful GitHub material because it gives teammates a reproducible
script, compact result tables, and a precise diagnosis of what remains open.
