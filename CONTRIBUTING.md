# 协作说明

本仓库用于“复杂航空载体电磁辐射空域特性测量技术比赛”的代码、文档、
CST 工作流和小型可复现结果协作。协作目标是让每一次提交都能被队友复现、
审查和继续推进。

## Issue 入口

开始新任务前，优先开 GitHub issue 并选择对应模板：

- `[CST]`：CST 建模、求解、导出、true near-field monitor 回填。
- `[ALG]`：采样优化、近远场重建、SWE/Huygens、分类识别实验。
- `[DOC]`：workflow、未来方案、报告、PPT、文献矩阵、README。
- `[BUG]`：脚本报错、数据字段异常、路径失效或协作流程问题。

当前最优先的 CST 数据阻塞是两个 required `full_grid_162` 真近场 monitor
CSV：

- `data/cst_exports/level1_true_nearfield/L1_short_dipole_z_1p2G_true_nearfield.csv`
- `data/cst_exports/level1_true_nearfield/L1_halfwave_dipole_z_1p2G_true_nearfield.csv`

每个文件应包含 486 行，并覆盖 `Ex/Ey/Ez` 三个复场分量。

## 分支与提交

- `main` 保持可读、可复现、可展示。
- 新任务建议从 `main` 拉分支，例如：
  - `feature/cst-true-monitor-*`
  - `feature/sampling-layout-*`
  - `feature/huygens-swe-*`
  - `docs/workflow-*`
- 每次提交尽量只改一个主题。不要把 CST 数据、算法脚本和报告文字混在一个
  commit 里。
- 提交说明使用清楚的动词短句，例如 `Add true-monitor dropzone check`。

## 文件进仓库规则

建议提交：

- `code/` 中可复现脚本。
- `docs/`、`README.md`、`CONTRIBUTING.md` 和 `.github/` 协作模板。
- 小型 CSV/JSON/README 结果摘要，尤其是能解释当前 gate 状态的文件。
- CST workpack、handoff、命令清单和校验摘要。

默认不提交：

- `node_modules/`
- CST `Result/`、`Temp/`、`ModelCache/`、`Export/` 等求解缓存。
- 最终 zip、视频缓存、重复提交包。
- 可再生成的大型 CSV。
- 大型 CST 工程二进制和运行缓存。

如果确实需要协作大文件，优先使用 GitHub Release、Git LFS 或队伍共享网盘，
并在仓库中保留链接、SHA256、生成命令和摘要。不要直接把大型缓存强行提交到
`main`。

## 提交前检查

只改文档时，至少检查路径和口径是否与当前工程状态一致，避免把
`pending_source`、`diagnostic_only` 或“复跑优先级”写成最终证明。

改 Python 脚本时，至少运行：

```powershell
python -m compileall code
```

涉及 true near-field monitor 时，按顺序运行：

```powershell
python code\check_true_nearfield_dropzone.py --required-only --full-grid-only
python code\run_true_nearfield_gate.py --required-only
python code\run_true_nearfield_workflow_decision.py
```

涉及 G3/SWE/Huygens 证据时，优先刷新：

```powershell
python code\build_g3_model_dashboard.py
```

## 结论口径

- `strict_pass` 或经导师认可的 near-pass 才能作为主证明。
- `pending_source` 表示数据还没到，不能写成算法失败或通过。
- `diagnostic_only` 表示可以写成瓶颈分析、校准证据或下一步工作，不能写成最终
  少测点证明。
- 当前标量 spherical NF-FF 结果可以作为角度、相位、极化和复场分量 sanity
  check，也可以作为 true-monitor 复跑优先级；在真近场 monitor 和物理/vector
  full-grid baseline 通过前，不能写成最终 vector SWE/Huygens 证明。
