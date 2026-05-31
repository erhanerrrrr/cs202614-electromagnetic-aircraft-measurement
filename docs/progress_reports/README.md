# 阶段进展汇报归档

本目录用于归档面向导师或组会的阶段性进展汇报。每当项目出现值得记录的进展、风险变化、交付物变化或阶段门关闭时，运行：

```powershell
python code\build_progress_report.py --note "本阶段完成了某项关键进展"
```

脚本会刷新 `docs/project_progress_report.md`，生成带 PNG/Mermaid 图表的导师汇报，并更新 `outputs/progress_report/progress_history.csv` 历史台账。若没有阶段备注，可省略 `--note`。

若用于定时巡检，希望无变化时不新增归档，可运行：

```powershell
python code\build_progress_report.py --only-if-changed
```

导师阅读门户见 `docs/progress_reports/mentor_portal.md`，组会汇报稿见 `docs/progress_reports/meeting_brief.md`，每日进展汇总见 `docs/progress_reports/daily_digest.md`，导师证据映射见 `docs/progress_reports/evidence_map.md`，导师决策清单见 `docs/progress_reports/decision_brief.md`，导师问答卡见 `docs/progress_reports/mentor_qa.md`，G5 关闭路线见 `docs/progress_reports/g5_closure_brief.md`，导师 30 秒快照见 `docs/progress_reports/mentor_snapshot.md`，本次变化说明见 `docs/progress_reports/latest_change_note.md`，下一步行动清单见 `docs/progress_reports/next_action_brief.md`，风险登记表见 `docs/progress_reports/risk_register.md`，提交就绪清单见 `docs/progress_reports/submission_readiness.md`，最终交付缺口板见 `docs/progress_reports/final_delivery_gap_board.md`，阶段索引见 `docs/progress_reports/progress_index.md`，巡检覆盖范围见 `docs/progress_reports/watch_scope.md`，跟进操作规程见 `docs/progress_reports/progress_update_protocol.md`，状态复核台账见 `docs/progress_reports/status_review_log.md`，最新巡检状态卡见 `docs/progress_reports/latest_status_review.md`，最新导师汇报固定入口见 `docs/progress_reports/latest_mentor_brief.md`。

## 命名规则

```text
YYYY-MM-DD_HHMM_mentor_brief.md
```

## 最新汇报

导师阅读门户：`docs/progress_reports/mentor_portal.md`  
组会汇报稿：`docs/progress_reports/meeting_brief.md`  
每日进展汇总：`docs/progress_reports/daily_digest.md`  
导师证据映射：`docs/progress_reports/evidence_map.md`  
导师决策清单：`docs/progress_reports/decision_brief.md`  
导师问答卡：`docs/progress_reports/mentor_qa.md`  
G5 关闭路线：`docs/progress_reports/g5_closure_brief.md`  
导师 30 秒快照：`docs/progress_reports/mentor_snapshot.md`  
本次变化说明：`docs/progress_reports/latest_change_note.md`  
下一步行动清单：`docs/progress_reports/next_action_brief.md`  
风险登记表：`docs/progress_reports/risk_register.md`  
提交就绪清单：`docs/progress_reports/submission_readiness.md`  
最终交付缺口板：`docs/progress_reports/final_delivery_gap_board.md`  
固定入口（推荐）：`docs/progress_reports/latest_mentor_brief.md`  
阶段索引：`docs/progress_reports/progress_index.md`  
跟进操作规程：`docs/progress_reports/progress_update_protocol.md`  
状态复核台账：`docs/progress_reports/status_review_log.md`  
最新巡检状态卡：`docs/progress_reports/latest_status_review.md`  
本次归档：`docs/progress_reports/2026-05-29_124012_mentor_brief.md`

## 汇报列表

