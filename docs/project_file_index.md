# 项目文件索引

本索引用来回答“每个文件夹放什么、从哪里开始看、哪些文件是主线证据”。本轮已经把根目录散落的 PDF/DOCX 和早期工作计划脚本归档，并将主源码入口调整为 `code/`。CST 大型求解缓存和自动生成结果仍保留在既有 `outputs/`/`submission/` 路径中，通过索引和 `.gitignore` 管理，避免破坏已形成的审计和复现链。

## 顶层目录

| 路径 | 内容 | 阅读/使用建议 |
|---|---|---|
| `README.md` | 项目总入口、当前路线和常用命令 | 首先阅读 |
| `code` | Python 脚本：算法、CST 接口、manifest、workpack、审计；`legacy_workplan/` 保留早期工作计划脚本 | 运行和复现 |
| `CST` | CST 建模与自动化工作流入口索引 | 查找 CST 模板、工程、导出和 Python 调 CST 流程 |
| `docs` | 文献、技术路线、规程、数据字典、报告草稿、阶段说明、当前工作讲解 | 理解方案和写材料 |
| `docs/stage_notes` | 每阶段说明 | 每完成阶段后更新 |
| `data` | 真实 CST 导出 dropzone | 只放真实 CST nearfield/farfield，不放 demo/synthetic |
| `outputs` | 所有自动生成结果、图表、manifest、审计报告 | 报告/PPT/提交包证据 |
| `submission` | 当前提交草稿包，按最终提交目录预排 | 检查材料齐套性，不等同于最终提交 |
| `文档` | 原始赛题 PDF、Workflow 历史文档、正式交付物位置说明 | 人可直接阅读的 Word/PDF/PPT 入口 |
| `文献` | 文献矩阵入口和新增推荐文献方向说明 | 查文献依据与未来方案 |
| `requirements.txt` | Python 依赖 | 建环境 |
| `.gitignore` | GitHub 协作忽略规则 | 排除 CST 缓存、final zip、node_modules 和可再生成大文件 |

## `code` 脚本分组

| 分组 | 脚本 | 意义 |
|---|---|---|
| 核心电磁与 baseline | `em_core.py`, `run_baseline.py` | 合成场、等效源、重建和初始布局验证 |
| CST 数据接口 | `cst_io.py`, `check_cst_export.py`, `normalize_cst_complex_columns.py`, `prepare_cst_templates.py`, `prepare_cst_macro_templates.py`, `build_cst_execution_dashboard.py`, `build_cst_operator_runbook.py`, `run_cst_level1_required_automation.py`, `run_cst_solver_project.py`, `export_cst_farfield_results.py`, `export_cst_true_nearfield_monitor.py`, `run_cst_level2_element_library.py`, `export_cst_level2_superposed_results.py` | 固定 CST 表格格式、校验、幅相转换、宏模板、执行 dashboard、真机操作包、本机 CST API 工程生成、单工程求解、FarfieldPlot 真实结果导出、G3 真近场 monitor/probe 导出控制器和 Level 2 element-library 叠加导出 |
| Level 1 标准源 | `prepare_cst_level1_manifest.py`, `prepare_cst_level1_workpack.py`, `merge_cst_level1_exports.py`, `run_cst_level1_batch_reconstruction.py`, `generate_synthetic_cst_level1_dataset.py` | 标准源计划、建模任务包、审计和重建 |
| Level 2 多源识别 | `prepare_cst_level2_manifest.py`, `prepare_cst_level2_workpack.py`, `merge_cst_level2_exports.py`, `generate_synthetic_cst_dataset.py`, `run_cst_recognition.py`, `run_cst_recognition_ablation.py`, `run_cst_level2_element_library.py`, `export_cst_level2_superposed_results.py`, `run_cst_structure_comparison.py` | 多源多状态计划、任务包、合并、识别、CST element-library 工程、sample-level full48 导出和简化结构遮挡对照 |
| 重建验证 | `run_cst_reconstruction.py`, `run_cst_level1_angular_calibration.py`, `run_reconstruction_robustness.py` | CST 数据重建、Level 1 FarfieldPlot-derived 角域校准和鲁棒性分析 |
| 项目审计与成稿 | `build_scorecard.py`, `build_problem_requirements_matrix.py`, `build_submission_index.py`, `build_completion_audit.py`, `build_master_dashboard.py`, `build_progress_report.py`, `build_submission_draft.py`, `build_final_report_docx.py`, `build_defense_pptx_artifact.py` | 评分项、赛题要求矩阵、提交物、完成度 gate、总控 dashboard、进展跟踪、导师汇报、提交草稿包、正式报告 DOCX/PDF 和答辩 PPTX/PDF |
| 执行记录 | `prepare_cst_execution_log_templates.py` | 真实 CST 运行、问题和截图记录模板 |

