# CS-202614 文献筛查与可迁移技术策略

版本：v0.1  
用途：作为方案报告“国内外发展调研分析”“研究思路与技术路线”“测试系统/重建算法设计”的前置依据。

## 1. 赛题牵引下的文献筛查框架

本赛题不是单纯做一个远场方向图或一个机器学习分类器，而是要求形成“2π 空域测量布局 - 近远场关联建模 - 三维场域重建 - 少测点优化 - 空间频谱特征辨识”的完整链条。因此文献筛查按以下标准取舍。

### 1.1 优先纳入

1. IEEE/权威标准：天线测量、近场测量、测量不确定度、探头校准、近远场变换。
2. IEEE Transactions / IEEE Journal / 权威期刊：近场到远场变换、等效源/源重构、压缩感知测量、辐射指纹识别。
3. 有实验或仿真验证：不仅有概念公式，还给出测量几何、误差指标、噪声/截断/缺测鲁棒性。
4. 能迁移到赛题约束：支持半球面/半柱面 2π 覆盖、大尺寸载体、宽频段、多极化、少测点。

### 1.2 暂不作为主线

1. 只做单角度远场测试的方案：无法满足 2π 空域和三维场域重建。
2. 只调用 CST/FEKO 自带 Far-field 的方案：可作为真值或对照，但不能体现自研重建算法。
3. 纯黑箱深度学习重建：除非先有物理模型基线，否则难以解释精度、测点数量和泛化边界。
4. PCB/芯片 EMI 近场扫描文献：其中等效偶极子和源定位思想可迁移，但尺度、频段、测量面与航空载体不同，不能原样套用。

## 2. 已筛选核心文献与可迁移点

