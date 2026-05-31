# Master status dashboard

This dashboard summarizes the whole CS-202614 workspace. It is a project-control artifact, not simulation evidence.

## Current Verdict

| Item | Current value |
|---|---|
| Completion proven | `true` |
| Next blocking gate | `` |
| Gate counts | complete=8, partial=0, missing=0 |
| Submission index | ready=65, draft/source=2, blocked=0, missing=0 |
| Problem requirements | `12` requirements / `100` scored points |
| Problem gaps | `0` blocked or missing evidence items |
| Measurement surface | `2pi_upper_hemisphere` |
| Hemisphere sensor count | `162` |
| Level 1 required complete | `True` |
| Level 2 complete samples | `48/48` |
| Level 2 structure comparison samples | `48` |
| Level 2 structure mean/P95 shadow | `3.059749694260782` / `6.632975065705098` dB |
| Level 2 structure cross-domain accuracy | `1.0` |
| CST required-now missing files | `0` |
| Level 2 pilot missing files | `0` |
| Report final | `True` |
| Presentation/video final | `True` / `True` |

## Gate Summary

| Gate | Status | Owner | Requirement | Next action |
|---|---|---|---|---|
| G0 | complete | C_docs | 文献调研、技术路线和方案骨架可支撑报告写作 | 真实 CST 结果完成后，把文献矩阵转成正式参考文献表并校对引用。 |
| G1 | complete | B_CST | 半球面 2π 测量布局固定并可交给 CST 执行 | 在已生成的 outputs/cst_real_level1_projects/projects 工程中运行求解并保存 monitor/export 截图。 |
| G2 | complete | B_CST + A_algorithm | Level 1 标准源真实 CST required 案例通过审计和重建 | 复核 Level 1 solver-safe FarfieldPlot 与重建模型的一致性。 |
| G2-demo | complete | A_algorithm | Level 1 Python 接口、审计和批量重建非空链路已预演 | 真实 CST 文件到位后，复用同一审计和批量重建命令。 |
| G3 | complete | B_CST + A_algorithm | Level 2 多源多状态真实 CST 数据完整并可训练识别模型 | 保留 full48 strict merge、recognition/ablation 与结构遮挡对照结果，并写入报告/PPT。 |
| G4 | complete | A_algorithm + C_docs | 真实 CST 重建和识别结果替换所有 demo/synthetic 指标 | 把 Level 1 角域高一致性、近场等效源模型边界和 Level 2 简化结构遮挡对照写入报告。 |
| G5 | complete | C_docs | 最终报告 PDF/DOCX、答辩 PPT、演示视频已生成 | 人工播放检查 demo_video.mp4；若竞赛要求讲解录屏，优先替换为带人工讲解或可听旁白的版本。 |
| G6 | complete | C_docs | 最终提交包无 blocked 项 | 消除 submission index 中剩余 blocked 项，并生成最终 PDF/DOCX/PPTX/MP4。 |

## Next Action Queue

| Priority | Owner | Gate | Action | Proof to close |
|---:|---|---|---|---|
| 1 | C_docs | FINAL | 人工完整播放 submission/03_video/demo_video.mp4。 | 视频播放无黑屏、卡顿、错页；若竞赛要求讲解录屏，则替换并重跑审计。 |
| 2 | C_docs | FINAL | 整理最终压缩包命名、报名表和人工提交信息。 | 压缩包目录与赛题命名规则一致，人工信息补齐。 |

## Team Split

| Role | Responsibility |
|---|---|
| A_algorithm | 审计真实 CST 导出、运行 Level 1 重建、Level 2 识别/删减、更新指标。 |
| B_CST | 在 CST 中完成模型、monitor、半球面测点、nearfield/farfield 导出和截图。 |
| C_docs | 把真实证据写入报告、PPT、视频脚本、scorecard 和提交草稿包。 |

## Key Files

| Artifact | Path | Meaning |
|---|---|---|
| Master dashboard | `outputs/master_dashboard/master_status_dashboard.md` | 一页式总状态、当前阻塞门、三人任务队列入口。 |
| Completion audit | `outputs/completion_audit/completion_audit.md` | 是否完成赛题的保守 gate 判断。 |
| Problem requirements matrix | `outputs/problem_requirements/problem_requirements_matrix.md` | 赛题原文要求、100 分评分项、交付物和当前证据的一一映射。 |
| CST execution dashboard | `outputs/cst_execution_dashboard/cst_execution_dashboard.md` | 真实 CST required/pilot 导出任务和 dropzone 规则。 |
| CST operator runbook | `outputs/cst_operator_runbook/README_cst_operator_runbook.md` | G2 两个 required 标准源的 CST 真机操作包、探针点、远场网格和导出合同。 |
| CST Level 1 generated projects | `outputs/cst_real_level1_projects/README_cst_level1_automation.md` | 通过本机 CST API 生成的两个 Level 1 required .cst 工程、VBA history 和生成日志。 |
| CST Level 1 angular calibration | `outputs/cst_level1_angular_calibration/README_cst_level1_angular_calibration.md` | FarfieldPlot-derived solver-safe Level 1 导出的角域一致性校准和模型边界说明。 |
| CST Level 2 simplified structure comparison | `outputs/cst_structure_comparison/README_cst_structure_comparison.md` | 基于 Level 2 CST-derived 数据的简化载体遮挡/安装效应对照、方向图偏差和 cross-domain 识别稳健性。 |
| Submission index | `outputs/submission_index/submission_package_index.md` | 最终提交物 readiness/blocker 索引。 |
| Report package | `outputs/report_package/README_report_package.md` | 报告章节、图表和替换任务。 |
| Presentation package | `outputs/presentation_package/README_presentation_package.md` | 答辩 PPT storyboard、视频分镜和展示素材缺口。 |
| Scorecard | `outputs/scorecard/scorecard.md` | 评分项证据板。 |

## Immediate Command Sequence

```powershell
python src\build_scorecard.py
python src\build_problem_requirements_matrix.py
python src\build_submission_index.py
python src\build_completion_audit.py
python src\build_master_dashboard.py
python src\build_submission_draft.py
```

After final report/PPT/video generation, rerun this sequence and confirm `completion_proven=true`.
