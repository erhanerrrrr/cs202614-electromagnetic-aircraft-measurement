# 未来工程方案

版本：v1.2
更新依据：当前 GitHub 工程状态、CST Level 1 诊断结果、导师 DeepSeek 记录、文献矩阵、新增非冗余采样/反演校准脚本和 true-monitor reduced-layout 复跑队列。

## 1. 当前工程判断

项目已经形成可协作的主链路：

```text
半球 2pi 测点设计
  -> CST Level 1 标准源数据
  -> Python near/far-field 数据合并与校验
  -> 等效源反演和远场外推
  -> 少测点采样对比
  -> 空域/频率/极化特征分类
  -> 报告、PPT、提交包和复现文档
```

当前最重要的判断不是“流程能否跑通”，而是“哪些证据可以写进报告，哪些还只能作为诊断”。目前结论如下：

| 模块 | 当前状态 | 工程含义 |
|---|---|---|
| 仓库整理 | 已建立可协作目录和 GitHub public 仓库 | 队友可以按 README、docs 和脚本入口接手。 |
| 非冗余采样候选 | 已生成 162/120/81/48/32 点候选布局 | 可作为 CST 复跑计划，不能单独作为最终少测点证明。 |
| Level 1 中心源 sanity check | `corr_pass_nmse_near`，主瓣误差为 0 | CST 导出、Python 读取和远场比较链路总体可信。 |
| 通用等效源网格 | `diagnostic_only` | 不能用它直接宣称 120/81/48/32 点方案有效。 |
| 稀疏等效源 | Corr/NMSE 明显改善，但主瓣仍未过关 | 稀疏有帮助，但不能替代物理源先验。 |
| 相位/极化约定检查 | 未发现能救活通用网格的简单全局约定错误 | 下一步应转向 Huygens/SWE/结构先验，而不是继续盲调符号。 |

## 2. 文献和导师建议的工程化吸收

导师 DeepSeek 记录和推荐文献可以归纳为五条工程原则：

1. 半球测量应以载体几何中心为坐标原点，测量半径要覆盖 `12 m x 10 m x 8 m` 包络并留余量。
2. 测点必须保留双极化复数场信息，不能只保留单通道幅值。
3. 少测点不是随机删点，而是要结合电磁场自由度、非冗余采样、互相干性和任务指标。
4. 远场外推应至少有一个规范物理基线，例如球面 NF-FF/SWE sanity check。
5. 分类不应只依赖单张方向图，应联合空域、频率、极化、等效源或球谐特征。

对应到项目，后续路线应把“采样、反演、分类”三块统一起来，而不是各自独立优化。

## 3. 下一阶段路线图

### G1：仓库协作与目录冻结

目标：让队友不依赖口头解释也能接手。

已完成：

- GitHub public 仓库已建立并推送主工程。
- `code/`、`data/`、`docs/`、`CST/` 等目录已整理。
- 小型 CSV/JSON/README 结果进入 Git；大型 CST 导出默认本地保留。

后续动作：

- 增加 `.github/ISSUE_TEMPLATE/`，至少包含 CST 样本提交、算法实验、文档修改、bug 四类模板。
- 在 README 中补充“哪些文件不进 Git、哪些结果必须附摘要”的协作规则。

### G2：采样方案升级

目标：从 162 点全量校准走向非冗余少测点方案。

已完成：

- `code/optimize_sampling_layout.py`
- `data/sampling_layouts/hemisphere_sampling_candidates.csv`
- `data/sampling_layouts/sampling_layout_summary.csv`
- `docs/nonredundant_sampling_design.md`

下一步：

1. 等 full-grid 物理反演基线稳定后，复跑 120/81/48/32 点候选。
2. 把采样方案分为两类：远场重建优先布局、分类识别优先布局。
3. 对 48/32 点方案增加任务驱动加权，例如主瓣、高能角域、极化差异和分类贡献区域。

建议判据：

