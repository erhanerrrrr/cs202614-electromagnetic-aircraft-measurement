# Defense slide storyboard

## 1. 题目与一句话方案

- Purpose: 用一句话说明本方案是物理约束的空-频-极化联合等效源重构与受限域压缩测量。
- Visual: title_only
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: 最终队伍名、成员、真实指标摘要。
- Speaker note: 开场强调：我们不是只做 CST 截图，而是建立可复现的 CST-Python 测量、重建、识别闭环。

## 2. 赛题指标拆解

- Purpose: 把 2π 覆盖、12m x 10m x 8m 包络、重建精度、少测点、85% 识别准确率映射到证据。
- Visual: table
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: scorecard 中核心项不再是 Needs CST evidence。
- Speaker note: 说明评分项对应的文件、脚本和最终证据，避免评委觉得只是概念方案。

## 3. 国内外方法启发

- Purpose: 展示标准近场测量、等效源重构、压缩采样、RF 指纹四条文献主线。
- Visual: citation_map
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: 参考文献格式统一。
- Speaker note: 用 IEEE 149/1720、IEEE TAP、IEEE TSP/JSTSP、RF 指纹文献支撑方法选择。

## 4. 总体技术路线

- Purpose: CST 导出 nearfield/farfield，自研 Python 完成等效源重建、少测点优化和识别。
- Visual: pipeline_diagram
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: 加入 Level 1/Level 2 当前真实输出路径、指标摘要和 G5 风险边界。
- Speaker note: 强调 CST 是可信数据源，自研算法负责重建和识别，避免直接调用 CST farfield 当结果。

## 5. 2π 半球面传感布局

- Purpose: 展示半球面 162 测点与 12m x 10m x 8m 包络。
- Visual: layout_figure
- Current source: `outputs/baseline/sensor_layout_hemisphere.png`
- Source status: `draft_ready`
- Replacement: 用 CST 工程中的测点/包络截图补强。
- Speaker note: 说明当前选择半球面，半柱面作为工程扩展，不混入本轮执行。

## 6. Level 1 标准源闭环

- Purpose: 展示 required 标准源、导出路径、审计和重建指标。
- Visual: result_figure
- Current source: `outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png`
- Source status: `cst_angular_ready`
- Replacement: 说明该图验证 solver-safe 角域一致性，不等同于 full-wave 近场 monitor 反演。
- Speaker note: 先讲短偶极子和半波振子为什么用于坐标、相位、极化 sanity check，再解释角域校准与等效源近场反演的边界。

## 7. 三维场重建算法

- Purpose: 解释 E_meas = G_nf J + n、Tikhonov/稀疏正则化、远场外推。
- Visual: formula_slide
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: 用 Level 1 required 结果证明链路可复现，同时说明精度风险和改进方向。
- Speaker note: 把公式讲成输入、传播矩阵、等效源、输出远场，不陷入数学细枝末节。

## 8. 少测点优化结果

- Purpose: 展示 100/75/50/25% 测点曲线和当前压缩结论。
- Visual: tradeoff_chart
- Current source: `outputs/reconstruction_robustness/reconstruction_sensor_tradeoff_30dB.png`
- Source status: `reference_only`
- Replacement: 作为算法鲁棒性参考保留；若用于高精度结论，需用 Level 1/结构样本复跑或明确边界。
- Speaker note: 说明当前合成结果显示 75% 稳健、50% 可候选，25% 只做极限对照。

## 9. Level 2 多源识别

- Purpose: 展示四类状态、多频多源、混淆矩阵和 accuracy/F1。
- Visual: confusion_matrix
- Current source: `outputs/cst_recognition_level2/cst_recognition_confusion_matrix.png`
- Source status: `cst_derived_ready`
- Replacement: 说明当前证据来自 CST-derived element-library superposition，补充结构散射边界。
- Speaker note: 强调识别不是单张方向图，而是空间、频谱、极化、等效源联合指纹。

## 10. 结构遮挡对照与边界

- Purpose: 展示简化载体遮挡前后方向图变化、遮挡 dB 和 cross-domain 识别结果。
- Visual: structure_comparison_chart
- Current source: `outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png`
- Source status: `bounded_structure_ready`
- Replacement: 说明该图是简化 aircraft occlusion transfer，不是 full-wave airframe scattering；用于约束 element-library 证据边界。
- Speaker note: 说明该结果是 simplified aircraft occlusion transfer，用于约束 element-library 证据边界；full-wave airframe 仍是增强项。

## 11. 创新点与工程可行性

- Purpose: 总结受限域等效源、少测点优化、空频极化指纹、可复现 CST-Python 闭环。
- Visual: innovation_summary
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: 最终指标表、工程截图、Level 1 风险说明和 Level 2 边界说明齐全。
- Speaker note: 把创新点和赛题评分逐项绑定。

## 12. 总结与提交物

- Purpose: 用最终指标和提交包结构收束。
- Visual: closing_checklist
- Current source: text/diagram placeholder
- Source status: `draft_text`
- Replacement: completion_proven=true；最终 PDF/DOCX/PPTX/MP4 存在。
- Speaker note: 最后明确交付物包括报告、PPT、视频、代码、CST 工程、数据和附录。
