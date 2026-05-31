from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "submission_index"


@dataclass
class SubmissionArtifact:
    category: str
    artifact: str
    expected_path: str
    current_source: str
    status: str
    blocker: str


def path_exists(path: str) -> bool:
    return (ROOT / path).exists()


def read_json(path: str) -> dict:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def status_for(expected_path: str, current_source: str, blocker: str = "") -> str:
    if path_exists(expected_path):
        return "ready"
    if current_source and path_exists(current_source):
        return "draft/source ready"
    if blocker:
        return "blocked"
    return "missing"


def apply_gate_status(row: SubmissionArtifact, gates: dict[str, object]) -> None:
    if row.artifact == "Level 1 CST 工程":
        if bool(gates.get("level1_required_complete")) and path_exists(row.expected_path):
            row.status = "ready"
        elif bool(gates.get("level1_required_complete")):
            row.status = "draft/source ready"
        elif bool(gates.get("level1_projects_generated")) and path_exists(row.current_source):
            row.status = "draft/source ready"
            row.blocker = "真实 CST 工程已由 API 生成；仍需在 CST 中求解并导出 Level 1 nearfield/farfield CSV。"
        else:
            row.status = "blocked"
        return

    if row.artifact == "Level 2 CST 工程":
        if bool(gates.get("level2_all_complete")) and path_exists(row.expected_path):
            row.status = "ready"
        elif bool(gates.get("level2_all_complete")):
            row.status = "draft/source ready"
        else:
            row.status = "blocked"
        return

    if row.artifact == "Level 2 合并 nearfield/farfield":
        if bool(gates.get("level2_all_complete")) and path_exists(row.expected_path):
            row.status = "ready"
        elif bool(gates.get("level2_all_complete")):
            row.status = "draft/source ready"
        else:
            row.status = "blocked"