```text
若 48 点在 Level 1/2 上保持 Corr >= 0.98 且分类 accuracy >= 0.85，
可作为主少测点方案；

若 32 点重建下降但分类稳定，
可作为“识别优先”低成本方案；

若 81 点显著更稳，
报告采用 81 点作为工程保守方案，48/32 点作为探索方案。
```

### G3：反演算法升级

目标：把 Tikhonov 等效源 baseline 升级成多模型可比较的反演工具箱。

已完成：

| 产物 | 结论 |
|---|---|
| `data/sampling_layouts/cst_level1_source_model_sweep/` | 中心源先验最好，通用网格仍诊断态。 |
| `data/sampling_layouts/cst_level1_sparse_calibration/` | group-sparse 提升 Corr/NMSE，但主瓣仍未达标。 |
| `data/sampling_layouts/cst_level1_convention_check/` | 未发现可直接解决通用网格问题的简单相位/极化约定错误。 |

下一步优先级：

1. 明确当前 Level 1 数据边界：nearfield 表来自 CST FarfieldPlot list evaluation，不是真正 full-wave 近场 monitor。
2. 准备一版真正的球面近场 monitor 导出任务包，用同一套脚本对比 FarfieldPlot-derived 样本和 near-field monitor 样本。
3. 增加 Huygens 面源或贴体/结构先验，避免自由点源网格把能量泄漏到非物理位置。
4. 增加球面 NF-FF/SWE sanity check，用于独立检查坐标、相位、极化和角度约定。
5. 做多频 group sparsity，让多个频点共享源支撑位置，只允许幅相随频率变化。

建议统一输出：

```text
reconstruction_metrics.csv
farfield_comparison.png
sensor_tradeoff.csv
model_comparison.md
```

### G4：复杂载体与安装效应增强

目标：从 element-library 和简化遮挡对照，走向更可信的航空载体结构影响分析。

后续动作：

1. 建立简化机身、翼面、尾翼参数化模型。
2. 建立源安装位置、朝向、工作状态配置表。
3. 比较无结构、有简化结构、局部遮挡三种情形的方向图差异。
4. 做跨结构域验证：无结构训练 -> 有结构测试，有结构训练 -> 无结构测试。

报告口径：

- element-library 证明源/状态可区分；
- 简化结构对照证明安装效应显著；
- full-wave airframe 是增强项，用于提高工程可信度。

### G5：分类识别泛化

目标：从“当前样本准确”升级为“面对噪声、缺测、结构变化仍可信”。

后续动作：

- 增加噪声强度、相位扰动、测点缺失、频点缺失消融。
- 对比 SVM、Random Forest、XGBoost、度量学习等模型。
- 增加特征重要性：空域、频率、极化、等效源/球谐特征各自贡献。
- 固定训练/测试划分和随机种子，避免偶然高分。

### G6：报告与答辩增强

目标：把方案从“材料齐全”提升为“评审容易相信”。

需要强化的叙事：

1. 为什么半球 2pi 不是任意选择：对应球面近场测量和受限区域采样。
2. 为什么少测点可行：自由度/NDF、非冗余采样、误差曲线三重证据。
3. 为什么能外推远场：球面 NF-FF 规范基线和等效源反演增强路线。
4. 为什么能分类：空域、频率、极化、等效源/球谐特征联合指纹。
5. 当前边界是什么：FarfieldPlot-derived Level 1 样本、element-library 和简化结构不是最终复杂载体 full-wave 证明。

## 4. 近期 Sprint 建议

按当前工程价值，建议下一轮按这个顺序推进：

1. 已新增 CST true near-field monitor 导出工作包、宏骨架、对照脚本和三档复跑队列；下一步等待 CST 真 monitor 实测 CSV 回填。
2. 已实现 `code/run_spherical_nf_ff_baseline.py` 的轻量球谐 NF-FF sanity check，当前 Level 1 两例达到 `strict_pass`。
3. 已新增 `docs/huygens_surface_model_note.md` 和 `code/prepare_huygens_surface_prior.py`，明确面源模型、四复未知量、正则化、输出指标和先验节点工作包。
4. 在当前 Level 1 两个标准源上复跑：center prior、generic grid、group-sparse、convention check、SWE sanity baseline。
5. 只有当 full-grid 基线达到验收标准后，再复跑 120/81/48/32 点候选并更新报告。

