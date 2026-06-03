# code 目录说明

本目录存放项目可运行源代码、CST/Python 接口脚本、数据处理脚本、算法实验脚本和报告生成脚本。建议在项目根目录执行命令。

## 核心算法与数据接口

| 文件 | 作用 |
|---|---|
| `em_core.py` | 半球测点、球坐标基、等效源传播矩阵、Tikhonov 反演、远场外推与指标函数。 |
| `cst_io.py` | CST near/far-field CSV 读取、字段校验、Ex/Ey/Ez 到 theta/phi 投影、样本频点配对。 |
| `check_cst_export.py` | 检查 CST 导出表是否满足 Python 重建链路要求。 |
| `normalize_cst_complex_columns.py` | 统一 CST 复数字段命名与格式。 |

## 采样与反演实验

| 文件 | 作用 |
|---|---|
| `optimize_sampling_layout.py` | 生成 162/120/81/48/32 点半球非冗余采样候选，并输出几何、矩阵、重建和分类代理指标。 |
| `run_cst_sampling_tradeoff.py` | 用当前 CST Level 1 near/far-field 导出评估候选采样布局。 |
| `run_cst_source_model_sweep.py` | 扫描 Level 1 等效源支撑和 Tikhonov 正则化，定位源模型校准瓶颈。 |
| `run_cst_sparse_reconstruction.py` | 用 group-sparse FISTA/ElasticNet 思路检查通用等效源网格的能量泄漏问题。 |
| `run_cst_level1_convention_check.py` | 诊断相位符号、复共轭、theta/phi 极化约定是否造成 Level 1 反演瓶颈。 |
| `compare_true_nearfield_exports.py` | 对比 CST 真近场 monitor 导出与当前 FarfieldPlot-derived nearfield 基线。 |
| `derive_true_nearfield_layout_exports.py` | 从 162 点 CST 真近场 monitor 导出自动派生 queued 32/120 reduced-layout CSV。 |
| `run_true_nearfield_gate.py` | Runs the true-monitor queue gate: source availability, optional 32/120 derivation, row-count checks, and FarfieldPlot-derived reference comparison. |
| `run_true_nearfield_workflow_decision.py` | Reads the true-monitor handoff, dropzone preflight, gate report, and G3 dashboard, then writes the next executable decision for CST export, gate rerun, physical G3 rerun, or report refresh. |
| `run_spherical_nf_ff_baseline.py` | 用切向球谐拟合建立轻量 NF-FF/SWE sanity baseline，独立检查角度、极化和远场比较链路。 |
| `build_sampling_decision_matrix.py` | 汇总采样代理指标、球谐 NF-FF 少测点结果、真近场复跑队列和识别消融上下文，输出 G2 采样决策矩阵。 |
| `prepare_huygens_surface_prior.py` | 生成 Huygens 面源先验节点、法向/切向基和四复未知量合同，供后续物理面源反演使用。 |
| `run_cst_huygens_baseline.py` | 用 Huygens-style 电/磁面源近似构造 Level 1 full-grid 诊断矩阵，并对比 `radiating_dipole` 与 `current_green` 两类 field model。 |
| `run_cst_reconstruction.py` | CST 数据等效源反演与远场外推入口。 |
| `run_reconstruction_robustness.py` | 重建鲁棒性实验。 |

## CST 工作流脚本

| 文件 | 作用 |
|---|---|
| `prepare_cst_templates.py`、`prepare_cst_macro_templates.py` | 生成 CST 建模和导出宏模板。 |
| `prepare_cst_level1_workpack.py`、`prepare_cst_level2_workpack.py` | 生成 Level 1/2 CST 执行任务包。 |
| `prepare_cst_true_nearfield_workpack.py` | 生成 CST 真近场 monitor 导出工作包、采样壳层、三档布局复跑队列、宏骨架和对照清单。 |
| `prepare_cst_true_nearfield_operator_packet.py` | 从真近场 workpack 和 gate 状态生成 required full-grid CST 任务卡、manifest、验收命令和 operator packet summary。 |
| `build_true_nearfield_handoff.py` | 将真近场 monitor 队列、gate 状态和 CSV 合同汇总成 CST 操作者 action sheet。 |
| `check_true_nearfield_dropzone.py` | 预检 CST 真近场 monitor dropzone 文件的合同列、行数、Ex/Ey/Ez 组件和 sensor 子集。 |
| `export_cst_true_nearfield_monitor.py` | 规划、检查并尝试导出两份 G3 required full-grid CST 真近场 monitor/probe CSV。 |
| `merge_cst_level1_exports.py`、`merge_cst_level2_exports.py` | 合并 CST 导出的 near/far-field 数据。 |
| `run_cst_solver_project.py`、`export_cst_farfield_results.py` | 本机 CST 求解和结果导出辅助入口。 |

