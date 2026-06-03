# 复杂航空载体电磁辐射空域特性测量技术方案报告（G5 成稿草稿）

题目编号：CS-202614  
发榜单位：电磁空间安全全国重点实验室  
版本：v0.2 G5 成稿草稿  
状态：Level 1 required、Level 2 full48、简化结构遮挡对照和 Level 2 复合扰动压力测试证据已接入；既有 PDF/DOCX/PPTX/MP4 已导出过，但本轮需把 Level 1 角域/近场模型边界、Level 2 非 full-wave 结构边界，以及复合仪器误差/结构缺测下的插补缓解口径同步到成稿并复核导出件。

## 摘要

本方案面向复杂航空载体电磁辐射发射空域特性的高效获取、三维场域重建与空间-频谱特征辨识需求，提出“物理约束的空-频-极化联合等效源重构与受限域压缩测量方法”。当前执行路线采用半球面 2π 空域分布式宽带电磁传感布局，通过 CST 建立标准源、多源和简化航空载体仿真模型，导出近场复数数据和远场参考真值；在算法侧构建等效源/Huygens 面反演模型，采用 Tikhonov/SVD 稳定反演与稀疏测点优化实现远场方向图重建；进一步提取方向图形态、频谱分布、极化比和等效源能量分布等联合特征，训练 SVM/随机森林等识别模型，实现不同载体与运行状态的有效区分。半柱面布局作为后续工程扩展备选，不进入本轮 CST 执行。

当前已完成文献筛查、CST 数据模板、导出校验脚本、早期接口验证基线、Level 1 required 标准源合并审计与批量重建、Level 1 FarfieldPlot-derived 角域校准、Level 2 full48 CST-derived element-library 样本合并、识别、删减验证、简化结构遮挡对照和复合仪器误差/结构缺测压力测试。Level 1 required 两个标准源的角域校准最大 NMSE 为 `8.41e-5`、最小相关系数为 `0.99988`，说明 solver-safe 角域数据与 CST 远场网格高度一致；等效源近场反演指标偏弱，需要作为模型边界说明。Level 2 当前 48/48 样本完整，SVM RBF 识别准确率达到 `1.000`；简化结构遮挡迁移下 cross-domain accuracy 仍为 `1.000`。新增 severe compound instrument/dropout pressure test 显示，原始 `zero_fill`/`mask_features` 策略会出现低于 0.85 的失败行，worst accuracy=`0.733`；`freq_sensor_median_impute` 的最小 accuracy=`0.867`，可作为当前工程缓解策略。必须说明这些证据是 CST-derived element-library + simplified occlusion/perturbation transfer，不等同于 full-wave airframe scattering 或实测标定结论。

## 1. 赛题理解与评分指标分解

### 1.1 赛题核心任务

赛题要求不是传统单点电磁测试，而是完整技术链：

```text
分布式宽带电磁传感布局
-> 2π 空域近场/全景采集
-> 近远场关联建模
-> 三维场域重建
-> 少测点优化
-> 空间-频谱辐射特征辨识
```

### 1.2 硬性指标

| 赛题要求 | 本方案响应 | 当前证据 | 剩余风险 |
|---|---|---|---|
| 覆盖 2π 空间立体角的测量区域 | 当前采用 13 m 半球面 162 测点，后续可扩展半柱面 | `outputs/baseline/sensor_layout_hemisphere.png`、`outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`，并已用于 Level 1/2 数据链 | 最终报告需补 CST 工程截图 |
| 可容纳不小于 12 m x 10 m x 8 m 被测对象 | 被测空间包络设为 x ±6 m、y ±5 m、z 0-8 m | baseline 布局图已画出包络；提交包中保留测点/包络证据 | CST 模型截图与参数记录仍需进入报告/PPT |
| 支撑远区辐射分布有效推算 | 等效源反演 + 远场外推 | `outputs/cst_level1_merge_report`、`outputs/cst_level1_reconstruction_batch`、`outputs/cst_reconstruction/L1_*` | Level 1 指标偏弱，需误差机理说明或继续优化 |
| 高精度重建且尽量减少测点 | 全测点、随机稀疏、优化稀疏对照 | `outputs/reconstruction_robustness`；Level 1 required 已完成 2 个重建案例 | 少测点结论仍需结合 Level 1 指标风险说明边界 |
| 空间频率特征辨识精度不低于 85% | 空-频-极化联合特征 + SVM/随机森林 + 复合扰动插补策略 | Level 2 48/48 样本完整，`outputs/cst_recognition_level2` 中 best_accuracy=`1.000`；简化结构遮挡 cross-domain accuracy=`1.000`；复合仪器误差/结构缺测下 `freq_sensor_median_impute` 最小 accuracy=`0.867` | 需说明 CST-derived element-library、simplified occlusion/perturbation transfer、原始 zero-fill 失败边界与 full-wave airframe/实测标定的边界 |

### 1.3 评分项映射

| 评分项 | 分值 | 报告章节 | 关键证据 |
|---|---:|---|---|
| 国内外发展调研分析 | 10 | 第 2 章 | `docs/literature_matrix.md` |
| 研究思路合理性 | 10 | 第 3 章 | 标准源 -> 多源 -> 简化载体递进路线 |
| 技术路线可行性 | 10 | 第 3-7 章 | CST-Python 闭环脚本与分级验证 |
| 测试方案完整性 | 10 | 第 4、8、9 章 | 数据字段、校验脚本、指标体系 |
| 传感布局覆盖 | 10 | 第 4 章 | 当前 2π 半球面布局、尺寸包络 |
| 三维场域重建 | 30 | 第 5-6 章 | 重建指标、测点压缩曲线 |
| 特征辨识精度 | 20 | 第 7 章 | 准确率、F1、混淆矩阵 |

