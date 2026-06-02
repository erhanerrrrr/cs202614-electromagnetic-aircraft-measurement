from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKPACK = ROOT / "data" / "cst_true_nearfield_workpack"
DEFAULT_QUEUE = WORKPACK / "true_nearfield_priority_layout_queue.csv"
DEFAULT_SUBSETS = WORKPACK / "true_nearfield_priority_sensor_subsets.csv"
DEFAULT_CONTRACT = WORKPACK / "true_nearfield_export_contract.csv"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_true_nearfield_dropzone_check"

NUMERIC_COLUMNS = {
    "frequency_hz",
    "sensor_id",
    "x_m",
    "y_m",
    "z_m",
    "theta_deg",
    "phi_deg",
    "radius_m",
    "e_real",
    "e_imag",
}
EXPECTED_POLARIZATIONS = {"ex", "ey", "ez"}


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    try:
        return str(full.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(full)


def normalize_list(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    cleaned = {str(value).strip() for value in values if str(value).strip()}
    return cleaned or None


def require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def contract_columns(contract: pd.DataFrame) -> list[str]:
    if contract.empty or "column_name" not in contract.columns:
        raise ValueError("contract table is missing column_name")
    return [str(value).strip() for value in contract["column_name"].tolist() if str(value).strip()]


def load_subset_sensors(subsets: pd.DataFrame) -> dict[str, set[int]]:
    require_columns(subsets, {"candidate", "sensor_id"}, "subset table")
    work = subsets.copy()
    work["candidate"] = work["candidate"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce")
    if bool(work["sensor_id"].isna().any()):
        bad = int(work["sensor_id"].isna().sum())
        raise ValueError(f"subset table has {bad} invalid sensor_id values")
    work["sensor_id"] = work["sensor_id"].astype(int)
    result: dict[str, set[int]] = {}
    for candidate, group in work.groupby("candidate", sort=True):
        result[str(candidate)] = set(group["sensor_id"].astype(int).tolist())
    return result


def select_queue(
    queue: pd.DataFrame,
    sample_filter: set[str] | None,
    candidate_filter: set[str] | None,
    required_only: bool,
    full_grid_only: bool,
) -> pd.DataFrame:
    require_columns(
        queue,
        {
            "queue_order",
            "sample_id",
            "case_priority",
            "frequency_hz",
            "candidate",
            "sensor_count",
            "expected_export_rows",
            "preferred_export_path",
        },
        "queue table",
    )
    selected = queue.copy()
    selected["sample_id"] = selected["sample_id"].astype(str).str.strip()
    selected["candidate"] = selected["candidate"].astype(str).str.strip()
    selected["case_priority"] = selected["case_priority"].astype(str).str.strip()
    if sample_filter is not None:
        selected = selected[selected["sample_id"].isin(sample_filter)]
    if candidate_filter is not None:
        selected = selected[selected["candidate"].isin(candidate_filter)]
    if required_only:
        selected = selected[selected["case_priority"].eq("required")]
    if full_grid_only:
        selected = selected[selected["candidate"].eq("full_grid_162")]
    if selected.empty:
        raise ValueError("no true-nearfield queue rows selected")
    return selected.sort_values("queue_order")


def numeric_error_count(frame: pd.DataFrame, columns: set[str]) -> dict[str, int]:
    errors: dict[str, int] = {}
    for column in sorted(columns & set(frame.columns)):
        converted = pd.to_numeric(frame[column], errors="coerce")
        bad = int(converted.isna().sum())
        if bad:
            errors[column] = bad
    return errors


def validate_table(
    frame: pd.DataFrame,
    expected_columns: list[str],
    sample_id: str,
    candidate: str,
    expected_frequency_hz: int,
    expected_sensor_count: int,
    expected_rows: int,
    expected_sensors: set[int] | None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    missing_columns = sorted(set(expected_columns) - set(frame.columns))
    if missing_columns:
        errors.append(f"missing columns: {missing_columns}")

    numeric_bad = numeric_error_count(frame, NUMERIC_COLUMNS)
    for column, count in numeric_bad.items():
        errors.append(f"{column} has {count} non-numeric or empty values")

    if errors:
        return {
            "status": "invalid_contract",
            "errors": errors,
            "warnings": warnings,
            "row_count": int(len(frame)),
            "sensor_count": "",
            "frequency_count": "",
            "polarizations": "",
        }

    work = frame.copy()
    for column in sorted(NUMERIC_COLUMNS & set(work.columns)):
        work[column] = pd.to_numeric(work[column], errors="coerce")
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["polarization_norm"] = work["polarization"].astype(str).str.strip().str.lower()
    work["sensor_id"] = work["sensor_id"].astype(int)
    work["frequency_hz"] = work["frequency_hz"].astype(int)

    row_count = int(len(work))
    sensor_set = set(work["sensor_id"].astype(int).tolist())
    frequency_set = set(work["frequency_hz"].astype(int).tolist())
    polarization_set = set(work["polarization_norm"].tolist())

    if row_count != expected_rows:
        errors.append(f"row_count {row_count} != expected_export_rows {expected_rows}")
    if work["sample_id"].nunique() != 1 or sample_id not in set(work["sample_id"]):
        found = sorted(work["sample_id"].unique().tolist())
        errors.append(f"sample_id mismatch, expected {sample_id}, found {found}")
    if frequency_set != {expected_frequency_hz}:
        errors.append(f"frequency_hz mismatch, expected {[expected_frequency_hz]}, found {sorted(frequency_set)}")
    if len(sensor_set) != expected_sensor_count:
        errors.append(f"sensor_count {len(sensor_set)} != expected {expected_sensor_count}")
    if expected_sensors is not None:
        missing_sensors = sorted(expected_sensors - sensor_set)
        extra_sensors = sorted(sensor_set - expected_sensors)
        if missing_sensors:
            errors.append(f"missing expected sensor_id values: {missing_sensors[:10]}")
        if extra_sensors:
            errors.append(f"unexpected sensor_id values: {extra_sensors[:10]}")
    if polarization_set != EXPECTED_POLARIZATIONS:
        errors.append(f"polarization set mismatch, expected {sorted(EXPECTED_POLARIZATIONS)}, found {sorted(polarization_set)}")

    duplicate_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization_norm"]
    duplicate_count = int(work.duplicated(duplicate_cols).sum())
    if duplicate_count:
        errors.append(f"{duplicate_count} duplicate sample/frequency/sensor/polarization rows")

    counts = work.groupby(["sample_id", "frequency_hz", "sensor_id"]).size()
    bad_component_counts = counts[counts != 3]
    if len(bad_component_counts):
        errors.append(f"{len(bad_component_counts)} sensor rows do not have exactly three components")

    if candidate != "full_grid_162" and row_count == expected_rows:
        warnings.append("reduced layout file is present; confirm it was derived from the full-grid monitor CSV or exported intentionally")

    status = "ready_for_gate" if not errors else "invalid_contract"
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "row_count": row_count,
        "sensor_count": int(len(sensor_set)),
        "frequency_count": int(len(frequency_set)),
        "polarizations": ";".join(sorted(polarization_set)),
    }


def check_queue_row(row: Any, expected_columns: list[str], subset_sensors: dict[str, set[int]]) -> dict[str, Any]:
    sample_id = str(row.sample_id)
    candidate = str(row.candidate)
    path = ROOT / str(row.preferred_export_path)
    base: dict[str, Any] = {
        "queue_order": int(row.queue_order),
        "sample_id": sample_id,
        "case_priority": str(row.case_priority),
        "candidate": candidate,
        "target_export_path": rel(path),
        "target_export_exists": path.exists(),
        "expected_frequency_hz": int(float(row.frequency_hz)),
        "expected_sensor_count": int(float(row.sensor_count)),
        "expected_export_rows": int(float(row.expected_export_rows)),
        "expected_status_after_success": "ready_for_gate",
    }
    if not path.exists():
        return {
            **base,
            "status": "missing_file",
            "row_count": "",
            "sensor_count": "",
            "frequency_count": "",
            "polarizations": "",
            "error_count": 1,
            "warning_count": 0,
            "errors": "file is missing",
            "warnings": "",
        }

    try:
        frame = read_csv(path)
        result = validate_table(
            frame=frame,
            expected_columns=expected_columns,
            sample_id=sample_id,
            candidate=candidate,
            expected_frequency_hz=int(float(row.frequency_hz)),
            expected_sensor_count=int(float(row.sensor_count)),
            expected_rows=int(float(row.expected_export_rows)),
            expected_sensors=subset_sensors.get(candidate),
        )
    except Exception as exc:  # noqa: BLE001 - report file-specific failure as data status.
        result = {
            "status": "read_error",
            "errors": [str(exc)],
            "warnings": [],
            "row_count": "",
            "sensor_count": "",
            "frequency_count": "",
            "polarizations": "",
        }

    return {
        **base,
        "status": result["status"],
        "row_count": result["row_count"],
        "sensor_count": result["sensor_count"],
        "frequency_count": result["frequency_count"],
        "polarizations": result["polarizations"],
        "error_count": len(result["errors"]),
        "warning_count": len(result["warnings"]),
        "errors": " | ".join(result["errors"]),
        "warnings": " | ".join(result["warnings"]),
    }


def write_readme(out_dir: Path, summary: dict[str, Any]) -> None:
    content = f"""# CST True Near-Field Dropzone Check

This folder is generated by:

```powershell
python code\\check_true_nearfield_dropzone.py
```

It checks the files expected by the true near-field monitor queue before the
post-export comparison gate is run.

## Current Summary

- Rows checked: {summary["checked_rows"]}
- Ready for gate: {summary["ready_for_gate_count"]}
- Missing files: {summary["missing_file_count"]}
- Invalid/read-error rows: {summary["invalid_or_read_error_count"]}
- Required full-grid ready: {summary["required_full_grid_ready_count"]}/{summary["required_full_grid_count"]}

## Files

| File | Purpose |
|---|---|
| `true_nearfield_dropzone_status.csv` | Per queued export file status, row count, sensor count, component set, and validation errors. |
| `true_nearfield_dropzone_summary.json` | Machine-readable aggregate summary. |

When the required full-grid rows are `ready_for_gate`, run:

```powershell
python code\\run_true_nearfield_gate.py --required-only
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def build_summary(status: pd.DataFrame) -> dict[str, Any]:
    status_counts = status["status"].value_counts().to_dict()
    required_full = status[
        status["case_priority"].astype(str).eq("required")
        & status["candidate"].astype(str).eq("full_grid_162")
    ]
    ready_required_full = required_full[required_full["status"].eq("ready_for_gate")]
    invalid = status[status["status"].isin(["invalid_contract", "read_error"])]
    return {
        "generated_by": "code/check_true_nearfield_dropzone.py",
        "checked_rows": int(status.shape[0]),
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "ready_for_gate_count": int(status["status"].eq("ready_for_gate").sum()),
        "missing_file_count": int(status["status"].eq("missing_file").sum()),
        "invalid_or_read_error_count": int(invalid.shape[0]),
        "required_full_grid_count": int(required_full.shape[0]),
        "required_full_grid_ready_count": int(ready_required_full.shape[0]),
        "next_command": (
            "python code\\run_true_nearfield_gate.py --required-only"
            if int(ready_required_full.shape[0]) == int(required_full.shape[0]) and int(required_full.shape[0]) > 0
            else "export the missing required full_grid_162 true-monitor CSV files"
        ),
        "output_files": {
            "status": "outputs\\cst_true_nearfield_dropzone_check\\true_nearfield_dropzone_status.csv",
            "summary": "outputs\\cst_true_nearfield_dropzone_check\\true_nearfield_dropzone_summary.json",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check CST true near-field monitor dropzone files.")
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--subsets", type=Path, default=DEFAULT_SUBSETS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--sample-id", action="append", default=None)
    parser.add_argument("--candidate", action="append", default=None)
    parser.add_argument("--required-only", action="store_true")
    parser.add_argument("--full-grid-only", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless every selected row is ready_for_gate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    queue = select_queue(
        read_csv(Path(args.queue)),
        sample_filter=normalize_list(args.sample_id),
        candidate_filter=normalize_list(args.candidate),
        required_only=bool(args.required_only),
        full_grid_only=bool(args.full_grid_only),
    )
    expected_columns = contract_columns(read_csv(Path(args.contract)))
    subset_sensors = load_subset_sensors(read_csv(Path(args.subsets)))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    status = pd.DataFrame([check_queue_row(row, expected_columns, subset_sensors) for row in queue.itertuples(index=False)])
    summary = build_summary(status)
    status.to_csv(out_dir / "true_nearfield_dropzone_status.csv", index=False, encoding="utf-8-sig")
    (out_dir / "true_nearfield_dropzone_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"CST true near-field dropzone check written to {rel(out_dir)}")
    print(f"status counts: {summary['status_counts']}")
    print(f"next command: {summary['next_command']}")
    if args.strict and summary["ready_for_gate_count"] != summary["checked_rows"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
