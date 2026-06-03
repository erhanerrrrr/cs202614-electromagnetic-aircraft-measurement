# 复杂航空载体电磁辐射空域特性测量技术赛题工作区

当前目标：围绕 CS-202614 赛题，逐步完成方案报告、CST 仿真、近远场重建算法、测点优化、特征辨识和最终提交材料。

当前测量面选择：半球面 2π 测点布局；`outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` 是本阶段 CST Level 1/Level 2 的唯一测点表。

最新进展：Level 1 两个 required 标准源已经完成本机 CST solver-safe 求解、FarfieldPlot 线性 E-field 导出、CSV 校验、严格合并、批量重建和角域校准；角域校准最大 NMSE 约 `8.41e-5`、最小相关系数约 `0.99988`。Level 2 已完成 CST element-library 路线的 48/48 个样本导出、严格合并、识别和消融，accuracy=`1.000`。Level 2 简化结构遮挡对照中 mean shadow 约 `3.06 dB`、P95 shadow 约 `6.63 dB`、cross-domain accuracy=`1.000`；该证据用于说明结构/安装效应敏感性，不等同于 full-wave airframe scattering。本轮已生成正式报告 `submission/01_report/solution_report.docx/pdf`、答辩 `submission/02_presentation/defense_slides.pptx/pdf`、演示视频 `submission/03_video/demo_video.mp4` 和最终压缩包 `outputs/final_archive/CS-202614_submission.zip`。当前 `completion_proven=true`，zip 完整性检查通过；视频是 PowerPoint 自动计时静音版，正式报送前建议人工播放并按竞赛要求决定是否替换为带讲解版本。

## 目录总览

| 目录 | 内容 |
|---|---|
| `code/` | Python 算法、CST 接口、自动化、报告/审计生成脚本。 |
| `CST/` | CST 建模、宏模板、工程、导出和 Python 调 CST 工作流索引。 |
| `data/` | 当前主线真实/准真实 CST nearfield/farfield CSV。 |
| `docs/` | 技术路线、workflow、未来工程方案、文献矩阵、复现命令和阶段说明。 |
| `文档/` | 原始赛题 PDF、历史 Workflow 文档和正式交付物位置说明。 |
| `文献/` | 文献矩阵入口和导师新增推荐文献方向说明。 |
| `outputs/` | 自动生成结果、图表、审计、CST workpack 和提交证据，本地保留大文件。 |
| `submission/` | 当前提交草稿/交付结构。 |

本仓库默认忽略 `node_modules/`、CST 求解缓存、最终 zip 和可再生成的大型 CSV，便于 GitHub 协作。

## 当前小目标

小目标 1 已完成初版：

