from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_REPORT = ROOT / "docs" / "project_progress_report.md"
REPORT_DIR = ROOT / "docs" / "progress_reports"
OUT_DIR = ROOT / "outputs" / "progress_report"
CURRENT_PROGRESS_BRIEF_DOC = REPORT_DIR / "current_progress_brief.md"
CURRENT_PROGRESS_BRIEF_DOC_REL = CURRENT_PROGRESS_BRIEF_DOC.relative_to(ROOT).as_posix()
LATEST_MENTOR_BRIEF = REPORT_DIR / "latest_mentor_brief.md"
LATEST_MENTOR_BRIEF_REL = LATEST_MENTOR_BRIEF.relative_to(ROOT).as_posix()
MENTOR_PORTAL_DOC = REPORT_DIR / "mentor_portal.md"
MENTOR_PORTAL_DOC_REL = MENTOR_PORTAL_DOC.relative_to(ROOT).as_posix()
MEETING_BRIEF_DOC = REPORT_DIR / "meeting_brief.md"
MEETING_BRIEF_DOC_REL = MEETING_BRIEF_DOC.relative_to(ROOT).as_posix()
DAILY_DIGEST_DOC = REPORT_DIR / "daily_digest.md"
DAILY_DIGEST_DOC_REL = DAILY_DIGEST_DOC.relative_to(ROOT).as_posix()
EVIDENCE_MAP_DOC = REPORT_DIR / "evidence_map.md"
EVIDENCE_MAP_DOC_REL = EVIDENCE_MAP_DOC.relative_to(ROOT).as_posix()
DECISION_BRIEF_DOC = REPORT_DIR / "decision_brief.md"
DECISION_BRIEF_DOC_REL = DECISION_BRIEF_DOC.relative_to(ROOT).as_posix()
MENTOR_QA_DOC = REPORT_DIR / "mentor_qa.md"
MENTOR_QA_DOC_REL = MENTOR_QA_DOC.relative_to(ROOT).as_posix()
G5_CLOSURE_DOC = REPORT_DIR / "g5_closure_brief.md"
G5_CLOSURE_DOC_REL = G5_CLOSURE_DOC.relative_to(ROOT).as_posix()
G5_STALL_ALERT_DOC = REPORT_DIR / "g5_stall_alert.md"
G5_STALL_ALERT_DOC_REL = G5_STALL_ALERT_DOC.relative_to(ROOT).as_posix()
MENTOR_SNAPSHOT_DOC = REPORT_DIR / "mentor_snapshot.md"
MENTOR_SNAPSHOT_DOC_REL = MENTOR_SNAPSHOT_DOC.relative_to(ROOT).as_posix()
LATEST_CHANGE_DOC = REPORT_DIR / "latest_change_note.md"
LATEST_CHANGE_DOC_REL = LATEST_CHANGE_DOC.relative_to(ROOT).as_posix()
NEXT_ACTION_DOC = REPORT_DIR / "next_action_brief.md"
NEXT_ACTION_DOC_REL = NEXT_ACTION_DOC.relative_to(ROOT).as_posix()
RISK_REGISTER_DOC = REPORT_DIR / "risk_register.md"
RISK_REGISTER_DOC_REL = RISK_REGISTER_DOC.relative_to(ROOT).as_posix()
SUBMISSION_READINESS_DOC = REPORT_DIR / "submission_readiness.md"
SUBMISSION_READINESS_DOC_REL = SUBMISSION_READINESS_DOC.relative_to(ROOT).as_posix()
FINAL_DELIVERY_GAP_DOC = REPORT_DIR / "final_delivery_gap_board.md"
FINAL_DELIVERY_GAP_DOC_REL = FINAL_DELIVERY_GAP_DOC.relative_to(ROOT).as_posix()
FINAL_DELIVERY_GAP_CHART = REPORT_DIR / "assets" / "final_delivery_gap_board.png"
FINAL_DELIVERY_GAP_CHART_REL = FINAL_DELIVERY_GAP_CHART.relative_to(REPORT_DIR).as_posix()
FINAL_DELIVERY_GAP_CHART_OUT = OUT_DIR / "assets" / "final_delivery_gap_board.png"
FINAL_DELIVERY_GAP_CHART_OUT_REL = FINAL_DELIVERY_GAP_CHART_OUT.relative_to(ROOT).as_posix()
WATCH_SCOPE_DOC = REPORT_DIR / "watch_scope.md"
WATCH_SCOPE_DOC_REL = WATCH_SCOPE_DOC.relative_to(ROOT).as_posix()
PROGRESS_PROTOCOL_DOC = REPORT_DIR / "progress_update_protocol.md"
PROGRESS_PROTOCOL_DOC_REL = PROGRESS_PROTOCOL_DOC.relative_to(ROOT).as_posix()
STATUS_REVIEW_DOC = REPORT_DIR / "status_review_log.md"
STATUS_REVIEW_DOC_REL = STATUS_REVIEW_DOC.relative_to(ROOT).as_posix()
LATEST_STATUS_REVIEW_DOC = REPORT_DIR / "latest_status_review.md"
LATEST_STATUS_REVIEW_DOC_REL = LATEST_STATUS_REVIEW_DOC.relative_to(ROOT).as_posix()
LATEST_STATUS_REVIEW_CHART = REPORT_DIR / "assets" / "latest_status_review.png"
LATEST_STATUS_REVIEW_CHART_REL = LATEST_STATUS_REVIEW_CHART.relative_to(REPORT_DIR).as_posix()
LATEST_STATUS_REVIEW_CHART_OUT = OUT_DIR / "assets" / "latest_status_review.png"
LATEST_STATUS_REVIEW_CHART_OUT_REL = LATEST_STATUS_REVIEW_CHART_OUT.relative_to(ROOT).as_posix()
STATUS_REVIEW_LOG = OUT_DIR / "status_review_log.csv"
STATUS_REVIEW_LOG_REL = STATUS_REVIEW_LOG.relative_to(ROOT).as_posix()
PROGRESS_INDEX_DOC = REPORT_DIR / "progress_index.md"
PROGRESS_INDEX_DOC_REL = PROGRESS_INDEX_DOC.relative_to(ROOT).as_posix()


FINAL_FILES = [
    ("正式报告 PDF", "submission/01_report/solution_report.pdf"),
    ("正式报告 DOCX", "submission/01_report/solution_report.docx"),
    ("答辩 PPTX", "submission/02_presentation/defense_slides.pptx"),
    ("答辩 PPT PDF", "submission/02_presentation/defense_slides.pdf"),
    ("演示视频 MP4", "submission/03_video/demo_video.mp4"),
]

KEY_ARTIFACTS = [
    ("总控状态看板", "outputs/master_dashboard/master_status_dashboard.md", "一页看清当前 gate、阻塞点和三人任务队列。"),
    ("完成度审计", "outputs/completion_audit/completion_audit.md", "保守判断哪些 gate 已完成、哪个 gate 未关闭。"),
    ("赛题要求矩阵", "outputs/problem_requirements/problem_requirements_matrix.md", "将赛题要求、评分项和已有证据逐项对齐。"),
    ("评分证据板", "outputs/scorecard/scorecard.md", "支撑报告/PPT 的评分项证据摘要。"),
    ("提交包索引", "outputs/submission_index/submission_package_index.md", "检查报告、代码、数据、CST、附录的提交状态。"),
    ("进展历史台账", "outputs/progress_report/progress_history.csv", "记录各阶段标记、Gate、提交包和最终交付物状态。"),
    ("当前进展简报", "docs/progress_reports/current_progress_brief.md", "每次巡检刷新，短版回答目前做了什么、产物是什么、下一步是什么。"),
    ("导师阅读门户", "docs/progress_reports/mentor_portal.md", "按阅读时间和用途导航所有导师汇报入口。"),
    ("组会汇报稿", "docs/progress_reports/meeting_brief.md", "可直接用于组会口头汇报的进展、产物、风险和请求。"),
    ("每日进展汇总", "docs/progress_reports/daily_digest.md", "按日期汇总阶段标记、产物演进、风险和图表。"),
    ("导师证据映射", "docs/progress_reports/evidence_map.md", "把关键结论逐条映射到证据文件和当前状态。"),
    ("导师决策清单", "docs/progress_reports/decision_brief.md", "集中列出当前需要导师拍板的未关闭问题。"),
    ("导师问答卡", "docs/progress_reports/mentor_qa.md", "预置导师常问问题、建议回答和证据入口。"),
    ("G5 关闭路线", "docs/progress_reports/g5_closure_brief.md", "集中说明从当前状态到最终提交态的关闭路线和判据。"),
    ("G5 停滞告警", "docs/progress_reports/g5_stall_alert.md", "当 G5 多轮未关闭时，集中提示连续复核次数、责任项和关闭证据。"),
    ("导师 30 秒快照", "docs/progress_reports/mentor_snapshot.md", "用最短篇幅呈现当前结论、产物、缺口和图表。"),
    ("本次变化说明", "docs/progress_reports/latest_change_note.md", "单独说明最新阶段相对上一阶段变化了什么。"),
    ("下一步行动清单", "docs/progress_reports/next_action_brief.md", "按负责人列出下一步任务、关闭证据和阻塞项。"),
    ("风险登记表", "docs/progress_reports/risk_register.md", "集中登记当前风险、影响、负责人、缓解动作和关闭证据。"),
    ("提交就绪清单", "docs/progress_reports/submission_readiness.md", "检查正式提交文件、completion 和 submission 草稿包状态。"),
    ("最终交付缺口板", "docs/progress_reports/final_delivery_gap_board.md", "按最终文件倒推负责人、依赖项、关闭证据和当前状态。"),
    ("阶段索引", "docs/progress_reports/progress_index.md", "按时间线汇总阶段标记、状态和导师汇报链接。"),
    ("巡检范围说明", "docs/progress_reports/watch_scope.md", "说明长期跟进时监测哪些关键文件和最终交付物。"),
    ("跟进操作规程", "docs/progress_reports/progress_update_protocol.md", "说明何时标记阶段、何时跳过复核、每次汇报前后要检查什么。"),
    ("状态复核台账", "docs/progress_reports/status_review_log.md", "记录无变化巡检，不打扰阶段归档但保留长期跟进痕迹。"),
    ("最新巡检状态卡", "docs/progress_reports/latest_status_review.md", "每次巡检都会刷新的实时状态卡，显示是否归档、最近复核和当前 G5 缺口。"),
    ("草稿提交包", "submission/", "当前可预览的最终提交目录结构。"),
]

WATCHED_FILES = [
    "README.md",
    "src/build_progress_report.py",
    "src/build_submission_draft.py",
    "src/build_presentation_package.py",
    "docs/solution_report_draft.md",
    "docs/final_submission_package_plan.md",
    "docs/project_file_index.md",
    "docs/reproduce_commands.md",
    "outputs/master_dashboard/master_dashboard_summary.json",
    "outputs/master_dashboard/master_gate_summary.csv",
    "outputs/master_dashboard/master_next_actions.csv",
    "outputs/completion_audit/completion_audit_summary.json",
    "outputs/submission_index/submission_index_summary.json",
    "outputs/scorecard/scorecard.md",
    "outputs/problem_requirements/problem_requirements_matrix.md",
    "outputs/report_package/report_package_summary.json",
    "outputs/presentation_package/presentation_package_summary.json",
    "submission/submission_draft_summary.json",
    "submission/01_report/solution_report.pdf",
    "submission/01_report/solution_report.docx",
    "submission/02_presentation/defense_slides.pptx",
    "submission/02_presentation/defense_slides.pdf",
    "submission/03_video/demo_video.mp4",
]

WATCHED_FILE_NOTES = {
    "README.md": "项目入口说明和当前小目标。",
    "src/build_progress_report.py": "进展跟踪、导师汇报、图表和历史台账生成脚本。",
    "src/build_submission_draft.py": "最终提交草稿包生成脚本。",
    "src/build_presentation_package.py": "答辩 PPT 与演示视频素材包生成脚本。",
    "docs/solution_report_draft.md": "正式报告草稿主内容。",
    "docs/final_submission_package_plan.md": "最终报告、PPT、视频和提交包规划。",
    "docs/project_file_index.md": "项目文件索引和阅读入口。",
    "docs/reproduce_commands.md": "复现命令和阶段巡检命令。",
    "outputs/master_dashboard/master_dashboard_summary.json": "总控 dashboard 机器可读摘要。",
    "outputs/master_dashboard/master_gate_summary.csv": "各 Gate 状态表。",
    "outputs/master_dashboard/master_next_actions.csv": "下一步任务队列表。",
    "outputs/completion_audit/completion_audit_summary.json": "完成度审计摘要。",
    "outputs/submission_index/submission_index_summary.json": "提交物索引摘要。",
    "outputs/scorecard/scorecard.md": "评分证据板。",
    "outputs/problem_requirements/problem_requirements_matrix.md": "赛题要求矩阵。",
    "outputs/cst_structure_comparison/structure_comparison_summary.json": "Level 2 简化结构遮挡对照摘要。",
    "outputs/report_package/report_package_summary.json": "报告包机器可读摘要，记录章节、G5 口径、图表和关键指标。",
    "outputs/presentation_package/presentation_package_summary.json": "答辩 PPT 与演示视频素材包机器可读摘要。",
    "submission/submission_draft_summary.json": "当前 submission 草稿包摘要。",
    "submission/01_report/solution_report.pdf": "正式报告 PDF。",
    "submission/01_report/solution_report.docx": "正式报告 DOCX。",
    "submission/02_presentation/defense_slides.pptx": "答辩 PPTX。",
    "submission/02_presentation/defense_slides.pdf": "答辩 PPT PDF。",
    "submission/03_video/demo_video.mp4": "演示视频 MP4。",
}

WATCHED_JSON_IGNORED_KEYS = {
    "outputs/presentation_package/presentation_package_summary.json": {
        "csv_write_status",
        "write_warnings",
    },
}


def read_json(rel_path: str) -> dict[str, Any]:
    path = ROOT / rel_path
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(rel_path: str) -> list[dict[str, str]]:
    path = ROOT / rel_path
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def file_digest(path: Path) -> str:
    if not path.exists() or not path.is_file():
        return ""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def watched_file_signature(rel_path: str, path: Path, exists: bool, raw_size: int, raw_sha256: str) -> tuple[str, int, str]:
    ignored_keys = WATCHED_JSON_IGNORED_KEYS.get(rel_path)
    if exists and ignored_keys:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return "raw", raw_size, raw_sha256
        if isinstance(data, dict):
            semantic_data = {key: value for key, value in data.items() if key not in ignored_keys}
            semantic_bytes = json.dumps(
                semantic_data,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            return "json-semantic", len(semantic_bytes), content_digest(semantic_bytes)
    return "raw", raw_size, raw_sha256


def watched_manifest() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for rel_path in WATCHED_FILES:
        path = ROOT / rel_path
        exists = path.exists() and path.is_file()
        stat = path.stat() if exists else None
        raw_size = int(stat.st_size) if stat else 0
        raw_sha256 = file_digest(path) if exists else ""
        fingerprint_mode, fingerprint_size, fingerprint_sha256 = watched_file_signature(
            rel_path,
            path,
            exists,
            raw_size,
            raw_sha256,
        )
        item = {
            "path": rel_path,
            "exists": exists,
            "size": raw_size,
            "mtime_ns": int(stat.st_mtime_ns) if stat else 0,
            "sha256": raw_sha256,
            "fingerprint_mode": fingerprint_mode,
            "fingerprint_size": fingerprint_size,
            "fingerprint_sha256": fingerprint_sha256,
        }
        files.append(item)
        fingerprint_item = {
            "path": rel_path,
            "exists": exists,
            "fingerprint_mode": fingerprint_mode,
            "fingerprint_size": fingerprint_size,
            "fingerprint_sha256": fingerprint_sha256,
        }
        digest.update(json.dumps(fingerprint_item, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return {
        "fingerprint": digest.hexdigest(),
        "files": files,
    }


def write_manifest_files(ctx: dict[str, Any]) -> None:
    manifest = ctx.get("watched_manifest", {})
    if not manifest:
        return
    write_json(OUT_DIR / "watch_manifest_latest.json", manifest)
    write_json(OUT_DIR / "watch_manifests" / f"{ctx['marker']}_watch_manifest.json", manifest)


def previous_watch_manifest(previous_marker: str) -> dict[str, Any]:
    if not previous_marker:
        return {}
    path = OUT_DIR / "watch_manifests" / f"{previous_marker}_watch_manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def watch_item_signature(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "exists": bool(item.get("exists")),
        "mode": item.get("fingerprint_mode", "raw"),
        "size": item.get("fingerprint_size", item.get("size", 0)),
        "sha256": item.get("fingerprint_sha256", item.get("sha256", "")),
    }


def summarize_watch_changes(previous: dict[str, Any], current: dict[str, Any]) -> list[str]:
    if not previous or not current:
        return []
    previous_files = {item.get("path", ""): item for item in previous.get("files", [])}
    changes: list[str] = []
    for item in current.get("files", []):
        rel_path = item.get("path", "")
        old = previous_files.get(rel_path)
        if old is None:
            changes.append(f"{rel_path}: 新增监测")
            continue
        if bool(old.get("exists")) != bool(item.get("exists")):
            changes.append(f"{rel_path}: exists {old.get('exists')} -> {item.get('exists')}")
        elif watch_item_signature(old) != watch_item_signature(item):
            changes.append(f"{rel_path}: 内容已更新")
    return changes


def md(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    text = "" if value is None else str(value)
    return text.replace("\n", "<br>").replace("|", "\\|")


def table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md(cell) for cell in row) + " |")
    return "\n".join(lines)


def now_string(value: str | None) -> str:
    if value:
        return value
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")


def marker_from_timestamp(timestamp: str) -> str:
    digits = "".join(ch for ch in timestamp if ch.isdigit())
    if len(digits) >= 14:
        return f"M-{digits[:8]}-{digits[8:14]}"
    if len(digits) >= 12:
        return f"M-{digits[:8]}-{digits[8:12]}"
    return "M-current"


def filename_from_timestamp(timestamp: str) -> str:
    digits = "".join(ch for ch in timestamp if ch.isdigit())
    if len(digits) >= 14:
        return f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}_{digits[8:14]}_mentor_brief.md"
    if len(digits) >= 12:
        return f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}_{digits[8:12]}_mentor_brief.md"
    return "current_mentor_brief.md"


