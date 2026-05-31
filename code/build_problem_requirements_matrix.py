from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "problem_requirements"
SOURCE_PDF = "CS-202614-电磁空间安全全国重点实验室-复杂航空载体电磁辐射空域特性测量技术比赛方案.pdf"


@dataclass
class RequirementItem:
    req_id: str
    source_page: str
    category: str
    requirement: str
    points: str
    current_status: str
    current_evidence: str
    missing_for_final: str
    owner_role: str
    next_action: str


@dataclass
class DeliverableItem:
    deliverable_id: str
    deliverable: str
    source_page: str
    final_expected_path: str
    current_source_path: str
    current_status: str
    final_blocker: str


def read_json(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def read_csv(path: str) -> pd.DataFrame:
    full = ROOT / path
    if not full.exists():
        return pd.DataFrame()
    return pd.read_csv(full, encoding="utf-8-sig")


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def status_from_submission(expected_path: str, submission_index: pd.DataFrame, fallback: str = "missing") -> str:
    if submission_index.empty:
        return fallback
    row = submission_index[submission_index["expected_path"].astype(str).eq(expected_path)]
    if row.empty:
        return fallback
    return str(row.iloc[0]["status"])


def metric(metrics: dict[str, Any], key: str, default: Any = 0) -> Any:
    value = metrics.get(key, default)
    return default if value is None else value


def build_requirement_items() -> list[RequirementItem]:
    metrics = read_json("outputs/scorecard/scorecard_metrics.json")
    completion = read_json("outputs/completion_audit/completion_audit_summary.json")
    submission_summary = read_json("outputs/submission_index/submission_index_summary.json")
    cst_dashboard = read_json("outputs/cst_execution_dashboard/cst_execution_dashboard_summary.json")
    report_summary = read_json("outputs/report_package/report_package_summary.json")
    presentation_summary = read_json("outputs/presentation_package/presentation_package_summary.json")
    operator_runbook = read_json("outputs/cst_operator_runbook/cst_operator_runbook_summary.json")
    level1_projects = read_json("outputs/cst_real_level1_projects/cst_automation_summary.json")

    literature_rows = int(metric(metrics, "literature_rows", 0))
    level1_required_complete = bool(metric(metrics, "level1_required_complete", False))
    level2_all_complete = bool(metric(metrics, "level2_all_complete", False))
    level2_complete_samples = int(metric(metrics, "level2_complete_samples", 0))
    level2_accuracy = metric(metrics, "level2_recognition_accuracy", "")
    level1_real_runs = int(metric(metrics, "level1_real_reconstruction_runs", 0))
    level1_real_min_corr = metric(metrics, "level1_real_min_correlation", "")
    level1_angular_runs = int(metric(metrics, "level1_angular_completed_runs", metric(metrics, "level1_angular_case_count", 0)))
    level1_angular_max_nmse = metric(metrics, "level1_angular_max_nmse", "")
    level1_angular_min_corr = metric(metrics, "level1_angular_min_correlation", "")
    level1_angular_max_lobe = metric(metrics, "level1_angular_max_main_lobe_error", "")
    structure_samples = int(metric(metrics, "structure_sample_count", 0) or 0)
    structure_cross_domain_accuracy = metric(metrics, "structure_cross_domain_accuracy", "")
    structure_mean_shadow_db = metric(metrics, "structure_mean_shadow_db", "")
    structure_p95_shadow_db = metric(metrics, "structure_p95_shadow_db", "")
    sensor_count = int(metric(metrics, "level1_workpack_sensor_count", 0))
    measurement_surface = str(metric(metrics, "level1_measurement_surface", "unknown"))
    submission_blocked = int(submission_summary.get("blocked", 999) or 0)
    missing_required_now = int(cst_dashboard.get("missing_required_now_files", 999) or 0)
    level1_projects_generated = bool(level1_projects.get("all_projects_created", False))
    level1_generated_project_count = int(level1_projects.get("projects_created", 0) or 0)
    report_final = bool(report_summary.get("is_final_report", False))
    slides_final = bool(presentation_summary.get("is_final_presentation", False))
    video_final = bool(presentation_summary.get("is_final_video", False))
    completion_proven = bool(completion.get("completion_proven", False))

    items = [
        RequirementItem(
            req_id="D1",
            source_page="p3, p5-p6",
            category="submission_deliverable",
            requirement="提交内容包括方案报告、PPT、视频/录屏、测试用例程序代码等；最终以压缩包报送。",
            points="submission gate",
            current_status="ready" if submission_blocked == 0 and report_final and slides_final and video_final else "partial",
            current_evidence="submission; outputs/submission_index/submission_package_index.md",
            missing_for_final=f"report_final={report_final}；slides_final={slides_final}；video_final={video_final}；submission blocked={submission_blocked}。",
            owner_role="C_docs",
            next_action="若 MP4 已生成，则人工播放复核并整理最终压缩包；否则先完成或录制演示视频。",
        ),
        RequirementItem(
            req_id="D2",
            source_page="p3",
            category="report_content",
            requirement="设计方案与仿真研究报告需覆盖调研、研究内容和技术路线、测试系统/重建算法、典型仿真测试结果。",
            points="report gate",
            current_status="ready" if report_final else "draft_evidence",
            current_evidence="docs/solution_report_draft.md; outputs/report_package/report_section_status.csv",
            missing_for_final=f"report_final={report_final}；blocked/demo sections={report_summary.get('blocked_or_demo_sections', 'unknown')}；正式报告文件见 submission/01_report。",
            owner_role="C_docs",
            next_action="在视频和最终压缩包中保持与正式报告一致的 Level 1/2 指标和边界表述。",
        ),
        RequirementItem(
            req_id="S1",
            source_page="p3",
            category="subjective_score",
            requirement="国内外发展调研分析情况。",
            points="10",
            current_status="draft_evidence" if literature_rows >= 20 else "incomplete",
            current_evidence=f"docs/literature_matrix.md；当前文献条目={literature_rows}。",
            missing_for_final="最终报告中需要统一参考文献格式并压缩成正式叙述。",
            owner_role="C_docs",
            next_action="把 literature matrix 转成正式参考文献表和方法谱系图。",
        ),
        RequirementItem(
            req_id="S2",
            source_page="p3",
            category="subjective_score",
            requirement="研究思路合理性。",
            points="10",
            current_status="evidence_ready_writeup_pending",
            current_evidence="docs/literature_to_algorithm_traceability.md; docs/solution_report_draft.md; outputs/master_dashboard; outputs/cst_level1_merge_report; outputs/cst_level2_merge_report; outputs/cst_structure_comparison",
            missing_for_final="Level 1/2 证据已到位，简化结构遮挡对照已补充；报告中还需统一 solver-safe、element-library、简化结构对照与 full-wave 边界说明。",
            owner_role="A_algorithm + C_docs",
            next_action="把 G2/G3/G4 当前指标写入报告并解释方法迁移边界。",
        ),
        RequirementItem(
            req_id="S3",
            source_page="p3",
            category="subjective_score",
            requirement="技术路线可行性。",
            points="10",
            current_status="model_risk_bounded",
            current_evidence="docs/phase_01_cst_technical_route_and_division.md; outputs/cst_operator_runbook; outputs/cst_execution_dashboard; outputs/cst_real_level1_projects; outputs/cst_level1_reconstruction_batch; outputs/cst_level1_angular_calibration; outputs/cst_recognition_level2; outputs/cst_structure_comparison",
            missing_for_final=(
                f"CST-Python 工程生成与 Level 2 full48 已完成；Level 1 角域校准 {level1_angular_runs} 个案例 "
                f"max NMSE={level1_angular_max_nmse}、min corr={level1_angular_min_corr}；"
                f"简化结构对照 {structure_samples} 个样本，cross-domain accuracy={structure_cross_domain_accuracy}；"
                "但 full-wave 近场等效源反演和 full-wave airframe 结构散射仍需边界说明。"
            ),
            owner_role="A_algorithm + B_CST",
            next_action="把角域校准、近场等效源风险和简化结构遮挡对照写入报告；时间允许时再补 full-wave airframe 对照。",
        ),
        RequirementItem(
            req_id="S4",
            source_page="p3",
            category="subjective_score",
            requirement="测试方案完整性。",
            points="10",
            current_status="screenshots_pending" if level1_projects_generated else "needs_real_cst_evidence",
            current_evidence="outputs/cst_level1_workpack; outputs/cst_level2_workpack; outputs/cst_macro_templates; outputs/cst_operator_runbook; outputs/cst_real_level1_projects",
            missing_for_final="Level 1/2 数据证据与简化结构对照已补齐；最终报告仍需 CST 参数截图、结构对照图和测试日志整理。",
            owner_role="B_CST + C_docs",
            next_action="补齐 CST 工程截图、执行日志、导出 CSV 和报告中的测试结果。",
        ),
        RequirementItem(
            req_id="O1",
            source_page="p4",
            category="objective_score",
            requirement="多角度、多极化传感单元快速布设；覆盖 2π 半柱面或半球面；可容纳不小于 12m x 10m x 8m。",
            points="10",
            current_status="ready" if level1_projects_generated and level2_all_complete else "needs_cst_project_proof",
            current_evidence=(
                f"outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv；surface={measurement_surface}；"
                f"sensor_count={sensor_count}；outputs/cst_operator_runbook/cst_probe_points_hemisphere_162.csv；"
                f"outputs/cst_real_level1_projects/projects。"
            ),
            missing_for_final="工程证明已具备；最终报告仍需要 CST 截图展示 probe layout、boundary 和 monitor。",
            owner_role="B_CST",
            next_action="在 Level 1 required CST 工程中保存 probe layout、boundary、monitor 截图。",
        ),
        RequirementItem(
            req_id="O2",
            source_page="p4",
            category="objective_score",
            requirement="基于电磁传播与等效原理进行三维场域重建；用典型辐射源远场重建精度验证；尽量减少测量点数。",
            points="30",
            current_status="model_risk_bounded" if level1_required_complete and level1_angular_runs > 0 else "missing_real_cst",
            current_evidence="outputs/cst_real_level1_projects; outputs/cst_level1_merge_report; outputs/cst_level1_reconstruction_batch; outputs/cst_level1_angular_calibration; outputs/reconstruction_robustness; outputs/level1_analytic_reference",
            missing_for_final=(
                f"Level 1 required 已完成 strict audit 和 {level1_real_runs} 个重建；"
                f"等效源反演最小相关系数={level1_real_min_corr}；"
                f"FarfieldPlot-derived 角域校准 max NMSE={level1_angular_max_nmse}、"
                f"min corr={level1_angular_min_corr}、max 主瓣误差={level1_angular_max_lobe} deg。"
            ),
            owner_role="A_algorithm + B_CST",
            next_action="最终报告中区分角域高一致性和 full-wave 近场等效源模型风险。",
        ),
        RequirementItem(
            req_id="O3",
            source_page="p4",
            category="objective_score",
            requirement="提取具有载体唯一性和稳定性的空间-频谱辐射特征，区分不同载体及运行状态；典型辐射源辨识精度不低于 85%。",
            points="20",
            current_status="ready" if level2_all_complete and float(level2_accuracy or 0.0) >= 0.85 else "missing_real_cst",
            current_evidence="outputs/cst_level2_merge_report; outputs/cst_recognition_level2; outputs/cst_recognition_level2_ablation; outputs/cst_level2_workpack; outputs/cst_structure_comparison",
            missing_for_final=(
                f"Level 2 完整样本={level2_complete_samples}/48；accuracy={level2_accuracy}；"
                f"简化结构对照样本={structure_samples}，平均遮挡={structure_mean_shadow_db} dB，"
                f"P95 遮挡={structure_p95_shadow_db} dB，cross-domain accuracy={structure_cross_domain_accuracy}；"
                "full-wave airframe 结构散射仍是可选增强项。"
            ),
            owner_role="A_algorithm + B_CST",
            next_action="把混淆矩阵、消融曲线、element-library 假设和简化结构遮挡对照写入报告。",
        ),
        RequirementItem(
            req_id="T1",
            source_page="p4-p5",
            category="schedule",
            requirement="2026 年 9 月 15 日前通过大赛申报系统提交作品；2026 年 5 月至 9 月上旬开展研发攻关。",
            points="schedule gate",
            current_status="human_admin_pending",
            current_evidence="docs/final_submission_package_plan.md; outputs/master_dashboard",
            missing_for_final="需要队伍在申报系统和邮箱提交前完成人工信息、学校名称、队名、联系人等最终填充。",
            owner_role="C_docs",
            next_action="最终压缩包生成后按学校/申报人/作品名称/联系电话命名并提交。",
        ),
        RequirementItem(
            req_id="T2",
            source_page="p5-p6",
            category="submission_method",
            requirement="作品以压缩包报送至指定邮箱；邮件主题和压缩包命名需包含赛题名称、学校、申报人等信息。",
            points="submission gate",
            current_status="human_admin_pending",
            current_evidence="docs/final_submission_package_plan.md",
            missing_for_final="学校全称、申报人姓名、联系电话、最终作品名称和审核通过报名表尚未填入。",
            owner_role="C_docs",
            next_action="提交前由队伍填入真实身份信息并附报名表扫描件。",
        ),
        RequirementItem(
            req_id="G0",
            source_page="workspace audit",
            category="completion_control",
            requirement="只有所有赛题要求、真实 CST 证据和最终交付物都被证明后，才能判定总目标完成。",
            points="internal gate",
            current_status="ready" if completion_proven else "not_complete",
            current_evidence=f"outputs/completion_audit/completion_audit_summary.json；completion_proven={completion_proven}。",
            missing_for_final="completion_proven=true 时总目标证据链已闭合；仍需人工播放视频、核对报名信息和最终压缩包命名。",
            owner_role="A_algorithm + B_CST + C_docs",
            next_action="按 master dashboard 的 priority 队列推进。",
        ),
    ]
    if operator_runbook:
        items[7].current_evidence += f"; operator_runbook_probe_points={operator_runbook.get('probe_point_count')}"
    return items


def build_deliverables() -> list[DeliverableItem]:
    submission_index = read_csv("outputs/submission_index/submission_checklist.csv")
    level1_projects = read_json("outputs/cst_real_level1_projects/cst_automation_summary.json")
    level1_projects_generated = bool(level1_projects.get("all_projects_created", False))
    rows = [
        DeliverableItem(
            "DL1",
            "方案报告 PDF",
            "p3, p5-p6",
            "submission/01_report/solution_report.pdf",
            "docs/solution_report_draft.md",
            status_from_submission("submission/01_report/solution_report.pdf", submission_index, "draft/source ready"),
            "正式 PDF 已生成时状态为 ready；后续只需随最终视频和压缩包审计同步复核。",
        ),
        DeliverableItem(
            "DL2",
            "方案报告 DOCX",
            "p3, p5-p6",
            "submission/01_report/solution_report.docx",
            "docs/solution_report_draft.md",
            status_from_submission("submission/01_report/solution_report.docx", submission_index, "draft/source ready"),
            "正式 DOCX 已生成时状态为 ready；后续只需随最终视频和压缩包审计同步复核。",
        ),
        DeliverableItem(
            "DL3",
            "答辩 PPT/PDF",
            "p3, p5-p6",
            "submission/02_presentation/defense_slides.pptx; submission/02_presentation/defense_slides.pdf",
            "outputs/presentation_package; outputs/presentation_artifact",
            status_from_submission("submission/02_presentation/defense_slides.pptx", submission_index, "draft/source ready"),
            "PPTX/PDF 已生成时状态为 ready；仍需与最终视频口径保持一致。",
        ),
        DeliverableItem(
            "DL4",
            "视频/录屏",
            "p3, p5-p6",
            "submission/03_video/demo_video.mp4",
            "outputs/presentation_package/demo_video_storyboard.md",
            status_from_submission("submission/03_video/demo_video.mp4", submission_index, "draft/source ready"),
            "MP4 已生成时状态为 ready；当前自动生成版本需人工播放确认，若竞赛要求讲解录屏可替换为带人工讲解版本。",
        ),
        DeliverableItem(
            "DL5",
            "测试用例程序代码",
            "p3, p5-p6",
            "submission/04_code/src",
            "code",
            status_from_submission("submission/04_code/src", submission_index, "ready"),
            "最终提交前需复核真实数据路径和 requirements。",
        ),
        DeliverableItem(
            "DL6",
            "CST 工程与真实导出",
            "p4",
            "submission/05_cst/level1_standard_sources; submission/05_cst/level2_multisource",
            "outputs/cst_real_level1_projects; outputs/cst_operator_runbook; outputs/cst_level1_workpack; outputs/cst_level2_workpack",
            "draft/source ready" if level1_projects_generated else "blocked",
            "Level 1/2 数据和简化结构对照已到位；复杂载体 full-wave 结构对照可作为增强项，最终截图仍需补充。",
        ),
        DeliverableItem(
            "DL7",
            "最终压缩包与报名表",
            "p5-p6",
            "CS-202614_submission.zip",
            "submission",
            "human_admin_pending",
            "需要队伍补充学校、申报人、电话、报名表扫描件并按要求发送。",
        ),
    ]
    return rows


def write_markdown(req_df: pd.DataFrame, dlv_df: pd.DataFrame, out_dir: Path) -> None:
    status_counts = req_df["current_status"].value_counts().to_dict()
    req_rows = "\n".join(
        (
            f"| {row.req_id} | {row.category} | {row.source_page} | {row.points} | "
            f"{row.current_status} | {row.current_evidence} | {row.missing_for_final} |"
        )
        for row in req_df.itertuples(index=False)
    )
    dlv_rows = "\n".join(
        (
            f"| {row.deliverable_id} | {row.deliverable} | `{row.final_expected_path}` | "
            f"`{row.current_source_path}` | {row.current_status} | {row.final_blocker} |"
        )
        for row in dlv_df.itertuples(index=False)
    )
    content = f"""# Problem requirements matrix

Source document: `{SOURCE_PDF}`

This matrix maps the problem statement to current project evidence. It is conservative: demo/synthetic outputs prove pipeline readiness only, not final contest completion.

## Status Counts

| Status | Count |
|---|---:|
"""
    for status, count in sorted(status_counts.items()):
        content += f"| {status} | {count} |\n"
    content += f"""
## Requirement Matrix

| ID | Category | Source | Points | Status | Current evidence | Missing for final |
|---|---|---|---|---|---|---|
{req_rows}

## Deliverable Checklist

| ID | Deliverable | Final expected path | Current source | Status | Final blocker |
|---|---|---|---|---|---|
{dlv_rows}

## Immediate Implication

The next evidence that can move multiple requirements at once is final reporting plus the remaining metric-risk/structure-risk treatment:

```powershell
python code\\build_scorecard.py
python code\\build_completion_audit.py
python code\\build_master_dashboard.py
```

Before final submission, update the report/PPT/video with the latest Level 1/2 metrics, explain the Level 1 angular-calibration versus near-field model boundary, and write the simplified structure/occlusion comparison as bounded evidence rather than full-wave airframe proof.
"""
    (out_dir / "problem_requirements_matrix.md").write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    requirements = build_requirement_items()
    deliverables = build_deliverables()
    req_df = pd.DataFrame([asdict(item) for item in requirements])
    dlv_df = pd.DataFrame([asdict(item) for item in deliverables])
    req_df.to_csv(OUT / "problem_requirements_matrix.csv", index=False, encoding="utf-8-sig")
    dlv_df.to_csv(OUT / "problem_deliverable_checklist.csv", index=False, encoding="utf-8-sig")
    write_markdown(req_df, dlv_df, OUT)

    objective_points = req_df[req_df["category"].eq("objective_score")]["points"].astype(int).sum()
    subjective_points = req_df[req_df["category"].eq("subjective_score")]["points"].astype(int).sum()
    completion_summary = read_json("outputs/completion_audit/completion_audit_summary.json")
    completion_proven_final = bool(completion_summary.get("completion_proven", False))
    blocked_or_missing_count = int(
        req_df["current_status"].isin(["missing_real_cst", "needs_real_cst_evidence", "needs_cst_project_proof", "not_complete"]).sum()
    )
    summary = {
        "out_dir": "outputs\\problem_requirements",
        "source_pdf": SOURCE_PDF,
        "requirement_count": int(len(req_df)),
        "deliverable_count": int(len(dlv_df)),
        "subjective_points": int(subjective_points),
        "objective_points": int(objective_points),
        "total_scored_points": int(subjective_points + objective_points),
        "not_final_status_count": int(req_df["current_status"].ne("ready").sum()),
        "blocked_or_missing_count": blocked_or_missing_count,
        "is_final": completion_proven_final and blocked_or_missing_count == 0,
        "completion_proven": completion_proven_final,
    }
    (OUT / "problem_requirements_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Problem requirements matrix written to {OUT}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
