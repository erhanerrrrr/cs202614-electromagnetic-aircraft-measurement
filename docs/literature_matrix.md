# CS-202614 权威文献矩阵

版本：v0.1  
用途：支撑方案报告“国内外发展调研分析”章节，并为技术路线、创新点和实验设计提供可追溯依据。

## 1. 文献分级规则

| 等级 | 含义 | 在报告中的用法 |
|---|---|---|
| A | 必引核心依据 | 用于说明赛题方案主线为何合理，直接支撑测量、重建、少测点、识别核心方法 |
| B | 重要支撑依据 | 用于扩展方法比较、备选方案、误差/鲁棒性讨论 |
| C | 背景或加分依据 | 用于说明发展趋势、深度学习拓展、后续优化方向 |

## 2. 矩阵总览

| 编号 | 方向 | 文献/标准 | 类型 | 等级 | 核心结论/方法 | 可迁移到本赛题的策略 | 对应评分项 | 来源 |
|---|---|---|---|---|---|---|---|---|
| L01 | 测量规范 | IEEE 149-2021, IEEE Recommended Practice for Antenna Measurements | IEEE 标准 | A | 给出天线方向图、测试场、仪器链路、场地评估等推荐实践 | 作为测试系统规范依据，报告中定义方向图、极化、测试链路、场地要求 | 测试方案完整性、传感布局覆盖 | https://standards.ieee.org/ieee/149/6667/ |
| L02 | 近场测量规范 | IEEE 1720-2012, IEEE Recommended Practice for Near-Field Antenna Measurements | IEEE 标准 | A | 推荐平面、柱面、球面近场测量几何，涉及探头校准、数据交付、NF-FF 变换 | 支撑半柱面/半球面 2π 布局和近场数据格式设计 | 测试方案完整性、技术路线可行性 | https://standards.ieee.org/ieee/1720/4190/ |
| L03 | 近场测量综述 | Yaghjian, “An overview of near-field antenna measurements,” IEEE TAP, 1986 | IEEE TAP 经典综述 | A | 系统梳理近场测量、探头修正、采样定理、误差来源 | 作为“为什么用近场测量再推远场”的理论背景 | 国内外调研、研究思路合理性 | https://zenodo.org/records/1232233 |
| L04 | 任意曲面 NF-FF | Rodríguez Varela et al., “Near-field to far-field transformation on arbitrary surfaces via multi-level spherical wave expansion,” IEEE TAP, 2020 | IEEE TAP | A | 任意测量曲面、多球面波展开、探头修正、层次化子域降低复杂度 | 支持半球面/半柱面及后续不规则布设的高级路线 | 技术路线可行性、三维场域重建 | https://oa.upm.es/68614/ |
| L05 | 表面源重建条件 | Kornprobst et al., “Accuracy and Conditioning of Surface-Source Based Near-Field to Far-Field Transformations,” IEEE TAP, 2021 | IEEE TAP | A | 对逆表面源表述的精度和条件数进行比较；球形 Huygens 面条件较好，贴近凸包表面精度较高 | 支撑“紧包络 Huygens/等效源面 + 正则化”方案 | 三维场域重建、研究思路合理性 | https://arxiv.org/abs/2004.08918 |
| L06 | 平台安装等效表示 | Malmström et al., “On the Accuracy of Equivalent Antenna Representations,” IEEE TAP, 2018 | IEEE TAP | A | 比较近场源/远场源在简化平台安装条件下的误差，强调等效表示配置影响精度 | 适合航空载体安装效应：用等效源降低天线细节，再做平台级辐射推算 | 三维场域重建、复杂载体适用性 | https://arxiv.org/abs/1701.03275 |
| L07 | 受限域压缩感知 | Valdez, Yuffa, Wakin, “Restricted Domain Compressive Sensing for Antenna Metrology,” IEEE TSP, 2022 | IEEE TSP/NIST | A | 对球面近场到远场问题的受限测量域建立压缩感知保证，减少测点仍保持重建质量 | 直接支撑“2π 受限空域 + 少测点高精度重建” | 测点数量优化、三维场域重建 | https://www.nist.gov/publications/restricted-domain-compressive-sensing-antenna-metrology |
| L08 | 球面测点优化 | Bangun & Culotta-Lopez, “Optimizing Sensing Matrices for Spherical Near-Field Antenna Measurements,” IEEE TAP, 2023 | IEEE TAP | A | 通过降低感知矩阵互相干性优化球面采样点，少于经典采样数仍能重建 SMC/远场 | 迁移为互相干性最小化或信息增益最大化的测点优化 | 测点数量优化、技术创新 | https://arxiv.org/abs/2206.02181 |
| L09 | 无相位近场测量 | Fuchs et al., “Phaseless Near Field Antenna Measurements from Two Surface Scans,” IEEE TAP, 2020 | IEEE TAP | B | 双表面无相位扫描 + 源重构，可恢复远场并具备噪声/采样步长鲁棒性 | 若 CST/实测只能稳定导出幅值，可作为备用方案；主线仍用幅相 | 备选方案、工程可行性 | https://orbit.dtu.dk/en/publications/phaseless-near-field-antenna-measurements-from-two-surface-scans- |
| L10 | 等效源/任意几何 | Sarkar & Taaghol, near-field to near/far-field transformation for arbitrary geometry using equivalent currents, IEEE TAP, 1999 | IEEE TAP | B | 利用等效电/磁流和 MoM，从任意近场几何推算近/远场 | 支撑复杂测量面条件下的等效源反演主线 | 三维场域重建 | https://citeseerx.ist.psu.edu/document?doi=21158cf93cfda676eff960f10a097075d7f49d8f&repid=rep1&type=pdf |
| L11 | 三维等效电流重构 | Alvarez/Las-Heras 等，equivalent current reconstruction over arbitrary 3D surfaces, IEEE TAP | IEEE TAP | B | 在任意三维表面上重构等效电流，用于 NF-FF 和诊断 | 支撑后续由规则网格升级到贴近载体外形的等效源面 | 三维场域重建、创新拓展 | https://citeseerx.ist.psu.edu/document?doi=0083cce83fc1cd83582b7578d2784027ced1025c&repid=rep1&type=pdf |
| L12 | EMI 源识别与远场预测 | Regué et al., “A genetic algorithm based method for source identification and far-field radiated emissions prediction from near-field measurements,” IEEE TEMC, 2001 | IEEE TEMC | B | 用等效偶极子替代实际辐射源，通过近场识别源位置并预测远场 | 迁移为机载多设备等效偶极子/稀疏源定位 | 三维场域重建、特征解释 | https://merit.url.edu/en/publications/a-genetic-algorithm-based-method-for-source-identification-and-fa |
| L13 | 磁近场到远场 | Gao et al., “Far-field prediction using only magnetic near-field scanning for EMI test,” IEEE TEMC, 2014 | IEEE TEMC | B | 用磁近场扫描和等效定理预测 EMI 远场 | 支撑“近场测量可推远场”的工程可信度；后续可扩展 E/H 多分量 | 工程可行性、测试完整性 | https://mst.elsevierpure.com/en/publications/far-field-prediction-using-only-magnetic-near-field-scanning-for- |
| L14 | 自适应近场扫描 | Deschrijver et al., “Automated near-field scanning algorithm for the EMC analysis of electronic devices,” IEEE TEMC, 2012 | IEEE TEMC | B | 结合 Kriging/顺序采样选择近场扫描点，减少测量工作量 | 可迁移为主动测点选择：先粗扫，再对高梯度/高不确定区域加密 | 测点优化、测试效率 | https://biblio.ugent.be/publication/2983839 |
| L15 | 幅相同步顺序采样 | Sequential sampling algorithm for simultaneous near-field scanning of amplitude and phase, EMC Europe, 2014 | IEEE 会议 | C | 同时测量幅度和相位的 EMI 近场顺序采样 | 支持后续“主动学习式扫描”加分路线 | 测点优化、鲁棒性 | https://biblio.ugent.be/publication/5737107 |
| L16 | 混合等效源优化 | Hybrid equivalent source - particle swarm optimization model for NF-FF conversion, Applied Soft Computing, 2022 | 期刊 | C | 将等效源模型与粒子群优化结合，提高远场预测稳定性 | 若 Tikhonov/L1 不稳定，可加入启发式优化做对照 | 算法拓展 | https://www.sciencedirect.com/science/article/pii/S0167926022001730 |
| L17 | RF 指纹综述 | Soltanieh et al., “A review of radio frequency fingerprinting techniques,” IEEE JRFID, 2020 | IEEE 综述 | A | 综述瞬态、稳态、调制段 RF 指纹特征与分类方法 | 支撑“空-频-极化辐射指纹”的概念和特征工程 | 国内外调研、特征辨识 | https://research.monash.edu/en/publications/a-review-of-radio-frequency-fingerprinting-techniques/ |
| L18 | 雷达发射机机理特征 | Liu et al., “Feature Analysis and Extraction for Specific Emitter Identification Based on the Signal Generation Mechanisms of Radar Transmitters,” Sensors, 2022 | 机理型论文 | A | 从频率稳定度、RF 放大链非线性、脉冲前沿包络等机理提取 SEI 特征，多特征优于单特征 | 提示识别模块要做多特征融合，而不是只用单一方向图指标 | 特征辨识精度、解释性 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9003364/ |
| L19 | 真实雷达 SEI | Gok, Alp, Arikan, “A New Method for Specific Emitter Identification With Results on Real Radar Measurements,” IEEE TIFS, 2020 | IEEE TIFS | A | 真实雷达测量中用时间对齐、相干积分、VMD 提升微弱指纹差异识别 | 可迁移为多脉冲/多频点相干增强和稳健特征提取思想 | 特征辨识精度、工程可信度 | https://repository.bilkent.edu.tr/items/59a973bb-eea4-4a1a-a79e-823ba7251534 |
| L20 | 无监督 SEI | Gong, Xu, Lei, “Unsupervised Specific Emitter Identification Method Using RF Fingerprint Embedded InfoGAN,” IEEE TIFS, 2020 | IEEE TIFS | B | 用 InfoGAN 和 RF 指纹嵌入解决非合作场景缺少标签的问题 | 作为后续少标签/未知载体状态识别拓展，不作为初版主线 | 识别拓展、创新点 | https://dblp.dagstuhl.de/rec/journals/tifs/GongXL20.html |
| L21 | 深度复数网络 RFFI | Wang et al., “Radio Frequency Fingerprint Identification Based on Deep Complex Residual Network,” IEEE Access, 2020 | IEEE Access | B | 直接面向复数信号做端到端 RF 指纹识别，减少手工图像化损失 | 可迁移为直接输入复数空频极化向量的深度模型 | 特征辨识加分项 | https://cir.nii.ac.jp/crid/1871428067672396672 |
| L22 | 大规模 RF 指纹实验 | Jian et al., “Deep Learning for RF Fingerprinting: A Massive Experimental Study,” IEEE IoT Magazine, 2020 | IEEE Magazine | C | 10,000 台无线电的大规模 IQ 数据实验，讨论信道、噪声、训练规模影响 | 提醒报告必须讨论信道/姿态/噪声对指纹稳定性的影响 | 鲁棒性、工程应用 | https://researchr.org/publication/JianROSWSGDCI20 |
| L23 | 度量学习 SEI | Man et al., “A Specific Emitter Identification Algorithm under Zero Sample Condition Based on Metric Learning,” Remote Sensing, 2021 | 应用期刊 | B | 用度量学习解决工作参数变化、零样本条件下的 SEI 泛化 | 迁移到“同一载体不同工作状态”拉近、“不同载体”拉远的识别策略 | 特征辨识、状态泛化 | https://www.mdpi.com/2072-4292/13/23/4919 |
| L24 | RF 指纹综合综述 | Jagannath et al., “A Comprehensive Survey on Radio Frequency Fingerprinting,” arXiv, 2022 | 综述预印本 | C | 从传统方法、深度学习、数据集和开放问题系统总结 RFF | 用于补充发展趋势和开放挑战，不作为核心权威证据 | 国内外调研 | https://arxiv.org/abs/2201.00680 |
| L25 | 多频压缩测量 | Valdez, Folz, Wakin, Gordon, “Multi-frequency Antenna Metrology with Sparse Measurements,” IEEE JSTSP, 2024 | IEEE JSTSP/NIST | A | 将单频压缩感知扩展到宽带/多频球面近场测量，比较稀疏和低秩模型，证明多频模型可进一步减少测量量 | 直接支撑本赛题 Level 2 多频点联合采样、组稀疏/低秩空频模型和测点减少策略 | 测点数量优化、多频特征辨识、技术创新 | https://www.nist.gov/publications/multi-frequency-antenna-metrology-sparse-measurements |
| L26 | 受限域压缩采样 | Valdez, Yuffa, Wakin, “Restricted Domain Compressive Sensing for Antenna Metrology,” arXiv:2109.10040 | arXiv/天线计量 | A | 面向受限测量域建立压缩感知天线计量框架，强调受限空域下采样与重建矩阵性质 | 直接支撑本项目 2π 半球面不是完整闭合球面的少测点设计；用于设计互相干性/条件数/NDF 共同约束的采样优化 | 测点数量优化、受限空域重建 | https://arxiv.org/abs/2109.10040 |
| L27 | 最优采样直观方法 | Migliore, “An Intuitive Approach to the Optimal Sampling of an Electromagnetic Field,” Sensors, 2025 | Sensors | A | 从电磁场信息自由度角度解释最优采样，强调采样应匹配场的有效信息量而非机械加密 | 用于把 162 点全量校准升级为 NDF/非冗余采样论证，支撑 48/32 点候选集的理论边界 | 测点数量优化、方案创新 | https://www.mdpi.com/1424-8220/25/24/7591 |
| L28 | 自由度与采样表示 | Bucci and Migliore, “Degrees of Freedom and Sampling Representation of Electromagnetic Fields,” IEEE Antennas and Propagation Magazine, 2025 | IEEE Magazine | A | 系统讨论电磁场自由度、NDF 与采样表示的概念和应用 | 用作报告中“为什么可以非冗余采样”的核心理论入口；指导以自由度预算设定采样下限 | 国内外调研、测点优化理论 | https://doi.org/10.1109/MAP.2024.3513216 |
| L29 | 球面 NF-FF 变换 | Sarkar, Salazar-Palma, Zhu, Chen, “Spherical Near-Field to Far-Field Transformation,” in Modern Characterization of Electromagnetic Systems and its Associated Metrology, 2021 | IEEE/Wiley 章节 | A | 给出球面近场到远场变换的标准理论链路 | 作为本项目等效源法的物理基线和坐标/极化/相位 sanity check，而不是替代复杂载体等效源主线 | 三维场域重建、物理可信度 | https://doi.org/10.1002/9781119076230.ch7 |
| L30 | 非冗余球面近场采样 | “Non-redundant spherical near-field sampling for efficient incident power density assessment for Electromagnetic Safety,” Frontiers in Antennas and Propagation, 2025 | Frontiers | A | 通过非冗余球面近场表示减少样本量，用于 IPD 等目标量评估 | 迁移为任务驱动采样：远场重建最优测点与分类识别最优测点可分开评估 | 非冗余采样、任务驱动测量 | https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2025.1738329/full |
| L31 | 球面近场工程实践 | RWTH Aachen IHF, “Spherical Near-Field Measurements” | 实验室工程资料 | B | 说明球面近场测量通过探头在球面采集近场并转换为完整三维远场方向图 | 用于完善 CST/实测 runbook 中的探头、坐标、极化、扫描和远场转换流程 | 测试方案完整性、工程可行性 | https://www.ihf.rwth-aachen.de/en/research/research-topics/antenna-measurement/spherical-near-field-measurements |

