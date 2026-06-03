from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "docs" / "solution_report_draft.md"
DEFAULT_LITERATURE = ROOT / "docs" / "literature_matrix.md"
DEFAULT_TRACEABILITY = ROOT / "docs" / "literature_to_algorithm_traceability.md"
DEFAULT_SCORECARD = ROOT / "outputs" / "scorecard" / "score_items.csv"
DEFAULT_MASTER = ROOT / "outputs" / "master_dashboard" / "master_dashboard_summary.json"
DEFAULT_COMPLETION = ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json"
DEFAULT_SUBMISSION = ROOT / "outputs" / "submission_index" / "submission_index_summary.json"
DEFAULT_LEVEL1_MERGE = ROOT / "outputs" / "cst_level1_merge_report" / "level1_merge_summary.json"
DEFAULT_LEVEL1_RECON = ROOT / "outputs" / "cst_level1_reconstruction_batch" / "level1_batch_reconstruction_summary.json"
DEFAULT_LEVEL1_ANGULAR = ROOT / "outputs" / "cst_level1_angular_calibration" / "angular_calibration_summary.json"
DEFAULT_LEVEL2_MERGE = ROOT / "outputs" / "cst_level2_merge_report" / "level2_merge_summary.json"
DEFAULT_LEVEL2_RECOG = ROOT / "outputs" / "cst_recognition_level2" / "cst_recognition_metrics.json"
DEFAULT_STRUCTURE_COMPARISON = ROOT / "outputs" / "cst_structure_comparison" / "structure_comparison_summary.json"
DEFAULT_COMPOUND_STRESS = ROOT / "data" / "recognition_stress_tests" / "level2_compound_stress" / "recognition_compound_stress_summary.json"
DEFAULT_OUT = ROOT / "outputs" / "report_package"
FINAL_FILES = [
    ("final PDF", ROOT / "submission" / "01_report" / "solution_report.pdf"),
    ("final DOCX", ROOT / "submission" / "01_report" / "solution_report.docx"),
    ("final PPTX", ROOT / "submission" / "02_presentation" / "defense_slides.pptx"),
    ("final PPT PDF", ROOT / "submission" / "02_presentation" / "defense_slides.pdf"),
    ("final MP4", ROOT / "submission" / "03_video" / "demo_video.mp4"),
]
FINAL_REPORT_FILES = [
    ROOT / "submission" / "01_report" / "solution_report.pdf",
    ROOT / "submission" / "01_report" / "solution_report.docx",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def nested_value(data: dict[str, object], keys: tuple[str, ...], default: object = "unknown") -> object:
    current: object = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def final_file_state() -> tuple[int, int, str]:
    missing = [name for name, path in FINAL_FILES if not path.exists()]
    ready = len(FINAL_FILES) - len(missing)
    missing_text = ", ".join(missing) if missing else "none"
    return ready, len(FINAL_FILES), missing_text


def final_blocker_text() -> str:
    ready, total, missing_text = final_file_state()
    if ready == total:
        return (
            "All report/PPT/video delivery files exist. Remaining work is human playback, "
            "administrative submission metadata, and final archive review."
        )
    return (
        "G5 remains partial: Level 1 angular/near-field model-boundary wording, "
        "Level 2 simplified structure-boundary evidence wording, and final delivery files "
        f"are not closed ({ready}/{total} ready; missing: {missing_text})."
    )


def report_final_ready() -> bool:
    return all(path.exists() and path.stat().st_size > 0 for path in FINAL_REPORT_FILES)


def parse_headings(markdown: str) -> list[dict[str, object]]:
    headings: list[dict[str, object]] = []
    lines = markdown.splitlines()
    for idx, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if not match:
            continue
        level = len(match.group(1))
        title = match.group(2).strip()
        headings.append({"line": idx, "level": level, "title": title})
    return headings


def section_status(headings: list[dict[str, object]], report_text: str) -> pd.DataFrame:
    status_rows: list[dict[str, object]] = []
    h2_titles = [row for row in headings if int(row["level"]) == 2]
    for idx, heading in enumerate(h2_titles):
        start_line = int(heading["line"])
        end_line = int(h2_titles[idx + 1]["line"]) - 1 if idx + 1 < len(h2_titles) else len(report_text.splitlines())
        title = str(heading["title"])
        section_text = "\n".join(report_text.splitlines()[start_line - 1 : end_line])
        has_demo = any(keyword in section_text for keyword in ["demo", "合成", "synthetic"])
        has_unresolved_real_cst_gap = any(keyword in section_text for keyword in ["待补真实", "尚未导出", "Needs CST"])
        has_g5_risk = any(
            keyword in section_text
            for keyword in ["Level 1 重建精度风险", "指标偏弱", "结构散射/遮挡", "CST-derived", "复合", "插补", "PDF/DOCX/PPTX/MP4"]
        )
        if "国内外发展调研" in title:
            readiness = "draft_ready"
            blocker = "统一参考文献格式，压缩为正式报告语言。"
        elif has_unresolved_real_cst_gap:
            readiness = "blocked_by_real_cst"
            blocker = "仍有明确的真实 CST 缺口表述，需要改成当前证据或列为 G5 风险。"
        elif has_g5_risk:
            readiness = "g5_review_needed"
            blocker = "章节已接入当前证据，但需在最终稿中统一 Level 1 精度风险、Level 2 结构边界或最终导出口径。"
        elif has_demo:
            readiness = "reference_only"
            blocker = "含 demo/synthetic 或合成参考内容，最终稿中必须标注其只用于算法接口/鲁棒性参考。"
        else:
            readiness = "draft_ready"
            blocker = "最终排版前复核语句和图表编号。"
        status_rows.append(
            {
                "section": title,
                "start_line": start_line,
                "end_line": end_line,
                "readiness": readiness,
                "blocker_or_final_edit": blocker,
            }
        )
    return pd.DataFrame(status_rows)


def literature_rows(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in markdown.splitlines():
        if not line.strip().startswith("| L"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8 or not re.match(r"L\d+", cells[0]):
            continue
        rows.append(
            {
                "id": cells[0],
                "direction": cells[1],
                "reference": cells[2],
                "type": cells[3],
                "grade": cells[4],
                "use_in_report": cells[6],
                "source": cells[7],
            }
        )
    return rows


def reference_shortlist(lit_rows: list[dict[str, str]]) -> pd.DataFrame:
    preferred = [row for row in lit_rows if row["grade"] == "A"]
    return pd.DataFrame(preferred)


def figure_manifest() -> pd.DataFrame:
    rows = [
        {
            "figure_id": "Fig-01",
            "caption": "2π 半球面测点布局与 12m x 10m x 8m 包络",
            "current_source": "outputs/baseline/sensor_layout_hemisphere.png",
            "report_section": "4. 分布式宽带传感布局设计",
            "status": "draft_ready",
            "replacement_needed": "用 CST 工程中的测点/包络截图补强。",
        },
        {
            "figure_id": "Fig-02",
            "caption": "CST Level 1 required 标准源执行顺序",
            "current_source": "outputs/master_dashboard/master_status_dashboard.md",
            "report_section": "8. CST 仿真测试设计",
            "status": "current_dashboard",
            "replacement_needed": "补充 CST 工程截图和最终审计日志。",
        },
        {
            "figure_id": "Fig-03",
            "caption": "标准源近远场重建结果对比",
            "current_source": "outputs/cst_reconstruction/L1_short_dipole_z_1p2G/cst_farfield_reconstruction_compare.png",
            "report_section": "5. 近远场关联建模与三维场域重建",
            "status": "cst_required_ready",
            "replacement_needed": "保留为等效源近场模型风险图，并配套 Fig-08 角域校准图解释数据边界。",
        },
        {
            "figure_id": "Fig-08",
            "caption": "Level 1 FarfieldPlot-derived 角域校准对比",
            "current_source": "outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png",
            "report_section": "5. 近远场关联建模与三维场域重建",
            "status": "cst_angular_ready",
            "replacement_needed": "说明该图验证 solver-safe 角域一致性，不等同于 full-wave 近场 monitor 反演。",
        },
        {
            "figure_id": "Fig-04",
            "caption": "测点数量与重建精度关系",
            "current_source": "outputs/reconstruction_robustness/reconstruction_sensor_tradeoff_30dB.png",
            "report_section": "6. 测点数量优化方法",
            "status": "reference_only",
            "replacement_needed": "作为算法鲁棒性参考保留；若用于高精度结论，需用 Level 1/结构样本复跑或明确边界。",
        },
        {
            "figure_id": "Fig-05",
            "caption": "重建正则化参数扫描",
            "current_source": "outputs/reconstruction_robustness/reconstruction_lambda_scan_optimized50_30dB.png",
            "report_section": "9. 误差、鲁棒性与工程可行性分析",
            "status": "reference_only",
            "replacement_needed": "作为正则化选择参考保留；最终稿中不得把它表述为 Level 1 required 高精度证明。",
        },
        {
            "figure_id": "Fig-06",
            "caption": "空间-频谱-极化识别混淆矩阵",
            "current_source": "outputs/cst_recognition_level2/cst_recognition_confusion_matrix.png",
            "report_section": "7. 空间-频谱-极化特征辨识",
            "status": "cst_derived_ready",
            "replacement_needed": "说明当前证据来自 CST-derived element-library superposition，补充结构散射边界。",
        },
        {
            "figure_id": "Fig-07",
            "caption": "识别测点/频点删减准确率",
            "current_source": "outputs/cst_recognition_level2_ablation/recognition_ablation_accuracy.png",
            "report_section": "7. 空间-频谱-极化特征辨识",
            "status": "cst_derived_ready",
            "replacement_needed": "说明删减实验的 CST-derived 边界并与最终报告口径一致。",
        },
        {
            "figure_id": "Fig-09",
            "caption": "Level 2 简化载体遮挡前后方向图对比",
            "current_source": "outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png",
            "report_section": "7. 空间-频谱-极化特征辨识",
            "status": "bounded_structure_ready",
            "replacement_needed": "说明该图是简化 aircraft occlusion transfer，不是 full-wave airframe scattering；用于约束 element-library 证据边界。",
        },
        {
            "figure_id": "Fig-10",
            "caption": "Level 2 复合仪器误差与结构缺测压力测试策略对比",
            "current_source": "data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_by_strategy.csv",
            "report_section": "7. 空间-频谱-极化特征辨识；9. 误差、鲁棒性与工程可行性分析",
            "status": "compound_stress_ready",
            "replacement_needed": "用表格说明 severe compound stress 下 zero-fill/mask 存在低于 0.85 的失败行，frequency/sensor median imputation 是当前通过 0.85 的缓解策略；该证据仍是 CST-derived 仿真压力测试。",
        },
    ]
    return pd.DataFrame(rows)


def replacement_todo(
    scorecard: pd.DataFrame,
    master: dict[str, object],
    completion: dict[str, object],
    submission: dict[str, object],
    level1_merge: dict[str, object],
    level1_recon: dict[str, object],
    level2_merge: dict[str, object],
    level2_recog: dict[str, object],
    level1_angular: dict[str, object],
    structure_summary: dict[str, object],
    compound_summary: dict[str, object],
) -> pd.DataFrame:
    best_accuracy = nested_value(level2_recog, ("recognition", "best_accuracy"))
    compound_core = compound_summary.get("summary", {})
    compound_core = compound_core if isinstance(compound_core, dict) else {}
    compound_best = compound_core.get("best_overall_strategy", {})
    compound_best = compound_best if isinstance(compound_best, dict) else {}
    compound_worst = compound_core.get("worst_row", {})
    compound_worst = compound_worst if isinstance(compound_worst, dict) else {}
    final_ready, final_total, final_missing = final_file_state()
    best_model = nested_value(level2_recog, ("recognition", "best_model"))
    rows = [
        {
            "priority": 1,
            "task": "将 Level 1 角域校准与近场模型边界写入成稿",
            "proof": "outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; outputs/cst_level1_angular_calibration/angular_calibration_summary.json",
            "current_status": (
                f"required_complete={level1_merge.get('required_complete', 'unknown')}; "
                f"required_cases={level1_merge.get('required_complete_cases', 'unknown')}/"
                f"{level1_merge.get('required_cases', 'unknown')}; "
                f"batch_runs={level1_recon.get('completed_runs', 'unknown')}/"
                f"{level1_recon.get('queued_cases', 'unknown')}; "
                f"angular_max_nmse={level1_angular.get('max_nmse', 'unknown')}; "
                f"angular_min_corr={level1_angular.get('min_correlation', 'unknown')}"
            ),
        },
        {
            "priority": 2,
            "task": "写入 Level 2 简化结构散射/遮挡对照",
            "proof": "outputs/cst_structure_comparison/structure_comparison_summary.json; outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png",
            "current_status": (
                f"complete_samples={level2_merge.get('complete_samples', 'unknown')}/"
                f"{level2_merge.get('planned_samples', 'unknown')}; "
                f"best_model={best_model}; best_accuracy={best_accuracy}; "
                f"structure_samples={structure_summary.get('sample_count', 'unknown')}; "
                f"mean_shadow_db={structure_summary.get('mean_shadow_db', 'unknown')}; "
                f"cross_domain_accuracy={structure_summary.get('cross_domain_accuracy', 'unknown')}; "
                "evidence=CST-derived + simplified occlusion transfer"
            ),
        },
        {
            "priority": 3,
            "task": "写入 Level 2 复合仪器误差与结构缺测边界",
            "proof": "data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_by_strategy.csv; data/recognition_stress_tests/level2_compound_stress/README.md",
            "current_status": (
                f"rows={compound_core.get('row_count', 'unknown')}; "
                f"all_rows_pass_085={compound_core.get('all_rows_pass_085', 'unknown')}; "
                f"worst={compound_worst.get('candidate', 'unknown')}/"
                f"{compound_worst.get('strategy', 'unknown')}/"
                f"{compound_worst.get('stress_case', 'unknown')} "
                f"accuracy={compound_worst.get('best_accuracy', 'unknown')}; "
                f"best_strategy={compound_best.get('strategy', 'unknown')} "
                f"min_accuracy={compound_best.get('min_accuracy', 'unknown')} "
                f"mean_delta_vs_zero_fill={compound_best.get('mean_delta_vs_zero_fill', 'unknown')}"
            ),
        },
        {
            "priority": 4,
            "task": "把 Level 1/2 最新证据写入正式报告叙述",
            "proof": "docs/solution_report_draft.md; outputs/report_package/report_section_status.csv",
            "current_status": "solution_report_draft.md 已接入 Level 1 required、Level 2 full48、结构对照和复合压力测试；仍需正式排版、图表编号和 G5 风险口径复核",
        },
        {
            "priority": 5,
            "task": "导出最终 PDF/DOCX/PPTX/MP4",
            "proof": "submission/01_report/solution_report.pdf; submission/01_report/solution_report.docx; submission/02_presentation/defense_slides.pptx; submission/03_video/demo_video.mp4",
            "current_status": f"artifact_count={submission.get('artifact_count', 'unknown')}; final_files_ready={final_ready}/{final_total}; missing={final_missing}",
        },
        {
            "priority": 6,
            "task": "重跑最终审计链并确认 completion_proven",
            "proof": "outputs/completion_audit/completion_audit_summary.json; outputs/master_dashboard/master_dashboard_summary.json",
            "current_status": (
                f"completion_proven={completion.get('completion_proven', 'unknown')}; "
                f"next_blocking_gate={completion.get('next_blocking_gate', master.get('next_blocking_gate', 'unknown'))}; "
                f"missing_required_now_files={master.get('missing_required_now_files', 'unknown')}"
            ),
        },
    ]
    if not scorecard.empty:
        statuses = scorecard.get("status", pd.Series(dtype=str)).astype(str)
        needs = scorecard[~statuses.eq("Ready")]
        for idx, item in enumerate(needs.itertuples(index=False), start=10):
            rows.append(
                {
                    "priority": idx,
                    "task": f"收口评分项：{getattr(item, 'item')}",
                    "proof": getattr(item, "evidence", ""),
                    "current_status": f"{getattr(item, 'status', '')}; {getattr(item, 'missing_for_final', '')}",
                }
            )
    return pd.DataFrame(rows)


def write_markdown_readme(
    out_dir: Path,
    section_df: pd.DataFrame,
    refs_df: pd.DataFrame,
    figs_df: pd.DataFrame,
    todo_df: pd.DataFrame,
) -> None:
    final_blocker = final_blocker_text()
    content = f"""# Report package

This folder prepares the final report workflow. It is not final because {final_blocker}

## Files

| File | Meaning |
|---|---|
| `report_section_status.csv` | Section-by-section readiness and blockers. |
| `report_reference_shortlist.csv` | Grade-A references to prioritize in the final report. |
| `report_reference_shortlist.md` | Human-readable citation shortlist. |
| `report_figure_manifest.csv` | Figure/table placeholders and what must replace demo figures. |
| `report_replacement_todo.csv` | Ordered tasks before final report/PPT/video export. |
| `report_package_summary.json` | Counts and gate status. |

## Current Counts

- Report sections tracked: {len(section_df)}
- Grade-A references: {len(refs_df)}
- Figure placeholders: {len(figs_df)}
- Replacement tasks: {len(todo_df)}

## Finalization Rule

Do not mark `submission/01_report/solution_report.pdf` or `solution_report.docx` as final until:

1. Level 1 required CST cases are either improved or their metric risk is explicitly bounded.
2. Level 1 angular calibration is described as FarfieldPlot-derived angular consistency, not full-wave near-field monitor proof.
3. Level 2 recognition evidence is described with the correct CST-derived structure-boundary caveat, including the simplified structure/occlusion comparison and its non-full-wave limitation.
4. Level 2 compound instrument/dropout stress is described honestly: raw zero-fill/mask can fail 0.85, while frequency/sensor median imputation is the current mitigation candidate.
5. Report figures and tables match the latest G5 audit state.
6. The exported DOCX/PDF are visually checked and the final completion audit is rerun.
"""
    (out_dir / "README_report_package.md").write_text(content, encoding="utf-8")


def write_reference_markdown(out_dir: Path, refs_df: pd.DataFrame) -> None:
    lines = ["# Grade-A reference shortlist", ""]
    for row in refs_df.itertuples(index=False):
        lines.append(f"- **{row.id}** ({row.direction}, {row.type}): {row.reference}. Source: {row.source}")
    (out_dir / "report_reference_shortlist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build report finalization package from current draft and evidence.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--literature", default=str(DEFAULT_LITERATURE))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_text = read_text(Path(args.report))
    literature_text = read_text(Path(args.literature))
    headings = parse_headings(report_text)
    section_df = section_status(headings, report_text)
    refs_df = reference_shortlist(literature_rows(literature_text))
    figs_df = figure_manifest()
    scorecard = read_csv(DEFAULT_SCORECARD)
    master = read_json(DEFAULT_MASTER)
    completion = read_json(DEFAULT_COMPLETION)
    submission = read_json(DEFAULT_SUBMISSION)
    level1_merge = read_json(DEFAULT_LEVEL1_MERGE)
    level1_recon = read_json(DEFAULT_LEVEL1_RECON)
    level1_angular = read_json(DEFAULT_LEVEL1_ANGULAR)
    level2_merge = read_json(DEFAULT_LEVEL2_MERGE)
    level2_recog = read_json(DEFAULT_LEVEL2_RECOG)
    structure_summary = read_json(DEFAULT_STRUCTURE_COMPARISON)
    compound_summary = read_json(DEFAULT_COMPOUND_STRESS)
    todo_df = replacement_todo(
        scorecard,
        master,
        completion,
        submission,
        level1_merge,
        level1_recon,
        level2_merge,
        level2_recog,
        level1_angular,
        structure_summary,
        compound_summary,
    )

    section_df.to_csv(out_dir / "report_section_status.csv", index=False, encoding="utf-8-sig")
    refs_df.to_csv(out_dir / "report_reference_shortlist.csv", index=False, encoding="utf-8-sig")
    figs_df.to_csv(out_dir / "report_figure_manifest.csv", index=False, encoding="utf-8-sig")
    todo_df.to_csv(out_dir / "report_replacement_todo.csv", index=False, encoding="utf-8-sig")
    write_reference_markdown(out_dir, refs_df)
    write_markdown_readme(out_dir, section_df, refs_df, figs_df, todo_df)

    summary = {
        "report": rel(Path(args.report)),
        "literature": rel(Path(args.literature)),
        "traceability": rel(DEFAULT_TRACEABILITY),
        "section_count": int(len(section_df)),
        "blocked_or_demo_sections": int(section_df["readiness"].isin(["blocked_by_real_cst", "demo_needs_replacement"]).sum()),
        "g5_review_sections": int(section_df["readiness"].eq("g5_review_needed").sum()),
        "reference_only_sections": int(section_df["readiness"].eq("reference_only").sum()),
        "grade_a_references": int(len(refs_df)),
        "figure_placeholders": int(len(figs_df)),
        "demo_or_synthetic_figures": int(figs_df["status"].isin(["demo_only", "synthetic_only"]).sum()),
        "reference_only_figures": int(figs_df["status"].eq("reference_only").sum()),
        "replacement_tasks": int(len(todo_df)),
        "completion_proven": bool(completion.get("completion_proven", False)),
        "next_blocking_gate": completion.get("next_blocking_gate", master.get("next_blocking_gate", "unknown")),
        "missing_required_now_files": as_int(master.get("missing_required_now_files", 0)),
        "submission_ready": as_int(master.get("submission_ready", submission.get("ready", 0))),
        "submission_missing": as_int(submission.get("missing", 0)),
        "level1_required_complete": bool(level1_merge.get("required_complete", False)),
        "level1_completed_runs": as_int(level1_recon.get("completed_runs", 0)),
        "level1_queued_runs": as_int(level1_recon.get("queued_cases", 0)),
        "level1_angular_case_count": as_int(level1_angular.get("case_count", 0)),
        "level1_angular_max_nmse": level1_angular.get("max_nmse", "unknown"),
        "level1_angular_min_correlation": level1_angular.get("min_correlation", "unknown"),
        "level2_complete_samples": as_int(level2_merge.get("complete_samples", 0)),
        "level2_planned_samples": as_int(level2_merge.get("planned_samples", 0)),
        "level2_recognition_accuracy": nested_value(level2_recog, ("recognition", "best_accuracy")),
        "structure_sample_count": as_int(structure_summary.get("sample_count", 0)),
        "structure_mean_shadow_db": structure_summary.get("mean_shadow_db", "unknown"),
        "structure_p95_shadow_db": structure_summary.get("p95_shadow_db", "unknown"),
        "structure_cross_domain_accuracy": structure_summary.get("cross_domain_accuracy", "unknown"),
        "structure_is_full_wave_airframe": bool(structure_summary.get("is_full_wave_cst_airframe", False)),
        "compound_stress_rows": nested_value(compound_summary, ("summary", "row_count"), 0),
        "compound_all_rows_pass_085": nested_value(compound_summary, ("summary", "all_rows_pass_085"), "unknown"),
        "compound_worst_accuracy": nested_value(compound_summary, ("summary", "worst_row", "best_accuracy"), "unknown"),
        "compound_best_strategy": nested_value(compound_summary, ("summary", "best_overall_strategy", "strategy"), "unknown"),
        "compound_best_min_accuracy": nested_value(compound_summary, ("summary", "best_overall_strategy", "min_accuracy"), "unknown"),
        "is_final_report": report_final_ready(),
        "final_report_pdf": rel(FINAL_REPORT_FILES[0]),
        "final_report_docx": rel(FINAL_REPORT_FILES[1]),
        "final_blocker": final_blocker_text(),
    }
    (out_dir / "report_package_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Report package written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