## `docs` 文档分组

| 分组 | 文件 | 意义 |
|---|---|---|
| 总览讲解 | `current_work_detailed_explanation.md` | 按推进过程讲清技术路线、CST 建模产物、代码职责、阶段路线和人工注意项 |
| 文献与策略 | `literature_screening_and_strategy.md`, `literature_matrix.md`, `literature_to_algorithm_traceability.md` | 论文筛查、方法迁移和算法证据链 |
| 人工提交 | `admin_submission_template.md` | 学校、队名、申报人、联系方式、报名表和最终命名的人工填写模板 |
| 技术路线 | `team_division_technical_route.md`, `phase_01_cst_technical_route_and_division.md`, `phase_02_cst_data_integration_plan.md`, `phase_03_cst_level2_multisource_recognition_protocol.md` | 三人实名分工、总路线和 CST/Python 分工 |
| Level 1 执行 | `cst_level1_standard_source_protocol.md`, `level1_cst_sprint_handoff.md` | 标准源建模、导出和验收 |
| 报告与提交 | `solution_report_draft.md`, `final_submission_package_plan.md` | 报告草稿、PPT/视频和提交包计划 |
| 进展跟踪 | `project_progress_report.md`, `progress_reports/mentor_portal.md`, `progress_reports/meeting_brief.md`, `progress_reports/daily_digest.md`, `progress_reports/evidence_map.md`, `progress_reports/decision_brief.md`, `progress_reports/mentor_qa.md`, `progress_reports/g5_closure_brief.md`, `progress_reports/mentor_snapshot.md`, `progress_reports/latest_change_note.md`, `progress_reports/next_action_brief.md`, `progress_reports/risk_register.md`, `progress_reports/submission_readiness.md`, `progress_reports/progress_index.md`, `progress_reports/latest_mentor_brief.md`, `progress_reports/watch_scope.md`, `progress_reports/progress_update_protocol.md`, `progress_reports/status_review_log.md`, `progress_reports/*.md` | 当前做了什么、产物是什么、缺口、下一步建议、导师阅读门户、组会汇报稿、每日进展汇总、导师证据映射、导师决策清单、导师问答卡、G5 关闭路线、导师 30 秒快照、本次变化说明、下一步行动清单、风险登记表、提交就绪清单、阶段时间线、导师汇报固定入口、巡检范围、跟进操作规程、状态复核台账和历史归档 |
| 复现与字段 | `reproduce_commands.md`, `data_dictionary.md` | 命令和数据字段说明 |
| 阶段说明 | `stage_notes/*.md` | 每阶段做了什么、为什么、产物意义 |

## `outputs` 目录分组

