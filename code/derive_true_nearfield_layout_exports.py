from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_priority_layout_queue.csv"
DEFAULT_SUBSETS = ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_priority_sensor_subsets.csv"
DEFAULT_SUMMARY = ROOT / "data" / "cst_true_nearfield_workpack" / "derived_layout_exports_summary.json"

REQUIRED_NEARFIELD_COLUMNS = {
    "sample_id",
    "sensor_id",
    "frequency_hz",
    "polarization",
    "e_real",
    "e_imag",
}


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing input table: {path}")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def normalize_list(values: list[str] | None) -> set[str] | None:
    if not values:
        return None
    normalized = {str(value).strip() for value in values if str(value).strip()}
    return normalized or None


def normalize_nearfield(frame: pd.DataFrame, source: Path) -> pd.DataFrame:
    missing = sorted(REQUIRED_NEARFIELD_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"{source} missing required columns: {missing}")

    work = frame.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce")
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    work["polarization"] = work["polarization"].astype(str).str.strip()
    work["e_real"] = pd.to_numeric(work["e_real"], errors="coerce")
    work["e_imag"] = pd.to_numeric(work["e_imag"], errors="coerce")

    bad = work[["sensor_id", "frequency_hz", "e_real", "e_imag"]].isna().any(axis=1)
    if bool(bad.any()):
        raise ValueError(f"{source} has {int(bad.sum())} rows with invalid numeric fields")
    work["sensor_id"] = work["sensor_id"].astype(int)

    duplicate_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization"]
    duplicate_count = int(work.duplicated(duplicate_cols).sum())
    if duplicate_count:
        raise ValueError(f"{source} has {duplicate_count} duplicated sample/frequency/sensor/polarization rows")
    return work


