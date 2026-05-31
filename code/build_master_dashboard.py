from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "master_dashboard"


@dataclass
class NextAction:
    priority: int
    owner_role: str
    owner_responsibility: str
    gate: str
    action: str
    trigger: str
    expected_artifact: str
    command_or_file: str
    proof_to_close: str
    blocked_by: str
    notes: str


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


def first_value(data: dict[str, Any], key: str, default: Any = "") -> Any:
    value = data.get(key, default)
    return default if value is None else value


def team_roles() -> dict[str, str]:
    return {
        "A_algorithm": "算法/数据负责人：审计 CST 导出、运行重建和识别、更新指标表。",
        "B_CST": "CST 仿真负责人：建模、monitor、nearfield/farfield 导出和截图留证。",
        "C_docs": "报告/答辩负责人：把真实指标、图表和过程证据写入报告、PPT、视频和提交包。",
    }


def build_gate_summary(completion: pd.DataFrame) -> pd.DataFrame:
    if completion.empty:
        return pd.DataFrame(
            [
                {
                    "gate": "unknown",
                    "status": "missing",
                    "owner_role": "A_algorithm",
                    "requirement": "Run build_completion_audit.py first.",
                    "evidence": "outputs/completion_audit",
                    "next_action": "python code\\build_completion_audit.py",
                }
            ]
        )

    owner_by_gate = {
        "G0": "C_docs",
        "G1": "B_CST",
        "G2": "B_CST + A_algorithm",
        "G2-demo": "A_algorithm",
        "G3": "B_CST + A_algorithm",
        "G4": "A_algorithm + C_docs",
        "G5": "C_docs",
        "G6": "C_docs",
    }
    rows: list[dict[str, Any]] = []
    for item in completion.itertuples(index=False):
        gate = str(getattr(item, "gate"))
        rows.append(
            {
                "gate": gate,
                "status": str(getattr(item, "status")),
                "owner_role": owner_by_gate.get(gate, "A_algorithm"),
                "requirement": str(getattr(item, "requirement")),
                "evidence": str(getattr(item, "evidence")),
                "next_action": str(getattr(item, "next_action")),
            }
        )
    return pd.DataFrame(rows)