| 方向 | 文献/标准 | 权威性 | 关键内容 | 对本赛题的迁移价值 |
|---|---|---:|---|---|
| 测量规范 | IEEE 149-2021, IEEE Recommended Practice for Antenna Measurements, IEEE SA | 标准 | 覆盖天线收发特性、方向图测试、测试场设计、仪器与场地评估 | 报告中作为测试系统规范依据，定义方向图、极化、场地和仪器链路 |
| 近场测量规范 | IEEE 1720-2012, IEEE Recommended Practice for Near-Field Antenna Measurements, IEEE SA | 标准 | 推荐平面、柱面、球面三类近场测量几何，包含探头校准、数据格式、NF-FF 变换等 | 支撑半柱面/半球面布局的标准合理性，报告中说明探头校准和数据交付格式 |
| 近场测量综述 | Yaghjian, “An overview of near-field antenna measurements,” IEEE TAP, 1986 | 经典综述 | 从任意曲面理想探头到平面/柱面/球面扫描，讨论探头修正、采样定理、误差来源 | 作为理论背景，说明为什么需要近场测量再变换到远场 |
| 任意曲面 NF-FF | Rodríguez Varela et al., “Near-field to far-field transformation on arbitrary surfaces via multi-level spherical wave expansion,” IEEE TAP, 2020 | IEEE TAP | 任意测量曲面的近远场变换，多球面波展开，多模探头修正，层次化子域降低复杂度 | 赛题中半柱面/半球面和可能的不规则布设可借鉴；后续可作为高级路线 |
| 等效源重构条件 | Kornprobst et al., “Accuracy and Conditioning of Surface-Source Based Near-Field to Far-Field Transformations,” IEEE TAP, 2021 | IEEE TAP | 比较多种逆表面源表述的精度和条件数；球形 Huygens 面条件最好，贴近 AUT 的凸包表面精度更高 | 给出本方案选择“紧包络 Huygens/等效源面 + 正则化”的依据 |
| 安装平台等效表示 | Malmström et al., “On the Accuracy of Equivalent Antenna Representations,” IEEE TAP, 2018 | IEEE TAP | 比较近场源和远场源在简化平台安装条件下的误差，强调等效表示配置会显著影响精度 | 对航空载体安装效应非常相关：先用等效源降低天线细节，再做平台级辐射推算 |
| 受限域压缩感知 | Valdez, Yuffa, Wakin, “Restricted Domain Compressive Sensing for Antenna Metrology,” IEEE TSP, 2022 | IEEE TSP/NIST | 在球面近场到远场问题中，对受限测量域建立压缩感知保证；在减少测量点时保持重建质量 | 直接对应赛题“2π 受限空域 + 少测点高精度重建” |
| 多频压缩测量 | Valdez, Folz, Wakin, Gordon, “Multi-frequency Antenna Metrology with Sparse Measurements,” IEEE JSTSP, 2024 | IEEE JSTSP/NIST | 将球面近场压缩测量扩展到多频/宽带场景，比较稀疏和低秩模型，并显示多频模型可进一步减少测量 | 直接支撑本方案 Level 2 的 5 频点联合建模、组稀疏/低秩空频特征和少测点策略 |
| 球面测点优化 | Bangun & Culotta-Lopez, “Optimizing Sensing Matrices for Spherical Near-Field Antenna Measurements,” IEEE TAP, 2023 | IEEE TAP | 通过降低感知矩阵互相干性优化球面近场采样点，少于经典采样数也能重建球面模式系数和远场 | 可迁移为“互相干性最小化/信息增益最大化”的测点优化策略 |
| 无相位测量拓展 | Fuchs et al., “Phaseless Near Field Antenna Measurements from Two Surface Scans,” IEEE TAP, 2020 | IEEE TAP | 用双面无相位近场扫描和源重构求等效电流，再推远场，验证噪声、采样步长鲁棒性 | 若比赛或实验条件只能测幅度，可作为备用方案；主线仍建议测幅相 |
| EMI 源重构 | Regué et al., “A genetic algorithm based method for source identification and far-field radiated emissions prediction from near-field measurements,” IEEE TEMC, 2001 | IEEE TEMC | 用等效偶极子替代实际辐射源，通过近场数据识别源位置并预测远场 | 可迁移到“机载多设备辐射源等效偶极子/稀疏源定位” |
| EMI 远场预测 | Gao et al., “Far-field prediction using only magnetic near-field scanning for EMI test,” IEEE TEMC, 2014 | IEEE TEMC | 利用磁近场扫描和等效定理预测 EMI 远场 | 支持“近场测量可推远场”的工程可信度；但航空载体需扩展到多极化/大尺寸 |
| RF 指纹综述 | Soltanieh et al., “A review of radio frequency fingerprinting techniques,” IEEE JRFID, 2020 | IEEE 综述 | 综述瞬态、稳态、调制段等 RF 指纹特征、分类算法与方法谱系 | 为“空间-频谱辐射指纹”命名和特征设计提供依据 |
| 雷达发射机机理特征 | Liu et al., “Feature Analysis and Extraction for Specific Emitter Identification Based on the Signal Generation Mechanisms of Radar Transmitters,” Sensors, 2022 | 机理型论文 | 从频率稳定度、RF 放大链非线性、脉冲前沿包络提取特征；多特征随机森林在模拟实验中显著优于单特征 | 提示识别模块不应只用一个方向图指标，应做多特征融合 |
| 变工作参数识别 | Man et al., “A Specific Emitter Identification Algorithm under Zero Sample Condition Based on Metric Learning,” Remote Sensing, 2021 | 应用期刊 | 用度量学习解决工作参数变化、零样本条件下的 SEI 泛化 | 可迁移到“同一载体不同运行状态”的度量学习或原型网络加分路线 |

## 3. 文献归纳：本赛题可用的方法谱系

### 3.1 测量布局

权威标准将近场测量主几何分为平面、柱面、球面。本赛题要求传感器布局覆盖 2π 空间立体角的半柱面或半球面，并容纳不小于 12 m x 10 m x 8 m 的被测对象。因此布局应从一开始就参数化，而不是只画概念图。

建议主布局：

1. 半柱面布局：更贴近大尺寸航空载体工程测试，轴向沿机身方向，圆弧覆盖上半空间或侧向半空间。
2. 半球面布局：更便于证明 2π 立体角覆盖，也便于球面波/压缩感知文献迁移。
3. 多极化采样：每个位置至少两正交极化，最好保留 Ex/Ey/Ez 或等效探头响应，避免识别阶段丢失极化特征。

### 3.2 三维场域重建

