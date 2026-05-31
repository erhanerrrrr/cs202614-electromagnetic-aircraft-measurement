# 导师证据映射

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
用途：把“目前做了什么”和“产物是什么”逐条映射到可核验证据。

## 结论到证据

| 结论 | 当前说法 | 证据入口 | 状态判断 |
| --- | --- | --- | --- |
| 方案和路线已建立 | 已形成文献矩阵、技术路线、报告草稿和赛题要求矩阵。 | docs/literature_matrix.md; docs/team_division_technical_route.md; docs/solution_report_draft.md; outputs/problem_requirements/problem_requirements_matrix.md | 已证实 |
| 测量布局已固定 | 采用 2π 上半球测量面，半球面测点数为 162。 | outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv | 已证实 |
| Level 1 required 标准源链路已完成 | required-now 缺失文件为 0；仍需处理 solver-safe 重建精度风险。 | outputs/cst_level1_merge_report; outputs/cst_level1_reconstruction_batch; src/run_cst_reconstruction.py | 已证实，但有指标风险 |
| Level 2 full48 样本链路已跑通 | 48/48 个 CST-derived element-library 样本完整，识别 accuracy 为 1.000。 | outputs/cst_level2_merge_report; outputs/cst_recognition_level2; docs/stage_notes/19_cst_level2_full48_recognition.md | 已证实；简化结构遮挡对照已补，full-wave airframe 仍为增强项 |
| 审计和评分证据已生成 | Gate 完成/部分/缺失为 8/0/0，下一阻塞门为 。 | outputs/scorecard/scorecard.md; outputs/completion_audit/completion_audit.md; outputs/master_dashboard/master_status_dashboard.md | 已证实 |
| 提交草稿包已生成 | submission 草稿包 copied_or_generated/missing 为 75/0；submission index ready/draft-source/blocked/missing 为 64/2/0/0。 | submission/; submission/submission_draft_summary.json; outputs/submission_index/submission_package_index.md | 草稿态已证实 |
| 最终提交态尚未达成 | completion_proven=True；正式 PDF/DOCX/PPTX/PPT PDF/MP4 已存在 5/5。 | submission/01_report; submission/02_presentation; submission/03_video; docs/progress_reports/submission_readiness.md | 未关闭 |

## 证据文件状态

| 证据 | 路径 | 当前状态 |
| --- | --- | --- |
| 文献矩阵 | docs/literature_matrix.md | 存在，13380 bytes |
| 技术路线和分工 | docs/team_division_technical_route.md | 存在，17214 bytes |
| 报告草稿 | docs/solution_report_draft.md | 存在，35476 bytes |
| 赛题要求矩阵 | outputs/problem_requirements/problem_requirements_matrix.md | 存在，7381 bytes |
| 测量布局 CSV | outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv | 存在，30416 bytes |
| Level 1 合并报告 | outputs/cst_level1_merge_report | 目录存在 |
| Level 1 重建结果 | outputs/cst_level1_reconstruction_batch | 目录存在 |
| Level 2 合并报告 | outputs/cst_level2_merge_report | 目录存在 |
| Level 2 识别结果 | outputs/cst_recognition_level2 | 目录存在 |
| 评分证据板 | outputs/scorecard/scorecard.md | 存在，6414 bytes |
| 完成度审计 | outputs/completion_audit/completion_audit.md | 存在，4443 bytes |
| 总控状态看板 | outputs/master_dashboard/master_status_dashboard.md | 存在，5883 bytes |
| 提交包索引 | outputs/submission_index/submission_package_index.md | 存在，15564 bytes |
| submission 草稿摘要 | submission/submission_draft_summary.json | 存在，396 bytes |

## 最终交付物状态

| 最终交付物 | 路径 | 状态 |
| --- | --- | --- |
| 正式报告 PDF | submission/01_report/solution_report.pdf | 存在 |
| 正式报告 DOCX | submission/01_report/solution_report.docx | 存在 |
| 答辩 PPTX | submission/02_presentation/defense_slides.pptx | 存在 |
| 答辩 PPT PDF | submission/02_presentation/defense_slides.pdf | 存在 |
| 演示视频 MP4 | submission/03_video/demo_video.mp4 | 存在 |

## 推荐入口

| 用途 | 路径 |
| --- | --- |
| 导师阅读门户 | docs/progress_reports/mentor_portal.md |
| 每日进展汇总 | docs/progress_reports/daily_digest.md |
| 导师问答卡 | docs/progress_reports/mentor_qa.md |
| 导师决策清单 | docs/progress_reports/decision_brief.md |
| 组会汇报稿 | docs/progress_reports/meeting_brief.md |
| 导师 30 秒快照 | docs/progress_reports/mentor_snapshot.md |
| 风险登记表 | docs/progress_reports/risk_register.md |
| 提交就绪清单 | docs/progress_reports/submission_readiness.md |
| 最新导师汇报 | docs/progress_reports/latest_mentor_brief.md |
| 阶段索引 | docs/progress_reports/progress_index.md |