| 分组 | 目录 | 意义 |
|---|---|---|
| baseline | `baseline` | 半球面布局和合成 baseline |
| CST 模板/接口 | `cst_templates`, `cst_phase_demo` | CST 测点表、导出模板、幅相转换验证 |
| CST 宏模板 | `cst_macro_templates` | Level 1/Level 2 宏输入表、VBA 骨架和 pilot 队列 |
| CST 执行 dashboard | `cst_execution_dashboard` | 当前 G2/G3 状态、action sheet、缺失文件和 dropzone 规则 |
| CST 操作 runbook | `cst_operator_runbook` | G2 required 标准源真机步骤、162 探针点、远场网格、导出合同和截图证据 |
| CST 真机工程生成 | `cst_real_level1_projects` | 通过本机 CST API 生成的两个 Level 1 required `.cst` 工程、VBA history、manifest 和生成日志 |
| CST solver-safe 工程 | `cst_solver_ready_level1_projects` | 使用 `efarfield` probe mode 生成的本机可求解 Level 1 required 工程 |
| CST 真机求解试验 | `cst_solver_trials` | 短偶极子/半波偶极子 solver-safe 求解证据，以及原始 13 m Cartesian probe 失败证据 |
| CST FarfieldPlot 导出 | `cst_farfield_export` | 真实 CST FarfieldPlot 导出 summary、stdout 和 `check_cst_export.py` 校验 JSON |
| CST 真近场导出控制器 | `cst_true_nearfield_monitor_export` | G3 required true-monitor/probe dry-run 任务计划、CST worker 日志、结果树检查和 raw export 尝试 |
| 报告成稿素材 | `report_package`, `final_report` | 报告章节状态、图表占位、核心引用、替换任务、正式报告导出摘要和 PDF 页面预览 |
| PPT/视频素材 | `presentation_package`, `presentation_artifact`, `video_artifact` | 答辩 storyboard、视频分镜、展示素材、PPTX/PDF 导出摘要、layout JSON、预览接触表和 MP4 导出摘要 |
| 最终归档 | `final_archive` | 最终 zip、文件级 SHA256 manifest、压缩包摘要和完整性检查依据 |
| Level 1 | `cst_level1_plan`, `cst_level1_workpack`, `level1_analytic_reference`, `cst_level1_merge_report`, `cst_level1_reconstruction_batch`, `cst_level1_angular_calibration`, `synthetic_cst_level1_dataset` | 标准源计划、任务包、解析 sanity reference、审计、等效源重建、FarfieldPlot-derived 角域校准和预演 |
| Level 2 | `cst_level2_plan`, `cst_level2_workpack`, `cst_level2_element_library`, `cst_level2_element_trials`, `cst_level2_superposed_export`, `cst_level2_merge_report`, `cst_recognition_level2`, `cst_recognition_level2_ablation`, `cst_structure_comparison`, `cst_recognition_level2_pilot`, `cst_recognition_level2_pilot_ablation`, `synthetic_cst_dataset`, `cst_recognition_demo`, `cst_recognition_ablation` | 多源识别计划、任务包、CST element-library 工程、三方向 element 求解试验、48 样本 full48 导出、审计、识别、消融、简化结构遮挡对照和预演 |
| 真实执行记录 | `cst_execution_logs` | CST 真实运行日志、问题日志和截图清单模板 |
| 重建验证 | `cst_reconstruction_demo`, `reconstruction_robustness` | 重建 demo 和鲁棒性扫描 |
| 项目审计 | `scorecard`, `problem_requirements`, `submission_index`, `completion_audit`, `master_dashboard` | 评分项、赛题要求矩阵、提交物、完成度 gate 和总控任务队列 |

## `submission` 目录分组

| 分组 | 目录 | 意义 |
|---|---|---|
| 人工信息 | `00_admin` | 报名与提交信息模板，需队伍人工填写 |
| 报告 | `01_report` | 正式报告 PDF/DOCX、报告草稿和状态说明 |
| 答辩 | `02_presentation` | 正式 PPTX/PDF、PPT 大纲和素材包 |
| 视频 | `03_video` | 演示视频脚本草稿和后续 MP4 位置 |
| 代码 | `04_code` | 可复现代码、依赖、命令和数据字典 |
| CST | `05_cst` | Level 1/Level 2 manifest、workpack、element-library、full48 导出审计、操作 runbook 和执行日志 |
| 数据 | `06_data` | demo/synthetic 数据、baseline、鲁棒性、scorecard、problem requirements、submission index、completion audit 和 master dashboard |
| 附录 | `07_appendix` | 文献、scorecard、完成度审计、总控 dashboard、当前工作讲解、阶段说明和交接单 |