def artifacts() -> list[SubmissionArtifact]:
    level1_merge = read_json("outputs/cst_level1_merge_report/level1_merge_summary.json")
    level2_merge = read_json("outputs/cst_level2_merge_report/level2_merge_summary.json")
    level1_projects = read_json("outputs/cst_real_level1_projects/cst_automation_summary.json")
    gates = {
        "level1_required_complete": level1_merge.get("required_complete", False),
        "level1_projects_generated": level1_projects.get("all_projects_created", False),
        "level2_all_complete": level2_merge.get("all_complete", False),
        "level2_complete_samples": int(level2_merge.get("complete_samples", 0) or 0),
    }
    rows = [
        SubmissionArtifact(
            "admin",
            "人工报名与提交信息模板",
            "submission/00_admin/admin_submission_template.md",
            "docs/admin_submission_template.md",
            "",
            "需由队伍人工填写学校、队名、申报人、电话、报名表和最终命名信息。",
        ),
        SubmissionArtifact(
            "report",
            "方案报告 PDF",
            "submission/01_report/solution_report.pdf",
            "docs/solution_report_draft.md",
            "",
            "Level 1/2 指标已接入草稿，尚未排版导出 PDF。",
        ),
        SubmissionArtifact(
            "report",
            "方案报告 DOCX",
            "submission/01_report/solution_report.docx",
            "docs/solution_report_draft.md",
            "",
            "Level 1/2 指标已接入草稿，尚未排版导出 DOCX。",
        ),
        SubmissionArtifact(
            "presentation",
            "答辩 PPT",
            "submission/02_presentation/defense_slides.pptx",
            "docs/final_submission_package_plan.md",
            "",
            "待 Level 1 角域/近场模型边界、Level 2 结构边界和最终报告口径稳定后制作。",
        ),
        SubmissionArtifact(
            "presentation",
            "答辩 PPT PDF",
            "submission/02_presentation/defense_slides.pdf",
            "submission/02_presentation/defense_slides.pptx",
            "",
            "由 PowerPoint COM 从 PPTX 导出，需与 PPTX 同步校验。",
        ),
        SubmissionArtifact(
            "presentation",
            "答辩 PPT storyboard",
            "submission/02_presentation/presentation_package",
            "outputs/presentation_package",
            "",
            "storyboard 是制作素材，不是最终 PPTX。",
        ),
        SubmissionArtifact(
            "video",
            "演示视频",
            "submission/03_video/demo_video.mp4",
            "docs/final_submission_package_plan.md",
            "",
            "待 CST 截图、PPT、Level 1/2 指标和风险口径稳定后录制。",
        ),
        SubmissionArtifact(
            "video",
            "演示视频 storyboard",
            "submission/03_video/video_package",
            "outputs/presentation_package",
            "",
            "storyboard 是录制素材，不是最终 MP4。",
        ),
        SubmissionArtifact(
            "video",
            "演示视频导出摘要",
            "submission/03_video/video_artifact",
            "outputs/video_artifact",
            "",
            "包含 PowerPoint 自动计时导出中间文件和 demo_video_summary.json。",
        ),
        SubmissionArtifact(
            "package",
            "提交草稿 README",
            "submission/README_submission_draft.md",
            "src/build_submission_draft.py",
            "",
            "草稿包需要在每次核心结果变化后重新生成。",
        ),
        SubmissionArtifact(
            "package",
            "提交草稿 manifest",
            "submission/submission_draft_manifest.csv",
            "src/build_submission_draft.py",
            "",
            "草稿包需要在每次核心结果变化后重新生成。",
        ),
        SubmissionArtifact(
            "package",
            "提交草稿 summary",
            "submission/submission_draft_summary.json",
            "src/build_submission_draft.py",
            "",
            "草稿包需要在每次核心结果变化后重新生成。",
        ),
        SubmissionArtifact(
            "code",
            "Python 代码",
            "submission/04_code/src",
            "code",
            "",
            "",
        ),
        SubmissionArtifact(
            "code",
            "复现说明",
            "submission/04_code/README.md",
            "README.md",
            "",
            "最终路径需要在打包前冻结。",
        ),
        SubmissionArtifact(
            "code",
            "Python 依赖清单",
            "submission/04_code/requirements.txt",
            "requirements.txt",
            "",
            "",
        ),
        SubmissionArtifact(
            "code",
            "复现命令清单",
            "submission/04_code/reproduce_commands.md",
            "docs/reproduce_commands.md",
            "",
            "最终真实 CST 路径需要在打包前复核。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 CST 执行清单",
            "submission/05_cst/level1_manifest",
            "outputs/cst_level1_plan",
            "",
            "当前是执行清单，真实 CST 工程和导出仍需补齐。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 CST 建模任务包",
            "submission/05_cst/level1_workpack",
            "outputs/cst_level1_workpack",
            "",
            "当前是半球面建模交接材料，真实 CST 工程和导出仍需补齐。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 解析方向图参考",
            "submission/05_cst/level1_analytic_reference",
            "outputs/level1_analytic_reference",
            "",
            "解析参考只用于 sanity check，不能替代真实 CST 审计和重建。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 导出审计报告",
            "submission/05_cst/level1_merge_report",
            "outputs/cst_level1_merge_report",
            "",
            "当前是缺漏审计报告，真实 CST 导出到位后需重新运行。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 批量重建报告",
            "submission/05_cst/level1_reconstruction_batch",
            "outputs/cst_level1_reconstruction_batch",
            "",
            "当前包含 required 2/2 批量重建；等效源近场模型风险需与角域校准一起说明。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 角域校准报告",
            "submission/05_cst/level1_angular_calibration",
            "outputs/cst_level1_angular_calibration",
            "",
            "当前用于证明 FarfieldPlot-derived solver-safe 数据的角域一致性，不替代 full-wave 近场 monitor。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 CST 工程",
            "submission/05_cst/level1_standard_sources",
            "outputs/cst_real_level1_projects/projects",
            "",
            "真实 CST 工程已生成；求解导出尚未完成。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 1 CST API 自动化证据",
            "submission/05_cst/level1_project_automation",
            "outputs/cst_real_level1_projects",
            "",
            "工程生成证据不能替代求解后的 nearfield/farfield CSV 和重建指标。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 CST 工程",
            "submission/05_cst/level2_multisource",
            "outputs/cst_level2_plan",
            "",
            "当前只有执行清单，真实 CST 工程尚未提供。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 CST 执行清单",
            "submission/05_cst/level2_manifest",
            "outputs/cst_level2_plan",
            "",
            "当前是执行清单，真实 CST 工程和导出仍需补齐。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 CST 建模任务包",
            "submission/05_cst/level2_workpack",
            "outputs/cst_level2_workpack",
            "",
            "当前是半球面建模交接材料，真实 CST 工程和导出仍需补齐。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 element-library 工程",
            "submission/05_cst/level2_element_library",
            "outputs/cst_level2_element_library",
            "",
            "当前是 CST-derived pilot 的三方向 element 工程，不等同于完整复杂载体 full-wave 工程。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 element 求解试验",
            "submission/05_cst/level2_element_solver_trials",
            "outputs/cst_level2_element_trials",
            "",
            "当前是 x/y/z element 求解证据，后续仍需结构对照。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 full48 叠加导出日志",
            "submission/05_cst/level2_superposed_export_logs",
            "outputs/cst_level2_superposed_export",
            "",
            "当前包含 full48 batch 导出日志；结构对照仍需补充。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 full48 合并审计报告",
            "submission/05_cst/level2_merge_report",
            "outputs/cst_level2_merge_report",
            "",
            "当前 all_complete=true；仍需在报告中说明 element-library superposition 假设。",
        ),
        SubmissionArtifact(
            "cst",
            "Level 2 简化结构遮挡对照",
            "submission/05_cst/level2_structure_comparison",
            "outputs/cst_structure_comparison",
            "",
            "当前是 simplified aircraft occlusion transfer 证据，不等同于 full-wave airframe scattering。",
        ),
        SubmissionArtifact(
            "cst",
            "CST 宏模板与 pilot 队列",
            "submission/05_cst/macro_templates",
            "outputs/cst_macro_templates",
            "",
            "宏模板需按本机 CST 版本适配后执行，不能替代真实 CST 结果。",
        ),
        SubmissionArtifact(
            "cst",
            "CST 执行 dashboard",
            "submission/05_cst/execution_dashboard",
            "outputs/cst_execution_dashboard",
            "",
            "dashboard 是执行辅助和缺口追踪，不能替代真实 CST 结果。",
        ),
        SubmissionArtifact(
            "cst",
            "CST 操作 runbook",
            "submission/05_cst/operator_runbook",
            "outputs/cst_operator_runbook",
            "",
            "runbook 是 G2 真机操作包，不能替代真实 CST 导出和重建指标。",
        ),
        SubmissionArtifact(
            "cst",
            "CST 真实执行日志模板",
            "submission/05_cst/execution_logs",
            "outputs/cst_execution_logs",
            "",
            "当前为空模板，真实仿真执行时需逐项填写。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 合并 nearfield/farfield",
            "submission/06_data/cst_exports/level2",
            "data/cst_exports/level2",
            "",
            f"当前完整样本为 {gates['level2_complete_samples']}/48；简化结构遮挡对照已补充，full-wave airframe 对照可作为增强项。",
        ),
        SubmissionArtifact(
            "data",
            "CST 真实导出 dropzone 说明",
            "submission/06_data/cst_exports/README_cst_exports.md",
            "data/cst_exports/README_cst_exports.md",
            "",
            "当前只有 README 和空目录，真实 nearfield/farfield 仍需导出。",
        ),
        SubmissionArtifact(
            "data",
            "CST 幅相转换 demo",
            "submission/06_data/phase_conversion_demo",
            "outputs/cst_phase_demo",
            "",
            "正式提交时可作为接口验证附录，真实数据仍需 CST 导出。",
        ),
        SubmissionArtifact(
            "data",
            "Level 1 同形合成闭环",
            "submission/06_data/synthetic_cst_level1_dataset",
            "outputs/synthetic_cst_level1_dataset",
            "",
            "仅作为接口和批处理验证证据，不能替代真实 CST 仿真结果。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 同形合成识别数据",
            "submission/06_data/synthetic_cst_dataset",
            "outputs/synthetic_cst_dataset",
            "",
            "仅作为识别接口验证证据，不能替代真实 CST 多源样本。",
        ),
        SubmissionArtifact(
            "data",
            "baseline 输出",
            "submission/06_data/processed_outputs/baseline",
            "outputs/baseline",
            "",
            "当前是合成 baseline，用于路线和代码验证。",
        ),
        SubmissionArtifact(
            "data",
            "重建鲁棒性输出",
            "submission/06_data/processed_outputs/reconstruction_robustness",
            "outputs/reconstruction_robustness",
            "",
            "当前是合成鲁棒性扫描，真实 CST 到位后需复核。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 full48 识别输出",
            "submission/06_data/processed_outputs/cst_recognition_level2",
            "outputs/cst_recognition_level2",
            "",
            "当前是 48 样本 CST-derived 识别结果，不能替代复杂载体 full-wave 结构对照。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 full48 消融输出",
            "submission/06_data/processed_outputs/cst_recognition_level2_ablation",
            "outputs/cst_recognition_level2_ablation",
            "",
            "当前是 48 样本 CST-derived 测点/频点删减验证，不能替代复杂载体 full-wave 结构对照。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 简化结构遮挡输出",
            "submission/06_data/processed_outputs/cst_structure_comparison",
            "outputs/cst_structure_comparison",
            "",
            "当前用于量化 element-library full48 在简化载体遮挡下的方向图偏差和 cross-domain 识别稳健性。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 pilot 识别输出",
            "submission/06_data/processed_outputs/cst_recognition_level2_pilot",
            "outputs/cst_recognition_level2_pilot",
            "",
            "保留 8 样本 pilot 作为阶段性过程证据。",
        ),
        SubmissionArtifact(
            "data",
            "Level 2 pilot 消融输出",
            "submission/06_data/processed_outputs/cst_recognition_level2_pilot_ablation",
            "outputs/cst_recognition_level2_pilot_ablation",
            "",
            "保留 8 样本 pilot 消融作为阶段性过程证据。",
        ),
        SubmissionArtifact(
            "metrics",
            "scorecard 指标目录",
            "submission/06_data/metrics/scorecard",
            "outputs/scorecard",
            "",
            "",
        ),
        SubmissionArtifact(
            "metrics",
            "赛题要求矩阵目录",
            "submission/06_data/metrics/problem_requirements",
            "outputs/problem_requirements",
            "",
            "赛题要求矩阵用于逐条验收，不是仿真结果证据。",
        ),
        SubmissionArtifact(
            "metrics",
            "报告成稿素材目录",
            "submission/06_data/metrics/report_package",
            "outputs/report_package",
            "",
            "该目录是成稿准备材料，不是最终 PDF/DOCX。",
        ),
        SubmissionArtifact(
            "metrics",
            "提交索引目录",
            "submission/06_data/metrics/submission_index",
            "outputs/submission_index",
            "",
            "",
        ),
        SubmissionArtifact(
            "metrics",
            "完成度审计目录",
            "submission/06_data/metrics/completion_audit",
            "outputs/completion_audit",
            "",
            "",
        ),
        SubmissionArtifact(
            "metrics",
            "master dashboard 目录",
            "submission/06_data/metrics/master_dashboard",
            "outputs/master_dashboard",
            "",
            "总控 dashboard 是项目管理与分工入口，不是仿真结果证据。",
        ),
        SubmissionArtifact(
            "metrics",
            "评分证据板",
            "submission/07_appendix/scorecard.md",
            "outputs/scorecard/scorecard.md",
            "",
            "",
        ),
        SubmissionArtifact(
            "metrics",
            "完成度审计报告",
            "submission/07_appendix/completion_audit.md",
            "outputs/completion_audit/completion_audit.md",
            "",
            "",
        ),
        SubmissionArtifact(
            "metrics",
            "master dashboard 报告",
            "submission/07_appendix/master_status_dashboard.md",
            "outputs/master_dashboard/master_status_dashboard.md",
            "",
            "总控 dashboard 需要在每轮真实 CST 证据更新后重建。",
        ),
        SubmissionArtifact(
            "appendix",
            "CST 操作 runbook",
            "submission/07_appendix/README_cst_operator_runbook.md",
            "outputs/cst_operator_runbook/README_cst_operator_runbook.md",
            "",
            "正式提交时可作为 CST 执行交接附录，需结合真实执行截图使用。",
        ),
        SubmissionArtifact(
            "appendix",
            "文献矩阵",
            "submission/07_appendix/literature_matrix.md",
            "docs/literature_matrix.md",
            "",
            "最终参考文献格式待统一。",
        ),
        SubmissionArtifact(
            "appendix",
            "文献到算法迁移证据链",
            "submission/07_appendix/literature_to_algorithm_traceability.md",
            "docs/literature_to_algorithm_traceability.md",
            "",
            "最终报告中需将该证据链转为正文叙述和正式引用。",
        ),
        SubmissionArtifact(
            "appendix",
            "赛题要求到证据矩阵",
            "submission/07_appendix/problem_requirements_matrix.md",
            "outputs/problem_requirements/problem_requirements_matrix.md",
            "",
            "该矩阵需随真实 CST 和最终交付物状态持续刷新。",
        ),
        SubmissionArtifact(
            "appendix",
            "数据字典",
            "submission/07_appendix/data_dictionary.md",
            "docs/data_dictionary.md",
            "",
            "最终 CST 字段若变化，需要同步更新。",
        ),
        SubmissionArtifact(
            "appendix",
            "最终提交计划",
            "submission/07_appendix/final_submission_package_plan.md",
            "docs/final_submission_package_plan.md",
            "",
            "",
        ),
        SubmissionArtifact(
            "appendix",
            "项目文件索引",
            "submission/07_appendix/project_file_index.md",
            "docs/project_file_index.md",
            "",
            "后续若移动文件，需要同步更新。",
        ),
        SubmissionArtifact(
            "appendix",
            "当前工作详细讲解",
            "submission/07_appendix/current_work_detailed_explanation.md",
            "docs/current_work_detailed_explanation.md",
            "",
            "若后续新增 full-wave airframe 对照或替换讲解视频，需要同步更新。",
        ),
        SubmissionArtifact(
            "appendix",
            "阶段说明目录",
            "submission/07_appendix/stage_notes",
            "docs/stage_notes",
            "",
            "每完成新阶段后需要补充对应说明。",
        ),
        SubmissionArtifact(
            "appendix",
            "Level 1 冲刺交接单",
            "submission/07_appendix/level1_cst_sprint_handoff.md",
            "docs/level1_cst_sprint_handoff.md",
            "",
            "正式提交时可作为过程管理附录，按真实执行情况更新。",
        ),
    ]
    for row in rows:
        row.status = status_for(row.expected_path, row.current_source, row.blocker)
        apply_gate_status(row, gates)
    return rows