## 识别与报告生成

| 文件 | 作用 |
|---|---|
| `run_cst_recognition.py`、`run_cst_recognition_ablation.py` | 空域、频率、极化等特征提取与分类识别实验。 |
| `run_cst_recognition_stress_test.py` | 对 G2 代表布局做 Level 2 clean-train/perturbed-test 鲁棒性验证，覆盖噪声、相位抖动和通道缺失。 |
| `run_cst_recognition_augmented_stress_test.py` | 在同一 held-out 压力测试上加入扰动增强训练，对照 clean-train 边界能否被校准/增强恢复。 |
| `run_cst_recognition_leave_one_family_out.py` | 逐类留出 noise/phase/dropout/combined 扰动族，检查增强训练对未见误差族的外推能力。 |
| `run_cst_recognition_seed_stability.py` | 对 leave-one-family 中的 noise/dropout 随机扰动做多种子稳定性统计，输出均值、最小值和近似 95% CI。 |
| `run_cst_recognition_dropout_mitigation.py` | 对 held-out dropout 或含 dropout 组合扰动比较 zero-fill、mask 特征和缺测插补策略。 |
| `run_cst_recognition_structured_dropout.py` | 在已知扰动增强训练后，测试 sensor-node dropout、polarization-pair dropout 和 azimuth-sector dropout 等未见结构化缺测模式。 |
| `run_cst_recognition_instrument_error.py` | 测试全局增益漂移、传感器增益偏置、频率响应斜率、极化增益不平衡和混合幅相偏置等仪器相关误差。 |
| `run_cst_recognition_compound_stress.py` | 测试仪器偏置与结构化缺测同时出现时的复合压力边界，并比较缺测缓解策略。 |
| `run_cst_structure_comparison.py` | 结构/安装影响对比实验。 |
| `build_g3_model_dashboard.py` | 汇总 G3 源模型、SWE、Huygens 和真近场 gate 证据，输出当前可汇报结论与下一步动作。 |
| `build_*.py` | 报告、PPT、提交包、仪表盘和审查材料生成脚本。 |

## 常用命令

```powershell
python code\optimize_sampling_layout.py
python code\run_cst_sampling_tradeoff.py
python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check
python code\run_cst_source_model_sweep.py
python code\run_cst_sparse_reconstruction.py
python code\run_cst_level1_convention_check.py
python code\prepare_cst_true_nearfield_workpack.py
python code\prepare_cst_true_nearfield_operator_packet.py
python code\export_cst_true_nearfield_monitor.py --dry-run
python code\export_cst_true_nearfield_monitor.py --inspect-only
python code\derive_true_nearfield_layout_exports.py --sample-id L1_short_dipole_z_1p2G
python code\run_true_nearfield_gate.py
python code\run_true_nearfield_workflow_decision.py
python code\build_true_nearfield_handoff.py
python code\check_true_nearfield_dropzone.py
python code\build_g3_model_dashboard.py
python code\compare_true_nearfield_exports.py --true-nearfield data\cst_exports\level1\all_nearfield.csv --reference-nearfield data\cst_exports\level1\all_nearfield.csv --out-dir data\cst_true_nearfield_workpack\reference_self_check
python code\run_spherical_nf_ff_baseline.py
python code\run_spherical_nf_ff_tradeoff.py
python code\build_sampling_decision_matrix.py
python code\prepare_huygens_surface_prior.py
python code\run_cst_huygens_baseline.py
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
python code\run_cst_recognition.py
python code\run_cst_recognition_stress_test.py
python code\run_cst_recognition_augmented_stress_test.py
python code\run_cst_recognition_leave_one_family_out.py
python code\run_cst_recognition_seed_stability.py
python code\run_cst_recognition_dropout_mitigation.py
python code\run_cst_recognition_dropout_mitigation.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --held-out-families dropout,combined --out-dir data\recognition_stress_tests\level2_dropout_mitigation_extended
python code\run_cst_recognition_structured_dropout.py
python code\run_cst_recognition_instrument_error.py
python code\run_cst_recognition_compound_stress.py
```

## Spherical reduced-layout addendum