## 2. 国内外发展调研

### 2.1 天线测量与近场测量规范

IEEE 149-2021 提供天线测量通用推荐实践，IEEE 1720-2012 专门面向近场测量，覆盖平面、柱面、球面扫描几何、探头校准和近远场变换。Yaghjian 的经典综述系统总结了近场测量理论、采样要求和误差来源。这些文献说明，本赛题应采用标准化近场测量数据格式，而不能只给出概念性的传感器布设图。

核心引用：L01-L03。

### 2.2 近远场变换与等效源重构

复杂航空载体具备大尺寸、复杂结构、多源协同和安装效应，传统规则球面/柱面 NF-FF 变换虽然成熟，但难以完整处理不规则测量与平台散射问题。IEEE TAP 中关于任意曲面 NF-FF、表面源重构条件、平台等效表示的研究表明，等效源/Huygens 面反演适合将复杂辐射体替换为可计算、可诊断的等效源分布。

核心引用：L04-L06、L10-L13。

### 2.3 压缩感知与测点优化

赛题客观分对“精度高、测点少”高度敏感。受限域压缩感知和球面感知矩阵优化研究说明，当辐射场在合适基或等效源表示下具备稀疏性，可以通过优化采样点降低测量数量。近年的多频球面近场压缩测量研究进一步说明，宽带/多频测量中可利用频点间共享结构，用稀疏或低秩模型继续降低采样需求。EMC 领域自适应近场扫描也提供了顺序采样和不确定度驱动加密的思路。

核心引用：L07-L08、L14-L16、L25。

### 2.4 RF/雷达辐射指纹识别

RF 指纹和特定辐射源识别研究说明，单一幅度特征通常不足以实现稳定识别，需要融合瞬态、稳态、频谱、相位和硬件非理想特征。真实雷达 SEI 研究进一步说明，相干积分、VMD 和多特征提取有助于放大微弱个体差异。本赛题中可利用空间方向图、频谱结构、极化特征和等效源分布构造更加贴合航空载体的空-频-极化辐射指纹。

核心引用：L17-L24。

## 3. 总体研究思路与技术路线

### 3.1 总体思路

本方案采用“由简到繁、物理先行、数据增强”的路线：

1. 标准源闭环：短偶极子/半波振子，校验 CST 导出与 Python 重建。
2. 多源闭环：多个等效辐射源、多频点、多极化，构造可控空频数据集。
3. 简化载体闭环：金属机身、机翼、尾翼和典型安装位置，体现遮挡、散射和安装效应。
4. 测点优化闭环：全测点、随机稀疏、规则稀疏、优化稀疏对照。
5. 特征辨识闭环：空-频-极化-等效源联合特征，达到 85% 以上识别准确率。

### 3.2 工具链

| 模块 | 工具 | 作用 |
|---|---|---|
| 电磁仿真 | CST | 标准源、多源、简化载体建模；近场/远场数据导出 |
| 数据接口 | Python/pandas | CST CSV 校验、字段转换、sample_id 管理 |
| 重建算法 | Python/numpy/scipy | 等效源传播矩阵、Tikhonov/SVD/L1 反演、远场外推 |
| 识别算法 | scikit-learn/PyTorch | SVM、随机森林、CNN/度量学习拓展 |
| 图表展示 | matplotlib/Plotly/PPT | 测点布局、方向图、误差热图、混淆矩阵 |

### 3.3 当前已实现代码

| 文件 | 功能 |
|---|---|
| `code/em_core.py` | 传感布局、等效源场计算、传播矩阵、反演、远场和指标 |
| `code/run_baseline.py` | 早期接口基线：布局、重建、测点优化、识别 |
| `code/prepare_cst_templates.py` | 生成 CST 测点和导出模板 |
| `code/check_cst_export.py` | 校验 CST nearfield/farfield CSV |
| `code/run_cst_reconstruction.py` | CST 数据导入、等效源重建、远场真值对比 |
| `code/run_cst_recognition.py` | 从 CST nearfield 表格提取空-频-极化特征并训练识别模型 |
| `code/prepare_cst_level2_manifest.py` | 生成 Level 2 多源多状态 CST 执行清单和源配置表 |
| `code/run_cst_recognition_ablation.py` | 对 CST 格式识别数据做测点/频点删减验证 |
| `code/merge_cst_level2_exports.py` | 合并 Level 2 批量 CST 导出并生成缺漏/完整性报告 |
| `code/run_reconstruction_robustness.py` | 扫描噪声、测点比例和正则化参数对重建精度的影响 |
| `code/build_scorecard.py` | 自动汇总评分项证据、关键指标和最终缺口 |
| `code/build_submission_index.py` | 自动生成最终提交包索引和打包缺口清单 |
| `code/normalize_cst_complex_columns.py` | 将 CST 幅值/相位导出归一化为实部/虚部复数字段 |
| `code/prepare_cst_level1_manifest.py` | 生成 Level 1 标准源 CST 执行清单、源参数和验证门槛 |
| `code/merge_cst_level1_exports.py` | 合并并审计 Level 1 标准源 CST 导出，生成缺漏报告和重建队列 |
| `code/run_cst_level1_batch_reconstruction.py` | 对已完整 Level 1 标准源案例批量执行等效源重建并聚合指标 |
| `code/prepare_cst_level1_workpack.py` | 生成半球面 Level 1 CST 建模任务包、导出核对表和单案例任务卡 |
| `code/prepare_cst_level2_workpack.py` | 生成半球面 Level 2 多源多状态 CST 建模任务包、频点任务和单样本任务卡 |
| `requirements.txt` | Python 依赖清单 |
| `docs/reproduce_commands.md` | 复现实验和 CST 接入命令清单 |
| `docs/data_dictionary.md` | nearfield/farfield/labels/manifest/metrics 字段字典 |
| `docs/level1_cst_sprint_handoff.md` | Level 1 标准源三人分工、CST 导出和验收交接单 |

