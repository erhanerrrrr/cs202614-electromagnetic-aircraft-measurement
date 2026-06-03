from __future__ import annotations

import argparse
import csv
import json
import math
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
DEFAULT_MANIFEST = (
    ROOT
    / "data"
    / "cst_true_nearfield_workpack"
    / "operator_packet"
    / "required_full_grid_manifest.csv"
)
DEFAULT_SENSOR_SHELL = (
    ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_sensor_shell.csv"
)
DEFAULT_PROJECT_DIR = ROOT / "outputs" / "cst_real_level1_projects" / "projects"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_true_nearfield_monitor_export"
CONTRACT_COLUMNS = [
    "sample_id",
    "frequency_hz",
    "sensor_id",
    "x_m",
    "y_m",
    "z_m",
    "theta_deg",
    "phi_deg",
    "radius_m",
    "polarization",
    "e_real",
    "e_imag",
    "cst_project",
    "cst_monitor_item",
    "extraction_method",
]
COMPONENTS = ["Ex", "Ey", "Ez"]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path: str | Path) -> str:
    full = resolve_path(path)
    try:
        return str(full.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(full)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv_rows(path: Path, rows: list[dict[str, Any]], columns: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if columns is None:
        columns = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item) for item in value]
    return str(value)


def safe_call(obj: Any, name: str, *args: Any) -> dict[str, Any]:
    if not hasattr(obj, name):
        return {"ok": False, "error": f"missing method {name}"}
    try:
        return {"ok": True, "value": jsonable(getattr(obj, name)(*args))}
    except Exception as exc:  # noqa: BLE001 - CST API methods vary by version.
        return {"ok": False, "error": repr(exc)}


def compact_tree_result(result: dict[str, Any]) -> dict[str, Any]:
    value = result.get("value")
    if result.get("ok") and isinstance(value, list):
        return {"ok": True, "value_count": len(value)}
    return result


def filter_manifest_rows(
    manifest_rows: list[dict[str, str]],
    sample_filter: set[str] | None,
    limit: int,
) -> list[dict[str, str]]:
    rows = []
    for row in manifest_rows:
        sample_id = str(row.get("sample_id", "")).strip()
        if sample_filter is not None and sample_id not in sample_filter:
            continue
        rows.append(row)
    rows.sort(key=lambda row: as_int(row.get("queue_order")))
    if limit > 0:
        rows = rows[:limit]
    if not rows:
        raise ValueError("no required true-nearfield manifest rows selected")
    return rows


def load_sensor_shell(path: Path) -> list[dict[str, str]]:
    rows = read_csv_rows(path)
    rows.sort(key=lambda row: as_int(row.get("sensor_id")))
    return rows


