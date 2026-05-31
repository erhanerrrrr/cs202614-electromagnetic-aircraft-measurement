# Demo video storyboard

## 0:00-0:20

- Screen: 题目页 + 总流程图
- Narration: 本方案面向 2π 空域测量、三维场重建、少测点和辐射指纹识别，采用 CST-Python 闭环。
- Linked slide(s): 1,4
- Current asset: final title/summary screen
- Replacement: 最终队伍信息、Level 1/2 指标摘要和 G5 风险一句话。

## 0:20-0:50

- Screen: 半球面测点布局
- Narration: 当前执行选择 13 m 半径上半球面 162 个测点，覆盖 12m x 10m x 8m 被测包络。
- Linked slide(s): 5
- Current asset: `outputs/baseline/sensor_layout_hemisphere.png`
- Replacement: CST 中实际 monitor/测点截图或已生成测点表路径。

## 0:50-1:30

- Screen: Level 1 标准源 CST 截图 + 重建对比
- Narration: 标准源用于校验坐标、极化和相位。当前 solver-safe 导出来自 FarfieldPlot 角域采样，角域校准与 CST 远场真值高度一致；等效源近场反演作为模型风险单独说明。
- Linked slide(s): 6,7
- Current asset: `outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png`
- Replacement: 同步讲清 Level 1 模型边界：角域一致性高，但 full-wave 近场 monitor 反演仍需后续增强。

## 1:30-2:10

- Screen: 测点删减与鲁棒性曲线
- Narration: 用全测点、随机稀疏、优化稀疏对照，给出精度和测点数的折中。
- Linked slide(s): 8,10
- Current asset: `outputs/reconstruction_robustness/reconstruction_sensor_tradeoff_30dB.png`
- Replacement: 标注为算法鲁棒性参考，避免替代 Level 1 required 结论。

## 2:10-2:50

- Screen: Level 2 多源识别混淆矩阵
- Narration: 识别模块融合空间、频谱和极化特征，当前 Level 2 full48 准确率达到 1.000，超过 85% 指标。
- Linked slide(s): 9
- Current asset: `outputs/cst_recognition_level2/cst_recognition_confusion_matrix.png`
- Replacement: 补充 CST-derived element-library 边界说明。

## 2:50-3:20

- Screen: 简化结构遮挡方向图对照
- Narration: 进一步把简化机身、机翼和尾翼遮挡迁移施加到 Level 2 数据上，量化安装效应，并检验跨域识别稳健性。
- Linked slide(s): 10
- Current asset: `outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png`
- Replacement: 强调它是 bounded structure evidence，不是 full-wave airframe scattering。

## 3:20-3:45

- Screen: 代码复现命令与 dashboard
- Narration: 展示导出校验、批量合并、重建、识别、scorecard 和 completion audit 命令，证明可复现。
- Linked slide(s): 11,12
- Current asset: `outputs/master_dashboard/master_status_dashboard.md`
- Replacement: 展示最新 G5 状态和最终审计。

## 3:45-4:10

- Screen: 总结页
- Narration: 总结最终指标、创新点和提交物。正式视频只在真实 CST 证据与报告/PPT一致后录制。
- Linked slide(s): 12
- Current asset: final title/summary screen
- Replacement: 最终 completion audit 和提交包截图。