## 4. 分布式宽带传感布局设计

### 4.1 半球面布局

当前执行路线固定选择半球面 2π 测点布局。后续如需更贴近大型载体地面测试，可在本框架下扩展半柱面布局；但本轮 CST Level 1/Level 2 任务、manifest、任务包和审计脚本均以半球面测点表为准。

初始方案采用 13 m 半径上半球面布局：

- theta：5 deg 到 85 deg。
- phi：0 deg 到 360 deg。
- 空间点：9 x 18 = 162。
- 极化：theta/phi 双极化，或 CST 导出 Ex/Ey/Ez 后统一投影。
- 被测包络：12 m x 10 m x 8 m。

当前证据：

- `outputs/baseline/sensor_layout_hemisphere.png`
- `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`

### 4.2 CST 幅相导出兼容

实际 CST 导出可能给出幅值/相位而不是实部/虚部。为避免相干重建阶段丢失相位信息，当前新增 `code/normalize_cst_complex_columns.py`：

```text
nearfield e_mag/e_phase_deg -> e_real/e_imag
farfield e_theta_mag/e_theta_phase_deg -> e_theta_real/e_theta_imag
farfield e_phi_mag/e_phi_phase_deg -> e_phi_real/e_phi_imag
```

已完成幅相兼容性验证：从 CST 模板数据反造幅值/相位输入，再转回标准复数字段。转换后的数据通过 nearfield/farfield/pair 校验，并可直接接入 `code/run_cst_reconstruction.py`。当前转换链路验证指标：

- NMSE：约 `1.26e-6`
- 方向图相关系数：约 `0.999999`
- 主瓣误差：`0 deg`

说明：该结果只证明幅相兼容链路可用；正式场重建结论以 Level 1 required 当前重建结果和风险说明为准。

### 4.3 半柱面布局（后续扩展）

半柱面更贴近大型航空载体工程测试。后续将以机身 x 轴为柱轴，x 方向覆盖 [-7, 7] m，弧向覆盖 180 deg，每点双极化或三分量场。

## 5. 近远场关联建模与三维场域重建

### 5.1 等效源模型

对每个频点 f：

```text
E_meas(f) = G_nf(f) J(f) + n(f)
```

其中 E_meas 为测点复数场向量，G_nf 为由 Green 函数和探头极化响应构成的传播矩阵，J 为等效源系数。稳定反演采用：

```text
min_J ||G_nf J - E_meas||_2^2 + lambda ||J||_2^2
```

后续拓展组稀疏多频联合反演：

```text
min_{J(f)} sum_f ||G_f J(f) - E_f||_2^2
             + lambda_2 sum_f ||J(f)||_2^2
             + lambda_1 sum_g ||[J_g(f1), J_g(f2), ...]||_2
```

### 5.2 Level 1 required 标准源重建结果

当前 Level 1 required 严格审计范围为短偶极子和半波振子两个标准源，均已完成 nearfield/farfield 合并和批量重建：

| 样本 | 频点 | NMSE | 方向图相关系数 | 主瓣误差 | 输出目录 |
|---|---:|---:|---:|---:|---|
| L1_halfwave_dipole_z_1p2G | 1.20 GHz | `0.5955` | `0.3740` | `22.02 deg` | `outputs/cst_reconstruction/L1_halfwave_dipole_z_1p2G` |
| L1_short_dipole_z_1p2G | 1.20 GHz | `0.6087` | `0.3666` | `15.15 deg` | `outputs/cst_reconstruction/L1_short_dipole_z_1p2G` |

当前结论是：CST-Python 标准源闭环已经跑通，required-now 缺失文件为 0，批量重建 `2/2` 成功；但 solver-safe 导出与等效源重建之间的一致性指标仍不满足“高精度”口径，必须作为 G5 风险处理。正式报告采用保守表述：该阶段证明了数据接口、坐标/极化链路和批量重建流程可复现，同时暴露出近远场一致性、等效源基函数或正则化设置需要继续复核。

进一步复核发现，该 Level 1 solver-safe `nearfield.csv` 并非 CST 在 13 m 半球面物理探针处的 full-wave near-field monitor 直接导出，而是通过 CST `FarfieldPlot` 在 13 m 半球方向上取线性 E-field 后转换为 Ex/Ey/Ez。为避免把 farfield-derived 角域样本强行套入有限距离近场等效源模型，新增角域 Legendre/Fourier 正则化校准通道。该通道只用于验证当前 solver-safe 导出在角域/远场意义下是否自洽，不替代完整近场等效源反演。

角域校准结果如下：