## 5. 参考链接

- DeepSeek 导师分享记录：`https://chat.deepseek.com/share/n42ew5j5gw8vx7unqd`
- Restricted Domain Compressive Sensing for Antenna Metrology：`https://arxiv.org/abs/2109.10040`
- Migliore, An Intuitive Approach to the Optimal Sampling of an Electromagnetic Field：`https://www.mdpi.com/1424-8220/25/24/7591`
- Bucci and Migliore, Degrees of Freedom and Sampling Representation of Electromagnetic Fields：`https://doi.org/10.1109/MAP.2024.3513216`
- Sarkar et al., Spherical Near-Field to Far-Field Transformation：`https://doi.org/10.1002/9781119076230.ch7`
- Non-redundant spherical near-field sampling for efficient incident power density assessment：`https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2025.1738329/full`
- RWTH Aachen spherical near-field measurements：`https://www.ihf.rwth-aachen.de/en/research/research-topics/antenna-measurement/spherical-near-field-measurements`

## 6. 2026-06-02 G3 baseline update

The Huygens geometry contract has moved from a workpack to a runnable Level 1
diagnostic:

```powershell
python code\run_cst_huygens_baseline.py
```

It writes `data/sampling_layouts/cst_level1_huygens_baseline/` and compares
compact `radiating_dipole` rows against fuller `current_green` diagnostic rows
on the full 162-point layout. The runner also includes a nearest-neighbor
surface smoothness sweep (`smooth_lambda = 0`, `1e-6`, `1e-4`, `1e-2`). The
current best result is still `diagnostic_only` (`field_model =
radiating_dipole`, `min_corr ~= 0.778`, `max_nmse ~= 0.264`, large main-lobe
error), and the best row keeps `smooth_lambda = 0`. The `current_green` rows
track the compact model closely, and a small smoothness penalty lowers the
worst NMSE and coefficient-jump metric slightly but does not close the physics
gate. This is not yet a report-ready reduced-sampling proof.

The scalar spherical NF-FF reduced-layout tradeoff has also been added:

```powershell
python code\run_spherical_nf_ff_tradeoff.py
```

It writes `data/sampling_layouts/spherical_nf_ff_tradeoff/`. Under this
FarfieldPlot-derived angular diagnostic, `geometric_farthest_32` is the
smallest `strict_pass` reduced candidate (`lmax = 4`, `lambda = 1e-10`,
`min_corr ~= 0.9991`, `max_nmse ~= 9.77e-04`, zero main-lobe error). This is a
strong layout-prioritization signal for the next true CST near-field monitor
rerun, not a final vector SWE/Huygens proof.

Updated sprint order:

1. Keep `spherical_nf_ff_baseline/` and the center-source prior as the current
   trustworthy data-path sanity checks.
2. Wait for or produce true CST near-field monitor CSVs, then rerun source
   sweep, convention check, SWE baseline, spherical reduced-layout tradeoff, and
   Huygens baseline on that input.
3. Validate the Huygens electric/magnetic surface-current convention beyond
   the current `current_green` diagnostic branch; keep the field-model and
   surface smoothness sweeps as diagnostic axes, then add node-group and
   multi-frequency regularization after the operator convention is stable.
4. Use the generated true-monitor rerun queue: `full_grid_162` first,
   `geometric_farthest_32` second, and `fibonacci_snap_120` as the conservative
   120-point cross-check.
   `code/derive_true_nearfield_layout_exports.py` can derive the queued 32/120
   CSVs from a full 162-point true-monitor export.
5. Only after a full-grid physical baseline reaches `strict_pass` or an
   approved near-pass, write the 120/81/48/32 sampling candidates as report-level
   reduced-layout evidence.

