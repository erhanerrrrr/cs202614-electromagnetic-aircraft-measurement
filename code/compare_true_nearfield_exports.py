from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRUE_NEARFIELD = ROOT / "data" / "cst_exports" / "level1_true_nearfield" / "all_true_nearfield.csv"
DEFAULT_REFERENCE_NEARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_nearfield.csv"
DEFAULT_CASE_TABLE = ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_monitor_cases.csv"
DEFAULT_OUT = ROOT / "data" / "cst_true_nearfield_workpack" / "comparison"


REQUIRED_COLUMNS = {
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


def normalize_nearfield_table(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"{table_name} missing required columns: {missing}")

    work = df.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce")
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    work["polarization"] = work["polarization"].astype(str).str.strip()
    work["polarization_norm"] = work["polarization"].str.lower()
    work["e_real"] = pd.to_numeric(work["e_real"], errors="coerce")
    work["e_imag"] = pd.to_numeric(work["e_imag"], errors="coerce")
    bad = work[["sensor_id", "frequency_hz", "e_real", "e_imag"]].isna().any(axis=1)
    if bool(bad.any()):
        raise ValueError(f"{table_name} has {int(bad.sum())} rows with non-numeric sensor/frequency/field values")

    work["sensor_id"] = work["sensor_id"].astype(int)
    work["e_complex"] = work["e_real"].to_numpy(dtype=float) + 1j * work["e_imag"].to_numpy(dtype=float)
    duplicate_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization_norm"]
    duplicate_count = int(work.duplicated(duplicate_cols).sum())
    if duplicate_count:
        raise ValueError(f"{table_name} has {duplicate_count} duplicated sample/frequency/sensor/polarization rows")

    keep_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization_norm", "polarization", "e_complex"]
    return work[keep_cols].sort_values(["sample_id", "frequency_hz", "sensor_id", "polarization_norm"])


def load_case_filter(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    cases = read_table(path)
    if "sample_id" not in cases.columns:
        raise ValueError(f"case table missing sample_id column: {path}")
    return set(cases["sample_id"].astype(str).str.strip())


def vector_metrics(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    ref_norm = float(np.linalg.norm(reference))
    cand_norm = float(np.linalg.norm(candidate))
    denom = max(ref_norm * cand_norm, 1e-30)
    inner = np.vdot(reference, candidate)
    corr = abs(inner) / denom
    rel_l2 = float(np.linalg.norm(candidate - reference) / max(ref_norm, 1e-30))
    amplitude_ratio_db = float(20.0 * np.log10(max(cand_norm, 1e-30) / max(ref_norm, 1e-30)))
    phase_offset_deg = float(np.rad2deg(np.angle(inner)))
    if cand_norm > 0.0:
        scale = np.vdot(candidate, reference) / max(float(np.vdot(candidate, candidate).real), 1e-30)
        scaled = scale * candidate
        scaled_rel_l2 = float(np.linalg.norm(scaled - reference) / max(ref_norm, 1e-30))
        scale_abs = float(abs(scale))
        scale_phase_deg = float(np.rad2deg(np.angle(scale)))
    else:
        scaled_rel_l2 = float("nan")
        scale_abs = float("nan")
        scale_phase_deg = float("nan")
    max_abs_error = float(np.max(np.abs(candidate - reference))) if reference.size else float("nan")
    return {
        "row_count": int(reference.size),
        "reference_l2_norm": ref_norm,
        "candidate_l2_norm": cand_norm,
        "complex_correlation_abs": float(corr),
        "relative_l2_error": rel_l2,
        "scaled_relative_l2_error": scaled_rel_l2,
        "amplitude_ratio_db": amplitude_ratio_db,
        "phase_offset_deg": phase_offset_deg,
        "optimal_scale_abs": scale_abs,
        "optimal_scale_phase_deg": scale_phase_deg,
        "max_abs_error": max_abs_error,
    }


def compare_tables(reference: pd.DataFrame, candidate: pd.DataFrame, sample_filter: set[str] | None) -> tuple[pd.DataFrame, dict[str, object]]:
    if sample_filter is not None:
        reference = reference[reference["sample_id"].isin(sample_filter)].copy()
        candidate = candidate[candidate["sample_id"].isin(sample_filter)].copy()

    key_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization_norm"]
    joined = reference.merge(
        candidate,
        on=key_cols,
        how="outer",
        suffixes=("_reference", "_candidate"),
        indicator=True,
    )
    missing_candidate = int((joined["_merge"] == "left_only").sum())
    missing_reference = int((joined["_merge"] == "right_only").sum())
    common = joined[joined["_merge"] == "both"].copy()
    if common.empty:
        raise ValueError("no overlapping rows between reference and candidate near-field tables")

    rows: list[dict[str, object]] = []
    group_cols = ["sample_id", "frequency_hz", "polarization_norm"]
    for (sample_id, frequency_hz, polarization), group in common.groupby(group_cols, sort=True):
        metrics = vector_metrics(group["e_complex_reference"].to_numpy(), group["e_complex_candidate"].to_numpy())
        rows.append(
            {
                "sample_id": sample_id,
                "frequency_hz": float(frequency_hz),
                "polarization": polarization,
                **metrics,
            }
        )

    for (sample_id, frequency_hz), group in common.groupby(["sample_id", "frequency_hz"], sort=True):
        metrics = vector_metrics(group["e_complex_reference"].to_numpy(), group["e_complex_candidate"].to_numpy())
        rows.append(
            {
                "sample_id": sample_id,
                "frequency_hz": float(frequency_hz),
                "polarization": "all",
                **metrics,
            }
        )

    result = pd.DataFrame(rows).sort_values(["sample_id", "frequency_hz", "polarization"])
    all_rows = result[result["polarization"].eq("all")]
    summary = {
        "sample_count": int(common["sample_id"].nunique()),
        "frequency_count": int(common[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "common_row_count": int(len(common)),
        "missing_candidate_rows": missing_candidate,
        "missing_reference_rows": missing_reference,
        "min_all_complex_correlation_abs": float(all_rows["complex_correlation_abs"].min()),
        "max_all_relative_l2_error": float(all_rows["relative_l2_error"].max()),
        "max_all_scaled_relative_l2_error": float(all_rows["scaled_relative_l2_error"].max()),
        "max_abs_amplitude_ratio_db": float(all_rows["amplitude_ratio_db"].abs().max()),
        "max_abs_phase_offset_deg": float(all_rows["phase_offset_deg"].abs().max()),
    }
    return result, summary


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    content = f"""# True near-field comparison

This folder contains comparison metrics between a candidate CST true
near-field monitor export and the current FarfieldPlot-derived Level 1
near-field table.

## Files

| File | Purpose |
|---|---|
| `nearfield_export_comparison_by_group.csv` | Per sample, frequency, and polarization comparison metrics. Rows with `polarization=all` concatenate Ex/Ey/Ez. |
| `nearfield_export_comparison_summary.json` | Machine-readable worst-case summary. |

## Current summary

- Common rows: {summary["common_row_count"]}
- Missing candidate rows: {summary["missing_candidate_rows"]}
- Missing reference rows: {summary["missing_reference_rows"]}
- Minimum all-component complex correlation: {summary["min_all_complex_correlation_abs"]:.6f}
- Maximum all-component relative L2 error: {summary["max_all_relative_l2_error"]:.6e}
- Maximum all-component scaled relative L2 error: {summary["max_all_scaled_relative_l2_error"]:.6e}

Use this as a diagnostic gate, not as final sampling evidence. If a real CST
true-monitor export differs from the FarfieldPlot-derived baseline, rerun the
Level 1 source-model and sampling diagnostics with the true-monitor table.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare CST true near-field exports with the current Level 1 baseline.")
    parser.add_argument("--true-nearfield", default=str(DEFAULT_TRUE_NEARFIELD), help="Candidate true near-field CSV.")
    parser.add_argument("--reference-nearfield", default=str(DEFAULT_REFERENCE_NEARFIELD), help="Reference near-field CSV.")
    parser.add_argument("--case-table", default=str(DEFAULT_CASE_TABLE), help="Optional case table used to filter sample_id values.")
    parser.add_argument("--no-case-filter", action="store_true", help="Compare all samples present in the two tables.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    true_path = Path(args.true_nearfield)
    reference_path = Path(args.reference_nearfield)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate = normalize_nearfield_table(read_table(true_path), "candidate")
    reference = normalize_nearfield_table(read_table(reference_path), "reference")
    sample_filter = None if args.no_case_filter else load_case_filter(Path(args.case_table))
    results, summary_metrics = compare_tables(reference, candidate, sample_filter)

    results.to_csv(out_dir / "nearfield_export_comparison_by_group.csv", index=False, encoding="utf-8-sig")
    summary = {
        "candidate_nearfield": rel(true_path),
        "reference_nearfield": rel(reference_path),
        "case_table": None if args.no_case_filter else rel(Path(args.case_table)),
        "output_dir": rel(out_dir),
        "comparison_boundary": "FarfieldPlot-derived samples are a reference baseline; true near-field monitor samples become authoritative once exported.",
        **summary_metrics,
    }
    (out_dir / "nearfield_export_comparison_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"near-field comparison written to {out_dir}")
    print(f"common rows: {summary['common_row_count']}")
    print(f"min all-component corr: {summary['min_all_complex_correlation_abs']:.6f}")
    print(f"max all-component relative L2 error: {summary['max_all_relative_l2_error']:.6e}")


if __name__ == "__main__":
    main()
