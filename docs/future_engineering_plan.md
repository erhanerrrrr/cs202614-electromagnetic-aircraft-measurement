# 未来工程方案

版本：v1.0  
依据：当前工程进展、已有文献矩阵、导师 DeepSeek 分享记录、导师新增推荐文献。

## 1. 当前工程判断

当前项目已经完成一条能跑通的主链：

```text
半球面 2π 采样
  -> CST Level 1 标准源校准
  -> CST Level 2 element-library 多源样本
  -> Python 合并、重建、识别、消融
  -> 报告/PPT/视频/提交包
```

它的价值是证明“数据格式、CST 导出、重建、识别、审计”已经闭环。下一阶段的核心不是重新搭一条链，而是把这条链从“可运行”升级为“采样更少、物理更强、复杂载体更可信、协作更稳定”。

## 2. 导师 DeepSeek 记录可吸收的要点

导师分享记录中可吸收的工程启发主要有五点：

1. 半球面测试应以被测载体几何中心为坐标原点，半径需要覆盖 `12 m x 10 m x 8 m` 包络并留裕量。
2. 传感器应至少保留双极化宽带幅相信息，不能只记录单通道幅值。
3. 测点可以从均匀半球面开始，再用 Fibonacci/低差异序列/互相干性优化向 `48` 或 `32` 点压缩。
4. 少测点成立的关键不是“少放几个探头”，而是把球谐/等效源/压缩感知作为重建模型。
5. 分类应使用空间方向图、频率变化、极化比和球谐/等效源系数等联合特征，而不是只对一张方向图做黑箱分类。

当前项目与这些建议的关系：

| DeepSeek 建议 | 当前状态 | 后续动作 |
|---|---|---|
| 半球面布局 | 已采用 13 m、162 点半球面 | 增加 48/32 点非冗余候选集 |
| 双极化/幅相 | 已保留复数场和极化字段 | 增加相位参考、探头校准和不确定度说明 |
| 压缩采样 | 已有 50%/75% baseline 与消融思路 | 引入 NDF、互相干性、Slepian/受限域压缩感知 |
| 等效源重建 | 已有规则等效源 + Tikhonov | 升级到 L1/组稀疏、多频联合、贴体 Huygens 面 |
| 联合特征分类 | 已有空-频-极化识别 | 加入等效源特征、跨结构域验证和噪声鲁棒性 |

## 3. 新增推荐文献的工程含义

### 3.1 arXiv 2109.10040：受限域压缩感知

该文献讨论受限测量域中的天线计量压缩感知问题，直接对应本项目的 `2π` 半球面场景。对我们最有用的不是照搬公式，而是建立两条工程规则：

1. 半球面是受限域，不要把全球采样理论机械套用到 2π。
2. 测点压缩要用场的低维结构和感知矩阵性质解释，不能只凭随机删点。

落地动作：

- 在 `code/` 增加 `optimize_sampling_layout.py`，输出 162/120/81/48/32 点候选集。
- 指标加入感知矩阵互相干性、条件数、NDF 估计和重建误差曲线。
- 用 `data/cst_exports/level1/` 与 `level2/` 复跑压缩比例实验。

### 3.2 Migliore 2025 与 Bucci/Migliore 2025：自由度与非冗余采样

这两篇的共同启发是：电磁场在有限观测区域内有有限自由度，采样应匹配信息自由度，而不是无限加密网格。

落地动作：

- 在 workflow 中增加 `NDF budget`：先估计被测包络尺寸、最高频率、观测区域对应的信息自由度，再决定测点数量下限。
- 把“162 点全量”改写成“稳定校准全量”，把“48/32 点”作为 NDF/非冗余采样验证目标。
- 在报告里把少测点论证从经验曲线升级为“自由度估计 + 重建误差 + 分类精度”的三重证据。

### 3.3 Sarkar 等球面近远场变换章节：物理基线

球面近场到远场变换是标准物理链路。我们的等效源方法更灵活，但仍需要一个球面 NF-FF 基线来校验坐标、角度、极化、相位定义。

落地动作：

- 增加一个轻量球面波/球谐投影 sanity check，不追求替代等效源主线，只用于发现坐标和相位错误。
- 在 Level 1 标准源中比较 CST farfield、等效源 farfield、球面基线 farfield。
- 报告中把球面 NF-FF 写成“规范基线”，把等效源/压缩感知写成“复杂载体增强路线”。

### 3.4 Frontiers 2025 非冗余球面近场采样

这篇文章强调通过非冗余表示减少球面近场样本，并服务于 incident power density 这类安全评估任务。对本项目的迁移点是：评估量不一定必须先完整恢复所有场细节，可以围绕目标指标做非冗余采样。

落地动作：

- 把输出指标分为两类：远场方向图重建指标与分类识别指标。
- 对分类任务单独训练“任务驱动采样集”，允许它与远场最优采样集不同。
- 对高贡献角域/频点进行主动加密，对低贡献区域稀疏化。

### 3.5 RWTH 球面近场测量资料：工程测试流程

RWTH 页面体现了球面近场测量的工程事实：探头在球面上采集近场，通过变换得到完整三维远场方向图。对项目最有价值的是把坐标、探头、转台/扫描、校准和远场转换流程说规范。