1. 文献筛查与可迁移技术策略：`docs/literature_screening_and_strategy.md`
2. 权威文献矩阵：`docs/literature_matrix.md`
3. 文献到算法迁移证据链：`docs/literature_to_algorithm_traceability.md`
4. 方案报告结构化初稿：`docs/solution_report_draft.md`
5. CST 技术路线与三人分工草案：`docs/phase_01_cst_technical_route_and_division.md`
6. 三人实名分工与技术路线交付稿：`docs/team_division_technical_route.md`
7. CST Level 1 标准源闭环规程：`docs/cst_level1_standard_source_protocol.md`
8. 可运行算法 baseline：`code/em_core.py`、`code/run_baseline.py`
9. CST 导出模板与校验接口：`code/prepare_cst_templates.py`、`code/check_cst_export.py`、`code/cst_io.py`
10. CST 数据重建闭环脚本：`code/run_cst_reconstruction.py`
11. CST 格式多源多状态识别数据生成：`code/generate_synthetic_cst_dataset.py`
12. CST 格式空-频-极化识别闭环脚本：`code/run_cst_recognition.py`
13. CST Level 2 多源多状态执行清单：`code/prepare_cst_level2_manifest.py`
14. CST 格式识别测点/频点删减验证：`code/run_cst_recognition_ablation.py`
15. CST Level 2 批量导出合并与缺漏检查：`code/merge_cst_level2_exports.py`
16. 重建鲁棒性与正则化扫描：`code/run_reconstruction_robustness.py`
17. 评分项证据板自动汇总：`code/build_scorecard.py`
18. 最终提交包索引：`code/build_submission_index.py`
19. 代码包依赖与复现说明：`requirements.txt`、`docs/reproduce_commands.md`
20. 数据字典与命名规范：`docs/data_dictionary.md`
21. CST 幅相导出归一化转换：`code/normalize_cst_complex_columns.py`
22. CST Level 1 标准源执行清单：`code/prepare_cst_level1_manifest.py`
23. CST Level 1 标准源批量导出审计：`code/merge_cst_level1_exports.py`
24. CST Level 1 标准源批量重建：`code/run_cst_level1_batch_reconstruction.py`
25. CST Level 1 三人冲刺交接单：`docs/level1_cst_sprint_handoff.md`
26. CST Level 1 同形合成闭环验证：`code/generate_synthetic_cst_level1_dataset.py`
27. CST Level 1 建模任务包：`code/prepare_cst_level1_workpack.py`
28. CST Level 2 多源识别建模任务包：`code/prepare_cst_level2_workpack.py`
29. 完成度审计与最短 gate：`code/build_completion_audit.py`
30. 项目文件索引：`docs/project_file_index.md`
31. 分阶段工作说明：`docs/stage_notes`
32. CST 真实执行日志模板：`code/prepare_cst_execution_log_templates.py`
33. 提交草稿包生成：`code/build_submission_draft.py`
34. CST 宏模板与 pilot 队列：`code/prepare_cst_macro_templates.py`
35. CST 执行 dashboard 与真实数据 dropzone：`code/build_cst_execution_dashboard.py`
36. 报告成稿素材包：`code/build_report_package.py`
37. 答辩 PPT 与演示视频素材包：`code/build_presentation_package.py`
38. Level 1 标准源解析方向图参考：`code/build_level1_analytic_reference.py`
39. 总控状态 dashboard 与三人任务队列：`code/build_master_dashboard.py`
40. CST G2 真机操作包：`code/build_cst_operator_runbook.py`
41. 赛题要求到证据矩阵：`code/build_problem_requirements_matrix.py`
42. CST Level 1 required 真机工程自动生成：`code/run_cst_level1_required_automation.py`
43. CST 单工程求解日志脚本：`code/run_cst_solver_project.py`
44. CST FarfieldPlot 真实结果导出脚本：`code/export_cst_farfield_results.py`
45. CST Level 2 element-library 工程生成：`code/run_cst_level2_element_library.py`
46. CST Level 2 element 叠加导出：`code/export_cst_level2_superposed_results.py`
47. 项目进展跟踪与导师汇报生成：`code/build_progress_report.py`
48. CST Level 1 FarfieldPlot-derived 角域校准：`code/run_cst_level1_angular_calibration.py`
49. CST Level 2 简化结构遮挡对照：`code/run_cst_structure_comparison.py`
50. 球谐 NF-FF 少测点布局诊断：`code/run_spherical_nf_ff_tradeoff.py`，当前将 `geometric_farthest_32` 标记为 true monitor 复跑优先候选，并已补充复场 `Etheta/Ephi` 分量相关系数与 L2 误差指标；`code/prepare_cst_true_nearfield_workpack.py` 已写入 162/32/120 三档 CST 复跑队列；`code/derive_true_nearfield_layout_exports.py` 可从 162 点真 monitor 导出派生 32/120 CSV；`code/run_true_nearfield_gate.py` 可刷新 `data/cst_true_nearfield_workpack/gate_report/`，记录当前 18 条队列项的源文件、派生和比较 gate 状态。
51. Huygens 面源 field-model/平滑正则诊断：`code/run_cst_huygens_baseline.py` 现在对比 `radiating_dipole` 与 `current_green`，并默认扫描 `smooth_lambda = 0, 1e-6, 1e-4, 1e-2`，结果写入 `data/sampling_layouts/cst_level1_huygens_baseline/`；当前最佳仍为 `diagnostic_only`，不能作为少测点最终证明。
52. CST 真近场 post-export 决策入口：`code/run_true_nearfield_workflow_decision.py` 汇总 handoff、dropzone、gate 和 G3 dashboard，输出 `outputs/cst_true_nearfield_workflow_decision/`；当前决策是等待两个 required `full_grid_162` 真 monitor CSV，再跑 required gate。
53. GitHub 协作入口：`.github/ISSUE_TEMPLATE/` 已补齐 CST、算法、文档和 bug 四类 issue 模板，`CONTRIBUTING.md` 明确了分支、提交、大文件、true-monitor 校验和结论口径规则，便于队友按统一格式推进任务。
54. G2 采样候选决策矩阵：`code/build_sampling_decision_matrix.py` 输出 `data/sampling_layouts/sampling_decision_matrix/`，把 `full_grid_162` 定为物理参考锚点，`geometric_farthest_32` 定为第一 reduced-layout true-monitor 复跑优先项，`fibonacci_snap_120` 定为保守 120 点交叉验证，`task_driven_32/48` 定为分类压力测试探针。
55. G5 识别鲁棒性压力测试：`code/run_cst_recognition_stress_test.py` 输出 `data/recognition_stress_tests/level2_robustness/`，在 clean-train/perturbed-test 设置下验证噪声、相位抖动和通道缺失；当前单因素扰动基本保持 `1.000`，但组合扰动会低于 `0.85`，需要作为分类泛化边界写入报告口径。
56. G5 扰动增强训练对照：`code/run_cst_recognition_augmented_stress_test.py` 输出 `data/recognition_stress_tests/level2_augmented_robustness/`，在同一 held-out 压力测试上加入已知噪声、相位、缺测和组合扰动增强训练；当前 5 个布局 × 8 个压力场景共 40 行均恢复到 accuracy=`1.000`，可作为已知测量误差族可校准的证据，但不能替代 full-wave 复杂载体验证。
57. G5 未见误差族外推验证：`code/run_cst_recognition_leave_one_family_out.py` 输出 `data/recognition_stress_tests/level2_leave_one_family_out/`，逐类留出 `noise/phase/dropout/combined` 扰动族后再测试；当前 35 行全部高于 `0.85`，但 held-out `dropout_25pct` 在 `geometric_farthest_32` 与 `task_driven_48` 上约为 `0.867`，说明缺测/掉通道仍是最窄裕度。
58. G5 多随机种子稳定性验证：`code/run_cst_recognition_seed_stability.py` 输出 `data/recognition_stress_tests/level2_seed_stability/`，对 held-out `noise/dropout` 做 3 个随机种子重复；当前 60 行全部高于 `0.85`，最窄项仍是 `geometric_farthest_32/dropout/dropout_25pct`，mean accuracy 约 `0.933`、min accuracy 约 `0.867`、裁剪后近似 95% CI 为 `[0.768, 1.000]`。
59. G5 缺测通道缓解验证：`code/run_cst_recognition_dropout_mitigation.py` 输出 `data/recognition_stress_tests/level2_dropout_mitigation/`，在两个最紧 dropout 布局上比较 zero-fill、mask 特征和 frequency/sensor median imputation；当前 48 行全部高于 `0.85`，插补策略将 `geometric_farthest_32/dropout_25pct` 聚合结果从 mean `0.956`、min `0.867` 提升到 mean/min `1.000`。
60. G5 缺测通道扩展验证：同一脚本输出 `data/recognition_stress_tests/level2_dropout_mitigation_extended/`，把比较扩展到 5 个 G2 代表布局和 held-out `dropout/combined` 两类含缺测压力；当前 180 行全部高于 `0.85`，zero-fill 最小 `0.867`，mask-only 最小 `0.867` 且个别聚合行会弱于 zero-fill，frequency/sensor median imputation 与 imputation+mask 均达到 mean/min `1.000`。
61. G5 结构化缺测验证：`code/run_cst_recognition_structured_dropout.py` 输出 `data/recognition_stress_tests/level2_structured_dropout/`，在已知扰动增强训练后测试 sensor-node dropout、polarization-pair dropout 和 60 deg azimuth-sector dropout；当前 240 行全部高于 `0.85`，最低 accuracy=`0.933`，frequency/sensor median imputation 两种策略 mean/min 均为 `1.000`。
62. G5 仪器相关误差验证：`code/run_cst_recognition_instrument_error.py` 输出 `data/recognition_stress_tests/level2_instrument_error/`，测试全局增益漂移、传感器增益偏置、频率响应斜率、极化增益不平衡和混合幅相偏置；当前 150 行全部高于 `0.85`，最低 accuracy=`0.933`，最紧项为 `geometric_farthest_32/sensor_gain_bias_3db`。

