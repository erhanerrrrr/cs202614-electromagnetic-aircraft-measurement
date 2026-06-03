from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "presentation_package"
DEFAULT_FIGURES = ROOT / "outputs" / "report_package" / "report_figure_manifest.csv"
DEFAULT_REPLACEMENTS = ROOT / "outputs" / "report_package" / "report_replacement_todo.csv"
DEFAULT_MASTER = ROOT / "outputs" / "master_dashboard" / "master_dashboard_summary.json"
DEFAULT_COMPLETION = ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json"
DEFAULT_SUBMISSION = ROOT / "outputs" / "submission_index" / "submission_index_summary.json"
DEFAULT_VIDEO_ARTIFACT = ROOT / "outputs" / "video_artifact" / "demo_video_summary.json"
FINAL_FILES = [
    ("final PDF", ROOT / "submission" / "01_report" / "solution_report.pdf"),
    ("final DOCX", ROOT / "submission" / "01_report" / "solution_report.docx"),
    ("final PPTX", ROOT / "submission" / "02_presentation" / "defense_slides.pptx"),
    ("final PPT PDF", ROOT / "submission" / "02_presentation" / "defense_slides.pdf"),
    ("final MP4", ROOT / "submission" / "03_video" / "demo_video.mp4"),
]
FINAL_PRESENTATION_FILES = [
    ROOT / "submission" / "02_presentation" / "defense_slides.pptx",
    ROOT / "submission" / "02_presentation" / "defense_slides.pdf",
]
FINAL_VIDEO_FILE = ROOT / "submission" / "03_video" / "demo_video.mp4"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    for attempt in range(3):
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except EmptyDataError:
            if attempt == 2:
                return pd.DataFrame()
            time.sleep(0.2)
    return pd.DataFrame()


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def exists(path: str) -> bool:
    return (ROOT / path).exists()


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


def presentation_final_ready() -> bool:
    return all(path.exists() and path.stat().st_size > 0 for path in FINAL_PRESENTATION_FILES)


def video_final_ready() -> bool:
    return FINAL_VIDEO_FILE.exists() and FINAL_VIDEO_FILE.stat().st_size > 0


def write_csv_if_changed(df: pd.DataFrame, path: Path, warnings: list[str]) -> str:
    data = df.to_csv(index=False).encode("utf-8-sig")
    if path.exists():
        try:
            if path.read_bytes() == data:
                return "unchanged"
        except OSError:
            pass
    try:
        path.write_bytes(data)
        return "written"
    except PermissionError:
        pending = path.with_name(f"{path.stem}.pending{path.suffix}")
        pending.write_bytes(data)
        warnings.append(f"{path.name} was locked; wrote {pending.name} instead.")
        return "locked_pending"