def write_package_tree(rows: list[SubmissionArtifact]) -> None:
    content = """# Submission package index

This index tracks final submission artifacts. `draft/source ready` means there is a current source artifact, but final packaging is not complete.

## Current Artifact Status

| Category | Artifact | Expected final path | Current source | Status | Blocker |
|---|---|---|---|---|---|
"""
    for row in rows:
        content += (
            f"| {row.category} | {row.artifact} | `{row.expected_path}` | "
            f"`{row.current_source}` | {row.status} | {row.blocker} |\n"
        )

    content += """
## Final Package Tree

```text
CS-202614_submission/
  00_admin/
    admin_submission_template.md
  README_submission_draft.md
  submission_draft_manifest.csv
  submission_draft_summary.json
  01_report/
  02_presentation/
    defense_slides.pptx
    defense_slides.pdf
    presentation_package/
  03_video/
    video_package/
    video_artifact/
  04_code/
    requirements.txt
    reproduce_commands.md
  05_cst/
    level1_manifest/
    level1_workpack/
    level1_project_automation/
    level1_analytic_reference/
    level1_merge_report/
    level1_reconstruction_batch/
    level1_angular_calibration/
    level2_manifest/
    level2_workpack/
    level2_element_library/
    level2_element_solver_trials/
    level2_superposed_export_logs/
    level2_merge_report/
    level2_structure_comparison/
    macro_templates/
    execution_dashboard/
    operator_runbook/
    execution_logs/
  06_data/
    cst_exports/
    phase_conversion_demo/
    synthetic_cst_level1_dataset/
    synthetic_cst_dataset/
    processed_outputs/
      baseline/
      reconstruction_robustness/
      cst_recognition_level2/
      cst_recognition_level2_ablation/
      cst_structure_comparison/
      cst_recognition_level2_pilot/
      cst_recognition_level2_pilot_ablation/
    metrics/
      report_package/
      problem_requirements/
      scorecard/
      submission_index/
      completion_audit/
      master_dashboard/
  07_appendix/
    data_dictionary.md
    literature_to_algorithm_traceability.md
    problem_requirements_matrix.md
    completion_audit.md
    master_status_dashboard.md
    README_cst_operator_runbook.md
    level1_cst_sprint_handoff.md
    project_file_index.md
    current_work_detailed_explanation.md
    stage_notes/
```

## Pack-Ready Gates

1. Real CST Level 1 strict merge, equivalent-source reconstruction, and angular calibration metrics exist.
2. Full CST Level 2 recognition accuracy and confusion matrix exist.
3. `code/merge_cst_level1_exports.py --strict` passes.
4. `code/merge_cst_level2_exports.py --strict` passes.
5. `code/build_scorecard.py` no longer reports core objective items as demo-only.
6. Report/PPT/video contain the same final metrics, Level 1 angular/near-field model-boundary wording, and Level 2 simplified structure/occlusion boundary.
"""
    (OUT / "submission_package_index.md").write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = artifacts()
    df = pd.DataFrame([asdict(row) for row in rows])
    df.to_csv(OUT / "submission_checklist.csv", index=False, encoding="utf-8-sig")
    write_package_tree(rows)
    summary = {
        "artifact_count": len(rows),
        "ready": int((df["status"] == "ready").sum()),
        "draft_or_source_ready": int((df["status"] == "draft/source ready").sum()),
        "blocked": int((df["status"] == "blocked").sum()),
        "missing": int((df["status"] == "missing").sum()),
    }
    (OUT / "submission_index_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Submission index written to {OUT}")
    print(df[["category", "artifact", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