## 如何阅读本项目

建议顺序：

1. 先看 `docs/project_workflow.md`，了解采样方案、CST/Python 数据接口、算法反演外推和分类识别如何串成闭环。
2. 再看 `docs/future_engineering_plan.md`，了解结合导师 DeepSeek 记录和新增文献后的下一阶段工程方案。
3. 然后看 `docs/current_work_detailed_explanation.md`，它按推进过程讲清技术路线、CST 建模、产物文件和代码职责。
4. 再看 `docs/project_progress_report.md`，快速了解当前做了什么、产物是什么和下一步；导师阅读门户见 `docs/progress_reports/mentor_portal.md`，组会汇报稿见 `docs/progress_reports/meeting_brief.md`，每日进展汇总见 `docs/progress_reports/daily_digest.md`，导师证据映射见 `docs/progress_reports/evidence_map.md`，导师决策清单见 `docs/progress_reports/decision_brief.md`，导师问答卡见 `docs/progress_reports/mentor_qa.md`，G5 关闭路线见 `docs/progress_reports/g5_closure_brief.md`，导师 30 秒快照见 `docs/progress_reports/mentor_snapshot.md`，本次变化说明见 `docs/progress_reports/latest_change_note.md`，下一步行动清单见 `docs/progress_reports/next_action_brief.md`，风险登记表见 `docs/progress_reports/risk_register.md`，提交就绪清单见 `docs/progress_reports/submission_readiness.md`，阶段时间线见 `docs/progress_reports/progress_index.md`，导师最新版固定入口见 `docs/progress_reports/latest_mentor_brief.md`，巡检范围见 `docs/progress_reports/watch_scope.md`，跟进操作规程见 `docs/progress_reports/progress_update_protocol.md`，状态复核台账见 `docs/progress_reports/status_review_log.md`，历史归档见 `docs/progress_reports/`。
5. 再看 `docs/project_file_index.md`，了解文件夹和主线产物。
6. 若要看三人分工、分工细节和技术路线，直接看 `docs/team_division_technical_route.md`。
7. 再看 `docs/stage_notes/README.md`，按阶段理解做了什么、为什么做、产物有哪些。
8. 若要对照赛题原文要求，查看 `outputs/problem_requirements/problem_requirements_matrix.md`。
9. 若要继续 CST 工作，直接看 `outputs/cst_level1_workpack/README_level1_workpack.md` 和 `outputs/cst_level2_workpack/README_level2_workpack.md`。
10. 若要减少 CST 批量建模/导出操作错误，查看 `outputs/cst_macro_templates/README_cst_macro_templates.md`。
11. 若要立刻执行真实 CST required 标准源，先看 `docs/stage_notes/17_cst_solver_safe_level1_export.md`，再看 `outputs/cst_execution_dashboard/cst_execution_dashboard.md`。
12. 若要直接打开本机 CST 已生成工程，查看 `outputs/cst_real_level1_projects/README_cst_level1_automation.md`、`outputs/cst_solver_ready_level1_projects` 和 `outputs/cst_solver_trials`。
13. 若要查看 Level 2 48 样本结果，先看 `docs/stage_notes/19_cst_level2_full48_recognition.md`，再看 `outputs/cst_level2_superposed_export`、`outputs/cst_level2_merge_report`、`outputs/cst_recognition_level2` 和 `outputs/cst_recognition_level2_ablation`。
14. 若要查看 Level 1 角域校准结果，查看 `outputs/cst_level1_angular_calibration/README_cst_level1_angular_calibration.md`。
15. 若要查看 Level 2 简化结构遮挡对照，查看 `outputs/cst_structure_comparison/README_cst_structure_comparison.md` 和 `docs/stage_notes/22_structure_occlusion_comparison.md`。
16. 若要理解 G5 报告/PPT/视频材料口径刷新，查看 `docs/stage_notes/20_g5_report_material_refresh.md`。
17. 若要查看正式报告与答辩 PPT 导出过程，查看 `docs/stage_notes/23_final_report_ppt_export.md`。
18. 若要查看演示视频导出过程，查看 `docs/stage_notes/24_demo_video_export.md`。
19. 若要查看最终压缩包与校验清单，查看 `docs/stage_notes/25_final_archive.md` 和 `outputs/final_archive/final_archive_summary.json`。
20. 若要查看本轮详细讲解文档的生成和归档说明，查看 `docs/stage_notes/26_current_work_explanation.md`。
21. 若要推进报告成稿，查看 `outputs/report_package/README_report_package.md`。
22. 若要推进答辩 PPT/视频，查看 `outputs/presentation_package/README_presentation_package.md`。
23. 若要记录真实 CST 执行，使用 `outputs/cst_execution_logs/README_cst_execution_logs.md`。
24. 若要判断当前总状态和三人下一步分工，先看 `outputs/master_dashboard/master_status_dashboard.md`。
25. 若要判断是否能交付，查看 `outputs/completion_audit/completion_audit.md`。
26. 若要推进真近场 monitor 复跑，先看 `docs/true_nearfield_monitor_workflow.md`，再运行 `python code\run_true_nearfield_gate.py` 查看 `data/cst_true_nearfield_workpack/gate_report/`。
27. 若要判断 CST 真 monitor 回填后下一步，运行 `python code\run_true_nearfield_workflow_decision.py`，再看 `outputs/cst_true_nearfield_workflow_decision/true_nearfield_workflow_decision.md`。
28. 若要查看 G5 分类鲁棒性边界、增强训练修复效果、未见误差族外推能力、种子稳定性、缺测缓解策略、结构化缺测压力和仪器相关误差压力，依次看 `data/recognition_stress_tests/level2_robustness/`、`data/recognition_stress_tests/level2_augmented_robustness/`、`data/recognition_stress_tests/level2_leave_one_family_out/`、`data/recognition_stress_tests/level2_seed_stability/`、`data/recognition_stress_tests/level2_dropout_mitigation/`、`data/recognition_stress_tests/level2_dropout_mitigation_extended/`、`data/recognition_stress_tests/level2_structured_dropout/` 与 `data/recognition_stress_tests/level2_instrument_error/`。

