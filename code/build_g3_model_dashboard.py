from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "outputs" / "g3_model_dashboard"


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def finite_float(value: Any) -> float:
    if value in ("", None):
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def format_float(value: Any, digits: int = 4) -> str:
    number = finite_float(value)
    if not math.isfinite(number):
        return ""
    if abs(number) >= 1000 or (0 < abs(number) < 0.001):
        return f"{number:.{digits}e}"
    return f"{number:.{digits}f}"


def status_rank(status: str) -> int:
    return {
        "strict_pass": 0,
        "corr_pass_nmse_near": 1,
        "corr_lobe_pass_nmse_open": 2,
        "reference_match": 3,
        "diagnostic_only": 4,
        "pending_source": 5,
        "needs_physical_rerun": 6,
        "row_count_mismatch": 7,
        "missing": 8,
    }.get(status, 99)


def category_rank(category: str) -> int:
    return {
        "data_boundary": 0,
        "trusted_sanity": 1,
        "rerun_priority": 2,
        "model_bottleneck": 3,
    }.get(category, 99)


def classify_status(min_corr: Any, max_nmse: Any, max_lobe_error_deg: Any) -> str:
    corr = finite_float(min_corr)
    nmse = finite_float(max_nmse)
    lobe = finite_float(max_lobe_error_deg)
    if not all(math.isfinite(v) for v in (corr, nmse, lobe)):
        return "missing"
    if corr >= 0.95 and nmse <= 1e-2 and lobe <= 5.0:
        return "strict_pass"
    if corr >= 0.95 and nmse <= 3e-2 and lobe <= 5.0:
        return "corr_pass_nmse_near"
    if corr >= 0.95 and lobe <= 5.0:
        return "corr_lobe_pass_nmse_open"
    return "diagnostic_only"


def row(
    category: str,
    artifact: str,
    scope: str,
    evidence_path: Path,
    command: str,
    best_setting: str,
    status: str,
    trust_level: str,
    interpretation: str,
    next_action: str,
    min_correlation: Any = math.nan,
    max_nmse: Any = math.nan,
    max_main_lobe_error_deg: Any = math.nan,
    sensor_count: Any = math.nan,
    blocker: str = "",
) -> dict[str, Any]:
    return {
        "category": category,
        "artifact": artifact,
        "scope": scope,
        "status": status,
        "category_rank": category_rank(category),
        "status_rank": status_rank(status),
        "trust_level": trust_level,
        "best_setting": best_setting,
        "min_correlation": finite_float(min_correlation),
        "max_nmse": finite_float(max_nmse),
        "max_main_lobe_error_deg": finite_float(max_main_lobe_error_deg),
        "sensor_count": finite_float(sensor_count),
        "evidence_path": display_path(evidence_path),
        "command": command,
        "interpretation": interpretation,
        "next_action": next_action,
        "blocker": blocker,
    }


def missing_row(category: str, artifact: str, evidence_path: Path, command: str) -> dict[str, Any]:
    return row(
        category=category,
        artifact=artifact,
        scope="missing evidence",
        evidence_path=evidence_path,
        command=command,
        best_setting="",
        status="missing",
        trust_level="missing",
        interpretation="Expected evidence is missing; rerun the command before using this gate.",
        next_action=command,
        blocker="missing evidence file",
    )


def best_candidate(summary: dict[str, Any], candidate_name: str | None = None) -> dict[str, Any]:
    candidates = summary.get("candidate_summary", [])
    if not isinstance(candidates, list) or not candidates:
        return {}
    if candidate_name is None:
        return dict(candidates[0])
    for item in candidates:
        if str(item.get("candidate", "")) == candidate_name:
            return dict(item)
    return {}


