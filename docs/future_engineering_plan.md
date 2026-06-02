# 未来工程方案

版本：v1.1
更新依据：当前 GitHub 工程状态、CST Level 1 诊断结果、导师 DeepSeek 记录、文献矩阵和新增非冗余采样/反演校准脚本。

## 1. 当前工程判断

项目已经形成可协作的主链路：

```text
半球 2pi 测点设计
  -> CST Level 1 标准源数据
  -> Python near/far-field 数据合并与校验
  -> 等效源反演和远场外推
  -> 少测点采样对比
  -> 空域/频率/极化特征分类
  -> 报告、PPT、提交包和复现文档
```

当前最重要的判断不是“流程能否跑通”，而是“哪些证据可以写进报告，哪些还只能作为诊断”。目前结论如下：

| 模块 | 当前状态 | 工程含义 |
|---|---|---|
| 仓库整理 | 已建立可协作目录和 GitHub public 仓库 | 队友可以按 README、docs 和脚本入口接手。 |
| 非冗余采样候选 | 已生成 162/120/81/48/32 点候选布局 | 可作为 CST 复跑计划，不能单独作为最终少测点证明。 |
| Level 1 中心源 sanity check | `corr_pass_nmse_near`，主瓣误差为 0 | CST 导出、Python 读取和远场比较链路总体可信。 |
| 通用等效源网格 | `diagnostic_only` | 不能用它直接宣称 120/81/48/32 点方案有效。 |
| 稀疏等效源 | Corr/NMSE 明显改善，但主瓣仍未过关 | 稀疏有帮助，但不能替代物理源先验。 |
| 相位/极化约定检查 | 未发现能救活通用网格的简单全局约定错误 | 下一步应转向 Huygens/SWE/结构先验，而不是继续盲调符号。 |

## 2. 文献和导师建议的工程化吸收

导师 DeepSeek 记录和推荐文献可以归纳为五条工程原则：

1. 半球测量应以载体几何中心为坐标原点，测量半径要覆盖 `12 m x 10 m x 8 m` 包络并留余量。
2. 测点必须保留双极化复数场信息，不能只保留单通道幅值。
3. 少测点不是随机删点，而是要结合电磁场自由度、非冗余采样、互相干性和任务指标。
4. 远场外推应至少有一个规范物理基线，例如球面 NF-FF/SWE sanity check。
5. 分类不应只依赖单张方向图，应联合空域、频率、极化、等效源或球谐特征。

对应到项目，后续路线应把“采样、反演、分类”三块统一起来，而不是各自独立优化。

## 3. 下一阶段路线图

### G1：仓库协作与目录冻结

目标：让队友不依赖口头解释也能接手。

已完成：

- GitHub public 仓库已建立并推送主工程。
- `code/`、`data/`、`docs/`、`CST/` 等目录已整理。
- 小型 CSV/JSON/README 结果进入 Git；大型 CST 导出默认本地保留。

后续动作：

- 增加 `.github/ISSUE_TEMPLATE/`，至少包含 CST 样本提交、算法实验、文档修改、bug 四类模板。
- 在 README 中补充“哪些文件不进 Git、哪些结果必须附摘要”的协作规则。

### G2：采样方案升级

目标：从 162 点全量校准走向非冗余少测点方案。

已完成：

- `code/optimize_sampling_layout.py`
- `data/sampling_layouts/hemisphere_sampling_candidates.csv`
- `data/sampling_layouts/sampling_layout_summary.csv`
- `docs/nonredundant_sampling_design.md`

下一步：

1. 等 full-grid 物理反演基线稳定后，复跑 120/81/48/32 点候选。
2. 把采样方案分为两类：远场重建优先布局、分类识别优先布局。
3. 对 48/32 点方案增加任务驱动加权，例如主瓣、高能角域、极化差异和分类贡献区域。

建议判据：

```text
若 48 点在 Level 1/2 上保持 Corr >= 0.98 且分类 accuracy >= 0.85，
可作为主少测点方案；

若 32 点重建下降但分类稳定，
可作为“识别优先”低成本方案；

若 81 点显著更稳，
报告采用 81 点作为工程保守方案，48/32 点作为探索方案。
```

### G3：反演算法升级

目标：把 Tikhonov 等效源 baseline 升级成多模型可比较的反演工具箱。

已完成：

