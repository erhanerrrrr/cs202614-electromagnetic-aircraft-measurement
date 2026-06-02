from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from compare_true_nearfield_exports import compare_tables, normalize_nearfield_table, write_readme
from derive_true_nearfield_layout_exports import derive_rows, load_subset_sensors, normalize_nearfield


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUEUE = ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_priority_layout_queue.csv"
DEFAULT_SUBSETS = ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_priority_sensor_subsets.csv"
DEFAULT_REPORT_DIR = ROOT / "data" / "cst_true_nearfield_workpack" / "gate_report"
DEFAULT_COMPARISON_ROOT = ROOT / "data" / "cst_true_nearfield_workpack" / "comparison"


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


def json_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    normalized = frame.where(pd.notna(frame), None)
    return json.loads(normalized.to_json(orient="records", force_ascii=False))


def select_queue_rows(
    queue: pd.DataFrame,
    sample_filter: set[str] | None,
    candidate_filter: set[str] | None,
    required_only: bool,
) -> pd.DataFrame:
    required = {
        "queue_order",
        "sample_id",
        "case_priority",
        "candidate",
        "expected_export_rows",
        "preferred_export_path",
        "full_grid_export_path",
        "farfieldplot_reference_export",
    }
    missing = sorted(required - set(queue.columns))
    if missing:
        raise ValueError(f"queue table missing required columns: {missing}")

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
    if selected.empty:
        raise ValueError("no true-monitor queue rows selected")
    return selected.sort_values("queue_order")


def candidate_output_path(preferred_path: Path, derive_out_dir: Path | None) -> Path:
    if derive_out_dir is None:
        return preferred_path
    return derive_out_dir / preferred_path.name


def comparison_dir(comparison_root: Path, sample_id: str, candidate: str) -> Path:
    return comparison_root / sample_id / candidate


def frame_counts(frame: pd.DataFrame | None) -> dict[str, object]:
    if frame is None or frame.empty:
        return {"row_count": 0, "sensor_count": 0, "frequency_count": 0}
    return {
        "row_count": int(len(frame)),
        "sensor_count": int(frame["sensor_id"].nunique()),
        "frequency_count": int(frame["frequency_hz"].nunique()),
    }


