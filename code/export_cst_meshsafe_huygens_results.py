from __future__ import annotations

import argparse
import csv
import json
import math
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CST_PYTHON = Path(
    r"D:\Program Files (x86)\CST Studio Suite 2025\Opera\code\bin\python.exe"
)
DEFAULT_PROJECT = Path(r"C:\csttmp\huy_s\h_short.cst")
DEFAULT_HFIELD_PROJECT = Path(r"C:\csttmp\huy_hs\h_short_hfield.cst")
DEFAULT_CASE_CSV = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "level1_required_meshsafe_huygens_cases.csv"
)
DEFAULT_PROBE_CSV = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "level1_local_huygens_probe_points.csv"
)
DEFAULT_CONTRACT_CSV = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "local_huygens_export_contract.csv"
)
DEFAULT_HFIELD_CONTRACT_CSV = (
    ROOT
    / "data"
    / "cst_meshsafe_huygens_workpack"
    / "local_huygens_hfield_export_contract.csv"
)
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_result_export"
DEFAULT_HFIELD_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_hfield_result_export"
FIELD_SPECS = {
    "e": {
        "label": "E-Field",
        "components": ("Ex", "Ey", "Ez"),
        "axis_to_component": {"X": "Ex", "Y": "Ey", "Z": "Ez"},
        "real_column": "e_real",
        "imag_column": "e_imag",
        "target_suffix": "_local_efield.csv",
        "derived_suffix": "_local_hfield.csv",
        "contract_csv": DEFAULT_CONTRACT_CSV,
        "out_dir": DEFAULT_OUT_DIR,
        "project": DEFAULT_PROJECT,
        "extraction_method": "CST ResultTree 1D complex local Cartesian E-field probe",
    },
    "h": {
        "label": "H-Field",
        "components": ("Hx", "Hy", "Hz"),
        "axis_to_component": {"X": "Hx", "Y": "Hy", "Z": "Hz"},
        "real_column": "h_real",
        "imag_column": "h_imag",
        "target_suffix": "_local_hfield.csv",
        "derived_suffix": "_local_hfield.csv",
        "contract_csv": DEFAULT_HFIELD_CONTRACT_CSV,
        "out_dir": DEFAULT_HFIELD_OUT_DIR,
        "project": DEFAULT_HFIELD_PROJECT,
        "extraction_method": "CST ResultTree 1D complex local Cartesian H-field probe",
    },
}
PRIMARY_ARTIFACT_SUFFIXES = {".m3d", ".ffm", ".fme"}
DIAGNOSTIC_SUFFIXES = {".json", ".txt", ".log"}
RESULT_TREE_ROOTS = ("1D Results", "2D/3D Results", "Tables", "Farfields")
PROBE_ITEM_PATTERN = re.compile(
    r"(?P<field>[EH])-Field\s+\((?P<coords>[-+0-9.eE,\s]+)\)\((?P<axis>Abs|X|Y|Z)\)\s+\[(?P<run>\d+)\]"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path_text: str | Path) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return ROOT / path


def rel(path_text: str | Path) -> str:
    path = resolve_path(path_text)
    try:
        return str(path.resolve().relative_to(ROOT)).replace("/", "\\")
    except Exception:
        return str(path)


def field_spec(field_kind: str) -> dict[str, Any]:
    key = str(field_kind).strip().lower()
    if key not in FIELD_SPECS:
        raise ValueError(f"unsupported field_kind {field_kind!r}; expected one of {sorted(FIELD_SPECS)}")
    return FIELD_SPECS[key]


def default_contract_csv(field_kind: str) -> Path:
    return Path(field_spec(field_kind)["contract_csv"])


def default_out_dir(field_kind: str) -> Path:
    return Path(field_spec(field_kind)["out_dir"])


def default_project(field_kind: str) -> Path:
    return Path(field_spec(field_kind)["project"])


def target_export_for_case(case: dict[str, str], field_kind: str, target_export: Path | None = None) -> Path:
    if target_export is not None:
        return resolve_path(target_export)
    base = resolve_path(case["nearfield_export"])
    if field_kind == "e":
        return base
    text = str(base)
    source_suffix = str(FIELD_SPECS["e"]["target_suffix"])
    target_suffix = str(field_spec(field_kind)["target_suffix"])
    if text.endswith(source_suffix):
        return Path(text[: -len(source_suffix)] + target_suffix)
    return base.with_name(base.stem + target_suffix)


