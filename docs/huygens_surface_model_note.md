# Huygens 面源先验模型说明

## 1. 目的

当前 G3 的核心瓶颈不是 CST/Python 数据链路，而是通用自由点源网格会把能量泄漏到非物理位置。已有证据显示：

| 证据 | 当前结论 |
|---|---|
| 中心源 sanity check | Level 1 已知中心源先验能给出高相关和零主瓣误差。 |
| 通用等效源网格 | full-grid 仍是 `diagnostic_only`，不能支撑少测点结论。 |
| group-sparse 网格 | Corr/NMSE 改善，但主瓣误差仍未过关。 |
| convention check | 未发现能修复通用网格的简单相位或极化约定错误。 |
| 球谐 NF-FF baseline | 角度、极化、远场比较链路可信，但不是结构化源模型。 |

因此下一步应把“源可以任意出现在体网格中”的假设，升级为“辐射可等效为封闭面上的切向电/磁流”。这就是 Huygens 面源先验的工程作用。

## 2. 模型口径

Huygens 面 `S` 包围真实辐射区域。面上未知量不是 3D 点偶极矩，而是每个离散面元上的切向等效电流和磁流：

```text
q_i = [J_t1, J_t2, M_t1, M_t2]
```

其中：

- `J_t1, J_t2` 是等效电表面电流在两个局部切向基上的复系数。
- `M_t1, M_t2` 是等效磁表面电流在两个局部切向基上的复系数。
- `t1, t2` 与外法向 `n` 构成局部正交基。
- 每个节点带 `weight_m2`，后续矩阵构造时应把面元面积纳入辐射权重或正则化权重。

测量向量仍沿用现有 CST 脚本格式：

```text
y = [Etheta(sensor_1..N), Ephi(sensor_1..N)]
```

未来 Huygens 反演矩阵写成：

```text
A_huygens(f, layout, S) q ~= y
```

其中 `A_huygens` 的每一列对应一个节点上的一个切向电流或磁流基函数，行对应传感器处的 `Etheta/Ephi` 复场。

## 3. 已新增几何工作包

运行：

```powershell
python code\prepare_huygens_surface_prior.py
```

输出目录：

```text
data/source_priors/huygens_surface/
```

关键文件：

| 文件 | 作用 |
|---|---|
| `huygens_surface_configs.csv` | 面源先验配置表。 |
| `level1_local_sphere_r0p35_nodes.csv` | 包围 Level 1 已知源中心 `(0, 0, 4 m)` 的局部球面 Huygens 先验。 |
| `airframe_box_coarse_nodes.csv` | 包围 `12 m x 10 m x 8 m` 载体包络的粗网格盒面先验。 |
| `airframe_box_medium_nodes.csv` | 后续 Level 2/Level 3 结构化重建用的中等密度盒面先验。 |
| `huygens_surface_prior_summary.json` | 节点数、未知量数和面积摘要。 |
| `README.md` | 队友接手说明。 |

当前这些文件只是几何和未知量合同，不是已经完成的 Huygens 重建结果。

## 4. 推荐实现路线

### Phase 0：固定先验几何

已完成。`prepare_huygens_surface_prior.py` 输出节点坐标、外法向、两个切向基、面积权重和四个复未知量名称。

### Phase 1：建立矩阵接口

新增函数建议放入 `code/em_core.py` 或单独文件 `code/huygens_core.py`：

```text
build_huygens_measurement_matrix(layout, surface_nodes, frequency_hz, sensor_indices=None)
```

输出矩阵维度：

```text
rows = 2 * sensor_count
cols = 4 * surface_node_count
```

这样它可以替换现有 `build_measurement_matrix()`，继续复用 `solve_tikhonov()`、`pattern_metrics()` 和候选采样布局循环。

### Phase 2：先做近似电/磁偶极面元，再升级完整算子

第一版可以把每个面元的 `J/M` 近似为带面积权重的等效电/磁偶极基函数，用来判断 Huygens 面是否比自由体网格更稳定。通过后再升级为更规范的等效电流/磁流 Green 算子。

这一步的目标不是一次写出完美电磁积分方程，而是建立可比较证据：

```text
center prior vs generic grid vs group-sparse grid vs spherical baseline vs Huygens surface
```

### Phase 3：统一输出模型比较表

建议新增输出目录：

```text
data/sampling_layouts/cst_level1_huygens_baseline/
```

建议输出：

| 文件 | 内容 |
|---|---|
| `huygens_reconstruction_results.csv` | 每个样本、频点、先验面、lambda、采样布局的指标。 |
| `huygens_reconstruction_by_model.csv` | 按模型汇总的 min Corr、max NMSE、max 主瓣误差。 |
| `huygens_surface_solution.csv` | 每个节点的 `J/M` 复系数和能量。 |
| `huygens_reconstruction_summary.json` | 最佳模型和验收状态。 |
| `README.md` | 结果口径和是否可用于少测点结论。 |

