# 当前工作详细讲解

本文用于给队员、导师或后续接手者解释：这个赛题工作是如何一步步推进的，技术路线为什么这样定，CST 建模产物在哪里，代码分别负责什么，最终提交包如何验证。

## 0. 当前状态一句话

当前项目已经形成一条完整的技术提交链：

```text
赛题要求拆解
  -> 文献筛查与方法迁移
  -> 半球面 2π 测量布局
  -> CST Level 1 标准源校准
  -> CST Level 2 多源/多状态识别样本
  -> Python 重建、识别、消融、结构遮挡对照
  -> 报告、PPT、视频、代码、CST/data、附录
  -> 最终 zip 与 SHA256 清单
```

自动审计的当前结论：

| 项目 | 当前值 |
|---|---:|
| completion audit | 8 complete / 0 partial / 0 missing |
| completion_proven | true |
| submission ready | 65 |
| submission blocked | 0 |
| 最终 zip | `outputs/final_archive/CS-202614_submission.zip` |
| zip SHA256 | 以 `outputs/final_archive/final_archive_summary.json` 为准 |

注意：技术包已经齐套，但正式报送仍需人工填写学校、队伍、申报人、联系电话、报名表等信息；当前 MP4 是 PowerPoint 自动计时静音版，正式提交前建议人工完整播放并按赛事要求决定是否替换为带讲解录屏。

## 1. 赛题要求如何拆解

赛题核心不是“做一张仿真图”，而是完成复杂航空载体电磁辐射空域特性测量方案。我们把要求拆成四类：

| 要求类型 | 赛题含义 | 项目响应 |
|---|---|---|
| 主观方案分 | 国内外调研、技术路线、测试方案完整性 | 文献矩阵、技术路线、阶段说明、报告 |
| 测量系统 | 覆盖 2π 空间，容纳 12m x 10m x 8m 对象 | 13 m 半球面、162 测点、CST workpack |
| 三维重建 | 从有限测点反演/外推远场辐射分布，尽量少测点 | 等效源/Tikhonov 反演、角域校准、鲁棒性扫描 |
| 特征识别 | 空间-频谱特征识别准确率不低于 85% | Level 2 full48 样本，SVM/RF 识别，accuracy=1.000 |

对应的审计文件是：

- `outputs/problem_requirements/problem_requirements_matrix.md`
- `outputs/scorecard/scorecard.md`
- `outputs/completion_audit/completion_audit.md`

这三个文件的作用不同：

- `problem_requirements`：逐条对应赛题原文。
- `scorecard`：按评分点看当前证据。
- `completion_audit`：保守判断是否真的可以说“完成”。

## 2. 总体技术路线

总体路线采用“先标准源、再多源、再结构扰动、最后交付”的方式推进。

```text
半球面测量布局
  -> Level 1 标准源
      目的：校准坐标、相位、极化和数据接口
      输出：nearfield/farfield、角域校准、重建指标
  -> Level 2 多源多状态
      目的：构造识别数据集
      输出：48 个样本、240 个 sample-frequency、混淆矩阵
  -> 简化结构遮挡对照
      目的：说明安装/结构效应会影响方向图，并给出边界
      输出：shadow dB、pattern correlation、cross-domain accuracy
  -> 报告/PPT/视频/zip
      目的：形成可提交材料
```

为什么不一开始就直接做完整复杂机体 full-wave？原因有三个：

1. CST full-wave 复杂载体仿真成本高，容易出现求解失败或导出不稳定。
2. 若直接上复杂结构，坐标、极化、相位、导出格式任何一环出问题都难定位。
3. 评分项需要的是可解释、可复现、可审计的技术链，而不仅是一组复杂模型截图。

因此先用 Level 1 标准源把链路打通，再用 Level 2 样本证明识别能力，最后用简化结构遮挡说明结构边界。

## 3. 半球面测量布局

用户已明确“目前选择半球面”，所以最终主方案采用上半球 2π 测量。

关键参数：

| 参数 | 当前值 |
|---|---:|
| 测量面 | 2π upper hemisphere |
| 半径 | 13 m |
| 空间测点 | 162 |
| 被测包络 | 12m x 10m x 8m |
| 单频双极化等效通道 | 324 |

