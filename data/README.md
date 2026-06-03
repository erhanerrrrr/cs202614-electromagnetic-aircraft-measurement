# data 目录说明

本目录存放真实或主线 CST 导出数据，以及适合进入 GitHub 的小型算法输入表和诊断结果。大体量 CST 导出 CSV 默认由 `.gitignore` 排除，仓库中保留可复现脚本、索引、摘要和小型结果表。

## 子目录

| 子目录 | 说明 |
|---|---|
| `cst_exports/level1/` | Level 1 标准源 nearfield/farfield CSV、合并结果和 dropzone 说明。真实大 CSV 本地保留，默认不进入普通 Git。 |
| `cst_exports/level2/` | Level 2 多源、多状态样本 nearfield/farfield CSV、合并结果和 dropzone 说明。 |
| `cst_true_nearfield_workpack/` | CST 真近场 monitor 导出工作包、162 点采样壳层、reduced-layout 复跑队列、宏骨架、对照清单、reference self-check 和 gate status report。 |
| `sampling_layouts/` | 162/120/81/48/32 点半球采样候选表、代理指标和当前 CST Level 1 诊断结果。 |
| `source_priors/` | Huygens 面源等结构化反演先验的节点表、未知量合同和 README。 |
| `recognition_stress_tests/` | Level 2 识别鲁棒性小型结果表，覆盖 G2 代表布局的 clean-train/perturbed-test、增强训练、未见误差族、种子稳定性、缺测缓解和结构化缺测对照。 |

## 主要生成物

| 路径 | 生成命令 | 作用 |
|---|---|---|
| `sampling_layouts/hemisphere_sampling_candidates.csv` | `python code\optimize_sampling_layout.py` | 候选测点布局。 |
| `sampling_layouts/sampling_layout_summary.csv` | `python code\optimize_sampling_layout.py` | 候选布局代理指标摘要。 |
| `sampling_layouts/cst_level1_tradeoff/` | `python code\run_cst_sampling_tradeoff.py` | 通用等效源网格下的 CST Level 1 采样诊断。 |
| `sampling_layouts/cst_level1_center_source_check/` | `python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check` | 已知中心源先验下的数据路径 sanity check。 |
| `sampling_layouts/cst_level1_source_model_sweep/` | `python code\run_cst_source_model_sweep.py` | 等效源支撑和 Tikhonov 正则化扫描。 |
| `sampling_layouts/cst_level1_sparse_calibration/` | `python code\run_cst_sparse_reconstruction.py` | group-sparse 等效源校准结果。 |
| `sampling_layouts/cst_level1_convention_check/` | `python code\run_cst_level1_convention_check.py` | 相位、复共轭和极化约定诊断。 |
| `cst_true_nearfield_workpack/` | `python code\prepare_cst_true_nearfield_workpack.py` | 真近场 monitor 导出任务包、三档布局复跑队列和 FarfieldPlot-derived 基线对照入口。 |
| `cst_true_nearfield_workpack/reference_self_check/` | `python code\compare_true_nearfield_exports.py --true-nearfield data\cst_exports\level1\all_nearfield.csv --reference-nearfield data\cst_exports\level1\all_nearfield.csv --out-dir data\cst_true_nearfield_workpack\reference_self_check` | 对照脚本自检结果，不是新增 CST 物理证据。 |
| `cst_true_nearfield_workpack/gate_report/` | `python code\run_true_nearfield_gate.py` | 当前 true-monitor 队列状态、可用源文件、派生状态、行数检查和参考比较汇总。 |
| `source_priors/huygens_surface/` | `python code\prepare_huygens_surface_prior.py` | Huygens 面源节点、法向/切向基、面积权重和四复未知量合同。 |
| `sampling_layouts/cst_level1_huygens_baseline/` | `python code\run_cst_huygens_baseline.py` | First Huygens-style surface-source reconstruction baseline, including `radiating_dipole` and `current_green` field-model diagnostics; current result is diagnostic only. |
| `recognition_stress_tests/level2_robustness/` | `python code\run_cst_recognition_stress_test.py` | G5 clean-train/perturbed-test recognition robustness summary for selected G2 layouts. |
| `recognition_stress_tests/level2_augmented_robustness/` | `python code\run_cst_recognition_augmented_stress_test.py` | G5 perturbation-aware training follow-up on the same selected G2 layouts and held-out stress cases. |
| `recognition_stress_tests/level2_leave_one_family_out/` | `python code\run_cst_recognition_leave_one_family_out.py` | G5 leave-one-stress-family-out check for unseen noise/phase/dropout/combined error-family generalization. |
| `recognition_stress_tests/level2_seed_stability/` | `python code\run_cst_recognition_seed_stability.py` | G5 repeated-seed stability summary for focused leave-one-family noise/dropout checks. |
| `recognition_stress_tests/level2_dropout_mitigation/` | `python code\run_cst_recognition_dropout_mitigation.py` | G5 focused missing-channel mitigation comparison for the tightest held-out dropout layouts. |
| `recognition_stress_tests/level2_dropout_mitigation_extended/` | `python code\run_cst_recognition_dropout_mitigation.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --held-out-families dropout,combined --out-dir data\recognition_stress_tests\level2_dropout_mitigation_extended` | G5 extended missing-channel mitigation comparison across all five G2 representative layouts and dropout-bearing stress families. |
| `recognition_stress_tests/level2_structured_dropout/` | `python code\run_cst_recognition_structured_dropout.py` | G5 structured missing-channel check for unseen sensor-node, polarization-pair, and azimuth-sector dropout patterns. |