def slide_storyboard(figures: pd.DataFrame) -> pd.DataFrame:
    figure_by_id = figures.set_index("figure_id").to_dict(orient="index") if not figures.empty else {}

    def fig_source(fig_id: str) -> tuple[str, str, str]:
        row = figure_by_id.get(fig_id, {})
        return (
            str(row.get("current_source", "")),
            str(row.get("status", "missing")),
            str(row.get("replacement_needed", "")),
        )

    rows: list[dict[str, object]] = []
    specs = [
        (
            1,
            "题目与一句话方案",
            "用一句话说明本方案是物理约束的空-频-极化联合等效源重构与受限域压缩测量。",
            "",
            "title_only",
            "开场强调：我们不是只做 CST 截图，而是建立可复现的 CST-Python 测量、重建、识别闭环。",
            "最终队伍名、成员、真实指标摘要。",
        ),
        (
            2,
            "赛题指标拆解",
            "把 2π 覆盖、12m x 10m x 8m 包络、重建精度、少测点、85% 识别准确率映射到证据。",
            "",
            "table",
            "说明评分项对应的文件、脚本和最终证据，避免评委觉得只是概念方案。",
            "scorecard 中核心项不再是 Needs CST evidence。",
        ),
        (
            3,
            "国内外方法启发",
            "展示标准近场测量、等效源重构、压缩采样、RF 指纹四条文献主线。",
            "",
            "citation_map",
            "用 IEEE 149/1720、IEEE TAP、IEEE TSP/JSTSP、RF 指纹文献支撑方法选择。",
            "参考文献格式统一。",
        ),
        (
            4,
            "总体技术路线",
            "CST 导出 nearfield/farfield，自研 Python 完成等效源重建、少测点优化和识别。",
            "",
            "pipeline_diagram",
            "强调 CST 是可信数据源，自研算法负责重建和识别，避免直接调用 CST farfield 当结果。",
            "加入 Level 1/Level 2 当前真实输出路径、指标摘要和 G5 风险边界。",
        ),
        (
            5,
            "2π 半球面传感布局",
            "展示半球面 162 测点与 12m x 10m x 8m 包络。",
            "Fig-01",
            "layout_figure",
            "说明当前选择半球面，半柱面作为工程扩展，不混入本轮执行。",
            "CST 中实际测点/monitor 截图。",
        ),
        (
            6,
            "Level 1 标准源闭环",
            "展示 required 标准源、导出路径、审计和重建指标。",
            "Fig-08",
            "result_figure",
            "先讲短偶极子和半波振子为什么用于坐标、相位、极化 sanity check，再解释角域校准与等效源近场反演的边界。",
            "真实 Level 1 required 角域校准指标已在位；同时保留等效源近场模型风险说明。",
        ),
        (
            7,
            "三维场重建算法",
            "解释 E_meas = G_nf J + n、Tikhonov/稀疏正则化、远场外推。",
            "",
            "formula_slide",
            "把公式讲成输入、传播矩阵、等效源、输出远场，不陷入数学细枝末节。",
            "用 Level 1 required 结果证明链路可复现，同时说明精度风险和改进方向。",
        ),
        (
            8,
            "少测点优化结果",
            "展示 100/75/50/25% 测点曲线和当前压缩结论。",
            "Fig-04",
            "tradeoff_chart",
            "说明当前合成结果显示 75% 稳健、50% 可候选，25% 只做极限对照。",
            "作为算法鲁棒性参考展示；若不补真实删减曲线，需标注不作为 Level 1 高精度证明。",
        ),
        (
            9,
            "Level 2 多源识别",
            "展示四类状态、多频多源、混淆矩阵和 accuracy/F1。",
            "Fig-06",
            "confusion_matrix",
            "强调识别不是单张方向图，而是空间、频谱、极化、等效源联合指纹。",
            "Level 2 full48 accuracy=1.000 已满足 85% 指标；需说明 CST-derived element-library 边界，并补充复合仪器误差/缺测压力测试的插补缓解口径。",
        ),
        (
            10,
            "结构遮挡与复合扰动边界",
            "展示简化载体遮挡前后方向图变化、遮挡 dB、cross-domain 识别结果，以及复合仪器误差/缺测下的策略边界。",
            "Fig-09",
            "structure_comparison_chart",
            "说明结构结果是 simplified aircraft occlusion transfer；复合压力测试显示原始 zero-fill/mask 在 severe dropout+bias 下可低于 0.85，frequency/sensor median imputation 是当前通过 0.85 的缓解候选。",
            "引用 mean/P95/max shadow、cross-domain accuracy、compound worst accuracy=0.733 和 imputation min accuracy=0.867，并写清二者都不是 full-wave airframe 或实测仪器校准结论。",
        ),
        (
            11,
            "创新点与工程可行性",
            "总结受限域等效源、少测点优化、空频极化指纹、可复现 CST-Python 闭环。",
            "",
            "innovation_summary",
            "把创新点和赛题评分逐项绑定。",
            "最终指标表、工程截图、Level 1 风险说明和 Level 2 边界说明齐全。",
        ),
        (
            12,
            "总结与提交物",
            "用最终指标和提交包结构收束。",
            "",
            "closing_checklist",
            "最后明确交付物包括报告、PPT、视频、代码、CST 工程、数据和附录。",
            "completion_proven=true；最终 PDF/DOCX/PPTX/MP4 存在。",
        ),
    ]

    for slide_no, title, purpose, fig_id, visual_type, notes, final_gate in specs:
        source, source_status, replacement = fig_source(fig_id) if fig_id else ("", "draft_text", "")
        rows.append(
            {
                "slide_no": slide_no,
                "title": title,
                "purpose": purpose,
                "visual_type": visual_type,
                "figure_id": fig_id,
                "current_source": source,
                "source_exists": exists(source) if source else False,
                "source_status": source_status,
                "replacement_needed": replacement,
                "speaker_note_draft": notes,
                "final_gate": final_gate,
                "is_final_ready": False,
            }
        )
    return pd.DataFrame(rows)