`run_spherical_nf_ff_tradeoff.py` writes
`data/sampling_layouts/spherical_nf_ff_tradeoff/`. It reuses the scalar
spherical-harmonic NF-FF sanity baseline on every candidate layout and records
the best `lmax`/regularization setting per candidate.

Current diagnostic result: `geometric_farthest_32` is the smallest reduced
layout that reaches `strict_pass` under this angular scalar check
(`lmax = 4`, `lambda = 1e-10`, min corr about `0.9991`, max NMSE about
`9.77e-04`, zero main-lobe error, total complex `Etheta/Ephi` far-field
correlation about `0.9994`, and total complex relative L2 error about
`3.47e-02`). Treat it as a priority layout for true CST near-field monitor
reruns, not as final vector SWE or Huygens proof.

`prepare_cst_true_nearfield_workpack.py` now consumes those results and writes
`true_nearfield_priority_layout_queue.csv` plus
`true_nearfield_priority_sensor_subsets.csv`, prioritizing `full_grid_162`,
`geometric_farthest_32`, and `fibonacci_snap_120`.

`prepare_cst_true_nearfield_operator_packet.py` narrows the current workpack to
the two required `full_grid_162` CST exports and writes tracked task cards under
`data/cst_true_nearfield_workpack/operator_packet/`. Current packet status:
required full-grid present `0/2`; export the two 486-row true-monitor CSVs
before running the required gate.

`export_cst_true_nearfield_monitor.py` is the executable bridge for that
blocker. Use `--dry-run` first to refresh
`outputs/cst_true_nearfield_monitor_export/true_nearfield_export_task_plan.csv`.
Use `--inspect-only` to open the two `.cst` projects with CST Python and record
available result-tree items without writing contract CSVs. A non-dry run only
writes `data/cst_exports/level1_true_nearfield/*_true_nearfield.csv` after it
can parse complete Cartesian `Ex/Ey/Ez` values for all 162 shell sensors. The
worker records `Field Monitors`/`Probes` definition nodes for diagnosis, but it
attempts ASCII export only on solved result-tree nodes under `1D Results`,
`2D/3D Results`, or `Tables`.

Once the full-grid true-monitor CSV exists,
`derive_true_nearfield_layout_exports.py` filters it through that subset table
and writes the queued 32/120 reduced-layout CSVs for follow-up comparison.

`build_sampling_decision_matrix.py` converts the same evidence into a
collaboration-facing decision table under
`data/sampling_layouts/sampling_decision_matrix/`. Current committed decision:
`full_grid_162` is the physical reference, `geometric_farthest_32` is the first
reduced-layout true-monitor rerun, `fibonacci_snap_120` is the conservative
cross-check, and `task_driven_32`/`task_driven_48` are classification probes
that still need validation before report-level claims.

`run_true_nearfield_gate.py` wraps the same queue into a post-export workflow
gate. It records whether each `full_grid_162`, `geometric_farthest_32`, and
`fibonacci_snap_120` source export is still pending, derives reduced layouts
from a full-grid monitor export when possible, compares available rows against
the FarfieldPlot-derived reference, and writes
`data/cst_true_nearfield_workpack/gate_report/`.

`run_true_nearfield_workflow_decision.py` is the decision entrance after the
handoff/dropzone/gate reports exist. It writes
`outputs/cst_true_nearfield_workflow_decision/` with the current decision,
required full-grid file status, and the next command list. Current committed
decision: wait for the two required `full_grid_162` true-monitor CSVs before
running the required gate.

## G3 model dashboard addendum

`build_g3_model_dashboard.py` writes `outputs/g3_model_dashboard/`. It
consolidates the current Level 1 evidence into:

- `model_comparison.md`: report-safe interpretation and next actions.
- `g3_model_status.csv`: one evidence row per source/SWE/Huygens/gate artifact.
- `reconstruction_metrics.csv`: same model status table under the future-plan
  metric filename.
- `g3_next_actions.csv`: owner/gate/action table for CST, algorithm, and report
  operators.

Current dashboard decision: do not claim final reduced-sampling proof yet. The
true CST near-field monitor gate is still `pending_source`, so `full_grid_162`
monitor data must be exported first. The scalar spherical NF-FF 32-point result
is a true-monitor rerun priority with both power-pattern and complex-component
sanity metrics, while Huygens and generic source-grid rows remain
`diagnostic_only`.

## Recognition stress-test addendum

