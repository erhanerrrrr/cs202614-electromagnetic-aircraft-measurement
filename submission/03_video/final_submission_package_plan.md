# 最终提交材料清单与汇报叙事大纲

版本：v0.4  
用途：把报告、PPT、视频、代码、CST 工程和数据证据统一到最终提交包视角。当前 Level 1 required、Level 2 full48 与简化结构遮挡对照证据已接入，正式报告 DOCX/PDF、答辩 PPTX/PDF、演示视频 MP4 和最终 zip 已导出。当前 MP4 为 PowerPoint 自动计时静音版；正式报送前建议人工完整播放，并按竞赛要求决定是否替换为带讲解录屏版本。

## 1. 最终提交包结构

建议最终压缩包命名：

```text
CS-202614_<队伍名>_复杂航空载体电磁辐射空域特性测量技术.zip
```

建议目录：

```text
CS-202614_submission/
  00_admin/
    admin_submission_template.md
  01_report/
    solution_report.pdf
    solution_report.docx
  02_presentation/
    defense_slides.pptx
    defense_slides.pdf
    presentation_package/
  03_video/
    demo_video.mp4
    demo_script.md
    video_package/
  04_code/
    src/
    README.md
    requirements.txt
    reproduce_commands.md
  05_cst/
    level1_manifest/
    level1_workpack/
    level1_project_automation/
    level1_analytic_reference/
    level1_merge_report/
    level1_reconstruction_batch/
    level1_angular_calibration/
    level1_standard_sources/
    level2_manifest/
    level2_workpack/
    level2_multisource/
    level2_structure_comparison/
    macro_templates/
    execution_dashboard/
    operator_runbook/
    execution_logs/
    level3_airframe/
    screenshots/
  06_data/
    cst_exports/
    synthetic_cst_level1_dataset/
    processed_outputs/
    metrics/
      report_package/
      master_dashboard/
      cst_structure_comparison/
      problem_requirements/
  07_appendix/
    literature_matrix.md
    literature_to_algorithm_traceability.md
    problem_requirements_matrix.md
    scorecard.md
    master_status_dashboard.md
    README_cst_operator_runbook.md
    data_dictionary.md
    level1_cst_sprint_handoff.md
    project_file_index.md
    stage_notes/

outputs/final_archive/
  CS-202614_submission.zip
  final_archive_manifest.csv
  final_archive_summary.json
```

## 2. 报告成稿结构

| 章节 | 内容 | 当前材料 | 待替换/补充 |
|---|---|---|---|
| 摘要 | 方法、指标和核心结果 | `submission/01_report/solution_report.pdf` | 已进入正式报告；后续视频需沿用同一摘要口径 |
| 1 赛题理解 | 评分项拆解、技术链路 | 已完成初稿 | 增加最终证据表 |
| 2 国内外调研 | 近场测量、等效源、压缩采样、RF 指纹 | `docs/literature_matrix.md`, `docs/literature_to_algorithm_traceability.md` | 规范参考文献格式 |
| 3 技术路线 | CST-Python 闭环和分级实验 | `docs/phase_01...`、`outputs/master_dashboard` | 加入真实 CST 流程截图和最新 dashboard |
| 4 传感布局 | 当前采用 2π 半球面、12m x 10m x 8m 包络 | `outputs/cst_templates/sensor_layout...` | CST 中半球面测点布局截图或测点表证据 |
| 5 场重建 | 等效源模型、Tikhonov、NF-FF、角域校准 | `outputs/cst_reconstruction/L1_*`、`outputs/cst_level1_reconstruction_batch`、`outputs/cst_level1_angular_calibration` | 写清 Level 1 required 已完成、角域校准高一致性，以及 full-wave 近场模型边界 |
| 6 少测点优化 | 100/75/50/25% 对比、λ 扫描 | `outputs/reconstruction_robustness` | 标注为算法鲁棒性参考，不外推为 Level 1 高精度证明 |
| 7 特征识别 | 空-频-极化特征、SVM/RF、混淆矩阵、结构遮挡跨域识别 | `outputs/cst_recognition_level2`、`outputs/cst_recognition_level2_ablation`、`outputs/cst_structure_comparison` | 写清 Level 2 full48 accuracy=1.000、结构遮挡 cross-domain accuracy=1.000 与非 full-wave 边界 |
| 8 CST 测试设计 | 标准源、多源、简化载体、扰动 | `docs/phase_03...`、`outputs/cst_level2_superposed_export`、`outputs/cst_structure_comparison` | CST 工程参数表、导出日志和简化结构对照图 |
| 9 误差与鲁棒性 | 噪声、缺测、正则化、姿态扰动、结构遮挡 | 合成鲁棒性、Level 1 指标风险、结构遮挡对照 | CST 误差来源、solver-safe 导出边界、简化结构遮挡边界和 full-wave 增强方向 |
| 10 创新点 | 受限域等效源、测点优化、联合指纹 | 已有草稿 | 与当前真实证据和保守风险口径绑定 |
| 11 复现说明 | 代码、命令、数据字段 | README + scripts | 最终路径和版本锁定 |

## 3. PPT 大纲

建议 12 页，控制在 8-10 分钟：