## 当前最短阅读顺序

1. `README.md`
2. `docs/current_work_detailed_explanation.md`
3. `docs/project_progress_report.md`
4. `docs/team_division_technical_route.md`
5. `docs/stage_notes/README.md`
6. `docs/stage_notes/00_project_structure.md`
7. `docs/solution_report_draft.md`
8. `outputs/problem_requirements/problem_requirements_matrix.md`
9. `outputs/master_dashboard/master_status_dashboard.md`
10. `outputs/completion_audit/completion_audit.md`
11. `outputs/cst_level1_workpack/README_level1_workpack.md`
12. `outputs/cst_level2_workpack/README_level2_workpack.md`
13. `outputs/cst_macro_templates/README_cst_macro_templates.md`
14. `outputs/cst_operator_runbook/README_cst_operator_runbook.md`
15. `docs/stage_notes/17_cst_solver_safe_level1_export.md`
16. `docs/stage_notes/18_cst_level2_element_library_pilot.md`
17. `docs/stage_notes/19_cst_level2_full48_recognition.md`
18. `docs/stage_notes/20_g5_report_material_refresh.md`
19. `docs/stage_notes/23_final_report_ppt_export.md`
20. `submission/01_report/solution_report.pdf`
21. `submission/02_presentation/defense_slides.pdf`
22. `docs/stage_notes/24_demo_video_export.md`
23. `docs/stage_notes/25_final_archive.md`
24. `docs/stage_notes/26_current_work_explanation.md`
25. `outputs/final_archive/final_archive_summary.json`
26. `outputs/final_archive/CS-202614_submission.zip`
27. `submission/03_video/demo_video.mp4`
28. `outputs/video_artifact/demo_video_summary.json`
29. `outputs/cst_level1_merge_report/level1_merge_summary.json`
30. `outputs/cst_level2_merge_report/level2_merge_summary.json`
31. `outputs/cst_recognition_level2/cst_recognition_metrics.json`
32. `outputs/cst_recognition_level2_ablation/recognition_ablation_summary.json`
33. `outputs/cst_level1_angular_calibration/README_cst_level1_angular_calibration.md`
34. `outputs/cst_structure_comparison/README_cst_structure_comparison.md`
35. `docs/stage_notes/22_structure_occlusion_comparison.md`
36. `outputs/cst_execution_dashboard/cst_execution_dashboard.md`
37. `outputs/cst_execution_logs/README_cst_execution_logs.md`
38. `docs/stage_notes/28_g3_true_nearfield_export_controller.md`
39. `outputs/cst_true_nearfield_monitor_export/README.md`

## 2026-06-02 true-monitor queue index

`data/cst_true_nearfield_workpack/` now contains the CST true near-field monitor
handoff package plus a reduced-layout rerun queue:

| File | Meaning |
|---|---|
| `true_nearfield_monitor_cases.csv` | Six Level 1 cases and full-grid true-monitor export contracts. |
| `true_nearfield_sensor_shell.csv` | Full 162-point upper-hemisphere shell. |
| `true_nearfield_priority_layout_queue.csv` | Eighteen case-layout tasks: `full_grid_162`, `geometric_farthest_32`, and `fibonacci_snap_120` for each Level 1 case. |
| `true_nearfield_priority_sensor_subsets.csv` | Sensor ids and coordinates needed to derive each queued layout from a full-grid export. |

`code/export_cst_true_nearfield_monitor.py` is the current executable bridge
from this packet to CST. It writes
`outputs/cst_true_nearfield_monitor_export/true_nearfield_export_task_plan.csv`
in dry-run mode and records CST result-tree inspection/export attempts in the
same output directory.