def video_storyboard(slides: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "time_code": "0:00-0:20",
            "screen": "题目页 + 总流程图",
            "narration": "本方案面向 2π 空域测量、三维场重建、少测点和辐射指纹识别，采用 CST-Python 闭环。",
            "linked_slide": "1,4",
            "current_asset": "",
            "replacement_needed": "最终队伍信息、Level 1/2 指标摘要和 G5 风险一句话。",
        },
        {
            "time_code": "0:20-0:50",
            "screen": "半球面测点布局",
            "narration": "当前执行选择 13 m 半径上半球面 162 个测点，覆盖 12m x 10m x 8m 被测包络。",
            "linked_slide": "5",
            "current_asset": "outputs/baseline/sensor_layout_hemisphere.png",
            "replacement_needed": "CST 中实际 monitor/测点截图或已生成测点表路径。",
        },
        {
            "time_code": "0:50-1:30",
            "screen": "Level 1 标准源 CST 截图 + 重建对比",
            "narration": "标准源用于校验坐标、极化和相位。当前 solver-safe 导出来自 FarfieldPlot 角域采样，角域校准与 CST 远场真值高度一致；等效源近场反演作为模型风险单独说明。",
            "linked_slide": "6,7",
            "current_asset": "outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png",
            "replacement_needed": "同步讲清 Level 1 模型边界：角域一致性高，但 full-wave 近场 monitor 反演仍需后续增强。",
        },
        {
            "time_code": "1:30-2:10",
            "screen": "测点删减与鲁棒性曲线",
            "narration": "用全测点、随机稀疏、优化稀疏对照，给出精度和测点数的折中。",
            "linked_slide": "8,10",
            "current_asset": "outputs/reconstruction_robustness/reconstruction_sensor_tradeoff_30dB.png",
            "replacement_needed": "标注为算法鲁棒性参考，避免替代 Level 1 required 结论。",
        },
        {
            "time_code": "2:10-2:50",
            "screen": "Level 2 多源识别混淆矩阵",
            "narration": "识别模块融合空间、频谱和极化特征，当前 Level 2 full48 准确率达到 1.000，超过 85% 指标；该结论适用于 CST-derived element-library 数据。",
            "linked_slide": "9",
            "current_asset": "outputs/cst_recognition_level2/cst_recognition_confusion_matrix.png",
            "replacement_needed": "补充 CST-derived element-library 边界说明，并衔接下一段复合压力测试。",
        },
        {
            "time_code": "2:50-3:20",
            "screen": "简化结构遮挡与复合扰动边界",
            "narration": "进一步把简化机身、机翼和尾翼遮挡迁移施加到 Level 2 数据上，量化安装效应；同时说明 severe 仪器偏差叠加结构缺测会打穿原始策略，需要用频点-测点中位数插补保护识别指标。",
            "linked_slide": "10",
            "current_asset": "outputs/cst_structure_comparison/plots/L2_comm_pair_000_1200MHz_structure_compare.png",
            "replacement_needed": "强调结构对照不是 full-wave airframe scattering，复合压力测试不是实测校准结论；表格引用 data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_by_strategy.csv。",
        },
        {
            "time_code": "3:20-3:45",
            "screen": "代码复现命令与 dashboard",
            "narration": "展示导出校验、批量合并、重建、识别、scorecard 和 completion audit 命令，证明可复现。",
            "linked_slide": "11,12",
            "current_asset": "outputs/master_dashboard/master_status_dashboard.md",
            "replacement_needed": "展示最新 G5 状态和最终审计。",
        },
        {
            "time_code": "3:45-4:10",
            "screen": "总结页",
            "narration": "总结最终指标、创新点和提交物。正式视频只在真实 CST 证据与报告/PPT一致后录制。",
            "linked_slide": "12",
            "current_asset": "",
            "replacement_needed": "最终 completion audit 和提交包截图。",
        },
    ]
    return pd.DataFrame(rows)