| 样本 | 最优角域阶数 | NMSE | 方向图相关系数 | 主瓣误差 | 说明 |
|---|---|---:|---:|---:|---|
| L1_halfwave_dipole_z_1p2G | P7/M4, lambda=`1e-4` | `6.57e-5` | `0.99995` | `0.00 deg` | FarfieldPlot-derived 角域样本到 CST 远场网格 |
| L1_short_dipole_z_1p2G | P7/M6, lambda=`1e-4` | `8.41e-5` | `0.99988` | `0.00 deg` | FarfieldPlot-derived 角域样本到 CST 远场网格 |

因此，Level 1 风险从“CST 数据不可用或结果不可复现”收敛为“数据类型与物理反演模型边界需要写清”：角域校准证明 solver-safe FarfieldPlot-derived 数据本身与 CST 远场网格高度一致；原等效源近场反演指标偏弱，主要说明该模型不应直接作为 full-wave 近场 monitor 反演结论。

当前证据：

- `outputs/cst_level1_merge_report/level1_merge_summary.json`
- `outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv`
- `outputs/cst_reconstruction/L1_short_dipole_z_1p2G/cst_farfield_reconstruction_compare.png`
- `outputs/cst_reconstruction/L1_halfwave_dipole_z_1p2G/cst_farfield_reconstruction_compare.png`
- `outputs/cst_level1_angular_calibration/angular_calibration_summary.json`
- `outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png`

## 6. 测点数量优化方法

### 6.1 对照组设计

| 组别 | 测点比例 | 说明 |
|---|---:|---|
| Full | 100% | 全测点基准 |
| Random sparse | 75% / 50% / 25% | 随机稀疏对照 |
| Optimized sparse | 75% / 50% | 最远点/互相干性近似优化 |
| Future active sampling | 自适应 | 基于误差贡献或不确定度加密 |

### 6.2 当前测点压缩参考结果

早期接口验证参考场中，50% 优化测点使用 81 个空间点、162 个测量通道，重建 NMSE 约 `8.36e-4`，方向图相关系数约 `0.9986`。该结果用于说明测点压缩算法接口和评价方式，不直接作为 Level 1 required 的高精度证明。

当前证据：

- `outputs/baseline/reconstruction_metrics.csv`
- `outputs/baseline/sampling_tradeoff.png`

### 6.3 重建鲁棒性与正则化扫描

当前新增 `code/run_reconstruction_robustness.py`，在三源参考场上扫描：

- 噪声：20、25、30、35、40 dB SNR。
- 测点：100%、75%、50%、25% 优化测点，以及 50% 随机测点对照。
- 正则化：`1e-6`、`1e-5`、`1e-4`、`1e-3`、`1e-2`。
- 每组 4 次噪声 trial。

30 dB SNR 下当前最佳 lambda 结果：

| Case | 测点数 | 通道数 | 最佳 lambda | NMSE | 相关系数 | 主瓣误差 |
|---|---:|---:|---:|---:|---:|---:|
| full_100 | 162 | 324 | `1e-2` | `5.32e-4` | `0.99882` | `0.00 deg` |
| optimized_75 | 122 | 244 | `1e-3` | `1.13e-3` | `0.99834` | `0.00 deg` |
| optimized_50 | 81 | 162 | `1e-6` | `2.07e-3` | `0.99595` | `25.81 deg` |
| random_50 | 81 | 162 | `1e-3` | `3.71e-3` | `0.99461` | `12.73 deg` |
| optimized_25 | 40 | 80 | `1e-6` | `2.36e-1` | `0.57621` | `33.42 deg` |

结论：75% 测点是当前稳健压缩候选；50% 测点方向图相关性仍较高，但主瓣定位对噪声和正则化更敏感；25% 测点不应作为主路线，只能作为极限压缩对照。本节在最终报告中需与 Level 1 required 重建指标风险并列陈述，避免把参考场压缩效果外推为已关闭的高精度指标。

当前证据：

- `outputs/reconstruction_robustness/reconstruction_robustness_best.csv`
- `outputs/reconstruction_robustness/reconstruction_noise_robustness.png`
- `outputs/reconstruction_robustness/reconstruction_sensor_tradeoff_30dB.png`
- `outputs/reconstruction_robustness/reconstruction_lambda_scan_optimized50_30dB.png`

## 7. 空间-频谱-极化特征辨识

### 7.1 特征体系

| 特征类型 | 示例 | 作用 |
|---|---|---|
| 空间方向图 | 主瓣方向、副瓣数量、方向图熵、空间相关矩阵特征值 | 区分载体结构和安装位置 |
| 频谱特征 | 峰值频点、谱质心、带宽、频点间相关性 | 区分运行状态和设备组合 |
| 极化特征 | theta/phi 功率比、交叉极化比、极化随频率变化 | 增强稳定性 |
| 等效源特征 | 活跃源数量、源能量质心、源分布稀疏度 | 提供物理可解释指纹 |

### 7.2 接口验证基线

在正式 Level 2 数据进入前，项目先用轻量源模型完成识别接口验证：从近场表格读取 Ex/Ey/Ez，按 sample_id 和频点聚合，提取空间功率、相对相位、极化比和频谱斜率等特征，并训练 SVM/随机森林分类器。该基线用于证明代码接口、特征工程和评价指标链路可复现；本章正式结论以 7.3-7.6 的 Level 2 full48、删减、结构遮挡和复合扰动结果为准。

当前证据：

- `outputs/baseline/recognition_metrics.json`
- `outputs/baseline/recognition_confusion_matrix.png`

### 7.3 Level 2 full48 识别结果