核心文件：

| 文件 | 意义 |
|---|---|
| `outputs/baseline/sensor_layout_hemisphere.png` | 半球面测点可视化 |
| `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` | 交给 CST 使用的测点表 |
| `outputs/cst_operator_runbook/cst_probe_points_hemisphere_162.csv` | CST 操作侧探针点清单 |
| `code/prepare_cst_templates.py` | 生成 CST 输入模板 |
| `code/run_baseline.py` | 初始布局、合成场、重建基线 |

布局代码在 `code/em_core.py` 中，核心函数是：

- `make_hemisphere_layout()`：生成半球面测点、theta/phi、极化基。
- `spherical_basis()`：建立球坐标方向向量和极化基。
- `farthest_point_subset()`：用于做几何均匀的少测点选择。

## 4. CST 建模路线

### 4.1 CST 数据接口先行

在真实 CST 仿真前，先定义统一数据合同。否则后续重建和识别脚本无法稳定读取数据。

近场表至少需要：

```text
sample_id, sensor_id, x_m, y_m, z_m,
frequency_hz, polarization, e_real, e_imag
```

远场表至少需要：

```text
sample_id, theta_deg, phi_deg, frequency_hz,
e_theta_real, e_theta_imag, e_phi_real, e_phi_imag
```

相关代码：

| 文件 | 作用 |
|---|---|
| `code/cst_io.py` | 读取、校验、坐标/极化转换 |
| `code/check_cst_export.py` | 检查 CST 导出 CSV 是否合格 |
| `code/normalize_cst_complex_columns.py` | 幅相/复数列标准化 |

`cst_io.py` 的关键函数：

- `validate_nearfield()`：检查 nearfield 必需列、数值列、重复行、测点一致性。
- `validate_farfield()`：检查 farfield 必需列、复数远场或增益列。
- `validate_pair()`：检查 nearfield 和 farfield 的 sample/frequency 是否匹配。
- `cartesian_to_theta_phi_rows()`：将 Ex/Ey/Ez 投影到 theta/phi 极化。

### 4.2 Level 1 标准源

Level 1 的目标是“校准链路”，不是追求复杂结构。它回答这些问题：

- 坐标方向是否正确？
- 极化定义是否一致？
- CST 导出的场能否被 Python 读入？
- Python 重建是否能和 CST 远场对上？

产物：

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_level1_plan` | Level 1 标准源计划 |
| `outputs/cst_level1_workpack` | 给 CST 建模/导出的任务包 |
| `outputs/cst_real_level1_projects` | 本机 CST API 生成的 Level 1 工程证据 |
| `outputs/cst_solver_ready_level1_projects` | solver-safe 版本工程 |
| `outputs/cst_farfield_export` | CST FarfieldPlot 导出记录 |
| `outputs/cst_level1_merge_report` | Level 1 严格合并审计 |
| `outputs/cst_level1_reconstruction_batch` | Level 1 批量重建结果 |
| `outputs/cst_level1_angular_calibration` | Level 1 角域校准结果 |

关键结果：

| 指标 | 当前值 |
|---|---:|
| required cases | 2/2 complete |
| angular max NMSE | 8.41e-5 |
| angular min correlation | 0.99988 |
| angular max main-lobe error | 0.0 deg |

这里要注意一个边界：当前高精度结论是 FarfieldPlot-derived 角域一致性，不应夸大为 full-wave near-field monitor 等效源反演已经完全解决。报告/PPT 中已经保守说明了这一点。

### 4.3 Level 2 多源多状态识别

Level 2 的目标是“构造可识别的数据集”。它模拟多源、多频、多状态的辐射样本，然后用空间-频谱-极化特征做识别。

产物：

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_level2_plan` | Level 2 样本计划 |
| `outputs/cst_level2_workpack` | Level 2 建模任务包 |
| `outputs/cst_level2_element_library` | 三方向 element-library 工程 |
| `outputs/cst_level2_element_trials` | element 求解试验 |
| `outputs/cst_level2_superposed_export` | full48 叠加导出日志 |
| `outputs/cst_level2_merge_report` | Level 2 严格合并审计 |
| `outputs/cst_recognition_level2` | Level 2 识别结果 |
| `outputs/cst_recognition_level2_ablation` | 测点/频点消融结果 |