def build_next_actions(
    cst_dashboard: dict[str, Any],
    completion_summary: dict[str, Any],
    report_summary: dict[str, Any],
    presentation_summary: dict[str, Any],
) -> list[NextAction]:
    roles = team_roles()
    next_gate = first_value(completion_summary, "next_blocking_gate", "G2")
    if bool(first_value(completion_summary, "completion_proven", False)):
        return [
            NextAction(
                priority=1,
                owner_role="C_docs",
                owner_responsibility=roles["C_docs"],
                gate="FINAL",
                action="人工完整播放 submission/03_video/demo_video.mp4。",
                trigger="completion_proven=true；当前 MP4 为 PowerPoint 自动计时静音版。",
                expected_artifact="人工确认视频能正常播放，或替换为带人工讲解/旁白的版本。",
                command_or_file="submission/03_video/demo_video.mp4; outputs/video_artifact/demo_video_summary.json",
                proof_to_close="视频播放无黑屏、卡顿、错页；若竞赛要求讲解录屏，则替换并重跑审计。",
                blocked_by="",
                notes="这是提交前质量动作，不影响当前自动审计的 completion_proven=true。",
            ),
            NextAction(
                priority=2,
                owner_role="C_docs",
                owner_responsibility=roles["C_docs"],
                gate="FINAL",
                action="整理最终压缩包命名、报名表和人工提交信息。",
                trigger="所有核心文件已齐套，submission index blocked=0。",
                expected_artifact="最终 zip、报名表扫描件/信息、学校和申报人信息。",
                command_or_file="submission; docs/final_submission_package_plan.md",
                proof_to_close="压缩包目录与赛题命名规则一致，人工信息补齐。",
                blocked_by="",
                notes="该项需要队伍成员提供真实学校、姓名、电话和报名表，不能由脚本自动完成。",
            ),
        ]

    return [
        NextAction(
            priority=1,
            owner_role="A_algorithm",
            owner_responsibility=roles["A_algorithm"],
            gate="G5",
            action="把 Level 1 角域校准与近场模型边界写入成稿。",
            trigger="角域校准已证明 solver-safe FarfieldPlot-derived 数据自洽；G5 需要把该结论转成报告口径。",
            expected_artifact="报告/PPT 中的 Level 1 双通道证据表：等效源反演风险 + 角域校准高一致性。",
            command_or_file="outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; outputs/cst_level1_angular_calibration; src/run_cst_level1_angular_calibration.py",
            proof_to_close="报告中明确区分 FarfieldPlot-derived 角域样本和 full-wave 近场 monitor，且不再把原等效源指标作为唯一结论。",
            blocked_by="",
            notes="当前不是缺 CST 文件；下一步是把模型边界讲清楚，避免指标看起来互相矛盾。",
        ),
        NextAction(
            priority=2,
            owner_role="A_algorithm + C_docs",
            owner_responsibility=roles["A_algorithm"] + " " + roles["C_docs"],
            gate="G5",
            action="把 Level 2 简化结构遮挡对照写入报告和展示材料。",
            trigger="Level 2 full48 已完成，简化 aircraft occlusion transfer 已生成结构敏感性和 cross-domain 识别指标。",
            expected_artifact="报告/PPT 中的结构遮挡对照图表、指标表和 non-full-wave 边界说明。",
            command_or_file="src/run_cst_structure_comparison.py; outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md",
            proof_to_close="报告/PPT 中明确 simplified structure/occlusion transfer 与 full-wave airframe scattering 的边界，并引用 cross-domain accuracy 与遮挡 dB 指标。",
            blocked_by="",
            notes="该阶段已补齐 bounded structure evidence；full-wave airframe CST 可作为时间允许时的增强项。",
        ),
        NextAction(
            priority=3,
            owner_role="C_docs",
            owner_responsibility=roles["C_docs"],
            gate="G5",
            action="把 Level 1/2 最新结果写入正式报告、PPT 和视频脚本。",
            trigger=f"当前 next_blocking_gate={next_gate}；G5 是唯一未关闭 gate。",
            expected_artifact="submission/01_report/solution_report.pdf; submission/01_report/solution_report.docx; submission/02_presentation/defense_slides.pptx; submission/03_video/demo_video.mp4。",
            command_or_file="docs/solution_report_draft.md; docs/final_submission_package_plan.md; outputs/scorecard/scorecard.md",
            proof_to_close="正式 PDF/DOCX/PPTX/MP4 文件存在，且指标与 scorecard 一致。",
            blocked_by="",
            notes=f"当前报告 final={first_value(report_summary, 'is_final_report', False)}；PPT final={first_value(presentation_summary, 'is_final_presentation', False)}；video final={first_value(presentation_summary, 'is_final_video', False)}。",
        ),
        NextAction(
            priority=4,
            owner_role="C_docs",
            owner_responsibility=roles["C_docs"],
            gate="G6",
            action="最终打包前重建所有索引和提交草稿。",
            trigger="正式报告/PPT/视频生成后。",
            expected_artifact="submission; outputs/submission_index; outputs/completion_audit; outputs/master_dashboard。",
            command_or_file="python code\\build_scorecard.py; python code\\build_problem_requirements_matrix.py; python code\\build_submission_index.py; python code\\build_completion_audit.py; python code\\build_master_dashboard.py; python code\\build_submission_draft.py",
            proof_to_close="completion_proven=true，submission index blocked=0，且最终文件齐全。",
            blocked_by="",
            notes="提交系统/邮箱所需学校、申报人、联系电话、报名表仍需人工补充。",
        ),
    ]


def artifact_links() -> pd.DataFrame:
    rows = [
        {
            "artifact": "Master dashboard",
            "path": "outputs/master_dashboard/master_status_dashboard.md",
            "meaning": "一页式总状态、当前阻塞门、三人任务队列入口。",
        },
        {
            "artifact": "Completion audit",
            "path": "outputs/completion_audit/completion_audit.md",
            "meaning": "是否完成赛题的保守 gate 判断。",
        },
        {
            "artifact": "Problem requirements matrix",
            "path": "outputs/problem_requirements/problem_requirements_matrix.md",
            "meaning": "赛题原文要求、100 分评分项、交付物和当前证据的一一映射。",
        },
        {
            "artifact": "CST execution dashboard",
            "path": "outputs/cst_execution_dashboard/cst_execution_dashboard.md",
            "meaning": "真实 CST required/pilot 导出任务和 dropzone 规则。",
        },
        {
            "artifact": "CST operator runbook",
            "path": "outputs/cst_operator_runbook/README_cst_operator_runbook.md",
            "meaning": "G2 两个 required 标准源的 CST 真机操作包、探针点、远场网格和导出合同。",
        },
        {
            "artifact": "CST Level 1 generated projects",
            "path": "outputs/cst_real_level1_projects/README_cst_level1_automation.md",
            "meaning": "通过本机 CST API 生成的两个 Level 1 required .cst 工程、VBA history 和生成日志。",
        },
        {
            "artifact": "CST Level 1 angular calibration",
            "path": "outputs/cst_level1_angular_calibration/README_cst_level1_angular_calibration.md",
            "meaning": "FarfieldPlot-derived solver-safe Level 1 导出的角域一致性校准和模型边界说明。",
        },
        {
            "artifact": "CST Level 2 simplified structure comparison",
            "path": "outputs/cst_structure_comparison/README_cst_structure_comparison.md",
            "meaning": "基于 Level 2 CST-derived 数据的简化载体遮挡/安装效应对照、方向图偏差和 cross-domain 识别稳健性。",
        },
        {
            "artifact": "Submission index",
            "path": "outputs/submission_index/submission_package_index.md",
            "meaning": "最终提交物 readiness/blocker 索引。",
        },
        {
            "artifact": "Report package",
            "path": "outputs/report_package/README_report_package.md",
            "meaning": "报告章节、图表和替换任务。",
        },
        {
            "artifact": "Presentation package",
            "path": "outputs/presentation_package/README_presentation_package.md",
            "meaning": "答辩 PPT storyboard、视频分镜和展示素材缺口。",
        },
        {
            "artifact": "Scorecard",
            "path": "outputs/scorecard/scorecard.md",
            "meaning": "评分项证据板。",
        },
    ]
    return pd.DataFrame(rows)


