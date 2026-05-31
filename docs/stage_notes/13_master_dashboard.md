# S13 总控状态 dashboard

## 做了什么

- 新增 `code/build_master_dashboard.py`，把 completion audit、submission index、CST execution dashboard、scorecard、报告素材包和 PPT/视频素材包汇总到一个总控视图。
- 生成三类表格：gate 状态表、下一步任务队列、关键文件入口表。
- 把总控 dashboard 接入提交草稿包和提交索引，后续打包时能自动复制到 `submission/06_data/metrics/master_dashboard` 和 `submission/07_appendix/master_status_dashboard.md`。

## 为什么这样做

- 当前项目已经有多个审计和执行文件，单独看每个文件容易漏掉“最短阻塞门”。
- 赛题周期较长且队内有三人，需要把 CST、算法、报告展示三条线拆成可交接任务。
- 总控 dashboard 只做项目管理和证据追踪，不把 synthetic/demo 结果当作真实仿真证据，避免提前误判完成。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_master_dashboard.py` | 总控 dashboard 生成脚本 | 每次 CST 证据或审计状态变化后运行 |
| `outputs/master_dashboard/master_status_dashboard.md` | 一页式状态、gate、三人分工和下一步命令 | 优先阅读入口 |
| `outputs/master_dashboard/master_next_actions.csv` | 队内下一步任务队列 | 按 priority 和 owner_role 分工执行 |
| `outputs/master_dashboard/master_gate_summary.csv` | G0-G6 gate 状态与责任人 | 判断当前卡在哪个门 |
| `outputs/master_dashboard/master_key_artifacts.csv` | 关键文件入口表 | 快速定位 scorecard、completion audit、CST dashboard 等 |
| `outputs/master_dashboard/master_dashboard_summary.json` | 机器可读摘要 | 供后续自动审计或打包引用 |

## 验证方式

```powershell
python -m compileall src\build_master_dashboard.py
python code\build_master_dashboard.py
```

本阶段验证结果：

- `completion_proven=false`
- `next_blocking_gate=G2`
- `action_count=6`
- `missing_required_now_files=4`
- `missing_level2_pilot_files=8`

## 当前不足

- dashboard 不能替代真实 CST 文件；当前 G2 required 标准源 nearfield/farfield 仍缺 4 个文件。
- Level 2 pilot 和 48 个全量样本仍未导出。
- 报告、PPT、视频仍只是成稿素材和 storyboard，不是最终提交文件。

## 下一步

1. B_CST 按 `outputs/cst_execution_dashboard/level1_required_action_sheet.csv` 完成两个 Level 1 required 标准源导出。
2. A_algorithm 运行 `merge_cst_level1_exports.py --strict` 和 `run_cst_level1_batch_reconstruction.py --require-cases`。
3. C_docs 将真实 Level 1 指标和截图补进报告、PPT 素材包、scorecard 和阶段说明。
