# Problem requirements matrix

Source document: `CS-202614-电磁空间安全全国重点实验室-复杂航空载体电磁辐射空域特性测量技术比赛方案.pdf`

This matrix maps the problem statement to current project evidence. It is conservative: demo/synthetic outputs prove pipeline readiness only, not final contest completion.

## Status Counts

| Status | Count |
|---|---:|
| draft_evidence | 1 |
| evidence_ready_writeup_pending | 1 |
| human_admin_pending | 2 |
| model_risk_bounded | 2 |
| ready | 5 |
| screenshots_pending | 1 |

## Requirement Matrix

| ID | Category | Source | Points | Status | Current evidence | Missing for final |
|---|---|---|---|---|---|---|
| D1 | submission_deliverable | p3, p5-p6 | submission gate | ready | submission; outputs/submission_index/submission_package_index.md | report_final=True；slides_final=True；video_final=True；submission blocked=0。 |
| D2 | report_content | p3 | report gate | ready | docs/solution_report_draft.md; outputs/report_package/report_section_status.csv | report_final=True；blocked/demo sections=0；正式报告文件见 submission/01_report。 |
| S1 | subjective_score | p3 | 10 | draft_evidence | docs/literature_matrix.md；当前文献条目=25。 | 最终报告中需要统一参考文献格式并压缩成正式叙述。 |
| S2 | subjective_score | p3 | 10 | evidence_ready_writeup_pending | docs/literature_to_algorithm_traceability.md; docs/solution_report_draft.md; outputs/master_dashboard; outputs/cst_level1_merge_report; outputs/cst_level2_merge_report; outputs/cst_structure_comparison | Level 1/2 证据已到位，简化结构遮挡对照已补充；报告中还需统一 solver-safe、element-library、简化结构对照与 full-wave 边界说明。 |
| S3 | subjective_score | p3 | 10 | model_risk_bounded | docs/phase_01_cst_technical_route_and_division.md; outputs/cst_operator_runbook; outputs/cst_execution_dashboard; outputs/cst_real_level1_projects; outputs/cst_level1_reconstruction_batch; outputs/cst_level1_angular_calibration; outputs/cst_recognition_level2; outputs/cst_structure_comparison | CST-Python 工程生成与 Level 2 full48 已完成；Level 1 角域校准 2 个案例 max NMSE=8.40556336030498e-05、min corr=0.9998782818365388；简化结构对照 48 个样本，cross-domain accuracy=1.0；但 full-wave 近场等效源反演和 full-wave airframe 结构散射仍需边界说明。 |
| S4 | subjective_score | p3 | 10 | screenshots_pending | outputs/cst_level1_workpack; outputs/cst_level2_workpack; outputs/cst_macro_templates; outputs/cst_operator_runbook; outputs/cst_real_level1_projects | Level 1/2 数据证据与简化结构对照已补齐；最终报告仍需 CST 参数截图、结构对照图和测试日志整理。 |
| O1 | objective_score | p4 | 10 | ready | outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv；surface=2pi_upper_hemisphere；sensor_count=162；outputs/cst_operator_runbook/cst_probe_points_hemisphere_162.csv；outputs/cst_real_level1_projects/projects。 | 工程证明已具备；最终报告仍需要 CST 截图展示 probe layout、boundary 和 monitor。 |
| O2 | objective_score | p4 | 30 | model_risk_bounded | outputs/cst_real_level1_projects; outputs/cst_level1_merge_report; outputs/cst_level1_reconstruction_batch; outputs/cst_level1_angular_calibration; outputs/reconstruction_robustness; outputs/level1_analytic_reference; operator_runbook_probe_points=162 | Level 1 required 已完成 strict audit 和 2 个重建；等效源反演最小相关系数=0.3665721711770728；FarfieldPlot-derived 角域校准 max NMSE=8.40556336030498e-05、min corr=0.9998782818365388、max 主瓣误差=0.0 deg。 |
| O3 | objective_score | p4 | 20 | ready | outputs/cst_level2_merge_report; outputs/cst_recognition_level2; outputs/cst_recognition_level2_ablation; outputs/cst_level2_workpack; outputs/cst_structure_comparison | Level 2 完整样本=48/48；accuracy=1.0；简化结构对照样本=48，平均遮挡=3.059749694260782 dB，P95 遮挡=6.632975065705098 dB，cross-domain accuracy=1.0；full-wave airframe 结构散射仍是可选增强项。 |
| T1 | schedule | p4-p5 | schedule gate | human_admin_pending | docs/final_submission_package_plan.md; outputs/master_dashboard | 需要队伍在申报系统和邮箱提交前完成人工信息、学校名称、队名、联系人等最终填充。 |
| T2 | submission_method | p5-p6 | submission gate | human_admin_pending | docs/final_submission_package_plan.md | 学校全称、申报人姓名、联系电话、最终作品名称和审核通过报名表尚未填入。 |
| G0 | completion_control | workspace audit | internal gate | ready | outputs/completion_audit/completion_audit_summary.json；completion_proven=True。 | completion_proven=true 时总目标证据链已闭合；仍需人工播放视频、核对报名信息和最终压缩包命名。 |

## Deliverable Checklist

| ID | Deliverable | Final expected path | Current source | Status | Final blocker |
|---|---|---|---|---|---|
| DL1 | 方案报告 PDF | `submission/01_report/solution_report.pdf` | `docs/solution_report_draft.md` | ready | 正式 PDF 已生成时状态为 ready；后续只需随最终视频和压缩包审计同步复核。 |
| DL2 | 方案报告 DOCX | `submission/01_report/solution_report.docx` | `docs/solution_report_draft.md` | ready | 正式 DOCX 已生成时状态为 ready；后续只需随最终视频和压缩包审计同步复核。 |
| DL3 | 答辩 PPT/PDF | `submission/02_presentation/defense_slides.pptx; submission/02_presentation/defense_slides.pdf` | `outputs/presentation_package; outputs/presentation_artifact` | ready | PPTX/PDF 已生成时状态为 ready；仍需与最终视频口径保持一致。 |
| DL4 | 视频/录屏 | `submission/03_video/demo_video.mp4` | `outputs/presentation_package/demo_video_storyboard.md` | ready | MP4 已生成时状态为 ready；当前自动生成版本需人工播放确认，若竞赛要求讲解录屏可替换为带人工讲解版本。 |
| DL5 | 测试用例程序代码 | `submission/04_code/src` | `src` | ready | 最终提交前需复核真实数据路径和 requirements。 |
| DL6 | CST 工程与真实导出 | `submission/05_cst/level1_standard_sources; submission/05_cst/level2_multisource` | `outputs/cst_real_level1_projects; outputs/cst_operator_runbook; outputs/cst_level1_workpack; outputs/cst_level2_workpack` | draft/source ready | Level 1/2 数据和简化结构对照已到位；复杂载体 full-wave 结构对照可作为增强项，最终截图仍需补充。 |
| DL7 | 最终压缩包与报名表 | `CS-202614_submission.zip` | `submission` | human_admin_pending | 需要队伍补充学校、申报人、电话、报名表扫描件并按要求发送。 |

## Immediate Implication

The next evidence that can move multiple requirements at once is final reporting plus the remaining metric-risk/structure-risk treatment:

```powershell
python src\build_scorecard.py
python src\build_completion_audit.py
python src\build_master_dashboard.py
```

Before final submission, update the report/PPT/video with the latest Level 1/2 metrics, explain the Level 1 angular-calibration versus near-field model boundary, and write the simplified structure/occlusion comparison as bounded evidence rather than full-wave airframe proof.
