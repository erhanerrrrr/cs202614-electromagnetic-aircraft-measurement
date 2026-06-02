# 非冗余半球采样方案设计

版本：v1.0  
日期：2026-06-02  
对应未来工作方案：G2 采样方案升级

## 1. 目标

本阶段的目标不是简单把 162 个半球测点删少，而是把“少测点”变成可复现、可验证、可交给 CST 同学执行的采样方案。采样方案需要同时回答三个问题：

1. 哪些测点被保留，坐标和极化通道是什么；
2. 为什么这些点比随机删点更合理；
3. 在远场重建和分类识别任务上，当前证据支持把它作为哪一级方案。

因此本轮新增了脚本：

```powershell
python code\optimize_sampling_layout.py
```

脚本输出目录：

```text
data/sampling_layouts/
```

## 2. 当前生成的候选方案

基础布局仍为 `R = 13 m`、上半球 `2pi`、`9 x 18 = 162` 个空间测点，每个测点保留 `theta/phi` 双极化通道。脚本在这个基础网格上生成：

| 点数 | 候选方法 |
|---:|---|
| 162 | full_grid，全量校准基准 |
| 120 | geometric_farthest、fibonacci_snap、dictionary_weighted、task_driven |
| 81 | geometric_farthest、fibonacci_snap、dictionary_weighted、task_driven |
| 48 | geometric_farthest、fibonacci_snap、dictionary_weighted、task_driven |
| 32 | geometric_farthest、fibonacci_snap、dictionary_weighted、task_driven |

四类少测点候选的含义如下：

| 方法 | 含义 | 适用判断 |
|---|---|---|
| `geometric_farthest` | 在半球面上做贪心最远点覆盖 | 几何均匀、简单稳健，适合作为工程基准 |
| `fibonacci_snap` | 先生成 Fibonacci 低差异半球方向，再吸附到 CST 网格 | 对应文献中的低冗余、近均匀采样思想 |
| `dictionary_weighted` | 用等效源测量矩阵的行能量加权选点 | 优先保留对反演字典贡献更大的测点 |
| `task_driven` | 用分类模板的空-频-极化特征差异加权选点 | 面向识别任务，允许与远场最优采样不同 |

## 3. 已生成文件

| 文件 | 用途 |
|---|---|
| `data/sampling_layouts/hemisphere_sampling_candidates.csv` | 每个候选方案的逐测点表，包含 `sensor_id`、坐标、角度、半径和双极化通道 |
| `data/sampling_layouts/sampling_layout_summary.csv` | 每个候选方案的几何、矩阵、重建和分类代理指标 |
| `data/sampling_layouts/sampling_layout_summary.json` | 机器可读版本，便于后续 dashboard 或批处理脚本读取 |
| `data/sampling_layouts/README.md` | 数据目录说明和当前候选摘要 |

这些文件体量很小，适合进入 GitHub；真实 CST 大型工程文件和求解缓存仍不建议直接进入普通 Git。

## 4. 当前代理验证结果

当前验证使用合成等效源代理模型，频点为 `1.2 GHz`，反演为 Tikhonov baseline。分类指标使用近邻质心代理分类器，目的是快速比较候选采样对“空-频-极化指纹”的保留能力。它是进入 CST 验证前的筛选证据，不等同于最终 CST 结论。

关键结果如下：

| 方案 | Corr | NMSE | 分类 accuracy | 当前定位 |
|---|---:|---:|---:|---|
| full_grid_162 | 0.9992 | 3.65e-4 | 1.000 | 全量校准基准 |
| geometric_farthest_120 | 0.9984 | 9.29e-4 | 1.000 | 推荐作为下一轮主少测点 CST 方案 |
| fibonacci_snap_120 | 0.9979 | 9.32e-4 | 1.000 | 推荐作为 120 点低差异对照 |
| dictionary_weighted_120 | 0.9978 | 1.14e-3 | 1.000 | 推荐作为反演字典加权对照 |
| dictionary_weighted_81 | 0.9150 | 7.13e-2 | 1.000 | 激进压缩候选，需改进反演后再争取主方案 |
| dictionary_weighted_48 | 0.4261 | 3.32e-1 | 1.000 | 分类优先探索，不宜直接宣称高保真远场重建 |
| dictionary_weighted_32 | 0.3538 | 4.08e-1 | 1.000 | 极限压缩探索，用于识别任务和主动采样研究 |

当前结论比较清楚：

1. `120` 点方案已经接近全量 162 点的远场重建质量，应作为下一轮 CST 验证主线。
2. `81` 点方案保留了进一步压缩的希望，但当前 Tikhonov baseline 下相关系数还不足以作为高保真主方案。
3. `48/32` 点虽然分类代理指标高，但远场重建误差明显，现阶段只能写成“识别优先/压缩探索”，不能写成完整远场重建已经达标。

## 5. 建议的 CST 验证队列

下一轮不要一次性把所有候选都放进 CST，而应按证据强弱分层推进：

| 优先级 | 方案 | 目的 |
|---|---|---|
| P0 | full_grid_162 | 保留全量校准和坐标/相位/极化基准 |
| P1 | geometric_farthest_120 | 主工程少测点方案 |
| P1 | fibonacci_snap_120 | 低差异非冗余对照 |
| P1 | dictionary_weighted_120 | 等效源字典加权对照 |
| P2 | dictionary_weighted_81 | 激进少测点验证 |
| P3 | dictionary_weighted_48、task_driven_48 | 分类优先探索 |
| P3 | dictionary_weighted_32、task_driven_32 | 极限压缩探索 |

建议 CST 同学先按 `hemisphere_sampling_candidates.csv` 中的 `candidate` 字段筛选测点，保持 `sensor_id` 与当前 162 点网格一致。这样 Python 侧可以用同一套 CSV 字段和重建脚本做缺测/删点对照。

## 6. 判据更新

后续报告中建议把少测点判据写成三层，而不是只写“点数越少越好”：

| 判据 | 建议门槛 | 用途 |
|---|---:|---|
| 远场方向图相关系数 Corr | `>= 0.98` | 判断是否能作为远场重建主方案 |
| 归一化均方误差 NMSE | `<= 1e-2` | 约束方向图整体误差 |
| 分类 Accuracy/F1 | `>= 0.85` | 判断是否能作为识别优先方案 |
| 主瓣方向误差 | 越小越好，优先控制在几个角度以内 | 防止只看 Corr 而忽略峰值方向 |
| CST/合成一致性 | CST 真实数据复跑后仍成立 | 防止合成代理过拟合 |

按照这个判据，当前可写入阶段报告的表述是：

```text
基于等效源代理验证，120 点非冗余半球采样在当前 baseline 下已接近 162 点全量结果；
81 点以下属于进一步压缩探索，需要结合更强的稀疏/多频联合反演与真实 CST 数据复验。
```

## 7. 下一步工程动作

1. 在 CST 导出环节加入 `candidate` 采样方案字段，至少优先跑 `geometric_farthest_120`、`fibonacci_snap_120`、`dictionary_weighted_120`。
2. 在 Python 重建脚本中增加按 `sensor_id` 子集筛选真实 CST nearfield 的能力，把当前代理指标升级成真实 CST 指标。
3. 将 81/48/32 点方案与 L1、Group Lasso、多频联合反演绑定验证；如果反演模型升级后 Corr 明显提升，再考虑写入主方案。
4. 分类任务单独保留 `task_driven_48/32` 路线，重点验证缺测、噪声、相位扰动下的稳定性。
5. 每一轮 CST 结果都更新 `sampling_layout_summary.csv` 或新增真实 CST 对照表，避免报告里只有口头判断。