当前 Level 2 数据链已完成 48/48 个 CST-derived element-library 样本合并，覆盖四类状态：

- 类别：`comm_pair`、`radar_top`、`mixed_avionics`、`multi_state_on`。
- 样本：48 个。
- 频点：0.90、1.05、1.20、1.35、1.50 GHz。
- 测点：13 m 半球面 162 点。
- nearfield：Ex/Ey/Ez 复数场，116640 行。
- farfield：Etheta/Ephi 复数场和 gain_db，164160 行。
- 特征维度：4965。
- 最优模型：SVM RBF。
- 测试集准确率：`1.000`。
- macro F1：`1.000`。

当前证据：

- `outputs/cst_level2_merge_report/level2_merge_summary.json`
- `outputs/cst_recognition_level2/cst_recognition_metrics.json`
- `outputs/cst_recognition_level2/cst_recognition_confusion_matrix.png`

说明：该准确率满足“空间频率特征辨识精度不低于 85%”的基础指标口径，但报告中必须明确其证据性质：当前 Level 2 是 CST-derived element-library superposition，用于验证多源多状态、频点和测点维度下的识别链路；复杂航空载体结构散射、遮挡和安装效应通过 7.5 的简化结构对照来给出边界约束，仪器增益误差与结构化缺测的复合扰动通过 7.6 的压力测试来给出缓解口径。

### 7.4 识别测点/频点删减验证

当前已加入 `code/run_cst_recognition_ablation.py`，用于回答两个问题：

1. 识别是否必须依赖全部 162 个测点。
2. 识别是否必须依赖全部 5 个频点。

在当前 Level 2 full48 数据上的删减结果如下：

| Case | 测点数 | 频点数 | 每样本双极化通道 | 特征数 | 准确率 | Macro F1 |
|---|---:|---:|---:|---:|---:|---:|
| full_5freq_100 | 162 | 5 | 1620 | 4965 | 1.000 | 1.000 |
| farthest_5freq_75 | 122 | 5 | 1220 | 3765 | 1.000 | 1.000 |
| farthest_5freq_50 | 81 | 5 | 810 | 2535 | 1.000 | 1.000 |
| farthest_5freq_25 | 40 | 5 | 400 | 1305 | 1.000 | 1.000 |
| full_3freq_100 | 162 | 3 | 972 | 2979 | 1.000 | 1.000 |
| full_1freq_100 | 162 | 1 | 324 | 992 | 1.000 | 1.000 |
| farthest_3freq_50 | 81 | 3 | 486 | 1521 | 1.000 | 1.000 |
| farthest_1freq_50 | 81 | 1 | 162 | 506 | 1.000 | 1.000 |

当前证据：

- `outputs/cst_recognition_level2_ablation/recognition_ablation_metrics.csv`
- `outputs/cst_recognition_level2_ablation/recognition_ablation_accuracy.png`
- `outputs/cst_recognition_level2_ablation/recognition_ablation_summary.json`

说明：删减结果显示在当前 CST-derived Level 2 数据上，测点和频点压缩后分类仍保持 1.000；但该结果不应外推为复杂载体 full-wave 结构对照结论，正式答辩中需将其定位为空-频-极化识别链路和压缩测量可行性证据。

### 7.5 Level 2 简化结构遮挡对照

为约束 element-library superposition 与复杂载体安装效应之间的偏差，本轮新增 `code/run_cst_structure_comparison.py`。该脚本没有声称完成 full-wave CST airframe 求解，而是在当前 Level 2 CST-derived nearfield/farfield 上施加透明、可复现的机身/机翼/尾翼遮挡迁移函数，再重新统计方向图变化和跨域识别准确率。

当前结构对照结果如下：

| 指标 | 数值 | 说明 |
|---|---:|---|
| 样本数 | 48 | 覆盖 Level 2 full48 全部 sample_id |
| 样本-频点数 | 240 | 48 个样本 x 5 个频点 |
| 平均遮挡 | `3.06 dB` | simplified airframe transfer 引入的平均方向图衰减 |
| P95 遮挡 | `6.63 dB` | 代表较强安装/遮挡方向的偏差 |
| 最大遮挡 | `13.33 dB` | 最强局部遮挡方向 |
| 平均方向图相关系数 | `0.730` | 说明结构遮挡会显著改变方向图形态 |
| cross-domain accuracy | `1.000` | 在无结构数据训练、简化结构数据测试下的最佳识别准确率 |

当前证据：

- `outputs/cst_structure_comparison/structure_comparison_summary.json`
- `outputs/cst_structure_comparison/structure_comparison_metrics.csv`
- `outputs/cst_structure_comparison/structure_effect_by_class.csv`
- `outputs/cst_structure_comparison/structure_recognition_metrics.json`
- `outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png`

结论：简化载体遮挡会带来可观方向图变化，因此报告和答辩中不能把 element-library full48 直接表述为复杂航空载体 full-wave 结构散射结论；但当前空-频-极化特征在该简化安装效应下仍保持跨域识别稳定，说明特征体系具有一定结构扰动鲁棒性。后续若时间允许，可进一步在 CST 中建立 full-wave airframe 模型验证散射、多径和安装点耦合效应。

### 7.6 Level 2 复合仪器误差与结构缺测压力测试

为避免把 clean full48 和单一结构遮挡结果过度外推，本轮新增 `code/run_cst_recognition_compound_stress.py`，在 Level 2 full48 特征上叠加更接近工程测量风险的复合扰动：传感器增益偏置、频点相关增益误差、结构化测点缺失、通道 dropout 以及组合压力情形。该测试重点不是追求更高数值，而是识别哪类预处理策略会在强扰动下失效，并给出报告中可落地的缓解策略。