def archived_mentor_reports() -> list[Path]:
    return sorted(
        [p for p in REPORT_DIR.glob("*_mentor_brief.md") if p.is_file() and p.name != LATEST_MENTOR_BRIEF.name],
        reverse=True,
    )


def archive_timestamp_label(path: Path) -> str:
    stem = path.stem.replace("_mentor_brief", "")
    if "_" not in stem:
        return stem
    date_part, hm = stem.split("_", 1)
    if len(hm) == 6:
        return f"{date_part} {hm[:2]}:{hm[2:4]}:{hm[4:]} +0800"
    if len(hm) == 4:
        return f"{date_part} {hm[:2]}:{hm[2:]} +0800"
    return stem.replace("_", " ")


def archive_marker(path: Path) -> str:
    digits = "".join(ch for ch in path.name if ch.isdigit())
    if len(digits) >= 14:
        return f"M-{digits[:8]}-{digits[8:14]}"
    if len(digits) >= 12:
        return f"M-{digits[:8]}-{digits[8:12]}"
    return "M-archive"


def status_counts(gates: list[dict[str, str]], completion: dict[str, Any]) -> dict[str, int]:
    counts = {
        "complete": int(completion.get("complete", 0) or 0),
        "partial": int(completion.get("partial", 0) or 0),
        "missing": int(completion.get("missing", 0) or 0),
    }
    if any(counts.values()):
        return counts
    for row in gates:
        status = row.get("status", "missing")
        counts[status] = counts.get(status, 0) + 1
    return counts


def final_file_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for label, rel_path in FINAL_FILES:
        rows.append([label, rel_path, "存在" if (ROOT / rel_path).exists() else "缺失"])
    return rows


def final_file_mermaid() -> str:
    lines = [
        "flowchart TB",
        '  A["当前 submission 草稿包"]',
    ]
    for idx, (label, rel_path) in enumerate(FINAL_FILES, start=1):
        status = "存在" if (ROOT / rel_path).exists() else "缺失"
        lines.append(f'  F{idx}["{label}: {status}"]')
        lines.append(f"  A --> F{idx}")
    lines.append('  Z["最终提交态: 取决于正式文件齐全和 completion_proven=true"]')
    for idx in range(1, len(FINAL_FILES) + 1):
        lines.append(f"  F{idx} --> Z")
    return "\n".join(lines)


def gate_flow(gates: list[dict[str, str]]) -> str:
    if not gates:
        return "flowchart LR\n  A[\"尚未生成 gate summary\"]"
    lines = ["flowchart LR"]
    prev_id = ""
    for idx, row in enumerate(gates):
        node_id = f"G{idx}"
        gate = row.get("gate", f"gate-{idx}")
        requirement = row.get("requirement", "")
        status = row.get("status", "unknown")
        short_req = requirement[:20] + ("..." if len(requirement) > 20 else "")
        lines.append(f'  {node_id}["{gate} {short_req}: {status}"]')
        if prev_id:
            lines.append(f"  {prev_id} --> {node_id}")
        prev_id = node_id
    return "\n".join(lines)


def pie(title: str, values: dict[str, int]) -> str:
    lines = [f"pie title {title}"]
    for key, value in values.items():
        lines.append(f'  "{key}" : {int(value)}')
    return "\n".join(lines)


def chart_asset_paths(marker: str) -> dict[str, str]:
    return {
        "status_overview_name": f"{marker}_status_overview.png",
        "deliverables_name": f"{marker}_final_deliverables.png",
        "history_name": f"{marker}_progress_history.png",
        "project_status_overview": f"progress_reports/assets/{marker}_status_overview.png",
        "project_deliverables": f"progress_reports/assets/{marker}_final_deliverables.png",
        "project_history": f"progress_reports/assets/{marker}_progress_history.png",
        "mentor_status_overview": f"assets/{marker}_status_overview.png",
        "mentor_deliverables": f"assets/{marker}_final_deliverables.png",
        "mentor_history": f"assets/{marker}_progress_history.png",
        "docs_status_overview": f"docs/progress_reports/assets/{marker}_status_overview.png",
        "docs_deliverables": f"docs/progress_reports/assets/{marker}_final_deliverables.png",
        "docs_history": f"docs/progress_reports/assets/{marker}_progress_history.png",
        "outputs_status_overview": f"outputs/progress_report/assets/{marker}_status_overview.png",
        "outputs_deliverables": f"outputs/progress_report/assets/{marker}_final_deliverables.png",
        "outputs_history": f"outputs/progress_report/assets/{marker}_progress_history.png",
    }


def save_progress_charts(ctx: dict[str, Any]) -> dict[str, str]:
    assets = chart_asset_paths(ctx["marker"])
    docs_asset_dir = REPORT_DIR / "assets"
    out_asset_dir = OUT_DIR / "assets"
    docs_asset_dir.mkdir(parents=True, exist_ok=True)
    out_asset_dir.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except Exception as exc:
        error_path = OUT_DIR / "chart_generation_error.txt"
        write_text(error_path, f"Chart generation skipped: {exc}\n")
        assets["chart_error"] = error_path.relative_to(ROOT).as_posix()
        return assets

    gate_counts = ctx["gate_counts"]
    submission = ctx["submission"]
    submission_values = {
        "ready": int(submission.get("ready", 0) or 0),
        "draft": int(submission.get("draft_or_source_ready", 0) or 0),
        "blocked": int(submission.get("blocked", 0) or 0),
        "missing": int(submission.get("missing", 0) or 0),
    }
    colors = {
        "complete": "#2E7D32",
        "partial": "#F9A825",
        "missing": "#C62828",
        "ready": "#1976D2",
        "draft": "#7B1FA2",
        "blocked": "#D84315",
        "exists": "#2E7D32",
    }

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3), dpi=160)
    nonzero_gate_items = [(label, int(value)) for label, value in gate_counts.items() if int(value) > 0]
    if not nonzero_gate_items:
        nonzero_gate_items = [("none", 1)]
    gate_labels = [label for label, _ in nonzero_gate_items]
    gate_values = [value for _, value in nonzero_gate_items]
    gate_colors = [colors.get(k, "#757575") for k in gate_labels]
    axes[0].pie(
        gate_values,
        labels=gate_labels,
        colors=gate_colors,
        autopct=lambda pct: f"{pct:.0f}%" if pct > 0 else "",
        startangle=90,
        textprops={"fontsize": 9},
    )
    axes[0].set_title("Gate status", fontsize=12, weight="bold")

    sub_labels = list(submission_values.keys())
    sub_values = [submission_values[k] for k in sub_labels]
    sub_colors = [colors.get(k, "#757575") for k in sub_labels]
    axes[1].bar(sub_labels, sub_values, color=sub_colors)
    axes[1].set_title("Submission index", fontsize=12, weight="bold")
    axes[1].set_ylabel("Items")
    ymax = max(sub_values + [1])
    axes[1].set_ylim(0, ymax * 1.18)
    for idx, value in enumerate(sub_values):
        axes[1].text(idx, value + ymax * 0.03, str(value), ha="center", fontsize=9)
    axes[1].spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Progress snapshot {ctx['marker']}", fontsize=14, weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))

    status_docs_path = docs_asset_dir / assets["status_overview_name"]
    fig.savefig(status_docs_path, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(status_docs_path, out_asset_dir / assets["status_overview_name"])

    final_labels = ["Report PDF", "Report DOCX", "Slides PPTX", "Slides PDF", "Demo MP4"]
    final_items = list(ctx["final_status"].items())
    fig, ax = plt.subplots(figsize=(10.5, 2.7), dpi=160)
    ax.set_xlim(0, len(final_items))
    ax.set_ylim(0, 1)
    ax.axis("off")
    for idx, ((_, ok), label) in enumerate(zip(final_items, final_labels)):
        face = colors["exists"] if ok else colors["missing"]
        status = "READY" if ok else "MISSING"
        ax.add_patch(Rectangle((idx + 0.05, 0.18), 0.9, 0.64, facecolor=face, edgecolor="#263238", linewidth=1.0))
        ax.text(idx + 0.5, 0.58, label, ha="center", va="center", color="white", fontsize=10, weight="bold")
        ax.text(idx + 0.5, 0.36, status, ha="center", va="center", color="white", fontsize=9)
    ax.set_title("Final deliverables", fontsize=13, weight="bold")
    fig.tight_layout()

    deliverables_docs_path = docs_asset_dir / assets["deliverables_name"]
    fig.savefig(deliverables_docs_path, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(deliverables_docs_path, out_asset_dir / assets["deliverables_name"])

    return assets


def progress_history_row(ctx: dict[str, Any]) -> dict[str, str]:
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_status = ctx["final_status"]
    return {
        "timestamp": str(ctx["timestamp"]),
        "marker": str(ctx["marker"]),
        "completion_proven": str(bool(ctx["master"].get("completion_proven", False))).lower(),
        "next_blocking_gate": str(ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))),
        "gate_complete": str(int(counts.get("complete", 0) or 0)),
        "gate_partial": str(int(counts.get("partial", 0) or 0)),
        "gate_missing": str(int(counts.get("missing", 0) or 0)),
        "submission_ready": str(int(submission.get("ready", 0) or 0)),
        "submission_draft_or_source_ready": str(int(submission.get("draft_or_source_ready", 0) or 0)),
        "submission_blocked": str(int(submission.get("blocked", 0) or 0)),
        "submission_missing": str(int(submission.get("missing", 0) or 0)),
        "submission_draft_items": str(int(draft.get("copied_or_generated", 0) or 0)),
        "final_report_pdf": str(bool(final_status.get("正式报告 PDF", False))).lower(),
        "final_report_docx": str(bool(final_status.get("正式报告 DOCX", False))).lower(),
        "final_pptx": str(bool(final_status.get("答辩 PPTX", False))).lower(),
        "final_ppt_pdf": str(bool(final_status.get("答辩 PPT PDF", False))).lower(),
        "final_mp4": str(bool(final_status.get("演示视频 MP4", False))).lower(),
        "watched_fingerprint": str(ctx.get("watched_manifest", {}).get("fingerprint", "")),
        "latest_mentor_brief": str(ctx["latest_report"]),
        "event_type": str(ctx.get("event_type", "")),
        "note": str(ctx.get("note", "")),
        "change_summary": "；".join(str(item) for item in ctx.get("changes_since_previous", [])),
    }


def read_progress_history() -> list[dict[str, str]]:
    history_path = OUT_DIR / "progress_history.csv"
    if history_path.exists():
        with history_path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    return []