| 时间 | 文件 | 主题 |
| --- | --- | --- |
| 2026-05-29 12:40:12 | `docs/progress_reports/2026-05-29_124012_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:34:54 | `docs/progress_reports/2026-05-29_123454_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:30:24 | `docs/progress_reports/2026-05-29_123024_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:26:14 | `docs/progress_reports/2026-05-29_122614_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:22:02 | `docs/progress_reports/2026-05-29_122202_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:20:26 | `docs/progress_reports/2026-05-29_122026_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:19:20 | `docs/progress_reports/2026-05-29_121920_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:15:10 | `docs/progress_reports/2026-05-29_121510_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:12:18 | `docs/progress_reports/2026-05-29_121218_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 12:00:57 | `docs/progress_reports/2026-05-29_120057_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:58:31 | `docs/progress_reports/2026-05-29_115831_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:55:29 | `docs/progress_reports/2026-05-29_115529_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:52:45 | `docs/progress_reports/2026-05-29_115245_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:51:46 | `docs/progress_reports/2026-05-29_115146_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:45:03 | `docs/progress_reports/2026-05-29_114503_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:38:33 | `docs/progress_reports/2026-05-29_113833_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:33:05 | `docs/progress_reports/2026-05-29_113305_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 11:19:18 | `docs/progress_reports/2026-05-29_111918_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:44:29 | `docs/progress_reports/2026-05-29_094429_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:38:51 | `docs/progress_reports/2026-05-29_093851_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:34:12 | `docs/progress_reports/2026-05-29_093412_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:32 | `docs/progress_reports/2026-05-29_0932_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:28 | `docs/progress_reports/2026-05-29_0928_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:26 | `docs/progress_reports/2026-05-29_0926_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:23 | `docs/progress_reports/2026-05-29_0923_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:21 | `docs/progress_reports/2026-05-29_0921_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:20 | `docs/progress_reports/2026-05-29_0920_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:11 | `docs/progress_reports/2026-05-29_0911_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:06 | `docs/progress_reports/2026-05-29_0906_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:04 | `docs/progress_reports/2026-05-29_0904_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:02 | `docs/progress_reports/2026-05-29_0902_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 09:00 | `docs/progress_reports/2026-05-29_0900_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 08:59 | `docs/progress_reports/2026-05-29_0859_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 08:48 | `docs/progress_reports/2026-05-29_0848_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 08:47 | `docs/progress_reports/2026-05-29_0847_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 08:44 | `docs/progress_reports/2026-05-29_0844_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:50 | `docs/progress_reports/2026-05-29_0550_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:48 | `docs/progress_reports/2026-05-29_0548_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:34 | `docs/progress_reports/2026-05-29_0534_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:25 | `docs/progress_reports/2026-05-29_0525_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:20 | `docs/progress_reports/2026-05-29_0520_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:15 | `docs/progress_reports/2026-05-29_0515_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:09 | `docs/progress_reports/2026-05-29_0509_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 05:04 | `docs/progress_reports/2026-05-29_0504_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 04:59 | `docs/progress_reports/2026-05-29_0459_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 04:58 | `docs/progress_reports/2026-05-29_0458_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 04:52 | `docs/progress_reports/2026-05-29_0452_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 04:30 | `docs/progress_reports/2026-05-29_0430_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:40 | `docs/progress_reports/2026-05-29_0340_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:31 | `docs/progress_reports/2026-05-29_0331_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:22 | `docs/progress_reports/2026-05-29_0322_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:15 | `docs/progress_reports/2026-05-29_0315_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:08 | `docs/progress_reports/2026-05-29_0308_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 03:03 | `docs/progress_reports/2026-05-29_0303_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:57 | `docs/progress_reports/2026-05-29_0257_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:52 | `docs/progress_reports/2026-05-29_0252_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:47 | `docs/progress_reports/2026-05-29_0247_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:40 | `docs/progress_reports/2026-05-29_0240_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:35 | `docs/progress_reports/2026-05-29_0235_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:31 | `docs/progress_reports/2026-05-29_0231_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:27 | `docs/progress_reports/2026-05-29_0227_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:22 | `docs/progress_reports/2026-05-29_0222_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:18 | `docs/progress_reports/2026-05-29_0218_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:15 | `docs/progress_reports/2026-05-29_0215_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:12 | `docs/progress_reports/2026-05-29_0212_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:10 | `docs/progress_reports/2026-05-29_0210_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:06 | `docs/progress_reports/2026-05-29_0206_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 02:01 | `docs/progress_reports/2026-05-29_0201_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:53 | `docs/progress_reports/2026-05-29_0153_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:49 | `docs/progress_reports/2026-05-29_0149_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:44 | `docs/progress_reports/2026-05-29_0144_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:40 | `docs/progress_reports/2026-05-29_0140_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:38 | `docs/progress_reports/2026-05-29_0138_mentor_brief.md` | 自动生成阶段汇报 |
| 2026-05-29 01:31 | `docs/progress_reports/2026-05-29_0131_mentor_brief.md` | 自动生成阶段汇报 |