关键结果：

| 指标 | 当前值 |
|---|---:|
| planned samples | 48 |
| complete samples | 48 |
| sample-frequency rows | 240 |
| recognition features | 4965 |
| best accuracy | 1.000 |
| ablation min accuracy | 1.000 |

识别代码主要在 `code/run_cst_recognition.py`：

- `ensure_theta_phi()`：确保输入变成 theta/phi 极化。
- `normalized_nearfield()`：整理 sample、sensor、frequency、坐标。
- `spatial_summary()`：提取空间能量分布、质心、熵等特征。
- `response_features()`：提取幅度、相位、极化功率比、空间摘要。
- `build_feature_matrix()`：把每个 sample 变成机器学习特征向量。
- SVM/RF：用于分类不同源组合/运行状态。

### 4.4 简化结构遮挡对照

Level 2 full48 是 CST-derived element-library 叠加证据。为了不把它误说成完整复杂机体 full-wave 结构散射，增加了简化结构遮挡对照。

产物：

| 文件/目录 | 意义 |
|---|---|
| `code/run_cst_structure_comparison.py` | 结构遮挡迁移、方向图偏差、跨域识别 |
| `outputs/cst_structure_comparison/structure_comparison_summary.json` | 结构对照总指标 |
| `outputs/cst_structure_comparison/structure_comparison_metrics.csv` | sample-frequency 级指标 |
| `outputs/cst_structure_comparison/plots/*_structure_compare.png` | 方向图对比图 |

关键结果：

| 指标 | 当前值 |
|---|---:|
| sample count | 48 |
| sample-frequency count | 240 |
| mean shadow | 3.06 dB |
| P95 shadow | 6.63 dB |
| max shadow | 13.33 dB |
| mean pattern correlation | 0.730 |
| cross-domain accuracy | 1.000 |

解释口径：

- 它证明结构/安装效应会改变方向图。
- 它证明当前识别特征在这种扰动下仍保持稳定。
- 它不是 full-wave CST airframe scattering。
- 在答辩中要把它说成 bounded structure evidence，而不是完整复杂机体散射结论。

## 5. 重建算法如何工作

重建算法的核心是等效源反演。

数学形式：

```text
y = G j + n
```

其中：

- `y`：半球面测得的近场复数值。
- `G`：等效源到测点的传播矩阵。
- `j`：待求等效源系数。
- `n`：噪声或模型误差。

反演采用 Tikhonov 正则：

```text
j_hat = argmin ||G j - y||^2 + lambda ||j||^2
```

在 `code/em_core.py` 中对应：

| 函数 | 作用 |
|---|---|
| `make_equivalent_grid()` | 建立等效源网格 |
| `build_measurement_matrix()` | 构建测量矩阵 G |
| `solve_tikhonov()` | 正则化反演等效源 |
| `vector_to_source_set()` | 将解向量变回源集合 |
| `farfield_pattern()` | 由等效源外推远场方向图 |
| `pattern_metrics()` | 计算 NMSE、相关系数、主瓣误差、峰值误差 |

相关脚本：

| 脚本 | 作用 |
|---|---|
| `code/run_cst_reconstruction.py` | 单个 CST 样本重建 |
| `code/run_cst_level1_batch_reconstruction.py` | Level 1 批量重建 |
| `code/run_cst_level1_angular_calibration.py` | 角域基函数校准 |
| `code/run_reconstruction_robustness.py` | 少测点和噪声鲁棒性扫描 |

鲁棒性结果示例：

| 指标 | 当前值 |
|---|---:|
| baseline opt50 NMSE | 8.36e-4 |
| baseline opt50 correlation | 0.99864 |
| robust 30dB opt75 NMSE | 1.13e-3 |
| robust 30dB opt75 correlation | 0.99834 |

## 6. 代码结构讲解

`code` 中脚本可按六组理解。

### 6.1 基础电磁与算法

| 文件 | 作用 |
|---|---|
| `em_core.py` | 半球面测点、等效源、传播矩阵、Tikhonov、远场和指标 |
| `run_baseline.py` | 合成 baseline，验证布局和算法链路 |
| `run_reconstruction_robustness.py` | 噪声/少测点鲁棒性 |

