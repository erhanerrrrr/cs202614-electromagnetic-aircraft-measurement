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
python code\run_cst_impedance_stability_gate.py
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

`run_cst_impedance_stability_gate.py` reads the mesh-safe Huygens batch result
CSV files and writes
`data/sampling_layouts/cst_meshsafe_huygens_impedance_stability/`. It checks
whether the scalar `eta_eff/eta0` calibration has an interior cross-case optimum
or is sitting on a scan boundary. It also reads cached CST ResultTree inspection
JSON files to record whether matching H-field probe curves are visible. Current
use: keep the mesh-safe Huygens route at calibrated-proxy wording until H-field
currents or an interior stable impedance bound exists.

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

## CST mesh-safe Huygens workpack addendum

`prepare_cst_meshsafe_huygens_workpack.py` is the current G3 bridge after the
13 m Cartesian probe mesh-limit diagnosis. It creates
`data/cst_meshsafe_huygens_workpack/` with:

- two Level 1 required mesh-safe Huygens CST cases;
- 96 local Cartesian probe points on `level1_local_sphere_r0p35`;
- `local_huygens_export_contract.csv` for local E-field probe exports;
- `local_huygens_hfield_export_contract.csv` for local H-field probe exports;
- `next_meshsafe_huygens_commands.csv` with the E/H project-generation,
  short-path solver gate, and ResultTree export commands.

Use it before regenerating the CST projects:

```powershell
python code\prepare_cst_meshsafe_huygens_workpack.py
python code\run_cst_level1_required_automation.py --level1-csv data\cst_meshsafe_huygens_workpack\level1_required_meshsafe_huygens_cases.csv --probe-csv data\cst_meshsafe_huygens_workpack\level1_local_huygens_probe_points.csv --out-dir C:\csttmp\huy_p --probe-mode efield
```

Then run the solver gates through short paths such as `C:\csttmp\huy_s` for
E-field and `C:\csttmp\huy_hs` for H-field to avoid CST internal result-path
limits. Keep both project generation and solver trials on short ASCII paths;
the Chinese desktop path can make CST API save/close calls report
`RuntimeError()` even when the `.cst` file appears. Current evidence says CST
can run the mesh-safe project without the 4.6B-cell blocker. Both short-dipole
and half-wave H-field probe exports are now present. The batch now has a frozen
real E/H candidate accepted by both current Level 1 cases; the current
non-proxy blocker is explaining and validating that frozen sign/J-scale rule,
not CST startup or H-field coverage.

`export_cst_meshsafe_huygens_results.py` is the next audit/export controller.
It inventories the short-path CST result artifacts, checks whether the local
Huygens CSV contract exists and has the expected `96 * 3 = 288` component rows,
and optionally opens the CST project to inspect result-tree candidates. Use
`--field-kind e` for electric probes and `--field-kind h` for magnetic probes:

```powershell
python code\export_cst_meshsafe_huygens_results.py --field-kind e --inspect-tree
python code\export_cst_meshsafe_huygens_results.py --field-kind h --inspect-tree
```

The successful export route is CST `ResultTree`, not Field Monitor ASCII
export. The earlier CST popup saying ASCII export was unavailable came from
trying to export the 3D Field Monitor view directly; the solved local probe
curves can instead be read under `1D Results\Probes\E-Field\...\(X/Y/Z)` with
`GetResultFromTreeItem`, `GetYRe`, and `GetYIm`.

```powershell
python code\export_cst_meshsafe_huygens_results.py --attempt-export --overwrite
```

Current E-field status after the first short-path solver gate is
`target_contract_complete`: the short-dipole 1.2 GHz local Huygens contract has
`96 * 3 = 288` complex E-field component rows in
`data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv`.
The short-dipole H-field route now also reaches `target_contract_complete`:
`data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv`
contains the matching `96 * 3 = 288` complex H-field rows. To repeat that export
after solving `C:\csttmp\huy_hs\h_short_hfield.cst`, run:

```powershell
python code\export_cst_meshsafe_huygens_results.py --field-kind h --attempt-export --project C:\csttmp\huy_hs\h_short_hfield.cst
```

