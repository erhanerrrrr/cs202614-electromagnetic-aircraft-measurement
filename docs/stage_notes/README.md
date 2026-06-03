# 阶段说明索引

本目录用于记录每一阶段工作说明。每份说明都按同一结构写：做了什么、为什么这样做、产物有哪些、各文件意义、如何验证、下一步是什么。

当前阶段说明：

| 阶段 | 文件 | 说明 |
|---|---|---|
| S00 | `00_project_structure.md` | 项目目录、文件组织和阅读顺序 |
| S01 | `01_literature_and_strategy.md` | 文献筛查、方法迁移和技术路线来源 |
| S02 | `02_hemisphere_layout_and_baseline.md` | 半球面测点、合成 baseline 和初步重建 |
| S03 | `03_cst_data_interface.md` | CST 数据格式、校验、幅相转换和导出模板 |
| S04 | `04_level1_standard_source.md` | Level 1 标准源 manifest、workpack、审计和重建 |
| S05 | `05_level2_multisource_recognition.md` | Level 2 多源多状态 manifest、workpack、合并和识别 |
| S06 | `06_validation_robustness_and_metrics.md` | 鲁棒性、删减实验、scorecard 和完成度审计 |
| S07 | `07_submission_package.md` | 最终报告、PPT、视频、代码和提交包缺口 |
| S08 | `08_cst_macro_templates.md` | CST 宏模板、批量执行输入表和 pilot 队列 |
| S09 | `09_cst_execution_dashboard.md` | CST 执行 dashboard、真实数据 dropzone 和下一步 action sheet |
| S10 | `10_report_package.md` | 报告成稿素材包、图表占位、引用短表和替换任务 |
| S11 | `11_presentation_video_package.md` | 答辩 PPT storyboard、演示视频分镜和展示素材替换清单 |
| S12 | `12_level1_analytic_reference.md` | Level 1 标准源解析方向图参考和 CST sanity check |
| S13 | `13_master_dashboard.md` | 总控状态 dashboard、三人任务队列和提交草稿包接入 |
| S14 | `14_cst_operator_runbook.md` | CST G2 真机操作包、探针点、远场网格、导出合同和截图证据 |
| S15 | `15_problem_requirements_matrix.md` | 赛题原文要求、100 分评分项、交付物和当前证据矩阵 |
| S16 | `16_cst_real_level1_project_generation.md` | 本机 CST API 生成 Level 1 required 真实工程、VBA history 和生成证据 |
| S17 | `17_cst_solver_safe_level1_export.md` | CST solver-safe 求解、FarfieldPlot 导出、Level 1 required strict 审计和重建 |
| S18 | `18_cst_level2_element_library_pilot.md` | CST Level 2 element-library pilot、8 个样本导出、合并、识别和消融 |
| S19 | `19_cst_level2_full48_recognition.md` | CST Level 2 full48 批量导出、严格合并、识别、消融和审计刷新 |
| S20 | `20_g5_report_material_refresh.md` | G5 报告、提交计划、PPT/视频素材包和风险口径刷新 |
| S21 | `21_level1_angular_calibration.md` | Level 1 FarfieldPlot-derived 角域校准、指标改善和模型边界说明 |
| S22 | `22_structure_occlusion_comparison.md` | Level 2 简化结构遮挡对照、方向图偏差和跨域识别稳健性 |
| S23 | `23_final_report_ppt_export.md` | 正式报告 DOCX/PDF、答辩 PPTX/PDF、视觉 QA 和提交审计刷新 |
| S24 | `24_demo_video_export.md` | PowerPoint 自动计时导出演示 MP4、视频摘要和 G5 最后文件缺口处理 |
| S25 | `25_final_archive.md` | 最终 zip、文件级 SHA256 manifest、压缩包完整性检查和人工提交清单 |
| S26 | `26_current_work_explanation.md` | 当前工作详细讲解、阅读入口、提交附录归档和后续接手口径 |
| S27 | `27_g5_compound_stress_material_refresh.md` | Level 2 复合仪器误差/结构缺测压力测试、zero-fill 失败边界和插补缓解口径 |

后续规则：

1. 每完成一个阶段，先更新对应阶段说明。
2. 若新增阶段，复制 `STAGE_NOTE_TEMPLATE.md` 作为起点。
3. 如果移动或新增关键文件，同时更新 `docs/project_file_index.md`。