`run_cst_recognition_stress_test.py` writes
`data/recognition_stress_tests/level2_robustness/`. It trains SVM/RF models on
clean Level 2 samples, then evaluates the held-out samples under clean, noise,
phase-jitter, dropout, and combined perturbation cases for `full_grid_162`,
`geometric_farthest_32`, `fibonacci_snap_120`, `task_driven_32`, and
`task_driven_48`.

Current result: clean, single-noise, single-phase, and 10 percent dropout cases
remain at accuracy `1.000`, but the combined `noise10_phase15_dropout10` case
falls below the `0.85` threshold for all tested layouts. Treat this as a G5
robustness boundary and as motivation for calibration/augmentation before
claiming recognition generalization under compound measurement errors.

`run_cst_recognition_augmented_stress_test.py` is the follow-up calibration
experiment. It keeps the same layouts, held-out split, and stress cases, but
expands the training set with the clean/noise/phase/dropout/combined
perturbation profiles before evaluating the same held-out stress rows. It
writes `data/recognition_stress_tests/level2_augmented_robustness/`.

Current augmented-training result: all 40 layout/stress rows return to
accuracy `1.000`, including the combined perturbation rows. Treat this as
evidence that known measurement-error families can be absorbed by training
augmentation on the current Level 2 CST-derived element-library data. It is not
proof of robustness to unknown full-wave airframe scattering or unmeasured
instrument errors.

`run_cst_recognition_leave_one_family_out.py` is the next generalization check.
It withholds one stress family from augmentation at a time (`noise`, `phase`,
`dropout`, or `combined`), trains on clean plus the remaining families, and
tests the held-out split on the unseen family. It writes
`data/recognition_stress_tests/level2_leave_one_family_out/`.

Current leave-one-family result: all 35 layout/family/stress rows remain above
the `0.85` threshold. The worst rows are `geometric_farthest_32` and
`task_driven_48` under held-out `dropout_25pct`, both at accuracy about
`0.867`. Treat this as stronger internal evidence than full augmentation, but
also as a reminder that dropout-like missing-channel errors are still the
tightest G5 recognition margin.

`run_cst_recognition_seed_stability.py` repeats the focused leave-one-family
check across seeds `202614`, `202615`, and `202616` for held-out `noise` and
`dropout` families. It writes
`data/recognition_stress_tests/level2_seed_stability/` with per-seed metrics
and aggregate mean/std/min/95% CI tables.

Current seed-stability result: all 60 rows pass the `0.85` threshold. The
tightest case is `geometric_farthest_32` under held-out `dropout_25pct`
(`mean accuracy ~= 0.933`, `min accuracy ~= 0.867`, clipped approximate 95% CI
`[0.768, 1.000]`). This keeps missing-channel/dropout behavior as the G5
calibration target while making the noise/dropout conclusion less dependent on
a single random split.

`run_cst_recognition_dropout_mitigation.py` is the focused missing-channel
follow-up. It keeps the leave-one-family protocol, focuses on held-out dropout
for the two tightest layouts, and compares zero-fill, missing-mask features,
frequency/sensor median imputation, and imputation plus mask features. It
writes `data/recognition_stress_tests/level2_dropout_mitigation/`.

Current dropout-mitigation result: 48 seed/layout/strategy/stress rows all pass
the `0.85` threshold. Mask features alone do not improve the zero-fill margin.
The frequency/sensor median imputation strategy raises the tightest
`geometric_farthest_32/dropout_25pct` aggregate from mean accuracy about
`0.956` and min `0.867` to mean/min `1.000`. Treat this as a candidate
test-time missing-channel preprocessing step for G5, still bounded to Level 2
CST-derived internal stochastic dropout evidence.

The extended mitigation run writes
`data/recognition_stress_tests/level2_dropout_mitigation_extended/`. It tests
the same four strategies on all five G2 representative layouts and withholds
both `dropout` and `combined` families. Current extended result: all 180 rows
pass `0.85`; zero-fill has min accuracy `0.867`; mask-only also bottoms at
`0.867` and can be worse than zero-fill on one `full_grid_162/dropout_25pct`
aggregate; both frequency/sensor median imputation variants reach mean/min
accuracy `1.000`. Report imputation-only as the cleaner current missing-channel
preprocessing candidate, with zero-fill retained as the conservative baseline.

