from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BATCH_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_extrapolation_batch"
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_impedance_stability"
DEFAULT_TREE_INSPECTION_DIRS = (
    ROOT / "outputs" / "cst_meshsafe_huygens_result_export",
    ROOT / "outputs" / "cst_meshsafe_huygens_result_export_halfwave",
)
RESULTS_FILENAME = "meshsafe_huygens_extrapolation_results.csv"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return ROOT / candidate


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except Exception:
        return str(path)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def finite_float(value: Any, default: float = math.nan) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def load_candidate_results(batch_dir: Path) -> pd.DataFrame:
    files = sorted(batch_dir.glob(f"*/{RESULTS_FILENAME}"))
    if not files:
        direct = batch_dir / RESULTS_FILENAME
        files = [direct] if direct.exists() else []
    frames: list[pd.DataFrame] = []
    for path in files:
        frame = pd.read_csv(path)
        frame["source_results_csv"] = display_path(path)
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def normalize_candidates(raw: pd.DataFrame, variant_family: str) -> pd.DataFrame:
    required = {
        "sample_id",
        "variant",
        "variant_family",
        "impedance_factor_to_eta0",
        "impedance_ohm",
        "calibration_mode",
        "scaled_power_nmse",
        "correlation",
        "main_lobe_region_error_deg",
        "status",
    }
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ValueError(f"missing required columns in mesh-safe Huygens results: {missing}")

    work = raw.copy()
    for column in [
        "frequency_hz",
        "impedance_factor_to_eta0",
        "impedance_ohm",
        "scaled_power_nmse",
        "correlation",
        "main_lobe_region_error_deg",
        "main_lobe_region_jaccard",
        "main_lobe_region_min_capture",
    ]:
        if column in work.columns:
            work[column] = pd.to_numeric(work[column], errors="coerce")

    mask = (
        work["calibration_mode"].astype(str).str.strip().eq("scalar_impedance_scan")
        & work["variant_family"].astype(str).str.strip().eq(variant_family)
        & work["impedance_factor_to_eta0"].notna()
        & work["scaled_power_nmse"].notna()
        & work["correlation"].notna()
    )
    filtered = work.loc[mask].copy()
    if filtered.empty:
        return filtered

    filtered = filtered.sort_values(
        ["sample_id", "scaled_power_nmse", "impedance_factor_to_eta0"],
        ascending=[True, True, True],
    ).reset_index(drop=True)
    filtered["rank_by_nmse"] = filtered.groupby("sample_id").cumcount() + 1
    return filtered