## 使用约定

- 真实 CST 导出优先放在 `data/cst_exports/`，不要混入临时仿真缓存。
- 合成数据和大体量中间结果优先由脚本生成到 `outputs/`。
- 可协作的小型 CSV/JSON/README 摘要放入 `data/sampling_layouts/` 并进入 Git。
- 结构化源先验放入 `data/source_priors/`；它定义反演模型允许的源支撑，不等同于采样布局或最终重建结果。
- 识别鲁棒性小型摘要放入 `data/recognition_stress_tests/`；它证明或暴露分类泛化边界，不等同于 full-wave 复杂载体结构验证。
- CST 真近场 monitor 当前先提交工作包和对照自检；真实 monitor 大 CSV 后续仍按 `data/cst_exports/` 大文件策略处理。
- 如后续需要长期共享大 CST 文件，建议启用 Git LFS、GitHub Release 或网盘；仓库中只保留索引、校验摘要和复现命令。

## Huygens baseline note

`sampling_layouts/cst_level1_huygens_baseline/` is generated from the local
Level 1 CST export and the `source_priors/huygens_surface/` geometry contract.
It records a runnable electric/magnetic dipole-sheet approximation, a fuller
`current_green` near-field diagnostic branch, and a surface smoothness sweep
(`smooth_lambda = 0`, `1e-6`, `1e-4`, `1e-2`). The best setting is still
`diagnostic_only` (`field_model = radiating_dipole`, `min_corr ~= 0.778`,
`max_nmse ~= 0.264`, best `smooth_lambda = 0`). The `current_green` rows stay
very close to the compact model, and a small smoothness penalty slightly lowers
NMSE/jump but does not pass the physics gate. Keep it as model-calibration
evidence, not as reduced-sampling validation.

## Spherical reduced-layout note

`sampling_layouts/spherical_nf_ff_tradeoff/` is generated by
`python code\run_spherical_nf_ff_tradeoff.py`. It extends the scalar
spherical-harmonic NF-FF sanity baseline from the full 162-point grid to every
candidate layout in `sampling_layouts/hemisphere_sampling_candidates.csv`.

Current diagnostic result: `geometric_farthest_32` is the smallest reduced
candidate with `strict_pass` (`lmax = 4`, `lambda = 1e-10`, max NMSE about
`9.77e-04`). Use it to prioritize true CST near-field monitor reruns; do not
treat it as final vector SWE or Huygens validation.

`cst_true_nearfield_workpack/true_nearfield_priority_layout_queue.csv` now
promotes this into a CST execution queue together with `full_grid_162` and the
conservative `fibonacci_snap_120` cross-check layout.

After a full 162-point true-monitor CSV is available,
`python code\derive_true_nearfield_layout_exports.py --sample-id <sample-id>`
derives the queued 32/120 reduced-layout CSVs from the subset table.

Run `python code\run_true_nearfield_gate.py` after export or derivation to
refresh `cst_true_nearfield_workpack/gate_report/`. The current committed gate
report records all 18 queued layout rows as `pending_source`, which is the
correct status until true CST near-field monitor CSVs are added locally.

