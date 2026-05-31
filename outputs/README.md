# outputs 目录说明

本目录存放脚本自动生成的中间结果、图表、报告素材、CST workpack、审计结果和提交包素材。

## 协作约定

- `outputs/` 里的内容多数可以由 `code/` 脚本再生成，不应把所有缓存都视为必须手工维护的源文件。
- GitHub 仓库会忽略 final zip、大型合成 CSV、CST 求解缓存和临时目录，以避免仓库过大。
- 需要复核某个结果时，优先查看对应子目录中的 `README_*.md`、`*.json` summary 和 `docs/stage_notes/`。

## 关键入口

| 子目录 | 说明 |
|---|---|
| `cst_macro_templates/` | CST 宏模板、参数表和 pilot 队列。 |
| `cst_level1_workpack/`, `cst_level2_workpack/` | Level 1/Level 2 CST 建模任务包。 |
| `cst_operator_runbook/` | CST 真机操作流程、测点表和导出合同。 |
| `completion_audit/`, `scorecard/`, `problem_requirements/` | 完成度、评分项和赛题要求证据矩阵。 |
| `final_archive/` | 最终 zip 与校验摘要，本地保留，默认不进 Git。 |