## Baseline 运行方式

```powershell
python code\run_baseline.py
```

输出目录：

```text
outputs/baseline
```

核心输出：

| 文件 | 用途 |
|---|---|
| `sensor_layout_hemisphere.csv` | 2π 半球面测点坐标与极化字段，可对齐 CST 导出 |
| `sensor_layout_hemisphere.png` | 测点布局与 12m x 10m x 8m 被测包络示意 |
| `reconstruction_metrics.csv` | 全测点、随机稀疏、优化稀疏的重建误差指标 |
| `farfield_comparison_full_100.png` | 全测点远场重建对比 |
| `farfield_comparison_optimized_50.png` | 50% 优化测点远场重建对比 |
| `sampling_tradeoff.png` | 测点数量与重建精度关系 |
| `recognition_metrics.json` | 空-频-极化特征识别指标 |
| `recognition_confusion_matrix.png` | 识别混淆矩阵 |
| `score_evidence.md` | 当前 baseline 对评分项的证据摘要 |

## 当前 baseline 指标

最近一次运行结果：

- 半球面空间测点：162 个。
- 单频双极化测量通道：324 个。
- 50% 优化测点：81 个空间点，162 个测量通道。
- 50% 优化测点重建：NMSE 约 `8.36e-4`，方向图相关系数约 `0.9986`。
- 识别基线：SVM，合成多源状态数据准确率 `1.000`。

这些数值只证明算法链路和指标计算可运行，不能替代 CST 仿真验证。当前真实/本机 CST 证据已进入 Level 1 required 与 Level 2 full48；baseline 仍保留为算法接口和测点压缩参考，不再作为最终指标主证据。

## 重建鲁棒性扫描

在真实 CST 标准源数据到来前，先用合成三源参考场扫描噪声、测点比例和 Tikhonov 正则化参数：

```powershell
python code\run_reconstruction_robustness.py
```

输出目录：

```text
outputs/reconstruction_robustness
```

核心输出：

| 文件 | 用途 |
|---|---|
| `reconstruction_robustness_raw.csv` | 每次 trial/case/SNR/lambda 的完整指标 |
| `reconstruction_robustness_summary.csv` | 按 case/SNR/lambda 聚合的均值和标准差 |
| `reconstruction_robustness_best.csv` | 每个 case/SNR 下最佳 lambda |
| `reconstruction_noise_robustness.png` | 噪声鲁棒性曲线 |
| `reconstruction_sensor_tradeoff_30dB.png` | 30 dB 下测点数与重建精度关系 |
| `reconstruction_lambda_scan_optimized50_30dB.png` | 50% 优化测点的正则化参数扫描 |
| `reconstruction_robustness_evidence.md` | 可写入报告的摘要 |

30 dB SNR 下当前合成结果：

| Case | 测点 | 通道 | 最佳 lambda | NMSE | 相关系数 | 主瓣误差 |
|---|---:|---:|---:|---:|---:|---:|
| full_100 | 162 | 324 | `1e-2` | `5.32e-4` | `0.99882` | `0.00 deg` |
| optimized_75 | 122 | 244 | `1e-3` | `1.13e-3` | `0.99834` | `0.00 deg` |
| optimized_50 | 81 | 162 | `1e-6` | `2.07e-3` | `0.99595` | `25.81 deg` |
| optimized_25 | 40 | 80 | `1e-6` | `2.36e-1` | `0.57621` | `33.42 deg` |

这说明合成条件下 75% 测点更稳，50% 测点虽然方向图相关性较高但主瓣定位仍需结合真实 CST 数据复核；25% 测点暂不作为主方案。

## 评分证据板

汇总当前评分项证据、关键指标和最终缺口：

```powershell
python code\build_scorecard.py
```

输出目录：

```text
outputs/scorecard
```

核心文件：

| 文件 | 用途 |
|---|---|
| `scorecard.md` | 面向报告/PPT 集成的评分项证据板 |
| `score_items.csv` | 每个评分项的状态、证据、缺口和下一步 |
| `scorecard_metrics.json` | 从现有输出自动读取的关键指标 |

当前 scorecard 判断：文献调研为 draft evidence；Level 1 required、Level 2 48 样本和简化结构遮挡已有 CST-derived/边界证据；识别 accuracy 达到 `1.000`，简化结构 cross-domain accuracy 达到 `1.000`；但 Level 1 近场等效源模型边界、full-wave airframe 边界和最终报告/PPT/视频仍未完成。

## 代码包复现材料

最终代码包需要的依赖、复现命令和数据字段说明已经单独整理：

