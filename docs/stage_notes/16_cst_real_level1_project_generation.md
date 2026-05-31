# S16 CST Level 1 真实工程自动生成说明

## 做了什么

本阶段通过本机 CST Studio Suite 2025 的 Python API，自动生成了两个 Level 1 required 标准源 `.cst` 工程：

- `L1_short_dipole_z_1p2G`
- `L1_halfwave_dipole_z_1p2G`

每个工程均写入了单位、开放边界、背景空间、两段 PEC 圆柱偶极子、离散馈电端口、1.2 GHz E-field monitor、1.2 GHz farfield monitor，以及 162 个半球面近场探针。

## 为什么这样做

原先 G2 的最短阻塞点是“真实 CST 工程和导出尚未落地”。只写 runbook 仍然需要人工逐项建模，容易产生几何、馈电、探针数量或命名不一致。改为 CST API 自动生成工程后，可以把 Level 1 required 的建模步骤固化为可复现脚本，后续只需集中处理求解、导出和审计。

## 产物

| 文件/目录 | 意义 |
|---|---|
| `code/run_cst_level1_required_automation.py` | 控制器 + CST worker 脚本；普通 Python 负责准备输入，CST 自带 Python 负责调用 `cst.interface` 写工程。 |
| `outputs/cst_real_level1_projects/projects/*.cst` | 真实 CST API 生成的两个 Level 1 required 工程。 |
| `outputs/cst_real_level1_projects/vba_history/*.bas` | 注入 CST 的 VBA history 片段，便于复查几何、端口、monitor 和探针。 |
| `outputs/cst_real_level1_projects/cst_level1_project_manifest.csv` | 每个工程的路径、探针数、history block 数、导出合同和状态。 |
| `outputs/cst_real_level1_projects/cst_automation_summary.json` | 本次自动化运行摘要，记录 CST Python 路径、工程数量和下一阻塞门。 |
| `outputs/cst_real_level1_projects/cst_automation_stdout.txt` | CST worker 原始日志。 |
| `outputs/cst_real_level1_projects/input_snapshots/*.csv` | 本次生成使用的 Level 1 清单、探针点和远场网格快照。 |

## 如何验证

已执行：

```powershell
python -m py_compile src\run_cst_level1_required_automation.py
python code\run_cst_level1_required_automation.py
```

关键结果：

- `projects_created = 2`
- `probe_count = 162`
- `all_projects_created = true`
- `stage_status = project_generation_complete`

## 当前边界

本阶段证明“真实 CST 工程已经由本机 CST API 生成”，但尚不证明最终数值指标。G2 仍需完成：

1. 打开或批处理运行两个 `.cst` 工程。
2. 导出 `data/cst_exports/level1/*_nearfield.csv` 和 `*_farfield.csv`。
3. 运行 `python code\merge_cst_level1_exports.py --strict`。
4. 运行 `python code\run_cst_level1_batch_reconstruction.py --require-cases`。

## 下一步

优先尝试对 `outputs/cst_real_level1_projects/projects/CST_L1_short_dipole_z_1p2G.cst` 进行求解和导出；若 solver 时间或许可证受限，先保存 CST 截图和错误日志，再调整 mesh/solver 设置。
