# Sampling Decision Matrix

This directory stores the G2 decision surface for reduced sampling layouts.
It combines the geometry/proxy summary, scalar spherical NF-FF reduced-layout
diagnostics, and the true-monitor rerun queue.

## Current Decision

- `full_grid_162` remains the physical reference anchor.
- `geometric_farthest_32` is the first reduced-layout true-monitor rerun
  priority because it is the smallest scalar SWE `strict_pass` candidate.
- `fibonacci_snap_120` remains the conservative 120-point cross-check.
- `task_driven_48` and `task_driven_32` are classification-focused probes, not
  report-level proof.

## Top Rows

| Candidate | Sensors | Recommendation | Evidence role | Reconstruction score | Classification score | SWE status | Claim boundary |
|---|---:|---|---|---:|---:|---|---|
| full_grid_162 | 162 | reference_anchor | physical_reference | 0.9577 | 0.6092 | strict_pass | reference only; reduced-layout proof still requires physical/vector baseline |
| geometric_farthest_32 | 32 | reconstruction_priority | queued_true_monitor_rerun | 0.9540 | 0.7579 | strict_pass | rerun priority; not final vector SWE/Huygens proof |
| fibonacci_snap_120 | 120 | conservative_cross_check | queued_true_monitor_rerun | 0.9558 | 0.6749 | strict_pass | rerun priority; not final vector SWE/Huygens proof |
| task_driven_32 | 32 | classification_probe | classification_priority_not_final_proof | 0.3762 | 0.7677 | diagnostic_only | classification probe; needs reduced-layout recognition validation |
| task_driven_48 | 48 | classification_probe | classification_priority_not_final_proof | 0.2684 | 0.7705 | diagnostic_only | classification probe; needs reduced-layout recognition validation |
| dictionary_weighted_32 | 32 | alternate_reconstruction_candidate | swe_strict_not_queued | 0.9525 | 0.7808 | strict_pass | scalar SWE diagnostic; backup priority only |
| geometric_farthest_48 | 48 | alternate_reconstruction_candidate | swe_strict_not_queued | 0.9563 | 0.7463 | strict_pass | scalar SWE diagnostic; backup priority only |
| dictionary_weighted_48 | 48 | alternate_reconstruction_candidate | swe_strict_not_queued | 0.9516 | 0.7704 | strict_pass | scalar SWE diagnostic; backup priority only |
| task_driven_81 | 81 | secondary_reconstruction_candidate | swe_strict_not_queued | 0.9564 | 0.7445 | strict_pass | scalar SWE diagnostic; backup priority only |
| geometric_farthest_81 | 81 | secondary_reconstruction_candidate | swe_strict_not_queued | 0.9562 | 0.7255 | strict_pass | scalar SWE diagnostic; backup priority only |
| fibonacci_snap_81 | 81 | secondary_reconstruction_candidate | swe_strict_not_queued | 0.9537 | 0.7181 | strict_pass | scalar SWE diagnostic; backup priority only |
| dictionary_weighted_81 | 81 | secondary_reconstruction_candidate | swe_strict_not_queued | 0.9506 | 0.7349 | strict_pass | scalar SWE diagnostic; backup priority only |

## Files

| File | Purpose |
|---|---|
| `sampling_decision_matrix.csv` | One row per layout candidate with scores, queue role, recommendation, and claim boundary. |
| `sampling_decision_summary.json` | Machine-readable summary and input references. |
| `README.md` | Human-facing decision note. |

## Regenerate

```powershell
python code\build_sampling_decision_matrix.py
```

## Boundary

This matrix is a planning and collaboration artifact. It does not replace the
true CST near-field monitor gate. Reduced-layout claims remain blocked until a
full-grid physical/vector baseline passes on authoritative monitor data.

## Inputs

- Layout proxy summary: `data\sampling_layouts\sampling_layout_summary.csv`
- Scalar SWE reduced-layout table: `data\sampling_layouts\spherical_nf_ff_tradeoff\spherical_nf_ff_tradeoff_best_by_candidate.csv`
- True-monitor queue: `data\cst_true_nearfield_workpack\true_nearfield_priority_layout_queue.csv`
- Recognition ablation context: `outputs\cst_recognition_level2_ablation\recognition_ablation_summary.json`