def asset_manifest(slides: pd.DataFrame, video: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source in slides["current_source"].dropna().astype(str).tolist() + video["current_asset"].dropna().astype(str).tolist():
        if not source:
            continue
        rows.append(
            {
                "asset": source,
                "exists": exists(source),
                "used_in": "presentation_or_video",
                "final_ready": False,
                "note": "Use with the source status from report_figure_manifest; reference-only visuals need explicit caveats.",
            }
        )
    if not rows:
        return pd.DataFrame(columns=["asset", "exists", "used_in", "final_ready", "note"])
    return pd.DataFrame(rows).drop_duplicates(subset=["asset"]).reset_index(drop=True)


def write_slide_markdown(out_dir: Path, slides: pd.DataFrame) -> None:
    lines = ["# Defense slide storyboard", ""]
    for row in slides.itertuples(index=False):
        lines.extend(
            [
                f"## {row.slide_no}. {row.title}",
                "",
                f"- Purpose: {row.purpose}",
                f"- Visual: {row.visual_type}",
                f"- Current source: `{row.current_source}`" if row.current_source else "- Current source: text/diagram placeholder",
                f"- Source status: `{row.source_status}`",
                f"- Replacement: {row.replacement_needed or row.final_gate}",
                f"- Speaker note: {row.speaker_note_draft}",
                "",
            ]
        )
    (out_dir / "defense_slide_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def write_video_markdown(out_dir: Path, video: pd.DataFrame) -> None:
    lines = ["# Demo video storyboard", ""]
    for row in video.itertuples(index=False):
        lines.extend(
            [
                f"## {row.time_code}",
                "",
                f"- Screen: {row.screen}",
                f"- Narration: {row.narration}",
                f"- Linked slide(s): {row.linked_slide}",
                f"- Current asset: `{row.current_asset}`" if row.current_asset else "- Current asset: final title/summary screen",
                f"- Replacement: {row.replacement_needed}",
                "",
            ]
        )
    (out_dir / "demo_video_storyboard.md").write_text("\n".join(lines), encoding="utf-8")


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    presentation_state = "final PPTX/PDF exported" if summary.get("is_final_presentation") else "PPTX/PDF export pending"
    video_state = "final MP4 exported" if summary.get("is_final_video") else "final MP4 pending"
    content = f"""# Presentation package

This folder prepares the defense slide deck and demo video. Current state: {presentation_state}; {video_state}. G5 remains partial until the final video and completion audit close.

## Files

| File | Meaning |
|---|---|
| `defense_slide_storyboard.csv` | 12-slide defense deck plan with visual source and final gate. |
| `defense_slide_storyboard.md` | Human-readable slide-by-slide outline and speaker notes. |
| `demo_video_storyboard.csv` | 3-5 minute video screen/narration plan. |
| `demo_video_storyboard.md` | Human-readable demo video script. |
| `presentation_asset_manifest.csv` | Draft assets currently available for slides/video. |
| `presentation_replacement_todo.csv` | Real CST and final output blockers to clear before export. |
| `presentation_package_summary.json` | Counts and final readiness flags. |

## Current Counts

- Slides planned: {summary["slide_count"]}
- Video segments planned: {summary["video_segment_count"]}
- Draft assets tracked: {summary["asset_count"]}
- Existing draft assets: {summary["existing_asset_count"]}
- Final-ready slides: {summary["final_ready_slides"]}

## Finalization Rule

Do not mark `submission/02_presentation/defense_slides.pptx` or `submission/03_video/demo_video.mp4` as final until the deck/video match the final report, Level 1 angular/near-field model-boundary wording, Level 2 simplified structure-boundary caveats, and the compound instrument/dropout stress mitigation caveat.
After export, rerun the completion audit; `completion_proven=true` is the final submit gate, not a prerequisite for drafting the export.
"""
    (out_dir / "README_presentation_package.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build defense slide and demo video preparation package.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--figures", default=str(DEFAULT_FIGURES))
    parser.add_argument("--replacements", default=str(DEFAULT_REPLACEMENTS))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    figures = read_csv(Path(args.figures))
    replacements = read_csv(Path(args.replacements))
    master = read_json(DEFAULT_MASTER)
    completion = read_json(DEFAULT_COMPLETION)
    submission = read_json(DEFAULT_SUBMISSION)
    video_artifact = read_json(DEFAULT_VIDEO_ARTIFACT)
    slides = slide_storyboard(figures)
    video = video_storyboard(slides)
    assets = asset_manifest(slides, video)
    write_warnings: list[str] = []

    csv_write_status = {
        "defense_slide_storyboard.csv": write_csv_if_changed(slides, out_dir / "defense_slide_storyboard.csv", write_warnings),
        "demo_video_storyboard.csv": write_csv_if_changed(video, out_dir / "demo_video_storyboard.csv", write_warnings),
        "presentation_asset_manifest.csv": write_csv_if_changed(assets, out_dir / "presentation_asset_manifest.csv", write_warnings),
        "presentation_replacement_todo.csv": write_csv_if_changed(replacements, out_dir / "presentation_replacement_todo.csv", write_warnings),
    }
    write_slide_markdown(out_dir, slides)
    write_video_markdown(out_dir, video)

    summary = {
        "pptx": "submission\\02_presentation\\defense_slides.pptx",
        "pdf": "submission\\02_presentation\\defense_slides.pdf",
        "video": "submission\\03_video\\demo_video.mp4",
        "slide_count": int(len(slides)),
        "video_segment_count": int(len(video)),
        "asset_count": int(len(assets)),
        "existing_asset_count": int(assets["exists"].sum()) if not assets.empty else 0,
        "final_ready_slides": int(len(slides)) if presentation_final_ready() else int(slides["is_final_ready"].sum()),
        "completion_proven": bool(completion.get("completion_proven", False)),
        "next_blocking_gate": completion.get("next_blocking_gate", master.get("next_blocking_gate", "unknown")),
        "missing_required_now_files": as_int(master.get("missing_required_now_files", 0)),
        "submission_ready": as_int(master.get("submission_ready", submission.get("ready", 0))),
        "submission_missing": as_int(submission.get("missing", 0)),
        "is_final_presentation": presentation_final_ready(),
        "is_final_video": video_final_ready(),
        "video_has_narration": bool(video_artifact.get("has_narration", False)),
        "video_qa_note": video_artifact.get("qa_note", ""),
        "final_blocker": final_blocker_text(),
        "csv_write_status": csv_write_status,
        "write_warnings": write_warnings,
    }
    (out_dir / "presentation_package_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, summary)

    print(f"Presentation package written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
