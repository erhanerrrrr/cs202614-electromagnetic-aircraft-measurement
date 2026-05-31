from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "completion_audit"


@dataclass
class AuditItem:
    gate: str
    requirement: str
    status: str
    evidence: str
    missing_or_risk: str
    next_action: str


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def read_json(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8-sig"))


def read_csv(path: str) -> pd.DataFrame:
    full = ROOT / path
    if not full.exists():
        return pd.DataFrame()
    return pd.read_csv(full, encoding="utf-8-sig")


def status_from_bool(ok: bool, partial: bool = False) -> str:
    if ok:
        return "complete"
    if partial:
        return "partial"
    return "missing"


def build_audit_items() -> list[AuditItem]:
    score_items = read_csv("outputs/scorecard/score_items.csv")
    submission = read_csv("outputs/submission_index/submission_checklist.csv")
    metrics = read_json("outputs/scorecard/scorecard_metrics.json")
    level1_merge = read_json("outputs/cst_level1_merge_report/level1_merge_summary.json")
    level2_merge = read_json("outputs/cst_level2_merge_report/level2_merge_summary.json")
    level1_projects = read_json("outputs/cst_real_level1_projects/cst_automation_summary.json")
    synthetic_level1 = read_json("outputs/synthetic_cst_level1_dataset/reconstruction_batch/level1_batch_reconstruction_summary.json")
    level1_angular = read_json("outputs/cst_level1_angular_calibration/angular_calibration_summary.json")
    structure_summary = read_json("outputs/cst_structure_comparison/structure_comparison_summary.json")
    video_summary = read_json("outputs/video_artifact/demo_video_summary.json")

    report_source_ready = exists("docs/solution_report_draft.md")
    report_final_ready = exists("submission/01_report/solution_report.pdf") and exists("submission/01_report/solution_report.docx")
    ppt_ready = exists("submission/02_presentation/defense_slides.pptx") and exists("submission/02_presentation/defense_slides.pdf")
    video_ready = exists("submission/03_video/demo_video.mp4")
    final_missing = [
        name
        for name, ok in [
            ("solution_report.pdf", exists("submission/01_report/solution_report.pdf")),
            ("solution_report.docx", exists("submission/01_report/solution_report.docx")),
            ("defense_slides.pptx", exists("submission/02_presentation/defense_slides.pptx")),
            ("defense_slides.pdf", exists("submission/02_presentation/defense_slides.pdf")),
            ("demo_video.mp4", video_ready),
        ]
        if not ok
    ]
    final_missing_text = ", ".join(final_missing) if final_missing else "none"
    video_note = str(video_summary.get("qa_note", ""))
    video_has_narration = bool(video_summary.get("has_narration", False))

    core_score_needs_cst = int(score_items["status"].astype(str).eq("Needs CST evidence").sum()) if not score_items.empty else 999
    metric_risk_items = int(score_items["status"].astype(str).str.contains("metric risk", case=False, na=False).sum()) if not score_items.empty else 999
    model_risk_items = int(score_items["status"].astype(str).str.contains("model risk", case=False, na=False).sum()) if not score_items.empty else 999
    blocked_artifacts = int(submission["status"].astype(str).eq("blocked").sum()) if not submission.empty else 999

    level1_required_complete = bool(level1_merge.get("required_complete", False))
    level1_projects_generated = (
        bool(level1_projects.get("all_projects_created", False))
        and int(level1_projects.get("projects_created", 0) or 0) >= 2
    )
    level2_all_complete = bool(level2_merge.get("all_complete", False))
    level2_complete_samples = int(level2_merge.get("complete_samples", 0) or 0)
    synthetic_level1_ok = int(synthetic_level1.get("completed_runs", 0) or 0) >= 6
    level1_angular_ok = (
        int(level1_angular.get("case_count", 0) or 0) >= 2
        and float(level1_angular.get("max_nmse", 999.0) or 999.0) <= 1e-2
        and float(level1_angular.get("min_correlation", 0.0) or 0.0) >= 0.95
    )
    structure_comparison_ok = (
        int(structure_summary.get("sample_count", 0) or 0) >= 48
        and float(structure_summary.get("cross_domain_accuracy", 0.0) or 0.0) >= 0.85
    )

    items = [
        AuditItem(
            gate="G0",
            requirement="文献调研、技术路线和方案骨架可支撑报告写作",
            status=status_from_bool(exists("docs/literature_matrix.md") and exists("docs/solution_report_draft.md")),
            evidence="docs/literature_matrix.md; docs/literature_screening_and_strategy.md; docs/solution_report_draft.md; outputs/problem_requirements/problem_requirements_matrix.md",
            missing_or_risk="参考文献最终格式和真实 CST 结果引用仍需成稿时统一。",
            next_action="真实 CST 结果完成后，把文献矩阵转成正式参考文献表并校对引用。",
        ),
        AuditItem(
            gate="G1",
            requirement="半球面 2π 测量布局固定并可交给 CST 执行",
            status=status_from_bool(
                exists("outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv")
                and int(metrics.get("level1_workpack_sensor_count", 0) or 0) == 162
            ),
            evidence="outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv; outputs/cst_level1_workpack; outputs/cst_level2_workpack; outputs/cst_real_level1_projects",
            missing_or_risk="已生成含 162 个半球面探针的 Level 1 CST 工程；仍需求解后截图和导出证明。",
            next_action="在已生成的 outputs/cst_real_level1_projects/projects 工程中运行求解并保存 monitor/export 截图。",
        ),
        AuditItem(
            gate="G2",
            requirement="Level 1 标准源真实 CST required 案例通过审计和重建",
            status=status_from_bool(level1_required_complete, partial=level1_projects_generated),
            evidence="outputs/cst_real_level1_projects; outputs/cst_level1_merge_report/level1_merge_summary.json; outputs/cst_level1_reconstruction_batch",
            missing_or_risk=(
                "Level 1 required 已完成；但重建精度偏低，需在 G4/报告中处理。"
                if level1_required_complete
                else
                "真实 CST 工程已生成，但 nearfield/farfield CSV 导出尚未到位；当前 required_complete=false。"
                if level1_projects_generated and not level1_required_complete
                else "真实 CST 导出尚未到位；当前 required_complete=false。"
                if not level1_required_complete
                else ""
            ),
            next_action=(
                "复核 Level 1 solver-safe FarfieldPlot 与重建模型的一致性。"
                if level1_required_complete
                else "打开/批处理 outputs/cst_real_level1_projects/projects 中两个工程，完成求解并导出 Level 1 nearfield/farfield CSV。"
            ),
        ),
        AuditItem(
            gate="G2-demo",
            requirement="Level 1 Python 接口、审计和批量重建非空链路已预演",
            status=status_from_bool(synthetic_level1_ok),
            evidence="outputs/synthetic_cst_level1_dataset/validation_report.json; outputs/synthetic_cst_level1_dataset/reconstruction_batch",
            missing_or_risk="该项是 synthetic surrogate，只证明接口可用，不能替代 CST 评分证据。",
            next_action="真实 CST 文件到位后，复用同一审计和批量重建命令。",
        ),
        AuditItem(
            gate="G3",
            requirement="Level 2 多源多状态真实 CST 数据完整并可训练识别模型",
            status=status_from_bool(level2_all_complete, partial=level2_complete_samples > 0),
            evidence="outputs/cst_level2_merge_report/level2_merge_summary.json; outputs/cst_level2_workpack; outputs/cst_level2_plan",
            missing_or_risk=(
                (
                    "48 样本已完整；当前为 CST-derived element-library 叠加证据，且简化结构遮挡对照已给出安装效应敏感性；"
                    "full-wave airframe 结构散射仍是可选增强项。"
                    if structure_comparison_ok
                    else "48 样本已完整；当前为 CST-derived element-library 叠加证据，复杂载体结构对照仍是后续风险项。"
                )
                if level2_all_complete
                else f"当前完整样本为 {level2_complete_samples}/48，不能证明 accuracy >= 85%。"
            ),
            next_action=(
                (
                    "保留 full48 strict merge、recognition/ablation 与结构遮挡对照结果，并写入报告/PPT。"
                    if structure_comparison_ok
                    else "保留 full48 strict merge 与 recognition/ablation 结果，并补充结构散射对照。"
                )
                if level2_all_complete
                else "按 outputs/cst_level2_workpack 分批完成 48 个样本导出并运行 merge/recognition。"
            ),
        ),
        AuditItem(
            gate="G4",
            requirement="真实 CST 重建和识别结果替换所有 demo/synthetic 指标",
            status=status_from_bool(core_score_needs_cst == 0),
            evidence="outputs/scorecard/score_items.csv; outputs/scorecard/scorecard.md",
            missing_or_risk=(
                (
                    "已替换 demo/synthetic 主证据；Level 1 角域校准已把 solver-safe FarfieldPlot-derived "
                    f"数据一致性风险降为模型边界说明；结构遮挡对照 ready={structure_comparison_ok}；"
                    f"仍有 {model_risk_items} 个评分项存在 model risk。"
                    if level1_angular_ok
                    else f"已替换 demo/synthetic 主证据；但仍有 {metric_risk_items} 个评分项存在 metric risk。"
                )
                if core_score_needs_cst == 0
                else f"当前仍有 {core_score_needs_cst} 个评分项标记为 Needs CST evidence。"
            ),
            next_action=(
                (
                    "把 Level 1 角域高一致性、近场等效源模型边界和 Level 2 简化结构遮挡对照写入报告。"
                    if level1_angular_ok
                    else "继续处理 Level 1 重建精度和复杂载体结构对照风险。"
                )
                if core_score_needs_cst == 0
                else "完成真实 Level 1/2 后重新运行 build_scorecard.py，并逐项检查不再依赖 demo 证据。"
            ),
        ),
        AuditItem(
            gate="G5",
            requirement="最终报告 PDF/DOCX、答辩 PPT、演示视频已生成",
            status=status_from_bool(report_final_ready and ppt_ready and video_ready, partial=report_source_ready),
            evidence="submission/01_report; submission/02_presentation; submission/03_video; docs/final_submission_package_plan.md",
            missing_or_risk=f"正式文件存在性审计：report_final_ready={report_final_ready}; ppt_ready={ppt_ready}; video_ready={video_ready}; missing={final_missing_text}; video_has_narration={video_has_narration}。{video_note}",
            next_action="人工播放检查 demo_video.mp4；若竞赛要求讲解录屏，优先替换为带人工讲解或可听旁白的版本。",
        ),
        AuditItem(
            gate="G6",
            requirement="最终提交包无 blocked 项",
            status=status_from_bool(blocked_artifacts == 0),
            evidence="outputs/submission_index/submission_checklist.csv; outputs/submission_index/submission_package_index.md",
            missing_or_risk=f"当前 submission index 中 blocked 项为 {blocked_artifacts}。",
            next_action="消除 submission index 中剩余 blocked 项，并生成最终 PDF/DOCX/PPTX/MP4。",
        ),
    ]
    return items


def write_markdown(items: list[AuditItem], out_dir: Path) -> None:
    status_counts = pd.Series([item.status for item in items]).value_counts().to_dict()
    all_complete = all(item.status == "complete" for item in items)
    rows = "\n".join(
        f"| {item.gate} | {item.requirement} | {item.status} | {item.evidence} | {item.missing_or_risk} | {item.next_action} |"
        for item in items
    )
    content = f"""# Completion audit

This audit is conservative. Synthetic/demo outputs prove pipeline readiness only; final completion requires real CST evidence and final submission artifacts.

## Current Verdict

- Completion proven: `{str(all_complete).lower()}`
- Complete gates: {int(status_counts.get('complete', 0))}
- Partial gates: {int(status_counts.get('partial', 0))}
- Missing gates: {int(status_counts.get('missing', 0))}

## Gate Table

| Gate | Requirement | Status | Evidence | Missing/Risk | Next action |
|---|---|---|---|---|---|
{rows}

## Shortest Gate Order

1. Keep Level 1 strict merge, equivalent-source reconstruction, and angular calibration evidence together.
2. Write the Level 1 angular-calibration versus near-field model boundary into the report/PPT/video.
3. Write the Level 2 simplified structure-scattering/occlusion comparison evidence and its non-full-wave boundary.
4. Export final PDF/DOCX/PPTX/MP4.
5. Rebuild scorecard, report package, presentation package, submission index, completion audit, and master dashboard.
"""
    (out_dir / "completion_audit.md").write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    items = build_audit_items()
    df = pd.DataFrame([asdict(item) for item in items])
    df.to_csv(OUT / "completion_audit.csv", index=False, encoding="utf-8-sig")
    write_markdown(items, OUT)
    summary = {
        "gate_count": int(len(items)),
        "complete": int((df["status"] == "complete").sum()),
        "partial": int((df["status"] == "partial").sum()),
        "missing": int((df["status"] == "missing").sum()),
        "completion_proven": bool((df["status"] == "complete").all()),
        "next_blocking_gate": df.loc[df["status"].ne("complete"), "gate"].iloc[0] if (df["status"].ne("complete")).any() else "",
    }
    (OUT / "completion_audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Completion audit written to {OUT}")
    print(df[["gate", "requirement", "status"]].to_string(index=False))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
