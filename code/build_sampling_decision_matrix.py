from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LAYOUT_SUMMARY = ROOT / "data" / "sampling_layouts" / "sampling_layout_summary.csv"
DEFAULT_SWE_BEST = (
    ROOT
    / "data"
    / "sampling_layouts"
    / "spherical_nf_ff_tradeoff"
    / "spherical_nf_ff_tradeoff_best_by_candidate.csv"
)
DEFAULT_TRUE_MONITOR_QUEUE = (
    ROOT / "data" / "cst_true_nearfield_workpack" / "true_nearfield_priority_layout_queue.csv"
)
DEFAULT_RECOGNITION_ABLATION = (
    ROOT / "outputs" / "cst_recognition_level2_ablation" / "recognition_ablation_summary.json"
)
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "sampling_decision_matrix"


STATUS_WEIGHT = {
    "strict_pass": 1.0,
    "corr_pass_nmse_near": 0.78,
    "corr_pass": 0.62,
    "diagnostic_only": 0.18,
    "missing": 0.0,
}

METHOD_CLASSIFICATION_BONUS = {
    "task_driven": 0.24,
    "dictionary_weighted": 0.14,
    "geometric_farthest": 0.08,
    "fibonacci_snap": 0.08,
    "full_grid": 0.0,
}


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def finite_float(value: object, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(result):
        return default
    return result


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def load_queue(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["candidate", "case_priority", "layout_role", "queue_order"])
    return pd.read_csv(path)


def queue_records(queue: pd.DataFrame) -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    if queue.empty:
        return records
    for candidate, group in queue.groupby("candidate"):
        priorities = sorted(set(str(value) for value in group.get("case_priority", []) if not pd.isna(value)))
        roles = sorted(set(str(value) for value in group.get("layout_role", []) if not pd.isna(value)))
        order = pd.to_numeric(group.get("queue_order", pd.Series(dtype=float)), errors="coerce")
        records[str(candidate)] = {
            "true_monitor_queue_min_order": int(order.min()) if not order.dropna().empty else None,
            "true_monitor_queue_rows": int(group.shape[0]),
            "true_monitor_case_priorities": ";".join(priorities),
            "true_monitor_layout_roles": ";".join(roles),
        }
    return records


def score_reconstruction(row: pd.Series) -> float:
    status = str(row.get("status", "missing"))
    status_score = STATUS_WEIGHT.get(status, 0.0)
    corr_score = max(0.0, min(1.0, finite_float(row.get("min_correlation"))))
    nmse = finite_float(row.get("max_nmse"), default=1.0)
    nmse_score = max(0.0, min(1.0, 1.0 - nmse / 0.02))
    complex_l2 = finite_float(row.get("max_farfield_total_complex_relative_l2_error"), default=1.0)
    complex_score = max(0.0, min(1.0, 1.0 - complex_l2 / 0.15))
    lobe = finite_float(row.get("max_main_lobe_error_deg"), default=180.0)
    lobe_score = max(0.0, min(1.0, 1.0 - lobe / 90.0))
    return round(
        0.32 * status_score + 0.24 * corr_score + 0.18 * nmse_score + 0.16 * complex_score + 0.10 * lobe_score,
        4,
    )


def score_classification(row: pd.Series, full_sensor_count: int) -> float:
    method = str(row.get("method", ""))
    sensor_count = max(int(finite_float(row.get("sensor_count"))), 1)
    accuracy = max(0.0, min(1.0, finite_float(row.get("classification_accuracy"))))
    efficiency = max(0.0, min(1.0, 1.0 - sensor_count / max(full_sensor_count, 1)))
    coherence = finite_float(row.get("mutual_coherence"), default=1.0)
    coherence_score = max(0.0, min(1.0, 1.0 - coherence))
    method_bonus = METHOD_CLASSIFICATION_BONUS.get(method, 0.04)
    return round(0.50 * accuracy + 0.24 * efficiency + 0.16 * coherence_score + 0.10 * method_bonus, 4)


def recommendation_for(row: pd.Series) -> tuple[str, str, str]:
    candidate = str(row["candidate"])
    method = str(row["method"])
    sensor_count = int(row["sensor_count"])
    status = str(row.get("status", "missing"))
    queue_role = str(row.get("true_monitor_layout_roles", ""))

    if candidate == "full_grid_162":
        return (
            "reference_anchor",
            "physical_reference",
            "Keep as full-grid reference; do not replace it with a reduced layout before the physical/vector baseline passes.",
        )
    if "smallest_strict" in queue_role:
        return (
            "reconstruction_priority",
            "queued_true_monitor_rerun",
            "Use as the first reduced-layout true-monitor rerun after the required full-grid CSVs arrive.",
        )
    if "conservative" in queue_role and "crosscheck" in queue_role:
        return (
            "conservative_cross_check",
            "queued_true_monitor_rerun",
            "Use as the 120-point conservative cross-check against the 32-point reduced candidate.",
        )
    if method == "task_driven" and sensor_count in {32, 48}:
        return (
            "classification_probe",
            "classification_priority_not_final_proof",
            "Use for classification-focused stress tests; validate on true-monitor or Level 2 reduced-layout ablation before report claims.",
        )
    if status == "strict_pass" and sensor_count <= 48:
        return (
            "alternate_reconstruction_candidate",
            "swe_strict_not_queued",
            "Keep as a backup reduced-layout rerun if CST time allows; current evidence is scalar/FarfieldPlot-derived.",
        )
    if status == "strict_pass":
        return (
            "secondary_reconstruction_candidate",
            "swe_strict_not_queued",
            "Useful for sensitivity comparison, but lower priority than the current true-monitor queue.",
        )
    return (
        "diagnostic_only",
        "not_report_proof",
        "Keep as diagnostic evidence; do not use as reduced-layout proof before a physical full-grid baseline passes.",
    )


def build_matrix(layout_summary: pd.DataFrame, swe_best: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    required_layout_cols = {"candidate", "method", "sensor_count", "classification_accuracy", "mutual_coherence"}
    missing_layout = required_layout_cols - set(layout_summary.columns)
    if missing_layout:
        raise ValueError(f"layout summary missing columns: {sorted(missing_layout)}")
    if "candidate" not in swe_best.columns:
        raise ValueError("SWE best table missing candidate column")

    merged = layout_summary.merge(
        swe_best,
        on="candidate",
        how="left",
        suffixes=("_proxy", "_swe"),
    )
    if "method_proxy" in merged.columns:
        merged["method"] = merged["method_proxy"]
    if "sensor_count_proxy" in merged.columns:
        merged["sensor_count"] = merged["sensor_count_proxy"]

    for candidate, record in queue_records(queue).items():
        mask = merged["candidate"].astype(str) == candidate
        for key, value in record.items():
            merged.loc[mask, key] = value
    for column in [
        "true_monitor_queue_min_order",
        "true_monitor_queue_rows",
        "true_monitor_case_priorities",
        "true_monitor_layout_roles",
    ]:
        if column not in merged.columns:
            merged[column] = "" if column.endswith(("priorities", "roles")) else 0
    merged["true_monitor_queue_rows"] = pd.to_numeric(merged["true_monitor_queue_rows"], errors="coerce").fillna(0).astype(int)
    merged["true_monitor_queue_min_order"] = pd.to_numeric(
        merged["true_monitor_queue_min_order"],
        errors="coerce",
    )

    full_sensor_count = int(pd.to_numeric(layout_summary["sensor_count"], errors="coerce").max())
    merged["reconstruction_priority_score"] = merged.apply(score_reconstruction, axis=1)
    merged["classification_priority_score"] = merged.apply(score_classification, axis=1, full_sensor_count=full_sensor_count)

    recommendations = merged.apply(recommendation_for, axis=1, result_type="expand")
    recommendations.columns = ["recommendation", "evidence_role", "next_action"]
    merged = pd.concat([merged, recommendations], axis=1)

    merged["claim_boundary"] = merged["evidence_role"].map(
        {
            "physical_reference": "reference only; reduced-layout proof still requires physical/vector baseline",
            "queued_true_monitor_rerun": "rerun priority; not final vector SWE/Huygens proof",
            "classification_priority_not_final_proof": "classification probe; needs reduced-layout recognition validation",
            "swe_strict_not_queued": "scalar SWE diagnostic; backup priority only",
            "not_report_proof": "diagnostic only",
        }
    )
    merged["claim_boundary"] = merged["claim_boundary"].fillna("diagnostic only")

    columns = [
        "candidate",
        "method",
        "sensor_count",
        "recommendation",
        "evidence_role",
        "reconstruction_priority_score",
        "classification_priority_score",
        "classification_accuracy",
        "channel_unknown_ratio",
        "mutual_coherence",
        "status",
        "min_correlation",
        "max_nmse",
        "max_main_lobe_error_deg",
        "min_farfield_total_complex_correlation_abs",
        "max_farfield_total_complex_relative_l2_error",
        "max_basis_condition",
        "true_monitor_queue_rows",
        "true_monitor_queue_min_order",
        "true_monitor_case_priorities",
        "true_monitor_layout_roles",
        "claim_boundary",
        "next_action",
    ]
    for column in columns:
        if column not in merged.columns:
            merged[column] = ""

    order = {
        "reference_anchor": 0,
        "reconstruction_priority": 1,
        "conservative_cross_check": 2,
        "classification_probe": 3,
        "alternate_reconstruction_candidate": 4,
        "secondary_reconstruction_candidate": 5,
        "diagnostic_only": 6,
    }
    merged["_recommendation_order"] = merged["recommendation"].map(order).fillna(99)
    merged = merged.sort_values(
        [
            "_recommendation_order",
            "sensor_count",
            "reconstruction_priority_score",
            "classification_priority_score",
            "candidate",
        ],
        ascending=[True, True, False, False, True],
    )
    return merged[columns].copy()


def recognition_context(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "available": False,
            "path": rel(path),
            "note": "Level 2 recognition ablation summary not found.",
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("ablation_cases", [])
    if not cases:
        return {
            "available": True,
            "path": rel(path),
            "case_count": 0,
            "note": "No ablation cases were recorded.",
        }
    best_low_sensor = sorted(
        cases,
        key=lambda item: (
            -finite_float(item.get("best_accuracy")),
            finite_float(item.get("sensor_count"), default=10_000.0),
            finite_float(item.get("frequency_count"), default=10_000.0),
        ),
    )[0]
    return {
        "available": True,
        "path": rel(path),
        "case_count": len(cases),
        "best_low_sensor_case": best_low_sensor,
        "boundary": (
            "This ablation uses Level 2 recognition features and farthest-style sensor fractions; "
            "it supports classification stress-test planning but does not validate the exact G2 candidate layouts."
        ),
    }


def write_readme(out_dir: Path, matrix: pd.DataFrame, summary: dict[str, object]) -> None:
    top_rows = []
    display = matrix.head(12)
    for row in display.itertuples(index=False):
        top_rows.append(
            f"| {row.candidate} | {int(row.sensor_count)} | {row.recommendation} | {row.evidence_role} | "
            f"{float(row.reconstruction_priority_score):.4f} | {float(row.classification_priority_score):.4f} | "
            f"{row.status} | {row.claim_boundary} |"
        )

    content = f"""# Sampling Decision Matrix

This directory stores the G2 decision surface for reduced sampling layouts.
It combines the geometry/proxy summary, scalar spherical NF-FF reduced-layout
diagnostics, and the true-monitor rerun queue.

## Current Decision

- `full_grid_162` remains the physical reference anchor.
- `geometric_farthest_32` is the first reduced-layout true-monitor rerun
  priority because it is the smallest scalar SWE `strict_pass` candidate.
- `fibonacci_snap_120` remains the conservative 120-point cross-check.
- `task_driven_48` and `task_driven_32` are classification-focused probes, not
  report-level proof.

## Top Rows

| Candidate | Sensors | Recommendation | Evidence role | Reconstruction score | Classification score | SWE status | Claim boundary |
|---|---:|---|---|---:|---:|---|---|
{chr(10).join(top_rows)}

## Files

| File | Purpose |
|---|---|
| `sampling_decision_matrix.csv` | One row per layout candidate with scores, queue role, recommendation, and claim boundary. |
| `sampling_decision_summary.json` | Machine-readable summary and input references. |
| `README.md` | Human-facing decision note. |

## Regenerate

```powershell
python code\\build_sampling_decision_matrix.py
```

## Boundary

This matrix is a planning and collaboration artifact. It does not replace the
true CST near-field monitor gate. Reduced-layout claims remain blocked until a
full-grid physical/vector baseline passes on authoritative monitor data.

## Inputs

- Layout proxy summary: `{summary['inputs']['layout_summary']}`
- Scalar SWE reduced-layout table: `{summary['inputs']['swe_best']}`
- True-monitor queue: `{summary['inputs']['true_monitor_queue']}`
- Recognition ablation context: `{summary['recognition_context']['path']}`
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def build_summary(
    matrix: pd.DataFrame,
    args: argparse.Namespace,
    recognition: dict[str, object],
) -> dict[str, object]:
    def row_as_dict(recommendation: str) -> dict[str, object] | None:
        rows = matrix[matrix["recommendation"] == recommendation]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {
            "candidate": str(row["candidate"]),
            "sensor_count": int(row["sensor_count"]),
            "evidence_role": str(row["evidence_role"]),
            "reconstruction_priority_score": finite_float(row["reconstruction_priority_score"]),
            "classification_priority_score": finite_float(row["classification_priority_score"]),
            "status": str(row["status"]),
            "claim_boundary": str(row["claim_boundary"]),
            "next_action": str(row["next_action"]),
        }

    return {
        "generated_by": "code/build_sampling_decision_matrix.py",
        "purpose": "G2 reduced-sampling decision surface for CST rerun planning and report wording boundaries.",
        "inputs": {
            "layout_summary": rel(Path(args.layout_summary)),
            "swe_best": rel(Path(args.swe_best)),
            "true_monitor_queue": rel(Path(args.true_monitor_queue)),
        },
        "output_files": {
            "matrix": rel(Path(args.out_dir) / "sampling_decision_matrix.csv"),
            "summary": rel(Path(args.out_dir) / "sampling_decision_summary.json"),
            "readme": rel(Path(args.out_dir) / "README.md"),
        },
        "candidate_count": int(matrix.shape[0]),
        "recommendation_counts": matrix["recommendation"].value_counts().to_dict(),
        "reference_anchor": row_as_dict("reference_anchor"),
        "reconstruction_priority": row_as_dict("reconstruction_priority"),
        "conservative_cross_check": row_as_dict("conservative_cross_check"),
        "classification_probes": [
            {
                "candidate": str(row["candidate"]),
                "sensor_count": int(row["sensor_count"]),
                "classification_priority_score": finite_float(row["classification_priority_score"]),
                "claim_boundary": str(row["claim_boundary"]),
            }
            for _, row in matrix[matrix["recommendation"] == "classification_probe"].sort_values(
                ["sensor_count", "classification_priority_score"],
                ascending=[True, False],
            ).iterrows()
        ],
        "recognition_context": recognition,
        "boundary": (
            "Planning artifact only. Use this matrix to choose CST true-monitor reruns and classification "
            "stress tests; do not use it as final reduced-sampling proof before true-monitor and physical/vector gates pass."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the G2 sampling layout decision matrix.")
    parser.add_argument("--layout-summary", default=str(DEFAULT_LAYOUT_SUMMARY), help="sampling_layout_summary.csv path.")
    parser.add_argument("--swe-best", default=str(DEFAULT_SWE_BEST), help="spherical NF-FF best-by-candidate CSV path.")
    parser.add_argument(
        "--true-monitor-queue",
        default=str(DEFAULT_TRUE_MONITOR_QUEUE),
        help="true_nearfield_priority_layout_queue.csv path.",
    )
    parser.add_argument(
        "--recognition-ablation",
        default=str(DEFAULT_RECOGNITION_ABLATION),
        help="Level 2 recognition ablation summary JSON path.",
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    layout_summary = load_csv(Path(args.layout_summary))
    swe_best = load_csv(Path(args.swe_best))
    queue = load_queue(Path(args.true_monitor_queue))
    matrix = build_matrix(layout_summary, swe_best, queue)
    recognition = recognition_context(Path(args.recognition_ablation))
    summary = build_summary(matrix, args, recognition)

    matrix.to_csv(out_dir / "sampling_decision_matrix.csv", index=False, encoding="utf-8-sig")
    (out_dir / "sampling_decision_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, matrix, summary)

    print(f"sampling decision matrix written to {rel(out_dir)}")
    if summary["reconstruction_priority"]:
        item = summary["reconstruction_priority"]
        print(f"reconstruction priority: {item['candidate']} ({item['sensor_count']} sensors)")
    if summary["conservative_cross_check"]:
        item = summary["conservative_cross_check"]
        print(f"conservative cross-check: {item['candidate']} ({item['sensor_count']} sensors)")
    if summary["classification_probes"]:
        probes = ", ".join(item["candidate"] for item in summary["classification_probes"])
        print(f"classification probes: {probes}")


if __name__ == "__main__":
    main()
