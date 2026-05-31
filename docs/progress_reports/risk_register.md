# 风险登记表

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
当前阻塞门：``

## 当前状态

| 指标 | 当前值 |
| --- | --- |
| completion_proven | true |
| next_blocking_gate |  |
| final files ready | 5/5 |
| submission draft copied_or_generated / missing | 75 / 0 |

## 风险清单

| 编号 | 等级 | 风险 | 影响 | 负责人 | 缓解动作 | 关闭证据 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | 高 | Level 1 solver-safe 重建精度风险 | 影响三维场重建高精度部分的可信度表达。 | A_algorithm | 复核近远场一致性、等效源基函数和正则化；必要时形成误差机理说明。 | 报告中能解释当前 NMSE/correlation 风险，或新重建指标明显改善。 | 未关闭 |
| R2 | 中 | Level 2 full48 主要是 element-library 叠加证据 | 已补简化结构遮挡对照，但仍不是 full-wave airframe scattering。 | A_algorithm + C_docs | 把简化结构对照写入报告/PPT，并明确 full-wave airframe 是后续增强项。 | outputs/cst_structure_comparison 被报告/PPT 引用，且边界说明清楚。 | 未关闭 |
| R3 | 高 | 正式交付物已存在 5/5，四件套已齐全。 | 不能进入最终提交态，G5 仍为 partial。 | C_docs | 把 Level 1/2 最新结果写入正式报告、PPT 和视频脚本并导出剩余正式文件。 | 正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。 | 未关闭 |
| R4 | 中 | 最终打包和人工报名信息仍需复核 | 提交系统/邮箱所需学校、申报人、联系电话、报名表仍需人工补充。 | C_docs / 全队 | 最终打包前重建 scorecard、submission index、completion audit、master dashboard 和 submission draft。 | completion_proven=true，submission index blocked=0，最终文件齐全，人工报名信息已补齐。 | 待最终阶段处理 |

## 证据入口

| 风险编号 | 证据/命令入口 |
| --- | --- |
| R1 | outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py |
| R2 | outputs/cst_level2_element_trials; docs/stage_notes/19_cst_level2_full48_recognition.md |
| R3 | submission/01_report; submission/02_presentation; submission/03_video; docs/solution_report_draft.md |
| R4 | outputs/submission_index; outputs/completion_audit; outputs/master_dashboard; submission/submission_draft_summary.json |

## 最终交付物缺口

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
| 组会汇报稿 | docs/progress_reports/meeting_brief.md |
| 每日进展汇总 | docs/progress_reports/daily_digest.md |
| 导师证据映射 | docs/progress_reports/evidence_map.md |
| 导师决策清单 | docs/progress_reports/decision_brief.md |
| 导师问答卡 | docs/progress_reports/mentor_qa.md |
| G5 关闭路线 | docs/progress_reports/g5_closure_brief.md |
| 下一步行动清单 | docs/progress_reports/next_action_brief.md |
| 提交就绪清单 | docs/progress_reports/submission_readiness.md |
| 导师 30 秒快照 | docs/progress_reports/mentor_snapshot.md |
| 本次变化说明 | docs/progress_reports/latest_change_note.md |
| 最新导师汇报 | docs/progress_reports/latest_mentor_brief.md |
| 评分证据板 | outputs/scorecard/scorecard.md |
| 完成度审计 | outputs/completion_audit/completion_audit.md |
