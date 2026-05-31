from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CST_PYTHON = Path(
    r"D:\Program Files (x86)\CST Studio Suite 2025\Opera\code\bin\python.exe"
)
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_solver_trials"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return str(value)


def safe_call(obj: Any, name: str, *args: Any) -> dict[str, Any]:
    if not hasattr(obj, name):
        return {"ok": False, "error": f"missing method {name}"}
    try:
        return {"ok": True, "value": jsonable(getattr(obj, name)(*args))}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": repr(exc)}


def copy_project_to_trial(source_project: Path, trial_dir: Path, trial_name: str) -> Path:
    trial_dir.mkdir(parents=True, exist_ok=True)
    target = trial_dir / trial_name
    if target.suffix.lower() != ".cst":
        target = target.with_suffix(".cst")
    shutil.copy2(source_project, target)
    return target


def worker_run(args: argparse.Namespace) -> int:
    import cst.interface

    project = resolve_path(args.project)
    summary_out = resolve_path(args.summary_out)
    started_at = time.monotonic()
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "status": "started",
        "real_cst_api_used": True,
        "project": str(project),
        "project_exists": project.exists(),
        "timeout_seconds": args.timeout_seconds,
        "poll_seconds": args.poll_seconds,
    }
    write_json(summary_out, summary)

    de = cst.interface.DesignEnvironment()
    prj = de.open_project(str(project))
    try:
        model = prj.model3d
        before_items = safe_call(model, "get_tree_items")
        before_tree_items = before_items.get("value", []) if before_items.get("ok") else []
        summary["tree_count_before"] = len(before_tree_items) if isinstance(before_tree_items, list) else 0
        summary["farfield_items_before"] = [
            item for item in before_tree_items if isinstance(item, str) and item.startswith("Farfields\\")
        ]

        start_result = safe_call(model, "start_solver")
        if not start_result["ok"]:
            start_result = safe_call(model, "RunSolver")
        summary["solver_start_result"] = start_result
        if not start_result["ok"]:
            summary.update(
                {
                    "completed_at": now_iso(),
                    "status": "failed_to_start",
                    "elapsed_seconds": time.monotonic() - started_at,
                }
            )
            write_json(summary_out, summary)
            return 1

        poll_log: list[dict[str, Any]] = []
        timed_out = False
        while True:
            running_result = safe_call(model, "is_solver_running")
            solver_info = safe_call(model, "get_solver_info")
            poll_log.append(
                {
                    "elapsed_seconds": round(time.monotonic() - started_at, 3),
                    "is_solver_running": running_result,
                    "solver_info": solver_info,
                }
            )
            running = bool(running_result.get("value")) if running_result.get("ok") else False
            if not running:
                break
            if time.monotonic() - started_at > args.timeout_seconds:
                timed_out = True
                break
            time.sleep(args.poll_seconds)

        save_project = safe_call(prj, "save")
        after_items = safe_call(model, "get_tree_items")
        after_tree_items = after_items.get("value", []) if after_items.get("ok") else []
        farfield_items_after = [
            item for item in after_tree_items if isinstance(item, str) and item.startswith("Farfields\\")
        ]
        last_solver_info = poll_log[-1]["solver_info"] if poll_log else {}
        last_solver_value = last_solver_info.get("value", {}) if isinstance(last_solver_info, dict) else {}
        last_solver_state = ""
        if isinstance(last_solver_value, dict):
            last_solver_state = str(last_solver_value.get("state", ""))
        status = "timed_out" if timed_out else "finished"
        if last_solver_state and last_solver_state.upper() not in {"SUCCESS", "FINISHED"}:
            status = "solver_reported_non_success"
        if not farfield_items_after:
            status = "finished_without_farfield_results" if status == "finished" else status

        summary.update(
            {
                "completed_at": now_iso(),
                "status": status,
                "elapsed_seconds": time.monotonic() - started_at,
                "poll_count": len(poll_log),
                "poll_log_tail": poll_log[-20:],
                "last_solver_info": last_solver_info,
                "save_project": save_project,
                "tree_count_after": len(after_tree_items) if isinstance(after_tree_items, list) else 0,
                "farfield_items_after": farfield_items_after,
                "project_size_bytes": project.stat().st_size if project.exists() else 0,
            }
        )
        write_json(summary_out, summary)
        return 0 if status == "finished" else 1
    finally:
        try:
            prj.close()
        except Exception:
            pass


def controller_run(args: argparse.Namespace) -> int:
    source_project = resolve_path(args.project)
    trial_dir = resolve_path(args.out_dir)
    trial_project = source_project
    if not args.in_place:
        trial_name = args.trial_name or f"{source_project.stem}_solver_trial.cst"
        trial_project = copy_project_to_trial(source_project, trial_dir, trial_name)

    summary_out = resolve_path(args.summary_out) if args.summary_out else trial_dir / f"{trial_project.stem}_solver_summary.json"
    stdout_log = resolve_path(args.stdout_log) if args.stdout_log else trial_dir / f"{trial_project.stem}_solver_stdout.log"
    if not args.cst_python.exists():
        write_json(
            summary_out,
            {
                "created_at": now_iso(),
                "status": "failed",
                "real_cst_api_used": False,
                "error": f"CST Python not found: {args.cst_python}",
                "source_project": str(source_project),
                "trial_project": str(trial_project),
            },
        )
        return 1

    command = [
        str(args.cst_python),
        str(Path("src") / Path(__file__).name),
        "--worker",
        "--project",
        str(trial_project),
        "--summary-out",
        str(summary_out),
        "--timeout-seconds",
        str(args.timeout_seconds),
        "--poll-seconds",
        str(args.poll_seconds),
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=args.timeout_seconds + 120,
    )
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    stdout_log.write_text(completed.stdout, encoding="utf-8")
    summary = {}
    if summary_out.exists():
        try:
            summary = json.loads(summary_out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {}
    summary.update(
        {
            "controller_returncode": completed.returncode,
            "source_project": str(source_project),
            "trial_project": str(trial_project),
            "stdout_log": str(stdout_log),
        }
    )
    write_json(summary_out, summary)
    return completed.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a CST solver for one project and write a reproducible summary.")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--project", required=True, help="Input .cst project.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--trial-name", default="")
    parser.add_argument("--summary-out", default="")
    parser.add_argument("--stdout-log", default="")
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.worker:
        return worker_run(args)
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
