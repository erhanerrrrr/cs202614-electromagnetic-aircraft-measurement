# CST 目录说明

本目录作为 CST 建模与自动化工作流的入口索引。当前不重复搬运大型 `.cst` 工程、`Result/` 缓存和临时求解目录；这些文件仍保留在 `outputs/` 与 `submission/05_cst/` 的既有路径中，避免破坏已生成的审计和复现链。

## 当前 CST 主线

| 类型 | 当前位置 | 说明 |
|---|---|---|
| 测点表与导出模板 | `outputs/cst_templates/` | 半球面 2π 测点、nearfield/farfield demo、导出模板。 |
| 宏模板与参数表 | `outputs/cst_macro_templates/` | Level 1/Level 2 VBA 宏骨架、参数表、pilot 队列。 |
| 操作手册 | `outputs/cst_operator_runbook/` | 162 探针点、远场网格、导出合同、人工 CST 操作步骤。 |
| Level 1 workpack | `outputs/cst_level1_workpack/` | 标准源建模任务卡、导出检查表、工作项。 |
| Level 2 workpack | `outputs/cst_level2_workpack/` | 多源多状态样本任务卡、频点/类别清单。 |
| 本机 CST 工程/求解痕迹 | `outputs/cst_real_level1_projects/`, `outputs/cst_solver_ready_level1_projects/`, `outputs/cst_solver_trials/`, `outputs/cst_level2_element_library/` | 已生成工程与求解记录，Git 默认排除大缓存。 |
| 真实导出数据 | `data/cst_exports/` | 供 Python 合并、重建和识别使用的 nearfield/farfield CSV。 |

## 后续 Python 调 CST 工作流

1. 在 `code/prepare_cst_level*_manifest.py` 固定样本、频点、极化、源参数和导出合同。
2. 在 `code/run_cst_level1_required_automation.py` 或 `code/run_cst_level2_element_library.py` 调用 CST API 生成工程。
3. 用 `code/run_cst_solver_project.py` 求解单工程，或按 runbook 人工批量运行。
4. 用 `code/export_cst_farfield_results.py` 与 `code/export_cst_level2_superposed_results.py` 导出结果。
5. 用 `code/check_cst_export.py`、`code/merge_cst_level*_exports.py` 进入 Python 数据链路。