def write_markdown(
    gate_df: pd.DataFrame,
    actions_df: pd.DataFrame,
    links_df: pd.DataFrame,
    summaries: dict[str, dict[str, Any]],
) -> None:
    completion = summaries["completion"]
    submission = summaries["submission"]
    cst_dashboard = summaries["cst_dashboard"]
    scorecard = summaries["scorecard"]
    report = summaries["report"]
    presentation = summaries["presentation"]
    problem = summaries["problem"]

    completion_proven = str(first_value(completion, "completion_proven", False)).lower()
    next_gate = first_value(completion, "next_blocking_gate", "unknown")
    gate_counts = (
        f"complete={first_value(completion, 'complete', 0)}, "
        f"partial={first_value(completion, 'partial', 0)}, "
        f"missing={first_value(completion, 'missing', 0)}"
    )
    submission_counts = (
        f"ready={first_value(submission, 'ready', 0)}, "
        f"draft/source={first_value(submission, 'draft_or_source_ready', 0)}, "
        f"blocked={first_value(submission, 'blocked', 0)}, "
        f"missing={first_value(submission, 'missing', 0)}"
    )

    gate_rows = "\n".join(
        f"| {row.gate} | {row.status} | {row.owner_role} | {row.requirement} | {row.next_action} |"
        for row in gate_df.itertuples(index=False)
    )
    action_rows = "\n".join(
        f"| {row.priority} | {row.owner_role} | {row.gate} | {row.action} | {row.proof_to_close} |"
        for row in actions_df.itertuples(index=False)
    )
    link_rows = "\n".join(
        f"| {row.artifact} | `{row.path}` | {row.meaning} |"
        for row in links_df.itertuples(index=False)
    )

    content = f"""# Master status dashboard

This dashboard summarizes the whole CS-202614 workspace. It is a project-control artifact, not simulation evidence.

## Current Verdict

| Item | Current value |
|---|---|
| Completion proven | `{completion_proven}` |
| Next blocking gate | `{next_gate}` |
| Gate counts | {gate_counts} |
| Submission index | {submission_counts} |
| Problem requirements | `{first_value(problem, 'requirement_count', 0)}` requirements / `{first_value(problem, 'total_scored_points', 0)}` scored points |
| Problem gaps | `{first_value(problem, 'blocked_or_missing_count', 0)}` blocked or missing evidence items |
| Measurement surface | `{first_value(scorecard, 'level1_measurement_surface', '2pi_upper_hemisphere')}` |
| Hemisphere sensor count | `{first_value(scorecard, 'level1_workpack_sensor_count', 0)}` |
| Level 1 required complete | `{first_value(scorecard, 'level1_required_complete', False)}` |
| Level 2 complete samples | `{first_value(scorecard, 'level2_complete_samples', 0)}/{first_value(scorecard, 'level2_planned_samples', 48)}` |
| Level 2 structure comparison samples | `{first_value(scorecard, 'structure_sample_count', 0)}` |
| Level 2 structure mean/P95 shadow | `{first_value(scorecard, 'structure_mean_shadow_db', 0)}` / `{first_value(scorecard, 'structure_p95_shadow_db', 0)}` dB |
| Level 2 structure cross-domain accuracy | `{first_value(scorecard, 'structure_cross_domain_accuracy', 'unknown')}` |
| CST required-now missing files | `{first_value(cst_dashboard, 'missing_required_now_files', 'unknown')}` |
| Level 2 pilot missing files | `{first_value(cst_dashboard, 'missing_level2_pilot_files', 'unknown')}` |
| Report final | `{first_value(report, 'is_final_report', False)}` |
| Presentation/video final | `{first_value(presentation, 'is_final_presentation', False)}` / `{first_value(presentation, 'is_final_video', False)}` |

## Gate Summary

| Gate | Status | Owner | Requirement | Next action |
|---|---|---|---|---|
{gate_rows}

## Next Action Queue

| Priority | Owner | Gate | Action | Proof to close |
|---:|---|---|---|---|
{action_rows}

## Team Split

| Role | Responsibility |
|---|---|
| A_algorithm | 审计真实 CST 导出、运行 Level 1 重建、Level 2 识别/删减、更新指标。 |
| B_CST | 在 CST 中完成模型、monitor、半球面测点、nearfield/farfield 导出和截图。 |
| C_docs | 把真实证据写入报告、PPT、视频脚本、scorecard 和提交草稿包。 |

## Key Files

| Artifact | Path | Meaning |
|---|---|---|
{link_rows}

## Immediate Command Sequence

```powershell
python code\\build_scorecard.py
python code\\build_problem_requirements_matrix.py
python code\\build_submission_index.py
python code\\build_completion_audit.py
python code\\build_master_dashboard.py
python code\\build_submission_draft.py
```

After final report/PPT/video generation, rerun this sequence and confirm `completion_proven=true`.
"""
    (OUT / "master_status_dashboard.md").write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    completion_summary = read_json("outputs/completion_audit/completion_audit_summary.json")
    submission_summary = read_json("outputs/submission_index/submission_index_summary.json")
    cst_dashboard_summary = read_json("outputs/cst_execution_dashboard/cst_execution_dashboard_summary.json")
    scorecard_metrics = read_json("outputs/scorecard/scorecard_metrics.json")
    report_summary = read_json("outputs/report_package/report_package_summary.json")
    presentation_summary = read_json("outputs/presentation_package/presentation_package_summary.json")
    problem_summary = read_json("outputs/problem_requirements/problem_requirements_summary.json")
    completion_csv = read_csv("outputs/completion_audit/completion_audit.csv")

    gate_df = build_gate_summary(completion_csv)
    actions = build_next_actions(cst_dashboard_summary, completion_summary, report_summary, presentation_summary)
    actions_df = pd.DataFrame([asdict(action) for action in actions])
    links_df = artifact_links()

    gate_df.to_csv(OUT / "master_gate_summary.csv", index=False, encoding="utf-8-sig")
    actions_df.to_csv(OUT / "master_next_actions.csv", index=False, encoding="utf-8-sig")
    links_df.to_csv(OUT / "master_key_artifacts.csv", index=False, encoding="utf-8-sig")

    summaries = {
        "completion": completion_summary,
        "submission": submission_summary,
        "cst_dashboard": cst_dashboard_summary,
        "scorecard": scorecard_metrics,
        "report": report_summary,
        "presentation": presentation_summary,
        "problem": problem_summary,
    }
    write_markdown(gate_df, actions_df, links_df, summaries)

    blocked_actions = int(actions_df["blocked_by"].astype(str).ne("").sum())
    summary = {
        "out_dir": "outputs\\master_dashboard",
        "gate_count": int(len(gate_df)),
        "action_count": int(len(actions_df)),
        "blocked_action_count": blocked_actions,
        "next_blocking_gate": first_value(completion_summary, "next_blocking_gate", "unknown"),
        "completion_proven": bool(first_value(completion_summary, "completion_proven", False)),
        "submission_ready": int(first_value(submission_summary, "ready", 0)),
        "submission_blocked": int(first_value(submission_summary, "blocked", 0)),
        "problem_requirement_count": int(first_value(problem_summary, "requirement_count", 0)),
        "problem_blocked_or_missing_count": int(first_value(problem_summary, "blocked_or_missing_count", 0)),
        "missing_required_now_files": first_value(cst_dashboard_summary, "missing_required_now_files", "unknown"),
        "missing_level2_pilot_files": first_value(cst_dashboard_summary, "missing_level2_pilot_files", "unknown"),
        "is_final": bool(first_value(completion_summary, "completion_proven", False)),
        "is_simulation_evidence": False,
    }
    (OUT / "master_dashboard_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Master dashboard written to {OUT}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