| 文件 | 用途 |
|---|---|
| `requirements.txt` | Python 依赖清单 |
| `docs/reproduce_commands.md` | 从环境安装到 baseline、CST demo、真实 CST 接入、scorecard 的命令清单 |
| `docs/data_dictionary.md` | nearfield、farfield、labels、manifest、指标表字段说明 |

提交打包前，`docs/reproduce_commands.md` 中的真实 CST 路径需要用最终数据路径复核一次。

## 最终提交包索引

生成报告、PPT、视频、代码、CST 和数据提交物的当前状态表：

```powershell
python code\build_submission_index.py
```

输出目录：

```text
outputs/submission_index
```

核心文件：

| 文件 | 用途 |
|---|---|
| `submission_package_index.md` | 最终提交包结构、当前状态和打包门槛 |
| `submission_checklist.csv` | 每个提交物的期望路径、当前来源、状态和 blocker |
| `submission_index_summary.json` | ready/draft/blocked 数量汇总 |

提交材料结构和 PPT/视频大纲见：`docs/final_submission_package_plan.md`

生成报告成稿素材包：

```powershell
python code\build_report_package.py
```

输出目录：

```text
outputs/report_package
```

生成答辩 PPT 与演示视频素材包：

```powershell
python code\build_presentation_package.py
```

输出目录：

```text
outputs/presentation_package
```

生成当前提交草稿包：

```powershell
python code\build_submission_draft.py
```

草稿包输出目录：

```text
submission
```

该目录用于提前固定最终材料结构，当前不是最终提交包；真实 CST 工程、真实导出、最终 PDF/DOCX/PPTX/MP4 仍需补齐。

## CST Level 1 模板与校验

生成 CST 标准源阶段需要的测点、近场、远场模板：

```powershell
python code\prepare_cst_templates.py
```

输出目录：

```text
outputs/cst_templates
```

核心文件：

| 文件 | 用途 |
|---|---|
| `sensor_layout_hemisphere_for_cst.csv` | CST 中应使用的 13 m 半球面 162 个测点坐标 |
| `nearfield_import_template.csv` | 近场 Ex/Ey/Ez 复数数据导出模板，需用 CST 结果填充 |
| `farfield_truth_template.csv` | 远场 Etheta/Ephi 或 gain 真值模板，需用 CST 结果填充 |
| `nearfield_demo_valid.csv` | 合成样例，仅用于测试 Python 接口 |
| `farfield_demo_valid.csv` | 合成样例，仅用于测试 Python 接口 |
| `demo_validation_report.json` | 合成样例的校验结果 |

生成 Level 1 标准源执行清单：

```powershell
python code\prepare_cst_level1_manifest.py
```

输出目录：

```text
outputs/cst_level1_plan
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level1_case_manifest.csv` | 6 个标准源案例的工程名、导出文件名、预期行数 |
| `level1_source_manifest.csv` | 源位置、方向、长度、馈电间隙和求解器备注 |
| `level1_validation_targets.csv` | 相关系数、主瓣误差、NMSE 通过门槛 |
| `README_level1_manifest.md` | CST 主责交接说明 |

必做案例：`L1_short_dipole_z_1p2G`、`L1_halfwave_dipole_z_1p2G`。建议再做短偶极子 x/y 方向，用于检查坐标轴和极化约定。

导出文件放入 `data/cst_exports/level1/` 后，批量审计 Level 1 完整性：

```powershell
python code\merge_cst_level1_exports.py
```

输出目录：

```text
outputs/cst_level1_merge_report
```

关键报告：

| 文件 | 用途 |
|---|---|
| `level1_case_status.csv` | 每个标准源案例的文件存在性、行数、校验状态和缺口 |
| `level1_reconstruction_queue.csv` | 已完整案例的重建命令队列 |
| `level1_merge_summary.json` | 必做/建议/可选案例完成度和严格验收状态 |

必做案例齐全后运行：

```powershell
python code\merge_cst_level1_exports.py --strict
```

审计通过后，批量执行已完整标准源案例的重建：

```powershell
python code\run_cst_level1_batch_reconstruction.py
```

若只想生成待执行命令队列：

```powershell
python code\run_cst_level1_batch_reconstruction.py --dry-run
```

输出目录：

```text
outputs/cst_level1_reconstruction_batch
outputs/cst_reconstruction\<sample_id>
```

生成给 CST 主责的 Level 1 建模任务包：

```powershell
python code\prepare_cst_level1_workpack.py
```

输出目录：

```text
outputs/cst_level1_workpack
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level1_cst_work_items.csv` | 每个标准源案例的源端点、monitor、导出路径、验收门槛 |
| `level1_cst_export_checklist.csv` | 工程、导出、审计、重建、截图逐项核对表 |
| `case_cards/<sample_id>.md` | 可直接交给 CST 主责的单案例任务卡 |
| `README_level1_workpack.md` | 任务包使用说明 |

为提前验证非空批处理链路，可生成 manifest 同形的合成 Level 1 数据：

```powershell
python code\generate_synthetic_cst_level1_dataset.py
python code\merge_cst_level1_exports.py --manifest outputs\synthetic_cst_level1_dataset\level1_case_manifest.csv --report-dir outputs\synthetic_cst_level1_dataset\merge_report --out-dir outputs\synthetic_cst_level1_dataset\merged --strict-all
python code\check_cst_export.py --nearfield outputs\synthetic_cst_level1_dataset\merged\all_nearfield.csv --farfield outputs\synthetic_cst_level1_dataset\merged\all_farfield.csv --json-out outputs\synthetic_cst_level1_dataset\validation_report.json
python code\run_cst_level1_batch_reconstruction.py --case-status outputs\synthetic_cst_level1_dataset\merge_report\level1_case_status.csv --out-root outputs\synthetic_cst_level1_dataset\reconstruction --batch-dir outputs\synthetic_cst_level1_dataset\reconstruction_batch --priority all --require-cases
```

该闭环当前完成 6 个合成标准源案例，最大 NMSE 约 `4.6e-6`，最小相关系数约 `0.999996`。它只验证接口、manifest、审计和批量重建流程，不能替代真实 CST 全波仿真结果。

