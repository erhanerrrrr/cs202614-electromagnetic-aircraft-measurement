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

## Current Reading

The generic 5 x 3 x 3 equivalent-source grid gives only about `Corr = 0.806`
and `NMSE = 0.309` for the full 162-point baseline. That means the inverse
model is not calibrated enough for final sampling conclusions.

The center-source Level 1 check gives a much stronger baseline: full-grid mean
correlation is about `0.996`, with zero main-lobe error on the current two
standard-source cases. Several 120-point and 81-point layouts remain near the
full-grid correlation under this source prior. The half-wave case still has
worst-case NMSE above `1e-2`, so this is not a final acceptance proof yet.

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
