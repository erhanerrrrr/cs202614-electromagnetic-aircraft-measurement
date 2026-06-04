from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN_DIR = ROOT / "data" / "cst_meshsafe_huygens_source_family_solver_safe_pilot"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_source_family_solver_safe_status"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def resolve_repo_path(text: str) -> Path:
    path = Path(text)
    if path.is_absolute():
        return path
    return ROOT / path


def summarize_trial(plan_row: dict[str, str]) -> dict[str, Any]:
    summary_path = resolve_repo_path(plan_row.get("summary_out", ""))
    summary = read_json(summary_path)
    artifacts = summary.get("solver_logs", {}).get("result_artifacts", {}) if summary else {}
    solver_start = summary.get("solver_start_result", {}) if summary else {}
    return {
        "execution_order": plan_row.get("execution_order", ""),
        "ladder_id": plan_row.get("ladder_id", ""),
        "sample_id": plan_row.get("sample_id", ""),
        "probe_mode": plan_row.get("probe_mode", ""),
        "probe_rows": plan_row.get("probe_rows", ""),
        "planned_timeout_seconds": plan_row.get("timeout_seconds", ""),
        "summary_path": display_path(summary_path),
        "summary_exists": summary_path.exists(),
        "status": str(summary.get("status", "not_run")) if summary else "not_run",
        "real_cst_api_used": bool(summary.get("real_cst_api_used", False)) if summary else False,
        "solver_start_ok": bool(solver_start.get("ok", False) and solver_start.get("value", False)),
        "elapsed_seconds": as_float(summary.get("elapsed_seconds")) if summary else None,
        "result_tree_count_after": as_int(summary.get("result_tree_count_after")) if summary else None,
        "artifact_count": as_int(artifacts.get("artifact_count")) if artifacts else 0,
        "has_nearfield_artifact": bool(artifacts.get("has_nearfield_artifact", False)),
        "has_farfield_artifact": bool(artifacts.get("has_farfield_artifact", False)),
        "generate_command": plan_row.get("generate_command", ""),
        "solve_command": plan_row.get("solve_command", ""),
        "gate_interpretation": plan_row.get("gate_interpretation", ""),
    }