## 7. 2026-06-02 true-monitor gate runner update

The true-monitor rerun queue now has a status gate:

```powershell
python code\run_true_nearfield_gate.py
```

It writes `data/cst_true_nearfield_workpack/gate_report/`, checks all 18 queued
case-layout rows, derives reduced layouts from a full-grid monitor export when
possible, and classifies each row as `pending_source`, `reference_match`,
`row_count_mismatch`, `pending_comparison`, or `needs_physical_rerun`.

Current committed state: all 18 rows are `pending_source`, because the real CST
true near-field monitor CSVs have not been exported into
`data/cst_exports/level1_true_nearfield/` yet. This is the intended clean state
for collaboration: CST operators know exactly which files to produce, and
algorithm operators have a single command to decide whether G3 can proceed or
must be rerun on authoritative monitor data.

## 8. 2026-06-02 G3 model dashboard update

The current G3 evidence is now consolidated by:

```powershell
python code\build_g3_model_dashboard.py
```

It writes `outputs/g3_model_dashboard/` and produces the future-plan filenames
`model_comparison.md` and `reconstruction_metrics.csv`, plus
`g3_model_status.csv`, `g3_next_actions.csv`, and
`g3_dashboard_summary.json`.

Current dashboard summary:

- `true_nearfield_monitor_gate` is `pending_source`; this is the active
  project boundary.
- Center-source prior and scalar spherical NF-FF baseline remain the trusted
  sanity checks for angle, polarization, and far-field comparison.
- `geometric_farthest_32` remains the smallest scalar SWE `strict_pass`
  reduced layout, but only as a true-monitor rerun priority.
- Generic grid, group-sparse, convention check, and Huygens surface prior remain
  `diagnostic_only`, so they should be written as calibration/bottleneck
  evidence rather than final sampling proof.

Use this dashboard as the first G3 decision entry in future sprints: if the
true-monitor gate remains pending, the CST operator exports monitor CSVs; if it
reports `needs_physical_rerun`, the algorithm operator reruns the source-model,
SWE, reduced-layout, and Huygens baselines on authoritative monitor data before
updating report claims.

## 9. 2026-06-02 CST true-monitor handoff update

The pending true-monitor export is now turned into a CST operator handoff by:

```powershell
python code\build_true_nearfield_handoff.py
```

It writes `outputs/cst_true_nearfield_handoff/`:

- `cst_true_nearfield_handoff.md`: the short human-facing task note.
- `expected_true_monitor_files.csv`: the full-grid monitor CSVs CST should
  produce first.
- `cst_operator_action_sheet.csv`: all 18 queued case-layout rows with action
  kind, target path, current file existence, and gate status.
- `post_export_algorithm_commands.csv`: the command sequence after files arrive.
- `handoff_summary.json`: machine-readable counts and next required action.

Current handoff result: two required full-grid CSVs are still pending, both with
486 expected rows:

- `data/cst_exports/level1_true_nearfield/L1_short_dipole_z_1p2G_true_nearfield.csv`
- `data/cst_exports/level1_true_nearfield/L1_halfwave_dipole_z_1p2G_true_nearfield.csv`

This narrows the external CST task to two exact required files before the
algorithm side derives 32/120 layouts or reruns physical G3 baselines.

The dropzone preflight is now:

```powershell
python code\check_true_nearfield_dropzone.py --required-only --full-grid-only
```

It writes `outputs/cst_true_nearfield_dropzone_check/` and validates the CST
CSV contract, expected 486 rows per required full-grid case, `Ex/Ey/Ez`
component coverage, frequency, sample id, and sensor subset before the
comparison gate is run. Current default status is `missing_file` for all 18
queued rows, which correctly reflects that no true-monitor CSV has been dropped
yet.

## 10. 2026-06-02 true-monitor workflow decision update

The handoff, dropzone preflight, true-monitor gate, and G3 dashboard are now
connected by a post-export decision entry:

```powershell
python code\run_true_nearfield_workflow_decision.py
```