def build_tasks(
    manifest_rows: list[dict[str, str]],
    sensor_shell: list[dict[str, str]],
    project_dir: Path,
    overwrite: bool,
) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    sensor_count = len(sensor_shell)
    for row in manifest_rows:
        sample_id = str(row.get("sample_id", "")).strip()
        project_name = str(row.get("cst_project", "")).strip()
        project_path = Path(project_name)
        if not project_path.is_absolute():
            project_path = project_dir / project_name
        shell_path = resolve_path(row.get("sample_shell_csv") or DEFAULT_SENSOR_SHELL)
        target_path = resolve_path(row.get("target_export_path", ""))
        expected_sensor_count = as_int(row.get("expected_sensor_count"), sensor_count)
        expected_rows = as_int(row.get("expected_export_rows"), expected_sensor_count * len(COMPONENTS))
        target_exists = target_path.exists()
        project_exists = project_path.exists()
        shell_exists = shell_path.exists()
        status = "ready_for_cst_export"
        blockers: list[str] = []
        if target_exists and not overwrite:
            status = "target_exists"
        if not project_exists:
            status = "blocked"
            blockers.append("missing CST project")
        if not shell_exists:
            status = "blocked"
            blockers.append("missing sensor shell CSV")
        if sensor_count != expected_sensor_count:
            status = "blocked"
            blockers.append(f"sensor shell row count {sensor_count} != expected {expected_sensor_count}")
        tasks.append(
            {
                "queue_order": as_int(row.get("queue_order")),
                "sample_id": sample_id,
                "frequency_hz": as_int(row.get("frequency_hz")),
                "frequency_label": str(row.get("frequency_label", "")).strip(),
                "cst_project": project_name,
                "project_path": str(project_path),
                "project_exists": project_exists,
                "project_size_bytes": project_path.stat().st_size if project_exists else 0,
                "true_nearfield_monitor": str(row.get("true_nearfield_monitor", "")).strip(),
                "sample_shell_csv": rel(shell_path),
                "sensor_count": sensor_count,
                "expected_sensor_count": expected_sensor_count,
                "expected_export_rows": expected_rows,
                "target_export_path": rel(target_path),
                "target_export_exists": target_exists,
                "reference_nearfield_export": rel(row.get("reference_nearfield_export", "")),
                "reference_export_exists": resolve_path(row.get("reference_nearfield_export", "")).exists(),
                "dropzone_command": str(row.get("dropzone_command", "")).strip(),
                "gate_command": str(row.get("gate_command", "")).strip(),
                "comparison_command": str(row.get("comparison_command", "")).strip(),
                "status": status,
                "blockers": blockers,
            }
        )
    return tasks


