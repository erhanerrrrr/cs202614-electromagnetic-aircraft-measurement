from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRIAL_DIR = ROOT / "outputs" / "cst_solver_trials" / "meshsafe_huygens_source_family"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_source_family_solver_status"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isfinite(number):
        return number
    return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def field_from_filename(path: Path) -> tuple[str, str]:
    name = path.name
    for field_kind in ("efield", "hfield"):
        suffix = f"_{field_kind}_solver_summary.json"
        if name.endswith(suffix):
            return name[: -len(suffix)], field_kind
    return path.stem.replace("_solver_summary", ""), ""


def log_tail_text(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    solver_logs = summary.get("solver_logs", {})
    for item in solver_logs.get("log_files", []):
        for line in item.get("tail", []) or []:
            lines.append(str(line))
    return "\n".join(lines)


def regex_group(text: str, pattern: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""
    return match.group(1)


def category_count(summary: dict[str, Any], needle: str) -> int:
    counts = summary.get("result_items_after_summary", {}).get("category_counts", {})
    values: list[int] = []
    for key, value in counts.items():
        if needle.lower() in str(key).lower():
            parsed = as_int(value)
            if parsed is not None:
                values.append(parsed)
    return max(values, default=0)


def summarize_trial(path: Path) -> dict[str, Any]:
    summary = read_json(path)
    sample_id, field_kind = field_from_filename(path)
    text = log_tail_text(summary)
    artifacts = summary.get("solver_logs", {}).get("result_artifacts", {})
    solver_start = summary.get("solver_start_result", {})
    save_project = summary.get("save_project", {})

    max_time_steps = regex_group(text, r"Maximum number of time steps:\s*([0-9]+)")
    time_step_width_ns = regex_group(text, r"used:\s*([0-9.eE+-]+)\s*ns")
    excitation_duration_ns = regex_group(text, r"Excitation duration:\s*([0-9.eE+-]+)\s*ns")
    steady_state_accuracy_db = regex_group(text, r"Steady state accuracy limit:\s*([+-]?[0-9.]+)\s*dB")

    return {
        "sample_id": sample_id,
        "field_kind": field_kind,
        "status": str(summary.get("status", "")),
        "real_cst_api_used": bool(summary.get("real_cst_api_used", False)),
        "project_exists": bool(summary.get("project_exists", False)),
        "solver_start_ok": bool(solver_start.get("ok", False) and solver_start.get("value", False)),
        "elapsed_seconds": as_float(summary.get("elapsed_seconds")),
        "timeout_seconds": as_float(summary.get("timeout_seconds")),
        "poll_count": as_int(summary.get("poll_count")),
        "result_tree_count_after": as_int(summary.get("result_tree_count_after")),
        "probe_result_count": max(category_count(summary, "1D Results\\Probes\\E-Field"), category_count(summary, "1D Results\\Probes\\H-Field")),
        "has_nearfield_artifact": bool(artifacts.get("has_nearfield_artifact", False)),
        "has_farfield_artifact": bool(artifacts.get("has_farfield_artifact", False)),
        "artifact_count": as_int(artifacts.get("artifact_count")) or 0,
        "max_time_steps": as_int(max_time_steps),
        "time_step_width_ns": as_float(time_step_width_ns),
        "excitation_duration_ns": as_float(excitation_duration_ns),
        "steady_state_accuracy_db": as_float(steady_state_accuracy_db),
        "open_boundary_warning": "open boundary condition" in text.lower(),
        "farfield_adjusted_to_model_box": "farfield monitor" in text.lower() and "adjusted to model box" in text.lower(),
        "save_project_ok": bool(save_project.get("ok", False)),
        "save_project_error": str(save_project.get("error", "")),
        "source_project": str(summary.get("source_project", "")),
        "trial_project": str(summary.get("trial_project", summary.get("project", ""))),
        "summary_path": display_path(path),
    }


def determine_stage(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "source_family_solver_status_missing"
    statuses = {str(row.get("status", "")) for row in rows}
    completed_statuses = {"completed", "complete", "success", "succeeded", "solver_completed"}
    completed_count = sum(1 for row in rows if str(row.get("status", "")) in completed_statuses)
    timed_out_count = sum(1 for row in rows if str(row.get("status", "")) == "timed_out")
    if timed_out_count and completed_count == 0:
        return "source_family_solver_pilot_timed_out"
    if timed_out_count:
        return "source_family_solver_partial_with_timeout"
    if completed_count == len(rows):
        return "source_family_solver_completed"
    if statuses:
        return "source_family_solver_partial"
    return "source_family_solver_status_missing"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "sample_id",
        "field_kind",
        "status",
        "real_cst_api_used",
        "project_exists",
        "solver_start_ok",
        "elapsed_seconds",
        "timeout_seconds",
        "poll_count",
        "result_tree_count_after",
        "probe_result_count",
        "has_nearfield_artifact",
        "has_farfield_artifact",
        "artifact_count",
        "max_time_steps",
        "time_step_width_ns",
        "excitation_duration_ns",
        "steady_state_accuracy_db",
        "open_boundary_warning",
        "farfield_adjusted_to_model_box",
        "save_project_ok",
        "save_project_error",
        "source_project",
        "trial_project",
        "summary_path",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# CST Huygens Source-Family Solver Pilot Status",
        "",
        "This report records the first real CST solver pilot for the independent source-family workpack.",
        "",
        "## Status",
        "",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Trial summaries found: `{summary['trial_count']}`",
        f"- Timed-out trials: `{summary['timed_out_count']}`",
        f"- Completed trials: `{summary['completed_count']}`",
        f"- Solver starts OK: `{summary['solver_start_ok_count']}/{summary['trial_count']}`",
        "",
        "The current evidence shows a CST runtime/settings bottleneck, not a CST project-generation failure. The pilot started through the real CST API and populated ResultTree probe entries, but it did not finish cleanly enough to export matched local E/H CSVs or far-field references.",
        "",
        "## Trial Rows",
        "",
        "| Sample | Field | Status | Elapsed / s | Timeout / s | Probe results | Max time steps | Artifact count |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['sample_id']}` | `{row['field_kind']}` | `{row['status']}` | "
            f"{format_value(row['elapsed_seconds'])} | {format_value(row['timeout_seconds'])} | "
            f"{format_value(row['probe_result_count'])} | {format_value(row['max_time_steps'])} | "
            f"{format_value(row['artifact_count'])} |"
        )
    lines.extend(
        [
            "",
            "## Next Gate",
            "",
            "Build a solver-safe pilot before running the full 12-project queue. The immediate target is the same short x-oriented case with adjusted CST solver settings or a frequency-domain/fast-path variant, followed by ResultTree export validation.",
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\build_cst_source_family_solver_status.py",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_status(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    trial_dir = Path(args.trial_dir)
    rows = [summarize_trial(path) for path in sorted(trial_dir.glob("*_solver_summary.json"))]
    stage_status = determine_stage(rows)
    completed_statuses = {"completed", "complete", "success", "succeeded", "solver_completed"}
    timed_out_count = sum(1 for row in rows if row["status"] == "timed_out")
    completed_count = sum(1 for row in rows if row["status"] in completed_statuses)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage_status": stage_status,
        "trial_dir": display_path(trial_dir),
        "trial_count": len(rows),
        "timed_out_count": timed_out_count,
        "completed_count": completed_count,
        "solver_start_ok_count": sum(1 for row in rows if row["solver_start_ok"]),
        "real_cst_api_used_count": sum(1 for row in rows if row["real_cst_api_used"]),
        "export_artifact_ready_count": sum(1 for row in rows if row["has_nearfield_artifact"] or row["has_farfield_artifact"]),
        "max_elapsed_seconds": max((row["elapsed_seconds"] or 0.0 for row in rows), default=0.0),
        "max_time_steps": max((row["max_time_steps"] or 0 for row in rows), default=0),
        "next_gate": "repair CST solver settings or create a frequency-domain/fast-path pilot before running the full source-family queue",
        "trials": rows,
    }
    return summary, rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize CST source-family solver pilot evidence.")
    parser.add_argument("--trial-dir", type=Path, default=DEFAULT_TRIAL_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, rows = build_status(args)

    (out_dir / "source_family_solver_status_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(out_dir / "source_family_solver_trials.csv", rows)
    write_markdown(out_dir / "source_family_solver_status.md", summary, rows)

    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "out_dir": display_path(out_dir),
                "trial_count": summary["trial_count"],
                "timed_out_count": summary["timed_out_count"],
                "completed_count": summary["completed_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
