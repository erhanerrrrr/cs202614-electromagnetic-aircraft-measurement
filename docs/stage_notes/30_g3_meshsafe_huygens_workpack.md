# S30 G3 mesh-safe Huygens CST workpack

## 做了什么

- 新增 `code/prepare_cst_meshsafe_huygens_workpack.py`，把 G3 required 的 CST 路线从 13 m Cartesian probe 直接求解改为局部 Huygens 面观测求解。
- 生成 `data/cst_meshsafe_huygens_workpack/`：包含 2 个 Level 1 required case、96 个 `level1_local_sphere_r0p35` 局部 E-field probe、导出契约和下一步命令清单。
- 用 `run_cst_level1_required_automation.py` 生成 mesh-safe CST 工程，并用短 ASCII 路径 `C:\csttmp\huy_p` / `C:\csttmp\huy_s` 运行工程生成和第一条 solver gate。
- 升级 `code/run_cst_solver_project.py`：除 result-tree 外，额外解析 CST `Result` 日志、`simulation_overview.json`、`output.json`、`.m3d/.ffm/.fme` 结果文件、路径长度错误和 `aborted_keeping_results` 状态。

## 为什么这样做

S29 已经证明 CST 本身可以启动，Python API 可以打开工程并调用 `StartSolver`。真正阻塞的是旧 13 m 真近场探针方案会把全波网格膨胀到约 `4.6` billion cells，并要求至少 `3` 个 MPI cluster nodes，本机无法完成。

因此本阶段把物理边界拆开：CST 只负责近源局部 Huygens 面或近边界场数据，Python 再把该局部证据外推到 13 m 测量壳，随后进入采样方案、外推反演和分类评估。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/prepare_cst_meshsafe_huygens_workpack.py` | 生成 mesh-safe Huygens 工作包、导出契约和下一步命令 | 在项目根目录运行 |
| `data/cst_meshsafe_huygens_workpack/README.md` | 本工作包的人类可读说明 | 给 CST/算法队友交接 |
| `data/cst_meshsafe_huygens_workpack/level1_required_meshsafe_huygens_cases.csv` | 2 个 required Level 1 case 的 mesh-safe 求解任务 | 输入给 CST 工程生成脚本 |
| `data/cst_meshsafe_huygens_workpack/level1_local_huygens_probe_points.csv` | 96 个局部 Huygens probe 点 | 作为 `--probe-csv` 输入 |
| `data/cst_meshsafe_huygens_workpack/local_huygens_export_contract.csv` | 后续 local `.m3d`/probe export adapter 需要写出的列契约 | 算法侧验收字段 |
| `data/cst_meshsafe_huygens_workpack/next_meshsafe_huygens_commands.csv` | 当前下一步命令清单 | 从 workpack 到 CST gate 的执行入口 |
| `C:\csttmp\huy_p` | 短 ASCII 路径下的 mesh-safe CST 工程缓存 | 避免 CST 保存阶段受中文长路径/内部路径长度影响 |
| `outputs/cst_solver_trials/meshsafe_huygens_required_shortpath/` | 第一条短路径 solver gate 的本机诊断摘要 | 本机证据，不包含大型 CST 结果体 |

## 验证方式

```powershell
python -m py_compile code\prepare_cst_meshsafe_huygens_workpack.py code\run_cst_solver_project.py code\run_cst_level1_required_automation.py
python code\prepare_cst_meshsafe_huygens_workpack.py
python code\run_cst_level1_required_automation.py --level1-csv data\cst_meshsafe_huygens_workpack\level1_required_meshsafe_huygens_cases.csv --probe-csv data\cst_meshsafe_huygens_workpack\level1_local_huygens_probe_points.csv --out-dir C:\csttmp\huy_p --probe-mode efield
python code\run_cst_solver_project.py --project C:\csttmp\huy_p\projects\CST_L1_short_dipole_z_1p2G_meshsafe_huygens_r0p35.cst --out-dir C:\csttmp\huy_s --trial-name h_short.cst --summary-out outputs\cst_solver_trials\meshsafe_huygens_required_shortpath\h_short_solver_summary.json --stdout-log outputs\cst_solver_trials\meshsafe_huygens_required_shortpath\h_short_stdout.log --timeout-seconds 600 --poll-seconds 20
```

短路径 solver gate 的当前观察：

- `C:\csttmp\huy_p` 工程生成返回 `stage_status = project_generation_complete`，2/2 `.cst` 工程保存成功，两个 case manifest 状态均为 `project_saved`。
- `mesh_limit_detected = false`
- `path_length_limit_detected = false`
- CST 使用 `HF Time Domain (Hex)`，运行约 `603` 秒。
- 600 秒 gate 结束为 `aborted_keeping_results`，CST 保留了 1 个局部 nearfield `.m3d` 文件和 1 对 farfield `.ffm/.fme` 文件。

## 当前不足

- 600 秒 gate 证明了“能跑且不再触发 4.6B mesh 限制”，但还不是干净完成的生产级求解。
- 中文长路径下重新生成工程时可能在 CST API 保存/关闭阶段出现 `RuntimeError()`，即使 `.cst` 文件已写出；后续自动化命令已改为短 ASCII 路径规避。
- 已有 `.m3d/.ffm/.fme` 结果文件，下一步需要写 local result export adapter，把局部 E-field 数据转成 `local_huygens_export_contract.csv` 的长表。
- Huygens 外推矩阵和 13 m 壳对比仍需用真实局部 CST 结果闭环，不能直接宣称最终 reduced-sampling proof。

## 下一步

1. 写 local `.m3d`/probe result export adapter，优先读取短路径 gate 已保留的 nearfield artifact。
2. 若 `.m3d` 解析不稳定，则调整 CST solver/monitor 导出设置，争取一次 clean completion 或显式 table export。
3. 把局部 Huygens 导出接入 `run_cst_huygens_baseline.py` 或新的 Huygens extrapolation runner，外推到 13 m 壳并与 FarfieldPlot-derived reference 对比。
4. 用完成后的真实局部场链路更新 G3 dashboard、workflow 和报告证据边界。

## 2026-06-03 后续更新

S31 已完成第 1 步和第一轮第 3 步诊断：`export_cst_meshsafe_huygens_results.py --attempt-export --overwrite` 已通过 CST ResultTree 读取 1D E-field probe 曲线，生成 `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv`，并由 `run_cst_meshsafe_huygens_extrapolation.py` 接入 Python 外推诊断。当前不再卡在 `.m3d` 是否存在或 ASCII export 弹窗，而是进入 Huygens 算子/约定校准与第二源案例复验阶段。
