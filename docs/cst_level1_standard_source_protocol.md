# G2：CST Level 1 标准源闭环操作规程

版本：v0.1  
目标：先用 CST 标准源数据跑通“CST 近场导出 - Python 等效源重建 - CST 远场真值对比”的闭环，再进入多源和简化航空载体。

## 1. 为什么先做标准源

标准源阶段的目的不是追求复杂，而是把坐标系、单位、相位、导出字段、远场真值和 Python 重建流程校准清楚。若直接从简化飞机模型开始，误差来源会混在一起：模型散射、网格精度、近场采样、坐标约定、相位导出和反演病态都可能影响结果，后续很难定位。

标准源闭环通过后，才能把 CST 作为可信数据源接入现有 baseline。

## 2. Level 1 推荐模型

优先顺序如下：

| 顺序 | 模型 | 用途 | 通过标准 |
|---|---|---|---|
| 1 | 短偶极子 | 有解析方向图直觉，便于 sanity check | 方向图主瓣/零点位置正确 |
| 2 | 半波振子 | 更接近实际窄带天线 | CST 远场与 Python 重建高度相关 |
| 3 | 小环天线或贴片天线 | 验证不同极化/结构类型 | 重建指标稳定 |

初期只需要一个频点，例如 `1.2 GHz`。多频点可在闭环稳定后扩展。

## 3. 统一坐标与空间包络

坐标系建议固定为：

- x 轴：机身纵向，后续简化航空载体长度方向。
- y 轴：横向。
- z 轴：高度方向。
- 原点：被测对象几何中心或地面投影中心。标准源阶段可放在 `(0, 0, 4 m)` 或等效源包络中心。

赛题空间包络：

```text
x in [-6, 6] m
y in [-5, 5] m
z in [0, 8] m
```

半球面测点：

- 半径：`13 m`
- theta：`5 deg` 到 `85 deg`
- phi：`0 deg` 到 `360 deg`
- 初始空间点：`9 x 18 = 162`
- 极化：theta/phi 双极化，或导出 Ex/Ey/Ez 后在 Python 中投影。

半球半径 13 m 覆盖 12 m x 10 m x 8 m 包络并留有余量。

## 4. CST 建模步骤

### 4.1 新建工程

建议工程命名：

```text
CST_L1_short_dipole_1p2GHz.cst
CST_L1_halfwave_dipole_1p2GHz.cst
```

单位建议：

- Geometry: m 或 mm 均可，但导出 CSV 必须统一为 m。
- Frequency: GHz。
- Time/Frequency domain solver 均可，建议初期用频域或时域后处理均能稳定导出幅相的设置。

### 4.2 辐射源设置

短偶极子：

- 中心位置：建议 `(0, 0, 4 m)`。
- 方向：先沿 z 轴，再可做 x/y 方向对照。
- 频点：`1.2 GHz`。
- 边界：Open/Add Space 或 PML。

半波振子：

- 长度约 `lambda/2`，`lambda = c / f`。
- `1.2 GHz` 下自由空间波长约 `0.2498 m`，半波振子总长约 `0.125 m`，可按 CST 天线建模经验微调。

### 4.3 场监视器设置

必须导出：

1. 近场复数数据：测点处 Ex/Ey/Ez，包含实部和虚部，或幅值和相位。
2. 远场真值：同频点的 Etheta/Ephi 或增益/方向图。

建议：

- 使用离散测点导出时，测点坐标使用 `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`。
- 若 CST 只能先导出网格面数据，则需要后处理插值到上述测点坐标，插值过程必须记录。

## 5. 导出字段规范

近场 CSV 必须至少包含：

| 字段 | 示例 | 说明 |
|---|---|---|
| sample_id | `L1_short_dipole_z_1p2G` | 样本编号 |
| sensor_id | `0` | 与测点布局表一致 |
| x_m, y_m, z_m | `1.23` | 测点坐标，单位 m |
| frequency_hz | `1200000000` | 频率，单位 Hz |
| polarization | `Ex` / `Ey` / `Ez` 或 `theta` / `phi` | 场分量或探头极化 |
| e_real | `...` | 电场实部 |
| e_imag | `...` | 电场虚部 |
| source_config | `short_dipole_z` | 源配置 |
| carrier_model | `standard_source` | 模型类别 |
| working_state | `single_source_on` | 状态标签 |

远场 CSV 必须至少包含：

| 字段 | 示例 | 说明 |
|---|---|---|
| sample_id | `L1_short_dipole_z_1p2G` | 必须与近场对应 |
| theta_deg | `45` | 远场角度 |
| phi_deg | `90` | 远场角度 |
| frequency_hz | `1200000000` | 频率 |
| e_theta_real, e_theta_imag | `...` | Etheta 复数值 |
| e_phi_real, e_phi_imag | `...` | Ephi 复数值 |
| gain_db | `...` | 若有，可保留 |

## 6. Python 校验入口

生成模板：

```powershell
python code\prepare_cst_templates.py
```

校验近场导出：

```powershell
python code\check_cst_export.py --nearfield path\to\nearfield.csv
```

同时校验近场和远场：

```powershell
python code\check_cst_export.py --nearfield path\to\nearfield.csv --farfield path\to\farfield.csv
```

校验通过后，再进入重建接入。

## 7. Level 1 通过判据

### 7.1 数据完整性

- 近场数据包含完整 `sensor_id`。
- 每个测点至少有两个正交极化，推荐 Ex/Ey/Ez 三分量。
- `sample_id`、`frequency_hz`、坐标单位一致。
- 远场真值与近场数据同频点、同样本编号。

### 7.2 重建精度

初期目标：

- 全测点方向图相关系数 >= 0.95。
- 主瓣方向误差 <= 5 deg。
- NMSE 尽量低于 `1e-2`，标准源阶段应更好。

### 7.3 可解释性

报告中必须能说明：

1. CST 远场只作为参考真值，不作为最终算法替代品。
2. Python 由近场数据反演等效源，再外推远场。
3. 误差指标来自 Python 重建结果与 CST 远场真值对比。

## 8. 常见问题与处理

| 问题 | 表现 | 处理 |
|---|---|---|
| 相位单位混乱 | 重建方向图相关性低 | 确认相位是 deg 还是 rad，尽量导出实部/虚部 |
| 坐标单位混乱 | 主瓣方向明显错误 | 确认 CST 导出是否为 mm，统一转换到 m |
| 极化定义不一致 | Etheta/Ephi 对比异常 | 优先导出 Ex/Ey/Ez，在 Python 中统一投影 |
| 测点顺序错乱 | sensor_id 对不上 | 以 sensor_id 合并，不依赖 CSV 行顺序 |
| 近场面太近 | 重建病态或强反应近场影响大 | 标准源阶段先用 13 m 半球面验证，再逐步缩小 |

## 9. 队内分工触发

当需要真实 CST 操作时，可进入第一次三人并行：

- CST 主责：完成短偶极子和半波振子工程，导出 nearfield/farfield CSV。
- 算法主责：用 `check_cst_export.py` 校验并接入重建。
- 数据/报告主责：记录 CST 参数、截图、文件命名和文献依据。

在标准源闭环通过之前，不建议推进复杂飞机模型。
