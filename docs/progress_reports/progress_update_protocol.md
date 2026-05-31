# 进展跟进操作规程

更新时间：2026-05-29 12:40:12 +0800  
阶段标记：`M-20260529-124012`  
用途：把本线程的长期跟进动作固定成可复用规则，避免遗漏阶段标记、产物路径、图表和最终提交缺口。

## 当前基线

| 项目 | 当前值 |
| --- | --- |
| 最新阶段标记 | `M-20260529-124012` |
| 最新有效导师汇报 | docs/progress_reports/2026-05-29_124012_mentor_brief.md |
| next_blocking_gate |  |
| completion_proven | true |
| Gate complete / partial / missing | 8 / 0 / 0 |
| submission ready / draft-source / blocked / missing | 64 / 2 / 0 / 0 |
| submission draft copied / missing / final | 75 / 0 / False |
| final files ready | 5/5 |

## 何时标记阶段

| 场景 | 判据 | 操作 |
| --- | --- | --- |
| 必须新增阶段标记 | Gate 状态、completion_proven、submission 统计、最终交付物、关键证据文件或报告/PPT/视频草稿有实质变化。 | 运行 `python code\build_progress_report.py --note "本阶段完成了..."`。 |
| 可以人工补记 | 会议纪要、导师意见、风险关闭口径或提交策略发生变化，但自动指纹未覆盖。 | 用 `--note` 明确写出变化、产物和下一步。 |
| 只做跳过复核 | 核心状态和关键文件没有变化，只想确认项目仍处于同一状态。 | 运行 `python code\build_progress_report.py --only-if-changed`，期望 `skipped=true`。 |
| 不得伪造完成 | 正式 PDF/DOCX/PPTX/PPT PDF/MP4 未齐全，或 G5 风险未关闭。 | 保持 `completion_proven=false`，并在汇报中写清缺口。 |

## 每次跟进节奏

| 时机 | 动作 |
| --- | --- |
| 阶段工作完成后 | 先重跑对应技术脚本或文档生成脚本，再刷新 scorecard / requirements / submission index / completion audit / dashboard。 |
| 汇报归档前 | 用明确 note 生成新阶段，确认 `archive_written=true`、图表存在、latest mentor brief 指向新归档。 |
| submission 同步 | 运行 `python code\build_submission_draft.py`，确认 `copied_or_generated=64` 且 `missing=0`。 |
| 防止噪声 | 随后运行一次 `--only-if-changed`，确认无新变化时不会继续写归档。 |
| 导师沟通前 | 优先打开导师门户、30 秒快照、G5 关闭路线和决策清单。 |

## 复核命令

| 用途 | 命令 |
| --- | --- |
| 评分证据 | python code\build_scorecard.py |
| 赛题要求矩阵 | python code\build_problem_requirements_matrix.py |
| 提交物索引 | python code\build_submission_index.py |
| 完成度审计 | python code\build_completion_audit.py |
| 总控看板 | python code\build_master_dashboard.py |
| 阶段标记 | python code\build_progress_report.py --note "本阶段完成了..." |
| 无变化复核 | python code\build_progress_report.py --only-if-changed |
| 提交草稿同步 | python code\build_submission_draft.py |

## 汇报口径

| 要回答的问题 | 最低要求 |
| --- | --- |
| 一句话结论 | 当前 Gate、是否可提交、最大缺口。 |
| 本阶段做了什么 | 列出新完成的脚本、数据、报告、图表或提交包动作。 |
| 产物是什么 | 给出可点击/可追溯路径，避免只写描述。 |
| 证据是否足够 | 说明 scorecard、completion audit、submission index 或人工文件能否支撑结论。 |
| 下一步谁来关 | 负责人、关闭证据和阻塞项必须落到文件或命令。 |

## 图表

![Gate 和提交物状态](assets/M-20260529-124012_status_overview.png)

![最终交付物状态](assets/M-20260529-124012_final_deliverables.png)

![阶段趋势](assets/M-20260529-124012_progress_history.png)

## 推荐入口

| 用途 | 路径 |
| --- | --- |
| 导师阅读门户 | docs/progress_reports/mentor_portal.md |
| 导师 30 秒快照 | docs/progress_reports/mentor_snapshot.md |
| G5 关闭路线 | docs/progress_reports/g5_closure_brief.md |
| 下一步行动清单 | docs/progress_reports/next_action_brief.md |
| 风险登记表 | docs/progress_reports/risk_register.md |
| 提交就绪清单 | docs/progress_reports/submission_readiness.md |
| 巡检范围说明 | docs/progress_reports/watch_scope.md |
| 状态复核台账 | docs/progress_reports/status_review_log.md |
| 最新巡检状态卡 | docs/progress_reports/latest_status_review.md |
| 阶段索引 | docs/progress_reports/progress_index.md |
