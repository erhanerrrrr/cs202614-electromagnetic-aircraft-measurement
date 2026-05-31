# 导师决策清单

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
用途：集中列出当前需要导师确认或拍板的技术取舍和提交策略。

## 当前状态

| 项目 | 当前值 |
| --- | --- |
| completion_proven | true |
| next_blocking_gate |  |
| final files ready | 5/5 |
| submission draft copied_or_generated / missing | 75 / 0 |
| submission draft is_final | false |

## 待决策事项

| 编号 | 议题 | 需要拍板的问题 | 影响 | 建议取向 | 证据入口 |
| --- | --- | --- | --- | --- | --- |
| D1 | Level 1 solver-safe 重建精度 | 继续优化重建，或保留现有结果并形成误差机理说明。 | 若继续优化，可能提升指标但占用时间；若写清机理，可先保障报告闭环。 | 建议先形成可辩护说明，同时保留一次快速复核机会。 | outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py |
| D2 | Level 2 复杂载体结构证据 | 简化结构遮挡对照已生成，需决定是否进一步追加 full-wave airframe 对照。 | 当前对照可支撑边界说明；full-wave 对照会增强可信度但耗时更长。 | 建议先把当前结构对照写入报告/PPT，时间允许再补 full-wave。 | outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md |
| D3 | 正式报告/PPT/视频优先级 | 先集中生成 PDF/DOCX/PPTX/PPT PDF/MP4，还是先继续补技术证据。 | 当前正式交付物 5/5，不生成则无法关闭 G5。 | 建议优先成稿并导出正式文件，再把技术风险作为报告边界或附录说明。 | docs/solution_report_draft.md; docs/final_submission_package_plan.md; outputs/scorecard/scorecard.md |
| D4 | 最终提交人工信息 | 学校、申报人、联系电话、报名表等由谁确认。 | 技术包可以自动生成，人工报名信息不能由脚本证明。 | 建议指定 C_docs 收口，全队最终复核。 | docs/final_submission_package_plan.md; submission/ |
| D5 | 最终完成度验收口径 | completion_proven=true 前，是否接受 G5 风险说明作为阶段闭环。 | 当前 completion_proven=True，next_blocking_gate=。 | 建议以正式文件齐全、scorecard 一致、风险边界明确作为最终验收口径。 | outputs/completion_audit/completion_audit.md; outputs/master_dashboard/master_status_dashboard.md |

## 关闭口径

| 编号 | 关闭证据 |
| --- | --- |
| D1 | 报告中能解释当前 NMSE/correlation 风险，或新重建指标明显改善。 |
| D2 | 报告/PPT 中明确结构对照结果，或明确 element-library full48 的适用边界。 |
| D3 | 正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。 |
| D4 | 人工报名信息已补齐并经全队复核。 |
| D5 | completion_proven=true，submission index blocked=0，最终文件齐全。 |

## 正式交付物缺口

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
| 导师问答卡 | docs/progress_reports/mentor_qa.md |
| 导师证据映射 | docs/progress_reports/evidence_map.md |
| G5 关闭路线 | docs/progress_reports/g5_closure_brief.md |
| 风险登记表 | docs/progress_reports/risk_register.md |
| 下一步行动清单 | docs/progress_reports/next_action_brief.md |
| 提交就绪清单 | docs/progress_reports/submission_readiness.md |
| 组会汇报稿 | docs/progress_reports/meeting_brief.md |
| 最新导师汇报 | docs/progress_reports/latest_mentor_brief.md |
