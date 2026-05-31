# CS-202614 项目 Workflow

版本：v1.0  
用途：把“采样方案确定 - CST 建模与数据接入 Python - 算法外推反演 - 分类识别”说清楚，作为队内协作和后续 GitHub 任务拆分依据。

## 1. 总体闭环

本项目不是单独做 CST 图，也不是单独训练分类器，而是一条可复现的数据闭环：

```text
赛题需求与文献约束
  -> 2π 半球面采样方案
  -> CST 参数化建模与导出合同
  -> Python 数据校验、合并、坐标/极化归一化
  -> 等效源/球面近远场重建
  -> 少测点压缩与误差评估
  -> 空-频-极化特征构造
  -> 载体/工作状态分类识别
  -> 报告、PPT、视频、提交包与审计
```

当前工程已经落地为：

| 环节 | 当前主文件/目录 |
|---|---|
| 采样与 baseline | `code/em_core.py`, `code/run_baseline.py`, `outputs/baseline/` |
| CST 模板/任务包 | `code/prepare_cst_templates.py`, `code/prepare_cst_level1_workpack.py`, `code/prepare_cst_level2_workpack.py`, `outputs/cst_*` |
| CST 导出数据 | `data/cst_exports/level1/`, `data/cst_exports/level2/` |
| 数据校验合并 | `code/check_cst_export.py`, `code/merge_cst_level1_exports.py`, `code/merge_cst_level2_exports.py` |
| 重建外推 | `code/run_cst_reconstruction.py`, `code/run_cst_level1_batch_reconstruction.py`, `code/run_cst_level1_angular_calibration.py` |
| 分类识别 | `code/run_cst_recognition.py`, `code/run_cst_recognition_ablation.py` |
| 证据与交付 | `outputs/scorecard/`, `outputs/completion_audit/`, `submission/` |

## 2. 工作块 A：采样方案确定

### 2.1 目标

确定半球面 2π 测量布局，使其同时满足：

1. 覆盖上半空间 2π 立体角。
2. 容纳不小于 `12 m x 10 m x 8 m` 的复杂航空载体。
3. 支撑近场到远场外推和特征识别。
4. 在保持精度的前提下尽量减少测点。

### 2.2 当前方案

当前主方案为 `13 m` 半径上半球面、`162` 个空间测点，保留双极化/多分量场信息。这个方案先作为稳定全量基准，不直接等同于最终最少测点方案。

后续少测点路径应分三层：

| 层级 | 做法 | 目的 |
|---|---|---|
| 全量基准 | 162 点半球面均匀覆盖 | 保证 CST/Python 坐标、相位、极化链路稳定 |
| 工程压缩 | 75%、50% 测点，几何最远点或低差异序列 | 找到精度-测点数拐点 |
| 非冗余优化 | NDF/互相干性/信息增益/主动学习选点 | 向 48 点、32 点甚至更低点数探索 |

### 2.3 CST/Python 接口

CST 侧必须固定导出合同，否则后续脚本无法稳定读取。近场 CSV 至少包含：

```text
sample_id, frequency_hz, sensor_id, x_m, y_m, z_m,
theta_deg, phi_deg, polarization,
Ex_real, Ex_imag, Ey_real, Ey_imag, Ez_real, Ez_imag
```

远场 CSV 至少包含：

```text
sample_id, frequency_hz, theta_deg, phi_deg,
Etheta_real, Etheta_imag, Ephi_real, Ephi_imag
```

执行顺序：

```powershell
python code\prepare_cst_templates.py
python code\prepare_cst_level1_manifest.py
python code\prepare_cst_level1_workpack.py
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
```

## 3. 工作块 B：算法外推反演

### 3.1 物理模型

近场测量向量可写为：

```text
E_nf(f) = G_nf(f) J(f) + n(f)
E_ff(f) = G_ff(f) J(f)
```

其中 `J(f)` 是等效源系数，`G_nf` 是等效源到测点的传播矩阵，`G_ff` 是等效源到远场角域的传播矩阵。

### 3.2 当前基线

当前代码采用规则等效源网格与 Tikhonov 正则化，先保证稳定可复现：

```powershell
python code\run_cst_level1_batch_reconstruction.py
python code\run_cst_level1_angular_calibration.py
```