生成 Level 1 标准源解析方向图 sanity reference：

```powershell
python code\build_level1_analytic_reference.py
```

输出目录：

```text
outputs/level1_analytic_reference
```

该目录给出短偶极子/半波振子的解析归一化方向图，用于真实 CST 导出后的坐标轴、极化和主瓣 sanity check，不能替代 `merge_cst_level1_exports.py --strict` 和批量重建验收。

校验 CST 导出的近场/远场文件：

```powershell
python code\check_cst_export.py --nearfield path\to\nearfield.csv --farfield path\to\farfield.csv
```

已验证 demo 样例：

```powershell
python code\check_cst_export.py --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv
```

若 CST 导出为幅值/相位而不是实部/虚部，先转换：

```powershell
python code\normalize_cst_complex_columns.py --nearfield path\to\nearfield_phase.csv --farfield path\to\farfield_phase.csv --nearfield-out path\to\nearfield.csv --farfield-out path\to\farfield.csv --phase-unit deg
```

已用 demo 数据验证幅相转换闭环：

```powershell
python code\normalize_cst_complex_columns.py --make-phase-demo --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv --out-dir outputs\cst_phase_demo
python code\run_cst_reconstruction.py --nearfield outputs\cst_phase_demo\normalized_nearfield.csv --farfield outputs\cst_phase_demo\normalized_farfield.csv --out-dir outputs\cst_phase_demo\reconstruction
```

## CST 数据重建闭环

真实 CST 数据导出并校验通过后，运行：

```powershell
python code\run_cst_reconstruction.py --nearfield path\to\nearfield.csv --farfield path\to\farfield.csv --out-dir outputs\cst_reconstruction\case_name
```

当前已用合成 demo 文件跑通完整管线：

```powershell
python code\run_cst_reconstruction.py --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv --out-dir outputs\cst_reconstruction_demo
```

demo 输出：

| 文件 | 用途 |
|---|---|
| `outputs/cst_reconstruction_demo/cst_reconstruction_metrics.json` | 重建指标 |
| `outputs/cst_reconstruction_demo/cst_farfield_reconstruction_compare.png` | 真值、重建和误差对比 |
| `outputs/cst_reconstruction_demo/equivalent_source_solution.csv` | 等效源解 |

demo 指标：

- NMSE：约 `1.26e-6`
- 方向图相关系数：约 `0.999999`
- 主瓣误差：`0 deg`

真实 CST 接入步骤见：`docs/phase_02_cst_data_integration_plan.md`

## CST 格式多状态识别闭环

真实 CST 多源/多状态数据尚未导出前，可先用合成偶极源生成与 CST 导出字段一致的数据集，验证识别接口和指标统计：

```powershell
python code\generate_synthetic_cst_dataset.py
python code\check_cst_export.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --farfield outputs\synthetic_cst_dataset\farfield_multistate.csv --json-out outputs\synthetic_cst_dataset\validation_report.json
python code\run_cst_recognition.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_demo
```

当前 demo 数据规模：

- 样本：4 类 x 24 个 = 96 个。
- 频点：0.90、1.05、1.20、1.35、1.50 GHz。
- 测点：13 m 半球面 162 个点。
- nearfield：Ex/Ey/Ez 复数场，233280 行。
- farfield：Etheta/Ephi 复数场与 gain_db，328320 行。

识别输出：

| 文件 | 用途 |
|---|---|
| `outputs/cst_recognition_demo/cst_recognition_metrics.json` | 识别指标、特征维度、nearfield 校验摘要 |
| `outputs/cst_recognition_demo/cst_recognition_confusion_matrix.png` | 识别混淆矩阵 |
| `outputs/cst_recognition_demo/cst_recognition_classification_report.csv` | precision/recall/F1 |
| `outputs/cst_recognition_demo/cst_recognition_predictions.csv` | 测试集逐样本预测 |

当前合成 CST 格式 demo 结果：

- 特征矩阵：96 个样本 x 4965 维。
- 最优模型：SVM RBF。
- 测试集准确率：`1.000`。
- 说明：该结果只证明 CST 表格接口、Ex/Ey/Ez 到 theta/phi 投影、特征提取和识别评分链路可运行；正式证据仍需替换为 CST 多源/载体仿真导出。

## CST Level 2 多源多状态计划

生成队内 CST 执行清单：

```powershell
python code\prepare_cst_level2_manifest.py
```

输出目录：

```text
outputs/cst_level2_plan
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level2_case_manifest.csv` | 48 个 sample_id、5 个频点，共 240 个 CST 样本-频点任务 |
| `level2_source_manifest.csv` | 120 条源位置、方向、相对幅度、相对相位配置 |
| `level2_labels.csv` | 后续真实 CST 识别训练标签 |
| `README_level2_manifest.md` | CST 主责交接说明 |

技术规程见：`docs/phase_03_cst_level2_multisource_recognition_protocol.md`

生成半球面 CST 建模任务包：

```powershell
python code\prepare_cst_level2_workpack.py
```

输出目录：

```text
outputs/cst_level2_workpack
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level2_cst_sample_work_items.csv` | 48 个 CST sample/project 的汇总任务 |
| `level2_cst_frequency_tasks.csv` | 240 个 sample-frequency monitor/export 任务 |
| `level2_cst_export_checklist.csv` | 工程、源、导出、审计、截图核对表 |
| `level2_class_summary.csv` | 4 类识别状态的样本数、源数和频点汇总 |
| `case_cards/<sample_id>.md` | 单 sample CST 任务卡 |

## CST 宏模板与 pilot 队列

生成 Level 1/Level 2 的 CST 宏输入表、VBA 骨架和 pilot 队列：

```powershell
python code\prepare_cst_macro_templates.py
```

输出目录：