这组代码相当于“算法发动机”。

### 6.2 CST 数据接口

| 文件 | 作用 |
|---|---|
| `cst_io.py` | 读表、校验、极化转换、构造测量向量 |
| `check_cst_export.py` | 单次导出校验 |
| `normalize_cst_complex_columns.py` | 幅相/复数格式标准化 |

这组代码保证 CST 文件可以被 Python 稳定读取。

### 6.3 CST 准备和自动化

| 文件 | 作用 |
|---|---|
| `prepare_cst_templates.py` | CST 测点/导出模板 |
| `prepare_cst_macro_templates.py` | CST 宏模板和批处理输入表 |
| `prepare_cst_level1_manifest.py` | Level 1 标准源计划 |
| `prepare_cst_level1_workpack.py` | Level 1 建模任务包 |
| `prepare_cst_level2_manifest.py` | Level 2 样本计划 |
| `prepare_cst_level2_workpack.py` | Level 2 建模任务包 |
| `run_cst_level1_required_automation.py` | 本机 CST API 生成 Level 1 工程 |
| `run_cst_solver_project.py` | CST solver-safe 求解 |
| `export_cst_farfield_results.py` | FarfieldPlot 导出 |
| `run_cst_level2_element_library.py` | Level 2 element-library 工程/数据 |
| `export_cst_level2_superposed_results.py` | Level 2 full48 叠加导出 |

这组代码相当于“CST 工程生产线”。

### 6.4 合并、重建、识别

| 文件 | 作用 |
|---|---|
| `merge_cst_level1_exports.py` | Level 1 strict merge |
| `merge_cst_level2_exports.py` | Level 2 strict merge |
| `run_cst_level1_batch_reconstruction.py` | Level 1 批量重建 |
| `run_cst_level1_angular_calibration.py` | Level 1 角域校准 |
| `run_cst_recognition.py` | Level 2 特征识别 |
| `run_cst_recognition_ablation.py` | 测点/频点删减消融 |
| `run_cst_structure_comparison.py` | 简化结构遮挡对照 |

这组代码直接产生评分指标。

### 6.5 审计与交付

| 文件 | 作用 |
|---|---|
| `build_scorecard.py` | 评分项证据板 |
| `build_problem_requirements_matrix.py` | 赛题要求矩阵 |
| `build_completion_audit.py` | 完成度 gate 审计 |
| `build_master_dashboard.py` | 总控仪表盘 |
| `build_submission_index.py` | 提交物索引 |
| `build_submission_draft.py` | 生成 `submission` 草稿包 |
| `build_final_archive.py` | 最终 zip 和 SHA256 |
| `build_progress_report.py` | 阶段进展和导师汇报 |

这组代码回答“现在到底完成没完成”。

### 6.6 报告、PPT、视频

| 文件 | 作用 |
|---|---|
| `build_final_report_docx.py` | 从草稿和图表生成正式 DOCX |
| `build_defense_pptx_artifact.py` | 生成答辩 PPTX |
| `export_demo_video_powerpoint.ps1` | PowerPoint 自动计时导出 MP4 |

这组代码把技术证据转成交付物。

## 7. 主要输出目录讲解

### 7.1 `docs`

`docs` 是“人读的解释层”。

| 路径 | 作用 |
|---|---|
| `docs/literature_matrix.md` | 文献矩阵 |
| `docs/literature_to_algorithm_traceability.md` | 文献到算法的迁移链 |
| `docs/team_division_technical_route.md` | 三人分工与技术路线 |
| `docs/solution_report_draft.md` | 报告草稿源 |
| `docs/final_submission_package_plan.md` | 最终提交计划 |
| `docs/stage_notes` | 每阶段说明 |
| `docs/admin_submission_template.md` | 人工报名信息模板 |
| `docs/current_work_detailed_explanation.md` | 本文 |

### 7.2 `outputs`

`outputs` 是“机器生成证据层”。