def build_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    center_path = ROOT / "data" / "sampling_layouts" / "cst_level1_center_source_check" / "cst_sampling_tradeoff_summary.json"
    center = read_json(center_path)
    if center:
        best = best_candidate(center, "full_grid_162") or best_candidate(center)
        status = classify_status(best.get("min_correlation"), best.get("max_nmse"), best.get("mean_main_lobe_error_deg"))
        rows.append(
            row(
                category="trusted_sanity",
                artifact="center_source_prior",
                scope="Level 1 known z-source, full 162-point reference",
                evidence_path=center_path,
                command="python code\\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\\sampling_layouts\\cst_level1_center_source_check",
                best_setting=f"{best.get('candidate', '')}, lambda={center.get('lambda_reg', '')}, grid={center.get('grid_shape', '')}",
                status=status,
                trust_level="trusted_data_path_check",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("mean_main_lobe_error_deg"),
                sensor_count=best.get("sensor_count"),
                interpretation="Known center-source prior validates the current CST/Python angle and far-field comparison chain.",
                next_action="Keep this as a sanity baseline; do not use it alone to prove generic reduced sampling.",
            )
        )
    else:
        rows.append(missing_row("trusted_sanity", "center_source_prior", center_path, "python code\\run_cst_sampling_tradeoff.py --level1-center-source-grid"))

    tradeoff_path = ROOT / "data" / "sampling_layouts" / "cst_level1_tradeoff" / "cst_sampling_tradeoff_summary.json"
    tradeoff = read_json(tradeoff_path)
    if tradeoff:
        best = best_candidate(tradeoff, "full_grid_162") or best_candidate(tradeoff)
        status = classify_status(best.get("min_correlation"), best.get("max_nmse"), best.get("mean_main_lobe_error_deg"))
        rows.append(
            row(
                category="model_bottleneck",
                artifact="generic_equivalent_source_grid",
                scope="Level 1 generic 5x3x3 source grid, full 162-point reference",
                evidence_path=tradeoff_path,
                command="python code\\run_cst_sampling_tradeoff.py",
                best_setting=f"{best.get('candidate', '')}, lambda={tradeoff.get('lambda_reg', '')}, grid={tradeoff.get('grid_shape', '')}",
                status=status,
                trust_level="diagnostic_only",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("mean_main_lobe_error_deg"),
                sensor_count=best.get("sensor_count"),
                interpretation="The generic grid fails before reduced-layout comparison, so low-point claims must wait.",
                next_action="Use structure-aware priors or true-monitor reruns before making sampling-compression claims.",
            )
        )
    else:
        rows.append(missing_row("model_bottleneck", "generic_equivalent_source_grid", tradeoff_path, "python code\\run_cst_sampling_tradeoff.py"))

    sweep_path = ROOT / "data" / "sampling_layouts" / "cst_level1_source_model_sweep" / "cst_source_model_sweep_summary.json"
    sweep = read_json(sweep_path)
    if sweep:
        best = dict(sweep.get("best_model", {}))
        rows.append(
            row(
                category="trusted_sanity",
                artifact="source_model_sweep_best",
                scope="Level 1 source-prior scan on full 162-point layout",
                evidence_path=sweep_path,
                command="python code\\run_cst_source_model_sweep.py",
                best_setting=f"{best.get('model_id', '')}, lambda={best.get('lambda_reg', '')}, candidate={best.get('candidate', '')}",
                status=str(best.get("status", "missing")),
                trust_level="trusted_for_known_source_only",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                interpretation="The scan confirms that the current data chain works under a tight known-source prior.",
                next_action="Keep the center prior as calibration evidence; use physical priors for unknown/source-rich cases.",
            )
        )
    else:
        rows.append(missing_row("trusted_sanity", "source_model_sweep_best", sweep_path, "python code\\run_cst_source_model_sweep.py"))

    sparse_path = ROOT / "data" / "sampling_layouts" / "cst_level1_sparse_calibration" / "cst_sparse_calibration_summary.json"
    sparse = read_json(sparse_path)
    if sparse:
        best = dict(sparse.get("best_setting", {}))
        rows.append(
            row(
                category="model_bottleneck",
                artifact="group_sparse_equivalent_sources",
                scope="Level 1 sparse source calibration on full 162-point layout",
                evidence_path=sparse_path,
                command="python code\\run_cst_sparse_reconstruction.py",
                best_setting=f"{best.get('config', '')}, {best.get('solver', '')}, l2={best.get('l2_lambda', '')}, group={best.get('group_alpha_frac', '')}",
                status=str(best.get("status", "missing")),
                trust_level="diagnostic_only",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                interpretation="Sparse support improves Corr/NMSE but does not fix the main-lobe/source-convention issue.",
                next_action="Do not tune sparsity alone; move to true monitor data and physical surface/vector bases.",
            )
        )
    else:
        rows.append(missing_row("model_bottleneck", "group_sparse_equivalent_sources", sparse_path, "python code\\run_cst_sparse_reconstruction.py"))

    convention_path = ROOT / "data" / "sampling_layouts" / "cst_level1_convention_check" / "cst_convention_check_summary.json"
    convention = read_json(convention_path)
    if convention:
        best = dict(convention.get("best_default_cube", {}))
        rows.append(
            row(
                category="model_bottleneck",
                artifact="generic_grid_convention_check",
                scope="Level 1 generic grid under phase/polarization transforms",
                evidence_path=convention_path,
                command="python code\\run_cst_level1_convention_check.py",
                best_setting=f"{best.get('source_model', '')}, {best.get('convention_id', '')}, lambda={best.get('lambda_reg', '')}",
                status=str(best.get("status", "missing")),
                trust_level="diagnostic_only",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                interpretation="No simple global phase or theta/phi transform rescues the generic grid.",
                next_action="Stop spending time on global sign flips unless true-monitor comparison contradicts this result.",
            )
        )
    else:
        rows.append(missing_row("model_bottleneck", "generic_grid_convention_check", convention_path, "python code\\run_cst_level1_convention_check.py"))

    swe_path = ROOT / "data" / "sampling_layouts" / "spherical_nf_ff_baseline" / "spherical_nf_ff_summary.json"
    swe = read_json(swe_path)
    if swe:
        best = dict(swe.get("best_setting", {}))
        rows.append(
            row(
                category="trusted_sanity",
                artifact="scalar_spherical_nf_ff_baseline",
                scope="Level 1 full 162-point scalar angular NF-FF sanity check",
                evidence_path=swe_path,
                command="python code\\run_spherical_nf_ff_baseline.py",
                best_setting=f"lmax={best.get('lmax', '')}, lambda={best.get('lambda_reg', '')}, modes={best.get('mode_count', '')}",
                status=str(best.get("status", "missing")),
                trust_level="trusted_angle_polarization_check",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                interpretation="The scalar angular SWE check strongly supports angle, phase, and polarization consistency.",
                next_action="Use this as a sanity baseline, while still labeling it non-vector and FarfieldPlot-derived.",
            )
        )
    else:
        rows.append(missing_row("trusted_sanity", "scalar_spherical_nf_ff_baseline", swe_path, "python code\\run_spherical_nf_ff_baseline.py"))

    swe_tradeoff_path = ROOT / "data" / "sampling_layouts" / "spherical_nf_ff_tradeoff" / "spherical_nf_ff_tradeoff_summary.json"
    swe_tradeoff = read_json(swe_tradeoff_path)
    if swe_tradeoff:
        best = dict(swe_tradeoff.get("smallest_strict_reduced_candidate", {}) or swe_tradeoff.get("best_overall_setting", {}))
        rows.append(
            row(
                category="rerun_priority",
                artifact="scalar_spherical_nf_ff_reduced_layout",
                scope="Reduced-layout scalar NF-FF diagnostic for true-monitor queue priority",
                evidence_path=swe_tradeoff_path,
                command="python code\\run_spherical_nf_ff_tradeoff.py",
                best_setting=f"{best.get('candidate', '')}, lmax={best.get('lmax', '')}, lambda={best.get('lambda_reg', '')}",
                status=str(best.get("status", "missing")),
                trust_level="layout_priority_not_final_proof",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                sensor_count=best.get("sensor_count"),
                interpretation="The 32-point reduced layout is a true-monitor rerun priority, not final vector SWE proof.",
                next_action="Export full_grid_162 true-monitor CSV first, then derive or compare geometric_farthest_32 and fibonacci_snap_120.",
            )
        )
    else:
        rows.append(missing_row("rerun_priority", "scalar_spherical_nf_ff_reduced_layout", swe_tradeoff_path, "python code\\run_spherical_nf_ff_tradeoff.py"))

    huygens_path = ROOT / "data" / "sampling_layouts" / "cst_level1_huygens_baseline" / "huygens_reconstruction_summary.json"
    huygens = read_json(huygens_path)
    if huygens:
        best = dict(huygens.get("best_setting", {}))
        rows.append(
            row(
                category="model_bottleneck",
                artifact="huygens_surface_prior",
                scope="Level 1 local Huygens surface, full 162-point reference",
                evidence_path=huygens_path,
                command="python code\\run_cst_huygens_baseline.py",
                best_setting=f"{best.get('model_variant', '')}, field={best.get('field_model', '')}, lambda={best.get('lambda_reg', '')}, smooth={best.get('smooth_lambda', '')}",
                status=str(best.get("status", "missing")),
                trust_level="diagnostic_only",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                sensor_count=162,
                interpretation="The Huygens workflow is runnable, but current field-model/smoothness axes still miss the physics gate.",
                next_action="Rerun on true-monitor input and validate the electric/magnetic surface-current convention.",
            )
        )
    else:
        rows.append(missing_row("model_bottleneck", "huygens_surface_prior", huygens_path, "python code\\run_cst_huygens_baseline.py"))

    gate_path = ROOT / "data" / "cst_true_nearfield_workpack" / "gate_report" / "true_nearfield_gate_summary.json"
    gate = read_json(gate_path)
    if gate:
        status_counts = gate.get("status_counts", {})
        status = "reference_match"
        if int(gate.get("pending_source_count", 0)) > 0:
            status = "pending_source"
        elif int(gate.get("needs_physical_rerun_count", 0)) > 0:
            status = "needs_physical_rerun"
        elif int(gate.get("row_count_mismatch_count", 0)) > 0:
            status = "row_count_mismatch"
        rows.append(
            row(
                category="data_boundary",
                artifact="true_nearfield_monitor_gate",
                scope="18-row true CST near-field monitor rerun queue",
                evidence_path=gate_path,
                command="python code\\run_true_nearfield_gate.py",
                best_setting=f"queue_rows={gate.get('queue_row_count', '')}, status_counts={status_counts}",
                status=status,
                trust_level="blocked_by_authoritative_monitor_data",
                interpretation="The immediate G3 boundary is data availability: real CST true near-field monitor CSVs are not present yet.",
                next_action="CST operator exports full_grid_162 true-monitor CSVs; algorithm operator reruns this gate and then reruns source/SWE/Huygens diagnostics if needed.",
                blocker="missing data/cst_exports/level1_true_nearfield/*.csv" if status == "pending_source" else "",
            )
        )
    else:
        rows.append(missing_row("data_boundary", "true_nearfield_monitor_gate", gate_path, "python code\\run_true_nearfield_gate.py"))

    return rows