def selected_project(args: argparse.Namespace) -> Path:
    value = getattr(args, "project", None)
    if value is None:
        return default_project(args.field_kind)
    return resolve_path(value)


def selected_contract_csv(args: argparse.Namespace) -> Path:
    value = getattr(args, "contract_csv", None)
    if value is None:
        return default_contract_csv(args.field_kind)
    return resolve_path(value)


def selected_out_dir(args: argparse.Namespace) -> Path:
    value = getattr(args, "out_dir", None)
    if value is None:
        return default_out_dir(args.field_kind)
    return resolve_path(value)


def selected_worker_summary(args: argparse.Namespace) -> Path:
    value = getattr(args, "worker_summary", None)
    if value is not None:
        return resolve_path(value)
    return selected_out_dir(args) / "meshsafe_huygens_tree_inspection.json"


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


def first_bytes(path: Path, count: int = 96) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(count)
    except OSError:
        return b""


def ascii_preview(data: bytes) -> str:
    return "".join(chr(item) if 32 <= item < 127 else "." for item in data)


def artifact_role(path: Path) -> str:
    suffix = path.suffix.lower()
    head = first_bytes(path, 64)
    if suffix == ".m3d":
        return "nearfield_monitor_binary"
    if suffix in {".ffm", ".fme"}:
        if head.startswith(b"**FarfieldMonitor**"):
            return "farfield_monitor_binary"
        return "farfield_binary"
    if suffix == ".json":
        return "solver_metadata_json"
    if suffix in {".txt", ".log"}:
        return "solver_log_text"
    return "diagnostic_file"


