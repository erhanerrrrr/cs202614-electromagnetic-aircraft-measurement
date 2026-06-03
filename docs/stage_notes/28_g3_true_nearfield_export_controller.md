# S28 G3 真近场导出控制器

## 做了什么

- 新增 `code/export_cst_true_nearfield_monitor.py`，把两份 required `full_grid_162` 真近场 CSV blocker 从人工说明推进为可执行控制器。
- 控制器读取 `required_full_grid_manifest.csv` 和 162 点 `true_nearfield_sensor_shell.csv`，输出每个 CST project、目标 CSV、验收命令和当前 blocker。
- 脚本支持 `--dry-run`、`--inspect-only`、`--run-solver` 三类入口：先生成任务计划，再通过 CST Python 检查结果树，最后才尝试求解和导出。
- 只有当 CST 结果能解析出完整 162 传感器 * Ex/Ey/Ez 三分量时，脚本才会写入 `data/cst_exports/level1_true_nearfield/*_true_nearfield.csv`。
- 根据 2026-06-03 的 CST History Error 反馈，`Field Monitors\nearfield_hemisphere_1200MHz` 是监视器定义节点，当前视图不支持 ASCII export；脚本已改为只对 `1D Results`、`2D/3D Results`、`Tables` 下的求解结果节点尝试导出。

## 为什么这样做

- G3 当前真正缺口不是报告材料，而是两份真实 CST true monitor/probe 全网格导出文件。
- 旧的 CST 工程已通过本机 CST API 生成，并插入 162 个 Cartesian E-field probes；本轮把这些工程、采样壳层和目标 CSV 合同连接成统一执行入口。
- 不用 FarfieldPlot-derived nearfield 去伪装 true nearfield。脚本会把 CST worker 的树项、raw export、解析状态和错误逐项记录，保留物理证据边界。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/export_cst_true_nearfield_monitor.py` | G3 required 真近场 monitor/probe 导出控制器 | `python code\export_cst_true_nearfield_monitor.py --dry-run` |
| `outputs/cst_true_nearfield_monitor_export/` | 控制器任务计划、summary、CST worker 日志和 raw export 位置 | 查看 `README.md` 和 `true_nearfield_export_task_plan.csv` |
| `data/cst_true_nearfield_workpack/operator_packet/README.md` | operator packet 增加自动化桥接命令 | 先 dry-run，再 inspect-only |
| `code/README.md` | 常用命令和真近场工作流说明接入新脚本 | 作为复现入口 |

## 验证方式

```powershell
python -m py_compile code\export_cst_true_nearfield_monitor.py
python code\export_cst_true_nearfield_monitor.py --dry-run
python code\export_cst_true_nearfield_monitor.py --inspect-only --timeout-seconds 300
python code\export_cst_true_nearfield_monitor.py --timeout-seconds 300
python code\check_true_nearfield_dropzone.py --required-only --full-grid-only
```

2026-06-03 复核结果：

- `--dry-run`：selected tasks 2，ready 2，blocked 0。
- `--inspect-only`：两个 `.cst` 工程均可被 CST Python 打开，树项各 205 个。
- 非 dry-run 安全返回 `no_solved_result_tree_items`；每个 case 都记录到 164 个 monitor/probe 定义候选，但 `exportable_result_count_after = 0`，未再触发 CST History Error。
- dropzone 仍为 `missing_file: 2`，说明 G3 物理证据尚未闭环。

## 当前不足

- 本轮没有声称 G3 已闭环；两份目标 true-nearfield CSV 仍需 CST worker 成功解析或人工 CST 导出。
- CST 不同版本的 monitor/probe ASCIIExport 结果格式可能不同，脚本当前会先保存树项和 raw export 尝试，再决定是否能写合同 CSV。
- 如果 CST project 尚未求解，`--inspect-only` 只能证明工程和结果树状态，不能产生最终场值。
- 若非 dry-run 返回 `no_solved_result_tree_items`，含义是工程中已有 monitor/probe 定义，但尚未在结果树中看到可导出的真近场求解结果；这比直接触发 CST 弹窗更利于自动化判断。

## 下一步

1. 运行 dry-run，确认两份 required 任务、项目路径和 162 点壳层均 ready。
2. 运行 inspect-only，记录 CST 结果树里 true-nearfield/probe 相关项。
3. 若结果树已含可解析场值，执行非 dry-run 导出并进入 dropzone/gate；若尚未求解，使用 `--run-solver` 或 CST GUI 求解后重复导出。