def summarize_cases(
    candidates: pd.DataFrame,
    nmse_absolute_tolerance: float,
    nmse_relative_tolerance: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    case_rows: list[dict[str, Any]] = []
    curve_frames: list[pd.DataFrame] = []

    for sample_id, group in candidates.groupby("sample_id", sort=True):
        ordered = group.sort_values(["scaled_power_nmse", "impedance_factor_to_eta0"]).reset_index(drop=True)
        best = ordered.iloc[0]
        best_nmse = finite_float(best["scaled_power_nmse"])
        scan_min = finite_float(ordered["impedance_factor_to_eta0"].min())
        scan_max = finite_float(ordered["impedance_factor_to_eta0"].max())
        best_factor = finite_float(best["impedance_factor_to_eta0"])
        absolute_window = max(nmse_absolute_tolerance, abs(best_nmse) * nmse_relative_tolerance)
        plateau_limit = best_nmse + absolute_window
        plateau = ordered.loc[ordered["scaled_power_nmse"] <= plateau_limit].copy()
        factor_min = finite_float(plateau["impedance_factor_to_eta0"].min())
        factor_max = finite_float(plateau["impedance_factor_to_eta0"].max())
        lower_boundary = math.isclose(best_factor, scan_min, rel_tol=1e-9, abs_tol=1e-12)
        upper_boundary = math.isclose(best_factor, scan_max, rel_tol=1e-9, abs_tol=1e-12)
        if lower_boundary:
            recommendation = "extend_lower_eta_scan"
        elif upper_boundary:
            recommendation = "extend_upper_eta_scan"
        else:
            recommendation = "candidate_interior_eta"

        annotated = ordered.copy()
        annotated["nmse_delta_from_best"] = annotated["scaled_power_nmse"] - best_nmse
        annotated["nmse_ratio_to_best"] = annotated["scaled_power_nmse"] / max(best_nmse, 1e-30)
        annotated["in_nmse_plateau"] = annotated["scaled_power_nmse"] <= plateau_limit
        curve_frames.append(annotated)

        case_rows.append(
            {
                "sample_id": sample_id,
                "candidate_count": int(ordered.shape[0]),
                "scan_min_factor_to_eta0": scan_min,
                "scan_max_factor_to_eta0": scan_max,
                "best_factor_to_eta0": best_factor,
                "best_impedance_ohm": finite_float(best["impedance_ohm"]),
                "best_variant": str(best["variant"]),
                "best_status": str(best["status"]),
                "best_scaled_power_nmse": best_nmse,
                "best_correlation": finite_float(best["correlation"]),
                "best_region_lobe_error_deg": finite_float(best["main_lobe_region_error_deg"]),
                "best_at_lower_scan_boundary": lower_boundary,
                "best_at_upper_scan_boundary": upper_boundary,
                "nmse_plateau_abs_window": absolute_window,
                "plateau_factor_min_to_eta0": factor_min,
                "plateau_factor_max_to_eta0": factor_max,
                "plateau_factor_width_to_eta0": factor_max - factor_min,
                "plateau_candidate_count": int(plateau.shape[0]),
                "recommendation": recommendation,
            }
        )

    case_summary = pd.DataFrame(case_rows)
    curve = pd.concat(curve_frames, ignore_index=True) if curve_frames else pd.DataFrame()
    return case_summary, curve


def walk_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for key, item in value.items():
            out.extend(walk_strings(key))
            out.extend(walk_strings(item))
        return out
    if isinstance(value, list):
        out = []
        for item in value:
            out.extend(walk_strings(item))
        return out
    return []


def inspect_hfield_readiness(directories: list[Path]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for directory in directories:
        inspection_json = directory / "meshsafe_huygens_tree_inspection.json"
        if not inspection_json.exists():
            rows.append(
                {
                    "result_export_dir": display_path(directory),
                    "inspection_json": display_path(inspection_json),
                    "e_field_string_count": 0,
                    "h_field_string_count": 0,
                    "magnetic_string_count": 0,
                    "status": "missing_inspection",
                }
            )
            continue
        try:
            data = json.loads(inspection_json.read_text(encoding="utf-8"))
            strings = walk_strings(data)
        except Exception:
            strings = inspection_json.read_text(encoding="utf-8", errors="replace").splitlines()
        e_count = sum(1 for item in strings if "E-Field" in item or "E Field" in item)
        h_count = sum(1 for item in strings if "H-Field" in item or "H Field" in item)
        magnetic_count = sum(1 for item in strings if "Magnetic" in item or "magnetic" in item)
        status = "hfield_resulttree_present" if h_count > 0 else "hfield_resulttree_missing"
        rows.append(
            {
                "result_export_dir": display_path(directory),
                "inspection_json": display_path(inspection_json),
                "e_field_string_count": int(e_count),
                "h_field_string_count": int(h_count),
                "magnetic_string_count": int(magnetic_count),
                "status": status,
            }
        )
    return pd.DataFrame(rows)


def classify_overall(case_summary: pd.DataFrame) -> str:
    if case_summary.empty:
        return "missing"
    if bool(case_summary["best_at_lower_scan_boundary"].any()):
        return "needs_impedance_extension"
    if bool(case_summary["best_at_upper_scan_boundary"].any()):
        return "needs_impedance_extension"
    unique_best = {
        round(finite_float(value), 12)
        for value in case_summary["best_factor_to_eta0"].tolist()
        if math.isfinite(finite_float(value))
    }
    if len(unique_best) == 1:
        return "stable_impedance_candidate"
    return "cross_case_impedance_disagreement"


def build_next_commands(overall_status: str) -> pd.DataFrame:
    if overall_status == "needs_impedance_extension":
        lower_scan = (
            "python code\\run_cst_meshsafe_huygens_extrapolation.py --batch "
            "--batch-out-dir data\\sampling_layouts\\cst_meshsafe_huygens_impedance_lower_scan "
            "--impedance-factors 0.015625,0.03125,0.0625,0.125,0.1875,0.25,0.375,0.5,0.75,1.0,1.5,2.0,3.0,4.0"
        )
        stability = (
            "python code\\run_cst_impedance_stability_gate.py "
            "--batch-dir data\\sampling_layouts\\cst_meshsafe_huygens_impedance_lower_scan"
        )
        primary_action = "If H-field curves remain unavailable, extend the scalar eta scan below the current lower bound."
        primary_close = "The best eta_eff is no longer on a scan boundary, or the report keeps the route as a calibrated proxy."
    elif overall_status == "cross_case_impedance_disagreement":
        lower_scan = "Add matching CST H-field probe export, or add more source-family CST cases before using one global eta_eff."
        stability = "python code\\run_cst_impedance_stability_gate.py"
        primary_action = "Resolve the source-dependent eta_eff disagreement with H-field-backed currents or more CST cases."
        primary_close = "The stability gate records a cross-case eta model, or final wording keeps eta_eff source-dependent and proxy-level."
    else:
        lower_scan = "Add independent CST H-field probe export before final Huygens wording."
        stability = "python code\\run_cst_impedance_stability_gate.py"
        primary_action = "Promote the interior eta candidate to H-field-backed evidence before final Huygens wording."
        primary_close = "H-field-backed currents or additional cases confirm the current eta_eff candidate."
    return pd.DataFrame(
        [
            {
                "priority": 1,
                "action": primary_action,
                "command": lower_scan,
                "expected_close_condition": primary_close,
            },
            {
                "priority": 2,
                "action": "Rebuild the impedance stability gate after the scan or H-field export changes.",
                "command": stability,
                "expected_close_condition": "impedance_stability_summary.json records stable_impedance_candidate or a documented boundary limitation.",
            },
        ]
    )


def write_readme(out_dir: Path, summary: dict[str, Any], case_summary: pd.DataFrame, hfield: pd.DataFrame) -> None:
    if case_summary.empty:
        case_table = "| Sample | Status |\n|---|---|\n| none | missing |\n"
    else:
        rows = [
            "| Sample | Best eta/eta0 | Boundary | NMSE | Corr | Recommendation |",
            "|---|---:|---|---:|---:|---|",
        ]
        for row in case_summary.itertuples(index=False):
            boundary = "lower" if row.best_at_lower_scan_boundary else "upper" if row.best_at_upper_scan_boundary else "no"
            rows.append(
                "| {sample} | {eta:.6g} | {boundary} | {nmse:.6g} | {corr:.6g} | {rec} |".format(
                    sample=row.sample_id,
                    eta=float(row.best_factor_to_eta0),
                    boundary=boundary,
                    nmse=float(row.best_scaled_power_nmse),
                    corr=float(row.best_correlation),
                    rec=row.recommendation,
                )
            )
        case_table = "\n".join(rows) + "\n"

    if hfield.empty:
        hfield_table = "| Result export | H-field status |\n|---|---|\n| none | missing |\n"
    else:
        rows = ["| Result export | E-field hits | H-field hits | Status |", "|---|---:|---:|---|"]
        for row in hfield.itertuples(index=False):
            rows.append(
                f"| `{row.result_export_dir}` | {row.e_field_string_count} | {row.h_field_string_count} | {row.status} |"
            )
        hfield_table = "\n".join(rows) + "\n"

    content = f"""# CST Mesh-Safe Huygens Impedance Stability Gate

## Status

Overall status: `{summary["overall_status"]}`

This gate checks whether the scalar `eta_eff/eta0` calibration used by the
mesh-safe Huygens proxy has an interior, cross-case stable optimum. A best value
on a scan boundary is treated as a limitation, even when the far-field shape
metrics are strong.

## Case Summary

{case_table}

## H-Field ResultTree Readiness

{hfield_table}

## Interpretation

The current CST route is runnable for the mesh-safe projects. The remaining
issue is evidence quality: current cached ResultTree exports expose E-field
probe curves, while matching H-field probe curves have not been found. Until
H-field-backed currents or an interior stable `eta_eff` bound exist, this route
should be described as a calibrated proxy rather than final Stratton-Chu or
Huygens proof.

## Command

```powershell
python code\\run_cst_impedance_stability_gate.py
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check scalar impedance stability for CST mesh-safe Huygens results.")
    parser.add_argument("--batch-dir", type=Path, default=DEFAULT_BATCH_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--variant-family", default="outgoing_equivalence_minus")
    parser.add_argument("--nmse-absolute-tolerance", type=float, default=1e-6)
    parser.add_argument("--nmse-relative-tolerance", type=float, default=0.01)
    parser.add_argument(
        "--tree-inspection-dirs",
        default=",".join(display_path(path) for path in DEFAULT_TREE_INSPECTION_DIRS),
        help="Comma-separated directories containing meshsafe_huygens_tree_inspection.json.",
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> dict[str, Any]:
    batch_dir = resolve_path(args.batch_dir)
    out_dir = resolve_path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = load_candidate_results(batch_dir)
    candidates = normalize_candidates(raw, args.variant_family) if not raw.empty else pd.DataFrame()
    if candidates.empty:
        case_summary = pd.DataFrame()
        curve = pd.DataFrame()
    else:
        case_summary, curve = summarize_cases(
            candidates,
            nmse_absolute_tolerance=args.nmse_absolute_tolerance,
            nmse_relative_tolerance=args.nmse_relative_tolerance,
        )

    tree_dirs = [resolve_path(item.strip()) for item in str(args.tree_inspection_dirs).split(",") if item.strip()]
    hfield = inspect_hfield_readiness(tree_dirs)
    overall_status = classify_overall(case_summary)
    next_commands = build_next_commands(overall_status)

    curve.to_csv(out_dir / "impedance_stability_curve.csv", index=False, encoding="utf-8-sig")
    case_summary.to_csv(out_dir / "impedance_stability_case_summary.csv", index=False, encoding="utf-8-sig")
    hfield.to_csv(out_dir / "hfield_resulttree_readiness.csv", index=False, encoding="utf-8-sig")
    next_commands.to_csv(out_dir / "next_impedance_stability_commands.csv", index=False, encoding="utf-8-sig")

    min_corr = (
        float(case_summary["best_correlation"].min())
        if not case_summary.empty and "best_correlation" in case_summary
        else math.nan
    )
    max_nmse = (
        float(case_summary["best_scaled_power_nmse"].max())
        if not case_summary.empty and "best_scaled_power_nmse" in case_summary
        else math.nan
    )
    summary = {
        "generated_at": now_iso(),
        "generated_by": "code/run_cst_impedance_stability_gate.py",
        "batch_dir": display_path(batch_dir),
        "out_dir": display_path(out_dir),
        "variant_family": args.variant_family,
        "case_count": int(case_summary.shape[0]),
        "overall_status": overall_status,
        "any_best_at_scan_boundary": bool(
            not case_summary.empty
            and (
                case_summary["best_at_lower_scan_boundary"].any()
                or case_summary["best_at_upper_scan_boundary"].any()
            )
        ),
        "min_best_correlation": min_corr,
        "max_best_scaled_power_nmse": max_nmse,
        "hfield_resulttree_status": (
            "hfield_resulttree_present"
            if not hfield.empty and (hfield["status"] == "hfield_resulttree_present").any()
            else "hfield_resulttree_missing"
        ),
        "case_summaries": case_summary.to_dict(orient="records"),
        "hfield_readiness": hfield.to_dict(orient="records"),
        "outputs": {
            "case_summary": "impedance_stability_case_summary.csv",
            "curve": "impedance_stability_curve.csv",
            "hfield_readiness": "hfield_resulttree_readiness.csv",
            "next_commands": "next_impedance_stability_commands.csv",
            "readme": "README.md",
        },
    }
    write_json(out_dir / "impedance_stability_summary.json", summary)
    write_readme(out_dir, summary, case_summary, hfield)
    return summary


def main() -> int:
    summary = run(parse_args())
    print(f"CST impedance stability gate written to {summary['out_dir']}")
    print(
        f"status={summary['overall_status']}; cases={summary['case_count']}; "
        f"hfield={summary['hfield_resulttree_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