```text
outputs/cst_macro_templates
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level1_macro_parameters.csv` | Level 1 标准源宏输入参数 |
| `level1_required_launch_order.csv` | G2 必做标准源执行顺序 |
| `level2_macro_sample_parameters.csv` | Level 2 每个样本的频点和导出路径 |
| `level2_macro_source_parameters.csv` | Level 2 每个源的坐标、方向、幅度和相位 |
| `level2_pilot_cases.csv` | 每个类别 1 个 pilot 样本 |
| `cst_macro_execution_checklist.csv` | 宏执行和证据清单 |
| `*.bas` | CST VBA 宏骨架，需按本机 CST 版本适配具体 API |

这些文件是 CST 执行辅助材料，不是仿真结果证据。

## CST Level 2 element-library full48

为避免全尺寸 Level 2 空域直接求解导致网格过大，当前采用 solver-safe 的 element-library 路线：CST 求解 x/y/z 三个短偶极子 element 的 5 个频点 FarfieldPlot，Python 再按 Level 2 source manifest 的位置、方向、幅度和相位做线性叠加，生成 48 个 sample-level nearfield/farfield CSV。

生成或刷新三方向 element 工程清单：

```powershell
python code\run_cst_level2_element_library.py --out-dir outputs\cst_level2_element_library --axes x,y,z --timeout-seconds 900
```

三个已求解 element 工程和日志位于：

```text
outputs/cst_level2_element_trials
```

导出缺失样本批处理命令：

```powershell
python code\export_cst_level2_superposed_results.py --all-samples --missing-only --summary-out outputs\cst_level2_superposed_export\level2_remaining_missing_batch_summary.json --stdout-log outputs\cst_level2_superposed_export\level2_remaining_missing_batch_stdout.log --timeout-seconds 7200
```

当前 full48 状态：

- 完整样本：48/48。
- 合并 nearfield：116640 行。
- 合并 farfield：164160 行。
- full48 识别：`outputs/cst_recognition_level2`，48 samples × 4965 features，SVM accuracy=`1.000`。
- full48 消融：`outputs/cst_recognition_level2_ablation`，5/3/1 频点与 100/75/50/25% 测点组合均为 `1.000`。

注意：这属于 CST-derived element-library 全量样本，不是最终 full-wave 复杂载体结构证据；当前已通过 `code/run_cst_structure_comparison.py` 补充 simplified aircraft occlusion transfer 对照，用于量化结构/安装效应边界。

## CST Level 2 简化结构遮挡对照

在 Level 2 full48 基础上运行：

```powershell
python code\run_cst_structure_comparison.py
```

输出目录：

```text
outputs/cst_structure_comparison
```

核心结果：

- 样本：48 个，样本-频点：240 个。
- mean shadow：约 `3.06 dB`。
- P95 shadow：约 `6.63 dB`。
- max shadow：约 `13.33 dB`。
- mean pattern correlation：约 `0.730`。
- cross-domain recognition accuracy：`1.000`。

说明：该结果是 simplified aircraft occlusion transfer on CST-derived Level 2 element-library fields，不是 full-wave CST airframe scattering。它用于报告/PPT 中说明 element-library 识别结论在结构遮挡扰动下的边界和稳健性。

## CST 执行 dashboard

生成当前真实 CST 执行状态、G2 required action sheet、G3 pilot action sheet 和真实数据 dropzone 说明：

```powershell
python code\build_cst_execution_dashboard.py
```

输出目录：

```text
outputs/cst_execution_dashboard
data/cst_exports
```

核心文件：

| 文件 | 用途 |
|---|---|
| `outputs/cst_execution_dashboard/cst_execution_dashboard.md` | 当前 G2/G3 状态和下一步命令 |
| `outputs/cst_execution_dashboard/level1_required_action_sheet.csv` | 两个 Level 1 required 标准源执行表 |
| `outputs/cst_execution_dashboard/level2_pilot_action_sheet.csv` | 每类 1 个 Level 2 pilot 样本 |
| `outputs/cst_execution_dashboard/missing_real_cst_files.csv` | 当前真实 CST 缺失文件清单 |
| `data/cst_exports/README_cst_exports.md` | 真实 CST 导出 dropzone 规则 |

## CST Level 2 批量导出合并

当 CST 主责按 `outputs/cst_level2_plan` 导出每个 sample_id 的 nearfield/farfield 后，运行：

```powershell
python code\merge_cst_level2_exports.py
```

输出缺漏报告：

| 文件 | 用途 |
|---|---|
| `outputs/cst_level2_merge_report/level2_sample_status.csv` | 每个 sample_id 的文件存在性、校验状态和完整性 |
| `outputs/cst_level2_merge_report/level2_frequency_completeness.csv` | 每个 sample_id/频点的 nearfield/farfield 行数检查 |
| `outputs/cst_level2_merge_report/level2_merge_summary.json` | 总体完成度和后续命令 |

真实导出齐全后，该脚本会生成：

```text
data/cst_exports/level2/all_nearfield.csv
data/cst_exports/level2/all_farfield.csv
```

正式验收时使用严格模式：

```powershell
python code\merge_cst_level2_exports.py --strict
```

当前已通过 CST element-library full48 导出 48 个完整样本；`merge_cst_level2_exports.py --strict` 通过，`level2_merge_summary.json` 中 `all_complete=true`。

## CST 格式识别删减验证

在合成 CST 格式数据上验证测点和频点删减后的识别链路：

```powershell
python code\run_cst_recognition_ablation.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_ablation
```

输出：

| 文件 | 用途 |
|---|---|
| `outputs/cst_recognition_ablation/recognition_ablation_metrics.csv` | 不同测点/频点组合的准确率和 F1 |
| `outputs/cst_recognition_ablation/recognition_ablation_accuracy.png` | 准确率柱状图和 85% 阈值线 |
| `outputs/cst_recognition_ablation/recognition_ablation_summary.json` | 完整模型报告 |

