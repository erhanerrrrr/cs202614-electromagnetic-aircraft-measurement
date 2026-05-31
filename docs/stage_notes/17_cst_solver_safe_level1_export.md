# S17 CST solver-safe Level 1 export

## 做了什么

本阶段把 Level 1 两个 required 标准源从“已生成 CST 工程”推进到“真实 CST 求解、导出、校验、合并、批量重建均可复现”。

完成事项：

1. 复核 CST/MCP 接入方式：`computer-use-windows` 可用于桌面确认和必要的 GUI 操作，批量建模/求解/导出则使用 CST Studio Suite 2025 自带 Python API。
2. 诊断原始 13 m Cartesian `efield` probes 方案的风险：短偶极子试算触发约 46 亿网格单元，CST 要求 MPI 集群，不能作为本机可执行路线。
3. 使用 `efarfield` 半球角度采样生成 solver-safe CST 工程，避免把 13 m 测点纳入三维网格。
4. 新增单工程求解脚本 `code/run_cst_solver_project.py`，并用它求解半波偶极子 required case。
5. 新增导出脚本 `code/export_cst_farfield_results.py`，通过 CST `FarfieldPlot` 线性 E-field 列表接口导出半球测点和远场网格。
6. 生成两个 required case 的真实 CST CSV：
   - `L1_short_dipole_z_1p2G`
   - `L1_halfwave_dipole_z_1p2G`
7. 运行 `check_cst_export.py`、`merge_cst_level1_exports.py --strict`、`run_cst_level1_batch_reconstruction.py --priority required --require-cases --stop-on-error`。

## 为什么这样做

直接在 13 m 半球面放置 Cartesian E-field probes 会让 CST 计算域扩展到测量半径，网格量级失控。本赛题当前选择的是半球面 2π 测量面，且 Level 1 标准源工作在 1.2 GHz，13 m 对短偶极子/半波偶极子已处于远场距离。因此本阶段采用“CST 真实 farfield 求解 + 在 13 m 半球方向上取线性 E-field + 转换为 Ex/Ey/Ez nearfield 合同格式”的 solver-safe 路线。

这条路线的好处是：

- 保留半球面角度采样和 162 个测点合同；
- 避免 13 m 探针扩域导致本机无法求解；
- 得到真实 CST 求解结果，而不是 synthetic/demo 数据；
- 输出仍能进入现有 nearfield/farfield 校验、合并和重建管线。

需要注意：当前 `nearfield.csv` 是 farfield-derived equivalent field，不是 CST 在 13 m 物理探针处的 full-wave near-field monitor 直接导出。对 Level 1 标准源这是合理的工程近似；对后续复杂航空载体 Level 2，需要继续根据载体尺寸和测量距离判断是否必须使用近场监视器、near-to-far 或更细的场采样策略。

## 产物有哪些

### 新增脚本

| 文件 | 意义 |
|---|---|
| `code/run_cst_solver_project.py` | 打开一个 `.cst` 工程，运行 solver，轮询完成状态，写出求解 summary/stdout。后续 Level 2 pilot 也可复用。 |
| `code/export_cst_farfield_results.py` | 打开已求解 `.cst`，用 CST `FarfieldPlot` 线性 E-field 列表接口导出半球测点和远场网格 CSV。 |