## 5. 正则化设计

Huygens 面源模型比自由点源更物理，但未知量数量可能更大，所以必须把正则化写清楚：

| 正则项 | 形式 | 作用 |
|---|---|---|
| Tikhonov 能量约束 | `lambda_l2 * ||W q||_2^2` | 避免过拟合和病态解。 |
| 面上平滑约束 | `lambda_smooth * ||L q||_2^2` | 抑制相邻面元电流剧烈跳变。 |
| 节点 group sparsity | `sum_i ||q_i||_2` | 允许少数区域主导辐射，避免全表面均匀泄漏。 |
| 多频共享支撑 | `sum_i sqrt(sum_f ||q_i(f)||_2^2)` | Level 2/多频时共享源位置，幅相随频率变化。 |
| 面权重归一化 | `W_i ~ sqrt(weight_m2)` | 避免不同面元面积导致系数尺度不一致。 |

第一版建议从 `Tikhonov + 面权重归一化` 开始，等 full-grid 稳定后再加平滑和 group sparsity。

## 6. 验收门槛

Huygens baseline 必须先在 full-grid 162 点上过关，再比较 120/81/48/32 点候选。

建议沿用当前 G3 指标：

| 指标 | 建议门槛 |
|---|---|
| `min_correlation` | `>= 0.95` |
| `max_nmse` | `<= 1e-2` 作为 strict target；`<= 3e-2` 可暂记为 near pass。 |
| `max_main_lobe_error_deg` | `<= 5 deg` |
| `nearfield_fit_relative_error` | 作为诊断项记录，不单独决定通过。 |
| `condition_number` | 记录并用于选择更稳定的先验面/正则化。 |
| `surface_energy_concentration` | 能量应集中在合理面区，不应无解释地散满整个包络面。 |

只有当 Huygens full-grid baseline 至少达到 `strict_pass` 或经过导师认可的 near pass，才应复跑少测点方案并写入报告结论。

## 7. 与 true near-field monitor 的关系

当前 Level 1 nearfield 表仍是 FarfieldPlot-derived angular sample，不是真正 full-wave near-field monitor。Huygens 面源更贴近近场等效原理，因此数据边界必须更谨慎：

1. 若 true monitor 与 FarfieldPlot-derived baseline 高度一致，可以继续使用当前 Level 1 表推进 Huygens 原型，并在报告中说明已通过 monitor gate。
2. 若两者主要差在幅度尺度，应先统一归一化，再跑 Huygens。
3. 若两者在相位、极化或主瓣方向上有明显差异，应以 true monitor 为权威输入，重新跑 G3 全链路。

## 8. 报告可用表述

可以写：

> 针对自由点源网格可能产生非物理能量泄漏的问题，方案引入 Huygens 面源先验，将辐射区域外场等效为包络面上的切向电/磁流，并通过 full-grid 近场样本先校准面源反演，再评估少测点布局。

暂时不要写：

> Huygens 面源模型已经证明 48 点或 32 点采样满足最终精度。

除非后续 `cst_level1_huygens_baseline/` 的 full-grid 和 reduced-layout 结果都已达到验收门槛。

## 9. 2026-06-02 runnable baseline update

The first matrix prototype is now implemented in:

```powershell
python code\run_cst_huygens_baseline.py
```

Generated result directory:

```text
data/sampling_layouts/cst_level1_huygens_baseline/
```

Current best setting on the Level 1 export is:

| Field | Value |
|---|---|
| Prior | `level1_local_sphere_r0p35` |
| Variant | `huygens_em_minus` |
| Candidate | `full_grid_162` |
| Lambda | `1e-2` |
| Status | `diagnostic_only` |
| Min Corr | `0.7781` |
| Max NMSE | `2.6423e-01` |
| Max main-lobe error / deg | `166.71` |
| Mean relative residual | `6.1942e-01` |

Interpretation: Phase 1 is complete as a software interface and smoke test, but
Phase 2 is not physically sufficient yet. The simplified electric/magnetic
dipole-sheet approximation does not recover the current CST Level 1 far-field
baseline well enough to support reduced-layout sampling claims.

Immediate follow-up:

1. Run the same baseline after true near-field monitor CSV data is available.
2. Upgrade the operator from the simplified dipole-sheet approximation toward a
   fuller electric/magnetic Huygens surface-current Green function.
3. Add surface smoothness or node-group regularization once the full-grid
   physical convention is stable.