It writes `outputs/cst_true_nearfield_workflow_decision/`:

- `true_nearfield_workflow_decision.md`: human-facing current decision,
  required file list, next commands, and claim boundary.
- `workflow_decision_summary.json`: machine-readable decision id, blocker,
  readiness counts, and input/output references.
- `workflow_next_commands.csv`: ordered CST/algorithm/report action list.
- `required_full_grid_status.csv`: two required full-grid rows with dropzone
  and gate status.

Current committed decision:

- `decision_id = await_required_full_grid_exports`
- required full-grid readiness is `0/2`
- blocker: the two required `full_grid_162` true-monitor CSVs are still missing
- next commands: export the two CST monitor CSVs, run
  `check_true_nearfield_dropzone.py --required-only --full-grid-only`, then run
  `run_true_nearfield_gate.py --required-only`

Use this script as the sprint decision entrance after every CST file drop. It
keeps the project from accidentally advancing to reduced-layout or report
claims before the authoritative monitor data and physical/vector baseline have
passed the gate.

## 11. 2026-06-02 component-aware SWE sanity update

The scalar spherical NF-FF scripts now record complex tangential far-field
component residuals in addition to angular power-pattern metrics:

```powershell
python code\run_spherical_nf_ff_baseline.py
python code\run_spherical_nf_ff_tradeoff.py
python code\build_g3_model_dashboard.py
```

Current full-grid scalar SWE sanity result:

- `lmax = 4`, `lambda = 0`, status `strict_pass`
- min power correlation about `0.9990`
- max power NMSE about `9.26e-04`
- min total complex `Etheta/Ephi` far-field correlation about `0.9995`
- max total complex `Etheta/Ephi` relative L2 error about `3.16e-02`

Current smallest strict reduced-layout result:

- `geometric_farthest_32`, `lmax = 4`, `lambda = 1e-10`
- min power correlation about `0.9991`
- max power NMSE about `9.77e-04`
- min total complex `Etheta/Ephi` far-field correlation about `0.9994`
- max total complex `Etheta/Ephi` relative L2 error about `3.47e-02`

This makes the scalar SWE sanity check stronger than a power-only comparison:
it now checks the complex tangential component path used by the near/far-field
workflow. The boundary is unchanged: these results are still based on the
current FarfieldPlot-derived angular samples and a scalar harmonic fit. They
should be used as layout-prioritization and convention evidence until true CST
near-field monitor exports and a physical/vector full-grid baseline pass.

## 12. 2026-06-02 GitHub collaboration update

The G1 collaboration action is now implemented in `.github/ISSUE_TEMPLATE/`
and `CONTRIBUTING.md`.

The repository has four issue templates:

- CST data/modeling task: CST modeling, export, true-monitor handoff, and gate
  checks.
- Algorithm experiment task: sampling, reconstruction, SWE/Huygens, recognition,
  and robustness experiments.
- Documentation/report task: workflow, future plan, report, PPT, literature
  matrix, and README updates.
- Bug report: script errors, CSV contract problems, invalid paths, and GitHub
  collaboration issues.

`CONTRIBUTING.md` now records branch naming, commit scope, large-file rules,
true-monitor validation commands, G3 dashboard refresh commands, and conclusion
wording boundaries. This closes the first G1 follow-up from the future plan:
teammates can now open structured issues for CST export, algorithm reruns,
documentation updates, and bugs instead of relying on oral task assignment.

## 13. 2026-06-02 G2 sampling decision matrix update

The reduced-sampling evidence is now consolidated into a collaboration-facing
decision matrix:

```powershell
python code\build_sampling_decision_matrix.py
```

It writes `data/sampling_layouts/sampling_decision_matrix/`:

- `sampling_decision_matrix.csv`: one row per candidate with proxy metrics,
  scalar SWE reduced-layout evidence, true-monitor queue role, recommendation,
  claim boundary, and next action.
- `sampling_decision_summary.json`: machine-readable summary of the current
  G2 decision.
- `README.md`: short human-facing handoff note for teammates.