### 真实 CST 求解工程和日志

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_solver_ready_level1_projects/` | 使用 `efarfield` probe mode 生成的 solver-safe Level 1 required 工程。 |
| `outputs/cst_solver_trials/short_solver_safe/` | 短偶极子 solver-safe 试算工程、日志和 summary。 |
| `outputs/cst_solver_trials/halfwave_solver_safe/` | 半波偶极子 solver-safe 试算工程、日志和 summary。 |
| `outputs/cst_solver_trials/short_probe/` | 原始 Cartesian `efield` probe 失败证据，记录 46 亿网格单元风险。 |

### 真实 CST 导出数据

| 文件 | 行数 | 意义 |
|---|---:|---|
| `data/cst_exports/level1/L1_short_dipole_z_1p2G_nearfield.csv` | 486 | 162 个半球测点 × Ex/Ey/Ez。 |
| `data/cst_exports/level1/L1_short_dipole_z_1p2G_farfield.csv` | 2664 | 37 × 72 半球远场网格，含 Etheta/Ephi 实虚部和 power。 |
| `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_nearfield.csv` | 486 | 半波偶极子 162 个半球测点 × Ex/Ey/Ez。 |
| `data/cst_exports/level1/L1_halfwave_dipole_z_1p2G_farfield.csv` | 2664 | 半波偶极子远场网格。 |
| `data/cst_exports/level1/all_nearfield.csv` | 972 | 两个 required case 合并 nearfield。 |
| `data/cst_exports/level1/all_farfield.csv` | 5328 | 两个 required case 合并 farfield。 |

### 审计和指标

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_farfield_export/` | 每个 case 的导出 summary、CST stdout 和校验 JSON。 |
| `outputs/cst_level1_merge_report/level1_merge_summary.json` | `required_complete=true`，说明 Level 1 required 导出已通过严格合并审计。 |
| `outputs/cst_level1_reconstruction_batch/` | 两个 required case 的批量重建汇总，`completed_runs=2`、`failed_runs=0`。 |
| `outputs/cst_reconstruction/L1_short_dipole_z_1p2G/` | 短偶极子重建结果、指标和方向图对比图。 |
| `outputs/cst_reconstruction/L1_halfwave_dipole_z_1p2G/` | 半波偶极子重建结果、指标和方向图对比图。 |
| `outputs/cst_reconstruction_sweep/L1_short_dipole_z_1p2G/sweep_summary.csv` | 真实短偶极子重建的网格/正则化小扫描，说明 demo 参数迁移后仍需算法标定。 |

## 如何验证

已运行并通过：

```powershell
python code\check_cst_export.py --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv
python code\check_cst_export.py --nearfield data\cst_exports\level1\L1_halfwave_dipole_z_1p2G_nearfield.csv --farfield data\cst_exports\level1\L1_halfwave_dipole_z_1p2G_farfield.csv
python code\merge_cst_level1_exports.py --strict
python code\run_cst_level1_batch_reconstruction.py --priority required --require-cases --stop-on-error
python -m compileall src
```

关键结果：

- `merge_cst_level1_exports.py --strict`：`complete cases=2`，`required complete=True`。
- 合并数据：nearfield 972 行，farfield 5328 行。
- 批量重建：queued 2，completed 2，failed 0。
- 当前真实 CST 重建指标仍一般：短偶极子 NMSE 约 0.609，半波偶极子 NMSE 约 0.596。这说明真实数据链路已打通，但最终方案仍需要改进重建模型或加入标准源专用校准。

## 文件夹整理说明

本阶段没有大规模移动既有文件，原因是现有脚本、manifest 和 submission draft 已经依赖稳定路径。整理方式采用“新增目录归档 + 索引说明”：

- 真实 `.cst` 工程生成证据仍在 `outputs/cst_real_level1_projects/`。
- solver-safe 工程在 `outputs/cst_solver_ready_level1_projects/`。
- 求解试验和失败证据在 `outputs/cst_solver_trials/`。
- 可进入算法管线的真实 CSV 统一放在 `data/cst_exports/level1/`。
- 导出日志和校验 JSON 放在 `outputs/cst_farfield_export/`。
- 阶段说明统一追加到 `docs/stage_notes/`。

## 下一步

当前 completion audit 的下一阻塞门槛已从 G2 推进到 G3：Level 2 多源多状态真实 CST 数据。

建议三人分工：

| 角色 | 当前主责 | 技术细节 |
|---|---|---|
| A：算法/重建 | 改进真实 CST 重建指标 | 针对 farfield-derived Level 1 数据，增加标准源校准、相位中心处理、源区域约束或 farfield-domain 反演；复查 `em_core.py` 的等效源模型与 CST farfield phase convention。 |
| B：CST 仿真 | 推进 Level 2 pilot | 复用 `code/run_cst_solver_project.py` 和 `code/export_cst_farfield_results.py`，先做 2 到 4 个多源 pilot，补齐截图和求解日志。 |
| C：报告/材料 | 更新方案报告和答辩证据 | 把本阶段的 solver-safe 策略、失败网格证据、required strict 通过结果写入报告，明确 Level 1 已有真实 CST evidence，Level 2 仍是下一阶段。 |