当前合成 demo 下，100%、75%、50%、25% 测点和 5/3/1 频点组合均达到 `1.000` 准确率。当前 48 样本 CST-derived full48 下，5/3/1 频点与 100/75/50/25% 测点组合均为 `1.000`。这些结果说明接口和特征体系已可运行；正式结论仍需结构散射/遮挡对照增强。

## 后续小目标

1. 把 Level 1 角域校准与 full-wave 近场模型边界写入最终报告/PPT。
2. 把 Level 2 full48 与简化结构遮挡对照写入最终报告/PPT，明确区分 CST-derived element-library、simplified occlusion transfer 和 full-wave airframe scattering。
3. 若时间允许，再在 CST 中补充 full-wave airframe 结构散射对照；若不补，则在最终稿中作为后续增强项说明。
4. 人工完整播放 `submission/03_video/demo_video.mp4`；若竞赛要求讲解录屏，替换为带人工讲解或可听旁白的版本。
5. 如替换视频或改报名信息，重跑 `build_submission_draft.py`、`build_final_archive.py`、`build_completion_audit.py`，确认 `completion_proven=true` 且 zip hash 更新。
6. 运行 `build_progress_report.py` 标记阶段进展并生成导师汇报，导师阅读门户为 `docs/progress_reports/mentor_portal.md`，组会汇报稿为 `docs/progress_reports/meeting_brief.md`，每日进展汇总为 `docs/progress_reports/daily_digest.md`，导师证据映射为 `docs/progress_reports/evidence_map.md`，导师决策清单为 `docs/progress_reports/decision_brief.md`，导师问答卡为 `docs/progress_reports/mentor_qa.md`，G5 关闭路线为 `docs/progress_reports/g5_closure_brief.md`，导师 30 秒快照为 `docs/progress_reports/mentor_snapshot.md`，本次变化说明为 `docs/progress_reports/latest_change_note.md`，下一步行动清单为 `docs/progress_reports/next_action_brief.md`，风险登记表为 `docs/progress_reports/risk_register.md`，提交就绪清单为 `docs/progress_reports/submission_readiness.md`，阶段时间线为 `docs/progress_reports/progress_index.md`，最新版固定入口为 `docs/progress_reports/latest_mentor_brief.md`，关键文件监测范围见 `docs/progress_reports/watch_scope.md`，跟进操作规程见 `docs/progress_reports/progress_update_protocol.md`，状态复核台账见 `docs/progress_reports/status_review_log.md`。
7. 运行 `build_submission_draft.py` 重新生成最终草稿包，再按审核结果导出正式提交件。
8. 运行 `python code\build_g3_model_dashboard.py` 刷新 `outputs/g3_model_dashboard/`，用 `model_comparison.md` 和 `g3_next_actions.csv` 统一 G3 源模型、SWE、Huygens 与真近场 monitor gate 的当前结论和队友分工。
9. 运行 `python code\build_true_nearfield_handoff.py` 刷新 `outputs/cst_true_nearfield_handoff/`，把 CST 真近场 monitor 的两个 required full-grid CSV、486 行验收标准和后续算法命令交给 CST 主责执行。
10. CST 文件回填后，先运行 `python code\check_true_nearfield_dropzone.py --required-only --full-grid-only` 预检列名、行数、组件和 sensor 子集，再运行 `run_true_nearfield_gate.py`。
11. 运行 `python code\run_true_nearfield_workflow_decision.py` 刷新 `outputs/cst_true_nearfield_workflow_decision/`，用 `true_nearfield_workflow_decision.md` 判断下一步是继续等 CST、跑 required gate、复跑 G3 physical baseline，还是刷新报告口径。
12. 运行 `python code\build_sampling_decision_matrix.py` 刷新 `data/sampling_layouts/sampling_decision_matrix/`，用矩阵安排 reduced-layout 真 monitor 复跑和分类压力测试；该矩阵仍是计划依据，不是 final vector/Huygens 证明。
13. 运行 `python code\run_cst_recognition_stress_test.py` 刷新 `data/recognition_stress_tests/level2_robustness/`，若组合扰动仍低于 `0.85`，下一步应加入噪声/相位/缺测增强训练或 error-aware 特征，而不是直接宣称复杂误差下识别稳健。
14. 运行 `python code\run_cst_recognition_augmented_stress_test.py` 刷新 `data/recognition_stress_tests/level2_augmented_robustness/`；若扰动 profile、随机种子或 Level 2 样本库变化，应同时复跑 clean-train 与 augmented 两个脚本，并在最终报告中区分“已知扰动增强有效”和“未知误差仍需外推验证”。
15. 运行 `python code\run_cst_recognition_leave_one_family_out.py` 刷新 `data/recognition_stress_tests/level2_leave_one_family_out/`；若 held-out dropout 仍是最窄裕度，下一步可做多随机种子置信区间、dropout-aware 特征或传感器缺测插补策略。
16. 运行 `python code\run_cst_recognition_seed_stability.py` 刷新 `data/recognition_stress_tests/level2_seed_stability/`；若 `geometric_farthest_32/dropout_25pct` 的下界仍偏窄，下一步优先做 dropout-aware 特征、缺测插补或测点冗余备份策略。
17. 运行 `python code\run_cst_recognition_dropout_mitigation.py` 刷新 `data/recognition_stress_tests/level2_dropout_mitigation/`；若插补仍优于 zero-fill，可在 G5 报告中将 frequency/sensor median imputation 写成缺测通道预处理候选。
18. 若要复核五布局和含缺测组合扰动，运行 `python code\run_cst_recognition_dropout_mitigation.py --layout-candidates full_grid_162,geometric_farthest_32,fibonacci_snap_120,task_driven_32,task_driven_48 --held-out-families dropout,combined --out-dir data\recognition_stress_tests\level2_dropout_mitigation_extended`；下一步仍应使用真实 monitor、相关传感器缺测或 full-wave airframe 数据复核该预处理策略。
