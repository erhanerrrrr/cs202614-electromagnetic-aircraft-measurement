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

## 2026-06-04 CST mesh-safe Huygens 区域主瓣门控与 dashboard 接入

本轮将 S32 的两例真实 CST mesh-safe Huygens batch 从单点主瓣评价升级为区域主瓣评价，并接入 G3 dashboard。区域主瓣指标使用归一化功率 `0.75` 等值区域，输出区域误差、区域 Jaccard 和区域 capture，用于处理短偶极子这类宽环状主瓣。

关键入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/33_g3_meshsafe_huygens_region_dashboard.md` | S33 阶段说明，记录区域主瓣指标、batch 结果和 dashboard 接入 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 新增 `main_lobe_region_*` 指标、`region_shape_pass` 状态和 batch pass 统计 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.csv` | 两例 batch 的 point-lobe/region-lobe 对照表 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | dashboard 使用的机器可读 batch 证据，`case_count_strict_proxy_or_region = 2` |
| `code/build_g3_model_dashboard.py` | 新增 `meshsafe_huygens_real_cst_batch` 证据行和 H-field/阻抗定标优先动作 |
| `outputs/g3_model_dashboard/g3_model_status.csv` | G3 状态矩阵刷新，mesh-safe batch 状态为 `region_proxy_batch_pass` |
| `outputs/g3_model_dashboard/g3_next_actions.csv` | 下一步优先级刷新，第一项为 mesh-safe Huygens H-field/阻抗定标 |

当前结论：`L1_short_dipole_z_1p2G` 的单点主瓣误差仍为 `139.52 deg`，但区域主瓣误差为 `0 deg`、区域 Jaccard 约 `0.919`、区域 min capture 约 `0.930`，因此应解释为宽环状方向图的单点指标失配，而不是方向图整体错位。两例真实 CST 数据链现在完成 `2/2`，缺失 `0`，strict/physics-proxy/region count 为 `2`。下一步应独立推进 H-field 或阻抗定标，而不是继续把 G3 完全卡在 true-monitor 队列上。

## 2026-06-04 CST mesh-safe Huygens scalar impedance calibration

S34 adds an explicit scalar impedance scan to the real CST mesh-safe Huygens
proxy. The scan keeps the original E-only and M-only diagnostics, then sweeps
`eta_eff/eta0` on the outgoing electric/magnetic equivalence variants. The
current two-case batch selects `eta_eff = 0.25 eta0` for both Level 1 real CST
exports and updates the G3 dashboard status to
`impedance_region_proxy_batch_pass`.

Key entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/34_g3_meshsafe_huygens_impedance_calibration.md` | S34 stage note documenting the scalar impedance calibration proxy, validation, and limitation. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `--impedance-factors`, per-row `eta_eff`, and batch impedance statistics. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.csv` | Two-case calibrated batch summary; both best settings use `outgoing_equivalence_minus_eta0p25`. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | Machine-readable batch evidence consumed by the dashboard. |
| `code/build_g3_model_dashboard.py` | Recognizes `impedance_region_proxy_batch_pass` and promotes the next action to H-field-backed validation. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Current G3 status matrix with calibrated proxy evidence. |

Boundary: the selected impedance is calibrated against the current Level 1
far-field reference. It is stronger than a fixed `eta0` assumption, but final
Stratton-Chu/Huygens wording still needs H-field-backed currents or stable
impedance bounds across additional CST cases.

## 2026-06-04 Mesh-safe Huygens impedance stability gate

`code/run_cst_impedance_stability_gate.py` records whether the scalar
`eta_eff/eta0` proxy has an interior stable optimum or remains on a scan
boundary. It also inspects cached CST ResultTree JSON files for matching
H-field probe curves. Current reading: CST is runnable on the mesh-safe route,
but the cached handoff exposes E-field probe curves only; `Field Monitor` ASCII
export is an export-path mismatch, not a CST startup failure. After the
lower-eta extension, the two cases prefer different eta values
(`0.03125 eta0` and `0.0625 eta0`), so the current status is
`cross_case_impedance_disagreement`.

Related entries:

| File/Directory | Meaning |
|---|---|
| `docs/stage_notes/35_g3_meshsafe_huygens_impedance_stability.md` | Stage note explaining the impedance boundary and H-field readiness check. |
| `data/sampling_layouts/cst_meshsafe_huygens_impedance_stability/` | Stability summary, per-case eta table, H-field ResultTree readiness, and next commands. |
| `outputs/g3_model_dashboard/g3_model_status.csv` | Dashboard row `meshsafe_huygens_impedance_stability`. |

## 2026-06-04 CST mesh-safe Huygens H-field 工作包