def read_status_review_log() -> list[dict[str, str]]:
    if STATUS_REVIEW_LOG.exists():
        with STATUS_REVIEW_LOG.open("r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    return []


def status_review_row(summary: dict[str, Any]) -> dict[str, str]:
    gate_counts = summary.get("gate_counts", {})
    submission = summary.get("submission", {})
    draft = summary.get("draft", {})
    final_status = summary.get("final_status", {})
    return {
        "timestamp": str(summary.get("timestamp", "")),
        "marker": str(summary.get("marker", "")),
        "event_type": str(summary.get("event_type", "")),
        "skipped": str(bool(summary.get("skipped", False))).lower(),
        "archive_written": str(bool(summary.get("archive_written", False))).lower(),
        "latest_mentor_brief": str(summary.get("latest_mentor_brief", "")),
        "completion_proven": str(bool(summary.get("completion_proven", False))).lower(),
        "next_blocking_gate": str(summary.get("next_blocking_gate", "")),
        "gate_complete": str(int(gate_counts.get("complete", 0) or 0)),
        "gate_partial": str(int(gate_counts.get("partial", 0) or 0)),
        "gate_missing": str(int(gate_counts.get("missing", 0) or 0)),
        "submission_ready": str(int(submission.get("ready", 0) or 0)),
        "submission_draft_or_source_ready": str(int(submission.get("draft_or_source_ready", 0) or 0)),
        "submission_blocked": str(int(submission.get("blocked", 0) or 0)),
        "submission_missing": str(int(submission.get("missing", 0) or 0)),
        "draft_copied_or_generated": str(int(draft.get("copied_or_generated", 0) or 0)),
        "draft_missing": str(int(draft.get("missing", 0) or 0)),
        "draft_is_final": str(bool(draft.get("is_final", False))).lower(),
        "final_ready": str(sum(1 for ok in final_status.values() if ok)),
        "final_total": str(len(final_status) or len(FINAL_FILES)),
        "watched_fingerprint": str(summary.get("watched_fingerprint", "")),
        "skip_reason": str(summary.get("skip_reason", "")),
        "change_summary": "；".join(str(item) for item in summary.get("changes_since_previous", [])),
    }


def update_status_review_log(summary: dict[str, Any]) -> list[dict[str, str]]:
    rows = read_status_review_log()
    row = status_review_row(summary)
    rows_by_timestamp = {item.get("timestamp", ""): item for item in rows if item.get("timestamp")}
    rows_by_timestamp[row["timestamp"]] = row
    rows = sorted(rows_by_timestamp.values(), key=lambda item: item.get("timestamp", ""))
    STATUS_REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_REVIEW_LOG.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def remove_status_review_log_entry(timestamp: str) -> list[dict[str, str]]:
    rows = read_status_review_log()
    if not rows:
        return []
    fieldnames = list(rows[0].keys())
    rows = [row for row in rows if row.get("timestamp", "") != timestamp]
    STATUS_REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
    with STATUS_REVIEW_LOG.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def current_metric_row(ctx: dict[str, Any]) -> dict[str, str]:
    row = progress_history_row(ctx)
    row.pop("latest_mentor_brief", None)
    row.pop("event_type", None)
    row.pop("note", None)
    row.pop("change_summary", None)
    return row


def summarize_changes(ctx: dict[str, Any], existing: list[dict[str, str]]) -> tuple[str, list[str]]:
    current = current_metric_row(ctx)
    if not existing:
        note = str(ctx.get("note", "")).strip()
        changes = ["建立进展历史基线，后续阶段将以此对比 Gate、提交包和最终交付物变化。"]
        if note:
            changes.append(note)
        return "baseline", changes

    previous = sorted(existing, key=lambda item: item.get("timestamp", ""))[-1]
    checks = [
        ("completion_proven", "完成度证明状态"),
        ("next_blocking_gate", "下一阻塞门"),
        ("gate_complete", "已完成 Gate 数"),
        ("gate_partial", "部分完成 Gate 数"),
        ("gate_missing", "缺失 Gate 数"),
        ("submission_ready", "ready 提交项"),
        ("submission_draft_or_source_ready", "draft/source 提交项"),
        ("submission_blocked", "blocked 提交项"),
        ("submission_missing", "missing 提交项"),
        ("submission_draft_items", "草稿包生成项"),
        ("final_report_pdf", "正式报告 PDF"),
        ("final_report_docx", "正式报告 DOCX"),
        ("final_pptx", "答辩 PPTX"),
        ("final_ppt_pdf", "答辩 PPT PDF"),
        ("final_mp4", "演示视频 MP4"),
        ("watched_fingerprint", "关键文件指纹"),
    ]
    changes: list[str] = []
    watch_fingerprint_changed = False
    for key, label in checks:
        old = str(previous.get(key, ""))
        new = str(current.get(key, ""))
        if old != new:
            if key == "watched_fingerprint":
                watch_fingerprint_changed = True
            else:
                changes.append(f"{label}: {old} -> {new}")

    if watch_fingerprint_changed:
        previous_manifest = previous_watch_manifest(previous.get("marker", ""))
        watch_changes = summarize_watch_changes(previous_manifest, ctx.get("watched_manifest", {}))
        if watch_changes:
            changes.extend(f"关键文件更新：{item}" for item in watch_changes[:6])
            if len(watch_changes) > 6:
                changes.append(f"关键文件更新：另有 {len(watch_changes) - 6} 项变化，详见 outputs/progress_report/watch_manifest_latest.json")
        else:
            changes.append("关键文件指纹发生变化，详见 outputs/progress_report/watch_manifest_latest.json。")

    note = str(ctx.get("note", "")).strip()
    if note:
        changes.append(note)

    if not changes:
        return "status_review", ["与上一阶段相比，核心 Gate、提交包和最终交付物状态暂无变化；本次为状态复核。"]

    positive_keys = {
        "completion_proven",
        "gate_complete",
        "submission_ready",
        "submission_draft_items",
        "final_report_pdf",
        "final_report_docx",
        "final_pptx",
        "final_ppt_pdf",
        "final_mp4",
    }
    has_positive = any(str(previous.get(key, "")) != str(current.get(key, "")) for key in positive_keys)
    if watch_fingerprint_changed and not has_positive and not note:
        return "artifact_change", changes
    return ("progress" if has_positive or note else "risk_change"), changes


def build_summary(
    ctx: dict[str, Any],
    archive: bool,
    history_rows: list[dict[str, str]],
    skipped: bool = False,
    skip_reason: str = "",
) -> dict[str, Any]:
    latest_mentor_brief = ctx["latest_report"]
    assets = ctx["assets"]
    archive_reports = archived_mentor_reports()
    history_report_paths = {row.get("latest_mentor_brief", "") for row in history_rows}
    if skipped and history_rows:
        latest_mentor_brief = history_rows[-1].get("latest_mentor_brief", latest_mentor_brief)
        assets = {}
    return {
        "timestamp": ctx["timestamp"],
        "marker": ctx["marker"],
        "project_progress_report": PROGRESS_REPORT.relative_to(ROOT).as_posix(),
        "current_progress_brief": CURRENT_PROGRESS_BRIEF_DOC_REL,
        "latest_mentor_brief": latest_mentor_brief,
        "latest_mentor_brief_stable": LATEST_MENTOR_BRIEF_REL,
        "mentor_portal": MENTOR_PORTAL_DOC_REL,
        "meeting_brief": MEETING_BRIEF_DOC_REL,
        "daily_digest": DAILY_DIGEST_DOC_REL,
        "evidence_map": EVIDENCE_MAP_DOC_REL,
        "decision_brief": DECISION_BRIEF_DOC_REL,
        "mentor_qa": MENTOR_QA_DOC_REL,
        "g5_closure_brief": G5_CLOSURE_DOC_REL,
        "g5_stall_alert": G5_STALL_ALERT_DOC_REL,
        "mentor_snapshot": MENTOR_SNAPSHOT_DOC_REL,
        "latest_change_note": LATEST_CHANGE_DOC_REL,
        "next_action_brief": NEXT_ACTION_DOC_REL,
        "risk_register": RISK_REGISTER_DOC_REL,
        "submission_readiness": SUBMISSION_READINESS_DOC_REL,
        "final_delivery_gap_board": FINAL_DELIVERY_GAP_DOC_REL,
        "final_delivery_gap_chart": FINAL_DELIVERY_GAP_CHART.relative_to(ROOT).as_posix(),
        "final_delivery_gap_chart_outputs": FINAL_DELIVERY_GAP_CHART_OUT_REL,
        "progress_index": PROGRESS_INDEX_DOC_REL,
        "watch_scope": WATCH_SCOPE_DOC_REL,
        "progress_update_protocol": PROGRESS_PROTOCOL_DOC_REL,
        "status_review_log": STATUS_REVIEW_DOC_REL,
        "latest_status_review": LATEST_STATUS_REVIEW_DOC_REL,
        "latest_status_review_chart": LATEST_STATUS_REVIEW_CHART.relative_to(ROOT).as_posix(),
        "latest_status_review_chart_outputs": LATEST_STATUS_REVIEW_CHART_OUT_REL,
        "status_review_log_csv": STATUS_REVIEW_LOG_REL,
        "archive_written": archive and not skipped,
        "skipped": skipped,
        "skip_reason": skip_reason,
        "completion_proven": bool(ctx["master"].get("completion_proven", False)),
        "next_blocking_gate": ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate")),
        "gate_counts": ctx["gate_counts"],
        "submission": ctx["submission"],
        "draft": ctx["draft"],
        "final_status": ctx["final_status"],
        "assets": assets,
        "history_csv": "outputs/progress_report/progress_history.csv",
        "history_count": len(history_rows),
        "archive_report_count": len(archive_reports),
        "archive_only_report_count": sum(1 for path in archive_reports if path.relative_to(ROOT).as_posix() not in history_report_paths),
        "watched_fingerprint": ctx.get("watched_manifest", {}).get("fingerprint", ""),
        "event_type": ctx["event_type"],
        "changes_since_previous": ctx["changes_since_previous"],
    }


def update_progress_history(ctx: dict[str, Any]) -> list[dict[str, str]]:
    history_path = OUT_DIR / "progress_history.csv"
    existing = read_progress_history()
    row = progress_history_row(ctx)
    rows_by_marker = {item.get("marker", ""): item for item in existing if item.get("marker")}
    rows_by_marker[row["marker"]] = row
    rows = sorted(rows_by_marker.values(), key=lambda item: item.get("timestamp", ""))
    fieldnames = list(row.keys())

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def save_history_chart(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> None:
    if not history_rows:
        return
    assets = ctx["assets"]
    docs_asset_dir = REPORT_DIR / "assets"
    out_asset_dir = OUT_DIR / "assets"
    docs_asset_dir.mkdir(parents=True, exist_ok=True)
    out_asset_dir.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        error_path = OUT_DIR / "chart_generation_error.txt"
        write_text(error_path, f"History chart generation skipped: {exc}\n")
        assets["chart_error"] = error_path.relative_to(ROOT).as_posix()
        return

    labels = [row.get("marker", "")[-4:] or str(idx + 1) for idx, row in enumerate(history_rows)]
    gate_complete = [int(row.get("gate_complete", 0) or 0) for row in history_rows]
    draft_items = [int(row.get("submission_draft_items", 0) or 0) for row in history_rows]
    ready_items = [int(row.get("submission_ready", 0) or 0) for row in history_rows]
    final_ready = [
        sum(
            1
            for key in ("final_report_pdf", "final_report_docx", "final_pptx", "final_ppt_pdf", "final_mp4")
            if row.get(key, "false") == "true"
        )
        for row in history_rows
    ]

    fig, ax1 = plt.subplots(figsize=(11.5, 4.2), dpi=160)
    x = list(range(len(history_rows)))
    ax1.plot(x, gate_complete, marker="o", color="#2E7D32", linewidth=2.0, label="complete gates")
    ax1.plot(x, final_ready, marker="s", color="#C62828", linewidth=2.0, label="final files ready")
    ax1.set_ylabel("Gate / final file count")
    ax1.set_ylim(0, max(8, max(gate_complete + final_ready + [1]) + 1))
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.grid(axis="y", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, draft_items, marker="^", color="#7B1FA2", linewidth=1.8, label="draft package items")
    ax2.plot(x, ready_items, marker="D", color="#1976D2", linewidth=1.8, label="submission ready items")
    ax2.set_ylabel("Submission item count")
    ax2.set_ylim(0, max(draft_items + ready_items + [1]) * 1.2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=4,
        fontsize=8,
        frameon=False,
    )
    fig.suptitle(f"Progress history through {ctx['marker']}", fontsize=14, weight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.92))

    history_docs_path = docs_asset_dir / assets["history_name"]
    fig.savefig(history_docs_path, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(history_docs_path, out_asset_dir / assets["history_name"])


def build_context(timestamp: str) -> dict[str, Any]:
    gates = read_csv("outputs/master_dashboard/master_gate_summary.csv")
    actions = read_csv("outputs/master_dashboard/master_next_actions.csv")
    completion = read_json("outputs/completion_audit/completion_audit_summary.json")
    master = read_json("outputs/master_dashboard/master_dashboard_summary.json")
    submission = read_json("outputs/submission_index/submission_index_summary.json")
    draft = read_json("submission/submission_draft_summary.json")
    problem = read_json("outputs/problem_requirements/problem_requirements_summary.json")

    counts = status_counts(gates, completion)
    latest_report = f"docs/progress_reports/{filename_from_timestamp(timestamp)}"
    marker = marker_from_timestamp(timestamp)
    final_status = {label: (ROOT / rel_path).exists() for label, rel_path in FINAL_FILES}
    watch_manifest = watched_manifest()

    return {
        "timestamp": timestamp,
        "marker": marker,
        "latest_report": latest_report,
        "gates": gates,
        "actions": actions,
        "completion": completion,
        "master": master,
        "submission": submission,
        "draft": draft,
        "problem": problem,
        "gate_counts": counts,
        "final_status": final_status,
        "assets": chart_asset_paths(marker),
        "watched_manifest": watch_manifest,
        "note": "",
        "event_type": "",
        "changes_since_previous": [],
    }


def image_section(ctx: dict[str, Any], target: str) -> str:
    assets = ctx.get("assets", {})
    if target == "mentor":
        status_path = assets.get("mentor_status_overview", "")
        deliverables_path = assets.get("mentor_deliverables", "")
        history_path = assets.get("mentor_history", "")
    else:
        status_path = assets.get("project_status_overview", "")
        deliverables_path = assets.get("project_deliverables", "")
        history_path = assets.get("project_history", "")
    if not status_path or not deliverables_path:
        return ""
    return f"""### 图片版总览

![Gate 和提交物状态]({status_path})

![最终交付物状态]({deliverables_path})

![阶段趋势]({history_path})
"""


def watch_scope_report(ctx: dict[str, Any]) -> str:
    rows: list[list[object]] = []
    for item in ctx.get("watched_manifest", {}).get("files", []):
        rel_path = str(item.get("path", ""))
        rows.append(
            [
                rel_path,
                "存在" if item.get("exists") else "缺失",
                int(item.get("size", 0) or 0),
                WATCHED_FILE_NOTES.get(rel_path, ""),
            ]
        )

    return f"""# 项目进展巡检范围

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
当前指纹：`{ctx.get("watched_manifest", {}).get("fingerprint", "")}`

## 使用方式

```powershell
python code\\build_progress_report.py --only-if-changed
```

无核心变化时，上述命令只刷新 `outputs/progress_report/progress_report_summary.json`，不会新增导师汇报归档；发现关键文件、Gate、提交包或最终交付物状态变化时，会生成新的阶段汇报。关键文件指纹按存在性、大小和 SHA256 内容计算，mtime 仅保留在 manifest 中用于诊断。

## 固定入口

| 入口 | 路径 |
| --- | --- |
| 当前进展总报告 | `docs/project_progress_report.md` |
| 导师阅读门户 | `{MENTOR_PORTAL_DOC_REL}` |
| 当前进展简报 | `{CURRENT_PROGRESS_BRIEF_DOC_REL}` |
| 组会汇报稿 | `{MEETING_BRIEF_DOC_REL}` |
| 每日进展汇总 | `{DAILY_DIGEST_DOC_REL}` |
| 导师证据映射 | `{EVIDENCE_MAP_DOC_REL}` |
| 导师决策清单 | `{DECISION_BRIEF_DOC_REL}` |
| 导师问答卡 | `{MENTOR_QA_DOC_REL}` |
| G5 关闭路线 | `{G5_CLOSURE_DOC_REL}` |
| 导师 30 秒快照 | `{MENTOR_SNAPSHOT_DOC_REL}` |
| 本次变化说明 | `{LATEST_CHANGE_DOC_REL}` |
| 下一步行动清单 | `{NEXT_ACTION_DOC_REL}` |
| 风险登记表 | `{RISK_REGISTER_DOC_REL}` |
| 提交就绪清单 | `{SUBMISSION_READINESS_DOC_REL}` |
| 最新导师汇报 | `{LATEST_MENTOR_BRIEF_REL}` |
| 阶段索引 | `{PROGRESS_INDEX_DOC_REL}` |
| 历史台账 CSV | `outputs/progress_report/progress_history.csv` |
| 最新关键文件指纹 | `outputs/progress_report/watch_manifest_latest.json` |
| 巡检范围说明 | `{WATCH_SCOPE_DOC_REL}` |
| 跟进操作规程 | `{PROGRESS_PROTOCOL_DOC_REL}` |
| 状态复核台账 | `{STATUS_REVIEW_DOC_REL}` |
| 状态复核 CSV | `{STATUS_REVIEW_LOG_REL}` |

## 关键文件监测范围

{table(["路径", "当前状态", "字节数", "用途"], rows)}
"""


def progress_update_protocol(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    final_ready = final_ready_count(ctx)
    current_rows = [
        ["最新阶段标记", f"`{ctx['marker']}`"],
        ["最新有效导师汇报", ctx.get("latest_report", LATEST_MENTOR_BRIEF_REL)],
        ["next_blocking_gate", blocker],
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["Gate complete / partial / missing", f"{ctx['gate_counts']['complete']} / {ctx['gate_counts']['partial']} / {ctx['gate_counts']['missing']}"],
        ["submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["submission draft copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
    ]
    trigger_rows = [
        ["必须新增阶段标记", "Gate 状态、completion_proven、submission 统计、最终交付物、关键证据文件或报告/PPT/视频草稿有实质变化。", "运行 `python code\\build_progress_report.py --note \"本阶段完成了...\"`。"],
        ["可以人工补记", "会议纪要、导师意见、风险关闭口径或提交策略发生变化，但自动指纹未覆盖。", "用 `--note` 明确写出变化、产物和下一步。"],
        ["只做跳过复核", "核心状态和关键文件没有变化，只想确认项目仍处于同一状态。", "运行 `python code\\build_progress_report.py --only-if-changed`，期望 `skipped=true`。"],
        ["不得伪造完成", "正式 PDF/DOCX/PPTX/PPT PDF/MP4 未齐全，或 G5 风险未关闭。", "保持 `completion_proven=false`，并在汇报中写清缺口。"],
    ]
    cadence_rows = [
        ["阶段工作完成后", "先重跑对应技术脚本或文档生成脚本，再刷新 scorecard / requirements / submission index / completion audit / dashboard。"],
        ["汇报归档前", "用明确 note 生成新阶段，确认 `archive_written=true`、图表存在、latest mentor brief 指向新归档。"],
        ["submission 同步", "运行 `python code\\build_submission_draft.py`，确认 `copied_or_generated=64` 且 `missing=0`。"],
        ["防止噪声", "随后运行一次 `--only-if-changed`，确认无新变化时不会继续写归档。"],
        ["导师沟通前", "优先打开导师门户、30 秒快照、G5 关闭路线和决策清单。"],
    ]
    command_rows = [
        ["评分证据", "python code\\build_scorecard.py"],
        ["赛题要求矩阵", "python code\\build_problem_requirements_matrix.py"],
        ["提交物索引", "python code\\build_submission_index.py"],
        ["完成度审计", "python code\\build_completion_audit.py"],
        ["总控看板", "python code\\build_master_dashboard.py"],
        ["阶段标记", "python code\\build_progress_report.py --note \"本阶段完成了...\""],
        ["无变化复核", "python code\\build_progress_report.py --only-if-changed"],
        ["提交草稿同步", "python code\\build_submission_draft.py"],
    ]
    report_rows = [
        ["一句话结论", "当前 Gate、是否可提交、最大缺口。"],
        ["本阶段做了什么", "列出新完成的脚本、数据、报告、图表或提交包动作。"],
        ["产物是什么", "给出可点击/可追溯路径，避免只写描述。"],
        ["证据是否足够", "说明 scorecard、completion audit、submission index 或人工文件能否支撑结论。"],
        ["下一步谁来关", "负责人、关闭证据和阻塞项必须落到文件或命令。"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["巡检范围说明", WATCH_SCOPE_DOC_REL],
        ["状态复核台账", STATUS_REVIEW_DOC_REL],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL],
        ["阶段索引", PROGRESS_INDEX_DOC_REL],
    ]
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = ctx.get("assets", {}).get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines) if chart_lines else "本次运行未生成 PNG 图表；若是 `--only-if-changed` 跳过复核，这是预期现象。"

    return f"""# 进展跟进操作规程

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：把本线程的长期跟进动作固定成可复用规则，避免遗漏阶段标记、产物路径、图表和最终提交缺口。

## 当前基线

{table(["项目", "当前值"], current_rows)}

## 何时标记阶段

{table(["场景", "判据", "操作"], trigger_rows)}

## 每次跟进节奏

{table(["时机", "动作"], cadence_rows)}

## 复核命令

{table(["用途", "命令"], command_rows)}

## 汇报口径

{table(["要回答的问题", "最低要求"], report_rows)}

## 图表

{charts}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def stagnation_level_for_count(consecutive_count: int) -> str:
    if consecutive_count >= 20:
        return "高：G5 已多轮未关闭，导师阅读时应优先关注 G5 关闭动作。"
    if consecutive_count >= 5:
        return "中：G5 或同阶段复核已多轮停留，建议确认责任项是否有人推进。"
    if consecutive_count:
        return "低：当前仍需跟踪 G5 收口。"
    return "无：尚无 skipped 状态复核记录。"


def status_review_log_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> str:
    gate_counts = summary.get("gate_counts", {})
    submission = summary.get("submission", {})
    draft = summary.get("draft", {})
    final_status = summary.get("final_status", {})
    final_ready = sum(1 for ok in final_status.values() if ok)
    latest_effective_report = str(summary.get("latest_mentor_brief", ""))
    latest_skipped_report = ""
    consecutive_rows: list[dict[str, str]] = []
    for row in reversed(rows):
        if row.get("skipped", "").lower() != "true":
            break
        row_report = row.get("latest_mentor_brief", "")
        if not latest_skipped_report:
            latest_skipped_report = row_report
        elif row_report != latest_skipped_report:
            break
        consecutive_rows.append(row)
    consecutive_count = len(consecutive_rows)
    consecutive_start = consecutive_rows[-1].get("timestamp", "") if consecutive_rows else ""
    stagnation_level = stagnation_level_for_count(consecutive_count)
    recent_rows = [
        [
            row.get("timestamp", ""),
            f"`{row.get('marker', '')}`",
            row.get("skipped", ""),
            row.get("next_blocking_gate", ""),
            f"{row.get('gate_complete', '')}/{row.get('gate_partial', '')}/{row.get('gate_missing', '')}",
            f"{row.get('draft_copied_or_generated', '')}/{row.get('draft_missing', '')}",
            f"{row.get('final_ready', '')}/{row.get('final_total', '')}",
            row.get("skip_reason", "") or row.get("change_summary", ""),
        ]
        for row in rows[-12:]
    ]
    recent_rows.reverse()
    if not recent_rows:
        recent_rows = [["", "", "", "", "", "", "", "尚无 skipped 状态复核记录。"]]

    status_rows = [
        ["最新巡检时间", summary.get("timestamp", "")],
        ["最新巡检 marker", f"`{summary.get('marker', '')}`"],
        ["本次是否跳过归档", bool(summary.get("skipped", False))],
        ["本次是否写导师归档", bool(summary.get("archive_written", False))],
        ["最新有效导师汇报", summary.get("latest_mentor_brief", "")],
        ["completion_proven", bool(summary.get("completion_proven", False))],
        ["next_blocking_gate", summary.get("next_blocking_gate", "")],
        ["Gate complete / partial / missing", f"{gate_counts.get('complete', 0)} / {gate_counts.get('partial', 0)} / {gate_counts.get('missing', 0)}"],
        ["submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["草稿包 copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
        ["正式交付物已存在", f"{final_ready}/{len(final_status) or len(FINAL_FILES)}"],
        ["状态复核记录数", len(rows)],
        ["最近无核心变化复核段", f"{consecutive_count} 次"],
        ["复核段起点", consecutive_start or "尚无"],
        ["停滞风险提示", stagnation_level],
    ]
    stagnation_rows = [
        ["判断", stagnation_level],
        ["证据", f"自 {consecutive_start or '暂无'} 起，最近 skipped 段跟踪的有效导师汇报为 {latest_skipped_report or '暂无'}；当前固定入口为 {latest_effective_report or '暂无'}；最终交付物仍为 {final_ready}/{len(final_status) or len(FINAL_FILES)}。"],
        ["处理口径", "不把无变化巡检写成阶段进展；导师阅读时直接转向 G5 关闭路线、风险登记表和提交就绪清单。"],
    ]
    entry_rows = [
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["进展操作规程", PROGRESS_PROTOCOL_DOC_REL],
        ["巡检范围说明", WATCH_SCOPE_DOC_REL],
        ["阶段索引", PROGRESS_INDEX_DOC_REL],
        ["状态复核 CSV", STATUS_REVIEW_LOG_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL],
    ]

    return f"""# 状态复核台账

更新时间：{summary.get("timestamp", "")}  
用途：记录 `--only-if-changed` 的无变化巡检结果；不把无实质变化写入导师阶段归档，但保留长期跟进痕迹。

## 当前巡检状态

{table(["项目", "当前值"], status_rows)}

## 连续复核判断

{table(["项目", "说明"], stagnation_rows)}

## 最近状态复核

{table(["时间", "marker", "skipped", "阻塞门", "Gate 完成/部分/缺失", "草稿包", "最终件", "原因/摘要"], recent_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def consecutive_skipped_segment(summary: dict[str, Any], rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], str]:
    latest_effective_report = str(summary.get("latest_mentor_brief", ""))
    consecutive_rows: list[dict[str, str]] = []
    for row in reversed(rows):
        if row.get("skipped", "").lower() != "true":
            break
        if latest_effective_report and row.get("latest_mentor_brief", "") != latest_effective_report:
            break
        consecutive_rows.append(row)
    consecutive_start = consecutive_rows[-1].get("timestamp", "") if consecutive_rows else "尚无"
    return consecutive_rows, consecutive_start


def save_latest_status_review_chart(summary: dict[str, Any], rows: list[dict[str, str]]) -> str:
    LATEST_STATUS_REVIEW_CHART.parent.mkdir(parents=True, exist_ok=True)
    LATEST_STATUS_REVIEW_CHART_OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        error_path = OUT_DIR / "latest_status_review_chart_error.txt"
        write_text(error_path, f"Latest status review chart generation skipped: {exc}\n")
        return ""

    gate_counts = summary.get("gate_counts", {})
    final_status = summary.get("final_status", {})
    final_total = len(final_status) or len(FINAL_FILES)
    final_ready = sum(1 for ok in final_status.values() if ok)
    consecutive_rows, _ = consecutive_skipped_segment(summary, rows)
    complete = int(gate_counts.get("complete", 0) or 0)
    partial = int(gate_counts.get("partial", 0) or 0)
    missing = int(gate_counts.get("missing", 0) or 0)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.1), dpi=160, gridspec_kw={"width_ratios": [1.4, 1.0, 1.0]})
    fig.patch.set_facecolor("white")

    axes[0].axis("off")
    status_color = "#2E7D32" if summary.get("archive_written") else "#F9A825"
    axes[0].text(0.0, 0.92, "Latest status review", fontsize=15, weight="bold", color="#263238")
    axes[0].text(0.0, 0.76, f"Event: {summary.get('event_type', '')}", fontsize=11, color="#37474F")
    axes[0].text(0.0, 0.64, f"Skipped: {bool(summary.get('skipped', False))}", fontsize=11, color=status_color, weight="bold")
    axes[0].text(0.0, 0.52, f"Archive written: {bool(summary.get('archive_written', False))}", fontsize=11, color="#37474F")
    axes[0].text(0.0, 0.40, f"Next gate: {summary.get('next_blocking_gate', '')}", fontsize=11, color="#C62828", weight="bold")
    axes[0].text(0.0, 0.28, f"Consecutive no-change: {len(consecutive_rows)}", fontsize=11, color="#37474F")
    axes[0].text(0.0, 0.12, str(summary.get("timestamp", "")), fontsize=9, color="#607D8B")

    gate_labels = ["complete", "partial", "missing"]
    gate_values = [complete, partial, missing]
    gate_colors = ["#2E7D32", "#F9A825", "#C62828"]
    axes[1].bar(gate_labels, gate_values, color=gate_colors)
    axes[1].set_title("Gate counts", fontsize=12, weight="bold")
    axes[1].set_ylim(0, max(8, max(gate_values + [1]) + 1))
    for idx, value in enumerate(gate_values):
        axes[1].text(idx, value + 0.15, str(value), ha="center", fontsize=10, weight="bold")
    axes[1].grid(axis="y", alpha=0.2)

    axes[2].bar(["ready", "missing"], [final_ready, final_total - final_ready], color=["#2E7D32", "#C62828"])
    axes[2].set_title("Final deliverables", fontsize=12, weight="bold")
    axes[2].set_ylim(0, max(final_total, 1) + 1)
    axes[2].text(0, final_ready + 0.1, str(final_ready), ha="center", fontsize=10, weight="bold")
    axes[2].text(1, final_total - final_ready + 0.1, str(final_total - final_ready), ha="center", fontsize=10, weight="bold")
    axes[2].grid(axis="y", alpha=0.2)

    fig.tight_layout()
    fig.savefig(LATEST_STATUS_REVIEW_CHART, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(LATEST_STATUS_REVIEW_CHART, LATEST_STATUS_REVIEW_CHART_OUT)
    return LATEST_STATUS_REVIEW_CHART_REL


def latest_status_review_card(summary: dict[str, Any], rows: list[dict[str, str]]) -> str:
    gate_counts = summary.get("gate_counts", {})
    submission = summary.get("submission", {})
    draft = summary.get("draft", {})
    final_status = summary.get("final_status", {})
    final_ready = sum(1 for ok in final_status.values() if ok)
    consecutive_rows, consecutive_start = consecutive_skipped_segment(summary, rows)
    consecutive_count = len(consecutive_rows)
    chart_path = save_latest_status_review_chart(summary, rows)
    chart_block = f"![最新巡检状态]({chart_path})" if chart_path else "图表生成失败；请查看 `outputs/progress_report/latest_status_review_chart_error.txt`。"
    latest_rows = [
        [
            row.get("timestamp", ""),
            f"`{row.get('marker', '')}`",
            row.get("event_type", ""),
            row.get("skipped", ""),
            row.get("archive_written", ""),
            row.get("next_blocking_gate", ""),
            f"{row.get('final_ready', '')}/{row.get('final_total', '')}",
        ]
        for row in rows[-6:]
    ]
    latest_rows.reverse()
    if not latest_rows:
        latest_rows = [["", "", "", "", "", "", "尚无状态复核记录"]]
    status_rows = [
        ["最新巡检时间", summary.get("timestamp", "")],
        ["最新巡检 marker", f"`{summary.get('marker', '')}`"],
        ["事件类型", summary.get("event_type", "")],
        ["是否跳过阶段归档", bool(summary.get("skipped", False))],
        ["是否写入导师归档", bool(summary.get("archive_written", False))],
        ["最新有效导师汇报", summary.get("latest_mentor_brief", "")],
        ["completion_proven", bool(summary.get("completion_proven", False))],
        ["next_blocking_gate", summary.get("next_blocking_gate", "")],
        ["Gate complete / partial / missing", f"{gate_counts.get('complete', 0)} / {gate_counts.get('partial', 0)} / {gate_counts.get('missing', 0)}"],
        ["submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["草稿包 copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
        ["正式交付物已存在", f"{final_ready}/{len(final_status) or len(FINAL_FILES)}"],
        ["连续无核心变化复核", f"{consecutive_count} 次"],
        ["连续段起点", consecutive_start],
    ]
    reading_rows = [
        ["本次 archive_written=true", "直接读最新导师汇报和本次变化说明。"],
        ["本次 skipped=true", "说明核心状态无变化；看本卡、状态复核台账和 G5 关闭路线即可。"],
        [f"final files ready 仍未达到 {len(FINAL_FILES)}/{len(FINAL_FILES)}", "不要判定完成，继续推进报告/PPT/视频和 G5 风险说明。"],
    ]
    entry_rows = [
        ["当前进展简报", CURRENT_PROGRESS_BRIEF_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["状态复核台账", STATUS_REVIEW_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
    ]

    return f"""# 最新巡检状态卡

更新时间：{summary.get("timestamp", "")}  
用途：每次巡检都会刷新，用来回答“刚刚是否复核过、有没有新阶段、当前卡在哪里”。

## 当前巡检结论

{table(["项目", "当前值"], status_rows)}

## 图表

{chart_block}

## 读法

{table(["场景", "处理方式"], reading_rows)}

## 最近巡检记录

{table(["时间", "marker", "类型", "skipped", "archive", "阻塞门", "最终件"], latest_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def final_ready_count(ctx: dict[str, Any]) -> int:
    return sum(1 for ok in ctx.get("final_status", {}).values() if ok)


def final_gap_phrase_from_status(final_status: dict[str, bool]) -> str:
    total = len(final_status) or len(FINAL_FILES)
    ready = sum(1 for ok in final_status.values() if ok)
    missing = [label for label, ok in final_status.items() if not ok]
    if missing:
        return f"正式交付物已存在 {ready}/{total}，尚缺 {'、'.join(missing)}。"
    return f"正式交付物已存在 {ready}/{total}，四件套已齐全。"


def final_gap_phrase(ctx: dict[str, Any]) -> str:
    return final_gap_phrase_from_status(ctx.get("final_status", {}))


def current_progress_chart_block(ctx: dict[str, Any], summary: dict[str, Any] | None = None) -> str:
    assets = summary.get("assets", {}) if summary is not None else ctx.get("assets", {})
    chart_rows = [
        ("Gate 和提交物状态", assets.get("mentor_status_overview", "")),
        ("最终交付物状态", assets.get("mentor_deliverables", "")),
        ("阶段趋势", assets.get("mentor_history", "")),
    ]
    chart_lines = [f"![{label}]({path})" for label, path in chart_rows if path]
    if chart_lines:
        return "\n\n".join(chart_lines)
    return (
        f"![最新巡检状态]({LATEST_STATUS_REVIEW_CHART_REL})\n\n"
        f"![最终交付缺口图]({FINAL_DELIVERY_GAP_CHART_REL})"
    )


def current_progress_brief(
    ctx: dict[str, Any],
    summary: dict[str, Any],
    status_review_rows: list[dict[str, str]] | None = None,
) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_ready = final_ready_count(ctx)
    latest_effective_report = summary.get("latest_mentor_brief", ctx.get("latest_report", ""))
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    rows = status_review_rows or []
    consecutive_rows, consecutive_start = consecutive_skipped_segment(summary, rows)
    consecutive_count = len(consecutive_rows)
    final_total = len(summary.get("final_status", {})) or len(FINAL_FILES)
    gate_hold_rows: list[dict[str, str]] = []
    completion_done = bool(summary.get("completion_proven", False) or master.get("completion_proven", False))
    if blocker and not completion_done:
        for row in reversed(rows):
            if row.get("next_blocking_gate", "") != blocker:
                break
            if row.get("final_total", "") and row.get("final_ready", "") == row.get("final_total", ""):
                break
            gate_hold_rows.append(row)
    gate_hold_count = len(gate_hold_rows)
    gate_hold_start = gate_hold_rows[-1].get("timestamp", "") if gate_hold_rows else "尚无"
    if completion_done:
        stagnation_level = "已关闭：completion_proven=true，技术 Gate 已完成；后续关注人工提交复核。"
    else:
        stagnation_level = stagnation_level_for_count(max(consecutive_count, gate_hold_count))
    progress_rows = [
        ["测量方案", "2π 上半球测量面已固定，半球面测点数为 162。"],
        ["算法链路", "近远场重建、测点删减、识别分类和鲁棒性扫描 baseline 已建立。"],
        ["CST 链路", "Level 1 required 标准源链路已完成；Level 2 full48 样本链路 48/48 完整，简化结构遮挡对照已生成。"],
        ["报告链路", "solution_report_draft.md 已进入 G5 成稿口径，报告包章节 13/13 draft_ready。"],
        ["提交草稿", f"submission 草稿包 {draft.get('copied_or_generated', 0)} 项已复制或生成，缺失 {draft.get('missing', 0)} 项。"],
    ]
    product_rows = [
        ["报告草稿", "docs/solution_report_draft.md", "正式报告主文来源。"],
        ["报告包摘要", "outputs/report_package/report_package_summary.json", "检查章节、引用、图表占位和 G5 风险。"],
        ["当前进展简报", CURRENT_PROGRESS_BRIEF_DOC_REL, "本线程优先阅读入口。"],
        ["最新有效导师汇报", latest_effective_report, "阶段性归档汇报，适合发给导师。"],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL, "确认刚刚是否复核、是否新增阶段。"],
        ["最终交付缺口板", FINAL_DELIVERY_GAP_DOC_REL, "按 PDF/DOCX/PPTX/PPT PDF/MP4 倒推 G5 收口。"],
        ["G5 停滞告警", G5_STALL_ALERT_DOC_REL, "连续无核心变化时给导师看的收口告警页。"],
        ["提交草稿包", "submission/", "当前可预览的最终提交目录结构。"],
    ]
    status_rows = [
        ["本次巡检 marker", f"`{summary.get('marker', ctx['marker'])}`"],
        ["事件类型", summary.get("event_type", ctx.get("event_type", ""))],
        ["是否新增导师阶段归档", bool(summary.get("archive_written", False))],
        ["最新有效导师汇报", latest_effective_report],
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", blocker],
        ["Gate complete / partial / missing", f"{counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}"],
        ["submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["草稿包 copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
        ["正式交付物已存在", f"{final_ready}/{final_total}"],
        ["同阶段无核心变化复核", f"{consecutive_count} 次"],
        ["未关闭 Gate 复核", "无" if completion_done or not blocker else f"{blocker}: {gate_hold_count} 次"],
        ["停滞风险提示", stagnation_level],
    ]
    if completion_done:
        stagnation_rows = [
            ["判断", "技术 Gate 已关闭"],
            ["证据", f"completion_proven=true；Gate 为 {counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}；最终交付物为 {final_ready}/{final_total}；最新有效导师汇报为 {latest_effective_report or '暂无'}。"],
            ["处理口径", "不再按 G5 停滞处理；后续转人工播放、报名信息、最终压缩包命名和静默 MP4 是否需旁白的复核。"],
        ]
    else:
        stagnation_rows = [
            ["判断", stagnation_level],
            ["证据", f"同一有效导师汇报下自 {consecutive_start or '暂无'} 起连续 {consecutive_count} 次无核心变化；{blocker} 未关闭复核自 {gate_hold_start or '暂无'} 起累计 {gate_hold_count} 次；最新有效导师汇报为 {latest_effective_report or '暂无'}；最终交付物仍为 {final_ready}/{final_total}。"],
            ["处理口径", "不把无变化巡检写成阶段进展；短版简报直接提示 G5 关闭路线、风险登记表和提交就绪清单。"],
        ]
    change_rows = [[summary.get("event_type", ctx.get("event_type", "")), item] for item in summary.get("changes_since_previous", [])]
    if not change_rows:
        change_rows = [["status_review", "本次未发现核心状态变化。"]]
    next_action_rows = [
        [
            row.get("priority", ""),
            row.get("owner_role", ""),
            row.get("action", ""),
            row.get("proof_to_close", row.get("expected_artifact", "")),
        ]
        for row in ctx["actions"][:4]
    ]
    if not next_action_rows:
        next_action_rows = [["", "", "暂无自动生成的下一步动作。", ""]]

    return f"""# 当前进展简报

更新时间：{summary.get("timestamp", ctx["timestamp"])}  
用途：本文件是此长期跟进线程的短版稳定入口，用来快速回答“目前做了什么、产物是什么、下一步是什么”。

## 一句话结论

{verdict(ctx)}

## 本次巡检状态

{table(["项目", "当前值"], status_rows)}

## 目前做了什么

{table(["方向", "进展"], progress_rows)}

## 产物是什么

{table(["产物", "路径", "作用"], product_rows)}

## 本次变化或复核结论

{table(["类型", "说明"], change_rows)}

## 连续复核判断

{table(["项目", "说明"], stagnation_rows)}

## 当前缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 下一步建议

{table(["优先级", "负责人", "动作", "关闭证据"], next_action_rows)}

## 图表

{current_progress_chart_block(ctx, summary)}
"""


def g5_stall_alert(
    ctx: dict[str, Any],
    summary: dict[str, Any],
    status_review_rows: list[dict[str, str]] | None = None,
) -> str:
    master = ctx["master"]
    draft = ctx["draft"]
    submission = ctx["submission"]
    final_status = summary.get("final_status", ctx["final_status"])
    final_ready = sum(1 for ok in final_status.values() if ok)
    final_total = len(final_status) or len(FINAL_FILES)
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    rows = status_review_rows or []
    consecutive_rows, consecutive_start = consecutive_skipped_segment(summary, rows)
    consecutive_count = len(consecutive_rows)
    gate_hold_rows: list[dict[str, str]] = []
    completion_done = bool(summary.get("completion_proven", False) or master.get("completion_proven", False))
    if blocker and not completion_done:
        for row in reversed(rows):
            if row.get("next_blocking_gate", "") != blocker:
                break
            if row.get("final_total", "") and row.get("final_ready", "") == row.get("final_total", ""):
                break
            gate_hold_rows.append(row)
    gate_hold_count = len(gate_hold_rows)
    gate_hold_start = gate_hold_rows[-1].get("timestamp", "") if gate_hold_rows else "尚无"
    if completion_done:
        alert_level = "已关闭：completion_proven=true，G5 不再是阻塞门。"
    else:
        alert_level = stagnation_level_for_count(max(consecutive_count, gate_hold_count))
    latest_effective_report = summary.get("latest_mentor_brief", ctx.get("latest_report", ""))
    status_rows = [
        ["本次巡检 marker", f"`{summary.get('marker', ctx['marker'])}`"],
        ["事件类型", summary.get("event_type", ctx.get("event_type", ""))],
        ["是否新增阶段归档", bool(summary.get("archive_written", False))],
        ["最新有效导师汇报", latest_effective_report],
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", blocker],
        ["同阶段无核心变化复核", f"{consecutive_count} 次"],
        ["未关闭 Gate 复核", "无" if completion_done or not blocker else f"{blocker}: {gate_hold_count} 次"],
        ["正式交付物已存在", f"{final_ready}/{final_total}"],
        ["提交草稿 copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
        ["submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["告警等级", alert_level],
    ]
    if completion_done:
        trigger_rows = [
            ["关闭证据", f"completion_proven=true；next_blocking_gate=无；最终交付物为 {final_ready}/{final_total}。"],
            ["后续关注", "人工播放、报名信息、最终压缩包命名，以及静默 MP4 是否需要替换为带旁白录屏。"],
            ["处理口径", "这不是 G5 停滞告警；保留本卡作为 G5 已关闭后的最终提交复核提醒。"],
        ]
    else:
        trigger_rows = [
            ["连续复核证据", f"同一有效导师汇报下自 {consecutive_start} 起连续 {consecutive_count} 次无核心变化。"],
            ["G5 长期未关闭证据", f"{blocker} 未关闭复核自 {gate_hold_start} 起累计 {gate_hold_count} 次；最终交付物仍为 {final_ready}/{final_total}。"],
            ["处理口径", "不把无变化复核写成项目进展；导师阅读时直接转向责任项、关闭证据和最终四件套缺口。"],
        ]
    owner_rows = [
        ["A_algorithm", "Level 1 solver-safe 重建精度风险", "报告中能解释当前 NMSE/correlation 风险，或新重建指标明显改善。", "outputs/cst_level1_reconstruction_batch"],
        ["A_algorithm + C_docs", "Level 2 结构散射/遮挡边界", "报告/PPT 中写入简化结构遮挡对照，并明确它与 full-wave airframe scattering 的差异。", "outputs/cst_structure_comparison"],
        ["C_docs", "正式报告、PPT、视频成稿", "正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。", "submission/"],
        ["全队", "最终审计与人工报名信息复核", "completion_proven=true，submission index blocked=0，最终文件齐全，人工信息补齐。", "outputs/completion_audit; outputs/submission_index"],
    ]
    entry_rows = [
        ["当前进展简报", CURRENT_PROGRESS_BRIEF_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["最终交付缺口板", FINAL_DELIVERY_GAP_DOC_REL],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
    ]
    title = "G5 收口状态卡" if completion_done else "G5 停滞告警"
    headline = (
        f"当前技术 Gate 已关闭：completion_proven=true，正式交付物 {final_ready}/{final_total} 已齐。剩余不是 G5 技术阻塞，而是人工播放、报名信息、最终压缩包命名，以及静默 MP4 是否需要旁白的复核。"
        if completion_done
        else f"当前不是新的技术突破，而是 G5 收口停滞告警：主体技术链路、简化结构遮挡对照和提交草稿已具备，但{final_gap_phrase_from_status(final_status)} Level 1 指标风险和 Level 2 结构边界说明仍需写入成稿。"
    )
    return f"""# {title}

更新时间：{summary.get("timestamp", ctx["timestamp"])}  
用途：给导师和队内负责人一个一页式 G5 收口状态说明。

## 一句话结论

{headline}

## 告警状态

{table(["项目", "当前值"], status_rows)}

## 为什么需要关注

{table(["证据", "说明"], trigger_rows)}

## 责任项和关闭证据

{table(["负责人", "责任项", "关闭证据", "证据入口"], owner_rows)}

## 正式交付缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 推荐入口

{table(["用途", "路径"], entry_rows)}

## 图表

![最新巡检状态](assets/latest_status_review.png)

![最终交付缺口图](assets/final_delivery_gap_board.png)
"""


def latest_change_note(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> str:
    previous_rows = [
        row
        for row in sorted(history_rows, key=lambda item: item.get("timestamp", ""))
        if row.get("marker") != ctx["marker"]
    ]
    previous = previous_rows[-1] if previous_rows else {}
    change_rows = [[ctx.get("event_type", ""), item] for item in ctx.get("changes_since_previous", [])]
    before_after_rows = [
        ["上一阶段", previous.get("marker", "无"), previous.get("timestamp", "")],
        ["当前阶段", ctx["marker"], ctx["timestamp"]],
        ["上一阻塞门", previous.get("next_blocking_gate", "无"), ""],
        ["当前阻塞门", ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", "")), ""],
        ["上一最终件", f"{ready_final_count(previous)}/{len(FINAL_FILES)}" if previous else "无", ""],
        ["当前最终件", f"{final_ready_count(ctx)}/{len(FINAL_FILES)}", ""],
        ["上一草稿包", f"{previous.get('submission_draft_items', '无')} 项" if previous else "无", ""],
        ["当前草稿包", f"{ctx['draft'].get('copied_or_generated', 0)} 项", ""],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["当前进展简报", CURRENT_PROGRESS_BRIEF_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["G5 停滞告警", G5_STALL_ALERT_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["阶段时间线", PROGRESS_INDEX_DOC_REL],
        ["当前进展总报告", PROGRESS_REPORT.relative_to(ROOT).as_posix()],
        ["历史台账", "outputs/progress_report/progress_history.csv"],
    ]
    change_text = "；".join(ctx.get("changes_since_previous", []))
    if ctx.get("event_type") == "progress":
        if "草稿包生成项" in change_text:
            why = "本次记录属于可交付草稿包进展：提交草稿包项目数发生变化，并同步刷新报告、PPT/视频分镜相关材料，适合作为新的导师阶段汇报。"
        else:
            why = "本次记录属于实质进展更新：关键指标、材料或交付状态发生变化，适合作为新的导师阶段汇报。"
    elif ctx.get("event_type") == "artifact_change" and "src/build_progress_report.py" in change_text:
        why = "本次记录属于进度跟踪工具链增强：刷新导师可读报告、状态风险和变化说明的表达，提升阶段汇报可读性。"
    elif ctx.get("event_type") == "artifact_change":
        why = "本次记录属于关键材料更新；核心 Gate、提交包和最终交付物状态需要继续按 G5 缺口复核。"
    else:
        why = "本次为状态复核，核心 Gate、提交包和最终交付物暂无变化。"

    return f"""# 本次变化说明

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
变化类型：`{ctx.get("event_type", "")}`  
详细汇报：`{ctx["latest_report"]}`

## 为什么值得记录

{why}

## 变化清单

{table(["类型", "变化/备注"], change_rows)}

## 前后状态

{table(["项目", "值", "时间"], before_after_rows)}

## 对导师阅读的影响

1. 可以先看 `{MENTOR_PORTAL_DOC_REL}` 按可用时间选择入口。
2. 可以看 `{MENTOR_SNAPSHOT_DOC_REL}` 获得当前结论。
3. 可以看 `{PROGRESS_INDEX_DOC_REL}` 回溯所有阶段，包括早期 archive-only 汇报。
4. 如果只关心本阶段差异，可直接看本文件。

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def next_action_brief(ctx: dict[str, Any]) -> str:
    action_rows = [
        [
            row.get("priority", ""),
            row.get("owner_role", ""),
            row.get("gate", ""),
            row.get("action", ""),
            row.get("expected_artifact", ""),
            row.get("proof_to_close", ""),
            row.get("blocked_by", "") or "无",
        ]
        for row in ctx.get("actions", [])
    ]
    if not action_rows:
        action_rows = [["", "", "", "暂无 next actions 数据", "", "", ""]]

    evidence_rows = [
        [
            row.get("priority", ""),
            row.get("command_or_file", ""),
            row.get("notes", ""),
        ]
        for row in ctx.get("actions", [])
    ]
    final_rows = final_file_rows()
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["阶段时间线", PROGRESS_INDEX_DOC_REL],
        ["总控状态看板", "outputs/master_dashboard/master_status_dashboard.md"],
        ["完成度审计", "outputs/completion_audit/completion_audit.md"],
    ]
    blocker = ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))

    return f"""# 下一步行动清单

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
当前阻塞门：`{blocker}`

## 一句话判断

{verdict(ctx)}

## 优先行动

{table(["优先级", "负责人", "Gate", "动作", "预期产物", "关闭证据", "当前阻塞"], action_rows)}

## 命令或证据入口

{table(["优先级", "命令/文件", "备注"], evidence_rows)}

## 最终交付物缺口

{table(["最终交付物", "路径", "状态"], final_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def risk_register(ctx: dict[str, Any]) -> str:
    risk_rows = [
        [
            "R1",
            "高",
            "Level 1 solver-safe 重建精度风险",
            "影响三维场重建高精度部分的可信度表达。",
            "A_algorithm",
            "复核近远场一致性、等效源基函数和正则化；必要时形成误差机理说明。",
            "报告中能解释当前 NMSE/correlation 风险，或新重建指标明显改善。",
            "未关闭",
        ],
        [
            "R2",
            "中",
            "Level 2 full48 主要是 element-library 叠加证据",
            "已补简化结构遮挡对照，但仍不是 full-wave airframe scattering。",
            "A_algorithm + C_docs",
            "把简化结构对照写入报告/PPT，并明确 full-wave airframe 是后续增强项。",
            "outputs/cst_structure_comparison 被报告/PPT 引用，且边界说明清楚。",
            "未关闭",
        ],
        [
            "R3",
            "高",
            final_gap_phrase(ctx),
            "不能进入最终提交态，G5 仍为 partial。",
            "C_docs",
            "把 Level 1/2 最新结果写入正式报告、PPT 和视频脚本并导出剩余正式文件。",
            "正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。",
            "未关闭",
        ],
        [
            "R4",
            "中",
            "最终打包和人工报名信息仍需复核",
            "提交系统/邮箱所需学校、申报人、联系电话、报名表仍需人工补充。",
            "C_docs / 全队",
            "最终打包前重建 scorecard、submission index、completion audit、master dashboard 和 submission draft。",
            "completion_proven=true，submission index blocked=0，最终文件齐全，人工报名信息已补齐。",
            "待最终阶段处理",
        ],
    ]
    evidence_rows = [
        ["R1", "outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py"],
        ["R2", "outputs/cst_level2_element_trials; docs/stage_notes/19_cst_level2_full48_recognition.md"],
        ["R3", "submission/01_report; submission/02_presentation; submission/03_video; docs/solution_report_draft.md"],
        ["R4", "outputs/submission_index; outputs/completion_audit; outputs/master_dashboard; submission/submission_draft_summary.json"],
    ]
    status_rows = [
        ["completion_proven", bool(ctx["master"].get("completion_proven", False))],
        ["next_blocking_gate", ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["final files ready", f"{final_ready_count(ctx)}/{len(FINAL_FILES)}"],
        ["submission draft copied_or_generated / missing", f"{ctx['draft'].get('copied_or_generated', 0)} / {ctx['draft'].get('missing', 0)}"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["评分证据板", "outputs/scorecard/scorecard.md"],
        ["完成度审计", "outputs/completion_audit/completion_audit.md"],
    ]

    return f"""# 风险登记表

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
当前阻塞门：`{ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))}`

## 当前状态

{table(["指标", "当前值"], status_rows)}

## 风险清单

{table(["编号", "等级", "风险", "影响", "负责人", "缓解动作", "关闭证据", "状态"], risk_rows)}

## 证据入口

{table(["风险编号", "证据/命令入口"], evidence_rows)}

## 最终交付物缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def submission_readiness(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    final_ready = final_ready_count(ctx)
    ready_to_submit = bool(master.get("completion_proven", False)) and final_ready == len(FINAL_FILES) and bool(draft.get("is_final", False))

    status_rows = [
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
        ["submission draft copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["submission draft is_final", bool(draft.get("is_final", False))],
        ["submission index ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["ready_to_submit", ready_to_submit],
    ]
    final_rows = [
        [
            label,
            rel_path,
            "存在" if (ROOT / rel_path).exists() else "缺失",
            "正式提交必须存在",
        ]
        for label, rel_path in FINAL_FILES
    ]
    blocker_rows = [
        ["G5", "正式报告/PPT/视频和剩余风险说明未闭合", "生成正式 PDF/DOCX/PPTX/PPT PDF/MP4，并处理 Level 1/Level 2 证据边界。"],
        ["Level 1", "solver-safe 重建精度风险", "优化重建或在报告中形成可辩护误差机理说明。"],
        ["Level 2", "简化结构遮挡对照需写入成稿", "引用 outputs/cst_structure_comparison，并明确非 full-wave airframe 边界。"],
        ["人工提交信息", "学校、申报人、联系电话、报名表等仍需人工复核", "最终打包前补齐并复查。"],
    ]
    command_rows = [
        ["阶段跟进", "python code\\build_progress_report.py --note \"本阶段完成了某项关键进展\""],
        ["无变化巡检", "python code\\build_progress_report.py --only-if-changed"],
        ["最终草稿包", "python code\\build_submission_draft.py"],
        ["最终复核链", "python code\\build_scorecard.py; python code\\build_problem_requirements_matrix.py; python code\\build_submission_index.py; python code\\build_completion_audit.py; python code\\build_master_dashboard.py"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["最终交付缺口板", FINAL_DELIVERY_GAP_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["submission 草稿包摘要", "submission/submission_draft_summary.json"],
        ["提交物索引", "outputs/submission_index/submission_package_index.md"],
    ]
    verdict_text = "尚未达到最终提交状态。" if not ready_to_submit else "已满足提交就绪条件，可进入最终人工复核。"

    return f"""# 提交就绪清单

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
结论：{verdict_text}

## 总体状态

{table(["指标", "当前值"], status_rows)}

## 正式交付物

{table(["交付物", "路径", "状态", "说明"], final_rows)}

## 仍需关闭的提交条件

{table(["对象", "当前问题", "关闭方式"], blocker_rows)}

## 复核命令

{table(["用途", "命令"], command_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def final_delivery_items(ctx: dict[str, Any]) -> list[dict[str, str]]:
    specs = {
        "正式报告 PDF": {
            "owner": "C_docs",
            "source": "docs/solution_report_draft.md",
            "dependency": "Level 1 风险说明、Level 2 边界说明、最终排版",
            "close_proof": "PDF 存在且指标与 scorecard 一致",
        },
        "正式报告 DOCX": {
            "owner": "C_docs",
            "source": "docs/solution_report_draft.md",
            "dependency": "与 PDF 同源导出，保留可编辑版",
            "close_proof": "DOCX 存在且目录、图表和引用可编辑",
        },
        "答辩 PPTX": {
            "owner": "C_docs",
            "source": "outputs/presentation_package; docs/progress_reports/meeting_brief.md",
            "dependency": "与最终报告的指标、图表和风险边界保持一致",
            "close_proof": "PPTX 存在且 12 页故事线与 scorecard 对齐",
        },
        "答辩 PPT PDF": {
            "owner": "C_docs",
            "source": "submission/02_presentation/defense_slides.pptx",
            "dependency": "与 PPTX 同源导出，用于不可编辑提交或导师快速预览",
            "close_proof": "PPT PDF 存在且页数、图表和指标口径与 PPTX 一致",
        },
        "演示视频 MP4": {
            "owner": "C_docs",
            "source": "outputs/presentation_package/demo_video_storyboard.md",
            "dependency": "PPT 与视频脚本定稿，最终指标口径不再变化",
            "close_proof": "MP4 存在且演示内容覆盖测量、重建、识别和提交物",
        },
    }
    rows: list[dict[str, str]] = []
    for label, rel_path in FINAL_FILES:
        item = specs[label]
        exists = (ROOT / rel_path).exists()
        rows.append(
            {
                "deliverable": label,
                "path": rel_path,
                "status": "存在" if exists else "缺失",
                "owner": item["owner"],
                "source": item["source"],
                "dependency": item["dependency"],
                "close_proof": item["close_proof"],
            }
        )
    return rows


def save_final_delivery_gap_chart(ctx: dict[str, Any]) -> str:
    FINAL_DELIVERY_GAP_CHART.parent.mkdir(parents=True, exist_ok=True)
    FINAL_DELIVERY_GAP_CHART_OUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        error_path = OUT_DIR / "final_delivery_gap_chart_error.txt"
        write_text(error_path, f"Final delivery gap chart generation skipped: {exc}\n")
        return ""

    items = final_delivery_items(ctx)
    statuses = [1 if item["status"] == "存在" else 0 for item in items]
    missing = [1 - value for value in statuses]
    labels = ["Report PDF", "Report DOCX", "Defense PPTX", "Defense PDF", "Demo MP4"]
    chart_notes = [
        "risk wording + final layout",
        "editable report export",
        "align with report metrics",
        "export from final PPTX",
        "locked script and visuals",
    ]

    fig, ax = plt.subplots(figsize=(11.5, 4.0), dpi=160)
    y = list(range(len(items)))
    ax.barh(y, statuses, color="#2E7D32", label="ready")
    ax.barh(y, missing, left=statuses, color="#C62828", label="missing")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlim(0, 1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["missing", "ready"])
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)
    ax.set_title(f"Final deliverable gap board - {ctx['marker']}", fontsize=14, weight="bold")
    for idx, item in enumerate(items):
        label = "ready" if item["status"] == "存在" else "missing"
        color = "#2E7D32" if item["status"] == "存在" else "#C62828"
        ax.text(0.03, idx, f"{label} | {item['owner']}", va="center", ha="left", fontsize=9, color="white", weight="bold")
        ax.text(1.02, idx, chart_notes[idx], va="center", ha="left", fontsize=8, color=color)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout(rect=(0, 0, 0.82, 1))
    fig.savefig(FINAL_DELIVERY_GAP_CHART, bbox_inches="tight")
    plt.close(fig)
    shutil.copy2(FINAL_DELIVERY_GAP_CHART, FINAL_DELIVERY_GAP_CHART_OUT)
    return FINAL_DELIVERY_GAP_CHART_REL


def final_delivery_gap_board(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    draft = ctx["draft"]
    final_ready = final_ready_count(ctx)
    chart_path = save_final_delivery_gap_chart(ctx)
    chart_block = f"![最终交付缺口图]({chart_path})" if chart_path else "图表生成失败；请查看 `outputs/progress_report/final_delivery_gap_chart_error.txt`。"
    item_rows = [
        [
            item["deliverable"],
            item["path"],
            item["status"],
            item["owner"],
            item["dependency"],
            item["close_proof"],
        ]
        for item in final_delivery_items(ctx)
    ]
    source_rows = [
        [item["deliverable"], item["source"]]
        for item in final_delivery_items(ctx)
    ]
    route_rows = [
        ["1", "先定报告口径", "把 Level 1 metric risk 和 Level 2 structure-boundary 写成可辩护表述。"],
        ["2", "导出报告双格式", "从同一报告源导出 PDF 与 DOCX，避免两份口径分叉。"],
        ["3", "同步答辩 PPT", "用报告中的最终数字、图和风险边界更新 12 页 story board。"],
        ["4", "录制/导出演示视频", "使用 PPT 和 demo_video_storyboard，确保口径不再变化。"],
        ["5", "重跑最终审计链", "刷新 scorecard、requirements、submission index、completion audit、master dashboard、submission draft。"],
    ]
    status_rows = [
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
        ["submission draft copied / missing / final", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)} / {bool(draft.get('is_final', False))}"],
    ]
    entry_rows = [
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
    ]

    return f"""# 最终交付缺口板

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：按最终提交文件倒推“谁负责、依赖什么、关闭证据是什么”，便于 G5 收口。

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 缺口图

{chart_block}

## 最终文件倒推表

{table(["交付物", "路径", "状态", "负责人", "当前依赖", "关闭证据"], item_rows)}

## 源文件/草稿入口

{table(["交付物", "源文件或草稿入口"], source_rows)}

## 建议关闭顺序

{table(["顺序", "动作", "说明"], route_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def mentor_portal(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_ready = final_ready_count(ctx)
    history_report_paths = {row.get("latest_mentor_brief", "") for row in history_rows}
    archive_reports = archived_mentor_reports()
    archive_only_count = sum(1 for path in archive_reports if path.relative_to(ROOT).as_posix() not in history_report_paths)

    reading_rows = [
        ["30 秒", MENTOR_SNAPSHOT_DOC_REL, "当前做到哪、能否提交、缺口是什么。"],
        ["45 秒", CURRENT_PROGRESS_BRIEF_DOC_REL, "目前做了什么、产物是什么、下一步是什么。"],
        ["1 分钟", LATEST_CHANGE_DOC_REL, "本阶段相对上一阶段变化了什么。"],
        ["2 分钟", NEXT_ACTION_DOC_REL, "下一步谁做、做什么、用什么证据关闭。"],
        ["3 分钟", RISK_REGISTER_DOC_REL, "主要风险、影响、负责人和关闭证据。"],
        ["今日复盘", DAILY_DIGEST_DOC_REL, "当天所有阶段标记、产物演进和剩余缺口。"],
        ["导师拍板", DECISION_BRIEF_DOC_REL, "需要导师确认的技术取舍和最终提交策略。"],
        ["导师问答", MENTOR_QA_DOC_REL, "常见追问、建议回答和证据入口。"],
        ["G5 收口", G5_CLOSURE_DOC_REL, "最终提交态还差什么、怎么关、用什么证据关。"],
        ["组会 5 分钟", MEETING_BRIEF_DOC_REL, "可直接照着讲的阶段汇报稿。"],
        ["提交前", SUBMISSION_READINESS_DOC_REL, "正式 PDF/DOCX/PPTX/PPT PDF/MP4、completion 和 submission 草稿包是否就绪。"],
        ["交付缺口", FINAL_DELIVERY_GAP_DOC_REL, "按 PDF/DOCX/PPTX/PPT PDF/MP4 倒推负责人、依赖和关闭证据。"],
        ["完整复盘", PROGRESS_INDEX_DOC_REL, "所有阶段标记、时间线和归档导师汇报。"],
        ["详细阅读", LATEST_MENTOR_BRIEF_REL, "完整导师汇报、图表、产物清单和风险。"],
        ["实时巡检", LATEST_STATUS_REVIEW_DOC_REL, "最新一次巡检是否归档、是否跳过、当前 G5 状态。"],
        ["产物总览", PROGRESS_REPORT.relative_to(ROOT).as_posix(), "目前做了什么、产物是什么、下一步是什么。"],
        ["巡检设置", WATCH_SCOPE_DOC_REL, "长期跟进监测哪些关键文件和最终交付物。"],
        ["跟进规程", PROGRESS_PROTOCOL_DOC_REL, "何时标记阶段、何时跳过复核、每次汇报要检查什么。"],
        ["复核台账", STATUS_REVIEW_DOC_REL, "无变化巡检记录，确认没有把状态复核误写成阶段归档。"],
    ]
    status_rows = [
        ["阶段标记", f"`{ctx['marker']}`"],
        ["完成度证明", bool(master.get("completion_proven", False))],
        ["下一阻塞门", master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["Gate 完成 / 部分 / 缺失", f"{counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}"],
        ["Submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["草稿包 copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["正式交付物已存在", f"{final_ready}/{len(FINAL_FILES)}"],
        ["历史台账记录", f"{len(history_rows)} 条"],
        ["归档导师汇报", f"{len(archive_reports)} 份，其中 archive-only {archive_only_count} 份"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["当前进展简报", CURRENT_PROGRESS_BRIEF_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["最终交付缺口板", FINAL_DELIVERY_GAP_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["阶段索引", PROGRESS_INDEX_DOC_REL],
        ["巡检范围", WATCH_SCOPE_DOC_REL],
        ["跟进操作规程", PROGRESS_PROTOCOL_DOC_REL],
        ["状态复核台账", STATUS_REVIEW_DOC_REL],
        ["最新巡检状态卡", LATEST_STATUS_REVIEW_DOC_REL],
        ["状态复核 CSV", STATUS_REVIEW_LOG_REL],
        ["历史台账 CSV", "outputs/progress_report/progress_history.csv"],
    ]

    assets = ctx.get("assets", {})
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = assets.get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines) if chart_lines else "本次运行未生成 PNG 图表；详见最新导师汇报中的 Mermaid 图。"

    return f"""# 导师阅读入口总门户

更新时间：{ctx["timestamp"]}  
最新阶段标记：`{ctx["marker"]}`  
最新导师汇报：`{ctx["latest_report"]}`

## 一句话结论

{verdict(ctx)}

## 按时间选择入口

{table(["可用时间", "建议入口", "适合回答的问题"], reading_rows)}

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 最新图表

{charts}

## 固定入口清单

{table(["入口", "路径"], entry_rows)}
"""


def meeting_brief(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_ready = final_ready_count(ctx)
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))

    speak_rows = [
        ["开场结论", verdict(ctx)],
        ["已完成 1", "测量方案固定为 2π 上半球，半球面测点数 162，可支撑 CST 与 Python 链路。"],
        ["已完成 2", "Python baseline、重建、测点删减、识别分类和鲁棒性扫描已经建立。"],
        ["已完成 3", "Level 1 required 标准源链路已完成，当前 required-now 缺失文件为 0。"],
        ["已完成 4", "Level 2 full48 element-library 样本链路已跑通，48/48 样本完整，识别 accuracy 为 1.000。"],
        ["已完成 5", f"scorecard、completion audit、master dashboard、submission index 和 submission 草稿包已生成；草稿包 {draft.get('copied_or_generated', 0)} 项已复制或生成，缺失 {draft.get('missing', 0)} 项。"],
        ["当前卡点", f"下一阻塞门为 {blocker}，正式 PDF/DOCX/PPTX/PPT PDF/MP4 仍为 {final_ready}/{len(FINAL_FILES)}，completion_proven={bool(master.get('completion_proven', False))}。"],
    ]
    artifact_rows = [
        ["进展入口总门户", MENTOR_PORTAL_DOC_REL, "按阅读时间选择报告入口。"],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL, "按日期复盘阶段标记、产物演进和剩余缺口。"],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL, "关键结论到证据文件的一一对应关系。"],
        ["导师决策清单", DECISION_BRIEF_DOC_REL, "需要导师确认或拍板的未关闭问题。"],
        ["导师问答卡", MENTOR_QA_DOC_REL, "导师常问问题、建议回答和证据入口。"],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL, "最终提交态关闭判据、路线和复核命令。"],
        ["跟进操作规程", PROGRESS_PROTOCOL_DOC_REL, "阶段标记、跳过复核、同步 submission 和汇报口径规则。"],
        ["状态复核台账", STATUS_REVIEW_DOC_REL, "记录 skipped 巡检，说明没有新增阶段归档的依据。"],
        ["当前进展总报告", PROGRESS_REPORT.relative_to(ROOT).as_posix(), "完整回答目前做了什么、产物是什么、缺口是什么。"],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL, "带图表的阶段汇报归档。"],
        ["总控状态看板", "outputs/master_dashboard/master_status_dashboard.md", "Gate、阻塞项和任务队列。"],
        ["完成度审计", "outputs/completion_audit/completion_audit.md", "最终完成度证明依据。"],
        ["提交草稿包", "submission/", "当前可预览的提交目录结构。"],
    ]
    ask_rows = [
        ["Level 1 重建", "请确认是否继续优化 solver-safe 重建，还是在报告中形成误差机理说明。"],
        ["Level 2 结构证据", "简化结构遮挡对照已生成，请确认是否接受其作为 G5 边界证据，或继续追加 full-wave airframe 对照。"],
        ["最终文档", "请确认报告/PPT/视频优先级，下一步集中生成正式 PDF/DOCX/PPTX/PPT PDF/MP4。"],
    ]
    next_rows = [
        [row.get("priority", ""), row.get("owner_role", ""), row.get("action", ""), row.get("proof_to_close", "")]
        for row in ctx.get("actions", [])[:4]
    ]
    if not next_rows:
        next_rows = [["", "", "暂无 next actions 数据", ""]]
    status_rows = [
        ["阶段标记", f"`{ctx['marker']}`"],
        ["Gate 完成 / 部分 / 缺失", f"{counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}"],
        ["Submission ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["草稿包 copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["最终交付物已存在", f"{final_ready}/{len(FINAL_FILES)}"],
        ["历史台账记录", f"{len(history_rows)} 条"],
    ]

    assets = ctx.get("assets", {})
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = assets.get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines) if chart_lines else "本次运行未生成 PNG 图表；详见最新导师汇报中的 Mermaid 图。"

    return f"""# 组会汇报稿

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
建议用途：5 分钟口头汇报，可直接按本页顺序讲。

## 口头汇报稿

{table(["段落", "建议表述"], speak_rows)}

## 当前状态数字

{table(["项目", "当前值"], status_rows)}

## 当前产物

{table(["产物", "路径", "可展示内容"], artifact_rows)}

## 建议向导师确认

{table(["议题", "需要确认的问题"], ask_rows)}

## 下一步安排

{table(["优先级", "负责人", "动作", "关闭证据"], next_rows)}

## 图表

{charts}
"""


def daily_digest(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> str:
    current_date = ctx["timestamp"][:10]
    rows_today = [
        row
        for row in sorted(history_rows, key=lambda item: item.get("timestamp", ""))
        if row.get("timestamp", "").startswith(current_date)
    ]
    if not rows_today:
        rows_today = [row for row in sorted(history_rows, key=lambda item: item.get("timestamp", ""))[-1:]]

    event_counts: dict[str, int] = {}
    for row in rows_today:
        event_type = row.get("event_type") or "status"
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

    milestone_rows = []
    for row in reversed(rows_today[-10:]):
        note = row.get("note") or row.get("change_summary") or "状态记录"
        report = row.get("latest_mentor_brief", "")
        milestone_rows.append(
            [
                row.get("timestamp", ""),
                f"`{row.get('marker', '')}`",
                row.get("event_type") or "status",
                note[:110] + ("..." if len(note) > 110 else ""),
                f"`{report}`" if report else "",
            ]
        )

    capability_rows = [
        [
            row.get("marker", ""),
            row.get("note") or row.get("change_summary", ""),
        ]
        for row in rows_today
        if "跟进机制" in (row.get("note") or row.get("change_summary", ""))
    ]
    if not capability_rows:
        capability_rows = [["", "今日未新增跟进机制能力；本页为状态复核汇总。"]]
    else:
        capability_rows = capability_rows[-8:]

    status_rows = [
        ["汇总日期", current_date],
        ["最新阶段标记", f"`{ctx['marker']}`"],
        ["今日入账阶段", f"{len(rows_today)} 条"],
        ["今日事件类型", ", ".join(f"{key}={value}" for key, value in sorted(event_counts.items()))],
        ["历史台账总数", f"{len(history_rows)} 条"],
        ["completion_proven", bool(ctx["master"].get("completion_proven", False))],
        ["next_blocking_gate", ctx["master"].get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["草稿包 copied_or_generated / missing", f"{ctx['draft'].get('copied_or_generated', 0)} / {ctx['draft'].get('missing', 0)}"],
        ["最终交付物已存在", f"{final_ready_count(ctx)}/{len(FINAL_FILES)}"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["跟进操作规程", PROGRESS_PROTOCOL_DOC_REL],
        ["状态复核台账", STATUS_REVIEW_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["阶段索引", PROGRESS_INDEX_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
    ]

    assets = ctx.get("assets", {})
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = assets.get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines) if chart_lines else "本次运行未生成 PNG 图表；详见最新导师汇报中的 Mermaid 图。"

    return f"""# 每日进展汇总

更新时间：{ctx["timestamp"]}  
汇总日期：{current_date}  
最新阶段标记：`{ctx["marker"]}`

## 今日一句话

{verdict(ctx)}

## 今日状态数字

{table(["项目", "当前值"], status_rows)}

## 今日阶段记录

{table(["时间", "阶段", "类型", "备注", "汇报文件"], milestone_rows)}

## 今日新增或强化的跟进能力

{table(["阶段", "说明"], capability_rows)}

## 仍未关闭的关键缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 图表

{charts}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def evidence_map(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]

    def status_for(rel_path: str) -> str:
        path = ROOT / rel_path
        if path.is_file():
            return f"存在，{path.stat().st_size} bytes"
        if path.is_dir():
            return "目录存在"
        return "缺失"

    claim_rows = [
        [
            "方案和路线已建立",
            "已形成文献矩阵、技术路线、报告草稿和赛题要求矩阵。",
            "docs/literature_matrix.md; docs/team_division_technical_route.md; docs/solution_report_draft.md; outputs/problem_requirements/problem_requirements_matrix.md",
            "已证实",
        ],
        [
            "测量布局已固定",
            "采用 2π 上半球测量面，半球面测点数为 162。",
            "outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv",
            "已证实",
        ],
        [
            "Level 1 required 标准源链路已完成",
            f"required-now 缺失文件为 {master.get('missing_required_now_files', 0)}；仍需处理 solver-safe 重建精度风险。",
            "outputs/cst_level1_merge_report; outputs/cst_level1_reconstruction_batch; src/run_cst_reconstruction.py",
            "已证实，但有指标风险",
        ],
        [
            "Level 2 full48 样本链路已跑通",
            "48/48 个 CST-derived element-library 样本完整，识别 accuracy 为 1.000。",
            "outputs/cst_level2_merge_report; outputs/cst_recognition_level2; docs/stage_notes/19_cst_level2_full48_recognition.md",
            "已证实；简化结构遮挡对照已补，full-wave airframe 仍为增强项",
        ],
        [
            "审计和评分证据已生成",
            f"Gate 完成/部分/缺失为 {counts.get('complete', 0)}/{counts.get('partial', 0)}/{counts.get('missing', 0)}，下一阻塞门为 {master.get('next_blocking_gate', ctx['completion'].get('next_blocking_gate', ''))}。",
            "outputs/scorecard/scorecard.md; outputs/completion_audit/completion_audit.md; outputs/master_dashboard/master_status_dashboard.md",
            "已证实",
        ],
        [
            "提交草稿包已生成",
            f"submission 草稿包 copied_or_generated/missing 为 {draft.get('copied_or_generated', 0)}/{draft.get('missing', 0)}；submission index ready/draft-source/blocked/missing 为 {submission.get('ready', 0)}/{submission.get('draft_or_source_ready', 0)}/{submission.get('blocked', 0)}/{submission.get('missing', 0)}。",
            "submission/; submission/submission_draft_summary.json; outputs/submission_index/submission_package_index.md",
            "草稿态已证实",
        ],
        [
            "最终提交态尚未达成",
            f"completion_proven={bool(master.get('completion_proven', False))}；正式 PDF/DOCX/PPTX/PPT PDF/MP4 已存在 {final_ready_count(ctx)}/{len(FINAL_FILES)}。",
            "submission/01_report; submission/02_presentation; submission/03_video; docs/progress_reports/submission_readiness.md",
            "未关闭",
        ],
    ]
    evidence_paths = [
        ["文献矩阵", "docs/literature_matrix.md"],
        ["技术路线和分工", "docs/team_division_technical_route.md"],
        ["报告草稿", "docs/solution_report_draft.md"],
        ["赛题要求矩阵", "outputs/problem_requirements/problem_requirements_matrix.md"],
        ["测量布局 CSV", "outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv"],
        ["Level 1 合并报告", "outputs/cst_level1_merge_report"],
        ["Level 1 重建结果", "outputs/cst_level1_reconstruction_batch"],
        ["Level 2 合并报告", "outputs/cst_level2_merge_report"],
        ["Level 2 识别结果", "outputs/cst_recognition_level2"],
        ["评分证据板", "outputs/scorecard/scorecard.md"],
        ["完成度审计", "outputs/completion_audit/completion_audit.md"],
        ["总控状态看板", "outputs/master_dashboard/master_status_dashboard.md"],
        ["提交包索引", "outputs/submission_index/submission_package_index.md"],
        ["submission 草稿摘要", "submission/submission_draft_summary.json"],
    ]
    evidence_rows = [[label, rel_path, status_for(rel_path)] for label, rel_path in evidence_paths]
    final_rows = final_file_rows()
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["导师 30 秒快照", MENTOR_SNAPSHOT_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["阶段索引", PROGRESS_INDEX_DOC_REL],
    ]

    return f"""# 导师证据映射

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：把“目前做了什么”和“产物是什么”逐条映射到可核验证据。

## 结论到证据

{table(["结论", "当前说法", "证据入口", "状态判断"], claim_rows)}

## 证据文件状态

{table(["证据", "路径", "当前状态"], evidence_rows)}

## 最终交付物状态

{table(["最终交付物", "路径", "状态"], final_rows)}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def decision_brief(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    draft = ctx["draft"]
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    final_ready = final_ready_count(ctx)

    decision_rows = [
        [
            "D1",
            "Level 1 solver-safe 重建精度",
            "继续优化重建，或保留现有结果并形成误差机理说明。",
            "若继续优化，可能提升指标但占用时间；若写清机理，可先保障报告闭环。",
            "建议先形成可辩护说明，同时保留一次快速复核机会。",
            "outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py",
        ],
        [
            "D2",
            "Level 2 复杂载体结构证据",
            "简化结构遮挡对照已生成，需决定是否进一步追加 full-wave airframe 对照。",
            "当前对照可支撑边界说明；full-wave 对照会增强可信度但耗时更长。",
            "建议先把当前结构对照写入报告/PPT，时间允许再补 full-wave。",
            "outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md",
        ],
        [
            "D3",
            "正式报告/PPT/视频优先级",
            "先集中生成 PDF/DOCX/PPTX/PPT PDF/MP4，还是先继续补技术证据。",
            f"当前正式交付物 {final_ready}/{len(FINAL_FILES)}，不生成则无法关闭 G5。",
            "建议优先成稿并导出正式文件，再把技术风险作为报告边界或附录说明。",
            "docs/solution_report_draft.md; docs/final_submission_package_plan.md; outputs/scorecard/scorecard.md",
        ],
        [
            "D4",
            "最终提交人工信息",
            "学校、申报人、联系电话、报名表等由谁确认。",
            "技术包可以自动生成，人工报名信息不能由脚本证明。",
            "建议指定 C_docs 收口，全队最终复核。",
            "docs/final_submission_package_plan.md; submission/",
        ],
        [
            "D5",
            "最终完成度验收口径",
            "completion_proven=true 前，是否接受 G5 风险说明作为阶段闭环。",
            f"当前 completion_proven={bool(master.get('completion_proven', False))}，next_blocking_gate={blocker}。",
            "建议以正式文件齐全、scorecard 一致、风险边界明确作为最终验收口径。",
            "outputs/completion_audit/completion_audit.md; outputs/master_dashboard/master_status_dashboard.md",
        ],
    ]
    status_rows = [
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", blocker],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
        ["submission draft copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["submission draft is_final", bool(draft.get("is_final", False))],
    ]
    close_rows = [
        ["D1", "报告中能解释当前 NMSE/correlation 风险，或新重建指标明显改善。"],
        ["D2", "报告/PPT 中明确结构对照结果，或明确 element-library full48 的适用边界。"],
        ["D3", "正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。"],
        ["D4", "人工报名信息已补齐并经全队复核。"],
        ["D5", "completion_proven=true，submission index blocked=0，最终文件齐全。"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["最新导师汇报", LATEST_MENTOR_BRIEF_REL],
    ]

    return f"""# 导师决策清单

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：集中列出当前需要导师确认或拍板的技术取舍和提交策略。

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 待决策事项

{table(["编号", "议题", "需要拍板的问题", "影响", "建议取向", "证据入口"], decision_rows)}

## 关闭口径

{table(["编号", "关闭证据"], close_rows)}

## 正式交付物缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def mentor_qa(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    final_ready = final_ready_count(ctx)

    qa_rows = [
        [
            "现在项目完成了吗？",
            f"还没有到最终提交态。主体技术链路和 submission 草稿结构已完成，但 completion_proven={bool(master.get('completion_proven', False))}，下一阻塞门是 {blocker}。",
            "docs/progress_reports/submission_readiness.md; outputs/completion_audit/completion_audit.md",
        ],
        [
            "目前做了什么？",
            "已完成文献与技术路线、2π 上半球测量布局、Python baseline、Level 1 required 标准源链路、Level 2 full48 样本链路、scorecard/completion audit/master dashboard/submission index 和 submission 草稿包。",
            "docs/progress_reports/evidence_map.md; docs/project_progress_report.md",
        ],
        [
            "当前产物是什么？",
            f"submission 草稿包 {draft.get('copied_or_generated', 0)} 项已复制或生成，缺失 {draft.get('missing', 0)}；submission index ready/draft-source/blocked/missing 为 {submission.get('ready', 0)}/{submission.get('draft_or_source_ready', 0)}/{submission.get('blocked', 0)}/{submission.get('missing', 0)}。",
            "submission/; submission/submission_draft_summary.json; outputs/submission_index/submission_package_index.md",
        ],
        [
            "为什么还不能最终提交？",
            f"正式 PDF/DOCX/PPTX/PPT PDF/MP4 仍为 {final_ready}/{len(FINAL_FILES)}，Level 1 重建指标风险和 Level 2 简化结构边界仍需在报告中处理。",
            "docs/progress_reports/decision_brief.md; docs/progress_reports/risk_register.md",
        ],
        [
            "Level 1 的风险怎么解释？",
            "当前不是缺 CST 文件，而是 solver-safe 重建质量需要复核；建议形成误差机理说明，并保留一次快速优化机会。",
            "outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; src/run_cst_reconstruction.py",
        ],
        [
            "Level 2 的证据够不够？",
            "full48 样本链路已跑通且识别 accuracy 为 1.000；简化结构遮挡对照已显示 cross-domain accuracy 为 1.000，但不是 full-wave airframe。",
            "outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md",
        ],
        [
            "下一步最应该先做什么？",
            "优先关闭 G5：把 Level 1/2 结果、风险边界和证据写进正式报告/PPT/视频脚本，并导出 PDF/DOCX/PPTX/PPT PDF/MP4。",
            "docs/progress_reports/next_action_brief.md; docs/final_submission_package_plan.md",
        ],
        [
            "需要导师拍板什么？",
            "请确认 Level 1 是继续优化还是先写误差说明、Level 2 是否接受简化结构对照作为边界证据、以及是否优先生成正式提交件。",
            "docs/progress_reports/decision_brief.md",
        ],
    ]
    quick_rows = [
        ["30 秒看结论", MENTOR_SNAPSHOT_DOC_REL],
        ["5 分钟组会汇报", MEETING_BRIEF_DOC_REL],
        ["今日复盘", DAILY_DIGEST_DOC_REL],
        ["证据逐条核对", EVIDENCE_MAP_DOC_REL],
        ["需要拍板的问题", DECISION_BRIEF_DOC_REL],
        ["G5 关闭路线", G5_CLOSURE_DOC_REL],
        ["提交前复核", SUBMISSION_READINESS_DOC_REL],
        ["最新完整汇报", LATEST_MENTOR_BRIEF_REL],
    ]
    status_rows = [
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["next_blocking_gate", blocker],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
        ["submission draft copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
    ]

    return f"""# 导师问答卡

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：预置导师常问问题、建议回答和证据入口，便于组会或答辩前快速预演。

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 常见问答

{table(["问题", "建议回答", "证据入口"], qa_rows)}

## 快速入口

{table(["用途", "路径"], quick_rows)}
"""


def g5_closure_brief(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))
    final_ready = final_ready_count(ctx)
    ready_to_submit = bool(master.get("completion_proven", False)) and final_ready == len(FINAL_FILES) and bool(draft.get("is_final", False))

    status_rows = [
        ["next_blocking_gate", blocker],
        ["completion_proven", bool(master.get("completion_proven", False))],
        ["final files ready", f"{final_ready}/{len(FINAL_FILES)}"],
        ["submission draft copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["submission draft is_final", bool(draft.get("is_final", False))],
        ["submission index ready / draft-source / blocked / missing", f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}"],
        ["ready_to_submit", ready_to_submit],
    ]
    closure_rows = [
        ["1", "A_algorithm", "Level 1 solver-safe 重建风险关闭", "新重建指标改善，或报告中形成可辩护误差机理说明。", "outputs/cst_level1_reconstruction_batch; docs/solution_report_draft.md"],
        ["2", "A_algorithm + C_docs", "Level 2 结构散射/遮挡边界关闭", "把简化结构对照写入报告/PPT，并明确它不是 full-wave airframe scattering。", "outputs/cst_structure_comparison; docs/stage_notes/22_structure_occlusion_comparison.md"],
        ["3", "C_docs", "正式报告、PPT、视频成稿", "正式 PDF/DOCX/PPTX/PPT PDF/MP4 文件存在，且指标与 scorecard 一致。", "submission/01_report; submission/02_presentation; submission/03_video"],
        ["4", "C_docs", "最终审计链重跑", "scorecard、需求矩阵、submission index、completion audit、master dashboard 和 submission draft 全部刷新。", "outputs/scorecard; outputs/problem_requirements; outputs/submission_index; outputs/completion_audit; outputs/master_dashboard"],
        ["5", "全队", "人工提交信息复核", "学校、申报人、联系电话、报名表等人工信息补齐并复核。", "docs/final_submission_package_plan.md; submission/"],
    ]
    command_rows = [
        ["评分证据", "python code\\build_scorecard.py"],
        ["赛题要求矩阵", "python code\\build_problem_requirements_matrix.py"],
        ["提交物索引", "python code\\build_submission_index.py"],
        ["完成度审计", "python code\\build_completion_audit.py"],
        ["总控看板", "python code\\build_master_dashboard.py"],
        ["阶段跟进", "python code\\build_progress_report.py --note \"G5 关闭状态更新\""],
        ["提交草稿包", "python code\\build_submission_draft.py"],
    ]
    flow = """flowchart LR
  A["当前状态: G5 partial"]
  B["处理 Level 1 风险"]
  C["处理 Level 2 边界"]
  D["导出 PDF/DOCX/PPTX/PPT PDF/MP4"]
  E["重跑审计和 submission draft"]
  F["completion_proven=true"]
  A --> B --> C --> D --> E --> F
"""
    entry_rows = [
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["导师问答卡", MENTOR_QA_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["最终包计划", "docs/final_submission_package_plan.md"],
    ]

    assets = ctx.get("assets", {})
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = assets.get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines) if chart_lines else "本次运行未生成 PNG 图表；详见最新导师汇报中的 Mermaid 图。"

    return f"""# G5 关闭路线图

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
用途：集中说明从当前 G5 partial 状态到最终提交态的关闭路线、判据和复核命令。

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 关闭路线

{table(["顺序", "负责人", "任务", "关闭证据", "证据入口"], closure_rows)}

## 正式交付物状态

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 流程图

```mermaid
{flow}
```

## 复核命令

{table(["用途", "命令"], command_rows)}

## 图表

{charts}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def mentor_snapshot(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_ready = final_ready_count(ctx)
    blocker = master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))

    status_rows = [
        ["阶段标记", f"`{ctx['marker']}`"],
        ["完成度证明", bool(master.get("completion_proven", False))],
        ["下一阻塞门", blocker],
        ["Gate 完成 / 部分 / 缺失", f"{counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}"],
        [
            "Submission ready / draft-source / blocked / missing",
            f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}",
        ],
        ["草稿包 copied_or_generated / missing", f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}"],
        ["最终交付物已存在", f"{final_ready}/{len(FINAL_FILES)}"],
    ]
    progress_rows = [
        ["测量方案", "2π 上半球测量面已固定，半球面测点数为 162。"],
        ["算法链路", "Python baseline、重建、测点删减、识别和鲁棒性扫描已建立。"],
        ["CST 链路", "Level 1 required 标准源链路、Level 2 full48 element-library 样本链路和简化结构遮挡对照已跑通。"],
        ["审计链路", "scorecard、completion audit、master dashboard、submission index、进展台账已生成。"],
        ["提交草稿", f"submission 草稿包 {draft.get('copied_or_generated', 0)} 项已复制或生成，缺失 {draft.get('missing', 0)} 项。"],
    ]
    entry_rows = [
        ["导师阅读门户", MENTOR_PORTAL_DOC_REL],
        ["组会汇报稿", MEETING_BRIEF_DOC_REL],
        ["每日进展汇总", DAILY_DIGEST_DOC_REL],
        ["导师证据映射", EVIDENCE_MAP_DOC_REL],
        ["导师决策清单", DECISION_BRIEF_DOC_REL],
        ["本次变化说明", LATEST_CHANGE_DOC_REL],
        ["下一步行动清单", NEXT_ACTION_DOC_REL],
        ["风险登记表", RISK_REGISTER_DOC_REL],
        ["提交就绪清单", SUBMISSION_READINESS_DOC_REL],
        ["详细导师汇报", LATEST_MENTOR_BRIEF_REL],
        ["阶段时间线", PROGRESS_INDEX_DOC_REL],
        ["当前进展总报告", PROGRESS_REPORT.relative_to(ROOT).as_posix()],
        ["巡检范围", WATCH_SCOPE_DOC_REL],
        ["跟进操作规程", PROGRESS_PROTOCOL_DOC_REL],
        ["状态复核台账", STATUS_REVIEW_DOC_REL],
        ["历史台账", "outputs/progress_report/progress_history.csv"],
    ]
    change_rows = [[ctx.get("event_type", ""), item] for item in ctx.get("changes_since_previous", [])[:5]]

    assets = ctx.get("assets", {})
    chart_lines = []
    for label, key in [
        ("Gate 和提交物状态", "mentor_status_overview"),
        ("最终交付物状态", "mentor_deliverables"),
        ("阶段趋势", "mentor_history"),
    ]:
        path = assets.get(key, "")
        if path:
            chart_lines.append(f"![{label}]({path})")
    charts = "\n\n".join(chart_lines)

    return f"""# 导师 30 秒快照

更新时间：{ctx["timestamp"]}  
阶段标记：`{ctx["marker"]}`  
详细汇报：`{ctx["latest_report"]}`

## 结论

{verdict(ctx)}

## 当前状态

{table(["项目", "当前值"], status_rows)}

## 目前做了什么

{table(["方向", "进展"], progress_rows)}

## 本次变化

{table(["类型", "变化/备注"], change_rows)}

## 当前缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

## 图表

{charts}

## 推荐入口

{table(["用途", "路径"], entry_rows)}
"""


def ready_final_count(row: dict[str, str]) -> int:
    return sum(
        1
        for key in ("final_report_pdf", "final_report_docx", "final_pptx", "final_ppt_pdf", "final_mp4")
        if row.get(key, "false") == "true"
    )


def progress_index_report(ctx: dict[str, Any], history_rows: list[dict[str, str]]) -> str:
    rows: list[list[object]] = []
    history_report_paths: set[str] = set()
    for row in sorted(history_rows, key=lambda item: item.get("timestamp", ""), reverse=True):
        note = row.get("note") or row.get("change_summary", "")
        report_path = row.get("latest_mentor_brief", "")
        if report_path:
            history_report_paths.add(report_path)
        rows.append(
            [
                row.get("timestamp", ""),
                f"`{row.get('marker', '')}`",
                row.get("event_type", "") or "status",
                row.get("next_blocking_gate", ""),
                f"{row.get('gate_complete', '0')}/{row.get('gate_partial', '0')}/{row.get('gate_missing', '0')}",
                f"{row.get('submission_draft_items', '0')} 项",
                f"{ready_final_count(row)}/{len(FINAL_FILES)}",
                note[:90] + ("..." if len(note) > 90 else ""),
                f"`{report_path}`",
            ]
        )

    archive_only_count = 0
    for path in archived_mentor_reports():
        rel_path = path.relative_to(ROOT).as_posix()
        if rel_path in history_report_paths:
            continue
        archive_only_count += 1
        rows.append(
            [
                archive_timestamp_label(path),
                f"`{archive_marker(path)}`",
                "archive-only",
                "见汇报",
                "见汇报",
                "见汇报",
                "见汇报",
                "早期归档汇报；该文件生成于历史台账完善前，详细状态以原汇报为准。",
                f"`{rel_path}`",
            ]
        )
    rows.sort(key=lambda item: str(item[0]), reverse=True)

    assets = ctx.get("assets", {})
    status_path = assets.get("mentor_status_overview", "")
    deliverables_path = assets.get("mentor_deliverables", "")
    history_path = assets.get("mentor_history", "")
    chart_block = ""
    if status_path and deliverables_path and history_path:
        chart_block = f"""## 最新图表

![Gate 和提交物状态]({status_path})

![最终交付物状态]({deliverables_path})

![阶段趋势]({history_path})
"""

    return f"""# 阶段进展索引

更新时间：{ctx["timestamp"]}  
最新阶段标记：`{ctx["marker"]}`  
最新导师汇报：`{ctx["latest_report"]}`  
固定导师入口：`{LATEST_MENTOR_BRIEF_REL}`

历史台账记录：{len(history_rows)} 条  
归档汇报文件：{len(archived_mentor_reports())} 份  
其中仅归档未入台账：{archive_only_count} 份

## 当前判断

{verdict(ctx)}

## 推荐阅读入口

| 用途 | 路径 |
| --- | --- |
| 导师阅读门户 | `{MENTOR_PORTAL_DOC_REL}` |
| 组会汇报稿 | `{MEETING_BRIEF_DOC_REL}` |
| 每日进展汇总 | `{DAILY_DIGEST_DOC_REL}` |
| 导师证据映射 | `{EVIDENCE_MAP_DOC_REL}` |
| 导师决策清单 | `{DECISION_BRIEF_DOC_REL}` |
| 导师问答卡 | `{MENTOR_QA_DOC_REL}` |
| 导师 30 秒快照 | `{MENTOR_SNAPSHOT_DOC_REL}` |
| 本次变化说明 | `{LATEST_CHANGE_DOC_REL}` |
| 下一步行动清单 | `{NEXT_ACTION_DOC_REL}` |
| 风险登记表 | `{RISK_REGISTER_DOC_REL}` |
| 提交就绪清单 | `{SUBMISSION_READINESS_DOC_REL}` |
| 当前进展总报告 | `docs/project_progress_report.md` |
| 最新导师汇报 | `{LATEST_MENTOR_BRIEF_REL}` |
| 阶段索引 | `{PROGRESS_INDEX_DOC_REL}` |
| 巡检范围 | `{WATCH_SCOPE_DOC_REL}` |
| 跟进操作规程 | `{PROGRESS_PROTOCOL_DOC_REL}` |
| 状态复核台账 | `{STATUS_REVIEW_DOC_REL}` |
| 最新巡检状态卡 | `{LATEST_STATUS_REVIEW_DOC_REL}` |
| 历史台账 CSV | `outputs/progress_report/progress_history.csv` |

{chart_block}
## 阶段时间线

{table(["时间", "阶段", "类型", "阻塞门", "Gate 完成/部分/缺失", "草稿包", "最终件", "备注", "汇报文件"], rows)}
"""


def verdict(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    next_gate = master.get("next_blocking_gate") or ctx["completion"].get("next_blocking_gate") or "unknown"
    if master.get("completion_proven"):
        return "项目已通过 completion audit，可进入最终提交复核。"
    return (
        "项目已完成主体技术链路和提交草稿结构；当前尚未达到最终提交状态。"
        f"下一关键阻塞门为 `{next_gate}`，重点是正式报告/PPT/视频和剩余风险说明。"
    )


def progress_report(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]
    final_status_text = " / ".join("true" if ok else "false" for ok in ctx["final_status"].values())

    key_rows = [
        ["completion_proven", master.get("completion_proven", False)],
        ["next_blocking_gate", master.get("next_blocking_gate", ctx["completion"].get("next_blocking_gate", ""))],
        ["gates complete / partial / missing", f"{counts.get('complete', 0)} / {counts.get('partial', 0)} / {counts.get('missing', 0)}"],
        [
            "submission ready / draft-source / blocked / missing",
            f"{submission.get('ready', 0)} / {submission.get('draft_or_source_ready', 0)} / {submission.get('blocked', 0)} / {submission.get('missing', 0)}",
        ],
        [
            "submission draft copied_or_generated / missing",
            f"{draft.get('copied_or_generated', 0)} / {draft.get('missing', 0)}",
        ],
        ["problem requirement count", master.get("problem_requirement_count", "")],
        ["problem blocked_or_missing evidence", master.get("problem_blocked_or_missing_count", "")],
        ["CST required-now missing files", master.get("missing_required_now_files", "")],
        ["Level 2 pilot missing files", master.get("missing_level2_pilot_files", "")],
        ["final PDF / DOCX / PPTX / PPT PDF / MP4", final_status_text],
    ]

    next_action_rows = [
        [
            row.get("priority", ""),
            row.get("owner_role", ""),
            row.get("action", ""),
            row.get("proof_to_close", row.get("expected_artifact", "")),
        ]
        for row in ctx["actions"][:4]
    ]

    artifact_rows = [[name, path, meaning] for name, path, meaning in KEY_ARTIFACTS]
    change_rows = [[ctx.get("event_type", ""), item] for item in ctx.get("changes_since_previous", [])]

    return f"""# 项目进展跟踪报告

更新时间：{ctx["timestamp"]}

最新导师汇报版：`{ctx["latest_report"]}`  
最新导师汇报固定入口：`{LATEST_MENTOR_BRIEF_REL}`  
当前进展简报：`{CURRENT_PROGRESS_BRIEF_DOC_REL}`  
导师阅读门户：`{MENTOR_PORTAL_DOC_REL}`  
组会汇报稿：`{MEETING_BRIEF_DOC_REL}`  
每日进展汇总：`{DAILY_DIGEST_DOC_REL}`  
导师证据映射：`{EVIDENCE_MAP_DOC_REL}`  
导师决策清单：`{DECISION_BRIEF_DOC_REL}`  
导师问答卡：`{MENTOR_QA_DOC_REL}`  
G5 关闭路线：`{G5_CLOSURE_DOC_REL}`  
导师 30 秒快照：`{MENTOR_SNAPSHOT_DOC_REL}`  
本次变化说明：`{LATEST_CHANGE_DOC_REL}`  
下一步行动清单：`{NEXT_ACTION_DOC_REL}`  
风险登记表：`{RISK_REGISTER_DOC_REL}`  
提交就绪清单：`{SUBMISSION_READINESS_DOC_REL}`  
最终交付缺口板：`{FINAL_DELIVERY_GAP_DOC_REL}`  
阶段索引：`{PROGRESS_INDEX_DOC_REL}`  
巡检范围说明：`{WATCH_SCOPE_DOC_REL}`  
跟进操作规程：`{PROGRESS_PROTOCOL_DOC_REL}`  
状态复核台账：`{STATUS_REVIEW_DOC_REL}`  
最新巡检状态卡：`{LATEST_STATUS_REVIEW_DOC_REL}`  
最新阶段标记：`{ctx["marker"]}`

## 一句话结论

{verdict(ctx)}

## 目前做了什么

1. 固定测量方案：采用 2π 上半球测量面，半球面测点数为 162 个。
2. 完成文献调研、技术路线、方案报告骨架和三人分工材料。
3. 建立 Python 算法 baseline，包括近远场重建、测点删减、识别分类和鲁棒性扫描。
4. 建立 CST 数据接口，包括模板生成、导出校验、幅相归一化、Level 1/Level 2 manifest、批量合并和严格审计。
5. 完成 Level 1 required 标准源链路，当前 required-now 缺失文件为 {master.get("missing_required_now_files", 0)}。
6. 完成 Level 2 full48 样本链路，48/48 样本完整，识别 accuracy 为 1.000。
7. 完成 Level 2 简化结构遮挡对照，mean shadow 约 3.06 dB，cross-domain accuracy 为 1.000。
8. 建立总控 dashboard、completion audit、scorecard、赛题要求矩阵和 submission index。
9. 生成当前 submission 草稿包，草稿包中 {draft.get("copied_or_generated", 0)} 项已复制或生成，缺失源文件为 {draft.get("missing", 0)}。

## 本次变化摘要

{table(["类型", "变化/备注"], change_rows)}

## 当前产物是什么

{table(["产物", "路径", "作用"], artifact_rows)}

## 图表总览

{image_section(ctx, "project")}

## 关键状态数值

{table(["指标", "当前值"], key_rows)}

## 当前缺口

{table(["最终交付物", "路径", "状态"], final_file_rows())}

1. Level 1 solver-safe 重建精度存在风险，需要继续优化，或在报告中给出可辩护的误差机理说明。
2. Level 2 full48 属于 CST-derived element-library 证据，简化结构遮挡对照已补充，但仍需在报告中明确它不是 full-wave airframe scattering。
3. 正式提交前需要重新运行 scorecard、需求矩阵、submission index、completion audit、master dashboard 和 submission draft。

## 下一步建议

{table(["优先级", "负责人", "动作", "关闭证据"], next_action_rows)}

## 本轮核验依据

- `outputs/master_dashboard/master_dashboard_summary.json`
- `outputs/completion_audit/completion_audit_summary.json`
- `outputs/submission_index/submission_index_summary.json`
- `submission/submission_draft_summary.json`
- `outputs/master_dashboard/master_gate_summary.csv`
- `outputs/master_dashboard/master_next_actions.csv`
- `submission/01_report`
- `submission/02_presentation`
- `submission/03_video`
"""


def mentor_brief(ctx: dict[str, Any]) -> str:
    master = ctx["master"]
    submission = ctx["submission"]
    draft = ctx["draft"]
    counts = ctx["gate_counts"]

    stage_rows = [
        ["文献与方案", "已形成文献矩阵、技术路线、报告草稿和赛题要求矩阵", "`docs/literature_matrix.md`; `docs/solution_report_draft.md`"],
        ["测量布局", "已固定 2π 上半球测量面，162 个半球面测点", "`outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`"],
        ["Level 1 CST", f"required 标准源链路已完成，当前 required-now 缺失文件为 {master.get('missing_required_now_files', 0)}", "`outputs/cst_level1_merge_report`; `outputs/cst_level1_reconstruction_batch`"],
        ["Level 2 CST", "48/48 个 CST-derived element-library 样本完整，识别 accuracy 为 1.000；简化结构遮挡 cross-domain accuracy 为 1.000", "`outputs/cst_level2_merge_report`; `outputs/cst_recognition_level2`; `outputs/cst_structure_comparison`"],
        ["项目审计", "已生成 scorecard、completion audit、master dashboard、submission index", "`outputs/scorecard`; `outputs/completion_audit`; `outputs/master_dashboard`"],
        ["提交草稿", f"当前 submission 草稿包 {draft.get('copied_or_generated', 0)} 项已复制或生成，缺失源文件为 {draft.get('missing', 0)}", "`submission/`; `submission/submission_draft_summary.json`"],
    ]

    artifact_rows = [[name, path, meaning] for name, path, meaning in KEY_ARTIFACTS]
    risk_rows = [
        ["Level 1 solver-safe 重建精度风险", "影响标准源重建部分的可信度表达", "复核近远场一致性、等效源基函数和正则化；必要时形成误差机理说明"],
        ["Level 2 full48 主要是 element-library 叠加证据", "简化结构遮挡对照已生成，但不是 full-wave airframe", "把结构对照写入报告并明确适用边界；时间允许时再补 full-wave 对照"],
        [final_gap_phrase(ctx), "不能进入最终提交态", "在指标稳定后集中成稿并导出剩余正式文件"],
    ]
    next_action_rows = [
        [row.get("priority", ""), row.get("owner_role", ""), row.get("action", ""), row.get("proof_to_close", "")]
        for row in ctx["actions"][:4]
    ]
    change_rows = [[ctx.get("event_type", ""), item] for item in ctx.get("changes_since_previous", [])]
    submission_values = {
        "ready": int(submission.get("ready", 0) or 0),
        "draft_or_source_ready": int(submission.get("draft_or_source_ready", 0) or 0),
        "blocked": int(submission.get("blocked", 0) or 0),
        "missing": int(submission.get("missing", 0) or 0),
    }

    return f"""# 阶段进展汇报：赛题完成度与下一步

汇报时间：{ctx["timestamp"]}  
汇报对象：导师/组会快速阅读版  
阶段标记：`{ctx["marker"]}`

## 一句话结论

{verdict(ctx)}

## 本阶段做了什么

{table(["模块", "当前进展", "证据入口"], stage_rows)}

## 本次变化摘要

{table(["类型", "变化/备注"], change_rows)}

## 完成度图表

{image_section(ctx, "mentor")}

### Gate 状态分布

```mermaid
{pie("当前 Gate 状态", counts)}
```

### 主线流程状态

```mermaid
{gate_flow(ctx["gates"])}
```

### 提交物状态分布

```mermaid
{pie("Submission Index 状态", submission_values)}
```

### 最终交付物缺口

```mermaid
{final_file_mermaid()}
```

## 当前产物

{table(["产物", "路径", "导师可看点"], artifact_rows)}

## 当前风险

{table(["风险", "影响", "建议处理"], risk_rows)}

## 下一步建议

{table(["优先级", "负责人", "动作", "关闭证据"], next_action_rows)}

## 本次核验依据

- `outputs/master_dashboard/master_dashboard_summary.json`
- `outputs/completion_audit/completion_audit_summary.json`
- `outputs/submission_index/submission_index_summary.json`
- `submission/submission_draft_summary.json`
- `outputs/master_dashboard/master_gate_summary.csv`
- `outputs/master_dashboard/master_next_actions.csv`
- `submission/01_report`
- `submission/02_presentation`
- `submission/03_video`
"""


def rebuild_archive_readme(latest_report: str) -> str:
    reports = archived_mentor_reports()
    rows: list[list[str]] = []
    for path in reports:
        rel_path = path.relative_to(ROOT).as_posix()
        rows.append([archive_timestamp_label(path).replace(" +0800", ""), f"`{rel_path}`", "自动生成阶段汇报"])

    return f"""# 阶段进展汇报归档

本目录用于归档面向导师或组会的阶段性进展汇报。每当项目出现值得记录的进展、风险变化、交付物变化或阶段门关闭时，运行：

```powershell
python code\\build_progress_report.py --note "本阶段完成了某项关键进展"
```

脚本会刷新 `docs/project_progress_report.md`，生成带 PNG/Mermaid 图表的导师汇报，并更新 `outputs/progress_report/progress_history.csv` 历史台账。若没有阶段备注，可省略 `--note`。

若用于定时巡检，希望无变化时不新增归档，可运行：

```powershell
python code\\build_progress_report.py --only-if-changed
```

导师阅读门户见 `{MENTOR_PORTAL_DOC_REL}`，组会汇报稿见 `{MEETING_BRIEF_DOC_REL}`，每日进展汇总见 `{DAILY_DIGEST_DOC_REL}`，导师证据映射见 `{EVIDENCE_MAP_DOC_REL}`，导师决策清单见 `{DECISION_BRIEF_DOC_REL}`，导师问答卡见 `{MENTOR_QA_DOC_REL}`，G5 关闭路线见 `{G5_CLOSURE_DOC_REL}`，导师 30 秒快照见 `{MENTOR_SNAPSHOT_DOC_REL}`，本次变化说明见 `{LATEST_CHANGE_DOC_REL}`，下一步行动清单见 `{NEXT_ACTION_DOC_REL}`，风险登记表见 `{RISK_REGISTER_DOC_REL}`，提交就绪清单见 `{SUBMISSION_READINESS_DOC_REL}`，最终交付缺口板见 `{FINAL_DELIVERY_GAP_DOC_REL}`，阶段索引见 `{PROGRESS_INDEX_DOC_REL}`，巡检覆盖范围见 `{WATCH_SCOPE_DOC_REL}`，跟进操作规程见 `{PROGRESS_PROTOCOL_DOC_REL}`，状态复核台账见 `{STATUS_REVIEW_DOC_REL}`，最新巡检状态卡见 `{LATEST_STATUS_REVIEW_DOC_REL}`，最新导师汇报固定入口见 `{LATEST_MENTOR_BRIEF_REL}`。

## 命名规则

```text
YYYY-MM-DD_HHMM_mentor_brief.md
```

## 最新汇报

导师阅读门户：`{MENTOR_PORTAL_DOC_REL}`  
组会汇报稿：`{MEETING_BRIEF_DOC_REL}`  
每日进展汇总：`{DAILY_DIGEST_DOC_REL}`  
导师证据映射：`{EVIDENCE_MAP_DOC_REL}`  
导师决策清单：`{DECISION_BRIEF_DOC_REL}`  
导师问答卡：`{MENTOR_QA_DOC_REL}`  
G5 关闭路线：`{G5_CLOSURE_DOC_REL}`  
导师 30 秒快照：`{MENTOR_SNAPSHOT_DOC_REL}`  
本次变化说明：`{LATEST_CHANGE_DOC_REL}`  
下一步行动清单：`{NEXT_ACTION_DOC_REL}`  
风险登记表：`{RISK_REGISTER_DOC_REL}`  
提交就绪清单：`{SUBMISSION_READINESS_DOC_REL}`  
最终交付缺口板：`{FINAL_DELIVERY_GAP_DOC_REL}`  
固定入口（推荐）：`{LATEST_MENTOR_BRIEF_REL}`  
阶段索引：`{PROGRESS_INDEX_DOC_REL}`  
跟进操作规程：`{PROGRESS_PROTOCOL_DOC_REL}`  
状态复核台账：`{STATUS_REVIEW_DOC_REL}`  
最新巡检状态卡：`{LATEST_STATUS_REVIEW_DOC_REL}`  
本次归档：`{latest_report}`

## 汇报列表

{table(["时间", "文件", "主题"], rows)}
"""


def build(timestamp: str, archive: bool = True, note: str = "", only_if_changed: bool = False) -> dict[str, Any]:
    ctx = build_context(timestamp)
    ctx["note"] = note.strip()
    existing_history = read_progress_history()
    event_type, changes = summarize_changes(ctx, existing_history)
    ctx["event_type"] = event_type
    ctx["changes_since_previous"] = changes
    if only_if_changed and event_type == "status_review" and not ctx["note"]:
        summary = build_summary(
            ctx,
            archive=False,
            history_rows=existing_history,
            skipped=True,
            skip_reason="No core status changes and no --note were provided.",
        )
        status_rows = update_status_review_log(summary)
        write_text(STATUS_REVIEW_DOC, status_review_log_report(summary, status_rows))
        write_text(LATEST_STATUS_REVIEW_DOC, latest_status_review_card(summary, status_rows))
        write_text(FINAL_DELIVERY_GAP_DOC, final_delivery_gap_board(ctx))
        write_text(CURRENT_PROGRESS_BRIEF_DOC, current_progress_brief(ctx, summary, status_rows))
        write_text(G5_STALL_ALERT_DOC, g5_stall_alert(ctx, summary, status_rows))
        write_json(OUT_DIR / "progress_report_summary.json", summary)
        return summary

    ctx["assets"] = save_progress_charts(ctx)
    history_rows = update_progress_history(ctx)
    write_manifest_files(ctx)
    save_history_chart(ctx, history_rows)
    brief_rel = ctx["latest_report"]
    brief_path = ROOT / brief_rel

    write_text(PROGRESS_REPORT, progress_report(ctx))
    if archive:
        brief_content = mentor_brief(ctx)
        write_text(brief_path, brief_content)
        write_text(LATEST_MENTOR_BRIEF, brief_content)
    write_text(LATEST_CHANGE_DOC, latest_change_note(ctx, history_rows))
    write_text(NEXT_ACTION_DOC, next_action_brief(ctx))
    write_text(RISK_REGISTER_DOC, risk_register(ctx))
    write_text(SUBMISSION_READINESS_DOC, submission_readiness(ctx))
    write_text(FINAL_DELIVERY_GAP_DOC, final_delivery_gap_board(ctx))
    write_text(MENTOR_PORTAL_DOC, mentor_portal(ctx, history_rows))
    write_text(MEETING_BRIEF_DOC, meeting_brief(ctx, history_rows))
    write_text(DAILY_DIGEST_DOC, daily_digest(ctx, history_rows))
    write_text(EVIDENCE_MAP_DOC, evidence_map(ctx))
    write_text(DECISION_BRIEF_DOC, decision_brief(ctx))
    write_text(MENTOR_QA_DOC, mentor_qa(ctx))
    write_text(G5_CLOSURE_DOC, g5_closure_brief(ctx))
    write_text(MENTOR_SNAPSHOT_DOC, mentor_snapshot(ctx))
    write_text(WATCH_SCOPE_DOC, watch_scope_report(ctx))
    write_text(PROGRESS_PROTOCOL_DOC, progress_update_protocol(ctx))
    write_text(PROGRESS_INDEX_DOC, progress_index_report(ctx, history_rows))
    write_text(REPORT_DIR / "README.md", rebuild_archive_readme(brief_rel))

    summary = build_summary(ctx, archive=archive, history_rows=history_rows)
    status_rows = remove_status_review_log_entry(ctx["timestamp"])
    write_text(STATUS_REVIEW_DOC, status_review_log_report(summary, status_rows))
    write_text(LATEST_STATUS_REVIEW_DOC, latest_status_review_card(summary, status_rows))
    write_text(CURRENT_PROGRESS_BRIEF_DOC, current_progress_brief(ctx, summary, status_rows))
    write_text(G5_STALL_ALERT_DOC, g5_stall_alert(ctx, summary, status_rows))
    write_json(OUT_DIR / "progress_report_summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build project progress tracker and mentor brief.")
    parser.add_argument("--timestamp", default=None, help="Override timestamp, e.g. 2026-05-29 01:40:00 +0800.")
    parser.add_argument("--no-archive", action="store_true", help="Only refresh docs/project_progress_report.md.")
    parser.add_argument("--note", default="", help="Optional milestone note to show in reports and history.")
    parser.add_argument("--only-if-changed", action="store_true", help="Skip writing a new archived report when no core status changed and no note is provided.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timestamp = now_string(args.timestamp)
    summary = build(timestamp, archive=not args.no_archive, note=args.note, only_if_changed=args.only_if_changed)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
