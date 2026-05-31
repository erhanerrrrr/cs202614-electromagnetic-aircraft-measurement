# S10 报告成稿素材包说明

## 做了什么

本阶段新增了报告成稿素材包，把 `docs/solution_report_draft.md` 拆解为章节状态、图表占位、正式引用短表和待替换 demo 结果清单。它不会生成最终 PDF/DOCX，而是为后续真实 CST 数据到位后的快速成稿做准备。

## 为什么这样做

目前真实 CST Level 1/Level 2 数据还未导出，直接生成最终报告文件会制造误解。更合理的做法是先明确：

- 哪些章节已经可以整理成正式文本。
- 哪些章节仍被真实 CST 证据阻塞。
- 哪些图表只是 demo/synthetic 占位。
- 哪些权威文献应作为正文核心引用。

这样等 G2/G3 通过后，只需要替换图表、指标和结论，不必重新梳理整篇报告。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_report_package.py` | 生成报告成稿素材包 | 每次报告草稿或证据状态变化后运行 |
| `outputs/report_package/README_report_package.md` | 报告素材包说明 | 从这里了解报告成稿规则 |
| `outputs/report_package/report_section_status.csv` | 每个报告章节的 readiness 与 blocker | 判断哪些章节能成稿 |
| `outputs/report_package/report_reference_shortlist.csv` | A 级核心引用清单 | 写正式参考文献和第 2 章 |
| `outputs/report_package/report_reference_shortlist.md` | 人读版核心引用清单 | 答辩和写作时查阅 |
| `outputs/report_package/report_figure_manifest.csv` | 图表占位和替换要求 | 替换 demo 图为真实 CST 图 |
| `outputs/report_package/report_replacement_todo.csv` | 报告/PPT/视频前的任务顺序 | 成稿前逐项检查 |
| `outputs/report_package/report_package_summary.json` | 素材包统计 | 供审计脚本或人工检查 |

## 验证方式

```powershell
python code\build_report_package.py
python code\build_scorecard.py
python code\build_submission_index.py
python code\build_completion_audit.py
```

当前结果：

- 跟踪报告章节：13 个。
- A 级核心引用：12 条。
- 图表占位：7 个。
- demo/synthetic 图表：5 个。
- 成稿前替换任务：12 项。

## 当前不足

- 报告成稿素材包不是最终报告。
- `solution_report.pdf` 和 `solution_report.docx` 仍不应导出为 final。
- 真实 CST Level 1/Level 2 数据和截图仍是决定性缺口。

## 下一步

1. 完成 G2 两个 required 标准源。
2. 用真实重建图替换 `Fig-03`。
3. 完成 G3 Level 2 数据后替换识别混淆矩阵和删减曲线。
4. 再生成正式 DOCX/PDF/PPT/视频。