本轮把 H-field handoff 从“下一步想法”整理成可执行工程路径：`run_cst_level1_required_automation.py`
支持 `--probe-mode hfield`，`export_cst_meshsafe_huygens_results.py` 支持
`--field-kind e|h`，工作包新增 H-field CSV 合同并把 H-field 工程生成、短路径求解和
ResultTree 导出列入 `next_meshsafe_huygens_commands.csv` 的步骤 5-7。

阶段结论：CST 不是无法正常运行。S36 将 H-field 路线整理成可执行步骤；
该阶段结束时，H-field 仍等待 `C:\csttmp\huy_hs\h_short_hfield.cst` 生成和
求解。S37 已继续完成短偶极子 H-field 导出和算法接入，因此当前状态见下一节。

相关入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/36_g3_meshsafe_huygens_hfield_workpack.md` | S36 阶段说明，记录 H-field 合同、导出控制器和当前 blocker |
| `data/cst_meshsafe_huygens_workpack/local_huygens_hfield_export_contract.csv` | H-field probe CSV 字段合同 |
| `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv` | E/H 工程生成、solver gate 和 ResultTree 导出命令队列 |
| `code/export_cst_meshsafe_huygens_results.py` | `--field-kind e|h` ResultTree 导出控制器 |
| `code/run_cst_level1_required_automation.py` | `--probe-mode hfield` CST 工程生成入口 |

## 2026-06-04 CST mesh-safe Huygens real E/H 外推门控

本轮继续执行 S36 的 H-field 步骤，短偶极子 `L1_short_dipole_z_1p2G`
已经完成 H-field mesh-safe CST 工程生成、短路径求解、ResultTree 导出和
Python E/H 双场接入。新增的 H-field CSV 与既有 E-field CSV 在 `96` 个局部
Huygens 面节点上逐点对齐，`run_cst_meshsafe_huygens_extrapolation.py`
现在会自动寻找同名 `_local_hfield.csv`，存在时评估真实 `J = n x H_t` 与
`M = -n x E_t` 分支，不存在时回退到 E-only 阻抗代理。

当前结论：CST 能正常完成 mesh-safe 路线的建模、求解和 ResultTree 导出。
短偶极子 H-field 单例门控显示 `hfield_available = true`，切向 E/H 阻抗约
`425.36 ohm`（约 `1.129 eta0`）。真实 E/H 分支
`eh_love_equivalence_minus` 已达到 `region_shape_pass`，相关性约 `0.9989`，
scale-fitted NMSE 约 `6.96e-04`，区域主瓣误差 `0 deg`。不过当前最佳分支
仍是 `outgoing_equivalence_minus_eta0p25` 阻抗代理，说明剩余问题是
Huygens 面积分核、符号约定和幅度归一化的算法定标，而不是 CST 启动或
求解失败。

相关入口：

| 文件/目录 | 意义 |
|---|---|
| `docs/stage_notes/37_g3_meshsafe_huygens_real_eh_extrapolation.md` | S37 阶段说明，记录短偶极子 H-field 导出、E/H 接入和当前算法边界 |
| `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` | 真实 CST 局部 H-field probe CSV，`96 * 3 = 288` 行 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 自动加载 H-field、E/H 几何对齐、真实双场等效电流和 batch 汇总 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation/` | 短偶极子单例 E/H 外推门控 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | 两例 batch 门控；`2/2` completed，`1/2` H-field loaded，`0/2` best real-H |

## 2026-06-04 CST mesh-safe Huygens full H-field coverage

S38 closes the remaining Level 1 mesh-safe H-field coverage gap. The half-wave
case now has a solved short-path CST H-field project, a ResultTree-exported
local H-field CSV, and a refreshed two-case Python batch gate. CST is therefore
not the current mesh-safe Huygens blocker; the active blocker is calibration of
the real E/H Love-equivalence operator against the scalar `eta_eff` proxy and
the CST far-field reference.

Tracked entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/38_g3_meshsafe_huygens_full_hfield_coverage.md` | S38 note covering half-wave H-field solve/export, sample-id export guard, and real E/H acceptance status. |
| `data/cst_exports/level1_meshsafe_huygens/L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_hfield.csv` | Half-wave real CST local H-field probe CSV, `96 * 3 = 288` rows. |
| `code/export_cst_meshsafe_huygens_results.py` | Adds project-path based sample-id inference when `--sample-id` is omitted. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `vector_gate` summary and batch counts for accepted real-H and real E/H candidates. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | Refreshed two-case batch: `2/2` H-field loaded, `2/2` real E/H accepted, `0/2` best settings using real-H. |
| `outputs/g3_model_dashboard/` | Dashboard now states that the current mesh-safe Huygens task is E/H operator calibration, not CST export recovery. |

## 2026-06-04 CST mesh-safe Huygens real E/H J-scale gate

S39 moves the mesh-safe Huygens line from "real E/H candidates are accepted" to
"real E/H branches are the best strict-pass diagnostic branches, but cross-source
operator stability is not yet closed." The batch now scans a global scale on
`J = n x H_t` while keeping the measured CST H-field distribution.

Tracked entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/39_g3_meshsafe_huygens_real_eh_jscale_gate.md` | S39 note covering the real E/H J-scale scan, strict-pass best branches, and the remaining cross-source sign/scale disagreement. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds `--eh-j-scale-factors`, calibrated real E/H variants, and `real_eh_operator_calibration_status`. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | Refreshed two-case batch: `2/2` H-field loaded, `2/2` best real-H branches, `2/2` strict/proxy, best J scales `96.0` and `256.0`. |
| `outputs/g3_model_dashboard/` | Dashboard now reports `real_eh_strict_batch_calibration_needed` and makes cross-source J-scale/sign stability the first next action. |

