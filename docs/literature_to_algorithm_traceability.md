# 文献到算法迁移证据链

版本：v0.1  
用途：把权威文献结论、赛题需求、算法模块、当前文件和待补 CST 证据逐项对应，供方案报告、答辩和队内分工使用。

## 1. 为什么需要这张表

赛题要求的不只是“能跑 CST”，而是能说明为什么选择半球面测量、为什么能由近场推远场、为什么可以减少测点、为什么空频特征能识别载体/状态。因此每个核心模块都需要有明确的文献依据和工程落点。

本表采用如下链条：

```text
文献/标准结论 -> 可迁移策略 -> 本项目算法/文件 -> 需要补强的真实证据
```

## 2. 核心迁移链条

| 模块 | 权威依据 | 文献结论 | 迁移到赛题的策略 | 当前落地文件 | 待补证据 |
|---|---|---|---|---|---|
| 天线测量规范 | IEEE 149-2021 | 方向图、测试场、仪器链路、测试设施评价是天线测量的基础内容 | 报告中固定方向图、极化、远场真值和测试链路，不只展示软件截图 | `docs/solution_report_draft.md`, `docs/data_dictionary.md` | CST 工程截图、边界/端口/监视器设置、远场导出记录 |
| 近场测量规范 | IEEE 1720-2012 | 近场测量包含平面、柱面、球面三类主几何，并强调探头校准和数据交付 | 当前选择半球面 2π；保留半柱面作为工程扩展；统一 CSV 字段 | `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`, `code/check_cst_export.py` | 真实 CST nearfield/farfield 数据通过校验 |
| 表面源重构 | Kornprobst et al., IEEE TAP 2021 | 重构面选择影响条件数和精度；球形 Huygens 面条件较好，贴近凸包面精度较高 | 初版用规则等效源网格稳定实现；后续升级为贴近载体包络的 Huygens 面 | `code/em_core.py`, `code/run_cst_reconstruction.py` | Level 1/Level 2 真实 CST 重建 NMSE、相关系数、主瓣误差 |
| 受限域压缩感知 | Valdez/Yuffa/Wakin, IEEE TSP 2022 | 在受限测量域的球面近远场问题中，可用 Slepian/压缩感知框架减少测量 | 半球面 2π 属于受限域；用测点优化和正则化支撑少测点重建 | `code/run_reconstruction_robustness.py`, `outputs/reconstruction_robustness` | 用真实 CST 数据复跑测点比例曲线 |
| 多频压缩测量 | Valdez/Folz/Wakin/Gordon, IEEE JSTSP 2024 | 多频稀疏/低秩模型可比单频压缩感知进一步减少测量数 | Level 2 已设计 5 个频点；后续使用多频共享源位置或低秩空频矩阵 | `outputs/cst_level2_plan`, `code/run_cst_recognition_ablation.py` | 真实 Level 2 多频 nearfield 与识别删减实验 |
| 测点矩阵优化 | Bangun & Culotta-Lopez, IEEE TAP 2023 | 优化球面近场感知矩阵互相干性可减少测量点 | 用最远点/互相干性近似选择半球面测点，与随机删点对照 | `outputs/baseline/sampling_tradeoff.png`, `outputs/reconstruction_robustness` | 基于真实 CST 的 100/75/50/25% 测点对比 |
| 平台安装等效表示 | Malmström et al., IEEE TAP 2018 | 等效天线表示会影响平台安装场计算精度 | Level 3 简化载体阶段用等效源降低天线细节，再验证安装遮挡与散射 | `docs/phase_01_cst_technical_route_and_division.md` | 简化航空载体 CST 工程和安装效应方向图 |
| RF 指纹综述 | Soltanieh et al., IEEE JRFID 2020 | RF 指纹需要多类特征和分类方法，不宜依赖单一幅度指标 | 构造空间、频谱、极化、等效源联合特征 | `code/run_cst_recognition.py`, `outputs/cst_recognition_demo` | 真实 CST Level 2 准确率、F1、混淆矩阵 |
| 雷达/发射机机理特征 | Liu et al., Sensors 2022; Gok et al., IEEE TIFS 2020 | 发射机识别应利用机理相关多特征，并考虑真实测量条件下的微弱差异增强 | 特征辨识中保留频点相关、相位/极化、源能量分布，必要时做多频相干增强 | `docs/phase_03_cst_level2_multisource_recognition_protocol.md` | 多状态真实样本下的特征重要性和误分类分析 |

## 3. 对当前技术路线的具体约束

### 3.1 半球面 2π 不是随意选择

IEEE 1720-2012 将球面近场列为主要近场测量几何之一；NIST/IEEE TSP 受限域压缩感知研究讨论了球面近场到远场问题中受限测量域的压缩采样。这与当前“上半球面 2π、162 点、双极化/三分量场”的选择一致。

因此当前路线固定为：

```text
13 m 半径上半球面 -> CST nearfield Ex/Ey/Ez -> Python 投影/重建 -> CST farfield 真值对比
```

