# 项目进展巡检范围

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
当前指纹：`fc713ec27a3fced44f17332a4793924e5d89b0653a32d7d4f4e0f9d88dac0329`

## 使用方式

```powershell
python code\build_progress_report.py --only-if-changed
```

无核心变化时，上述命令只刷新 `outputs/progress_report/progress_report_summary.json`，不会新增导师汇报归档；发现关键文件、Gate、提交包或最终交付物状态变化时，会生成新的阶段汇报。关键文件指纹按存在性、大小和 SHA256 内容计算，mtime 仅保留在 manifest 中用于诊断。

## 固定入口

| 入口 | 路径 |
| --- | --- |
| 当前进展总报告 | `docs/project_progress_report.md` |
| 导师阅读门户 | `docs/progress_reports/mentor_portal.md` |
| 当前进展简报 | `docs/progress_reports/current_progress_brief.md` |
| 组会汇报稿 | `docs/progress_reports/meeting_brief.md` |
| 每日进展汇总 | `docs/progress_reports/daily_digest.md` |
| 导师证据映射 | `docs/progress_reports/evidence_map.md` |
| 导师决策清单 | `docs/progress_reports/decision_brief.md` |
| 导师问答卡 | `docs/progress_reports/mentor_qa.md` |
| G5 关闭路线 | `docs/progress_reports/g5_closure_brief.md` |
| 导师 30 秒快照 | `docs/progress_reports/mentor_snapshot.md` |
| 本次变化说明 | `docs/progress_reports/latest_change_note.md` |
| 下一步行动清单 | `docs/progress_reports/next_action_brief.md` |
| 风险登记表 | `docs/progress_reports/risk_register.md` |
| 提交就绪清单 | `docs/progress_reports/submission_readiness.md` |
| 最新导师汇报 | `docs/progress_reports/latest_mentor_brief.md` |
| 阶段索引 | `docs/progress_reports/progress_index.md` |
| 历史台账 CSV | `outputs/progress_report/progress_history.csv` |
| 最新关键文件指纹 | `outputs/progress_report/watch_manifest_latest.json` |
| 巡检范围说明 | `docs/progress_reports/watch_scope.md` |
| 跟进操作规程 | `docs/progress_reports/progress_update_protocol.md` |
| 状态复核台账 | `docs/progress_reports/status_review_log.md` |
| 状态复核 CSV | `outputs/progress_report/status_review_log.csv` |

## 关键文件监测范围

| 路径 | 当前状态 | 字节数 | 用途 |
| --- | --- | --- | --- |
| README.md | 存在 | 32842 | 项目入口说明和当前小目标。 |
| src/build_progress_report.py | 存在 | 163041 | 进展跟踪、导师汇报、图表和历史台账生成脚本。 |
| src/build_submission_draft.py | 存在 | 16569 | 最终提交草稿包生成脚本。 |
| src/build_presentation_package.py | 存在 | 21915 | 答辩 PPT 与演示视频素材包生成脚本。 |
| docs/solution_report_draft.md | 存在 | 35476 | 正式报告草稿主内容。 |
| docs/final_submission_package_plan.md | 存在 | 9541 | 最终报告、PPT、视频和提交包规划。 |
| docs/project_file_index.md | 存在 | 12377 | 项目文件索引和阅读入口。 |
| docs/reproduce_commands.md | 存在 | 21777 | 复现命令和阶段巡检命令。 |
| outputs/master_dashboard/master_dashboard_summary.json | 存在 | 439 | 总控 dashboard 机器可读摘要。 |
| outputs/master_dashboard/master_gate_summary.csv | 存在 | 2475 | 各 Gate 状态表。 |
| outputs/master_dashboard/master_next_actions.csv | 存在 | 1281 | 下一步任务队列表。 |
| outputs/completion_audit/completion_audit_summary.json | 存在 | 134 | 完成度审计摘要。 |
| outputs/submission_index/submission_index_summary.json | 存在 | 109 | 提交物索引摘要。 |
| outputs/scorecard/scorecard.md | 存在 | 6414 | 评分证据板。 |
| outputs/problem_requirements/problem_requirements_matrix.md | 存在 | 7381 | 赛题要求矩阵。 |
| outputs/report_package/report_package_summary.json | 存在 | 1483 | 报告包机器可读摘要，记录章节、G5 口径、图表和关键指标。 |
| outputs/presentation_package/presentation_package_summary.json | 存在 | 1156 | 答辩 PPT 与演示视频素材包机器可读摘要。 |
| submission/submission_draft_summary.json | 存在 | 396 | 当前 submission 草稿包摘要。 |
| submission/01_report/solution_report.pdf | 存在 | 1471851 | 正式报告 PDF。 |
| submission/01_report/solution_report.docx | 存在 | 805797 | 正式报告 DOCX。 |
| submission/02_presentation/defense_slides.pptx | 存在 | 680245 | 答辩 PPTX。 |
| submission/02_presentation/defense_slides.pdf | 存在 | 678644 | 答辩 PPT PDF。 |
| submission/03_video/demo_video.mp4 | 存在 | 7856755 | 演示视频 MP4。 |
