# 导师问答卡

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
用途：预置导师常问问题、建议回答和证据入口，便于组会或答辩前快速预演。

## 当前状态

| 项目 | 当前值 |
| --- | --- |
| completion_proven | true |
| next_blocking_gate |  |
| final files ready | 5/5 |
| submission draft copied_or_generated / missing | 75 / 0 |

## 常见问答

| 问题 | 建议回答 | 证据入口 |
| --- | --- | --- |
| 现在项目完成了吗？ | 还没有到最终提交态。主体技术链路和 submission 草稿结构已完成，但 completion_proven=True，下一阻塞门是 。 | docs/progress_reports/submission_readiness.md; outputs/completion_audit/completion_audit.md |
| 目前做了什么？ | 已完成文献与技术路线、2π 上半球测量布局、Python baseline、Level 1 required 标准源链路、Level 2 full48 样本链路、scorecard/completion audit/master dashboard/submission index 和 submission 草稿包。 | docs/progress_reports/evidence_map.md; docs/project_progress_report.md |
| 当前产物是什么？ | submission 草稿包 75 项已复制或生成，缺失 0；submission index ready/draft-source/blocked/missing 为 64/2/0/0。 | submission/; submission/submission_draft_summary.json; outputs/submission_index/submission_package_index.md |
| 为什么还不能最终提交？ | 正式 PDF/DOCX/PPTX/PPT PDF/MP4 仍为 5/5，Level 1 重建指标风险和 Level 2 简化结构边界仍需在报告中处理。 | docs/progress_reports/decision_brief.md; docs/progress_reports/risk_register.md |
| Level 1 的风险怎么解释？ | 当前不是缺 CST 文件，而是 solver-safe 重建质量需要复核；建议形成误差机理说明，并保留一次快速优化机会。 | outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py |
| Level 2 的证据够不够？ | full48 样本链路已跑通且识别 accuracy 为 1.000；简化结构遮挡对照已显示 cross-domain accuracy 为 1.000，但不是 full-wave airframe。 | outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md |
| 下一步最应该先做什么？ | 优先关闭 G5：把 Level 1/2 结果、风险边界和证据写进正式报告/PPT/视频脚本，并导出 PDF/DOCX/PPTX/PPT PDF/MP4。 | docs/progress_reports/next_action_brief.md; docs/final_submission_package_plan.md |
| 需要导师拍板什么？ | 请确认 Level 1 是继续优化还是先写误差说明、Level 2 是否接受简化结构对照作为边界证据、以及是否优先生成正式提交件。 | docs/progress_reports/decision_brief.md |

## 快速入口

| 用途 | 路径 |
| --- | --- |
| 30 秒看结论 | docs/progress_reports/mentor_snapshot.md |
| 5 分钟组会汇报 | docs/progress_reports/meeting_brief.md |
| 今日复盘 | docs/progress_reports/daily_digest.md |
| 证据逐条核对 | docs/progress_reports/evidence_map.md |
| 需要拍板的问题 | docs/progress_reports/decision_brief.md |
| G5 关闭路线 | docs/progress_reports/g5_closure_brief.md |
| 提交前复核 | docs/progress_reports/submission_readiness.md |
| 最新完整汇报 | docs/progress_reports/latest_mentor_brief.md |