| 目录 | 作用 |
|---|---|
| `baseline` | 半球面布局和 baseline 图表 |
| `cst_templates` | CST 输入模板 |
| `cst_level1_*` | Level 1 计划、任务包、合并、重建、角域校准 |
| `cst_level2_*` | Level 2 计划、任务包、element-library、导出、合并 |
| `cst_recognition_level2` | Level 2 识别结果 |
| `cst_recognition_level2_ablation` | 消融实验 |
| `cst_structure_comparison` | 简化结构遮挡对照 |
| `scorecard` | 评分证据板 |
| `problem_requirements` | 赛题要求矩阵 |
| `completion_audit` | 完成度审计 |
| `master_dashboard` | 总控仪表盘 |
| `final_report` | 报告 PDF 渲染检查 |
| `presentation_artifact` | PPT 导出和检查 |
| `video_artifact` | 视频导出摘要 |
| `final_archive` | 最终 zip 和 hash |

### 7.3 `submission`

`submission` 是“提交包内容层”。

| 目录 | 作用 |
|---|---|
| `00_admin` | 人工报名信息模板 |
| `01_report` | 正式报告 PDF/DOCX |
| `02_presentation` | 答辩 PPTX/PDF |
| `03_video` | 演示视频 MP4 |
| `04_code` | 可复现代码和命令 |
| `05_cst` | CST 工程、任务包、导出和审计证据 |
| `06_data` | 数据、图表、指标 |
| `07_appendix` | 文献、审计、阶段说明等附录 |

最终 zip 位于：

```text
outputs/final_archive/CS-202614_submission.zip
```

## 8. 工作是如何一步步推进的

可以按 8 个大阶段讲。

### 阶段 A：读赛题，定路线

做了什么：

- 读赛题 PDF。
- 拆成主观分、客观分、交付物、提交方式。
- 建立文献筛查和方法迁移路径。

产物：

- `docs/literature_matrix.md`
- `docs/literature_screening_and_strategy.md`
- `docs/literature_to_algorithm_traceability.md`
- `docs/team_division_technical_route.md`

为什么这样做：

评分不仅看结果，也看路线是否合理。先把评分项映射到证据文件，后面不会“做了很多但不知道怎么得分”。

### 阶段 B：定半球面测量系统

做了什么：

- 选择上半球 2π 测量。
- 设计 13 m 半径、162 测点。
- 生成 CST 测点模板。

产物：

- `outputs/baseline/sensor_layout_hemisphere.png`
- `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`

为什么这样做：

半球面能满足 2π 要求，也比半柱面更容易在报告中讲清楚三维覆盖和远场外推。

### 阶段 C：建立 CST 数据合同

做了什么：

- 统一 nearfield/farfield CSV 字段。
- 写校验脚本。
- 写幅相转换和 Ex/Ey/Ez 到 theta/phi 转换。

产物：

- `code/cst_io.py`
- `code/check_cst_export.py`
- `code/normalize_cst_complex_columns.py`
- `docs/data_dictionary.md`

为什么这样做：

CST 导出格式如果不统一，后面重建和识别都会变成手工修表，无法复现。

### 阶段 D：Level 1 标准源闭环

做了什么：

- 生成标准源计划和 workpack。
- 通过本机 CST API 生成/求解 solver-safe 工程。
- 导出 FarfieldPlot 数据。
- 做 strict merge、批量重建和角域校准。

产物：

- `outputs/cst_real_level1_projects`
- `outputs/cst_solver_ready_level1_projects`
- `outputs/cst_farfield_export`
- `outputs/cst_level1_merge_report`
- `outputs/cst_level1_reconstruction_batch`
- `outputs/cst_level1_angular_calibration`

为什么这样做：

标准源用于先校准坐标、相位和极化。如果标准源都不闭环，复杂载体结果没有可信度。

### 阶段 E：Level 2 多源识别

做了什么：

- 设计 48 个多源/多状态样本。
- 用 element-library 路线生成 240 个 sample-frequency。
- 合并数据，提取空间-频谱-极化特征。
- 训练 SVM/RF，输出混淆矩阵和消融实验。

产物：

- `outputs/cst_level2_workpack`
- `outputs/cst_level2_superposed_export`
- `outputs/cst_level2_merge_report`
- `outputs/cst_recognition_level2`
- `outputs/cst_recognition_level2_ablation`

为什么这样做：

赛题要求识别准确率不低于 85%。Level 2 直接对应这一条，最终 accuracy=1.000。

### 阶段 F：结构遮挡边界