def task_plan_rows(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task in tasks:
        rows.append(
            {
                "queue_order": task["queue_order"],
                "sample_id": task["sample_id"],
                "frequency_hz": task["frequency_hz"],
                "cst_project": task["cst_project"],
                "project_exists": task["project_exists"],
                "project_size_bytes": task["project_size_bytes"],
                "true_nearfield_monitor": task["true_nearfield_monitor"],
                "sample_shell_csv": task["sample_shell_csv"],
                "sensor_count": task["sensor_count"],
                "expected_export_rows": task["expected_export_rows"],
                "target_export_path": task["target_export_path"],
                "target_export_exists": task["target_export_exists"],
                "reference_export_exists": task["reference_export_exists"],
                "status": task["status"],
                "blockers": ";".join(task["blockers"]),
            }
        )
    return rows


def build_readme(summary: dict[str, Any]) -> str:
    dry_run_line = (
        "This run was a dry-run task-plan refresh; no CST project was opened."
        if summary.get("dry_run")
        else "This run attempted to open CST projects through CST Python."
    )
    lines = [
        "# CST True Near-Field Monitor Export",
        "",
        "Purpose: make the G3 true-monitor blocker executable and auditable.",
        "",
        dry_run_line,
        "",
        "The worker records `Field Monitors`/`Probes` definition nodes for diagnosis, but ASCII export is attempted only on solved result-tree nodes under `1D Results`, `2D/3D Results`, or `Tables`.",
        "",
        "## Current Summary",
        "",
        f"- Selected tasks: {summary.get('selected_task_count')}",
        f"- Ready tasks: {summary.get('ready_task_count')}",
        f"- Target CSVs already present: {summary.get('target_present_count')}",
        f"- CST Python exists: {summary.get('cst_python_exists')}",
        f"- Controller status: `{summary.get('status')}`",
        "",
        "## Files",
        "",
        "| File | Purpose |",
        "|---|---|",
        "| `true_nearfield_export_task_plan.csv` | Selected required CST projects, target CSVs, blockers, and current file status. |",
        "| `true_nearfield_export_summary.json` | Machine-readable controller summary. |",
        "| `true_nearfield_export_stdout.log` | CST worker stdout/stderr when a non-dry run is attempted. |",
        "| `worker_case_results.csv` | Per-case worker result, created after CST worker execution. |",
        "",
        "After target CSVs are written, run:",
        "",
        "```powershell",
        "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
        "python code\\run_true_nearfield_gate.py --required-only --candidate full_grid_162",
        "python code\\run_true_nearfield_workflow_decision.py",
        "```",
        "",
    ]
    return "\n".join(lines)


def write_controller_outputs(
    out_dir: Path,
    tasks: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv_rows(
        out_dir / "true_nearfield_export_task_plan.csv",
        task_plan_rows(tasks),
        [
            "queue_order",
            "sample_id",
            "frequency_hz",
            "cst_project",
            "project_exists",
            "project_size_bytes",
            "true_nearfield_monitor",
            "sample_shell_csv",
            "sensor_count",
            "expected_export_rows",
            "target_export_path",
            "target_export_exists",
            "reference_export_exists",
            "status",
            "blockers",
        ],
    )
    write_json(out_dir / "true_nearfield_export_summary.json", summary)
    (out_dir / "README.md").write_text(build_readme(summary), encoding="utf-8")


def copy_inputs(out_dir: Path, manifest: Path, sensor_shell: Path) -> None:
    input_dir = out_dir / "input_snapshots"
    input_dir.mkdir(parents=True, exist_ok=True)
    for source in [manifest, sensor_shell]:
        if source.exists():
            shutil.copy2(source, input_dir / source.name)


def run_solver_if_requested(model: Any, timeout_seconds: int, poll_seconds: float) -> dict[str, Any]:
    started_at = time.monotonic()
    start_result = safe_call(model, "start_solver")
    if not start_result["ok"]:
        start_result = safe_call(model, "RunSolver")
    poll_log: list[dict[str, Any]] = []
    if not start_result["ok"]:
        return {
            "requested": True,
            "status": "failed_to_start",
            "start_result": start_result,
            "elapsed_seconds": 0,
            "poll_log_tail": poll_log,
        }
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
        if time.monotonic() - started_at > timeout_seconds:
            timed_out = True
            break
        time.sleep(poll_seconds)
    return {
        "requested": True,
        "status": "timed_out" if timed_out else "finished",
        "start_result": start_result,
        "elapsed_seconds": round(time.monotonic() - started_at, 3),
        "poll_log_tail": poll_log[-20:],
    }


def discover_tree_items(model: Any) -> tuple[list[str], dict[str, Any]]:
    tree_result = safe_call(model, "get_tree_items")
    value = tree_result.get("value", [])
    if not isinstance(value, list):
        return [], tree_result
    return [str(item) for item in value], tree_result


def likely_true_nearfield_items(tree_items: list[str], monitor_name: str) -> list[str]:
    tokens = [
        monitor_name.lower(),
        "nearfield",
        "near field",
        "e-field",
        "efield",
        "electric field",
        "probe",
    ]
    candidates = []
    for item in tree_items:
        lowered = item.lower()
        if any(token and token in lowered for token in tokens):
            candidates.append(item)
    return candidates


def has_tree_root(item: str, root: str) -> bool:
    lowered = item.strip().lower()
    root = root.lower()
    return lowered == root or lowered.startswith(f"{root}\\") or lowered.startswith(f"{root}/")


def is_definition_tree_item(item: str) -> bool:
    return has_tree_root(item, "field monitors") or has_tree_root(item, "probes")


def is_exportable_result_tree_item(item: str) -> bool:
    return (
        has_tree_root(item, "1d results")
        or has_tree_root(item, "2d/3d results")
        or has_tree_root(item, "tables")
    )


def likely_definition_true_nearfield_items(tree_items: list[str], monitor_name: str) -> list[str]:
    return [item for item in likely_true_nearfield_items(tree_items, monitor_name) if is_definition_tree_item(item)]


def likely_exportable_true_nearfield_items(tree_items: list[str], monitor_name: str) -> list[str]:
    return [
        item
        for item in likely_true_nearfield_items(tree_items, monitor_name)
        if is_exportable_result_tree_item(item) and not is_definition_tree_item(item)
    ]


def write_shell_contract_rows(
    target_path: Path,
    task: dict[str, Any],
    sensor_shell: list[dict[str, str]],
    component_values: dict[tuple[int, str], complex],
    monitor_item: str,
    extraction_method: str,
) -> int:
    rows: list[dict[str, Any]] = []
    for sensor in sensor_shell:
        sensor_id = as_int(sensor.get("sensor_id"))
        for component in COMPONENTS:
            value = component_values.get((sensor_id, component), 0.0 + 0.0j)
            rows.append(
                {
                    "sample_id": task["sample_id"],
                    "frequency_hz": int(task["frequency_hz"]),
                    "sensor_id": sensor_id,
                    "x_m": sensor.get("x_m", ""),
                    "y_m": sensor.get("y_m", ""),
                    "z_m": sensor.get("z_m", ""),
                    "theta_deg": sensor.get("theta_deg", ""),
                    "phi_deg": sensor.get("phi_deg", ""),
                    "radius_m": sensor.get("radius_m", ""),
                    "polarization": component,
                    "e_real": f"{value.real:.12e}",
                    "e_imag": f"{value.imag:.12e}",
                    "cst_project": rel(task["project_path"]),
                    "cst_monitor_item": monitor_item,
                    "extraction_method": extraction_method,
                }
            )
    write_csv_rows(target_path, rows, CONTRACT_COLUMNS)
    return len(rows)


def parse_float_tokens(line: str) -> list[float]:
    cleaned = line.replace(",", " ").replace(";", " ").replace("\t", " ")
    values: list[float] = []
    for token in cleaned.split():
        try:
            values.append(float(token))
        except ValueError:
            continue
    return values


def nearest_sensor_id(
    x: float,
    y: float,
    z: float,
    sensors: list[dict[str, str]],
    tolerance_m: float,
) -> int | None:
    best_id: int | None = None
    best_dist = float("inf")
    for sensor in sensors:
        sx = as_float(sensor.get("x_m"))
        sy = as_float(sensor.get("y_m"))
        sz = as_float(sensor.get("z_m"))
        dist = math.sqrt((x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2)
        if dist < best_dist:
            best_dist = dist
            best_id = as_int(sensor.get("sensor_id"))
    if best_dist <= tolerance_m:
        return best_id
    return None


def parse_raw_cartesian_ascii(
    raw_path: Path,
    sensors: list[dict[str, str]],
    tolerance_m: float,
) -> dict[tuple[int, str], complex]:
    values: dict[tuple[int, str], complex] = {}
    if not raw_path.exists():
        return values
    for line in raw_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        numbers = parse_float_tokens(line)
        # Expected fallback shape: x y z Re(Ex) Im(Ex) Re(Ey) Im(Ey) Re(Ez) Im(Ez)
        if len(numbers) < 9:
            continue
        sensor_id = nearest_sensor_id(numbers[0], numbers[1], numbers[2], sensors, tolerance_m)
        if sensor_id is None:
            continue
        values[(sensor_id, "Ex")] = complex(numbers[3], numbers[4])
        values[(sensor_id, "Ey")] = complex(numbers[5], numbers[6])
        values[(sensor_id, "Ez")] = complex(numbers[7], numbers[8])
    return values


def try_ascii_export(model: Any, item: str, raw_path: Path) -> dict[str, Any]:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    escaped_item = item.replace('"', '""')
    escaped_path = str(raw_path).replace("\\", "\\\\").replace('"', '""')
    history = f'''
SelectTreeItem ("{escaped_item}")
With ASCIIExport
    .Reset
    .FileName ("{escaped_path}")
    .Mode ("FixedNumber")
    .Step (1)
    .Execute
End With
'''
    add_result = safe_call(model, "add_to_history", "export_true_nearfield_ascii", history)
    return {
        "item": item,
        "raw_path": str(raw_path),
        "add_to_history": add_result,
        "raw_exists": raw_path.exists(),
        "raw_size_bytes": raw_path.stat().st_size if raw_path.exists() else 0,
    }


def worker_export_case(
    model: Any,
    task: dict[str, Any],
    sensor_shell: list[dict[str, str]],
    raw_dir: Path,
    overwrite: bool,
    nearest_tolerance_m: float,
) -> dict[str, Any]:
    target_path = resolve_path(task["target_export_path"])
    if target_path.exists() and not overwrite:
        return {
            "sample_id": task["sample_id"],
            "status": "skipped_target_exists",
            "target_csv_written": False,
            "target_export_path": rel(target_path),
            "target_rows": "",
        }
    tree_items, tree_result = discover_tree_items(model)
    monitor_name = str(task.get("true_nearfield_monitor", ""))
    candidates = likely_true_nearfield_items(tree_items, monitor_name)
    definition_candidates = likely_definition_true_nearfield_items(tree_items, monitor_name)
    exportable_candidates = likely_exportable_true_nearfield_items(tree_items, monitor_name)
    result: dict[str, Any] = {
        "sample_id": task["sample_id"],
        "status": "no_parseable_true_nearfield_export",
        "status_detail": "",
        "target_csv_written": False,
        "target_export_path": rel(target_path),
        "target_rows": "",
        "tree_item_count": len(tree_items),
        "tree_result": compact_tree_result(tree_result),
        "candidate_items": candidates[:50],
        "candidate_count": len(candidates),
        "definition_candidate_items": definition_candidates[:50],
        "exportable_result_items": exportable_candidates[:50],
        "definition_candidate_count": len(definition_candidates),
        "exportable_result_count": len(exportable_candidates),
        "raw_export_attempts": [],
    }
    if not exportable_candidates:
        if definition_candidates:
            result.update(
                {
                    "status": "no_solved_result_tree_items",
                    "status_detail": (
                        "CST true near-field monitor/probe definitions exist, but no solved "
                        "result-tree items were found under 1D Results, 2D/3D Results, or Tables."
                    ),
                }
            )
        else:
            result.update(
                {
                    "status": "no_candidate_tree_items",
                    "status_detail": "No true near-field/probe definition or solved result-tree item was found.",
                }
            )
        return result
    for index, item in enumerate(exportable_candidates[:10], start=1):
        raw_path = raw_dir / f"{task['sample_id']}_candidate_{index:02d}.txt"
        export_result = try_ascii_export(model, item, raw_path)
        component_values = parse_raw_cartesian_ascii(raw_path, sensor_shell, nearest_tolerance_m)
        complete_sensor_components = len(component_values)
        export_result["parsed_component_values"] = complete_sensor_components
        result["raw_export_attempts"].append(export_result)
        if complete_sensor_components == len(sensor_shell) * len(COMPONENTS):
            rows_written = write_shell_contract_rows(
                target_path=target_path,
                task=task,
                sensor_shell=sensor_shell,
                component_values=component_values,
                monitor_item=item,
                extraction_method="CST true near-field monitor/probe ASCII export parsed on spherical shell",
            )
            result.update(
                {
                    "status": "export_complete",
                    "target_csv_written": True,
                    "target_rows": rows_written,
                    "cst_monitor_item": item,
                    "extraction_method": "CST true near-field monitor/probe ASCII export parsed on spherical shell",
                }
            )
            return result
    result["status_detail"] = "Solved result-tree candidates were found, but none parsed to a complete 162-point Ex/Ey/Ez shell."
    return result


def worker_run(config_path: Path, worker_summary_path: Path) -> int:
    import cst.interface

    config = json.loads(config_path.read_text(encoding="utf-8"))
    tasks: list[dict[str, Any]] = config["tasks"]
    sensor_shell: list[dict[str, str]] = config["sensor_shell"]
    out_dir = Path(config["out_dir"])
    raw_dir = out_dir / "raw_ascii_exports"
    run_solver = bool(config.get("run_solver", False))
    inspect_only = bool(config.get("inspect_only", False))
    overwrite = bool(config.get("overwrite", False))
    timeout_seconds = int(config.get("timeout_seconds", 900))
    poll_seconds = float(config.get("poll_seconds", 5.0))
    nearest_tolerance_m = float(config.get("nearest_tolerance_m", 1e-6))
    worker_results: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "status": "started",
        "real_cst_api_used": True,
        "run_solver": run_solver,
        "inspect_only": inspect_only,
        "task_count": len(tasks),
        "cases": worker_results,
    }
    write_json(worker_summary_path, summary)

    de = cst.interface.DesignEnvironment()
    try:
        for task in tasks:
            project_path = resolve_path(task["project_path"])
            case_result: dict[str, Any] = {
                "sample_id": task["sample_id"],
                "cst_project": task.get("cst_project", ""),
                "project_path": rel(project_path),
                "project_exists": project_path.exists(),
                "target_export_path": task.get("target_export_path", ""),
                "status": "started",
            }
            worker_results.append(case_result)
            if not project_path.exists():
                case_result.update({"status": "missing_project", "error": "CST project file is missing"})
                continue
            prj = de.open_project(str(project_path))
            try:
                model = prj.model3d
                before_items, before_tree_result = discover_tree_items(model)
                before_monitor = str(task.get("true_nearfield_monitor", ""))
                before_candidates = likely_true_nearfield_items(before_items, before_monitor)
                before_definition_candidates = likely_definition_true_nearfield_items(
                    before_items,
                    before_monitor,
                )
                before_exportable_candidates = likely_exportable_true_nearfield_items(
                    before_items,
                    before_monitor,
                )
                case_result["tree_count_before"] = len(before_items)
                case_result["candidate_items_before"] = before_candidates[:50]
                case_result["candidate_count_before"] = len(before_candidates)
                case_result["definition_candidate_items_before"] = before_definition_candidates[:50]
                case_result["definition_candidate_count_before"] = len(before_definition_candidates)
                case_result["exportable_result_items_before"] = before_exportable_candidates[:50]
                case_result["exportable_result_count_before"] = len(before_exportable_candidates)
                case_result["tree_result_before"] = compact_tree_result(before_tree_result)
                if run_solver:
                    case_result["solver"] = run_solver_if_requested(model, timeout_seconds, poll_seconds)
                    case_result["save_project"] = safe_call(prj, "save")
                after_items, after_tree_result = discover_tree_items(model)
                after_monitor = str(task.get("true_nearfield_monitor", ""))
                after_candidates = likely_true_nearfield_items(after_items, after_monitor)
                after_definition_candidates = likely_definition_true_nearfield_items(
                    after_items,
                    after_monitor,
                )
                after_exportable_candidates = likely_exportable_true_nearfield_items(
                    after_items,
                    after_monitor,
                )
                case_result["tree_count_after"] = len(after_items)
                case_result["candidate_items_after"] = after_candidates[:50]
                case_result["candidate_count_after"] = len(after_candidates)
                case_result["definition_candidate_items_after"] = after_definition_candidates[:50]
                case_result["definition_candidate_count_after"] = len(after_definition_candidates)
                case_result["exportable_result_items_after"] = after_exportable_candidates[:50]
                case_result["exportable_result_count_after"] = len(after_exportable_candidates)
                case_result["tree_result_after"] = compact_tree_result(after_tree_result)
                if inspect_only:
                    tree_path = out_dir / f"{task['sample_id']}_tree_items.json"
                    write_json(
                        tree_path,
                        {
                            "sample_id": task["sample_id"],
                            "cst_project": task.get("cst_project", ""),
                            "project_path": rel(project_path),
                            "tree_items": after_items,
                            "candidate_items": case_result["candidate_items_after"],
                            "candidate_count": case_result["candidate_count_after"],
                            "definition_candidate_items": case_result["definition_candidate_items_after"],
                            "definition_candidate_count": case_result["definition_candidate_count_after"],
                            "exportable_result_items": case_result["exportable_result_items_after"],
                            "exportable_result_count": case_result["exportable_result_count_after"],
                        },
                    )
                    case_result.update(
                        {
                            "status": "inspected",
                            "tree_items_json": str(tree_path),
                            "target_csv_written": False,
                        }
                    )
                    continue
                export_result = worker_export_case(
                    model=model,
                    task=task,
                    sensor_shell=sensor_shell,
                    raw_dir=raw_dir,
                    overwrite=overwrite,
                    nearest_tolerance_m=nearest_tolerance_m,
                )
                case_result.update(export_result)
            except Exception as exc:  # noqa: BLE001 - CST runtime failure must be captured.
                case_result.update({"status": "failed", "error": repr(exc)})
            finally:
                try:
                    prj.close()
                except Exception:
                    pass
    finally:
        try:
            de.close()
        except Exception as exc:  # noqa: BLE001
            summary["close_error"] = repr(exc)

    exported = sum(1 for row in worker_results if row.get("status") == "export_complete")
    inspected = sum(1 for row in worker_results if row.get("status") == "inspected")
    if inspect_only:
        status = "inspection_complete" if inspected == len(tasks) and tasks else "inspection_incomplete"
        returncode = 0 if inspected == len(tasks) and tasks else 1
    else:
        status = "export_complete" if exported == len(tasks) and tasks else "incomplete"
        returncode = 0 if exported == len(tasks) and tasks else 1
    summary.update(
        {
            "completed_at": now_iso(),
            "status": status,
            "exported_count": exported,
            "inspected_count": inspected,
            "cases": worker_results,
        }
    )
    write_json(worker_summary_path, summary)
    return returncode


def run_worker(config_path: Path, worker_summary_path: Path, args: argparse.Namespace) -> subprocess.CompletedProcess[str]:
    command = [
        str(args.cst_python),
        str(Path(__file__).resolve()),
        "--worker",
        str(config_path),
        str(worker_summary_path),
    ]
    return subprocess.run(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=args.timeout_seconds + 180,
    )


def controller_run(args: argparse.Namespace) -> int:
    out_dir = resolve_path(args.out_dir)
    manifest_path = resolve_path(args.manifest)
    sensor_shell_path = resolve_path(args.sensor_shell)
    project_dir = resolve_path(args.project_dir)
    manifest_rows = filter_manifest_rows(
        read_csv_rows(manifest_path),
        set(args.sample_id) if args.sample_id else None,
        args.limit,
    )
    sensor_shell = load_sensor_shell(sensor_shell_path)
    tasks = build_tasks(manifest_rows, sensor_shell, project_dir, args.overwrite)
    copy_inputs(out_dir, manifest_path, sensor_shell_path)

    ready_count = sum(1 for task in tasks if task["status"] in {"ready_for_cst_export", "target_exists"})
    target_present_count = sum(1 for task in tasks if task["target_export_exists"])
    blocked_count = sum(1 for task in tasks if task["status"] == "blocked")
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "generated_by": "code/export_cst_true_nearfield_monitor.py",
        "status": "dry_run_complete" if args.dry_run else "planned",
        "dry_run": args.dry_run,
        "inspect_only": args.inspect_only,
        "run_solver": args.run_solver,
        "manifest": rel(manifest_path),
        "sensor_shell": rel(sensor_shell_path),
        "project_dir": rel(project_dir),
        "out_dir": rel(out_dir),
        "cst_python": str(args.cst_python),
        "cst_python_exists": args.cst_python.exists(),
        "selected_task_count": len(tasks),
        "ready_task_count": ready_count,
        "blocked_task_count": blocked_count,
        "target_present_count": target_present_count,
        "task_plan": rel(out_dir / "true_nearfield_export_task_plan.csv"),
        "next_command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
    }
    write_controller_outputs(out_dir, tasks, summary)
    if args.dry_run:
        print(f"CST true near-field export dry-run written to {rel(out_dir)}")
        print(f"selected tasks: {len(tasks)}, ready: {ready_count}, blocked: {blocked_count}")
        return 0
    if blocked_count:
        summary.update(
            {
                "completed_at": now_iso(),
                "status": "blocked_before_cst_worker",
                "error": "one or more selected tasks are missing required project/sensor inputs",
            }
        )
        write_controller_outputs(out_dir, tasks, summary)
        return 1
    if not args.cst_python.exists():
        summary.update(
            {
                "completed_at": now_iso(),
                "status": "failed",
                "error": f"CST Python not found: {args.cst_python}",
            }
        )
        write_controller_outputs(out_dir, tasks, summary)
        return 1

    config_path = out_dir / "true_nearfield_export_worker_input.json"
    worker_summary_path = out_dir / "true_nearfield_export_worker_summary.json"
    stdout_path = out_dir / "true_nearfield_export_stdout.log"
    config = {
        "created_at": now_iso(),
        "tasks": tasks,
        "sensor_shell": sensor_shell,
        "out_dir": str(out_dir),
        "run_solver": args.run_solver,
        "inspect_only": args.inspect_only,
        "overwrite": args.overwrite,
        "timeout_seconds": args.timeout_seconds,
        "poll_seconds": args.poll_seconds,
        "nearest_tolerance_m": args.nearest_tolerance_m,
    }
    write_json(config_path, config)
    completed = run_worker(config_path, worker_summary_path, args)
    stdout_path.write_text(completed.stdout, encoding="utf-8")

    worker_summary: dict[str, Any] = {}
    if worker_summary_path.exists():
        try:
            worker_summary = json.loads(worker_summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            worker_summary = {}
    case_rows: list[dict[str, Any]] = []
    for case in worker_summary.get("cases", []):
        case_rows.append(
            {
                "sample_id": case.get("sample_id", ""),
                "project_exists": case.get("project_exists", ""),
                "status": case.get("status", ""),
                "status_detail": case.get("status_detail", ""),
                "tree_count_before": case.get("tree_count_before", ""),
                "tree_count_after": case.get("tree_count_after", ""),
                "candidate_count_after": case.get(
                    "candidate_count_after",
                    case.get("candidate_count", len(case.get("candidate_items_after", case.get("candidate_items", [])))),
                ),
                "definition_candidate_count_after": case.get(
                    "definition_candidate_count_after",
                    case.get(
                        "definition_candidate_count",
                        len(case.get("definition_candidate_items_after", case.get("definition_candidate_items", []))),
                    ),
                ),
                "exportable_result_count_after": case.get(
                    "exportable_result_count_after",
                    case.get(
                        "exportable_result_count",
                        len(case.get("exportable_result_items_after", case.get("exportable_result_items", []))),
                    ),
                ),
                "target_csv_written": case.get("target_csv_written", ""),
                "target_export_path": case.get("target_export_path", ""),
                "target_rows": case.get("target_rows", ""),
                "error": case.get("error", ""),
            }
        )
    if case_rows:
        write_csv_rows(
            out_dir / "worker_case_results.csv",
            case_rows,
            [
                "sample_id",
                "project_exists",
                "status",
                "status_detail",
                "tree_count_before",
                "tree_count_after",
                "candidate_count_after",
                "definition_candidate_count_after",
                "exportable_result_count_after",
                "target_csv_written",
                "target_export_path",
                "target_rows",
                "error",
            ],
        )
    summary.update(
        {
            "completed_at": now_iso(),
            "status": worker_summary.get("status", "failed"),
            "controller_returncode": completed.returncode,
            "worker_summary": rel(worker_summary_path),
            "stdout_log": rel(stdout_path),
            "exported_count": int(worker_summary.get("exported_count", 0)),
            "inspected_count": int(worker_summary.get("inspected_count", 0)),
        }
    )
    write_controller_outputs(out_dir, tasks, summary)
    return completed.returncode


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan, inspect, or export the required CST true near-field monitor CSVs."
    )
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("worker_config", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("worker_summary", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--sensor-shell", type=Path, default=DEFAULT_SENSOR_SHELL)
    parser.add_argument("--project-dir", type=Path, default=DEFAULT_PROJECT_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-id", action="append", default=None)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--run-solver", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--nearest-tolerance-m", type=float, default=1e-6)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.worker:
        if not args.worker_config or not args.worker_summary:
            raise SystemExit("--worker requires worker_config and worker_summary")
        return worker_run(Path(args.worker_config), Path(args.worker_summary))
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
