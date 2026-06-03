# S29 G3 CST solver mesh-limit diagnosis

## 做了什么

- 修正 `code/run_cst_solver_project.py` 和 `code/run_cst_level1_required_automation.py` 的 worker 启动路径，使本仓库当前 `code/` 目录下的脚本能被 CST Python 正确回调。
- 对 `outputs/cst_real_level1_projects/projects/CST_L1_short_dipole_z_1p2G.cst` 建立只用于试求解的副本，并用本机 CST Python 调用 `StartSolver`。
- 增强 `code/run_cst_solver_project.py`：自动采集 CST `Result/Model.log`、`Result/output.txt`、`Result/outputDS.txt`、`hexmeshengine.log` 和 `ml_info.log`，解析网格规模、MPI 节点要求、编码告警和真实结果树子项。

## 为什么这样做

G3 true-nearfield 任务之前卡在“结果树没有可导出 ASCII 项”。单看导出控制器，无法判断是 CST 未启动、工程未求解、结果节点名不匹配，还是求解资源不足。本阶段直接启动一个受控试求解，用 CST 自己的日志确定失败原因。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/run_cst_solver_project.py` | 单工程 CST 试求解与诊断入口；现在能识别 `solver_mesh_limit` | 用于验证某个 `.cst` 工程是否能在本机完成求解 |
| `code/run_cst_level1_required_automation.py` | Level 1 required 工程生成/自动化脚本；worker 路径已匹配当前 `code/` 目录 | 后续生成 mesh-safe 工程时继续沿用 |
| `outputs/cst_solver_trials/required_true_nf_short/CST_L1_short_dipole_z_1p2G_solver_trial_solver_summary.json` | 本次 CST 试求解证据摘要 | 查看 `status`、`solver_logs.mesh_cell_count_billion`、`required_mpi_nodes` |
| `outputs/cst_solver_trials/required_true_nf_short/README.md` | 本次试求解的人类可读诊断说明 | 给导师/队友解释当前 CST 阻塞点 |

## 关键结论

CST 不是无法正常运行。当前证据显示：

- CST Python 可以启动。
- `.cst` 工程可以打开。
- `StartSolver` 返回成功。
- 求解约 17 秒后停止。
- CST 日志给出明确错误：当前仿真需要约 `4.6` billion mesh cells，并要求至少 `3` 个 MPI cluster nodes。
- 结果树中真实结果子项数量为 `0`，因此 `Field Monitors` 或 `Probes` 定义节点不能被当成可导出的求解结果。

这说明阻塞点是建模/采样方案造成的网格爆炸，不是 CST 安装、许可证或 Python 接口不可用。

## 当前不足

- 原始 13 m Cartesian probe/full-grid true-nearfield 路线把远距离测量壳直接放进全波求解域，导致本机资源不可承受。
- `outputDS.txt` 同时出现了 `Expecting local encoding but found utf8 multibyte`，说明中文绝对路径在 CST 内部日志/参数存储中仍可能触发编码告警；当前脚本已尽量用相对路径写摘要，但后续 CST 工程目录最好继续保持 ASCII trial 名称。
- 本阶段只对短偶极子 required case 做了受控试求解；半波偶极子 case 预计会遇到同类远距离探针网格问题，但仍应在 mesh-safe 改造后复核。

## 后续路线

1. 不再把 13 m 测量壳上的 162 个 Cartesian probe 作为 CST 全波网格内的直接求解对象。
2. 将 13 m 半球壳保留为 Python 侧算法评估/外推目标。
3. CST 侧改为 mesh-safe 物理观测：近源局部 Huygens 面、近边界场监视器、端口/远场结果或较小包围面上的切向场。
4. Python 侧用已有 `prepare_huygens_surface_prior.py` 和 `run_cst_huygens_baseline.py` 路线，把局部物理面数据外推到 13 m 测量壳，再进入采样方案、外推反演和分类评估。
5. 为 mesh-safe 工程生成新的 Level 1 required CST workpack，并用本阶段增强后的 `run_cst_solver_project.py` 先做求解可行性门控。

## 验证方式

```powershell
python -m py_compile code\run_cst_solver_project.py code\run_cst_level1_required_automation.py code\export_cst_true_nearfield_monitor.py

python code\run_cst_solver_project.py `
  --project outputs\cst_real_level1_projects\projects\CST_L1_short_dipole_z_1p2G.cst `
  --out-dir outputs\cst_solver_trials\required_true_nf_short `
  --trial-name CST_L1_short_dipole_z_1p2G_solver_trial.cst `
  --timeout-seconds 300 `
  --poll-seconds 10
```

预期试求解返回码仍为 `1`，但摘要应给出 `status = solver_mesh_limit`、`mesh_cell_count_billion = 4.6`、`required_mpi_nodes = 3`、`result_tree_count_after = 0`。