文献主线可分为三类：

1. 经典 NF-FF 变换：基于平面/柱面/球面波展开，理论成熟，但对标准扫描几何和采样完整性要求较强。
2. 等效源/源重构：基于 Huygens 等效原理，把被测载体包围在等效电/磁流或等效偶极子面内，由近场反演等效源，再计算远场。优点是适合复杂结构、不规则测量面和诊断解释。
3. 压缩感知/稀疏重建：把辐射场投影到稀疏基或等效源稀疏表示上，通过优化测点和正则化减少采样点。

本赛题最适合的主线是“等效源重构 + 压缩感知测点优化”。原因是它同时回应两个客观评分核心：重建精度和测点数量。

## 4. 面向本赛题的创新策略

提出方案名称：

**物理约束的空-频-极化联合等效源重构与受限域压缩测量方法**

核心思想：

1. 用半球面/半柱面多极化传感阵列获取 2π 空域近场幅相数据。
2. 在载体外包络附近建立 Huygens 等效源面或等效偶极子网格，把复杂机载多源辐射压缩为可反演的等效源系数。
3. 采用 Tikhonov/SVD 作为稳定基线，再引入 L1/组稀疏正则化，使多频点共享稀疏源位置，实现少测点重建。
4. 用受限域压缩感知思想优化测点：初始采用均匀/低差异序列覆盖 2π，再按互相干性、信息增益或重建误差贡献删减测点。
5. 将重建得到的远场方向图、等效源系数、频谱峰值、极化比和空间相关矩阵组成“空-频-极化辐射指纹”，用于载体/运行状态识别。

## 5. 技术细节建议

### 5.1 数学模型

对每个频点 f，近场测量可写为：

```text
E_meas(f) = G_nf(f) J(f) + n(f)
```

其中：

- E_meas(f)：所有测点、极化、场分量拼接后的复数测量向量。
- G_nf(f)：由 Green 函数、测点坐标、等效源坐标、探头极化响应构成的传播矩阵。
- J(f)：待反演的等效源系数，可表示为等效电流/磁流或等效偶极子矩。
- n(f)：噪声、校准误差、截断误差和环境反射残差。

稳定重建基线：

```text
min_J || W (G_nf J - E_meas) ||_2^2 + lambda_2 || L J ||_2^2
```

少测点/多频联合增强：

```text
min_{J(f)} sum_f || W_f (G_f J(f) - E_f) ||_2^2
             + lambda_2 sum_f || L J(f) ||_2^2
             + lambda_1 sum_g || [J_g(f1), J_g(f2), ...] ||_2
```

这里的组稀疏项表达“同一物理辐射源在多个频点上位置相对稳定”，适合机载多设备辐射建模。

远场外推：

```text
E_far(theta, phi, f) = G_ff(theta, phi, f) J(f)
```

### 5.2 测点优化

测点优化不建议只做随机删点。建议至少设置四组对照：

| 组别 | 测点比例 | 作用 |
|---|---:|---|
| Full | 100% | 全测点基准 |
| Uniform sparse | 75% / 50% / 25% | 规则稀疏采样 |
| Random sparse | 75% / 50% / 25% | 随机抽样对照 |
| Optimized sparse | 自适应 | 基于互相干性/信息增益/误差贡献的优化测点 |

推荐指标：

- NMSE：归一化均方误差。
- Corr：方向图相关系数。
- Main-lobe error：主瓣方向误差。
- Peak error：峰值误差。
- Point-efficiency score：在相同精度阈值下所需测点数。

### 5.3 特征辨识

识别模块不要只把“某频点方向图图片”丢给 CNN。建议先做可解释特征基线，再做深度学习加分。

基础特征：

1. 空间方向图特征：主瓣方向、副瓣数量、半功率波束宽度、方向图熵、空间相关矩阵特征值。
2. 频谱特征：峰值频点、带宽、谱质心、谱峰数量、频点间相关性。
3. 极化特征：H/V 或 theta/phi 极化功率比、交叉极化比、极化随频率变化趋势。
4. 等效源特征：等效源能量分布、活跃源数量、源位置质心、源系数随频率变化。

分类模型：