当前策略对照结果如下：

| Strategy | Mean accuracy | Min accuracy | Passes 0.85 |
|---|---:|---:|---|
| `zero_fill` | `0.939` | `0.733` | false |
| `mask_features` | `0.940` | `0.733` | false |
| `freq_sensor_median_impute` | `0.993` | `0.867` | true |
| `freq_sensor_median_impute_mask` | `0.990` | `0.867` | true |

最差失败行出现在 `full_grid_162 / zero_fill / sensor_gain3db_sensor_node_dropout25pct`，accuracy=`0.733`。这说明在传感器增益误差和结构化缺测同时存在时，直接补零或仅加 mask 特征不足以保证 85% 指标；按频点和传感器维度做中位数插补后，当前压力测试中的最小 accuracy 提升到 `0.867`，平均 accuracy 相对 zero-fill 提升约 `0.054`。

当前证据：

- `data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_summary.json`
- `data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_by_strategy.csv`
- `data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_metrics.csv`

结论：Level 2 识别能力可以作为 85% 指标的核心支撑，但最终材料应写成“clean full48 达标、简化结构遮挡跨域稳定、复合扰动下需采用 frequency/sensor median imputation 缓解”的口径。该结论仍属于 CST-derived 数据与可复现扰动模型上的算法证据，不能替代真实仪器标定误差和 full-wave airframe 求解。

## 8. CST 仿真测试设计

### 8.1 Level 1 标准源

对象：

- 短偶极子。
- 半波振子。

目的：

- 校验坐标、相位、极化、远场角度和 Python 重建。

通过标准：

- 相关系数 >= 0.95。
- 主瓣误差 <= 5 deg。
- NMSE <= `1e-2`。

当前已生成 Level 1 CST 执行清单：

- 输出目录：`outputs/cst_level1_plan`
- 计划案例：6 个。
- 必做案例：`L1_short_dipole_z_1p2G`、`L1_halfwave_dipole_z_1p2G`。
- 建议对照：`L1_short_dipole_x_1p2G`、`L1_short_dipole_y_1p2G`。
- 源参数：`outputs/cst_level1_plan/level1_source_manifest.csv`
- 验证门槛：`outputs/cst_level1_plan/level1_validation_targets.csv`

同时已加入 Level 1 批量导出审计：

- 脚本：`code/merge_cst_level1_exports.py`
- 当前合并报告：`outputs/cst_level1_merge_report`
- 当前状态：required 严格范围已完成，必做 2 个案例均完整；建议/可选对照未作为本轮最终门槛。
- 必做验收命令：`python code\merge_cst_level1_exports.py --strict`
- 全量验收命令：`python code\merge_cst_level1_exports.py --strict-all`
- 批量重建命令：`python code\run_cst_level1_batch_reconstruction.py`
- CST 建模任务包：`outputs/cst_level1_workpack`

Level 1 required 当前验收结果：

- `required_complete=true`
- `required_complete_cases=2/2`
- `completed_runs=2/2`
- `failed_runs=0`
- 角域校准：2/2 案例完成，最大 NMSE `8.41e-5`，最小相关系数 `0.99988`，最大主瓣误差 `0.00 deg`。
- 当前主要风险：等效源近场反演指标偏弱，但已定位为 FarfieldPlot-derived 角域样本与 full-wave 近场反演模型不匹配；最终报告需明确该边界，后续如需完整近场反演需补 near-field monitor 或匹配传播模型。

早期接口验证资料保留在代码和数据附录中，仅用于说明批处理链路的可复现性；本章正式证据以 Level 1 required 当前合并与重建结果为准。

### 8.2 Level 2 多源多状态

对象：

- 两到四个辐射源。
- 三到五个频点。
- 通信源/雷达源/导航源/多源同时工作。

输出：

- 多状态 nearfield/farfield 数据集。
- 识别标签与混淆矩阵。

当前已生成 Level 2 CST 执行清单：

- 输出目录：`outputs/cst_level2_plan`
- 计划样本：48 个 sample_id。
- 样本-频点任务：240 行。
- 源配置：120 行。
- 标签文件：`outputs/cst_level2_plan/level2_labels.csv`
- 技术规程：`docs/phase_03_cst_level2_multisource_recognition_protocol.md`

同时已加入批量导出合并与缺漏检查：

- 脚本：`code/merge_cst_level2_exports.py`
- 半球面建模任务包：`outputs/cst_level2_workpack`
- 当前合并报告：`outputs/cst_level2_merge_report`
- 当前状态：48/48 个样本完整，240 个 sample-frequency nearfield/farfield 任务均完整。
- 验收命令：`python code\merge_cst_level2_exports.py --strict`

Level 2 当前验收结果：

- `complete_samples=48/48`
- nearfield 合并行数：116640
- farfield 合并行数：164160
- 识别输出：`outputs/cst_recognition_level2`
- 最优模型：SVM RBF
- best accuracy：`1.000`

说明：Level 2 当前证据是 CST-derived element-library superposition，适合支撑多源多状态识别链路和空-频-极化特征有效性；简化结构遮挡对照已在 `outputs/cst_structure_comparison` 中给出，复合仪器误差/结构缺测压力测试已在 `data/recognition_stress_tests/level2_compound_stress` 中给出，full-wave airframe 结构散射和真实仪器标定仍作为后续增强项。