| 页码 | 标题 | 核心图表/证据 |
|---:|---|---|
| 1 | 题目与方案一句话 | 题目、队伍、总框架图 |
| 2 | 赛题指标拆解 | 评分项映射表 |
| 3 | 国内外方法启发 | 文献方法谱系：NF-FF、等效源、压缩采样、SEI |
| 4 | 总体技术路线 | CST -> nearfield -> 等效源 -> farfield -> recognition |
| 5 | 2π 传感布局 | 半球面测点图、12m x 10m x 8m 包络 |
| 6 | CST Level 1 标准源闭环 | CST 模型截图、重建对比图、NMSE/相关系数 |
| 7 | 三维场重建算法 | 等效源公式、传播矩阵、正则化 |
| 8 | 少测点优化结果 | 测点数-NMSE/相关系数曲线 |
| 9 | Level 2 多源识别 | 多源配置表、混淆矩阵、accuracy/F1 |
| 10 | 结构遮挡与鲁棒性 | 简化结构遮挡方向图、mean/P95/max shadow、cross-domain accuracy |
| 11 | 创新点与工程可行性 | 4 个创新点 + 数据接口闭环 |
| 12 | 总结与提交物 | 最终指标、代码/CST/报告/视频清单 |

## 4. 视频脚本骨架

建议 3-5 分钟，避免只录 PPT 翻页，要展示代码/输出/CST 截图。

| 时间 | 画面 | 解说重点 |
|---|---|---|
| 0:00-0:20 | 题目页 + 总流程图 | 赛题要求是 2π 测量、三维重建、少测点和识别 |
| 0:20-0:50 | 传感布局图 | 半球面 162 测点覆盖 12m x 10m x 8m |
| 0:50-1:30 | CST 标准源截图 + 角域/重建对比 | 展示 FarfieldPlot-derived 角域校准与 CST 真值高度一致，同时说明 full-wave 近场等效源反演边界 |
| 1:30-2:10 | 鲁棒性/测点曲线 | 说明 75% 测点稳健、50% 为压缩候选，但标注为算法参考结果 |
| 2:10-2:50 | Level 2 多源识别混淆矩阵 | 展示 full48 accuracy=1.000，并说明 CST-derived element-library 边界 |
| 2:50-3:20 | 简化结构遮挡方向图对照 | 展示 mean shadow=3.06 dB、P95 shadow=6.63 dB、cross-domain accuracy=1.000，并说明非 full-wave airframe |
| 3:20-3:45 | 代码和复现命令 | 展示校验、重建、识别、结构对照、scorecard 命令 |
| 3:45-4:10 | 总结页 | 对应评分项总结和最终提交物 |

## 5. 三人最终冲刺分工

| 角色 | 最终冲刺重点 | 必交材料 |
|---|---|---|
| A：算法/报告主责 | 重建、测点优化、鲁棒性、报告第 5/6/9/10 章 | 指标表、方向图、误差分析、报告成稿 |
| B：CST 主责 | Level 1/2/3 工程、nearfield/farfield 导出、截图 | `.cst` 工程、CSV、截图、参数表 |
| C：数据/展示主责 | 识别实验、scorecard、PPT、视频、提交包 | 混淆矩阵、PPT、视频脚本、压缩包清单 |

Level 1 标准源阶段的详细日内分工和验收命令见 `docs/level1_cst_sprint_handoff.md`；半球面 CST 建模任务卡见 `outputs/cst_level1_workpack`；已由本机 CST API 生成的两个 required 工程见 `outputs/cst_real_level1_projects`。
项目文件组织和分阶段说明见 `docs/project_file_index.md` 与 `docs/stage_notes`。

## 6. 最终验收门槛

正式打包前必须满足：

1. `src/check_cst_export.py` 对 Level 1/Level 2 当前导出数据返回 `ok: True`。
2. `src/merge_cst_level1_exports.py --strict` 对 Level 1 必做标准源通过，且批量重建输出已归档。
3. Level 1 指标差异已通过角域校准和模型边界说明处理：角域校准高一致性，full-wave 近场等效源反演仍作为后续增强项。
4. `src/merge_cst_level2_exports.py --strict` 通过，48/48 样本完整。
5. `src/run_cst_recognition.py` 在 Level 2 full48 数据上 accuracy >= 0.85，并明确其 CST-derived element-library 证据性质。
6. `src/run_cst_structure_comparison.py` 已生成简化结构遮挡对照，并在报告/PPT 中明确它不是 full-wave airframe scattering。
7. `src/build_scorecard.py` 重新运行后，客观项不再只依赖 synthetic/demo 证据。
8. 报告、PPT、视频中的 demo/synthetic 数字都已替换或明确标注为算法接口/鲁棒性参考。
9. 正式打包前需确认 `submission/01_report/solution_report.pdf`、`solution_report.docx`、`submission/02_presentation/defense_slides.pptx`、`defense_slides.pdf` 和 `submission/03_video/demo_video.mp4` 均已导出并复核；当前 MP4 已生成但为静音自动计时版，需人工播放确认。
10. `src/build_completion_audit.py` 和 `src/build_master_dashboard.py` 重跑后确认 `completion_proven=true`。

`outputs/synthetic_cst_level1_dataset` 可作为代码接口验证附录，但不能计入真实 CST 结果门槛。

## 7. 当前最短路径

1. 人工完整播放 `submission/03_video/demo_video.mp4`，确认自动计时静音版是否满足提交展示要求。
2. 若需要讲解录屏，按同一 PPT 和分镜替换为带人工讲解版本，并保持 Level 1/Level 2 边界口径一致。
3. 如替换视频或修改提交信息，重跑 scorecard、problem requirements、submission index、completion audit、master dashboard、submission draft 和 `build_final_archive.py`。
4. 整理最终压缩包命名、报名表和人工提交信息。