`run_cst_recognition_structured_dropout.py` is the structured missing-channel
follow-up. It trains with the existing clean/noise/phase/random-dropout/combined
augmentation profiles, then tests unseen sensor-node dropout, polarization-pair
dropout, and contiguous 60 deg azimuth-sector dropout. It writes
`data/recognition_stress_tests/level2_structured_dropout/`. Current structured
result: all 240 seed/layout/strategy/case rows pass `0.85`; the worst single
row is `geometric_farthest_32` with mask features under
`sensor_node_dropout_25pct` at accuracy `0.933`; both frequency/sensor median
imputation variants reach mean/min accuracy `1.000`. Treat this as internal
structured missing-channel evidence, not as real instrument calibration or
full-wave complex-airframe validation.

`run_cst_recognition_instrument_error.py` is the instrument-error follow-up.
It trains both clean and known-perturbation-augmented models, then tests
unseen correlated calibration errors: global gain drift, per-sensor gain bias,
frequency-response slope, polarization gain imbalance, and mixed amplitude/
phase bias. It writes `data/recognition_stress_tests/level2_instrument_error/`.
Current result: all 150 seed/layout/profile/case rows pass `0.85`; the worst
single row is `geometric_farthest_32` under `sensor_gain_bias_3db` at accuracy
`0.933`; both training profiles have mean accuracy about `0.999` and minimum
`0.933`. Treat this as internal simulated instrument-error evidence, not as
real calibration or full-wave complex-airframe validation.

`run_cst_recognition_compound_stress.py` is the severe compound-stress
follow-up. It trains with the existing clean/noise/phase/random-dropout/combined
augmentation profiles, then tests unseen cases that combine instrument-like
gain/phase bias with structured sensor-node, polarization-pair, or azimuth
sector dropout. It writes
`data/recognition_stress_tests/level2_compound_stress/`. Current result: all
240 rows run, but not all rows pass `0.85`; the worst single row is
`full_grid_162/zero_fill/sensor_gain3db_sensor_node_dropout25pct` at accuracy
`0.733`. The best overall strategy is `freq_sensor_median_impute`, with mean
accuracy about `0.993` and minimum `0.867`. Treat this as the current G5
boundary: raw zero-fill/mask can fail under severe compound errors, while
frequency/sensor median imputation is the reportable mitigation candidate.

## Huygens baseline addendum

`huygens_core.py` builds the first Huygens-style surface measurement and
far-field matrices. `run_cst_huygens_baseline.py` runs the Level 1 full-grid
diagnostic using `data/source_priors/huygens_surface/level1_local_sphere_r0p35_nodes.csv`.
It now compares two field models: the compact `radiating_dipole` sheet and the
fuller diagnostic `current_green` near-field branch.

The runner now includes a surface smoothness sweep through `--smooth-lambda`
(default `0`, `1e-6`, `1e-4`, `1e-2`) and reports the coefficient jump metric
in `data/sampling_layouts/cst_level1_huygens_baseline/`.

The current best setting is still `diagnostic_only`: `huygens_em_minus` with
`field_model = radiating_dipole`, `lambda = 1e-2`, `smooth_lambda = 0`, min
corr about `0.778`, max NMSE about `0.264`, and a large main-lobe error. The
new `current_green` branch is also diagnostic-only and tracks the best row very
closely, so the remaining gap is likely a source/operator convention issue
rather than a simple missing near-field term. A small smoothness penalty
slightly reduces NMSE/jump but does not close the gate, so this script remains
a measurement-matrix smoke test and a physics-prior development entry point. Do
not use it as a final reduced-sampling proof until the full-grid Huygens
baseline reaches the same acceptance gate used by the source-model diagnostics.

## 当前重点

G2 已生成非冗余半球采样候选。G3 正在校准真实 CST Level 1 数据链：中心源先验和轻量球谐 NF-FF baseline 共同证明角度/极化/比较链路可信；Huygens 面源 baseline 已可运行并新增 `current_green` 诊断分支，但当前仍为 `diagnostic_only`，通用等效源网格也仍未达到最终采样证明要求。下一步应补 CST 真近场 monitor 实测，并升级 Huygens 电/磁面流 Green 算子与正则化。

## CST solver mesh-limit addendum

`run_cst_solver_project.py` now records CST solver-log diagnostics in addition
to result-tree inspection. For the current required true-nearfield trial,
`StartSolver` succeeds but CST stops before producing result-tree child items
because the 13 m Cartesian probe setup expands to about `4.6` billion mesh
cells and requires at least `3` MPI cluster nodes. Treat this as a modeling and
sampling-workflow limit, not as CST installation failure.

Next G3 code work should generate a mesh-safe CST observation pack: local
Huygens/near-boundary monitors or other compact physical evidence near the
source, followed by Python extrapolation to the 13 m hemisphere shell.