Current decision:

- `full_grid_162` remains the physical reference anchor.
- `geometric_farthest_32` is the first reduced-layout true-monitor rerun
  priority because it is the smallest scalar SWE `strict_pass` candidate and is
  already queued by the true-monitor workpack.
- `fibonacci_snap_120` is the conservative 120-point cross-check against the
  32-point result.
- `task_driven_32` and `task_driven_48` are classification-focused probes.

This separates the next engineering actions more cleanly than a single
"best layout" label. G2 uses `geometric_farthest_32`/`fibonacci_snap_120` for
reconstruction evidence after the full-grid true-monitor CSVs arrive. G4 can
use `task_driven_32`/`task_driven_48` for recognition stress tests. G3 keeps
`full_grid_162` as the physical/vector baseline gate. The boundary is unchanged:
the matrix is a planning artifact, not final reduced-sampling proof, until true
CST monitor exports and the physical/vector baseline pass.

## 14. 2026-06-02 G5 recognition robustness update

The classification branch now has a clean-train/perturbed-test robustness
runner:

```powershell
python code\run_cst_recognition_stress_test.py
```

It writes `data/recognition_stress_tests/level2_robustness/`:

- `recognition_stress_metrics.csv`: one row per G2 representative layout and
  perturbation case, including SVM/RF accuracy and macro-F1.
- `recognition_stress_summary.json`: machine-readable worst-case summary,
  input references, stress definitions, and detailed model reports.
- `README.md`: human-facing interpretation and claim boundary.

The runner trains recognition models on clean Level 2 CST-derived samples and
evaluates the held-out samples under:

- clean reference,
- additive complex noise at 20 dB and 10 dB SNR,
- independent phase jitter at 15 deg and 45 deg,
- random theta/phi channel dropout at 10 percent and 25 percent,
- combined 10 dB noise + 15 deg phase jitter + 10 percent dropout.

Current result:

- `full_grid_162`, `geometric_farthest_32`, `fibonacci_snap_120`,
  `task_driven_32`, and `task_driven_48` all keep accuracy `1.000` for clean,
  single-noise, single-phase, and 10 percent dropout cases.
- The combined perturbation case falls below the `0.85` threshold for all
  tested layouts; the worst row is `full_grid_162` with accuracy about `0.467`.
- `dropout_25pct` is also a weak point for the task-driven 32/48 layouts.

Engineering interpretation: the current feature and model stack is strong for
single-factor disturbances but should not be claimed robust under compound
measurement errors. The next G5 step is to add perturbation-aware training or
calibration, then rerun the same script until the combined stress rows either
recover above `0.85` or are explicitly documented as the operating boundary.
This does not change the G3 reconstruction boundary: true CST monitor exports
and physical/vector baselines are still required for reduced-layout
reconstruction claims.

## 15. 2026-06-02 G5 perturbation-aware training update

The clean-train stress test exposed a useful but uncomfortable boundary: the
current recognition feature/model stack handles single-factor measurement
errors, but compound noise, phase jitter, and channel dropout can push every
tested layout below the `0.85` accuracy threshold.

The follow-up runner is now available:

```powershell
python code\run_cst_recognition_augmented_stress_test.py
```

It writes `data/recognition_stress_tests/level2_augmented_robustness/`:

- `recognition_augmented_stress_metrics.csv`: one row per selected layout and
  held-out stress case, with the clean-train baseline accuracy and the
  augmented-training delta.
- `recognition_augmented_stress_summary.json`: input references, augmentation
  definitions, model reports, and worst-case summary.
- `README.md`: short teammate-facing interpretation and claim boundary.

Current result:

- The same five layouts are tested: `full_grid_162`, `geometric_farthest_32`,
  `fibonacci_snap_120`, `task_driven_32`, and `task_driven_48`.
- The same eight held-out stress cases are used as the clean-train run.
- Training is expanded with clean, noise, phase-jitter, dropout, and combined
  perturbation profiles.
