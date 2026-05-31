# 提交就绪清单

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
结论：尚未达到最终提交状态。

## 总体状态

| 指标 | 当前值 |
| --- | --- |
| completion_proven | true |
| next_blocking_gate |  |
| final files ready | 5/5 |
| submission draft copied_or_generated / missing | 75 / 0 |
| submission draft is_final | false |
| submission index ready / draft-source / blocked / missing | 64 / 2 / 0 / 0 |
| ready_to_submit | false |

## 正式交付物

| 交付物 | 路径 | 状态 | 说明 |
| --- | --- | --- | --- |
| 正式报告 PDF | submission/01_report/solution_report.pdf | 存在 | 正式提交必须存在 |
| 正式报告 DOCX | submission/01_report/solution_report.docx | 存在 | 正式提交必须存在 |
| 答辩 PPTX | submission/02_presentation/defense_slides.pptx | 存在 | 正式提交必须存在 |
| 答辩 PPT PDF | submission/02_presentation/defense_slides.pdf | 存在 | 正式提交必须存在 |
| 演示视频 MP4 | submission/03_video/demo_video.mp4 | 存在 | 正式提交必须存在 |

## 仍需关闭的提交条件

| 对象 | 当前问题 | 关闭方式 |
| --- | --- | --- |
| G5 | 正式报告/PPT/视频和剩余风险说明未闭合 | 生成正式 PDF/DOCX/PPTX/PPT PDF/MP4，并处理 Level 1/Level 2 证据边界。 |
| Level 1 | solver-safe 重建精度风险 | 优化重建或在报告中形成可辩护误差机理说明。 |
| Level 2 | 简化结构遮挡对照需写入成稿 | 引用 outputs/cst_structure_comparison，并明确非 full-wave airframe 边界。 |
| 人工提交信息 | 学校、申报人、联系电话、报名表等仍需人工复核 | 最终打包前补齐并复查。 |

## 复核命令

| 用途 | 命令 |
| --- | --- |
| 阶段跟进 | python code\build_progress_report.py --note "本阶段完成了某项关键进展" |
| 无变化巡检 | python code\build_progress_report.py --only-if-changed |
| 最终草稿包 | python code\build_submission_draft.py |
| 最终复核链 | python code\build_scorecard.py; python code\build_problem_requirements_matrix.py; python code\build_submission_index.py; python code\build_completion_audit.py; python code\build_master_dashboard.py |

## 推荐入口

| 用途 | 路径 |
| --- | --- |
| 导师阅读门户 | docs/progress_reports/mentor_portal.md |
| 组会汇报稿 | docs/progress_reports/meeting_brief.md |
| 每日进展汇总 | docs/progress_reports/daily_digest.md |
| 导师证据映射 | docs/progress_reports/evidence_map.md |
| 导师决策清单 | docs/progress_reports/decision_brief.md |
| 导师问答卡 | docs/progress_reports/mentor_qa.md |
| G5 关闭路线 | docs/progress_reports/g5_closure_brief.md |
| 风险登记表 | docs/progress_reports/risk_register.md |
| 下一步行动清单 | docs/progress_reports/next_action_brief.md |
| 最终交付缺口板 | docs/progress_reports/final_delivery_gap_board.md |
| 导师 30 秒快照 | docs/progress_reports/mentor_snapshot.md |
| 最新导师汇报 | docs/progress_reports/latest_mentor_brief.md |
| submission 草稿包摘要 | submission/submission_draft_summary.json |
| 提交物索引 | outputs/submission_index/submission_package_index.md |