## Recognition stress-test note

`recognition_stress_tests/level2_robustness/` is generated by
`python code\run_cst_recognition_stress_test.py`. It trains on clean Level 2
CST-derived samples and tests the same held-out split under noise, phase
jitter, channel dropout, and combined perturbations for the G2 representative
layouts.

Current result: clean, single-noise, single-phase, and 10 percent dropout cases
stay at accuracy `1.000`, but combined `10 dB noise + 15 deg phase jitter + 10
percent dropout` falls below the `0.85` threshold for all tested layouts. This
is useful G5 boundary evidence: recognition remains strong for single-factor
disturbances, but compound measurement errors need calibration, augmentation,
or error-aware features before report-level robustness claims.

`recognition_stress_tests/level2_augmented_robustness/` is generated by
`python code\run_cst_recognition_augmented_stress_test.py`. It keeps the same
held-out split and stress cases, expands only the training set with the known
clean/noise/phase/dropout/combined perturbation families, and compares back to
the clean-train baseline. Current result: all 40 layout/stress rows pass the
`0.85` threshold with accuracy `1.000`. This is useful calibration evidence,
but the boundary remains Level 2 CST-derived data and known perturbation
families, not unknown full-wave airframe scattering.

`recognition_stress_tests/level2_leave_one_family_out/` is generated by
`python code\run_cst_recognition_leave_one_family_out.py`. It withholds one
stress family from augmentation, trains on clean plus the remaining families,
and evaluates the unseen family on the same held-out split. Current result: all
35 rows pass `0.85`; the tightest rows are held-out `dropout_25pct` for
`geometric_farthest_32` and `task_driven_48`, both about `0.867`. This gives a
more conservative G5 margin than full augmentation and flags missing-channel
errors as the next calibration target.

`recognition_stress_tests/level2_seed_stability/` is generated by
`python code\run_cst_recognition_seed_stability.py`. It repeats the focused
leave-one-family check for held-out `noise` and `dropout` across seeds
`202614`, `202615`, and `202616`, varying the split and stochastic perturbation
draws. Current result: all 60 rows pass `0.85`; the tightest case remains
`geometric_farthest_32/dropout/dropout_25pct` with mean accuracy about `0.933`
and minimum accuracy about `0.867`. This turns the dropout margin from a
single-run observation into a small seed-stability result.

`recognition_stress_tests/level2_dropout_mitigation/` is generated by
`python code\run_cst_recognition_dropout_mitigation.py`. It keeps the
leave-one-family dropout protocol and compares zero-fill, missing-mask
features, frequency/sensor median imputation, and imputation plus mask
features for `geometric_farthest_32` and `task_driven_48`. Current result: all
48 rows pass `0.85`; mask features alone do not improve zero-fill, while
frequency/sensor median imputation raises the tightest
`geometric_farthest_32/dropout_25pct` aggregate from mean accuracy about
`0.956` and minimum `0.867` to mean/min `1.000`. This is a candidate
missing-channel preprocessing step, still bounded to internal stochastic
dropout evidence.

`recognition_stress_tests/level2_dropout_mitigation_extended/` is generated by
the same runner with explicit layout and family arguments. It extends the
comparison to `full_grid_162`, `geometric_farthest_32`, `fibonacci_snap_120`,
`task_driven_32`, and `task_driven_48`, and tests both held-out `dropout` and
`combined` families. Current result: all 180 rows pass `0.85`; zero-fill has
minimum accuracy `0.867`; mask-only also bottoms at `0.867` and can weaken one
`full_grid_162/dropout_25pct` aggregate relative to zero-fill; frequency/sensor
median imputation and imputation plus mask both reach mean/min accuracy
`1.000`. This makes imputation-only the cleaner current preprocessing
candidate, while preserving zero-fill as the conservative baseline.

`recognition_stress_tests/level2_structured_dropout/` is generated by
`python code\run_cst_recognition_structured_dropout.py`. It trains with the
known perturbation augmentation profiles and tests unseen structured missing
patterns: sensor-node dropout, polarization-pair dropout, and contiguous
azimuth-sector dropout. Current result: all 240 rows pass `0.85`; the worst
single row is `0.933`; both frequency/sensor median imputation variants reach
mean/min accuracy `1.000`. This strengthens the missing-channel preprocessing
choice but remains internal simulated dropout evidence.