- All 40 layout/stress rows recover to accuracy `1.000`; the mean accuracy
  delta against the clean-train baseline is about `+0.060`.
- The previously weak combined perturbation rows recover, including the
  `noise10_phase15_dropout10` cases.

Engineering interpretation: for the current Level 2 CST-derived
element-library data, the recognition branch can absorb known measurement-error
families through perturbation-aware training. This should be reported as a
calibration/augmentation result, not as an unconditional robustness claim.

Remaining G5 validation before final report-level confidence:

1. Add a leave-one-stress-family-out check so the model is tested on an error
   family it did not see during augmentation.
2. Repeat the stress tests across several random seeds for dropout/noise
   sampling and report confidence intervals, not only one split.
3. When full-wave airframe or real measurement data arrives, rerun both
   `run_cst_recognition_stress_test.py` and
   `run_cst_recognition_augmented_stress_test.py` on that data.
4. Keep the G3 boundary separate: this G5 result supports classification
   robustness, while reduced-layout reconstruction still waits on true CST
   near-field monitor CSVs and a physical/vector baseline gate.

## 16. 2026-06-02 G5 leave-one-stress-family-out update

The next G5 validation step is now implemented:

```powershell
python code\run_cst_recognition_leave_one_family_out.py
```

It writes `data/recognition_stress_tests/level2_leave_one_family_out/`:

- `recognition_leave_one_family_metrics.csv`: one row per selected layout,
  held-out error family, and held-out stress case.
- `recognition_leave_one_family_summary.json`: input references, family
  mapping, training manifests, model reports, and worst-case summary.
- `README.md`: teammate-facing interpretation and claim boundary.

Method:

- Stress cases are grouped into `noise`, `phase`, `dropout`, and `combined`.
- For each run, one family is withheld from augmentation.
- The model trains on clean plus the remaining stress families.
- The same held-out sample split is then evaluated only on the unseen family.

Current result:

- Five layouts are tested: `full_grid_162`, `geometric_farthest_32`,
  `fibonacci_snap_120`, `task_driven_32`, and `task_driven_48`.
- Four held-out families are tested, covering seven non-clean stress cases.
- All 35 layout/family/stress rows remain above the `0.85` threshold.
- The tightest rows are held-out `dropout_25pct` for
  `geometric_farthest_32` and `task_driven_48`, both at accuracy about
  `0.867`, which is `-0.133` versus full perturbation-aware training.
- Held-out `noise`, `phase`, and `combined` rows remain at accuracy `1.000`.

Engineering interpretation: this is stronger evidence than full augmentation
because the tested error family is unseen during training augmentation. It
supports the claim that the current feature/model stack has some internal
generalization across measurement-error families on Level 2 CST-derived data.
The main remaining G5 margin is missing-channel/dropout behavior.

Next G5 actions:

1. Try dropout-aware features or simple missing-channel imputation to widen the
   `dropout_25pct` margin.
2. Preserve the report boundary: this is still internal perturbation-family
   evidence, not full-wave airframe validation or real instrument calibration.

## 17. 2026-06-02 G5 repeated-seed stability update

The focused repeated-seed validation step is now implemented:

```powershell
python code\run_cst_recognition_seed_stability.py
```

It writes `data/recognition_stress_tests/level2_seed_stability/`:

- `recognition_seed_stability_metrics.csv`: per-seed, per-layout, per-stress
  recognition metrics.
- `recognition_seed_stability_by_case.csv`: mean, standard deviation, minimum,
  and clipped approximate 95 percent CI by layout/stress case.
- `recognition_seed_stability_by_family.csv`: aggregate stability by held-out
  family.
- `recognition_seed_stability_by_layout.csv`: aggregate stability by layout.
- `recognition_seed_stability_summary.json` and `README.md`: machine-readable
  and human-facing summaries.

Method:

- Repeat the leave-one-stress-family-out protocol for seeds `202614`, `202615`,
  and `202616`.
- Focus on held-out `noise` and `dropout`, because those families contain
  stochastic perturbation draws and dropout was the tightest margin in the
  previous run.
