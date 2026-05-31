# S14 CST G2 真机操作包

## 做了什么

- 新增 `code/build_cst_operator_runbook.py`，把 G2 必做的两个 Level 1 标准源整理成 CST 操作者可直接执行的 runbook。
- 从当前半球面测点表生成 162 个 CST nearfield probe 点位。
- 从远场模板生成 2664 个 theta/phi 采样点。
- 生成真实导出字段合同、截图证据清单和导出后的验证/重建命令。
- 将该操作包接入总控 dashboard、提交草稿包、提交索引、复现命令和项目文件索引。

## 为什么这样做

- 当前最短阻塞门是 G2：真实 CST Level 1 required 标准源尚未导出。
- 仅有宏模板和任务卡还不够保险，CST 操作者还需要逐项确认探针点、远场采样、导出字段、截图和导出后命令。
- 操作包能减少坐标单位、文件命名、行数、字段名和截图留证上的人为误差。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_cst_operator_runbook.py` | CST 操作包生成脚本 | 每次 Level 1 action sheet 或测点表变化后运行 |
| `outputs/cst_operator_runbook/README_cst_operator_runbook.md` | G2 真机执行主说明 | 交给 CST 主责首先阅读 |
| `outputs/cst_operator_runbook/level1_required_operator_steps.csv` | 两个 required 标准源的建模与导出参数 | 在 CST 中逐行执行 |
| `outputs/cst_operator_runbook/cst_probe_points_hemisphere_162.csv` | 162 个半球面近场探针点 | 导入 CST 或手工创建 probe |
| `outputs/cst_operator_runbook/cst_farfield_sampling_grid.csv` | 2664 个远场 theta/phi 采样点 | 对齐 farfield 导出网格 |
| `outputs/cst_operator_runbook/cst_level1_required_export_contract.csv` | nearfield/farfield 字段、行数和路径合同 | 导出后逐项核对 |
| `outputs/cst_operator_runbook/cst_level1_required_screenshot_manifest.csv` | 每个 required 案例 6 张截图要求，共 12 张 | 用作提交证据清单 |
| `outputs/cst_operator_runbook/post_export_level1_validation_commands.ps1` | 导出后校验、重建、审计和刷新 dashboard 的命令 | 真实 CSV 到位后运行 |

## 验证方式

```powershell
python -m compileall src\build_cst_operator_runbook.py
python code\build_cst_operator_runbook.py
```

本阶段验证结果：

- required 案例数：2
- half-sphere probe 点数：162
- nearfield 每案例期望行数：486
- farfield 每案例期望行数：2664
- 截图证据清单：12 项
- `is_simulation_evidence=false`

## 当前不足

- 本阶段仍未产生真实 CST nearfield/farfield；它只是把真机执行和验收要求压实。
- `post_export_level1_validation_commands.ps1` 中的验证命令必须等真实 CSV 到位后再运行。
- CST 版本和具体导出菜单可能略有差异，操作者需要按本机 CST API/界面适配，但文件路径和字段合同不能随意改。

## 下一步

1. B_CST 按 `outputs/cst_operator_runbook/README_cst_operator_runbook.md` 执行两个 G2 required 标准源。
2. 将真实 CSV 放入 `data/cst_exports/level1/`，截图按 manifest 存入 `submission/05_cst/screenshots/level1/`。
3. A_algorithm 运行 `outputs/cst_operator_runbook/post_export_level1_validation_commands.ps1` 或其中的命令，关闭 G2。