def build_next_actions(status: pd.DataFrame) -> pd.DataFrame:
    pending_true_monitor = bool((status["artifact"] == "true_nearfield_monitor_gate").any()) and bool(
        (status["artifact"].eq("true_nearfield_monitor_gate") & status["status"].eq("pending_source")).any()
    )
    actions = [
        {
            "priority": 1,
            "owner": "CST operator",
            "gate": "true_monitor",
            "action": "Use outputs\\cst_true_nearfield_handoff\\expected_true_monitor_files.csv, then export authoritative full-grid CST true near-field monitor CSVs for the queued Level 1 cases.",
            "trigger": "G3 dashboard status is pending_source.",
            "artifact": "data/cst_exports/level1_true_nearfield/<sample>_true_nearfield.csv",
            "proof_to_close": "python code\\run_true_nearfield_gate.py reports no pending_source rows for full_grid_162.",
            "blocked_by": "CST monitor CSVs" if pending_true_monitor else "",
        },
        {
            "priority": 2,
            "owner": "Algorithm operator",
            "gate": "post_true_monitor",
            "action": "After full-grid monitor CSVs exist, derive queued 32/120 layouts and compare them against the FarfieldPlot-derived reference.",
            "trigger": "full_grid_162 true-monitor CSV exists for each required sample.",
            "artifact": "data/cst_true_nearfield_workpack/comparison/",
            "proof_to_close": "true_nearfield_gate_summary.json reports reference_match or needs_physical_rerun with comparison metrics, not pending_source.",
            "blocked_by": "Full-grid monitor CSVs" if pending_true_monitor else "",
        },
        {
            "priority": 3,
            "owner": "Algorithm operator",
            "gate": "physical_baseline",
            "action": "Rerun source-model, convention, scalar SWE, reduced-layout, and Huygens baselines on true-monitor input if the gate reports needs_physical_rerun.",
            "trigger": "true-monitor comparison differs materially from the current FarfieldPlot-derived table.",
            "artifact": "Updated data/sampling_layouts/* result directories and this dashboard.",
            "proof_to_close": "A full-grid physical baseline reaches strict_pass or an approved near-pass before reduced-layout claims are written.",
            "blocked_by": "True-monitor gate comparison result",
        },
        {
            "priority": 4,
            "owner": "Report/PPT operator",
            "gate": "wording",
            "action": "Use center-source and scalar SWE rows as sanity evidence; keep generic, sparse, and Huygens rows as diagnostic bottleneck evidence.",
            "trigger": "Preparing report, PPT, or mentor update.",
            "artifact": "docs/progress_reports/latest_mentor_brief.md or final report text.",
            "proof_to_close": "Reduced-layout claims explicitly say 'priority for true-monitor rerun' until a physical full-grid baseline passes.",
            "blocked_by": "",
        },
    ]
    return pd.DataFrame(actions)