`run_cst_meshsafe_huygens_extrapolation.py` is the next Python-side diagnostic.
It consumes the real local CST probe CSV plus the Level 1 farfield reference
and writes local field quality and farfield-shape checks to
`data/sampling_layouts/cst_meshsafe_huygens_extrapolation/`:

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py
```

The first diagnostic pass is a data-chain success rather than a final physics
claim: the best variant reaches whole-pattern correlation about `0.999` and
scale-fitted power NMSE about `6.96e-4`, while the single-point main-lobe index
is still ambiguous for the broad short-dipole pattern. The next model work is
operator/convention calibration and a second source-case repeat, not CST
startup repair.

## CST mesh-safe Huygens two-case batch gate addendum

The second Level 1 mesh-safe source case now has the same real CST data-chain
coverage as the first one. The half-wave dipole short-path trial uses
`C:\csttmp\huy_h\h_half.cst`; CST finishes cleanly, the result tree contains
the expected probe curves, and the local Huygens E-field export reaches the
`96 * 3 = 288` row contract.

Use the half-wave export and batch gate commands below after the corresponding
short-path CST project has been solved:

```powershell
python code\export_cst_meshsafe_huygens_results.py --project C:\csttmp\huy_h\h_half.cst --sample-id L1_halfwave_dipole_z_1p2G --out-dir outputs\cst_meshsafe_huygens_result_export_halfwave --attempt-export --overwrite
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```

Current batch status is `2/2` completed with no missing local-field exports.
`L1_halfwave_dipole_z_1p2G` reaches `physics_proxy_pass`
(`electric_only_outgoing`, correlation about `0.9868`, scale-fitted power NMSE
about `1.41e-2`, main-lobe error `0 deg`). `L1_short_dipole_z_1p2G` remains a
strong data-chain case but is labeled `shape_pass_lobe_ambiguous` because its
broad ring-like pattern makes a single-point main-lobe metric unstable.

Run the batch manually with:

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```

The tracked batch outputs live in
`data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/`. Large CST
solver caches and result-tree export logs stay under `C:\csttmp` and
`outputs/`; they are audit caches rather than Git payloads.

## CST mesh-safe Huygens region-lobe addendum

`run_cst_meshsafe_huygens_extrapolation.py` now reports a top-power region-lobe
metric in addition to the older single-point main-lobe error. The region metric
uses the normalized-power `0.75` contour and records region error, Jaccard
overlap, and min capture. This keeps the strict point-lobe metric visible while
avoiding a false negative for broad or ring-like patterns.

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

Current two-case status:

- `L1_halfwave_dipole_z_1p2G`: `physics_proxy_pass`, point-lobe error `0 deg`,
  region-lobe error `0 deg`.
- `L1_short_dipole_z_1p2G`: `region_shape_pass`; point-lobe error remains about
  `139.52 deg`, but region-lobe error is `0 deg` and region Jaccard is about
  `0.919`.

The G3 dashboard now includes `meshsafe_huygens_real_cst_batch` as a
`region_proxy_batch_pass` evidence row. The first next action is no longer to
wait idly for true-monitor CSVs; it is to add H-field or calibrated-impedance
support for the local Huygens surface and rerun the two-case gate.

## CST mesh-safe Huygens scalar impedance addendum

`run_cst_meshsafe_huygens_extrapolation.py` now has an explicit scalar
impedance calibration proxy. The default run scans
`eta_eff/eta0 = 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0` for the outgoing
electric/magnetic equivalence variants while preserving the original E-only
and M-only diagnostics.

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

Current calibrated two-case status:

- Both real CST Level 1 mesh-safe cases select
  `outgoing_equivalence_minus_eta0p25`, i.e. `eta_eff = 0.25 eta0`.
- Both cases are `region_shape_pass`; the worst scaled NMSE is about
  `8.48e-4`, and the region-lobe error is `0 deg`.
- The G3 dashboard status for `meshsafe_huygens_real_cst_batch` is now
  `impedance_region_proxy_batch_pass`.

This is still a calibrated proxy, not final Huygens physics proof. The next
upgrade is H-field probe export or an independent stability test of the
selected `eta_eff` across additional CST cases.