已验证的主指标包括：

| 指标 | 作用 |
|---|---|
| NMSE | 衡量远场整体重建误差 |
| pattern correlation | 衡量方向图形态一致性 |
| peak/main-lobe error | 衡量峰值和主瓣方向可靠性 |
| sensor count | 衡量测点压缩收益 |

### 3.3 后续增强

后续不应只继续调参，而应按物理先验逐步增强：

1. 球面近场到远场变换作为理论对照，校验坐标、角度和极化定义。
2. 等效源面从规则网格升级为贴近载体外包络的 Huygens 面。
3. 单频 Tikhonov 升级为 L1/组稀疏，利用源分布稀疏性。
4. 多频联合建模，利用不同频点共享源位置或低秩空频结构。
5. 对半球面受限空域引入 Slepian/受限域压缩感知思想，降低非观测半空间带来的病态性。

## 4. 工作块 C：分类识别

分类不是脱离物理模型单独做图像分类，而是把重建结果转化为空-频-极化辐射指纹。

### 4.1 特征

| 特征族 | 含义 |
|---|---|
| 空间方向图 | 主瓣方向、旁瓣结构、角域能量分布、方向图相关矩阵 |
| 频谱变化 | 多频点幅度斜率、频点间相关性、峰值漂移 |
| 极化信息 | 极化功率比、Etheta/Ephi 比例、三分量能量分布 |
| 等效源特征 | 源能量重心、稀疏源位置、源系数范数和空间分布 |
| 稳健统计 | 噪声扰动下的特征均值、方差、置信区间 |

### 4.2 当前分类链

当前 Level 2 已形成 `48/48` 样本导出、合并、识别和消融，主入口为：

```powershell
python code\run_cst_recognition.py
python code\run_cst_recognition_ablation.py
```

当前 `accuracy=1.000` 是工程闭环证据，不应被写成“复杂真实载体识别已经完全解决”。报告口径应说明：当前证明了空-频-极化特征在 CST-derived element-library 样本上的区分能力，后续需要 full-wave airframe scattering 和实测噪声验证泛化。

## 5. 协作分工建议

| 角色 | 主要任务 | GitHub 交付 |
|---|---|---|
| CST 建模同学 | 完善 Level 1/Level 2 工程、记录边界/端口/监视器、导出 CSV | `CST/`, `data/cst_exports/`, issue 运行记录 |
| 算法同学 | 重建、少测点优化、误差曲线、分类识别 | `code/`, `outputs/*summary.json`, `docs/reproduce_commands.md` |
| 文档同学 | 文献矩阵、方案报告、PPT、进度记录 | `docs/`, `文档/`, `submission/` |

## 6. 质量门槛

每次进入下一阶段前至少满足：

1. CSV 通过 `check_cst_export.py`。
2. 合并脚本没有缺样本/缺频点/缺字段。
3. 重建输出包含 NMSE、相关系数、主瓣/峰值误差。
4. 分类输出包含 accuracy、F1、混淆矩阵和消融结果。
5. `docs/stage_notes/` 记录新增产物。
6. GitHub 提交不包含 CST 缓存、final zip、`node_modules` 或可再生成大文件。

## 7. 参考资料

- DeepSeek 导师分享记录：`https://chat.deepseek.com/share/n42ew5j5gw8vx7unqd`
- Restricted Domain Compressive Sensing for Antenna Metrology: `https://arxiv.org/abs/2109.10040`
- Migliore, An Intuitive Approach to the Optimal Sampling of an Electromagnetic Field: `https://www.mdpi.com/1424-8220/25/24/7591`
- Bucci and Migliore, Degrees of Freedom and Sampling Representation of Electromagnetic Fields: `https://doi.org/10.1109/MAP.2024.3513216`
- Sarkar et al., Spherical Near-Field to Far-Field Transformation: `https://doi.org/10.1002/9781119076230.ch7`
- Non-redundant spherical near-field sampling for efficient incident power density assessment: `https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2025.1738329/full`
- RWTH Aachen spherical near-field measurements: `https://www.ihf.rwth-aachen.de/en/research/research-topics/antenna-measurement/spherical-near-field-measurements`