def determine_stage(plan_exists: bool, rows: list[dict[str, Any]]) -> str:
    if not plan_exists:
        return "source_family_solver_safe_plan_missing"
    if not rows or not any(row["summary_exists"] for row in rows):
        return "source_family_solver_safe_pilot_plan_ready"
    finished = [row for row in rows if row["status"] == "finished"]
    timed_out = [row for row in rows if row["status"] == "timed_out"]
    full_finished = any(row["ladder_id"] == "efield96" and row["status"] == "finished" for row in rows)
    all_run = all(row["summary_exists"] for row in rows)
    if full_finished:
        return "source_family_solver_safe_full_efield_finished"
    if finished and all_run and not timed_out:
        return "source_family_solver_safe_ladder_completed"
    if finished:
        return "source_family_solver_safe_ladder_partial"
    if timed_out:
        return "source_family_solver_safe_trials_timed_out"
    return "source_family_solver_safe_trials_started"


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# CST source-family solver-safe status",
        "",
        "This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.",
        "",
        "## Status",
        "",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Planned trials: `{summary['planned_trial_count']}`",
        f"- Executed trials: `{summary['trial_count']}`",
        f"- Finished trials: `{summary['finished_count']}`",
        f"- Timed-out trials: `{summary['timed_out_count']}`",
        "",
        "## Trial rows",
        "",
        "| Order | Ladder | Mode | Probes | Status | Elapsed / s | Artifacts |",
        "|---:|---|---|---:|---|---:|---:|",
    ]
    for row in rows:
        elapsed = "" if row["elapsed_seconds"] is None else f"{float(row['elapsed_seconds']):.1f}"
        lines.append(
            f"| {row['execution_order']} | `{row['ladder_id']}` | `{row['probe_mode']}` | "
            f"{row['probe_rows']} | `{row['status']}` | {elapsed} | {row['artifact_count']} |"
        )
    lines.extend(["", "## Next command", ""])
    if summary.get("next_ladder_id"):
        lines.extend(
            [
                f"Next diagnostic row: `{summary['next_ladder_id']}`.",
                "",
                "```powershell",
                str(summary.get("next_generate_command", "")),
                str(summary.get("next_solve_command", "")),
                "python code\\build_cst_source_family_solver_safe_status.py",
                "python code\\build_g3_model_dashboard.py",
                "```",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "All planned diagnostic rows have a trial summary. Refresh status and inspect failures before running broader queues.",
                "",
                "```powershell",
                "python code\\build_cst_source_family_solver_safe_status.py",
                "python code\\build_g3_model_dashboard.py",
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_status(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan_dir = Path(args.plan_dir)
    plan_summary_path = plan_dir / "solver_safe_pilot_plan_summary.json"
    commands_path = plan_dir / "solver_safe_pilot_commands.csv"
    plan_summary = read_json(plan_summary_path)
    plan_rows = read_csv_rows(commands_path)
    trial_rows = [summarize_trial(row) for row in plan_rows]
    stage_status = determine_stage(plan_summary_path.exists(), trial_rows)
    trial_count = sum(1 for row in trial_rows if row["summary_exists"])
    next_row = next((row for row in trial_rows if not row["summary_exists"]), None)
    if next_row:
        next_gate = (
            f"run next diagnostic row {next_row['ladder_id']}: generate the CST project, solve it, "
            "then rebuild solver-safe status and the G3 dashboard"
        )
        next_ladder_id = next_row["ladder_id"]
        next_generate_command = next_row["generate_command"]
        next_solve_command = next_row["solve_command"]
    else:
        next_gate = "all planned solver-safe diagnostic rows have summaries; inspect pass/fail pattern before expanding the source-family queue"
        next_ladder_id = ""
        next_generate_command = ""
        next_solve_command = ""
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage_status": stage_status,
        "plan_summary_path": display_path(plan_summary_path),
        "commands_path": display_path(commands_path),
        "plan_exists": plan_summary_path.exists(),
        "target_sample_id": plan_summary.get("target_sample_id", ""),
        "full_probe_row_count": plan_summary.get("full_probe_row_count", ""),
        "planned_trial_count": len(plan_rows),
        "trial_count": trial_count,
        "finished_count": sum(1 for row in trial_rows if row["status"] == "finished"),
        "timed_out_count": sum(1 for row in trial_rows if row["status"] == "timed_out"),
        "solver_start_ok_count": sum(1 for row in trial_rows if row["solver_start_ok"]),
        "artifact_ready_count": sum(
            1 for row in trial_rows if row["has_nearfield_artifact"] or row["has_farfield_artifact"]
        ),
        "next_gate": next_gate,
        "next_ladder_id": next_ladder_id,
        "next_generate_command": next_generate_command,
        "next_solve_command": next_solve_command,
        "trials": trial_rows,
    }
    return summary, trial_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize CST source-family solver-safe ladder status.")
    parser.add_argument("--plan-dir", type=Path, default=DEFAULT_PLAN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, rows = build_status(args)
    (out_dir / "solver_safe_status_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(
        out_dir / "solver_safe_trial_status.csv",
        rows,
        [
            "execution_order",
            "ladder_id",
            "sample_id",
            "probe_mode",
            "probe_rows",
            "planned_timeout_seconds",
            "summary_path",
            "summary_exists",
            "status",
            "real_cst_api_used",
            "solver_start_ok",
            "elapsed_seconds",
            "result_tree_count_after",
            "artifact_count",
            "has_nearfield_artifact",
            "has_farfield_artifact",
            "generate_command",
            "solve_command",
            "gate_interpretation",
        ],
    )
    write_markdown(out_dir / "solver_safe_status.md", summary, rows)
    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "out_dir": display_path(out_dir),
                "planned_trial_count": summary["planned_trial_count"],
                "trial_count": summary["trial_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