| 产物 | 结论 |
|---|---|
| `data/sampling_layouts/cst_level1_source_model_sweep/` | 中心源先验最好，通用网格仍诊断态。 |
| `data/sampling_layouts/cst_level1_sparse_calibration/` | group-sparse 提升 Corr/NMSE，但主瓣仍未达标。 |
| `data/sampling_layouts/cst_level1_convention_check/` | 未发现可直接解决通用网格问题的简单相位/极化约定错误。 |

下一步优先级：

1. 明确当前 Level 1 数据边界：nearfield 表来自 CST FarfieldPlot list evaluation，不是真正 full-wave 近场 monitor。
2. 准备一版真正的球面近场 monitor 导出任务包，用同一套脚本对比 FarfieldPlot-derived 样本和 near-field monitor 样本。
3. 增加 Huygens 面源或贴体/结构先验，避免自由点源网格把能量泄漏到非物理位置。
4. 增加球面 NF-FF/SWE sanity check，用于独立检查坐标、相位、极化和角度约定。
5. 做多频 group sparsity，让多个频点共享源支撑位置，只允许幅相随频率变化。

建议统一输出：

```text
reconstruction_metrics.csv
farfield_comparison.png
sensor_tradeoff.csv
model_comparison.md
```

### G4：复杂载体与安装效应增强

目标：从 element-library 和简化遮挡对照，走向更可信的航空载体结构影响分析。

后续动作：

1. 建立简化机身、翼面、尾翼参数化模型。
2. 建立源安装位置、朝向、工作状态配置表。
3. 比较无结构、有简化结构、局部遮挡三种情形的方向图差异。
4. 做跨结构域验证：无结构训练 -> 有结构测试，有结构训练 -> 无结构测试。

报告口径：

- element-library 证明源/状态可区分；
- 简化结构对照证明安装效应显著；
- full-wave airframe 是增强项，用于提高工程可信度。

### G5：分类识别泛化

目标：从“当前样本准确”升级为“面对噪声、缺测、结构变化仍可信”。

后续动作：

- 增加噪声强度、相位扰动、测点缺失、频点缺失消融。
- 对比 SVM、Random Forest、XGBoost、度量学习等模型。
- 增加特征重要性：空域、频率、极化、等效源/球谐特征各自贡献。
- 固定训练/测试划分和随机种子，避免偶然高分。

### G6：报告与答辩增强

目标：把方案从“材料齐全”提升为“评审容易相信”。

需要强化的叙事：

1. 为什么半球 2pi 不是任意选择：对应球面近场测量和受限区域采样。
2. 为什么少测点可行：自由度/NDF、非冗余采样、误差曲线三重证据。
3. 为什么能外推远场：球面 NF-FF 规范基线和等效源反演增强路线。
4. 为什么能分类：空域、频率、极化、等效源/球谐特征联合指纹。
5. 当前边界是什么：FarfieldPlot-derived Level 1 样本、element-library 和简化结构不是最终复杂载体 full-wave 证明。

## 4. 近期 Sprint 建议

按当前工程价值，建议下一轮按这个顺序推进：

1. 已新增 CST true near-field monitor 导出工作包、宏骨架和对照脚本；下一步等待 CST 真 monitor 实测 CSV 回填。
2. 实现 `code/run_spherical_nf_ff_baseline.py` 的轻量 SWE/NF-FF sanity check。
3. 写 `docs/huygens_surface_model_note.md`，明确面源模型、未知量、正则化和输出指标。
4. 在当前 Level 1 两个标准源上复跑：center prior、generic grid、group-sparse、convention check、SWE sanity baseline。
5. 只有当 full-grid 基线达到验收标准后，再复跑 120/81/48/32 点候选并更新报告。

## 5. 参考链接

- DeepSeek 导师分享记录：`https://chat.deepseek.com/share/n42ew5j5gw8vx7unqd`
- Restricted Domain Compressive Sensing for Antenna Metrology：`https://arxiv.org/abs/2109.10040`
- Migliore, An Intuitive Approach to the Optimal Sampling of an Electromagnetic Field：`https://www.mdpi.com/1424-8220/25/24/7591`
- Bucci and Migliore, Degrees of Freedom and Sampling Representation of Electromagnetic Fields：`https://doi.org/10.1109/MAP.2024.3513216`
- Sarkar et al., Spherical Near-Field to Far-Field Transformation：`https://doi.org/10.1002/9781119076230.ch7`
- Non-redundant spherical near-field sampling for efficient incident power density assessment：`https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2025.1738329/full`
- RWTH Aachen spherical near-field measurements：`https://www.ihf.rwth-aachen.de/en/research/research-topics/antenna-measurement/spherical-near-field-measurements`