落地动作：

- CST runbook 中补充“探头校准、相位参考、坐标零点、转台角度、极化定义”的检查项。
- 报告中增加一张“真实测量系统链路图”：载体、半球测点、接收链路、参考同步、Python 重建。
- GitHub issue 模板中加入 CST/实测数据提交 checklist。

## 4. 下一阶段路线图

### G1：仓库协作与目录冻结

目标：让队友能快速接手，不再靠口头解释。

交付：

- GitHub public 仓库。
- `README.md`、各一级目录 README、`.gitignore`。
- issue 模板：CST 样本提交、算法实验、文档修改、bug。
- 约定大文件策略：CST 缓存不进 Git，必要时用 Git LFS/Release/网盘。

### G2：采样方案升级

目标：从 162 点全量校准走向非冗余少测点方案。

交付：

- 162/120/81/48/32 点候选测点表。
- 几何均匀、Fibonacci/低差异、互相干性优化、任务驱动选点四类对照。
- 每类候选集输出 `NMSE-Corr-SensorCount-Accuracy` 表。

判断标准：

```text
若 48 点在 Level 1/2 上保持 Corr >= 0.98 且分类 accuracy >= 0.85，则作为主少测点方案；
若 32 点重建下降但分类保持稳定，则作为“识别优先”方案；
若 81 点明显更稳，则报告采用 81 点为工程保守方案，48/32 点作为探索。
```

### G3：反演算法升级

目标：把当前 Tikhonov 等效源 baseline 升级为多模型可比的反演工具箱。

交付：

| 模型 | 目的 |
|---|---|
| Tikhonov | 稳定基线 |
| L1 / ElasticNet | 稀疏等效源 |
| Group Lasso | 多频共享源位置 |
| Low-rank 空频模型 | 多频联合压缩 |
| 球谐/SWE sanity check | 坐标、相位、极化校验 |

输出统一为：

```text
reconstruction_metrics.csv
farfield_comparison.png
sensor_tradeoff.csv
model_comparison.md
```

### G4：复杂载体与安装效应增强

目标：从 element-library 和简化遮挡对照走向更可信的航空载体结构影响分析。

交付：

1. 简化机身/翼面/尾翼几何参数化模型。
2. 源安装位置、朝向、开关状态配置表。
3. full-wave 或混合近似下的结构遮挡/散射对照。
4. 跨域识别测试：无结构训练 -> 有结构测试、有结构训练 -> 无结构测试。

报告口径：

- 当前 element-library 证明源/状态可区分。
- 简化结构对照证明安装效应显著。
- full-wave airframe 是增强项，用于提高工程可信度。

### G5：分类识别泛化

目标：识别结果从“当前样本准确”升级为“面对噪声、缺测、结构变化仍可信”。

交付：

- 噪声强度、相位扰动、测点缺失、频点缺失消融。
- SVM/RF/XGBoost/度量学习四类模型对照。
- 特征重要性：空间、频率、极化、等效源各自贡献。
- 训练/测试划分固定随机种子，避免偶然高分。

### G6：报告与答辩增强

目标：把方案从“材料齐套”提升为“评审容易信服”。

需要补强的叙事：

1. 为什么半球面 2π 不是任意选的：标准近场测量 + 受限域压缩采样。
2. 为什么少测点可行：自由度/NDF + 非冗余采样 + 误差曲线。
3. 为什么能外推远场：球面 NF-FF 标准链路 + 等效源反演。
4. 为什么能分类：空-频-极化-等效源联合指纹。
5. 当前边界是什么：element-library 与简化结构不是完整复杂载体 full-wave。

## 5. 文件级任务建议

| 任务 | 建议文件 |
|---|---|
| 新增少测点优化脚本 | `code/optimize_sampling_layout.py` |
| 新增 NDF/非冗余采样说明 | `docs/nonredundant_sampling_design.md` |
| 新增球面 NF-FF sanity check | `code/run_spherical_nf_ff_baseline.py` |
| 新增复杂载体参数表 | `CST/airframe_model_plan.md` |
| 新增 GitHub issue 模板 | `.github/ISSUE_TEMPLATE/` |
| 更新文献矩阵 | `docs/literature_matrix.md` |

## 6. 参考链接

- DeepSeek 导师分享记录：`https://chat.deepseek.com/share/n42ew5j5gw8vx7unqd`
- Restricted Domain Compressive Sensing for Antenna Metrology：`https://arxiv.org/abs/2109.10040`
- Migliore, An Intuitive Approach to the Optimal Sampling of an Electromagnetic Field：`https://www.mdpi.com/1424-8220/25/24/7591`
- Bucci and Migliore, Degrees of Freedom and Sampling Representation of Electromagnetic Fields：`https://doi.org/10.1109/MAP.2024.3513216`
- Sarkar et al., Spherical Near-Field to Far-Field Transformation：`https://doi.org/10.1002/9781119076230.ch7`
- Non-redundant spherical near-field sampling for efficient incident power density assessment：`https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2025.1738329/full`
- RWTH Aachen spherical near-field measurements：`https://www.ihf.rwth-aachen.de/en/research/research-topics/antenna-measurement/spherical-near-field-measurements`