1. 基线：SVM、Random Forest、XGBoost。
2. 增强：1D/2D CNN 输入空频图，或 Autoencoder 提取低维辐射指纹。
3. 变状态泛化：Metric Learning / Prototypical Network，将“同载体不同运行参数”拉近，将“不同载体”拉远。

目标：先用可控仿真数据稳定达到 85% 以上，再扩大到多源、多频、多姿态和噪声扰动。

## 6. 推荐技术路线

### 阶段一：文献与指标闭环

输出：

- 文献矩阵。
- 评分项到技术证据映射表。
- 测量布局、重建、识别三个模块的指标定义。

### 阶段二：标准源验证

对象：

- 短偶极子、半波振子、小环天线或等效偶极子阵列。

目标：

- 跑通 E_meas -> J -> E_far。
- 与解析方向图或 CST/FEKO 远场真值对比。

### 阶段三：复杂载体迁移

对象：

- 多源、多频、多极化组合。
- 简化航空载体：金属圆柱机身、平板机翼、典型天线安装位置。

目标：

- 验证遮挡、散射、安装位置对空间辐射指纹的影响。
- 建立不同载体/状态标签。

### 阶段四：少测点优化

目标：

- 给出“测点数量 - 重建精度”曲线。
- 证明优化测点优于随机删点或简单规则删点。

### 阶段五：空频指纹识别

目标：

- 基线模型准确率 >= 85%。
- 输出混淆矩阵、F1、特征重要性。
- 给出“为什么这些特征具有唯一性和稳定性”的解释。

## 7. 报告章节建议

1. 赛题理解与评分指标分解。
2. 国内外发展调研。
   - 近场测量与标准。
   - 近远场变换与等效源重构。
   - 压缩感知与测点优化。
   - RF/雷达辐射指纹识别。
3. 总体技术路线。
4. 分布式宽带传感布局设计。
5. 近远场关联建模与三维场域重建算法。
6. 测点数量优化方法。
7. 空间-频谱-极化特征辨识方法。
8. 典型仿真测试结果。
9. 误差、鲁棒性与工程可行性分析。
10. 创新点与后续应用价值。

## 8. 下一步工作清单

1. 完成文献矩阵扩展到 20 篇左右，标注“必引/可引/背景”。
2. 基于上述数学模型补齐可运行 baseline：传感布局、等效源反演、远场重建、测点压缩、识别。
3. 生成第一批图表：2π 测点布局图、重建方向图对比、测点压缩曲线、识别混淆矩阵。
4. 将图表嵌入报告章节草稿，形成“文献依据 - 方法设计 - 实验验证”的闭环。

## 9. 主要来源链接

- IEEE 149-2021: https://standards.ieee.org/ieee/149/6667/
- IEEE 1720-2012: https://standards.ieee.org/ieee/1720/4190/
- Yaghjian 1986: https://zenodo.org/records/1232233
- Rodríguez Varela et al. 2020: https://oa.upm.es/68614/
- Kornprobst et al. 2021: https://arxiv.org/abs/2004.08918
- Malmström et al. 2018: https://arxiv.org/abs/1701.03275
- Valdez et al. 2022: https://www.nist.gov/publications/restricted-domain-compressive-sensing-antenna-metrology
- Valdez et al. 2024: https://www.nist.gov/publications/multi-frequency-antenna-metrology-sparse-measurements
- Bangun & Culotta-Lopez 2023: https://arxiv.org/abs/2206.02181
- Fuchs et al. 2020: https://orbit.dtu.dk/en/publications/phaseless-near-field-antenna-measurements-from-two-surface-scans-
- Regué et al. 2001: https://merit.url.edu/en/publications/a-genetic-algorithm-based-method-for-source-identification-and-fa
- Gao et al. 2014: https://mst.elsevierpure.com/en/publications/far-field-prediction-using-only-magnetic-near-field-scanning-for-
- Soltanieh et al. 2020: https://research.monash.edu/en/publications/a-review-of-radio-frequency-fingerprinting-techniques/
- Liu et al. 2022: https://pmc.ncbi.nlm.nih.gov/articles/PMC9003364/
- Man et al. 2021: https://www.mdpi.com/2072-4292/13/23/4919