## 当前不能声称完成的原因

- 真实 Level 1 CST required 已完成求解、CSV 导出、严格审计、批量重建和 FarfieldPlot-derived 角域校准；Level 2 已完成 48/48 个 CST-derived element-library 样本、严格合并、识别、消融和简化结构遮挡对照，但复杂载体 full-wave airframe 对照仍未完成。
- 正式报告 PDF/DOCX、答辩 PPTX/PDF、演示视频 MP4 和最终 zip 已生成；MP4 是自动计时静音版，正式报送前建议人工播放并按竞赛要求决定是否替换为带讲解版本。
- Level 1 solver-safe 数据已经在报告/PPT 中区分角域高一致性与 full-wave 近场等效源模型边界；最终视频如替换，应保持同一口径。

## 2026-06-03 CST solver mesh-limit 诊断

`code/run_cst_solver_project.py` 现在会在 CST 试求解后解析 `Result` 日志、真实结果树子项、网格规模和 MPI 节点要求。本轮短偶极子 trial 证明：CST Python 可启动、工程可打开、`StartSolver` 返回成功，但原始 13 m Cartesian probe/full-grid true-nearfield 工程触发约 `4.6` billion mesh cells，并要求至少 `3` 个 MPI cluster nodes，因此本机没有生成可导出的求解结果。

相关证据入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/29_g3_cst_solver_mesh_limit.md` | S29 阶段说明，解释“CST 可运行但当前采样建模路线不可求解”的原因 |
| `outputs/cst_solver_trials/required_true_nf_short/CST_L1_short_dipole_z_1p2G_solver_trial_solver_summary.json` | 机器可读 trial 摘要，`status = solver_mesh_limit` |
| `outputs/cst_solver_trials/required_true_nf_short/README.md` | 人类可读 trial 诊断 |

后续 G3 路线应切换为 mesh-safe 流程：CST 侧求解近源/局部 Huygens 面或近边界物理数据，Python 侧把该数据外推到 13 m 测量壳，再做采样方案、外推反演和分类评估。

## 2026-06-03 CST mesh-safe Huygens 工作包

本轮新增 `data/cst_meshsafe_huygens_workpack/` 和 `code/prepare_cst_meshsafe_huygens_workpack.py`，把 S29 中不可求解的 13 m Cartesian probe 路线改成局部 Huygens 面观测路线：CST 只求解 0.35 m 局部面附近的 E-field probe 和 farfield reference，Python 负责把局部证据外推到 13 m 测量壳。由于 CST 对中文长路径和内部结果路径较敏感，工作包命令默认使用 `C:\csttmp\huy_p` 生成工程、`C:\csttmp\huy_s` 跑求解 gate。

当前结论：CST 不是无法正常运行。短路径 `C:\csttmp\huy_p` 工程生成已经返回 `project_generation_complete`，2/2 `.cst` 工程保存成功；短路径 `L1_short_dipole_z_1p2G` solver gate 已经能进入 `HF Time Domain (Hex)` solver，并保留 `.m3d/.ffm/.fme` 结果文件；本轮没有再触发 mesh limit 或路径长度错误。剩余问题是 clean completion 与局部结果导出/解析，而不是 CST 启动或 Python API 失效。

相关入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/30_g3_meshsafe_huygens_workpack.md` | S30 阶段说明，记录本轮 mesh-safe CST 路线和证据边界 |
| `code/prepare_cst_meshsafe_huygens_workpack.py` | 生成 mesh-safe case CSV、局部 Huygens probe CSV、导出契约和下一步命令 |
| `data/cst_meshsafe_huygens_workpack/README.md` | 给 CST/算法队友的工作包说明 |
| `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv` | 从生成工程到短路径 solver gate 的命令清单 |
| `C:\csttmp\huy_p` | 短 ASCII 路径下的 mesh-safe CST 工程缓存 |
| `outputs/cst_solver_trials/meshsafe_huygens_required_shortpath/` | 本机短路径 solver gate 摘要和日志缓存 |

