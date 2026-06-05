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
        "source_family_solver_safe_reduced_layout_validated": 1,
        "source_family_solver_safe_matched_eh_validated": 1,
        "reduced_layout_validated": 1,
        "source_family_solver_safe_matched_eh_exported": 2,
        "rotation_covariance_pass": 2,
        "source_family_solver_safe_matched_eh_finished": 2,
        "source_family_solver_safe_full_efield_finished": 2,
        "source_family_solver_completed": 2,
        "source_family_projects_generated": 2,
        "source_family_workpack_ready": 3,
        "source_family_solver_partial_with_timeout": 4,
        "source_family_project_generation_partial": 4,
        "source_family_solver_pilot_timed_out": 5,
        "source_family_solver_partial": 5,
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

    source_family_path = (
        ROOT
        / "data"
        / "cst_meshsafe_huygens_source_family_workpack"
        / "source_family_workpack_summary.json"
    )
    source_family_generation_path = (
        ROOT
        / "outputs"
        / "cst_meshsafe_huygens_source_family_generation"
        / "source_family_project_generation_summary.json"
    )
    source_family_solver_path = (
        ROOT
        / "outputs"
        / "cst_meshsafe_huygens_source_family_solver_status"
        / "source_family_solver_status_summary.json"
    )
    source_family_safe_path = (
        ROOT
        / "outputs"
        / "cst_meshsafe_huygens_source_family_solver_safe_status"
        / "solver_safe_status_summary.json"
    )
    source_family_reduced_layout_path = (
        ROOT
        / "data"
        / "sampling_layouts"
        / "cst_meshsafe_huygens_source_family_reduced_layout_x"
        / "reduced_layout_summary.json"
    )
    source_family = read_json(source_family_path)
    source_family_generation = read_json(source_family_generation_path)
    source_family_solver = read_json(source_family_solver_path)
    source_family_safe = read_json(source_family_safe_path)
    safe_stage_for_workpack = str(source_family_safe.get("stage_status", "")) if source_family_safe else ""
    if source_family:
        solver_status = str(source_family_solver.get("stage_status", ""))
        if solver_status in (
            "source_family_solver_pilot_timed_out",
            "source_family_solver_partial_with_timeout",
            "source_family_solver_partial",
            "source_family_solver_completed",
        ):
            trial_count = int(source_family_solver.get("trial_count", 0) or 0)
            timed_out_count = int(source_family_solver.get("timed_out_count", 0) or 0)
            completed_count = int(source_family_solver.get("completed_count", 0) or 0)
            solver_start_ok_count = int(source_family_solver.get("solver_start_ok_count", 0) or 0)
            source_family_status = solver_status
            source_family_evidence = source_family_solver_path
            source_family_command = "python code\\build_cst_source_family_solver_status.py"
            source_family_scope = (
                f"{trial_count} CST source-family solver pilot trial(s); "
                f"{timed_out_count} timed out; {completed_count} completed"
            )
            source_family_best = (
                f"solver_start_ok={solver_start_ok_count}/{trial_count}; "
                f"max_elapsed_s={format_float(source_family_solver.get('max_elapsed_seconds'))}; "
                f"max_time_steps={source_family_solver.get('max_time_steps', 0)}; "
                f"real_cst_api_trials={source_family_solver.get('real_cst_api_used_count', 0)}"
            )
            if safe_stage_for_workpack == "source_family_solver_safe_reduced_layout_validated":
                source_family_interpretation = (
                    "The original 600 s source-family solver pilot is now historical timeout evidence. The "
                    "solver-safe follow-up has completed the matched 96-point E/H short x pilot, exported local "
                    "E/H and far-field references, passed the frozen E/H Huygens validation, and passed a sparse "
                    "reconstruction gate down to a deployable 24-point Fibonacci layout."
                )
                source_family_next = (
                    "Carry the same CST export, sparse reconstruction, and frozen j96 Huygens chain to the "
                    "y-oriented and off-axis source-family cases without retuning."
                )
                source_family_trust = "historical_timeout_superseded_by_reduced_layout_cst_pilot"
                source_family_blocker = ""
            elif safe_stage_for_workpack == "source_family_solver_safe_matched_eh_validated":
                source_family_interpretation = (
                    "The original 600 s source-family solver pilot is now historical timeout evidence. The "
                    "solver-safe follow-up has completed the matched 96-point E/H pilot, exported local E/H "
                    "CSV rows and a CST far-field reference for the short x case, and passed the real/frozen "
                    "E/H Huygens region-shape validation."
                )
                source_family_next = (
                    "Use this as the closed short x pilot gate, then expand the same frozen operator to reduced "
                    "layouts and additional source-family cases without retuning."
                )
                source_family_trust = "historical_timeout_superseded_by_validated_matched_eh_pilot"
                source_family_blocker = ""
            elif safe_stage_for_workpack == "source_family_solver_safe_matched_eh_exported":
                source_family_interpretation = (
                    "The original 600 s source-family solver pilot is now historical timeout evidence. The "
                    "solver-safe follow-up has completed matched 96-point E/H pilot solves and CSV/far-field "
                    "exports for the short x case; the remaining gate is frozen Huygens validation."
                )
                source_family_next = (
                    "Run the frozen real E/H Huygens validation on the exported short x source-family pilot, "
                    "then update the dashboard before expanding the source family."
                )
                source_family_trust = "historical_timeout_superseded_by_exported_matched_eh_pilot"
                source_family_blocker = "frozen Huygens validation not yet recorded"
            elif safe_stage_for_workpack == "source_family_solver_safe_matched_eh_finished":
                source_family_interpretation = (
                    "The original 600 s source-family solver pilot is now historical timeout evidence: it showed "
                    "that CST could start and populate probe ResultTree entries, while the long-window solver-safe "
                    "follow-up has since completed the matched 96-point E/H pilot for the same short x case."
                )
                source_family_next = (
                    "Use the completed solver-safe E/H pilot to export matched local CSVs and far-field references, "
                    "then evaluate the frozen Huygens rule before expanding to the rest of the source family."
                )
                source_family_trust = "historical_timeout_superseded_by_matched_solver_safe_pilot"
                source_family_blocker = ""
            elif safe_stage_for_workpack == "source_family_solver_safe_full_efield_finished":
                source_family_interpretation = (
                    "The original 600 s source-family solver pilot is now historical timeout evidence: it showed "
                    "that CST could start and populate probe ResultTree entries, while the solver-safe follow-up "
                    "has since completed the full 96-point E-field pilot."
                )
                source_family_next = (
                    "Run the matching 96-point H-field long-window pilot, then export matched local E/H CSVs and "
                    "far-field references for frozen-rule validation."
                )
                source_family_trust = "historical_timeout_partly_superseded_by_solver_safe_pilot"
                source_family_blocker = "matching 96-point H-field pilot not yet complete"
            else:
                source_family_interpretation = (
                    "The independent source-family gate has moved into real CST solver execution. The first pilot "
                    "started successfully and populated ResultTree probe entries, but the current time-domain setup "
                    "did not finish inside the solver timeout, so no matched local E/H CSV or far-field export is "
                    "ready for frozen-rule validation."
                )
                source_family_next = (
                    "Build a solver-safe pilot for the short x-oriented case before running the full 12-project queue: "
                    "reduce or verify CST time-domain settings, or switch to a validated frequency-domain/fast-path "
                    "variant, then rerun solve/export and only then evaluate the frozen Huygens rule."
                )
                source_family_trust = "solver_gate_not_physics_proof"
                source_family_blocker = "current CST time-domain solver settings timed out before export"
        else:
            generation_status = str(source_family_generation.get("stage_status", ""))
            if generation_status in ("source_family_projects_generated", "source_family_project_generation_partial"):
                source_family_status = generation_status
                source_family_evidence = source_family_generation_path
                source_family_command = "python code\\build_cst_source_family_generation_status.py"
                source_family_scope = (
                    f"{source_family_generation.get('efield_projects_created', 0)} E-field + "
                    f"{source_family_generation.get('hfield_projects_created', 0)} H-field CST source-family projects"
                )
                source_family_best = (
                    f"rule={source_family.get('frozen_rule_under_test', '')}; "
                    f"projects={source_family_generation.get('total_projects_created', 0)}; "
                    f"rows={source_family_generation.get('total_project_rows', 0)}; "
                    f"real_cst_api={source_family_generation.get('real_cst_api_used', False)}"
                )
                source_family_interpretation = (
                    "The S42 handoff has moved past planning: real CST API project generation succeeded for the E/H "
                    "source-family set. This proves the x/y/off-axis case generator is CST-compatible; it still does "
                    "not prove the electromagnetic result until the generated projects are solved and exported."
                )
                source_family_next = (
                    "Solve the generated projects listed in next_source_family_commands.csv, export matched local "
                    "E/H probe CSVs and far-field references, then run the frozen Huygens rule without retuning."
                )
                source_family_trust = "project_generation_not_physics_proof"
                source_family_blocker = ""
            else:
                source_family_status = str(source_family.get("stage_status", "missing"))
                source_family_evidence = source_family_path
                source_family_command = "python code\\prepare_cst_huygens_source_family_workpack.py"
                source_family_scope = (
                    f"{source_family.get('automation_ready_count', 0)} automation-ready CST source-family cases; "
                    f"{source_family.get('pending_advanced_count', 0)} advanced gates tracked"
                )
                source_family_best = (
                    f"rule={source_family.get('frozen_rule_under_test', '')}; "
                    f"cases={source_family.get('axis_aligned_case_count', 0)}; "
                    f"probes/case={source_family.get('probe_count_per_case', 0)}; "
                    f"probe_rows={source_family.get('probe_row_count', 0)}"
                )
                source_family_interpretation = (
                    "The next independent CST validation package is ready: x/y-oriented and off-axis Level 1 "
                    "single-source cases have case-scoped local Huygens probe rows and ordered CST project, solve, "
                    "and export commands. This is an execution handoff, not proof that the frozen rule has passed "
                    "new electromagnetic solves."
                )
                source_family_next = (
                    "Run data\\cst_meshsafe_huygens_source_family_workpack\\next_source_family_commands.csv, then "
                    "evaluate the frozen E/H Huygens rule on the exported source-family E/H CSVs without retuning."
                )
                source_family_trust = "workpack_not_physics_proof"
                source_family_blocker = ""
        rows.append(
            row(
                category="rerun_priority",
                artifact="meshsafe_huygens_source_family_workpack",
                scope=source_family_scope,
                evidence_path=source_family_evidence,
                command=source_family_command,
                best_setting=source_family_best,
                status=source_family_status,
                trust_level=source_family_trust,
                sensor_count=source_family.get("probe_count_per_case"),
                interpretation=source_family_interpretation,
                next_action=source_family_next,
                blocker=source_family_blocker,
            )
        )
        if source_family_safe:
            planned_count = int(source_family_safe.get("planned_trial_count", 0) or 0)
            diagnostic_planned_count = int(source_family_safe.get("diagnostic_planned_trial_count", 0) or 0)
            supplemental_count = int(source_family_safe.get("supplemental_trial_count", 0) or 0)
            trial_count = int(source_family_safe.get("trial_count", 0) or 0)
            finished_count = int(source_family_safe.get("finished_count", 0) or 0)
            timed_out_count = int(source_family_safe.get("timed_out_count", 0) or 0)
            artifact_ready_count = int(source_family_safe.get("artifact_ready_count", 0) or 0)
            safe_status = str(source_family_safe.get("stage_status", ""))
            validation_best_variant = str(source_family_safe.get("validation_best_variant", ""))
            validation_best_status = str(source_family_safe.get("validation_best_status", ""))
            frozen_j96_status = str(source_family_safe.get("frozen_j96_status", ""))
            validation_corr = source_family_safe.get("validation_best_correlation", math.nan)
            validation_nmse = source_family_safe.get("validation_best_scaled_power_nmse", math.nan)
            validation_region_error = source_family_safe.get("validation_best_region_error_deg", math.nan)
            validation_jaccard = source_family_safe.get("validation_best_region_jaccard", math.nan)
            frozen_corr = source_family_safe.get("frozen_j96_correlation", math.nan)
            frozen_nmse = source_family_safe.get("frozen_j96_scaled_power_nmse", math.nan)
            if safe_status == "source_family_solver_safe_reduced_layout_validated":
                safe_trust = "validated_reduced_layout_cst_pilot"
                safe_interpretation = (
                    "The short x source-family case now has completed 96-point local E/H CST solver evidence, "
                    "ResultTree local E/H CSV exports, a CST FarfieldPlot far-field reference, a passed "
                    "real/frozen E/H Huygens validation, and a passed reduced-layout reconstruction gate. The "
                    "current CST work is therefore source-family generalization, not runtime repair."
                )
            elif safe_status == "source_family_solver_safe_matched_eh_validated":
                safe_trust = "validated_matched_eh_cst_pilot"
                safe_interpretation = (
                    "The short x source-family case now has completed 96-point local E/H CST solver evidence, "
                    "ResultTree local E/H CSV exports, a CST FarfieldPlot far-field reference, and a passed "
                    "real/frozen E/H Huygens region-shape validation. The remaining G3 work is no longer a CST "
                    "runtime blocker; it is reduced-layout and source-family generalization."
                )
            elif safe_status == "source_family_solver_safe_matched_eh_exported":
                safe_trust = "matched_eh_export_evidence_not_huygens_proof"
                safe_interpretation = (
                    "The short x source-family case now has completed 96-point local E/H CST solver evidence "
                    "and matching CSV/far-field exports. Frozen-rule electromagnetic validation is the only "
                    "remaining gate before calling the pilot closed."
                )
            elif safe_status == "source_family_solver_safe_matched_eh_finished":
                safe_trust = "matched_solver_evidence_not_huygens_proof"
                safe_interpretation = (
                    "The short x source-family case now has completed 96-point local E-field and H-field "
                    "solver evidence with near-field and far-field artifacts. This resolves the earlier "
                    "runtime gate for the pilot case, but frozen-rule validation still requires ResultTree "
                    "CSV export and comparison against the CST far-field reference."
                )
            elif trial_count:
                safe_trust = "solver_diagnostic_evidence_not_huygens_proof"
                safe_interpretation = (
                    "The source-family timeout is now being isolated with a staged CST diagnostic ladder. "
                    "Executed rows are runtime evidence only; frozen-rule electromagnetic validation still "
                    "requires export-ready matched local E/H CSVs and far-field references."
                )
            else:
                safe_trust = "solver_diagnostic_plan_not_physics_proof"
                safe_interpretation = (
                    "A solver-safe diagnostic ladder is ready for the blocked short x-oriented source-family "
                    "case: no-probe, efarfield96, efield24, hfield24, efield48, then full efield96. "
                    "This is a controlled execution plan, not a solved CST physics result."
                )
            rows.append(
                row(
                    category="rerun_priority",
                    artifact="meshsafe_huygens_source_family_solver_safe_pilot",
                    scope=(
                        f"{planned_count} tracked CST trial(s): {diagnostic_planned_count} solver-safe ladder "
                        f"and {supplemental_count} matched-field; {trial_count} executed; "
                        f"{finished_count} finished; {timed_out_count} timed out"
                    ),
                    evidence_path=source_family_safe_path,
                    command="python code\\build_cst_source_family_solver_safe_status.py",
                    best_setting=(
                        f"target={source_family_safe.get('target_sample_id', '')}; "
                        f"artifact_ready={artifact_ready_count}; "
                        "ladder=none->efarfield96->efield24->hfield24->efield48->efield96->hfield96; "
                        f"validation={validation_best_variant}/{validation_best_status}; "
                        f"frozen_j96={frozen_j96_status}; "
                        f"corr={format_float(validation_corr)}; "
                        f"scaled_nmse={format_float(validation_nmse)}; "
                        f"region_jaccard={format_float(validation_jaccard)}"
                    ),
                    status=safe_status,
                    trust_level=safe_trust,
                    sensor_count=source_family_safe.get("full_probe_row_count"),
                    min_correlation=validation_corr,
                    max_nmse=validation_nmse,
                    max_main_lobe_error_deg=validation_region_error,
                    interpretation=safe_interpretation,
                    next_action=str(source_family_safe.get("next_gate", "")),
                    blocker=(
                        ""
                        if safe_status
                        in (
                            "source_family_solver_safe_full_efield_finished",
                            "source_family_solver_safe_matched_eh_finished",
                            "source_family_solver_safe_matched_eh_exported",
                            "source_family_solver_safe_matched_eh_validated",
                            "source_family_solver_safe_reduced_layout_validated",
                        )
                        else "diagnostic ladder not yet complete"
                    ),
                )
            )
            if source_family_safe.get("reduced_layout_summary_exists", False):
                rows.append(
                    row(
                        category="trusted_sanity",
                        artifact="meshsafe_huygens_source_family_reduced_layout",
                        scope=(
                            f"{source_family_safe.get('reduced_layout_layout_count', 0)} reduced-layout rows on "
                            "the real short x CST matched E/H pilot; "
                            f"{source_family_safe.get('reduced_layout_deployable_frozen_accepted_count', 0)} "
                            "deployable frozen passes"
                        ),
                        evidence_path=source_family_reduced_layout_path,
                        command=str(source_family_safe.get("reduced_layout_command", "")),
                        best_setting=(
                            f"smallest={source_family_safe.get('reduced_layout_smallest_layout', '')}/"
                            f"{source_family_safe.get('reduced_layout_smallest_mode', '')}; "
                            f"sensors={source_family_safe.get('reduced_layout_smallest_sensor_count', '')}; "
                            f"degree={source_family_safe.get('reduced_layout_smallest_reconstruction_degree', '')}; "
                            f"direct_subset_accept="
                            f"{source_family_safe.get('reduced_layout_direct_subset_frozen_accepted_count', 0)}; "
                            f"reconstruct_accept="
                            f"{source_family_safe.get('reduced_layout_reconstructed_frozen_accepted_count', 0)}"
                        ),
                        status=str(source_family_safe.get("reduced_layout_status", "missing")),
                        trust_level="single_source_cst_sparse_reconstruction_gate",
                        sensor_count=source_family_safe.get("reduced_layout_smallest_sensor_count"),
                        min_correlation=source_family_safe.get(
                            "reduced_layout_smallest_frozen_correlation", math.nan
                        ),
                        max_nmse=source_family_safe.get(
                            "reduced_layout_smallest_frozen_scaled_power_nmse", math.nan
                        ),
                        max_main_lobe_error_deg=source_family_safe.get(
                            "reduced_layout_smallest_region_error_deg", math.nan
                        ),
                        interpretation=(
                            "The real short x CST E/H surface supports sparse sampling only when the selected "
                            "24/32/48/72 probes reconstruct the full local 96-node Huygens surface before the "
                            "frozen j96 propagation step. Direct quadrature thinning is retained as a failed "
                            "diagnostic, so the claim is sparse measurement plus reconstruction rather than "
                            "directly deleting surface cells."
                        ),
                        next_action=(
                            "Use geometry-only 24-point Fibonacci and farthest-point layouts as the current "
                            "candidate sampling plans, then repeat the same reconstruction/frozen-j96 gate on "
                            "y-oriented and off-axis CST source-family exports."
                        ),
                        blocker="single-source evidence until additional source-family orientations are exported",
                    )
                )
    else:
        rows.append(
            missing_row(
                "rerun_priority",
                "meshsafe_huygens_source_family_workpack",
                source_family_path,
                "python code\\prepare_cst_huygens_source_family_workpack.py",
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
    source_family_workpack_ready = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_workpack")
            & status["status"].isin(
                [
                    "source_family_workpack_ready",
                    "source_family_projects_generated",
                    "source_family_solver_pilot_timed_out",
                    "source_family_solver_partial_with_timeout",
                    "source_family_solver_partial",
                    "source_family_solver_completed",
                ]
            )
        ).any()
    )
    source_family_projects_generated = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_workpack")
            & status["status"].eq("source_family_projects_generated")
        ).any()
    )
    source_family_solver_timed_out = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_workpack")
            & status["status"].isin(["source_family_solver_pilot_timed_out", "source_family_solver_partial_with_timeout"])
        ).any()
    )
    source_family_safe_full_efield = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_solver_safe_pilot")
            & status["status"].eq("source_family_solver_safe_full_efield_finished")
        ).any()
    )
    source_family_safe_validated = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_solver_safe_pilot")
            & status["status"].eq("source_family_solver_safe_matched_eh_validated")
        ).any()
    )
    source_family_safe_reduced_validated = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_solver_safe_pilot")
            & status["status"].eq("source_family_solver_safe_reduced_layout_validated")
        ).any()
    )
    source_family_safe_exported = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_solver_safe_pilot")
            & status["status"].eq("source_family_solver_safe_matched_eh_exported")
        ).any()
    )
    source_family_safe_matched_eh = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_solver_safe_pilot")
            & status["status"].eq("source_family_solver_safe_matched_eh_finished")
        ).any()
    )
    if source_family_safe_reduced_validated:
        source_family_action = (
            "Run the same CST export, sparse reconstruction, and frozen eh_love_equivalence_minus_j96 Huygens gate "
            "on y-oriented and off-axis source-family cases. Keep the 24-point Fibonacci layout as the current "
            "deployment candidate, with farthest-point 24/32 layouts as robustness checks."
        )
        source_family_trigger = (
            "The short x solver-safe pilot now has completed matched E/H CST solves, exports, far-field reference "
            "validation, and a reduced-layout reconstruction pass down to 24 geometry-only probes."
        )
        source_family_blocker = ""
    elif source_family_safe_validated:
        source_family_action = (
            "Use the validated short x matched E/H pilot as the closed source-family seed: run reduced-layout "
            "subsets and additional x/y/off-axis source-family cases with the same frozen Huygens operator, without "
            "per-case retuning."
        )
        source_family_trigger = (
            "The short x solver-safe pilot now has completed matched E/H CST solves, ResultTree CSV exports, a CST "
            "far-field reference, and real/frozen E/H region-shape validation."
        )
        source_family_blocker = ""
    elif source_family_safe_exported:
        source_family_action = (
            "Evaluate the frozen eh_love_equivalence_minus_j96 Huygens rule on the exported short x matched E/H "
            "pilot, then update the source-family status before expanding to reduced layouts or additional cases."
        )
        source_family_trigger = (
            "The short x solver-safe pilot now has completed matched E/H CST solves and CSV/far-field exports; "
            "the remaining pilot gate is frozen-rule validation."
        )
        source_family_blocker = "frozen-rule Huygens validation not yet recorded"
    elif source_family_safe_matched_eh:
        source_family_action = (
            "Export matched local E/H CSVs and far-field references from the completed short x 96-point E/H pilot, "
            "then evaluate the frozen eh_love_equivalence_minus_j96 Huygens rule without retuning before expanding "
            "to the remaining source-family cases."
        )
        source_family_trigger = (
            "The short x solver-safe pilot now has completed full local E-field and H-field artifacts; "
            "the active gate is no longer runtime repair, but matched export and frozen-rule verification."
        )
        source_family_blocker = ""
    elif source_family_safe_full_efield:
        source_family_action = (
            "Run the matching long-window H-field pilot for the short x case, then export matched E/H and "
            "far-field references."
        )
        source_family_trigger = (
            "The full local E-field pilot completed cleanly; the remaining runtime check is the matching H-field pilot."
        )
        source_family_blocker = "matching 96-point H-field pilot not yet complete"
    elif source_family_solver_timed_out:
        source_family_action = (
            "Repair the CST source-family solver pilot before running the full 12-project queue: keep the short "
            "x-oriented case as the pilot, adjust CST time-domain settings or use a validated frequency-domain/fast-path "
            "variant, then export local E/H probes and far-field references."
        )
        source_family_trigger = (
            "The first real CST source-family solver pilot started and populated probe ResultTree entries, but the "
            "current time-domain setup timed out before export; the next proof step is solver-parameter repair, not "
            "blindly running all remaining cases."
        )
        source_family_blocker = "Current source-family CST time-domain solver settings timed out before export"
    else:
        source_family_action = (
            "Execute the CST source-family handoff in "
            "data\\cst_meshsafe_huygens_source_family_workpack\\next_source_family_commands.csv: generate E/H "
            "projects, solve the six x/y/off-axis cases, export local E/H probes, then test the frozen rule "
            "without per-source retuning."
        )
        if frozen_real_eh_needs_validation and rotation_covariance_ready and source_family_projects_generated:
            source_family_trigger = (
                "The frozen Huygens rule passes rotation-covariance and the source-family E/H CST projects have "
                "been generated; the next proof step is solve/export plus frozen-rule evaluation."
            )
        elif frozen_real_eh_needs_validation and rotation_covariance_ready and source_family_workpack_ready:
            source_family_trigger = (
                "The frozen Huygens rule passes rotation-covariance and the source-family workpack is ready; "
                "the next proof step is running those independent CST solves."
            )
        elif frozen_real_eh_needs_validation and rotation_covariance_ready:
            source_family_trigger = (
                "Mesh-safe real CST batch has a frozen real E/H candidate and the rotation-covariance gate passes; "
                "the remaining proof is independent CST source-family validation."
            )
        elif frozen_real_eh_needs_validation:
            source_family_trigger = (
                "Mesh-safe real CST batch now has a frozen real E/H candidate accepted by every current Level 1 case; "
                "it still needs a physics/geometry explanation and broader source-family validation."
            )
        elif real_eh_calibration_needed:
            source_family_trigger = (
                "Mesh-safe real CST batch gate now reaches strict/proxy status with real E/H currents, but the best "
                "J-scale/sign is source-dependent."
            )
        elif impedance_extension_needed:
            source_family_trigger = (
                "Mesh-safe real CST batch gate is region/proxy ready, but the stability gate still shows "
                "source-dependent impedance sensitivity."
            )
        else:
            source_family_trigger = (
                "Mesh-safe real CST batch gate is region/proxy ready and the impedance stability gate is available."
            )
        source_family_blocker = "" if meshsafe_ready and source_family_workpack_ready else "Mesh-safe batch gate or source-family workpack"
    actions = [
        {
            "priority": 1,
            "owner": "Independent workflow",
            "gate": "meshsafe_huygens_physics",
            "action": source_family_action,
            "trigger": source_family_trigger,
            "artifact": "data/cst_meshsafe_huygens_source_family_workpack/next_source_family_commands.csv and data/cst_exports/level1_meshsafe_huygens_source_family/*_local_[eh]field.csv",
            "proof_to_close": "Six automation-ready source-family rows have matched local E/H exports, far-field references, and the same sparse reconstruction plus frozen Huygens rule remains accepted without retuning.",
            "blocked_by": source_family_blocker,
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
    source_family_reduced_ready = bool(
        (
            status["artifact"].eq("meshsafe_huygens_source_family_reduced_layout")
            & status["status"].eq("reduced_layout_validated")
        ).any()
    )
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
    source_family_safe_rows = status.loc[status["artifact"] == "meshsafe_huygens_source_family_solver_safe_pilot"]
    if source_family_reduced_ready:
        lines.append(
            "- The short-x source-family CST pilot now passes the reduced-layout reconstruction gate; the active "
            "source-family task is y/off-axis expansion, not CST runtime repair."
        )
    elif not source_family_safe_rows.empty and str(source_family_safe_rows.iloc[0].get("status", "")) == "source_family_solver_safe_matched_eh_finished":
        lines.append(
            "- The short x source-family solver-safe pilot now has matched 96-point local E/H artifacts; the active "
            "CST gate is ResultTree CSV export plus frozen-rule validation, not solver-runtime repair."
        )
    elif not source_family_safe_rows.empty and str(source_family_safe_rows.iloc[0].get("status", "")) == "source_family_solver_safe_full_efield_finished":
        lines.append(
            "- The short x source-family solver-safe pilot has completed the full 96-point E-field row; the matching "
            "long-window H-field row remains the next CST runtime check."
        )
    source_family_rows = status.loc[status["artifact"] == "meshsafe_huygens_source_family_workpack"]
    if source_family_safe_rows.empty and not source_family_rows.empty and str(source_family_rows.iloc[0].get("status", "")) in (
        "source_family_solver_pilot_timed_out",
        "source_family_solver_partial_with_timeout",
    ):
        lines.append(
            "- The first independent CST source-family solver pilot started through the real CST API and populated "
            "probe ResultTree entries, but timed out before export; solver settings now need repair before the "
            "full queue is run."
        )
    elif not source_family_rows.empty and str(source_family_rows.iloc[0].get("status", "")) == "source_family_projects_generated":
        lines.append(
            "- The independent CST source-family workpack has generated all six E-field and six H-field CST projects; "
            "solve/export is now the active gate before frozen-rule validation."
        )
    elif not source_family_rows.empty and str(source_family_rows.iloc[0].get("status", "")) == "source_family_workpack_ready":
        lines.append(
            "- The independent CST source-family workpack is ready for execution: six x/y/off-axis cases are scripted, "
            "while tilted and multi-source rows remain explicit future gates."
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