### 8.3 Level 3 简化航空载体

对象：

- 12 m 机身。
- 10 m 机翼。
- 垂尾/平尾。
- 顶部、腹部、翼尖、侧向安装位置。

输出：

- 简化安装效应方向图对照：`outputs/cst_structure_comparison/plots/*_structure_compare.png`。
- 遮挡导致的空间指纹变化统计：平均遮挡 `3.06 dB`、P95 遮挡 `6.63 dB`、最大遮挡 `13.33 dB`。
- 跨域识别验证：无结构数据训练、简化结构数据测试，best model 为 SVM RBF，accuracy=`1.000`。

边界：当前 Level 3 是 simplified aircraft occlusion transfer，不是 full-wave CST airframe scattering。它的作用是把结构遮挡影响量化为 G5 成稿边界和鲁棒性证据；若后续继续提高说服力，应在 CST 中补充全波机体模型、材料/边界条件和安装点耦合求解。

## 9. 误差、鲁棒性与工程可行性分析

已完成鲁棒性参考扫描：

- 重建噪声鲁棒性：20/25/30/35/40 dB SNR。
- 测点删减：100%/75%/50%/25% 优化测点与 50% 随机测点。
- 正则化参数：`1e-6` 到 `1e-2`。
- 识别复合扰动压力测试：传感器增益误差、频点相关误差、结构化缺测和 dropout 组合。

G5 阶段仍需说明或补强的工程扰动项：

1. 噪声鲁棒性：20/30/40 dB SNR。
2. 测点缺失：随机缺测、局部遮挡缺测。
3. 频点扰动：中心频率偏移。
4. 姿态扰动：俯仰、滚转、偏航小角度变化。
5. 复合仪器误差：原始 zero-fill/mask 在强扰动下会低于 0.85，当前需采用 frequency/sensor median imputation 作为工程缓解策略。
6. 正则化参数扫描：lambda 与 NMSE/相关系数关系。

## 10. 创新点

1. 面向 2π 受限空域的等效源重构框架：兼容半球面、半柱面和后续不规则测量面。
2. 测点数量-重建精度联合优化：用全测点、随机稀疏和优化稀疏对照支撑客观评分。
3. 空-频-极化-等效源联合辐射指纹：从场域重建结果中提取物理可解释特征。
4. CST-Python 可复现闭环：CST 生成可信电磁数据，Python 完成自研重建和识别，避免只展示仿真软件截图。

## 11. 当前交付物状态

| 交付物 | 当前状态 | 文件 |
|---|---|---|
| 文献筛查 | 初版完成 | `docs/literature_screening_and_strategy.md`、`docs/literature_matrix.md` |
| 文献到算法迁移证据链 | 已生成 | `docs/literature_to_algorithm_traceability.md` |
| 技术路线 | 初版完成 | `docs/phase_01_cst_technical_route_and_division.md` |
| CST 标准源规程 | 初版完成 | `docs/cst_level1_standard_source_protocol.md` |
| CST Level 1 执行清单 | 已生成 | `outputs/cst_level1_plan` |
| CST Level 1 合并/缺漏报告 | required 严格范围已完成，2/2 必做案例完整 | `outputs/cst_level1_merge_report` |
| CST Level 1 批量重建入口 | 已完成 required 2/2 批量重建，但指标存在风险 | `outputs/cst_level1_reconstruction_batch` |
| CST Level 1 冲刺交接单 | 已生成 | `docs/level1_cst_sprint_handoff.md` |
| CST Level 1 建模任务包 | 已生成，半球面路线 | `outputs/cst_level1_workpack` |
| CST 宏模板与 pilot 队列 | 已生成，服务仿真执行 | `outputs/cst_macro_templates` |
| CST 数据接入计划 | 初版完成 | `docs/phase_02_cst_data_integration_plan.md` |
| CST Level 2 多源识别规程 | 初版完成 | `docs/phase_03_cst_level2_multisource_recognition_protocol.md` |
| CST Level 2 执行清单 | 已生成 | `outputs/cst_level2_plan` |
| CST Level 2 建模任务包 | 已生成，半球面路线 | `outputs/cst_level2_workpack` |
| CST Level 2 合并/缺漏报告 | full48 样本已完成，48/48 样本完整 | `outputs/cst_level2_merge_report` |
| CST Level 2 识别结果 | 已完成，SVM RBF accuracy=1.000 | `outputs/cst_recognition_level2` |
| CST Level 2 识别删减验证 | 已完成，当前 Level 2 full48 数据上各删减组 accuracy=1.000 | `outputs/cst_recognition_level2_ablation` |
| CST Level 2 简化结构遮挡对照 | 已完成，mean shadow=3.06 dB，cross-domain accuracy=1.000 | `outputs/cst_structure_comparison` |
| CST Level 2 复合干扰压力测试 | 已完成，zero-fill/mask 最差 accuracy=0.733，frequency/sensor median imputation 最小 accuracy=0.867 | `data/recognition_stress_tests/level2_compound_stress` |
| 重建鲁棒性扫描 | 已跑通，待 CST 复核 | `outputs/reconstruction_robustness` |
| 评分项证据板 | 已跑通，保守标注缺口 | `outputs/scorecard` |
| 最终提交材料计划 | 初版完成 | `docs/final_submission_package_plan.md` |
| 最终提交包索引 | 已跑通，等待成稿材料 | `outputs/submission_index` |
| 代码包依赖清单 | 初版完成 | `requirements.txt` |
| 复现命令清单 | 初版完成，待最终路径复核 | `docs/reproduce_commands.md` |
| 数据字典 | 初版完成，待最终字段复核 | `docs/data_dictionary.md` |
| CST 幅相转换验证 | 已跑通 | 代码与附录数据包 |
| CST 标准源结果 | required 链路已补齐，但重建精度风险未关闭 | `outputs/cst_reconstruction/L1_*` |
| 多源识别结果 | Level 2 full48 已补齐；简化结构遮挡和复合干扰压力测试已补充，zero-fill 失败边界与插补缓解需作为边界说明 | `outputs/cst_recognition_level2`、`outputs/cst_structure_comparison`、`data/recognition_stress_tests/level2_compound_stress` |
| PPT/视频 | 已导出过，需复核 | 按最新复合扰动边界口径复核/必要时重导出正式 PPTX/MP4 |

