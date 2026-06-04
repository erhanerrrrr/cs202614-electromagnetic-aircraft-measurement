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
RESULT_JSON_RELATIVE_PATHS = (
    "Result/simulation_overview.json",
    "Result/output.json",
)
RESULT_ARTIFACT_SUFFIXES = {".ffm", ".fme", ".m3d"}


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


def timeout_output_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
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


def read_json_safe(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text, _encoding = read_text_safe(path)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"_json_error": "decode_failed", "_text_tail": tail_lines(text, keep=12)}
    return data if isinstance(data, dict) else {"value": data}


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
        "maximal path length",
    )
    lines: list[str] = []
    seen: set[str] = set()
    raw_lines = text.splitlines()
    include_next = 0
    for line in raw_lines:
        stripped = line.strip()
        lowered = f" {stripped.lower()} "
        triggered = any(needle in lowered for needle in needles)
        if not stripped:
            continue
        if not triggered and include_next <= 0:
            continue
        if stripped in seen:
            include_next = max(include_next - 1, 0)
            continue
        seen.add(stripped)
        lines.append(stripped)
        include_next = 3 if triggered else max(include_next - 1, 0)
        if len(lines) >= limit:
            break
    return lines


def result_item_summary(items: list[str], sample_size: int = 80) -> dict[str, Any]:
    category_counts: dict[str, int] = {}
    for item in items:
        parts = item.split("\\")
        if len(parts) >= 3:
            category = "\\".join(parts[:3])
        elif len(parts) >= 2:
            category = "\\".join(parts[:2])
        else:
            category = item
        category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "count": len(items),
        "category_counts": dict(sorted(category_counts.items())),
        "sample": items[:sample_size],
        "omitted_count": max(0, len(items) - sample_size),
    }