## CST mesh-safe Huygens H-field workpack addendum

`export_cst_meshsafe_huygens_results.py` now supports a field switch instead of
being E-only:

```powershell
python code\export_cst_meshsafe_huygens_results.py --field-kind e
python code\export_cst_meshsafe_huygens_results.py --field-kind h
```

The default E-field path is still `C:\csttmp\huy_s\h_short.cst`; the default
H-field path is `C:\csttmp\huy_hs\h_short_hfield.cst`. The E-field route is
complete for the short-dipole contract (`288` rows). The H-field route has now
also completed for the short-dipole contract (`288` rows) through the short-path
project `C:\csttmp\huy_hs\h_short_hfield.cst`. The half-wave H-field export is
still pending, so the remaining work is case coverage and algorithmic
calibration, not general CST failure.

The generated workpack now includes:

- `data/cst_meshsafe_huygens_workpack/local_huygens_hfield_export_contract.csv`
- `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv`
  steps 5-7 for H-field project generation, short-path solver gate, and
  ResultTree export

`run_cst_meshsafe_huygens_extrapolation.py` now auto-loads a matching
`*_local_hfield.csv` when it exists, checks E/H surface alignment, and evaluates
real E/H variants based on `J = n x H_t` and `M = -n x E_t`.

## CST mesh-safe Huygens real E/H addendum

Both Level 1 mesh-safe local H-field CSVs now exist:

```powershell
python code\run_cst_meshsafe_huygens_extrapolation.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
```

Current E/H status:

- `L1_short_dipole_z_1p2G` loads real E-field and H-field rows, `96 * 3 = 288`
  components for each field.
- `L1_halfwave_dipole_z_1p2G` also loads matched real E-field and H-field rows,
  again `96 * 3 = 288` components for each field.
- The measured tangential E/H impedances are about `425.36 ohm` (`1.129 eta0`)
  for the short dipole and `370.38 ohm` (`0.983 eta0`) for the half-wave dipole.
- The real E/H J-scale scan now reaches `strict_pass` for both cases. The best
  branches are `eh_love_equivalence_minus_j96` for the half-wave dipole
  (`scaled_power_nmse = 7.131984e-04`) and `eh_love_equivalence_plus_j256` for
  the short dipole (`scaled_power_nmse = 9.953152e-04`).
- The batch gate completes `2/2` cases, with `2/2` H-field loaded, `2/2`
  accepted real E/H candidate sets, and `0/2` best rows using a non-eta0 scalar
  impedance proxy. The remaining gate is `cross_case_sign_and_scale_disagreement`
  (`J = 96` vs `256`, `minus` vs `plus`), so the next algorithm work is a
  source-family or geometry-aware Huygens/Stratton-Chu normalization rule.
- The frozen-rule gate now selects one global candidate,
  `eh_love_equivalence_minus_j96`, for the two current Level 1 cases. It is
  accepted for `2/2` cases, strict for `1/2`, has minimum correlation
  `0.9988956628`, and maximum scaled power NMSE `7.303417569844e-04`.
  Therefore the next algorithm work is no longer free per-source selection; it
  is explaining and validating the frozen sign/J-scale rule on a broader source
  family.

This means CST is currently runnable on the mesh-safe path. The active blocker
is not CST startup or solver failure; it is turning the now-available real E/H
probe data into a report-level vector surface-integral proof.

## CST mesh-safe Huygens rotation-covariance addendum

The frozen real E/H candidate can now be checked for coordinate covariance:

```powershell
python code\run_cst_huygens_rotation_covariance.py
python code\build_g3_model_dashboard.py
```

Current result: `rotation_covariance_strict_pass` for
`eh_love_equivalence_minus_j96`. The gate uses `2` real E/H base CST cases and
`9` rigid rotations per case, giving `18/18` strict covariance passes. The
maximum covariance scaled power NMSE is about `4.04e-29`, and the maximum
normalized absolute error is about `2.74e-14`.

This proves the implementation rotates consistently as a vector surface
operator. It is still not an independent CST source-family proof; the remaining
CST work is x/y/tilted/off-axis/multi-source export under the same frozen rule.

## CST mesh-safe Huygens source-family workpack addendum

