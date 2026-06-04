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
        "real_eh_strict_batch_pass": 1,
        "real_eh_frozen_rule_strict_pass": 1,
        "rotation_covariance_strict_pass": 1,
        "physics_proxy_pass": 1,
        "corr_pass_nmse_near": 1,
        "real_eh_frozen_rule_region_pass": 2,
        "rotation_covariance_pass": 2,
        "impedance_region_proxy_batch_pass": 2,
        "region_proxy_batch_pass": 2,
        "region_shape_pass": 2,
        "rotation_covariance_near": 3,
        "real_eh_strict_batch_calibration_needed": 3,
        "stable_impedance_candidate": 3,
        "corr_lobe_pass_nmse_open": 2,
        "reference_match": 3,
        "shape_pass_lobe_ambiguous": 4,
        "diagnostic_only": 4,
        "rotation_covariance_diagnostic": 4,
        "needs_impedance_extension": 5,
        "cross_case_impedance_disagreement": 5,
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


def best_batch_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases = summary.get("case_summaries", [])
    rows: list[dict[str, Any]] = []
    if not isinstance(cases, list):
        return rows
    for case in cases:
        if not isinstance(case, dict):
            continue
        best = case.get("best_setting", {})
        quality = case.get("quality", {})
        if not isinstance(best, dict):
            continue
        item = dict(best)
        item["sample_id"] = case.get("sample_id", "")
        item["sensor_count"] = quality.get("sensor_count", math.nan) if isinstance(quality, dict) else math.nan
        item["hfield_available"] = bool(case.get("hfield_available", False))
        item["hfield_load_status"] = str(case.get("hfield_load_status", "unknown"))
        rows.append(item)
    return rows


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
                best_setting=(
                    f"lmax={best.get('lmax', '')}, lambda={best.get('lambda_reg', '')}, "
                    f"modes={best.get('mode_count', '')}, "
                    f"ff_complex_l2={format_float(best.get('max_farfield_total_complex_relative_l2_error'))}"
                ),
                status=str(best.get("status", "missing")),
                trust_level="trusted_angle_polarization_check",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                interpretation=(
                    "The scalar angular SWE check now includes total complex Etheta/Ephi residuals; "
                    "it strongly supports angle, phase, and tangential-component consistency."
                ),
                next_action=(
                    "Use this as a component-aware sanity baseline, while still labeling it non-vector "
                    "and FarfieldPlot-derived."
                ),
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
                best_setting=(
                    f"{best.get('candidate', '')}, lmax={best.get('lmax', '')}, "
                    f"lambda={best.get('lambda_reg', '')}, "
                    f"ff_complex_l2={format_float(best.get('max_farfield_total_complex_relative_l2_error'))}"
                ),
                status=str(best.get("status", "missing")),
                trust_level="layout_priority_not_final_proof",
                min_correlation=best.get("min_correlation"),
                max_nmse=best.get("max_nmse"),
                max_main_lobe_error_deg=best.get("max_main_lobe_error_deg"),
                sensor_count=best.get("sensor_count"),
                interpretation=(
                    "The 32-point reduced layout has strong power-pattern and complex-component sanity metrics; "
                    "it is a true-monitor rerun priority, not final vector SWE proof."
                ),
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

    meshsafe_batch_path = (
        ROOT
        / "data"
        / "sampling_layouts"
        / "cst_meshsafe_huygens_extrapolation_batch"
        / "meshsafe_huygens_batch_summary.json"
    )
    meshsafe_batch = read_json(meshsafe_batch_path)
    meshsafe_requested = 0
    meshsafe_hfield_available = 0
    meshsafe_best_real_hfield = 0
    meshsafe_real_eh_accepted = 0
    if meshsafe_batch:
        case_rows = best_batch_rows(meshsafe_batch)
        requested = int(meshsafe_batch.get("case_count_requested", 0))
        meshsafe_requested = requested
        completed = int(meshsafe_batch.get("case_count_completed", 0))
        missing = int(meshsafe_batch.get("case_count_missing_or_failed", 0))
        strict_or_proxy_count = int(meshsafe_batch.get("case_count_strict_or_proxy", 0))
        pass_like = int(meshsafe_batch.get("case_count_strict_proxy_or_region", 0))
        impedance_scan_enabled = bool(meshsafe_batch.get("impedance_scan_enabled", False))
        non_eta0_count = int(meshsafe_batch.get("case_count_best_non_eta0_impedance", 0))
        hfield_available_count = int(meshsafe_batch.get("case_count_hfield_available", 0))
        real_eh_accepted_count = int(meshsafe_batch.get("case_count_real_eh_accepted", 0))
        best_real_hfield_count = int(meshsafe_batch.get("case_count_best_real_hfield", 0))
        real_eh_calibration_status = str(
            meshsafe_batch.get("real_eh_operator_calibration_status", "unknown")
        )
        frozen_real_eh_status = str(meshsafe_batch.get("frozen_real_eh_rule_status", "missing"))
        frozen_real_eh_rule = meshsafe_batch.get("frozen_real_eh_best_rule", {})
        if not isinstance(frozen_real_eh_rule, dict):
            frozen_real_eh_rule = {}
        frozen_rule_requested = int(frozen_real_eh_rule.get("requested_case_count", 0) or 0)
        frozen_rule_accepted = int(frozen_real_eh_rule.get("accepted_case_count", 0) or 0)
        frozen_rule_strict = int(frozen_real_eh_rule.get("strict_case_count", 0) or 0)
        frozen_rule_variant = str(frozen_real_eh_rule.get("variant", ""))
        frozen_rule_j_scale = frozen_real_eh_rule.get("hfield_j_scale", "")
        best_real_eh_j_scales = meshsafe_batch.get("best_real_eh_j_scale_values", [])
        best_real_eh_families = meshsafe_batch.get("best_real_eh_variant_families", [])
        best_real_eh_j_ratio = meshsafe_batch.get("best_real_eh_j_scale_ratio", math.nan)
        best_real_eh_j_scale_text = (
            ", ".join(format_float(value, 4) for value in best_real_eh_j_scales)
            if isinstance(best_real_eh_j_scales, list)
            else str(best_real_eh_j_scales)
        )
        best_real_eh_family_text = (
            ", ".join(str(value) for value in best_real_eh_families)
            if isinstance(best_real_eh_families, list)
            else str(best_real_eh_families)
        )
        meshsafe_hfield_available = hfield_available_count
        meshsafe_real_eh_accepted = real_eh_accepted_count
        meshsafe_best_real_hfield = best_real_hfield_count
        if (
            completed == requested
            and requested > 0
            and strict_or_proxy_count == requested
            and best_real_hfield_count == requested
        ):
            batch_status = (
                "real_eh_strict_batch_pass"
                if real_eh_calibration_status == "stable_for_current_level1_cases"
                else "real_eh_frozen_rule_strict_pass"
                if frozen_real_eh_status == "frozen_real_eh_strict_pass"
                else "real_eh_frozen_rule_region_pass"
                if frozen_real_eh_status in (
                    "frozen_real_eh_mixed_strict_region_pass",
                    "frozen_real_eh_region_or_proxy_pass",
                )
                else "real_eh_strict_batch_calibration_needed"
            )
        elif completed == requested and requested > 0 and pass_like == requested:
            batch_status = "impedance_region_proxy_batch_pass" if impedance_scan_enabled else "region_proxy_batch_pass"
        elif completed == requested and pass_like > 0:
            batch_status = "physics_proxy_pass"
        elif missing > 0:
            batch_status = "pending_source"
        else:
            batch_status = "diagnostic_only"
        if batch_status.startswith("real_eh_frozen_rule") and frozen_real_eh_rule:
            max_scaled_nmse = finite_float(frozen_real_eh_rule.get("max_scaled_power_nmse"))
            max_region_error = finite_float(frozen_real_eh_rule.get("max_main_lobe_region_error_deg"))
            min_corr = finite_float(frozen_real_eh_rule.get("min_correlation"))
        else:
            max_scaled_nmse = max((finite_float(item.get("scaled_power_nmse")) for item in case_rows), default=math.nan)
            max_region_error = max(
                (finite_float(item.get("main_lobe_region_error_deg")) for item in case_rows),
                default=math.nan,
            )
            min_corr = min((finite_float(item.get("correlation")) for item in case_rows), default=math.nan)
        best_settings = "; ".join(
            (
                f"{item.get('sample_id', '')}:{item.get('status', '')}/{item.get('variant', '')}"
                f"/eta={format_float(item.get('impedance_factor_to_eta0'), 3)}eta0"
                f"/J={format_float(item.get('hfield_j_scale'), 4)}"
                f"/H={item.get('hfield_load_status', 'unknown')}"
            )
            for item in case_rows
        )
        if frozen_rule_variant:
            best_settings = (
                f"{best_settings}; frozen:{frozen_real_eh_status}/{frozen_rule_variant}"
                f"/J={format_float(frozen_rule_j_scale, 4)}"
                f"/accepted={frozen_rule_accepted}/{frozen_rule_requested}"
                f"/strict={frozen_rule_strict}/{frozen_rule_requested}"
            )
        rows.append(
            row(
                category="trusted_sanity",
                artifact="meshsafe_huygens_real_cst_batch",
                scope=f"{completed}/{requested} Level 1 real CST local Huygens exports",
                evidence_path=meshsafe_batch_path,
                command="python code\\run_cst_meshsafe_huygens_extrapolation.py --batch",
                best_setting=best_settings,
                status=batch_status,
                trust_level="real_cst_data_chain_not_final_huygens_proof",
                min_correlation=min_corr,
                max_nmse=max_scaled_nmse,
                max_main_lobe_error_deg=max_region_error,
                sensor_count=96,
                interpretation=(
                    "The mesh-safe route now uses real CST local probe curves for two Level 1 sources and "
                    "the best diagnostic branches now use real E/H currents rather than the scalar eta_eff proxy "
                    f"({non_eta0_count}/{requested} best settings use non-eta0 eta_eff). "
                    f"Matching H-field is now loaded for {hfield_available_count}/{requested} cases and "
                    f"real E/H candidates are accepted for {real_eh_accepted_count}/{requested} cases; "
                    f"{best_real_hfield_count}/{requested} best settings currently select a real-H branch, "
                    f"with J-scale values {best_real_eh_j_scale_text}, families {best_real_eh_family_text}, "
                    f"ratio {format_float(best_real_eh_j_ratio, 4)}, and calibration status "
                    f"{real_eh_calibration_status}. The frozen-rule gate selects {frozen_rule_variant or 'no candidate'} "
                    f"with status {frozen_real_eh_status}, accepted {frozen_rule_accepted}/{frozen_rule_requested}, "
                    f"strict {frozen_rule_strict}/{frozen_rule_requested}, min Corr "
                    f"{format_float(frozen_real_eh_rule.get('min_correlation'))}, and max scaled NMSE "
                    f"{format_float(frozen_real_eh_rule.get('max_scaled_power_nmse'))}. This is now an operator-stability "
                    "question rather than a CST export blocker."
                ),
                next_action=(
                    "Promote the frozen real E/H candidate into a geometry/physics rule, then test the accepted rule on a broader CST "
                    "source-family set before propagating it to the 13 m measurement shell."
                ),
            )
        )
    else:
        rows.append(
            missing_row(
                "trusted_sanity",
                "meshsafe_huygens_real_cst_batch",
                meshsafe_batch_path,
                "python code\\run_cst_meshsafe_huygens_extrapolation.py --batch",
            )
        )

    rotation_covariance_path = (
        ROOT
        / "data"
        / "sampling_layouts"
        / "cst_meshsafe_huygens_rotation_covariance"
        / "huygens_rotation_covariance_summary.json"
    )
    rotation_covariance = read_json(rotation_covariance_path)
    if rotation_covariance:
        rows.append(
            row(
                category="trusted_sanity",
                artifact="meshsafe_huygens_rotation_covariance",
                scope=(
                    f"{rotation_covariance.get('base_case_count', 0)} real E/H base cases x "
                    f"{rotation_covariance.get('rotation_count', 0)} rigid rotations"
                ),
                evidence_path=rotation_covariance_path,
                command="python code\\run_cst_huygens_rotation_covariance.py",
                best_setting=(
                    f"{rotation_covariance.get('variant', '')}; "
                    f"strict={rotation_covariance.get('covariance_strict_count', 0)}/"
                    f"{rotation_covariance.get('covariance_test_count', 0)}; "
                    f"base_accepted={rotation_covariance.get('base_real_cst_accepted_count', 0)}/"
                    f"{rotation_covariance.get('base_case_count', 0)}"
                ),
                status=str(rotation_covariance.get("status", "missing")),
                trust_level="operator_covariance_not_new_cst_source",
                min_correlation=rotation_covariance.get("min_covariance_correlation"),
                max_nmse=rotation_covariance.get("max_covariance_scaled_power_nmse"),
                max_main_lobe_error_deg=rotation_covariance.get("max_covariance_region_error_deg"),
                sensor_count=96,
                interpretation=(
                    "The frozen real E/H Huygens candidate is now checked under rigid rotations of the measured "
                    "CST local E/H surface fields. This proves the Python current extraction and far-field "
                    "operator are coordinate-covariant for the current vector rule; it does not replace real "
                    "CST x/y, tilted, off-axis, or multi-source exports."
                ),
                next_action=(
                    "Keep this as the prerequisite geometry-rule evidence, then add true CST source-family "
                    "exports to test the frozen rule against independent electromagnetic solves."
                ),
            )
        )
    else:
        rows.append(
            missing_row(
                "trusted_sanity",
                "meshsafe_huygens_rotation_covariance",
                rotation_covariance_path,
                "python code\\run_cst_huygens_rotation_covariance.py",
            )
        )

    impedance_stability_path = (
        ROOT
        / "data"
        / "sampling_layouts"
        / "cst_meshsafe_huygens_impedance_stability"
        / "impedance_stability_summary.json"
    )
    impedance_stability = read_json(impedance_stability_path)
    if impedance_stability:
        case_rows = impedance_stability.get("case_summaries", [])
        stability_status = str(impedance_stability.get("overall_status", "diagnostic_only"))
        best_settings = "; ".join(
            (
                f"{item.get('sample_id', '')}:eta={format_float(item.get('best_factor_to_eta0'), 4)}eta0"
                f"/{item.get('recommendation', '')}"
            )
            for item in case_rows
        )
        hfield_status = str(impedance_stability.get("hfield_resulttree_status", "unknown"))
        if meshsafe_requested > 0:
            hfield_context = (
                f"Latest batch H-field coverage is {meshsafe_hfield_available}/{meshsafe_requested} loaded and "
                f"real E/H acceptance is {meshsafe_real_eh_accepted}/{meshsafe_requested}; "
                f"{meshsafe_best_real_hfield}/{meshsafe_requested} best settings use a real-H branch; "
                f"the older stability ResultTree flag is {hfield_status}."
            )
        else:
            hfield_context = f"Current H-field ResultTree readiness is {hfield_status}."
        if stability_status == "cross_case_impedance_disagreement":
            stability_interpretation = (
                "The lower-eta extension removed the immediate scan-boundary issue, but the two real CST "
                f"cases now prefer different eta_eff values. {hfield_context} "
                "Therefore the scalar impedance route is a source-dependent calibrated proxy, not a single "
                "global physical impedance closure."
            )
            stability_next_action = (
                "Rerun the stability check through the accepted real E/H branch and keep scalar eta_eff as a "
                "proxy baseline before using this route in final Huygens wording."
            )
        elif stability_status == "needs_impedance_extension":
            stability_interpretation = (
                "The scalar impedance proxy is now guarded by an explicit stability check, and the best eta_eff "
                f"still sits on a scan boundary. {hfield_context} The "
                "calibrated proxy remains useful but not final physics evidence."
            )
            stability_next_action = (
                "Run the lower-eta scan listed by the stability gate only as a proxy check; prioritize full "
                "E/H operator calibration before final physics wording."
            )
        else:
            stability_interpretation = (
                "The scalar impedance proxy is now guarded by an explicit stability check. "
                f"{hfield_context} Keep the result as a calibrated "
                "proxy until H-field-backed currents or broader CST case coverage confirm it."
            )
            stability_next_action = (
                "Use the proxy as a baseline while calibrating the accepted E/H branch and adding CST source-family checks."
            )
        rows.append(
            row(
                category="model_bottleneck",
                artifact="meshsafe_huygens_impedance_stability",
                scope=f"{impedance_stability.get('case_count', 0)} scalar eta calibration cases plus H-field tree readiness",
                evidence_path=impedance_stability_path,
                command="python code\\run_cst_impedance_stability_gate.py",
                best_setting=best_settings,
                status=stability_status,
                trust_level="calibration_sensitivity_check",
                min_correlation=impedance_stability.get("min_best_correlation"),
                max_nmse=impedance_stability.get("max_best_scaled_power_nmse"),
                max_main_lobe_error_deg=0.0,
                sensor_count=96,
                interpretation=stability_interpretation,
                next_action=stability_next_action,
            )
        )
    else:
        rows.append(
            missing_row(
                "model_bottleneck",
                "meshsafe_huygens_impedance_stability",
                impedance_stability_path,
                "python code\\run_cst_impedance_stability_gate.py",
            )
        )

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
    meshsafe_ready = bool(
        (
            status["artifact"].eq("meshsafe_huygens_real_cst_batch")
            & status["status"].isin(
                [
                    "real_eh_strict_batch_pass",
                    "real_eh_frozen_rule_strict_pass",
                    "real_eh_frozen_rule_region_pass",
                    "real_eh_strict_batch_calibration_needed",
                    "impedance_region_proxy_batch_pass",
                    "region_proxy_batch_pass",
                    "physics_proxy_pass",
                ]
            )
        ).any()
    )
    impedance_extension_needed = bool(
        (
            status["artifact"].eq("meshsafe_huygens_impedance_stability")
            & status["status"].isin(["needs_impedance_extension", "cross_case_impedance_disagreement"])
        ).any()
    )
    real_eh_calibration_needed = bool(
        (
            status["artifact"].eq("meshsafe_huygens_real_cst_batch")
            & status["status"].eq("real_eh_strict_batch_calibration_needed")
        ).any()
    )
    frozen_real_eh_needs_validation = bool(
        (
            status["artifact"].eq("meshsafe_huygens_real_cst_batch")
            & status["status"].isin(["real_eh_frozen_rule_strict_pass", "real_eh_frozen_rule_region_pass"])
        ).any()
    )
    rotation_covariance_ready = bool(
        (
            status["artifact"].eq("meshsafe_huygens_rotation_covariance")
            & status["status"].isin(["rotation_covariance_strict_pass", "rotation_covariance_pass"])
        ).any()
    )
    actions = [
        {
            "priority": 1,
            "owner": "Independent workflow",
            "gate": "meshsafe_huygens_physics",
            "action": (
                "Close the real E/H Huygens operator-stability gate: tie the plus/minus convention and J-scale "
                "normalization to source geometry, then test true CST x/y, tilted, off-axis, or multi-source cases "
                "before propagating the accepted rule toward the 13 m shell."
            ),
            "trigger": (
                "Mesh-safe real CST batch has a frozen real E/H candidate and the rotation-covariance gate passes; the remaining proof is independent CST source-family validation." if frozen_real_eh_needs_validation and rotation_covariance_ready else
                "Mesh-safe real CST batch now has a frozen real E/H candidate accepted by every current Level 1 case; it still needs a physics/geometry explanation and broader source-family validation." if frozen_real_eh_needs_validation else
                "Mesh-safe real CST batch gate now reaches strict/proxy status with real E/H currents, but the best J-scale/sign is source-dependent." if real_eh_calibration_needed else
                "Mesh-safe real CST batch gate is region/proxy ready, but the stability gate still shows "
                "source-dependent impedance sensitivity." if impedance_extension_needed else
                "Mesh-safe real CST batch gate is region/proxy ready and the impedance stability gate is available."
            ),
            "artifact": "data/cst_exports/level1_meshsafe_huygens/*_local_hfield.csv and data/sampling_layouts/cst_meshsafe_huygens_*/",
            "proof_to_close": "Batch summary reports H-field loaded for all required cases, frozen_real_eh_rule_status is accepted, rotation_covariance status is pass, and independent CST source-family rows keep the same frozen rule accepted.",
            "blocked_by": "" if meshsafe_ready else "Mesh-safe batch gate",
        },
        {
            "priority": 2,
            "owner": "CST operator",
            "gate": "true_monitor",
            "action": "Use outputs\\cst_true_nearfield_handoff\\expected_true_monitor_files.csv, then export authoritative full-grid CST true near-field monitor CSVs for the queued Level 1 cases.",
            "trigger": "G3 dashboard status is pending_source.",
            "artifact": "data/cst_exports/level1_true_nearfield/<sample>_true_nearfield.csv",
            "proof_to_close": "python code\\run_true_nearfield_gate.py reports no pending_source rows for full_grid_162.",
            "blocked_by": "CST monitor CSVs" if pending_true_monitor else "",
        },
        {
            "priority": 3,
            "owner": "Algorithm operator",
            "gate": "post_true_monitor",
            "action": "After full-grid monitor CSVs exist, derive queued 32/120 layouts and compare them against the FarfieldPlot-derived reference.",
            "trigger": "full_grid_162 true-monitor CSV exists for each required sample.",
            "artifact": "data/cst_true_nearfield_workpack/comparison/",
            "proof_to_close": "true_nearfield_gate_summary.json reports reference_match or needs_physical_rerun with comparison metrics, not pending_source.",
            "blocked_by": "Full-grid monitor CSVs" if pending_true_monitor else "",
        },
        {
            "priority": 4,
            "owner": "Algorithm operator",
            "gate": "physical_baseline",
            "action": "Rerun source-model, convention, scalar SWE, reduced-layout, and Huygens baselines on true-monitor input if the gate reports needs_physical_rerun.",
            "trigger": "true-monitor comparison differs materially from the current FarfieldPlot-derived table.",
            "artifact": "Updated data/sampling_layouts/* result directories and this dashboard.",
            "proof_to_close": "A full-grid physical baseline reaches strict_pass or an approved near-pass before reduced-layout claims are written.",
            "blocked_by": "True-monitor gate comparison result",
        },
        {
            "priority": 5,
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
    meshsafe_rows = status.loc[status["artifact"] == "meshsafe_huygens_real_cst_batch"]
    if not meshsafe_rows.empty:
        meshsafe_status = str(meshsafe_rows.iloc[0].get("status", ""))
        frozen_note = (
            " A frozen real E/H candidate is now accepted by every current Level 1 case, so the remaining bottleneck is explaining and validating that frozen operator."
            if meshsafe_status.startswith("real_eh_frozen_rule")
            else " The current bottleneck is cross-source J-scale/sign stability before the operator is safe to propagate."
        )
        lines.append(
            "- Mesh-safe Huygens is no longer blocked at CST export: both Level 1 E/H local-field paths are loaded, "
            f"and the best batch branches now use real H-field currents.{frozen_note}"
        )
    covariance_rows = status.loc[status["artifact"] == "meshsafe_huygens_rotation_covariance"]
    if not covariance_rows.empty and str(covariance_rows.iloc[0].get("status", "")).startswith("rotation_covariance"):
        lines.append(
            "- The frozen Huygens rule also has a rotation-covariance operator check; treat it as geometry-rule evidence, "
            "not as a substitute for independent CST source-family solves."
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
    strict_or_near = status[
        status["status"].isin(
            [
                "strict_pass",
                "corr_pass_nmse_near",
                "physics_proxy_pass",
                "region_proxy_batch_pass",
                "impedance_region_proxy_batch_pass",
            ]
        )
    ]
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
