# S07 最终提交包说明

## 做了什么

建立了最终提交包计划、报告草稿、PPT/视频大纲、代码复现说明、数据字典、scorecard 和 submission index。当前重点是保证最终材料结构不散，所有结果能回溯到脚本和输出。

## 为什么这样做

最终提交不是只交代码，还需要报告、PPT、视频、CST 工程、数据和附录。提前固定目录结构，可以防止后期真实 CST 数据到位后临时拼材料。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `docs/solution_report_draft.md` | 方案报告草稿 | 真实数据到位后替换 demo 结果并成稿 |
| `docs/final_submission_package_plan.md` | 最终提交包结构、PPT 和视频大纲 | 指导后期制作 |
| `docs/reproduce_commands.md` | 全流程复现命令 | 代码包说明基础 |
| `docs/data_dictionary.md` | 数据字段字典 | 确保 CST、Python、报告字段一致 |
| `outputs/submission_index` | 提交物状态表 | 判断哪些 final 文件缺失或 blocked |
| `outputs/completion_audit` | 完成度 gate | 判断总目标是否能声称完成 |
| `code/build_submission_draft.py` | 提交草稿包生成脚本 | 把当前文档、代码、manifest、审计结果预排到 `submission/` |
| `submission/` | 当前提交草稿包 | 检查最终材料目录和缺口，不等同于最终提交 |

## 验证方式

```powershell
python code\build_submission_index.py
python code\build_completion_audit.py
python code\build_submission_draft.py
```

## 当前不足

- `submission/` 已生成草稿结构，但尚未生成正式 PDF/DOCX/PPTX/MP4。
- 真实 CST 工程和导出缺失，因此报告和视频还不能成稿。

## 下一步

1. 补齐真实 CST Level 1/Level 2 证据。
2. 将真实图表和指标替换到报告和 PPT。
3. 导出最终提交包，并重新运行 completion audit。