The next independent CST source-family gate is now packaged:

```powershell
python code\prepare_cst_huygens_source_family_workpack.py
python code\build_g3_model_dashboard.py
```

The workpack lives in:

```text
data/cst_meshsafe_huygens_source_family_workpack
```

Current status: `source_family_workpack_ready`.

- Frozen rule under test: `eh_love_equivalence_minus_j96`.
- Automation-ready source-family cases: `6`.
- Case-scoped local Huygens probe rows: `576`.
- Advanced tracked but not automated rows: tilted dipole and two-source pilot.
- Ordered CST commands:
  `data/cst_meshsafe_huygens_source_family_workpack/next_source_family_commands.csv`.

This is not a new physics pass yet. It is the CST generation/solve/export
handoff needed to test whether the same frozen E/H Huygens rule remains
accepted on independent x/y/off-axis CST solves without per-source retuning.

## CST mesh-safe Huygens source-family project generation addendum

The S42 source-family handoff has now passed real CST API project generation
for both E-field and H-field variants:

```powershell
python code\build_cst_source_family_generation_status.py
python code\build_g3_model_dashboard.py
```

Current status: `source_family_projects_generated`.

- E-field CST projects: `6/6`.
- H-field CST projects: `6/6`.
- Total combined project rows: `12`.
- Local project roots: `C:\csttmp\huy_sf_e\projects` and
  `C:\csttmp\huy_sf_h\projects`.
- Repository evidence:
  `outputs/cst_meshsafe_huygens_source_family_generation/`.

This proves that the x/y/off-axis source-family generator is CST-compatible.
The active gate is now solver/export completion plus frozen-rule validation on
the exported source-family E/H CSVs.

## CST mesh-safe Huygens source-family solver pilot addendum

The first generated source-family solver pilot is now tracked separately from
project generation:

```powershell
python code\build_cst_source_family_solver_status.py
python code\build_g3_model_dashboard.py
```

Current status: `source_family_solver_pilot_timed_out`.

Key evidence from `L1_short_dipole_x_1p2G_efield`:

- Real CST API used and solver start returned OK.
- Elapsed time: `609.36 s` against a `600 s` timeout.
- ResultTree after the run contains `788` result items, including `770`
  E-field probe entries.
- CST reports `1457297` maximum time steps and a `-40 dB` steady-state
  accuracy limit.
- No export-ready local E/H CSV or far-field artifact was produced.

This is not a CST startup failure. It is a solver/runtime settings gate. Keep
the same short x-oriented case as the pilot, repair the time-domain settings or
validate a frequency-domain/fast-path variant, and only then run the remaining
source-family queue.

## CST mesh-safe Huygens source-family solver-safe pilot addendum

The S44 timeout is now split into an ordered diagnostic ladder:

```powershell
python code\prepare_cst_source_family_solver_safe_pilot.py
python code\build_cst_source_family_solver_safe_status.py
python code\build_g3_model_dashboard.py
```

Current status: `source_family_solver_safe_matched_eh_finished`.

- Target sample: `L1_short_dipole_x_1p2G`.
- Tracked CST trials: `7`.
- Executed CST trials: `7`.
- Finished rows: `none` (`78.7 s`), `efarfield96` (`114.0 s`),
  `efield24` (`343.4 s`), `hfield24` (`333.3 s`), `efield48`
  (`946.5 s`), `efield96` (`3564.2 s`), and `hfield96` (`3348.3 s`).
- Matched E/H ready: `True`.
- Ladder: `none -> efarfield96 -> efield24 -> hfield24 -> efield48 -> efield96 -> hfield96`.
- Workpack: `data/cst_meshsafe_huygens_source_family_solver_safe_pilot/`.
- Status output: `outputs/cst_meshsafe_huygens_source_family_solver_safe_status/`.

This is still not a new physics pass. It is the execution queue needed to
determine whether the source-family timeout is caused by the base CST solve,
far-field angular probes, or local Cartesian Huygens probe count. The completed
full E/H pilot shows that the short x model is not blocked by CST itself; the
practical gate is now ResultTree CSV export and then frozen-rule Huygens
validation on matched E/H data.