## 2026-06-03 CST mesh-safe Huygens ResultTree 导出与外推诊断

S31 完成了 mesh-safe Huygens 路线的第一个真实数据闭环：CST 短路径工程已保留局部 `.m3d`、farfield `.ffm/.fme` 结果，导出控制器改用 ResultTree 读取 1D probe 复数曲线，生成了第一份可进入算法链路的局部 Huygens E-field CSV。Field Monitor ASCII 弹窗不是 CST 不能运行，而是导出入口不适用于当前 3D monitor view。

相关入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/31_g3_meshsafe_huygens_resulttree_extrapolation.md` | S31 阶段说明，记录 ResultTree 导出、实测 CSV 和 Python 外推诊断结果 |
| `code/export_cst_meshsafe_huygens_results.py` | CST 结果审计/导出控制器；可用 `--attempt-export --overwrite` 生成局部复数 E-field CSV |
| `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` | 第一份真实 CST 局部 Huygens probe 导出，`96 * 3 = 288` 行 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Python 侧局部 Huygens 证据外推到远场参考的诊断脚本 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation/` | 外推诊断结果、局部场质量表、最佳 farfield shape 对比和摘要 |
| `outputs/cst_meshsafe_huygens_result_export/` | 本机 CST 结果树探查、日志和导出审计缓存；默认不纳入 Git 版本库 |

当前结论：CST Python API、短路径工程生成、solver gate、ResultTree 读取和 CSV 接入链路均可用；剩余风险集中在等效源/Huygens 算子的物理约定校准、第二源案例复验，以及从局部实测面向 13 m 半球采样方案的严格误差门限收敛。

## 2026-06-04 CST mesh-safe Huygens 两例批处理门控

本轮为第二个 Level 1 mesh-safe Huygens 源例 `L1_halfwave_dipole_z_1p2G` 完成短路径 CST clean solver、ResultTree 局部场导出和 Python 外推诊断，并把短偶极子与半波偶极子合并成两例批处理门控。半波偶极子 solver gate 显示 `status = finished`，未触发 mesh limit、路径长度错误或 aborted-keeping-results；ResultTree 导出显示 `target_contract_complete`，目标 CSV 行数 `288`。

纳入 Git 的关键入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/32_g3_meshsafe_huygens_two_case_batch.md` | S32 阶段说明，记录第二源例 CST clean solver、导出和批处理结果 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 新增批处理入口 `--batch`、case CSV 选择、输出目录选择和样本筛选参数 |
| `data/cst_exports/level1_meshsafe_huygens/L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` | 半波偶极子真实 CST 局部 Huygens probe 导出，`96 * 3 = 288` 行 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_halfwave/` | 半波偶极子单例外推诊断结果，最佳分支 `electric_only_outgoing` / `physics_proxy_pass` |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | 两例批处理汇总：`2/2` completed，`0` missing/failed，`1` physics-proxy pass |

保留在本机、不纳入 Git 的审计缓存：

| 文件/目录 | 意义 |
|---|---|
| `C:\csttmp\huy_h\h_half.cst` | 半波偶极子短路径 CST solved project 缓存 |
| `outputs/cst_solver_trials/meshsafe_huygens_halfwave_shortpath/` | 半波偶极子 CST solver gate 摘要和 stdout log |
| `outputs/cst_meshsafe_huygens_result_export_halfwave/` | 半波偶极子 ResultTree 探查、probe item map 和导出审计缓存 |

当前结论：CST 可正常运行，并且 mesh-safe 路线已经在两个 Level 1 源例上完成真实数据链路。剩余问题不是 CST 启动或求解能力，而是 Huygens/等效源算子的严格物理定标：需要补 H-field、阻抗校准或更完整的矢量面 Green/Stratton-Chu 积分，并把主瓣评价从单点 argmax 升级为适合宽环状方向图的区域指标。