## 2026-06-04 CST mesh-safe Huygens frozen real E/H rule gate

S40 adds a stricter cross-case diagnostic: a single real E/H candidate must use
the same plus/minus convention and the same J-scale for every completed Level 1
case. The best frozen candidate is `eh_love_equivalence_minus_j96`, accepted for
`2/2` cases and strict for `1/2`, with minimum correlation `0.9988956628` and
maximum scaled power NMSE `7.303417569844e-04`. This moves the mesh-safe Huygens
line from free per-source calibration toward a frozen operator candidate that
still needs a geometry/physics explanation and broader source-family validation.

Tracked entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/40_g3_meshsafe_huygens_frozen_real_eh_rule.md` | S40 note covering the frozen real E/H rule gate and dashboard status. |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | Adds the frozen real E/H rule aggregation and summary outputs. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_frozen_real_eh_rule_summary.csv` | Ranked frozen real E/H candidates across current Level 1 cases. |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_frozen_real_eh_rule_cases.csv` | Per-case rows for the selected frozen candidate. |
| `outputs/g3_model_dashboard/` | Dashboard now reports `real_eh_frozen_rule_region_pass` and makes physics/geometry validation of the frozen candidate the next gate. |

## 2026-06-04 CST mesh-safe Huygens rotation covariance gate

S41 checks the frozen real E/H candidate `eh_love_equivalence_minus_j96` under
rigid rotations of the measured local CST E/H surface fields. The gate uses the
unrotated Huygens prediction evaluated at inverse-rotated far-field directions
as the comparison reference, so it proves coordinate covariance of the
implementation. It does not replace independent CST x/y/tilted/off-axis source
family validation.

Current result: `rotation_covariance_strict_pass`. The two current real E/H
base cases remain accepted against CST far fields, and the rotation suite gives
`18/18` strict covariance passes across `9` rigid rotations per case. The
maximum covariance scaled power NMSE is `4.038192571773e-29`; the maximum
normalized absolute error is `2.742250870824e-14`; the maximum region-lobe error
is `1.207418269726e-06 deg`.

Tracked entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/41_g3_huygens_rotation_covariance.md` | S41 note covering the rotation-covariance gate, metrics, and remaining CST source-family boundary. |
| `code/run_cst_huygens_rotation_covariance.py` | Rotation-covariance stress test for the frozen real E/H Huygens rule. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_covariance_summary.json` | Summary status and headline covariance metrics. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_base_cst_agreement.csv` | Base real CST agreement rows for the frozen candidate. |
| `data/sampling_layouts/cst_meshsafe_huygens_rotation_covariance/huygens_rotation_covariance_cases.csv` | Per-case, per-rotation covariance metrics. |
| `outputs/g3_model_dashboard/` | Dashboard now includes `meshsafe_huygens_rotation_covariance = rotation_covariance_strict_pass`. |

## 2026-06-04 CST mesh-safe Huygens source-family workpack

S42 packages the next independent CST validation gate for the frozen Huygens
rule. The workpack is ready for execution, but it is not yet a physics pass:
the next step is to run the generated CST project, solver, and ResultTree export
commands, then evaluate the same frozen E/H rule without retuning.

Tracked entries:

| File/directory | Meaning |
|---|---|
| `docs/stage_notes/42_g3_huygens_source_family_workpack.md` | S42 note covering the source-family workpack, automation boundary, and next CST gate. |
| `code/prepare_cst_huygens_source_family_workpack.py` | Generates six x/y/off-axis Level 1 source-family cases, case-scoped probe points, validation matrix, and command queue. |
| `code/run_cst_level1_required_automation.py` | Now supports axis-aligned x/y/z dipole generation inferred from each case segment. |
| `code/export_cst_meshsafe_huygens_results.py` | Now filters case-scoped probe rows by `sample_id` during ResultTree export checks. |
| `data/cst_meshsafe_huygens_source_family_workpack/` | Generated source-family cases, probe CSV, validation matrix, command queue, summary JSON, and README. |
| `outputs/g3_model_dashboard/` | Dashboard now includes `meshsafe_huygens_source_family_workpack = source_family_workpack_ready`. |