做了什么：

- 在 Level 2 数据上施加简化机身/机翼/尾翼遮挡迁移。
- 统计方向图变化。
- 检查跨域识别稳定性。

产物：

- `code/run_cst_structure_comparison.py`
- `outputs/cst_structure_comparison`

为什么这样做：

避免把 element-library 叠加误说成完整 full-wave airframe scattering。我们既给出结构影响的量化证据，也明确它的边界。

### 阶段 G：报告、PPT、视频

做了什么：

- 从报告草稿生成 DOCX/PDF。
- 生成 12 页答辩 PPTX/PDF。
- 用 PowerPoint 导出演示 MP4。

产物：

- `submission/01_report/solution_report.pdf`
- `submission/01_report/solution_report.docx`
- `submission/02_presentation/defense_slides.pptx`
- `submission/02_presentation/defense_slides.pdf`
- `submission/03_video/demo_video.mp4`

为什么这样做：

赛题明确要求报告、PPT、视频/录屏和代码等材料。技术结果必须转化为正式交付物。

### 阶段 H：审计与最终打包

做了什么：

- 生成 scorecard、requirements matrix、submission index、completion audit、master dashboard。
- 生成 submission 草稿包。
- 生成最终 zip 和 SHA256 manifest。

产物：

- `outputs/completion_audit/completion_audit_summary.json`
- `outputs/master_dashboard/master_dashboard_summary.json`
- `outputs/final_archive/CS-202614_submission.zip`
- `outputs/final_archive/final_archive_manifest.csv`

为什么这样做：

最终不能只说“我觉得完成了”，要有自动审计和可核验压缩包。

## 9. 如何向导师或评委讲

建议按这个顺序讲：

1. 我们先把赛题拆成四类：调研路线、2π 测量、远场重建、特征识别。
2. 测量系统选择 13 m 半球面，162 测点覆盖 12m x 10m x 8m 包络。
3. CST 不直接上复杂机体，而是 Level 1 标准源先校准链路。
4. Level 1 的角域校准和 CST 远场高度一致，证明 solver-safe 数据链可信。
5. Level 2 构建 48 个多源多状态样本，空间-频谱-极化特征识别准确率达到 1.000。
6. 为了说明结构边界，又做了简化结构遮挡对照，mean shadow 3.06 dB，跨域识别仍为 1.000。
7. 所有结果进入报告、PPT、视频和最终 zip，completion audit 为 true。
8. 保守边界：Level 1 角域校准不是 full-wave 近场 monitor 反演；Level 2 结构对照不是完整 full-wave airframe scattering。

## 10. 仍需人工注意的地方

虽然技术包已经自动审计通过，但人工提交前仍要注意：

1. 完整播放 `submission/03_video/demo_video.mp4`。
2. 当前视频是静音自动计时版；如赛事要求讲解录屏，应替换为带讲解版本。
3. 填写 `submission/00_admin/admin_submission_template.md` 中的学校、队名、申报人、联系方式和报名表信息。
4. 按赛事要求重命名 `outputs/final_archive/CS-202614_submission.zip`。
5. 如果替换视频或修改提交包内容，重新运行：

```powershell
python code\build_submission_draft.py
python code\build_final_archive.py
python code\build_completion_audit.py
```

## 11. 推荐阅读顺序

如果你只想快速理解项目：

1. `docs/current_work_detailed_explanation.md`
2. `outputs/master_dashboard/master_status_dashboard.md`
3. `outputs/completion_audit/completion_audit.md`
4. `docs/stage_notes/README.md`
5. `submission/README_FINAL_SUBMISSION.md`

如果你要看技术细节：

1. `docs/team_division_technical_route.md`
2. `docs/literature_to_algorithm_traceability.md`
3. `code/em_core.py`
4. `code/cst_io.py`
5. `code/run_cst_level1_angular_calibration.py`
6. `code/run_cst_recognition.py`
7. `code/run_cst_structure_comparison.py`

如果你要准备提交：

1. `submission/README_FINAL_SUBMISSION.md`
2. `submission/00_admin/admin_submission_template.md`
3. `outputs/final_archive/final_archive_summary.json`
4. `outputs/final_archive/CS-202614_submission.zip`