### 11.1 评分项证据板

当前新增 `code/build_scorecard.py`，从现有文档、代码输出和指标文件自动生成评分项证据板：

- 输出目录：`outputs/scorecard`
- 面向汇报的 Markdown：`outputs/scorecard/scorecard.md`
- 结构化评分项表：`outputs/scorecard/score_items.csv`
- 关键指标 JSON：`outputs/scorecard/scorecard_metrics.json`

当前 scorecard 的保守判断：

| 评分项 | 分值 | 当前状态 |
|---|---:|---|
| 国内外发展调研分析 | 10 | Draft evidence |
| 研究思路合理性 | 10 | CST evidence ready; write-up pending |
| 技术路线可行性 | 10 | CST evidence ready; model risk bounded |
| 测试方案完整性 | 10 | CST evidence ready; screenshots pending |
| 2π 传感布局与 12m x 10m x 8m 包络 | 10 | Ready |
| 三维场重建高精度与少测点 | 30 | CST angular calibration ready; near-field model risk |
| 空间-频谱特征辨识准确率 >= 85% | 20 | Ready with compound-stress mitigation caveat |

该表用于区分早期接口证据和当前 G5 成稿证据。当前 CST 证据已从“缺文件”转为“G5 成稿风险”：Level 1 需写清 FarfieldPlot-derived 角域校准与 full-wave 近场等效源模型边界，Level 2 识别需要说明 element-library/简化结构遮挡/full-wave airframe 边界，同时写清复合仪器误差和结构缺测下 zero-fill/mask 会失败、frequency/sensor median imputation 是当前缓解策略；既有正式 PDF/DOCX/PPTX/MP4 需按该口径复核或重导出。

### 11.2 最终提交包索引

当前新增 `docs/final_submission_package_plan.md` 和 `code/build_submission_index.py`，用于约束最终提交包结构：

- 报告：`01_report/solution_report.pdf/docx`
- PPT：`02_presentation/defense_slides.pptx/pdf`
- 视频：`03_video/演示视频 MP4`
- 代码：`04_code/src` 和复现说明
- CST：`05_cst/level1_standard_sources`、`05_cst/level2_multisource`
- 数据：`06_data/cst_exports` 和指标输出
- 附录：文献矩阵、scorecard、数据字典

当前自动索引输出：

- `outputs/submission_index/submission_package_index.md`
- `outputs/submission_index/submission_checklist.csv`
- `outputs/submission_index/submission_index_summary.json`

当前状态：submission 草稿包可由 `code/build_submission_draft.py` 重新生成，submission index 可由 `code/build_submission_index.py` 刷新；正式打包前的主要缺口已收敛为按最新 G5 风险说明复核报告、PPT、视频和最终归档。

### 11.3 复现与数据交接材料

当前新增三份代码包辅助材料：

- `requirements.txt`：列出 numpy、pandas、matplotlib、scikit-learn、openpyxl 等运行依赖。
- `docs/reproduce_commands.md`：按 baseline、CST Level 1、鲁棒性、识别、Level 2 合并和最终检查整理命令。
- `docs/data_dictionary.md`：定义 nearfield、farfield、labels、Level 2 manifest 和指标表字段。

正式打包前，需要用最终 CST 文件路径复核 `docs/reproduce_commands.md`，并确认导出字段仍满足 `docs/data_dictionary.md`。

## 12. 下一步

1. 将 Level 1 角域校准结果和近场等效源模型边界写入正式报告/PPT；若后续追求 full-wave 近场反演，再补 near-field monitor 或匹配传播模型。
2. 将 Level 2 full48 识别结果、删减验证、简化结构遮挡对照和复合干扰压力测试写入正式报告/PPT，并写清 CST-derived element-library + simplified occlusion/perturbation transfer 的适用边界。
3. 将本报告中的 Level 1/Level 2/结构对照/复合扰动当前证据统一到摘要、评分项映射、结果章节和风险章节。
4. 根据 `docs/final_submission_package_plan.md` 与 `outputs/presentation_package` 复核正式 PPTX 和视频脚本，必要时按最新口径重导出。
5. 复核正式报告 PDF/DOCX、答辩 PPTX 和演示视频 MP4 是否已同步复合扰动边界。
6. 重跑 `code/build_scorecard.py`、`code/build_problem_requirements_matrix.py`、`code/build_submission_index.py`、`code/build_completion_audit.py`、`code/build_master_dashboard.py` 和 `code/build_submission_draft.py`。
7. 运行 `code/build_progress_report.py --note "G5 最终文件和风险说明已收口"`，确认 `completion_proven=true` 后再进入最终提交。