## 3. 对本赛题的文献结论归纳

### 3.1 测量系统路线

IEEE 149 和 IEEE 1720 共同说明，方向图测量和近场测量需要明确测试场、探头、坐标、极化、校准和数据交付格式。本赛题要求 2π 半球面或半柱面覆盖，不能只用单角度远场测量。因此方案应采用参数化半球面/半柱面传感布局，并从一开始固定 `sensor_id, x, y, z, frequency, polarization, complex field` 等字段。

### 3.2 重建算法路线

经典球面/柱面/平面 NF-FF 变换理论成熟，但对规则测量几何、采样完备性和探头修正要求较高。复杂航空载体存在安装效应和不规则外形，更适合采用等效源/表面源重构路线：先在载体外包络建立 Huygens 面或等效偶极子网格，再用正则化反演等效源，最后外推远场。

### 3.3 少测点路线

受限域压缩感知和球面感知矩阵优化文献直接对应赛题“2π 受限空域 + 尽量少测点”的客观评分要求。初版方案应至少给出全测点、随机稀疏、规则稀疏和优化稀疏四类对照，用 NMSE、方向图相关系数、主瓣误差和测点数共同排序。

### 3.4 特征辨识路线

RF/雷达指纹文献说明，稳定识别不能只依赖单一幅度指标，应融合频谱、相位、瞬态/稳态、硬件非理想和多尺度特征。本赛题的数据天然包含空间方向、频率和极化维度，因此建议构造“空间-频谱-极化-等效源”联合指纹：方向图形态用于载体空间特征，频谱峰值/相关性用于运行状态，极化比和等效源能量分布用于增强唯一性。

## 4. 报告引用优先级

方案报告中建议主引用 L01-L08、L17-L19、L25-L30，保证主线权威；L09-L16、L20-L24 和 L31 放在“备选方案、拓展方向、工程实践与鲁棒性讨论”中。这样既不会把报告写散，也能体现调研广度。