def collect_result_artifacts(project: Path) -> dict[str, Any]:
    result_dir = project.with_suffix("")
    artifacts: list[dict[str, Any]] = []
    if result_dir.exists():
        for path in sorted(result_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in RESULT_ARTIFACT_SUFFIXES:
                continue
            artifacts.append(
                {
                    "path": display_path(path),
                    "name": path.name,
                    "suffix": path.suffix.lower(),
                    "size_bytes": path.stat().st_size,
                }
            )
    suffix_counts: dict[str, int] = {}
    for artifact in artifacts:
        suffix = str(artifact["suffix"])
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
    return {
        "result_dir": display_path(result_dir),
        "artifact_count": len(artifacts),
        "suffix_counts": suffix_counts,
        "has_farfield_artifact": any(row["suffix"] in {".ffm", ".fme"} for row in artifacts),
        "has_nearfield_artifact": any(row["suffix"] == ".m3d" for row in artifacts),
        "artifacts": artifacts[:40],
        "omitted_count": max(0, len(artifacts) - 40),
    }


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

    result_jsons: dict[str, Any] = {}
    for relative_text in RESULT_JSON_RELATIVE_PATHS:
        json_path = result_dir / Path(*relative_text.split("/"))
        result_jsons[Path(relative_text).name] = {
            "path": display_path(json_path),
            "exists": json_path.exists(),
            "data": read_json_safe(json_path),
        }

    combined = "\n".join(combined_parts)
    mesh_match = re.search(r"Simulation setup for\s+([\d.]+)\s+billion mesh cells", combined, re.IGNORECASE)
    mpi_match = re.search(r"at least\s+(\d+)\s+cluster nodes", combined, re.IGNORECASE)
    mesh_cell_count_billion = float(mesh_match.group(1)) if mesh_match else None
    required_mpi_nodes = int(mpi_match.group(1)) if mpi_match else None
    path_length_limit_detected = "exceeds the maximal path length" in combined
    output_data = result_jsons.get("output.json", {}).get("data", {})
    output_messages = output_data.get("messages", []) if isinstance(output_data, dict) else []
    output_message_text = "\n".join(
        str(row.get("message", "")) for row in output_messages if isinstance(row, dict)
    )
    simulation_data = result_jsons.get("simulation_overview.json", {}).get("data", {})
    solver_run = (
        simulation_data.get("solver_runs_and_tasks", {})
        .get("solver_run", {})
        if isinstance(simulation_data, dict)
        else {}
    )
    return {
        "project_result_dir": display_path(result_dir),
        "log_files": log_files,
        "result_jsons": result_jsons,
        "result_artifacts": collect_result_artifacts(project),
        "error_lines": unique_error_lines(combined),
        "mesh_cell_count_billion": mesh_cell_count_billion,
        "required_mpi_nodes": required_mpi_nodes,
        "mesh_limit_detected": bool(mesh_cell_count_billion and required_mpi_nodes),
        "path_length_limit_detected": path_length_limit_detected,
        "encoding_warning_detected": "Expecting local encoding" in combined,
        "aborted_keeping_results_detected": "aborted by user (keeping results)" in output_message_text.lower(),
        "solver_return_code": solver_run.get("return_code") if isinstance(solver_run, dict) else None,
        "solver_used": solver_run.get("solver_used") if isinstance(solver_run, dict) else None,
        "solver_run_time_seconds": (
            solver_run.get("time_info", {}).get("run_time")
            if isinstance(solver_run, dict) and isinstance(solver_run.get("time_info"), dict)
            else None
        ),
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
    if solver_logs.get("path_length_limit_detected"):
        lines.extend(
            [
                "- Parsed path-length issue: CST reported a project/result path longer than its supported limit",
                "",
                "Interpretation: rerun this trial from a shorter ASCII path such as `C:\\csttmp\\huy_short` before treating the solve as numerically blocked.",
            ]
        )
    result_artifacts = solver_logs.get("result_artifacts", {})
    if solver_logs.get("aborted_keeping_results_detected"):
        lines.extend(
            [
                "- CST output status: solver was aborted while keeping generated results",
                f"- Result artifacts found: `{result_artifacts.get('artifact_count', 0)}`",
                f"- Farfield artifacts present: `{result_artifacts.get('has_farfield_artifact', False)}`",
                f"- Nearfield artifacts present: `{result_artifacts.get('has_nearfield_artifact', False)}`",
                "",
                "Interpretation: this is not a clean completed solve, but it may contain exportable CST result artifacts for a follow-up extraction attempt.",
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
    summary["checkpoint"] = "before_design_environment"
    write_json(summary_out, summary)

    de = cst.interface.DesignEnvironment()
    summary["checkpoint"] = "before_open_project"
    write_json(summary_out, summary)
    prj = de.open_project(str(project))
    try:
        summary["checkpoint"] = "before_model3d"
        write_json(summary_out, summary)
        model = prj.model3d
        summary["checkpoint"] = "before_initial_tree_query"
        write_json(summary_out, summary)
        before_items = safe_call(model, "get_tree_items")
        before_tree_items = before_items.get("value", []) if before_items.get("ok") else []
        summary["tree_count_before"] = len(before_tree_items) if isinstance(before_tree_items, list) else 0
        summary["result_tree_roots_before"] = result_tree_roots(before_tree_items)
        summary["result_tree_count_before"] = len(result_tree_items(before_tree_items))
        summary["farfield_items_before"] = farfield_tree_items(before_tree_items)
        summary["checkpoint"] = "before_solver_start"
        write_json(summary_out, summary)

        start_result = safe_call(model, "start_solver")
        if not start_result["ok"]:
            start_result = safe_call(model, "RunSolver")
        summary["solver_start_result"] = start_result
        summary["checkpoint"] = "solver_start_returned"
        write_json(summary_out, summary)
        if not start_result["ok"]:
            summary.update(
                {
                    "completed_at": now_iso(),
                    "status": "failed_to_start",
                    "checkpoint": "failed_to_start",
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
            summary["checkpoint"] = "solver_polling"
            summary["poll_count"] = len(poll_log)
            summary["last_poll"] = poll_log[-1]
            write_json(summary_out, summary)
            running = bool(running_result.get("value")) if running_result.get("ok") else False
            if not running:
                break
            if time.monotonic() - started_at > args.timeout_seconds:
                timed_out = True
                break
            time.sleep(args.poll_seconds)

        timeout_stop_solver: dict[str, Any] = {}
        if timed_out:
            for stop_name in ("abort_solver", "AbortSolver", "stop_solver", "StopSolver"):
                timeout_stop_solver = safe_call(model, stop_name)
                if timeout_stop_solver.get("ok"):
                    break

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
        elif solver_logs.get("path_length_limit_detected"):
            status = "solver_path_length_limit"
        elif (
            status == "timed_out"
            and solver_logs.get("aborted_keeping_results_detected")
            and solver_logs.get("result_artifacts", {}).get("artifact_count", 0)
        ):
            status = "aborted_keeping_results"
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
                "checkpoint": "completed",
                "elapsed_seconds": time.monotonic() - started_at,
                "poll_count": len(poll_log),
                "poll_log_tail": poll_log[-20:],
                "last_solver_info": last_solver_info,
                "timeout_stop_solver": timeout_stop_solver,
                "save_project": save_project,
                "tree_count_after": len(after_tree_items) if isinstance(after_tree_items, list) else 0,
                "result_tree_roots_after": result_tree_roots(after_tree_items),
                "result_tree_count_after": len(result_items_after),
                "result_items_after_summary": result_item_summary(result_items_after),
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
    stdout_log.parent.mkdir(parents=True, exist_ok=True)
    try:
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
    except subprocess.TimeoutExpired as exc:
        stdout_log.write_text(
            timeout_output_text(exc.stdout) + timeout_output_text(exc.stderr),
            encoding="utf-8",
        )
        summary = {}
        if summary_out.exists():
            try:
                summary = json.loads(summary_out.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                summary = {}
        summary.update(
            {
                "completed_at": now_iso(),
                "status": "controller_timeout",
                "controller_timeout_seconds": args.timeout_seconds + 120,
                "controller_timeout_error": repr(exc),
                "source_project": display_path(source_project),
                "trial_project": display_path(trial_project),
                "stdout_log": display_path(stdout_log),
            }
        )
        write_json(summary_out, summary)
        write_trial_readme(trial_dir, summary)
        return 124
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