def inventory_artifacts(result_dir: Path) -> list[dict[str, Any]]:
    if not result_dir.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(result_dir.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix not in PRIMARY_ARTIFACT_SUFFIXES and suffix not in DIAGNOSTIC_SUFFIXES:
            continue
        head = first_bytes(path, 96)
        rows.append(
            {
                "path": rel(path),
                "name": path.name,
                "suffix": suffix,
                "role": artifact_role(path),
                "size_bytes": path.stat().st_size,
                "header_hex": head[:32].hex(" "),
                "header_ascii": ascii_preview(head),
            }
        )
    return rows


def summarize_artifacts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    suffix_counts: dict[str, int] = {}
    role_counts: dict[str, int] = {}
    total_size = 0
    for row in rows:
        suffix = str(row["suffix"])
        role = str(row["role"])
        suffix_counts[suffix] = suffix_counts.get(suffix, 0) + 1
        role_counts[role] = role_counts.get(role, 0) + 1
        total_size += as_int(row["size_bytes"])
    return {
        "artifact_count": len(rows),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "role_counts": dict(sorted(role_counts.items())),
        "total_size_bytes": total_size,
        "has_nearfield_binary": any(row["role"] == "nearfield_monitor_binary" for row in rows),
        "has_farfield_binary": any(str(row["role"]).startswith("farfield") for row in rows),
    }


def select_case(case_rows: list[dict[str, str]], sample_id: str) -> dict[str, str]:
    for row in case_rows:
        if str(row.get("sample_id", "")).strip() == sample_id:
            return row
    available = ", ".join(row.get("sample_id", "") for row in case_rows)
    raise ValueError(f"sample_id {sample_id!r} not found in case CSV. Available: {available}")


def contract_columns(contract_csv: Path) -> list[str]:
    return [row["column_name"] for row in read_csv_rows(contract_csv)]


def build_task(
    project: Path,
    result_dir: Path,
    case: dict[str, str],
    probe_csv: Path,
    contract_csv: Path,
    field_kind: str,
    target_export_override: Path | None = None,
) -> dict[str, Any]:
    spec = field_spec(field_kind)
    sample_id = case["sample_id"]
    target_export = target_export_for_case(case, field_kind, target_export_override)
    probe_rows = read_csv_rows(probe_csv)
    expected_rows = len(probe_rows) * len(spec["components"])
    target_rows = 0
    target_columns: list[str] = []
    if target_export.exists():
        with target_export.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            target_columns = list(reader.fieldnames or [])
            target_rows = sum(1 for _row in reader)
    required_columns = contract_columns(contract_csv)
    missing_columns = [column for column in required_columns if column not in target_columns]
    status = "target_contract_complete"
    blockers: list[str] = []
    if not project.exists():
        status = "blocked"
        blockers.append("missing CST project")
    elif not result_dir.exists():
        status = "blocked"
        blockers.append("missing CST result directory")
    elif not target_export.exists():
        status = "needs_local_result_export"
        blockers.append("target local Huygens CSV does not exist")
    elif target_rows != expected_rows:
        status = "target_contract_incomplete"
        blockers.append(f"target row count {target_rows} != expected {expected_rows}")
    elif missing_columns:
        status = "target_contract_incomplete"
        blockers.append("missing contract columns: " + ";".join(missing_columns))

    return {
        "sample_id": sample_id,
        "field_kind": field_kind,
        "field_label": spec["label"],
        "frequency_hz": as_int(case.get("frequency_hz")),
        "project_path": rel(project),
        "project_exists": project.exists(),
        "project_size_bytes": project.stat().st_size if project.exists() else 0,
        "result_dir": rel(result_dir),
        "result_dir_exists": result_dir.exists(),
        "probe_csv": rel(probe_csv),
        "probe_count": len(probe_rows),
        "expected_contract_rows": expected_rows,
        "target_export_path": rel(target_export),
        "target_export_exists": target_export.exists(),
        "target_rows": target_rows,
        "target_has_required_columns": not missing_columns and bool(target_columns),
        "missing_contract_columns": ";".join(missing_columns),
        "status": status,
        "blockers": ";".join(blockers),
    }


def has_tree_root(item: str, root: str) -> bool:
    lowered = item.strip().lower()
    root = root.lower()
    return lowered == root or lowered.startswith(f"{root}\\") or lowered.startswith(f"{root}/")


def is_result_tree_item(item: str) -> bool:
    return any(has_tree_root(item, root) for root in RESULT_TREE_ROOTS)


def likely_local_huygens_items(items: list[str], monitor_name: str, field_kind: str = "e") -> list[str]:
    spec = field_spec(field_kind)
    tokens = [
        monitor_name.lower(),
        "local_huygens",
        "huygens",
        "nearfield",
        "near field",
        "probe",
        str(spec["label"]).lower(),
    ]
    if field_kind == "e":
        tokens.extend(["efield", "e-field", "electric"])
    else:
        tokens.extend(["hfield", "h-field", "magnetic"])
    candidates: list[str] = []
    for item in items:
        lowered = item.lower()
        if any(token and token in lowered for token in tokens):
            candidates.append(item)
    return candidates


def parse_probe_result_item(item: str, field_kind: str = "e") -> dict[str, Any] | None:
    spec = field_spec(field_kind)
    match = PROBE_ITEM_PATTERN.search(item)
    if not match:
        return None
    if match.group("field").lower() != field_kind:
        return None
    axis = match.group("axis")
    axis_to_component = spec["axis_to_component"]
    if axis not in axis_to_component:
        return None
    coords = [as_float(value) for value in match.group("coords").replace(",", " ").split()]
    if len(coords) != 3:
        return None
    return {
        "item": item,
        "axis": axis,
        "component": axis_to_component[axis],
        "field_kind": field_kind,
        "field_label": spec["label"],
        "x_m": coords[0],
        "y_m": coords[1],
        "z_m": coords[2],
        "run_index": as_int(match.group("run")),
    }


def distance_m(a: dict[str, Any], b: dict[str, Any]) -> float:
    return math.sqrt(
        (as_float(a.get("x_m")) - as_float(b.get("x_m"))) ** 2
        + (as_float(a.get("y_m")) - as_float(b.get("y_m"))) ** 2
        + (as_float(a.get("z_m")) - as_float(b.get("z_m"))) ** 2
    )


def choose_probe_item(
    probe: dict[str, str],
    component: str,
    parsed_items: list[dict[str, Any]],
    tolerance_m: float,
) -> dict[str, Any] | None:
    candidates = [item for item in parsed_items if item["component"] == component]
    best_item: dict[str, Any] | None = None
    best_distance = float("inf")
    for item in candidates:
        dist = distance_m(probe, item)
        if dist < best_distance:
            best_distance = dist
            best_item = item
    if best_item is None or best_distance > tolerance_m:
        return None
    out = dict(best_item)
    out["distance_m"] = best_distance
    return out


def frequency_index(result_obj: Any, target_frequency_ghz: float) -> dict[str, Any]:
    n_points = as_int(result_obj.GetN())
    if n_points <= 0:
        return {
            "ok": False,
            "error": "empty CST probe curve",
            "n_points": n_points,
        }
    best_index = 0
    best_frequency = as_float(result_obj.GetX(0))
    best_error = abs(best_frequency - target_frequency_ghz)
    for index in range(1, n_points):
        current_frequency = as_float(result_obj.GetX(index))
        current_error = abs(current_frequency - target_frequency_ghz)
        if current_error < best_error:
            best_index = index
            best_frequency = current_frequency
            best_error = current_error
    return {
        "ok": True,
        "index": best_index,
        "n_points": n_points,
        "target_frequency_ghz": target_frequency_ghz,
        "selected_frequency_ghz": best_frequency,
        "frequency_error_ghz": best_error,
        "title": safe_call(result_obj, "GetTitle").get("value", ""),
        "x_label_unit": safe_call(result_obj, "GetXLabelAndUnit").get("value", ""),
        "y_label_unit": safe_call(result_obj, "GetYLabelAndUnit").get("value", ""),
    }


def contract_rows_from_values(
    case: dict[str, str],
    project: Path,
    probe_rows: list[dict[str, str]],
    values: dict[tuple[int, str], dict[str, Any]],
    field_kind: str,
) -> list[dict[str, Any]]:
    spec = field_spec(field_kind)
    real_column = str(spec["real_column"])
    imag_column = str(spec["imag_column"])
    rows: list[dict[str, Any]] = []
    for probe in probe_rows:
        sensor_id = as_int(probe.get("sensor_id"))
        for component in spec["components"]:
            value = values[(sensor_id, component)]
            rows.append(
                {
                    "sample_id": case["sample_id"],
                    "frequency_hz": as_int(case["frequency_hz"]),
                    "sensor_id": sensor_id,
                    "node_id": as_int(probe.get("node_id")),
                    "prior_id": probe.get("prior_id", ""),
                    "x_m": probe.get("x_m", ""),
                    "y_m": probe.get("y_m", ""),
                    "z_m": probe.get("z_m", ""),
                    "normal_x": probe.get("normal_x", ""),
                    "normal_y": probe.get("normal_y", ""),
                    "normal_z": probe.get("normal_z", ""),
                    "tangent1_x": probe.get("tangent1_x", ""),
                    "tangent1_y": probe.get("tangent1_y", ""),
                    "tangent1_z": probe.get("tangent1_z", ""),
                    "tangent2_x": probe.get("tangent2_x", ""),
                    "tangent2_y": probe.get("tangent2_y", ""),
                    "tangent2_z": probe.get("tangent2_z", ""),
                    "weight_m2": probe.get("weight_m2", ""),
                    "polarization": component,
                    real_column: f"{as_float(value.get(real_column)):.12e}",
                    imag_column: f"{as_float(value.get(imag_column)):.12e}",
                    "cst_project": rel(project),
                    "cst_probe_item": value.get("cst_probe_item", ""),
                    "extraction_method": spec["extraction_method"],
                }
            )
    return rows


def tree_summary(items: list[str], monitor_name: str, field_kind: str = "e") -> dict[str, Any]:
    result_items = [item for item in items if is_result_tree_item(item)]
    candidates = likely_local_huygens_items(items, monitor_name, field_kind)
    exportable = [item for item in candidates if is_result_tree_item(item)]
    parsed_candidates = [parsed for item in exportable if (parsed := parse_probe_result_item(item, field_kind))]
    definition = [
        item
        for item in candidates
        if has_tree_root(item, "field monitors") or has_tree_root(item, "probes")
    ]
    root_counts: dict[str, int] = {}
    for item in items:
        root = item.split("\\", 1)[0]
        root_counts[root] = root_counts.get(root, 0) + 1
    return {
        "tree_item_count": len(items),
        "field_kind": field_kind,
        "field_label": field_spec(field_kind)["label"],
        "result_tree_item_count": len(result_items),
        "root_counts": dict(sorted(root_counts.items())),
        "candidate_count": len(candidates),
        "definition_candidate_count": len(definition),
        "exportable_candidate_count": len(exportable),
        "parsed_probe_result_count": len(parsed_candidates),
        "candidate_items": candidates[:80],
        "definition_candidate_items": definition[:80],
        "exportable_candidate_items": exportable[:80],
        "parsed_probe_result_items": [item["item"] for item in parsed_candidates[:80]],
    }


def inspect_project_worker(args: argparse.Namespace) -> int:
    import cst.interface as ci  # type: ignore[import-not-found]

    project = selected_project(args)
    case = select_case(read_csv_rows(resolve_path(args.case_csv)), args.sample_id)
    probe_rows = read_csv_rows(resolve_path(args.probe_csv))
    contract_csv = selected_contract_csv(args)
    monitor_name = str(case.get("nearfield_monitor", "")).strip()
    target_export = target_export_for_case(case, args.field_kind, args.target_export)
    target_frequency_ghz = as_float(case.get("frequency_hz")) / 1.0e9
    summary_path = selected_worker_summary(args)
    item_map_path = summary_path.with_name("meshsafe_huygens_probe_item_map.csv")
    summary: dict[str, Any] = {
        "created_at": now_iso(),
        "status": "started",
        "field_kind": args.field_kind,
        "field_label": field_spec(args.field_kind)["label"],
        "project": rel(project),
        "project_exists": project.exists(),
        "monitor_name": monitor_name,
        "attempt_export": bool(args.worker_attempt_export),
    }
    write_json(summary_path, summary)

    de = ci.DesignEnvironment()
    prj = de.open_project(str(project))
    try:
        model = prj.model3d
        tree_result = safe_call(model, "get_tree_items")
        items = tree_result.get("value", []) if tree_result.get("ok") else []
        items = [str(item) for item in items] if isinstance(items, list) else []
        summary.update(
            {
                "completed_at": now_iso(),
                "status": "tree_inspected",
                "tree_result": {
                    "ok": tree_result.get("ok"),
                    "error": tree_result.get("error", ""),
                    "value_count": len(items),
                },
                "tree": tree_summary(items, monitor_name, args.field_kind),
            }
        )
        if args.worker_attempt_export:
            export_summary = export_probe_results_from_tree(
                model=model,
                case=case,
                project=project,
                contract_csv=contract_csv,
                probe_rows=probe_rows,
                items=items,
                target_export=target_export,
                item_map_path=item_map_path,
                target_frequency_ghz=target_frequency_ghz,
                nearest_tolerance_m=args.nearest_tolerance_m,
                frequency_tolerance_ghz=args.frequency_tolerance_ghz,
                result_id=args.result_id,
                overwrite=args.overwrite,
                field_kind=args.field_kind,
            )
            summary["export"] = export_summary
            summary["status"] = export_summary.get("status", "export_attempted")
        write_json(summary_path, summary)
        return 0 if summary["status"] in {"tree_inspected", "export_complete"} else 1
    finally:
        try:
            prj.close()
        except Exception:
            pass
        try:
            de.close()
        except Exception:
            pass


def export_probe_results_from_tree(
    model: Any,
    case: dict[str, str],
    project: Path,
    contract_csv: Path,
    probe_rows: list[dict[str, str]],
    items: list[str],
    target_export: Path,
    item_map_path: Path,
    target_frequency_ghz: float,
    nearest_tolerance_m: float,
    frequency_tolerance_ghz: float,
    result_id: str,
    overwrite: bool,
    field_kind: str = "e",
) -> dict[str, Any]:
    spec = field_spec(field_kind)
    components = tuple(spec["components"])
    real_column = str(spec["real_column"])
    imag_column = str(spec["imag_column"])
    if target_export.exists() and not overwrite:
        return {
            "status": "skipped_target_exists",
            "target_export": rel(target_export),
            "target_exists": True,
        }
    result_tree = model.ResultTree
    exportable_items = [
        item
        for item in likely_local_huygens_items(items, case.get("nearfield_monitor", ""), field_kind)
        if is_result_tree_item(item)
    ]
    parsed_items = [parsed for item in exportable_items if (parsed := parse_probe_result_item(item, field_kind))]
    item_map_rows: list[dict[str, Any]] = []
    values: dict[tuple[int, str], dict[str, Any]] = {}
    missing: list[str] = []
    selected_frequency: dict[str, Any] | None = None

    for probe in probe_rows:
        sensor_id = as_int(probe.get("sensor_id"))
        for component in components:
            map_row: dict[str, Any] = {
                "sensor_id": sensor_id,
                "node_id": as_int(probe.get("node_id")),
                "component": component,
                "probe_x_m": probe.get("x_m", ""),
                "probe_y_m": probe.get("y_m", ""),
                "probe_z_m": probe.get("z_m", ""),
                "status": "started",
            }
            item = choose_probe_item(probe, component, parsed_items, nearest_tolerance_m)
            if item is None:
                map_row["status"] = "missing_tree_item"
                missing.append(f"sensor {sensor_id} {component}: no matching result-tree probe item")
                item_map_rows.append(map_row)
                continue
            map_row.update(
                {
                    "cst_probe_item": item["item"],
                    "item_x_m": item["x_m"],
                    "item_y_m": item["y_m"],
                    "item_z_m": item["z_m"],
                    "distance_m": f"{as_float(item.get('distance_m')):.12e}",
                }
            )
            try:
                result_ids = list(result_tree.GetResultIDsFromTreeItem(item["item"]))
                chosen_result_id = result_id or (result_ids[0] if result_ids else "")
                result_obj = result_tree.GetResultFromTreeItem(item["item"], chosen_result_id)
                if selected_frequency is None:
                    selected_frequency = frequency_index(result_obj, target_frequency_ghz)
                if not selected_frequency.get("ok"):
                    raise RuntimeError(str(selected_frequency.get("error")))
                frequency_error = as_float(selected_frequency.get("frequency_error_ghz"))
                if frequency_error > frequency_tolerance_ghz:
                    raise RuntimeError(
                        f"nearest frequency error {frequency_error:g} GHz exceeds tolerance {frequency_tolerance_ghz:g}"
                    )
                index = as_int(selected_frequency.get("index"))
                real = as_float(result_obj.GetYRe(index))
                imag = as_float(result_obj.GetYIm(index))
                values[(sensor_id, component)] = {
                    real_column: real,
                    imag_column: imag,
                    "cst_probe_item": item["item"],
                    "result_id": chosen_result_id,
                }
                map_row.update(
                    {
                        "status": "value_read",
                        "result_ids": ";".join(str(value) for value in result_ids),
                        "result_id": chosen_result_id,
                        "frequency_index": index,
                        "n_points": selected_frequency.get("n_points", ""),
                        "target_frequency_ghz": selected_frequency.get("target_frequency_ghz", ""),
                        "selected_frequency_ghz": selected_frequency.get("selected_frequency_ghz", ""),
                        "frequency_error_ghz": selected_frequency.get("frequency_error_ghz", ""),
                        real_column: f"{real:.12e}",
                        imag_column: f"{imag:.12e}",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - CST result access can fail per item.
                map_row["status"] = "read_failed"
                map_row["error"] = repr(exc)
                missing.append(f"sensor {sensor_id} {component}: {exc!r}")
            item_map_rows.append(map_row)

    write_csv_rows(
        item_map_path,
        item_map_rows,
        [
            "sensor_id",
            "node_id",
            "component",
            "probe_x_m",
            "probe_y_m",
            "probe_z_m",
            "cst_probe_item",
            "item_x_m",
            "item_y_m",
            "item_z_m",
            "distance_m",
            "status",
            "result_ids",
            "result_id",
            "frequency_index",
            "n_points",
            "target_frequency_ghz",
            "selected_frequency_ghz",
            "frequency_error_ghz",
            real_column,
            imag_column,
            "error",
        ],
    )

    expected_values = len(probe_rows) * len(components)
    if len(values) != expected_values:
        return {
            "status": "export_incomplete",
            "field_kind": field_kind,
            "field_label": spec["label"],
            "target_export": rel(target_export),
            "parsed_probe_result_items": len(parsed_items),
            "expected_values": expected_values,
            "values_read": len(values),
            "missing_count": len(missing),
            "missing_examples": missing[:20],
            "item_map": rel(item_map_path),
            "frequency": selected_frequency or {},
        }

    rows = contract_rows_from_values(case, project, probe_rows, values, field_kind)
    write_csv_rows(target_export, rows, contract_columns(contract_csv))
    return {
        "status": "export_complete",
        "field_kind": field_kind,
        "field_label": spec["label"],
        "target_export": rel(target_export),
        "target_rows": len(rows),
        "parsed_probe_result_items": len(parsed_items),
        "expected_values": expected_values,
        "values_read": len(values),
        "item_map": rel(item_map_path),
        "frequency": selected_frequency or {},
    }

def build_readme(summary: dict[str, Any]) -> str:
    task = summary.get("task", {})
    artifacts = summary.get("artifact_summary", {})
    tree = summary.get("tree_inspection", {}).get("tree", {})
    field_label = summary.get("field_label", "E-Field")
    field_kind = summary.get("field_kind", "e")
    lines = [
        "# CST Mesh-Safe Huygens Result Export",
        "",
        f"Purpose: audit the local Huygens CST result package and decide whether `{field_label}` probe curves can be converted into the local CSV contract.",
        "",
        "## Current Status",
        "",
        f"- Controller status: `{summary.get('status')}`",
        f"- Sample: `{task.get('sample_id', '')}`",
        f"- Field kind: `{field_kind}` / `{field_label}`",
        f"- Target CSV: `{task.get('target_export_path', '')}`",
        f"- Target CSV exists: `{task.get('target_export_exists', False)}`",
        f"- Expected contract rows: `{task.get('expected_contract_rows', 0)}`",
        f"- Artifact count: `{artifacts.get('artifact_count', 0)}`",
        f"- Nearfield binary present: `{artifacts.get('has_nearfield_binary', False)}`",
        f"- Farfield binary present: `{artifacts.get('has_farfield_binary', False)}`",
        f"- Exportable local result-tree candidates: `{tree.get('exportable_candidate_count', 0)}`",
        "",
        "## Interpretation",
        "",
        "A `.m3d` local nearfield artifact proves CST kept a binary field result, but it is not the same thing as a parsed CSV. The algorithm pipeline should only consume `data/cst_exports/level1_meshsafe_huygens/*_local_efield.csv` or `*_local_hfield.csv` after this controller reports a complete target contract.",
        "",
        f"If only binary artifacts are present, the next step is to open the short-path project in CST and expose solved local `{field_label}` table/result items, or add a CST-API path that reads the binary result through an official result accessor.",
        "",
        "When `--attempt-export` is used, this controller reads 1D probe curves through `ResultTree.GetResultFromTreeItem(...).GetYRe/GetYIm` and writes the local Huygens CSV only after all Cartesian component probe values are available.",
        "",
        "## Files",
        "",
        "| File | Purpose |",
        "|---|---|",
        "| `meshsafe_huygens_export_summary.json` | Machine-readable controller summary. |",
        "| `meshsafe_huygens_artifact_inventory.csv` | Binary/log/metadata artifact list from the CST result directory. |",
        "| `meshsafe_huygens_export_task_plan.csv` | Contract row target, blockers, and current completion state. |",
        "| `meshsafe_huygens_tree_inspection.json` | CST result-tree snapshot when `--inspect-tree` is used. |",
        "| `cst_meshsafe_huygens_export_stdout.log` | CST worker stdout/stderr. |",
        "",
    ]
    return "\n".join(lines)


def copy_inputs(out_dir: Path, paths: list[Path]) -> None:
    input_dir = out_dir / "input_snapshots"
    input_dir.mkdir(parents=True, exist_ok=True)
    for source in paths:
        if source.exists():
            shutil.copy2(source, input_dir / source.name)


def controller_run(args: argparse.Namespace) -> int:
    project = selected_project(args)
    result_dir = project.with_suffix("")
    out_dir = selected_out_dir(args)
    case_csv = resolve_path(args.case_csv)
    probe_csv = resolve_path(args.probe_csv)
    contract_csv = selected_contract_csv(args)
    spec = field_spec(args.field_kind)
    out_dir.mkdir(parents=True, exist_ok=True)
    copy_inputs(out_dir, [case_csv, probe_csv, contract_csv])

    case = select_case(read_csv_rows(case_csv), args.sample_id)
    task = build_task(project, result_dir, case, probe_csv, contract_csv, args.field_kind, args.target_export)
    artifact_rows = inventory_artifacts(result_dir)
    artifact_summary = summarize_artifacts(artifact_rows)
    tree_summary_data: dict[str, Any] = {}
    stdout_log = out_dir / "cst_meshsafe_huygens_export_stdout.log"
    worker_summary = selected_worker_summary(args)

    if args.inspect_tree or args.attempt_export:
        if not args.cst_python.exists():
            tree_summary_data = {
                "status": "skipped",
                "error": f"CST Python not found: {args.cst_python}",
            }
        elif not project.exists():
            tree_summary_data = {"status": "skipped", "error": "project does not exist"}
        else:
            command = [
                str(args.cst_python),
                str(Path(__file__).resolve()),
                "--worker-inspect-tree",
                "--project",
                str(project),
                "--case-csv",
                str(case_csv),
                "--sample-id",
                args.sample_id,
                "--field-kind",
                args.field_kind,
                "--worker-summary",
                str(worker_summary),
                "--probe-csv",
                str(probe_csv),
                "--contract-csv",
                str(contract_csv),
                "--nearest-tolerance-m",
                str(args.nearest_tolerance_m),
                "--frequency-tolerance-ghz",
                str(args.frequency_tolerance_ghz),
            ]
            if args.attempt_export:
                command.append("--worker-attempt-export")
            if args.overwrite:
                command.append("--overwrite")
            if args.result_id:
                command.extend(["--result-id", args.result_id])
            if args.target_export:
                command.extend(["--target-export", str(resolve_path(args.target_export))])
            completed = subprocess.run(
                command,
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=args.inspect_timeout_seconds,
            )
            stdout_log.write_text(completed.stdout, encoding="utf-8")
            if worker_summary.exists():
                tree_summary_data = json.loads(worker_summary.read_text(encoding="utf-8"))
            else:
                tree_summary_data = {
                    "status": "worker_failed",
                    "returncode": completed.returncode,
                    "stdout_tail": completed.stdout[-2000:],
                }
            if args.attempt_export:
                task = build_task(project, result_dir, case, probe_csv, contract_csv, args.field_kind, args.target_export)

    if not args.inspect_tree and not args.attempt_export:
        write_json(worker_summary, {"status": "not_requested"})
        stdout_log.write_text("", encoding="utf-8")

    status = task["status"]
    blockers = [item for item in str(task.get("blockers", "")).split(";") if item]
    if status == "needs_local_result_export" and artifact_summary["has_nearfield_binary"]:
        status = "binary_result_present_needs_export_adapter"
        blockers.append("nearfield .m3d is binary and not yet converted to CSV contract")
    if args.inspect_tree and tree_summary_data.get("tree", {}).get("parsed_probe_result_count", 0):
        blockers.append(f"exportable CST {spec['label']} probe curves require ASCII/table export attempt")
    export_status = tree_summary_data.get("export", {}).get("status", "")
    if args.attempt_export and export_status and export_status != "export_complete":
        status = "result_tree_export_incomplete"
        blockers.append(f"CST ResultTree export status: {export_status}")
    if status == "target_contract_complete":
        blockers = []

    summary = {
        "created_at": now_iso(),
        "status": status,
        "sample_id": args.sample_id,
        "field_kind": args.field_kind,
        "field_label": spec["label"],
        "project": rel(project),
        "result_dir": rel(result_dir),
        "contract_csv": rel(contract_csv),
        "task": task,
        "artifact_summary": artifact_summary,
        "tree_inspection": tree_summary_data,
        "blockers": blockers,
        "next_recommended_gate": (
            "run local Huygens CSV contract validation and Python extrapolation"
            if status == "target_contract_complete"
            else f"export or parse local Huygens {spec['label']} result into the CSV contract"
        ),
    }

    write_csv_rows(
        out_dir / "meshsafe_huygens_export_task_plan.csv",
        [task],
        [
            "sample_id",
            "field_kind",
            "field_label",
            "frequency_hz",
            "project_path",
            "project_exists",
            "project_size_bytes",
            "result_dir",
            "result_dir_exists",
            "probe_csv",
            "probe_count",
            "expected_contract_rows",
            "target_export_path",
            "target_export_exists",
            "target_rows",
            "target_has_required_columns",
            "missing_contract_columns",
            "status",
            "blockers",
        ],
    )
    write_csv_rows(
        out_dir / "meshsafe_huygens_artifact_inventory.csv",
        artifact_rows,
        ["path", "name", "suffix", "role", "size_bytes", "header_hex", "header_ascii"],
    )
    write_json(out_dir / "meshsafe_huygens_export_summary.json", summary)
    (out_dir / "README.md").write_text(build_readme(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "target_contract_complete" else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit/export mesh-safe local Huygens CST results.")
    parser.add_argument("--project", type=Path, default=None)
    parser.add_argument("--case-csv", type=Path, default=DEFAULT_CASE_CSV)
    parser.add_argument("--probe-csv", type=Path, default=DEFAULT_PROBE_CSV)
    parser.add_argument("--field-kind", choices=sorted(FIELD_SPECS), default="e")
    parser.add_argument("--contract-csv", type=Path, default=None)
    parser.add_argument("--sample-id", default="L1_short_dipole_z_1p2G")
    parser.add_argument("--target-export", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--cst-python", type=Path, default=DEFAULT_CST_PYTHON)
    parser.add_argument("--inspect-tree", action="store_true")
    parser.add_argument("--attempt-export", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--nearest-tolerance-m", type=float, default=1e-3)
    parser.add_argument("--frequency-tolerance-ghz", type=float, default=1e-6)
    parser.add_argument("--result-id", default="")
    parser.add_argument("--inspect-timeout-seconds", type=int, default=120)
    parser.add_argument("--worker-inspect-tree", action="store_true")
    parser.add_argument("--worker-attempt-export", action="store_true")
    parser.add_argument("--worker-summary", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.worker_inspect_tree:
        return inspect_project_worker(args)
    return controller_run(args)


if __name__ == "__main__":
    raise SystemExit(main())