def write_comparison_outputs(
    out_dir: Path,
    candidate_path: Path,
    reference_path: Path,
    sample_id: str,
    candidate: str,
    result: pd.DataFrame,
    metrics: dict[str, object],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_dir / "nearfield_export_comparison_by_group.csv", index=False, encoding="utf-8-sig")
    summary = {
        "candidate_nearfield": rel(candidate_path),
        "reference_nearfield": rel(reference_path),
        "case_table": None,
        "output_dir": rel(out_dir),
        "sample_id": sample_id,
        "layout_candidate": candidate,
        "comparison_boundary": (
            "FarfieldPlot-derived samples are a reference baseline; true near-field monitor samples "
            "become authoritative once exported."
        ),
        **metrics,
    }
    (out_dir / "nearfield_export_comparison_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)


def classify_gate_status(
    source_status: str,
    row_count: int,
    expected_rows: int,
    metrics: dict[str, object] | None,
    corr_threshold: float,
    scaled_l2_threshold: float,
) -> str:
    if source_status.startswith("missing"):
        return "pending_source"
    if row_count != expected_rows:
        return "row_count_mismatch"
    if metrics is None:
        return "pending_comparison"
    corr = float(metrics["min_all_complex_correlation_abs"])
    scaled_l2 = float(metrics["max_all_scaled_relative_l2_error"])
    if corr >= corr_threshold and scaled_l2 <= scaled_l2_threshold:
        return "reference_match"
    return "needs_physical_rerun"


def write_gate_readme(report_dir: Path, summary: dict[str, object]) -> None:
    content = f"""# True Near-Field Gate Report

This folder is generated by:

```powershell
python code\\run_true_nearfield_gate.py
```

It summarizes the current CST true-monitor queue after export, optional
reduced-layout derivation, and comparison against the FarfieldPlot-derived
Level 1 reference.

## Current Status

- Queue rows checked: {summary["queue_row_count"]}
- Compared rows: {summary["compared_count"]}
- Pending source rows: {summary["pending_source_count"]}
- Reference-match rows: {summary["reference_match_count"]}
- Needs physical rerun rows: {summary["needs_physical_rerun_count"]}

## Files

| File | Purpose |
|---|---|
| `true_nearfield_gate_status.csv` | One row per queued layout with source, derivation, row-count, and comparison status. |
| `true_nearfield_gate_summary.json` | Machine-readable aggregate summary. |

This report is a workflow gate. It does not turn FarfieldPlot-derived samples
into final full-wave evidence; it records whether true CST monitor exports have
arrived and whether they agree with the current reference on the compared rows.
"""
    (report_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CST true near-field monitor post-export gate.")
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE), help="Priority layout queue CSV.")
    parser.add_argument("--subsets", default=str(DEFAULT_SUBSETS), help="Priority sensor subset CSV.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Output status report directory.")
    parser.add_argument("--comparison-root", default=str(DEFAULT_COMPARISON_ROOT), help="Per-layout comparison output root.")
    parser.add_argument("--derive-out-dir", default=None, help="Optional reduced-layout CSV output directory override.")
    parser.add_argument("--full-grid-override", default=None, help="Use this full-grid CSV for every selected queue row.")
    parser.add_argument("--sample-id", action="append", default=None, help="Limit to a sample_id. Can repeat.")
    parser.add_argument("--candidate", action="append", default=None, help="Limit to a layout candidate. Can repeat.")
    parser.add_argument("--required-only", action="store_true", help="Limit to required Level 1 cases.")
    parser.add_argument("--no-derive", action="store_true", help="Do not derive reduced layouts from a full-grid export.")
    parser.add_argument("--dry-run", action="store_true", help="Do not write derived CSVs or comparison folders.")
    parser.add_argument("--corr-threshold", type=float, default=0.98, help="Reference-match correlation threshold.")
    parser.add_argument("--scaled-l2-threshold", type=float, default=0.10, help="Reference-match scaled L2 threshold.")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    subset_path = Path(args.subsets)
    report_dir = Path(args.report_dir)
    comparison_root = Path(args.comparison_root)
    derive_out_dir = Path(args.derive_out_dir) if args.derive_out_dir else None
    full_grid_override = Path(args.full_grid_override) if args.full_grid_override else None
    sample_filter = normalize_list(args.sample_id)
    candidate_filter = normalize_list(args.candidate)

    queue = select_queue_rows(read_table(queue_path), sample_filter, candidate_filter, bool(args.required_only))
    subset_sensors = load_subset_sensors(read_table(subset_path))
    source_cache: dict[Path, pd.DataFrame] = {}
    reference_cache: dict[Path, pd.DataFrame] = {}
    rows: list[dict[str, object]] = []

    for row in queue.itertuples(index=False):
        item = pd.Series(row._asdict())
        sample_id = str(item["sample_id"])
        candidate = str(item["candidate"])
        expected_rows = int(item["expected_export_rows"])
        preferred_path = ROOT / str(item["preferred_export_path"])
        full_grid_path = full_grid_override or (ROOT / str(item["full_grid_export_path"]))
        reference_path = ROOT / str(item["farfieldplot_reference_export"])
        candidate_path = preferred_path
        candidate_frame: pd.DataFrame | None = None
        source_status = "missing_candidate_export"
        source_path = preferred_path

        if candidate == "full_grid_162":
            source_path = full_grid_path if full_grid_override is not None else preferred_path
            candidate_path = source_path
            if source_path.exists():
                candidate_frame = normalize_nearfield(read_table(source_path), source_path)
                source_status = "full_grid_export_available"
        elif preferred_path.exists():
            source_path = preferred_path
            candidate_path = preferred_path
            candidate_frame = normalize_nearfield(read_table(preferred_path), preferred_path)
            source_status = "reduced_export_available"
        elif not args.no_derive and full_grid_path.exists():
            if candidate not in subset_sensors:
                raise ValueError(f"candidate {candidate} missing from subset table")
            if full_grid_path not in source_cache:
                source_cache[full_grid_path] = normalize_nearfield(read_table(full_grid_path), full_grid_path)
            derived = derive_rows(source_cache[full_grid_path], sample_id, candidate, subset_sensors[candidate])
            candidate_frame = derived
            candidate_path = candidate_output_path(preferred_path, derive_out_dir)
            source_path = full_grid_path
            source_status = "derived_from_full_grid"
            if not args.dry_run and not derived.empty:
                candidate_path.parent.mkdir(parents=True, exist_ok=True)
                derived.to_csv(candidate_path, index=False, encoding="utf-8-sig")
        elif full_grid_path.exists():
            source_status = "missing_reduced_export_derivation_disabled"
            source_path = full_grid_path
        else:
            source_status = "missing_full_grid_export"
            source_path = full_grid_path

        counts = frame_counts(candidate_frame)
        metrics: dict[str, object] | None = None
        comparison_status = "not_run"
        comparison_output = comparison_dir(comparison_root, sample_id, candidate)
        if candidate_frame is not None and reference_path.exists():
            if reference_path not in reference_cache:
                reference_cache[reference_path] = normalize_nearfield_table(read_table(reference_path), "reference")
            reference = reference_cache[reference_path]
            normalized_candidate = normalize_nearfield_table(candidate_frame, "candidate")
            comparison_result, metrics = compare_tables(reference, normalized_candidate, {sample_id})
            comparison_status = "ok"
            if not args.dry_run:
                write_comparison_outputs(
                    comparison_output,
                    candidate_path,
                    reference_path,
                    sample_id,
                    candidate,
                    comparison_result,
                    metrics,
                )
        elif candidate_frame is not None:
            comparison_status = "missing_reference"

        gate_status = classify_gate_status(
            source_status,
            int(counts["row_count"]),
            expected_rows,
            metrics,
            float(args.corr_threshold),
            float(args.scaled_l2_threshold),
        )
        rows.append(
            {
                "queue_order": int(item["queue_order"]),
                "sample_id": sample_id,
                "case_priority": item["case_priority"],
                "candidate": candidate,
                "layout_role": item.get("layout_role", ""),
                "expected_export_rows": expected_rows,
                "source_status": source_status,
                "source_path": rel(source_path),
                "candidate_export_path": rel(candidate_path),
                "reference_export_path": rel(reference_path),
                "row_count": counts["row_count"],
                "sensor_count": counts["sensor_count"],
                "frequency_count": counts["frequency_count"],
                "comparison_status": comparison_status,
                "comparison_output": rel(comparison_output),
                "gate_status": gate_status,
                "min_all_complex_correlation_abs": "" if metrics is None else metrics["min_all_complex_correlation_abs"],
                "max_all_scaled_relative_l2_error": "" if metrics is None else metrics["max_all_scaled_relative_l2_error"],
                "max_all_relative_l2_error": "" if metrics is None else metrics["max_all_relative_l2_error"],
                "missing_candidate_rows": "" if metrics is None else metrics["missing_candidate_rows"],
                "missing_reference_rows": "" if metrics is None else metrics["missing_reference_rows"],
                "dry_run": bool(args.dry_run),
            }
        )

    status = pd.DataFrame(rows).sort_values("queue_order")
    summary = {
        "purpose": "CST true near-field monitor post-export gate.",
        "queue": rel(queue_path),
        "subsets": rel(subset_path),
        "report_dir": rel(report_dir),
        "comparison_root": rel(comparison_root),
        "dry_run": bool(args.dry_run),
        "queue_row_count": int(len(status)),
        "compared_count": int(status["comparison_status"].eq("ok").sum()),
        "pending_source_count": int(status["gate_status"].eq("pending_source").sum()),
        "reference_match_count": int(status["gate_status"].eq("reference_match").sum()),
        "needs_physical_rerun_count": int(status["gate_status"].eq("needs_physical_rerun").sum()),
        "row_count_mismatch_count": int(status["gate_status"].eq("row_count_mismatch").sum()),
        "corr_threshold": float(args.corr_threshold),
        "scaled_l2_threshold": float(args.scaled_l2_threshold),
        "status_counts": {str(key): int(value) for key, value in status["gate_status"].value_counts().to_dict().items()},
        "records": json_records(status),
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    status.to_csv(report_dir / "true_nearfield_gate_status.csv", index=False, encoding="utf-8-sig")
    (report_dir / "true_nearfield_gate_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_gate_readme(report_dir, summary)

    print(f"true near-field gate report written to {report_dir}")
    print(f"queue rows: {summary['queue_row_count']}")
    print(f"compared rows: {summary['compared_count']}")
    print(f"pending source rows: {summary['pending_source_count']}")
    print(f"reference-match rows: {summary['reference_match_count']}")


if __name__ == "__main__":
    main()