def load_subset_sensors(subsets: pd.DataFrame) -> dict[str, list[int]]:
    required = {"candidate", "sensor_id", "selection_order"}
    missing = sorted(required - set(subsets.columns))
    if missing:
        raise ValueError(f"subset table missing required columns: {missing}")

    work = subsets.copy()
    work["candidate"] = work["candidate"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce")
    work["selection_order"] = pd.to_numeric(work["selection_order"], errors="coerce")
    if work[["sensor_id", "selection_order"]].isna().any(axis=1).any():
        raise ValueError("subset table has invalid sensor_id or selection_order values")
    work["sensor_id"] = work["sensor_id"].astype(int)

    sensors: dict[str, list[int]] = {}
    for candidate, group in work.sort_values(["candidate", "selection_order"]).groupby("candidate", sort=True):
        sensors[str(candidate)] = group["sensor_id"].astype(int).tolist()
    return sensors


def build_output_path(row: pd.Series, out_dir: Path | None) -> Path:
    preferred = ROOT / str(row["preferred_export_path"])
    if out_dir is None:
        return preferred
    return out_dir / preferred.name


def derive_rows(
    source_nearfield: pd.DataFrame,
    sample_id: str,
    candidate: str,
    sensor_ids: list[int],
) -> pd.DataFrame:
    sensor_rank = {sensor_id: order for order, sensor_id in enumerate(sensor_ids)}
    subset = source_nearfield[
        source_nearfield["sample_id"].eq(sample_id) & source_nearfield["sensor_id"].isin(sensor_rank)
    ].copy()
    if subset.empty:
        return subset
    subset["_sensor_order"] = subset["sensor_id"].map(sensor_rank)
    subset["_polarization_order"] = subset["polarization"].map({"Ex": 0, "Ey": 1, "Ez": 2, "ex": 0, "ey": 1, "ez": 2})
    subset["_polarization_order"] = subset["_polarization_order"].fillna(99).astype(int)
    subset["derived_layout_candidate"] = candidate
    subset["derived_from_full_grid"] = True
    order_cols = ["sample_id", "frequency_hz", "_sensor_order", "_polarization_order", "sensor_id", "polarization"]
    subset = subset.sort_values(order_cols).drop(columns=["_sensor_order", "_polarization_order"])
    return subset


def frame_summary(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {
            "row_count": 0,
            "sensor_count": 0,
            "frequency_count": 0,
            "frequencies_hz": [],
            "polarizations": [],
        }
    return {
        "row_count": int(len(frame)),
        "sensor_count": int(frame["sensor_id"].nunique()),
        "frequency_count": int(frame["frequency_hz"].nunique()),
        "frequencies_hz": [int(value) for value in sorted(frame["frequency_hz"].dropna().unique())],
        "polarizations": sorted(frame["polarization"].astype(str).unique().tolist()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Derive reduced true-nearfield layout exports from a full-grid CST monitor CSV."
    )
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE), help="Priority layout queue CSV.")
    parser.add_argument("--subsets", default=str(DEFAULT_SUBSETS), help="Priority sensor subsets CSV.")
    parser.add_argument(
        "--full-grid-nearfield",
        default=None,
        help="Optional full-grid near-field CSV used for every selected queue row.",
    )
    parser.add_argument(
        "--sample-id",
        action="append",
        default=None,
        help="Limit derivation to one sample_id. Can be supplied more than once.",
    )
    parser.add_argument(
        "--candidate",
        action="append",
        default=None,
        help="Limit derivation to one candidate layout. Can be supplied more than once.",
    )
    parser.add_argument("--include-full-grid", action="store_true", help="Also copy/filter full_grid_162 rows.")
    parser.add_argument("--out-dir", default=None, help="Override output directory while preserving queued filenames.")
    parser.add_argument("--summary-out", default=str(DEFAULT_SUMMARY), help="Summary JSON path.")
    parser.add_argument("--allow-missing", action="store_true", help="Record missing source files instead of failing.")
    parser.add_argument("--dry-run", action="store_true", help="Validate planned outputs without writing CSV files.")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    subset_path = Path(args.subsets)
    summary_path = Path(args.summary_out)
    out_dir = Path(args.out_dir) if args.out_dir else None
    full_grid_override = Path(args.full_grid_nearfield) if args.full_grid_nearfield else None
    sample_filter = normalize_list(args.sample_id)
    candidate_filter = normalize_list(args.candidate)

    queue = read_table(queue_path)
    subsets = read_table(subset_path)
    required_queue = {"sample_id", "candidate", "preferred_export_path", "full_grid_export_path", "expected_export_rows"}
    missing_queue = sorted(required_queue - set(queue.columns))
    if missing_queue:
        raise ValueError(f"queue table missing required columns: {missing_queue}")

    queue["sample_id"] = queue["sample_id"].astype(str).str.strip()
    queue["candidate"] = queue["candidate"].astype(str).str.strip()
    selected = queue.copy()
    if not args.include_full_grid:
        selected = selected[selected["candidate"].ne("full_grid_162")]
    if sample_filter is not None:
        selected = selected[selected["sample_id"].isin(sample_filter)]
    if candidate_filter is not None:
        selected = selected[selected["candidate"].isin(candidate_filter)]
    if selected.empty:
        raise ValueError("no queue rows selected for derivation")

    subset_sensors = load_subset_sensors(subsets)
    source_cache: dict[Path, pd.DataFrame] = {}
    records: list[dict[str, object]] = []

    for row in selected.sort_values(["queue_order"] if "queue_order" in selected.columns else ["sample_id", "candidate"]).itertuples(index=False):
        row_series = pd.Series(row._asdict())
        sample_id = str(row_series["sample_id"])
        candidate = str(row_series["candidate"])
        if candidate not in subset_sensors:
            raise ValueError(f"candidate {candidate} is missing from subset table")

        source_path = full_grid_override or (ROOT / str(row_series["full_grid_export_path"]))
        output_path = build_output_path(row_series, out_dir)
        record: dict[str, object] = {
            "sample_id": sample_id,
            "candidate": candidate,
            "source_nearfield": rel(source_path),
            "output_path": rel(output_path),
            "expected_export_rows": int(row_series["expected_export_rows"]),
            "dry_run": bool(args.dry_run),
        }

        if not source_path.exists():
            record.update({"status": "missing_source", **frame_summary(pd.DataFrame())})
            records.append(record)
            if not args.allow_missing:
                raise FileNotFoundError(f"missing source full-grid export: {source_path}")
            continue

        if source_path not in source_cache:
            source_cache[source_path] = normalize_nearfield(read_table(source_path), source_path)
        derived = derive_rows(source_cache[source_path], sample_id, candidate, subset_sensors[candidate])
        record.update(frame_summary(derived))
        record["status"] = "ok" if int(record["row_count"]) == int(row_series["expected_export_rows"]) else "row_count_mismatch"
        records.append(record)

        if not args.dry_run and not derived.empty:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            derived.to_csv(output_path, index=False, encoding="utf-8-sig")

    summary = {
        "purpose": "Derive reduced true-nearfield layout exports from full-grid CST monitor rows.",
        "queue": rel(queue_path),
        "subsets": rel(subset_path),
        "full_grid_override": None if full_grid_override is None else rel(full_grid_override),
        "out_dir_override": None if out_dir is None else rel(out_dir),
        "selected_row_count": int(len(records)),
        "ok_count": int(sum(1 for record in records if record["status"] == "ok")),
        "missing_source_count": int(sum(1 for record in records if record["status"] == "missing_source")),
        "row_count_mismatch_count": int(sum(1 for record in records if record["status"] == "row_count_mismatch")),
        "records": records,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"derived layout export summary written to {summary_path}")
    print(f"selected rows: {summary['selected_row_count']}")
    print(f"ok rows: {summary['ok_count']}")
    print(f"missing sources: {summary['missing_source_count']}")
    print(f"row count mismatches: {summary['row_count_mismatch_count']}")


if __name__ == "__main__":
    main()
