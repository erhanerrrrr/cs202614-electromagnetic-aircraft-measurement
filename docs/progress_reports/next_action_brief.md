# 下一步行动清单

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
当前阻塞门：``

## 一句话判断

项目已通过 completion audit，可进入最终提交复核。

## 优先行动

| 优先级 | 负责人 | Gate | 动作 | 预期产物 | 关闭证据 | 当前阻塞 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | C_docs | FINAL | 人工完整播放 submission/03_video/demo_video.mp4。 | 人工确认视频能正常播放，或替换为带人工讲解/旁白的版本。 | 视频播放无黑屏、卡顿、错页；若竞赛要求讲解录屏，则替换并重跑审计。 | 无 |
| 2 | C_docs | FINAL | 整理最终压缩包命名、报名表和人工提交信息。 | 最终 zip、报名表扫描件/信息、学校和申报人信息。 | 压缩包目录与赛题命名规则一致，人工信息补齐。 | 无 |

## 命令或证据入口

| 优先级 | 命令/文件 | 备注 |
| --- | --- | --- |
| 1 | submission/03_video/demo_video.mp4; outputs/video_artifact/demo_video_summary.json | 这是提交前质量动作，不影响当前自动审计的 completion_proven=true。 |
| 2 | submission; docs/final_submission_package_plan.md | 该项需要队伍成员提供真实学校、姓名、电话和报名表，不能由脚本自动完成。 |

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
| 导师 30 秒快照 | docs/progress_reports/mentor_snapshot.md |
| 本次变化说明 | docs/progress_reports/latest_change_note.md |
| 风险登记表 | docs/progress_reports/risk_register.md |
| 最新导师汇报 | docs/progress_reports/latest_mentor_brief.md |
| 阶段时间线 | docs/progress_reports/progress_index.md |
| 总控状态看板 | outputs/master_dashboard/master_status_dashboard.md |
| 完成度审计 | outputs/completion_audit/completion_audit.md |