半柱面保留为工程扩展，不再混入本轮 Level 1/Level 2 执行，避免测点表和导出格式分裂。

### 3.2 等效源面先规则、后贴体

Kornprobst 等关于表面源重构的结论说明，重构表面的条件数和精度会随表面形状变化。当前阶段没有真实复杂载体 CST 数据，先用规则等效源网格保证算法闭环；真实 Level 1 通过后，再考虑两级重构面：

| 阶段 | 重构面 | 目的 |
|---|---|---|
| Level 1 | 规则点源/偶极源网格 | 验证坐标、相位、极化和远场角度 |
| Level 2 | 规则 Huygens 面或载体外包络网格 | 支撑多源重建和识别 |
| Level 3 | 贴近简化航空载体凸包的等效源面 | 提高安装效应建模精度 |

### 3.3 少测点不只看准确率

压缩测量文献的启发不是“随便删点”，而是利用场的结构先验。因此报告中的少测点方案必须同时给出：

| 指标 | 作用 |
|---|---|
| NMSE | 衡量方向图整体误差 |
| Corr | 衡量方向图形态相似度 |
| Main-lobe error | 衡量主瓣定位是否可靠 |
| Peak error | 衡量峰值估计是否可靠 |
| Sensor count | 量化测点压缩收益 |

当前合成鲁棒性结果显示 75% 测点更稳，50% 测点需要真实 CST 复核，25% 测点只能作为极限对照。

### 3.4 识别要有物理可解释特征

RF 指纹文献提示，稳定识别依赖多维特征。对本赛题，最自然的特征并不是一张方向图图片，而是：

```text
空间方向图形态 + 频点间变化 + 极化功率比 + 等效源能量分布
```

所以当前 `run_cst_recognition.py` 保留以下特征方向：

- 每个频点的空间幅度分布。
- theta/phi 投影后的双极化功率。
- 频点间统计量和频谱斜率。
- 后续可加入等效源系数特征。

## 4. 报告写作迁移模板

可在报告“研究思路合理性”中使用如下逻辑：

1. IEEE 149 和 IEEE 1720 说明本题应按天线/近场测量规范定义场地、极化、校准和数据格式。
2. 复杂航空载体存在安装散射和多源耦合，直接依赖 CST 远场图不足以体现自研算法，因此采用等效源/Huygens 面重构。
3. 2π 半球面属于受限测量域，受限域压缩感知和多频压缩测量文献支持在结构先验下减少测点。
4. 空间-频谱-极化联合特征与 RF 指纹文献一致，能把重建结果转化为可分类的辐射指纹。
5. 因此本方案形成“标准化采集 - 物理重建 - 少测点优化 - 物理可解释识别”的闭环。

## 5. 当前文件与评分项对应

| 评分项 | 可引用文件 | 当前证据强度 | 补强方式 |
|---|---|---|---|
| 国内外发展调研分析 | `docs/literature_matrix.md`, 本文件 | draft evidence | 统一参考文献格式，加入最终报告 |
| 研究思路合理性 | `docs/solution_report_draft.md`, `docs/phase_01_cst_technical_route_and_division.md` | draft evidence | 用真实 CST Level 1 证明路线可运行 |
| 技术路线可行性 | `code/check_cst_export.py`, `code/run_cst_reconstruction.py`, `code/prepare_cst_macro_templates.py` | interface evidence | G2/G3 真实数据通过审计 |
| 测试方案完整性 | `docs/data_dictionary.md`, `outputs/cst_execution_logs`, `outputs/cst_macro_templates` | execution-ready | 补 CST 工程截图和执行日志 |
| 三维场域重建 | `outputs/cst_reconstruction_demo`, `outputs/synthetic_cst_level1_dataset` | synthetic/demo | 替换为真实 CST 标准源/多源结果 |
| 特征辨识精度 | `outputs/cst_recognition_demo`, `outputs/cst_recognition_ablation` | synthetic/demo | 替换为真实 Level 2 识别结果 |

## 6. 本轮补查来源

- IEEE 149-2021: https://standards.ieee.org/ieee/149/6667/
- IEEE 1720-2012: https://standards.ieee.org/ieee/1720/4190/
- Valdez, Yuffa, Wakin, “Restricted Domain Compressive Sensing for Antenna Metrology,” IEEE TSP, 2022: https://www.nist.gov/publications/restricted-domain-compressive-sensing-antenna-metrology
- Valdez, Folz, Wakin, Gordon, “Multi-frequency Antenna Metrology with Sparse Measurements,” IEEE JSTSP, 2024: https://www.nist.gov/publications/multi-frequency-antenna-metrology-sparse-measurements
- Kornprobst et al., “Accuracy and conditioning of surface-source based near-field to far-field transformations,” IEEE TAP, 2021: https://portal.fis.tum.de/en/publications/accuracy-and-conditioning-of-surface-source-based-near-field-to-f/
