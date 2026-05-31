# 小目标 2：CST 标准源数据接入与重建闭环

版本：v0.1  
目标：用真实 CST Level 1 标准源数据替换当前 demo 数据，得到可写入报告的第一组“CST 近场 - 自研重建 - CST 远场真值”结果。

## 1. 当前已具备的入口

已完成：

1. CST 测点与导出模板：`outputs/cst_templates`
2. 导出格式校验：`code/check_cst_export.py`
3. CST 数据重建脚本：`code/run_cst_reconstruction.py`
4. 合成 demo 验证结果：`outputs/cst_reconstruction_demo`

demo 数据不是 CST 证据，只证明 Python 接口和重建流程已准备好。

## 2. 真实 CST 数据接入步骤

### 步骤 1：生成模板

```powershell
python code\prepare_cst_templates.py
```

将 `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` 中的 162 个坐标作为 CST 近场采样点。

### 步骤 2：CST 建模

先做两个模型：

1. `CST_L1_short_dipole_1p2GHz.cst`
2. `CST_L1_halfwave_dipole_1p2GHz.cst`

推荐先固定频点 `1.2 GHz`，等闭环稳定后再扩展多频点。

### 步骤 3：导出近场和远场

近场文件建议命名：

```text
data/cst_exports/L1_short_dipole_z_1p2G_nearfield.csv
```

远场文件建议命名：

```text
data/cst_exports/L1_short_dipole_z_1p2G_farfield.csv
```

字段必须满足 `docs/cst_level1_standard_source_protocol.md`。

### 步骤 4：校验导出

```powershell
python code\check_cst_export.py `
  --nearfield data\cst_exports\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield data\cst_exports\L1_short_dipole_z_1p2G_farfield.csv `
  --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_validation.json
```

校验必须 `ok: True`。如果只有 warning 且 warning 是 Ex/Ey/Ez 可转换为 theta/phi，可以继续。

### 步骤 5：运行重建

```powershell
python code\run_cst_reconstruction.py `
  --nearfield data\cst_exports\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield data\cst_exports\L1_short_dipole_z_1p2G_farfield.csv `
  --sample-id L1_short_dipole_z_1p2G `
  --frequency-hz 1200000000 `
  --out-dir outputs\cst_reconstruction\L1_short_dipole_z_1p2G
```

输出：

| 文件 | 用途 |
|---|---|
| `cst_reconstruction_metrics.csv/json` | 重建指标，可进报告 |
| `cst_farfield_reconstruction_compare.png` | CST 真值、自研重建和误差图 |
| `equivalent_source_solution.csv` | 等效源系数，可用于解释和后续稀疏源分析 |

## 3. 通过判据

短偶极子/半波振子阶段建议达成：

- 全测点方向图相关系数 >= 0.95。
- 主瓣方向误差 <= 5 deg。
- NMSE <= `1e-2`。
- 能解释主要误差来源：坐标、极化、相位、网格、正则化。

如果无法达成，先不要进入复杂载体模型，应优先检查：

1. CST 导出坐标单位是否为 m。
2. 相位是否导出为实部/虚部，避免 deg/rad 混乱。
3. 远场角度定义是否与 Python 的 theta/phi 一致。
4. 标准源位置是否在等效源网格包络内。
5. 等效源网格是否过粗或正则化参数是否过大。

## 4. 队内分工建议

此阶段可以开始第一次真实分工：

| 角色 | 技术任务 | 交付物 |
|---|---|---|
| CST 主责 | 建模、监视器设置、近场/远场导出、截图 | `.cst` 工程、nearfield/farfield CSV、参数记录 |
| 算法主责 | 校验、重建、调参、指标输出 | metrics、compare 图、等效源 CSV |
| 数据/报告主责 | 文件命名、数据字典、记录误差与图表说明 | 实验记录表、报告段落草稿 |

## 5. 完成后进入小目标 3

标准源闭环通过后，进入多源/多频/多极化 CST 数据集构建：

1. 两到四个辐射源组合。
2. 三到五个频点。
3. 多种工作状态标签。
4. 接入识别模块，形成第一个 85% 以上识别结果。