- Vary both the stratified train/test split and the stochastic perturbation
  draws.

Current result:

- Five layouts, two held-out families, four stress cases, and three seeds give
  60 rows.
- All 60 rows remain above the `0.85` threshold.
- The worst single row is seed `202616`,
  `geometric_farthest_32/dropout/dropout_25pct`, accuracy about `0.867`.
- The tightest aggregated case is the same row family:
  `geometric_farthest_32/dropout/dropout_25pct`, mean accuracy about `0.933`,
  minimum accuracy about `0.867`, and clipped approximate 95 percent CI
  `[0.768, 1.000]`.
- Held-out `noise` is stable overall: family mean about `0.998`, minimum about
  `0.933`.
- Held-out `dropout` remains the main G5 margin: family mean about `0.991`,
  minimum about `0.867`.

Engineering interpretation: the repeated-seed result makes the G5 conclusion
less dependent on one random split or one stochastic perturbation draw. It also
confirms the same engineering priority as the leave-one-family run:
missing-channel/dropout robustness is the next useful calibration target.

Next G5 actions:

1. Add dropout-aware features that explicitly encode missing-channel masks or
   per-sensor valid-channel counts.
2. Test simple missing-channel imputation before classification, then compare
   against the current zero-fill convention.
3. Keep the report wording conservative: the seed-stability check strengthens
   internal perturbation evidence, but it is not real measurement calibration
   or full-wave complex-airframe validation.

## 18. 2026-06-03 G5 dropout mitigation update

The missing-channel follow-up is now implemented:

```powershell
python code\run_cst_recognition_dropout_mitigation.py
```

It writes `data/recognition_stress_tests/level2_dropout_mitigation/`:

- `recognition_dropout_mitigation_metrics.csv`: per-seed, per-layout,
  per-strategy dropout accuracy and macro-F1.
- `recognition_dropout_mitigation_by_strategy.csv`: aggregate comparison of
  zero-fill, missing-mask features, and imputation.
- `recognition_dropout_mitigation_by_case.csv`: layout/dropout-case/strategy
  aggregate table.
- `recognition_dropout_mitigation_by_layout.csv`,
  `recognition_dropout_mitigation_summary.json`, and `README.md`: supporting
  summaries and claim boundary.

Method:

- Keep the leave-one-stress-family-out protocol.
- Focus on held-out `dropout` for the two layouts that were tightest in the
  earlier checks: `geometric_farthest_32` and `task_driven_48`.
- Repeat seeds `202614`, `202615`, and `202616`.
- Compare four test-time missing-channel strategies: current zero-fill,
  missing-mask features, frequency/sensor median imputation, and imputation
  plus mask features.

Current result:

- Two layouts, two dropout cases, four strategies, and three seeds give 48
  rows.
- All 48 rows remain above the `0.85` threshold.
- Mask features alone do not improve zero-fill.
- Frequency/sensor median imputation raises the tightest
  `geometric_farthest_32/dropout_25pct` aggregate from mean accuracy about
  `0.956` and minimum accuracy about `0.867` to mean/min `1.000`.
- Adding mask features on top of imputation gives the same aggregate result as
  imputation alone, so the simpler imputation-only strategy is the cleaner
  current candidate.

Engineering interpretation: for the current Level 2 CST-derived
element-library data, random channel dropout is better treated as a
missing-data problem than as a raw zero-amplitude measurement. The best current
G5 preprocessing candidate is frequency/sensor median imputation before
recognition feature extraction.

Next G5 actions:

1. Use frequency/sensor median imputation as the default candidate when writing
   the missing-channel robustness section, while reporting zero-fill as the
   conservative baseline.
2. If time allows, broaden this mitigation comparison to all five G2 layouts
   and to compound perturbations that include dropout.
3. Keep the boundary explicit: this is still internal stochastic dropout
   evidence, not real instrument calibration, arbitrary sensor-failure
   coverage, or full-wave complex-airframe validation.
