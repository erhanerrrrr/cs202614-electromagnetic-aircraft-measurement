# S09 CST 执行 dashboard 与真实数据 dropzone 说明

## 做了什么

本阶段新增了真实 CST 执行 dashboard，把当前最短阻塞点 `G2` 拆成可直接交给 CST 负责同学执行的操作表。脚本同时创建 `data/cst_exports` 真实导出 dropzone，用于放置 CST 导出的 nearfield/farfield CSV。

## 为什么这样做

当前项目已经有 manifest、workpack、宏模板和审计脚本，但真实 CST 执行时仍容易遇到三个问题：

- 不知道先跑哪个案例。
- 导出文件名和路径容易写错。
- 跑完后不知道先用哪个命令验收。

dashboard 把这些信息压缩到一页，并把 required 文件缺口自动列出来。这样队友只要按 dashboard 操作，导出的文件就能直接被 Python 审计脚本识别。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_cst_execution_dashboard.py` | 生成 CST 执行 dashboard、action sheet 和 dropzone README | 每次放入新 CST 文件后重新运行 |
| `outputs/cst_execution_dashboard/cst_execution_dashboard.md` | 当前 G2/G3 状态、先跑哪些、导出到哪里、验收命令 | CST 执行入口 |
| `outputs/cst_execution_dashboard/level1_required_action_sheet.csv` | 两个 Level 1 required 标准源的参数、路径、命令 | 直接交给 CST 负责同学 |
| `outputs/cst_execution_dashboard/level2_pilot_action_sheet.csv` | 每类 1 个 Level 2 pilot 样本 | G2 通过后再跑 |
| `outputs/cst_execution_dashboard/missing_real_cst_files.csv` | 当前缺失的真实 nearfield/farfield 文件 | 判断还有哪些文件未导出 |
| `data/cst_exports/README_cst_exports.md` | 真实 CST 导出总说明 | 放置真实 CST 文件前先看 |
| `data/cst_exports/level1/README_level1_dropzone.md` | Level 1 required 文件名与规则 | G2 标准源导出位置 |
| `data/cst_exports/level2/README_level2_dropzone.md` | Level 2 pilot/full 文件名与规则 | G3 多源样本导出位置 |

## 验证方式

```powershell
python code\build_cst_execution_dashboard.py
python code\merge_cst_level1_exports.py
python code\merge_cst_level2_exports.py
python code\build_completion_audit.py
```

当前 dashboard 结果：

- Level 1 required action：2 个。
- 当前 required-now 缺失文件：4 个。
- Level 2 pilot action：4 个。
- 当前 Level 2 pilot 缺失文件：8 个。
- `data/cst_exports` 已创建，但其中只有 README，没有伪造 nearfield/farfield 数据。

## 当前不足

- 真实 CST nearfield/farfield 仍未导出。
- dashboard 只能降低执行摩擦，不能替代 CST 工程、截图、真实导出和审计指标。

## 下一步

1. 先按 `outputs/cst_execution_dashboard/level1_required_action_sheet.csv` 完成两个 Level 1 required 导出。
2. 将文件放入 `data/cst_exports/level1`。
3. 运行 `python code\merge_cst_level1_exports.py --strict`。
4. 通过后运行 `python code\run_cst_level1_batch_reconstruction.py --require-cases`。