def write_markdown(status: pd.DataFrame, actions: pd.DataFrame, summary: dict[str, Any], out_dir: Path) -> None:
    lines: list[str] = [
        "# G3 Model Dashboard",
        "",
        "This dashboard consolidates the current Level 1 inverse-model evidence.",
        "It separates report-safe sanity checks from diagnostic bottlenecks and true-monitor rerun priorities.",
        "",
        "## Executive Decision",
        "",
    ]

    if summary["true_monitor_status"] == "pending_source":
        lines.extend(
            [
                "- Do not claim final reduced-sampling proof yet.",
                "- The immediate boundary is missing CST true near-field monitor CSVs.",
                "- Export `full_grid_162` true-monitor data first; derive or compare the queued 32/120 layouts after that.",
            ]
        )
    else:
        lines.extend(
            [
                "- True-monitor gate is no longer pending; inspect its status before writing reduced-layout claims.",
                "- Rerun physical baselines when the gate reports `needs_physical_rerun`.",
            ]
        )

    lines.extend(
        [
            "",
            "## Evidence Matrix",
            "",
            "| Category | Artifact | Status | Trust level | Best setting | Min Corr | Max NMSE | Max lobe / deg | Sensors | Evidence |",
            "|---|---|---|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for item in status.itertuples(index=False):
        lines.append(
            f"| {item.category} | {item.artifact} | {item.status} | {item.trust_level} | "
            f"{item.best_setting} | {format_float(item.min_correlation)} | {format_float(item.max_nmse)} | "
            f"{format_float(item.max_main_lobe_error_deg, 2)} | {format_float(item.sensor_count, 0)} | `{item.evidence_path}` |"
        )

    lines.extend(["", "## Interpretation", ""])
    for item in status.itertuples(index=False):
        lines.append(f"- `{item.artifact}`: {item.interpretation}")

    lines.extend(
        [
            "",
            "## Next Actions",
            "",
            "| Priority | Owner | Gate | Action | Proof to close | Blocked by |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for item in actions.itertuples(index=False):
        lines.append(
            f"| {item.priority} | {item.owner} | {item.gate} | {item.action} | {item.proof_to_close} | {item.blocked_by} |"
        )

    lines.extend(
        [
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\build_g3_model_dashboard.py",
            "```",
            "",
        ]
    )
    (out_dir / "model_comparison.md").write_text("\n".join(lines), encoding="utf-8")


def build_summary(status: pd.DataFrame) -> dict[str, Any]:
    status_counts = status["status"].value_counts().to_dict()
    true_monitor = status.loc[status["artifact"] == "true_nearfield_monitor_gate"]
    true_monitor_status = str(true_monitor["status"].iloc[0]) if not true_monitor.empty else "missing"
    strict_or_near = status[status["status"].isin(["strict_pass", "corr_pass_nmse_near"])]
    diagnostic = status[status["status"].eq("diagnostic_only")]
    return {
        "generated_by": "code/build_g3_model_dashboard.py",
        "status_counts": {str(k): int(v) for k, v in status_counts.items()},
        "true_monitor_status": true_monitor_status,
        "trusted_or_near_pass_count": int(strict_or_near.shape[0]),
        "diagnostic_only_count": int(diagnostic.shape[0]),
        "output_files": {
            "model_comparison": "outputs\\g3_model_dashboard\\model_comparison.md",
            "g3_model_status": "outputs\\g3_model_dashboard\\g3_model_status.csv",
            "reconstruction_metrics": "outputs\\g3_model_dashboard\\reconstruction_metrics.csv",
            "next_actions": "outputs\\g3_model_dashboard\\g3_next_actions.csv",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a consolidated G3 model dashboard.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sort_columns = ["category_rank", "status_rank", "artifact"]
    status = pd.DataFrame(build_rows()).sort_values(sort_columns).reset_index(drop=True)
    actions = build_next_actions(status)
    summary = build_summary(status)

    output_status = status.drop(columns=["category_rank", "status_rank"])
    output_status.to_csv(out_dir / "g3_model_status.csv", index=False, encoding="utf-8-sig")
    output_status.to_csv(out_dir / "reconstruction_metrics.csv", index=False, encoding="utf-8-sig")
    actions.to_csv(out_dir / "g3_next_actions.csv", index=False, encoding="utf-8-sig")
    (out_dir / "g3_dashboard_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(output_status, actions, summary, out_dir)

    print(f"G3 model dashboard written to {display_path(out_dir)}")
    print(f"true monitor status: {summary['true_monitor_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
