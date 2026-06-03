from __future__ import annotations

import argparse
import json
import re
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
RESULT_TREE_ROOTS = ("1D Results", "2D/3D Results", "Tables", "Farfields")
RESULT_TREE_PREFIXES = tuple(f"{root}\\" for root in RESULT_TREE_ROOTS)
SOLVER_LOG_RELATIVE_PATHS = (
    "Result/Model.log",
    "Result/output.txt",
    "Result/outputDS.txt",
    "Result/hexmeshengine.log",
    "Result/ml_info.log",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def display_path(path_text: str | Path) -> str:
    path = Path(path_text)
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


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


def result_tree_items(tree_items: Any) -> list[str]:
    if not isinstance(tree_items, list):
        return []
    return [
        item
        for item in tree_items
        if isinstance(item, str) and item.startswith(RESULT_TREE_PREFIXES)
    ]


def result_tree_roots(tree_items: Any) -> list[str]:
    if not isinstance(tree_items, list):
        return []
    return [item for item in tree_items if isinstance(item, str) and item in RESULT_TREE_ROOTS]


def farfield_tree_items(tree_items: Any) -> list[str]:
    return [
        item
        for item in result_tree_items(tree_items)
        if item.startswith("Farfields\\") or "\\Farfields\\" in item or "\\Farfield\\" in item
    ]


def read_text_safe(path: Path) -> tuple[str, str]:
    last_error = ""
    for encoding in ("utf-8-sig", "utf-16", "mbcs", "cp1252", "latin-1"):
        try:
            text = path.read_text(encoding=encoding, errors="replace")
        except Exception as exc:  # noqa: BLE001
            last_error = repr(exc)
            continue
        if text and text.count("\x00") / max(len(text), 1) > 0.1:
            last_error = f"decoded with many NULs using {encoding}"
            continue
        return text, encoding
    return f"<failed to read {path}: {last_error}>", "unreadable"


def tail_lines(text: str, keep: int = 24) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return lines[-keep:]


def unique_error_lines(text: str, limit: int = 20) -> list[str]:
    needles = (
        "*** error ***",
        " error ",
        "error:",
        "requires:",
        "simulation cannot be started",
        "expecting local encoding",
    )
    lines: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        lowered = f" {stripped.lower()} "
        if not stripped or not any(needle in lowered for needle in needles):
            continue
        if stripped in seen:
            continue
        seen.add(stripped)
        lines.append(stripped)
        if len(lines) >= limit:
            break
    return lines


def collect_solver_logs(project: Path) -> dict[str, Any]:
    result_dir = project.with_suffix("")
    log_files: list[dict[str, Any]] = []
    combined_parts: list[str] = []
    for relative_text in SOLVER_LOG_RELATIVE_PATHS:
        log_path = result_dir / Path(*relative_text.split("/"))
        entry: dict[str, Any] = {
            "path": display_path(log_path),
            "exists": log_path.exists(),
        }
        if log_path.exists():
            text, encoding = read_text_safe(log_path)
            entry.update(
                {
                    "encoding": encoding,
                    "size_bytes": log_path.stat().st_size,
                    "tail": tail_lines(text),
                }
            )
            combined_parts.append(text)
        log_files.append(entry)

    combined = "\n".join(combined_parts)
    mesh_match = re.search(r"Simulation setup for\s+([\d.]+)\s+billion mesh cells", combined, re.IGNORECASE)
    mpi_match = re.search(r"at least\s+(\d+)\s+cluster nodes", combined, re.IGNORECASE)
    mesh_cell_count_billion = float(mesh_match.group(1)) if mesh_match else None
    required_mpi_nodes = int(mpi_match.group(1)) if mpi_match else None
    return {
        "project_result_dir": display_path(result_dir),
        "log_files": log_files,
        "error_lines": unique_error_lines(combined),
        "mesh_cell_count_billion": mesh_cell_count_billion,
        "required_mpi_nodes": required_mpi_nodes,
        "mesh_limit_detected": bool(mesh_cell_count_billion and required_mpi_nodes),
        "encoding_warning_detected": "Expecting local encoding" in combined,
    }


def write_trial_readme(trial_dir: Path, summary: dict[str, Any]) -> None:
    solver_logs = summary.get("solver_logs", {}) if isinstance(summary.get("solver_logs"), dict) else {}
    lines = [
        "# CST solver trial diagnostic",
        "",
        f"- Status: `{summary.get('status', 'unknown')}`",
        f"- Source project: `{summary.get('source_project', '')}`",
        f"- Trial project: `{summary.get('trial_project', '')}`",
        f"- CST API start result: `{summary.get('solver_start_result', {})}`",
        f"- Result-tree child items after solve: `{summary.get('result_tree_count_after', 0)}`",
    ]
    if solver_logs.get("mesh_limit_detected"):
        lines.extend(
            [
                f"- Parsed mesh size: `{solver_logs.get('mesh_cell_count_billion')}` billion cells",
                f"- Parsed MPI requirement: `{solver_logs.get('required_mpi_nodes')}` cluster nodes",
                "",
                "Interpretation: CST could start the solver, but the full-wave setup is too large for the local machine.",
                "The 13 m measurement shell should be treated as a Python-side extrapolation target, not as a remote probe mesh inside this CST solve.",
            ]
        )
    error_lines = solver_logs.get("error_lines", [])
    if error_lines:
        lines.extend(["", "## Key log lines", ""])
        lines.extend(f"- `{line}`" for line in error_lines[:12])
    readme = trial_dir / "README.md"
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def worker_run(args: argparse.Namespace) -> int:
    import cst.interface

    project = resolve_path(args.project)
    summary_out = resolve_path(args.summary_out)
    started_at = time.monotonic()
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "status": "started",
        "real_cst_api_used": True,
        "project": display_path(project),
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
        summary["result_tree_roots_before"] = result_tree_roots(before_tree_items)
        summary["result_tree_count_before"] = len(result_tree_items(before_tree_items))
        summary["farfield_items_before"] = farfield_tree_items(before_tree_items)

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
        result_items_after = result_tree_items(after_tree_items)
        farfield_items_after = farfield_tree_items(after_tree_items)
        solver_logs = collect_solver_logs(project)
        last_solver_info = poll_log[-1]["solver_info"] if poll_log else {}
        last_solver_value = last_solver_info.get("value", {}) if isinstance(last_solver_info, dict) else {}
        last_solver_state = ""
        if isinstance(last_solver_value, dict):
            last_solver_state = str(last_solver_value.get("state", ""))
        status = "timed_out" if timed_out else "finished"
        if solver_logs.get("mesh_limit_detected"):
            status = "solver_mesh_limit"
        elif status == "finished" and last_solver_state and last_solver_state.upper() not in {"SUCCESS", "FINISHED"}:
            status = "solver_reported_non_success"
        elif status == "finished" and not result_items_after:
            status = "finished_without_result_tree_items"
        elif status == "finished" and not farfield_items_after:
            status = "finished_without_farfield_results"

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
                "result_tree_roots_after": result_tree_roots(after_tree_items),
                "result_tree_count_after": len(result_items_after),
                "result_items_after": result_items_after,
                "farfield_items_after": farfield_items_after,
                "project_size_bytes": project.stat().st_size if project.exists() else 0,
                "solver_logs": solver_logs,
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
                "source_project": display_path(source_project),
                "trial_project": display_path(trial_project),
            },
        )
        return 1

    command = [
        str(args.cst_python),
        str(Path(__file__).resolve()),
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
            "source_project": display_path(source_project),
            "trial_project": display_path(trial_project),
            "stdout_log": display_path(stdout_log),
        }
    )
    write_json(summary_out, summary)
    write_trial_readme(trial_dir, summary)
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
