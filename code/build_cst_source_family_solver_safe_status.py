from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN_DIR = ROOT / "data" / "cst_meshsafe_huygens_source_family_solver_safe_pilot"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_meshsafe_huygens_source_family_solver_safe_status"
FINISHED_STATUSES = {"finished", "aborted_keeping_results"}
TIMEOUT_STATUSES = {"timed_out", "controller_timeout"}
TARGET_SAMPLE_ID = "L1_short_dipole_x_1p2G"
SOURCE_FAMILY_EXPORT_DIR = ROOT / "data" / "cst_exports" / "level1_meshsafe_huygens_source_family"
MATCHED_EH_VALIDATION_DIR = (
    ROOT / "data" / "sampling_layouts" / "cst_meshsafe_huygens_source_family_matched_eh_x"
)
VALIDATION_PASS_STATUSES = {"strict_pass", "physics_proxy_pass", "region_shape_pass"}
SUPPLEMENTAL_TRIAL_ROWS = [
    {
        "execution_order": "7",
        "ladder_id": "hfield96",
        "sample_id": "L1_short_dipole_x_1p2G",
        "probe_mode": "hfield",
        "probe_rows": "96",
        "timeout_seconds": "5400",
        "summary_out": (
            "outputs/cst_solver_trials/meshsafe_huygens_source_family_solver_safe/"
            "L1_short_dipole_x_1p2G_hfield96_solver_summary.json"
        ),
        "generate_command": (
            "python code\\run_cst_level1_required_automation.py --level1-csv "
            "data\\cst_meshsafe_huygens_source_family_solver_safe_pilot\\solver_safe_pilot_case.csv "
            "--probe-csv data\\cst_meshsafe_huygens_source_family_solver_safe_pilot\\solver_safe_probe_96.csv "
            "--out-dir C:\\csttmp\\huy_sf_safe_hfield96 --probe-mode hfield --timeout-seconds 900"
        ),
        "solve_command": (
            "python code\\run_cst_solver_project.py --project "
            "C:\\csttmp\\huy_sf_safe_hfield96\\projects\\CST_L1_short_dipole_x_1p2G_meshsafe_huygens_r0p35.cst "
            "--out-dir C:\\csttmp\\huy_sf_safe_hfield96_s --trial-name L1_short_dipole_x_1p2G_hfield96.cst "
            "--summary-out outputs\\cst_solver_trials\\meshsafe_huygens_source_family_solver_safe\\"
            "L1_short_dipole_x_1p2G_hfield96_solver_summary.json "
            "--stdout-log outputs\\cst_solver_trials\\meshsafe_huygens_source_family_solver_safe\\"
            "L1_short_dipole_x_1p2G_hfield96_stdout.log --timeout-seconds 5400 --poll-seconds 10"
        ),
        "gate_interpretation": "matching full local H-field pilot for the completed efield96 row",
    }
]


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    number = as_float(value)
    if number is None:
        return None
    return int(number)


def resolve_repo_path(text: str) -> Path:
    path = Path(text)
    if path.is_absolute():
        return path
    return ROOT / path


def summarize_export_validation(sample_id: str) -> dict[str, Any]:
    efield_path = (
        SOURCE_FAMILY_EXPORT_DIR
        / f"{sample_id}_level1_local_sphere_r0p35_local_efield.csv"
    )
    hfield_path = (
        SOURCE_FAMILY_EXPORT_DIR
        / f"{sample_id}_level1_local_sphere_r0p35_local_hfield.csv"
    )
    farfield_path = SOURCE_FAMILY_EXPORT_DIR / f"{sample_id}_farfield.csv"
    farfieldplot_nearfield_path = SOURCE_FAMILY_EXPORT_DIR / f"{sample_id}_farfieldplot_13m_nearfield.csv"
    validation_summary_path = MATCHED_EH_VALIDATION_DIR / "meshsafe_huygens_extrapolation_summary.json"
    validation_results_path = MATCHED_EH_VALIDATION_DIR / "meshsafe_huygens_extrapolation_results.csv"
    field_quality_path = MATCHED_EH_VALIDATION_DIR / "meshsafe_huygens_field_quality.csv"
    validation_summary = read_json(validation_summary_path)
    best = validation_summary.get("best_setting", {}) if validation_summary else {}
    if not isinstance(best, dict):
        best = {}
    result_rows = read_csv_rows(validation_results_path)
    frozen_j96 = next(
        (row for row in result_rows if row.get("variant") == "eh_love_equivalence_minus_j96"),
        {},
    )
    efield_rows = csv_row_count(efield_path)
    hfield_rows = csv_row_count(hfield_path)
    farfield_rows = csv_row_count(farfield_path)
    farfieldplot_nearfield_rows = csv_row_count(farfieldplot_nearfield_path)
    export_ready = efield_rows == 288 and hfield_rows == 288 and farfield_rows > 0
    best_status = str(best.get("status", ""))
    frozen_status = str(frozen_j96.get("status", ""))
    validation_ready = bool(
        export_ready
        and validation_summary
        and validation_summary.get("hfield_available", False)
        and best_status in VALIDATION_PASS_STATUSES
        and frozen_status in VALIDATION_PASS_STATUSES
    )
    return {
        "sample_id": sample_id,
        "efield_export_path": display_path(efield_path),
        "hfield_export_path": display_path(hfield_path),
        "farfield_export_path": display_path(farfield_path),
        "farfieldplot_nearfield_path": display_path(farfieldplot_nearfield_path),
        "validation_summary_path": display_path(validation_summary_path),
        "validation_results_path": display_path(validation_results_path),
        "field_quality_path": display_path(field_quality_path),
        "efield_export_exists": efield_path.exists(),
        "hfield_export_exists": hfield_path.exists(),
        "farfield_export_exists": farfield_path.exists(),
        "farfieldplot_nearfield_exists": farfieldplot_nearfield_path.exists(),
        "validation_summary_exists": validation_summary_path.exists(),
        "validation_results_exists": validation_results_path.exists(),
        "field_quality_exists": field_quality_path.exists(),
        "efield_export_rows": efield_rows,
        "hfield_export_rows": hfield_rows,
        "farfield_export_rows": farfield_rows,
        "farfieldplot_nearfield_rows": farfieldplot_nearfield_rows,
        "export_ready": export_ready,
        "validation_ready": validation_ready,
        "validation_hfield_available": bool(validation_summary.get("hfield_available", False))
        if validation_summary
        else False,
        "validation_best_variant": str(best.get("variant", "")),
        "validation_best_status": best_status,
        "validation_best_correlation": as_float(best.get("correlation")),
        "validation_best_scaled_power_nmse": as_float(best.get("scaled_power_nmse")),
        "validation_best_nmse": as_float(best.get("nmse")),
        "validation_best_region_error_deg": as_float(best.get("main_lobe_region_error_deg")),
        "validation_best_region_jaccard": as_float(best.get("main_lobe_region_jaccard")),
        "validation_best_capture": as_float(best.get("reference_lobe_region_capture")),
        "validation_best_precision": as_float(best.get("predicted_lobe_region_precision")),
        "frozen_j96_variant": str(frozen_j96.get("variant", "")),
        "frozen_j96_status": frozen_status,
        "frozen_j96_correlation": as_float(frozen_j96.get("correlation")),
        "frozen_j96_scaled_power_nmse": as_float(frozen_j96.get("scaled_power_nmse")),
        "frozen_j96_nmse": as_float(frozen_j96.get("nmse")),
        "frozen_j96_region_error_deg": as_float(frozen_j96.get("main_lobe_region_error_deg")),
        "frozen_j96_region_jaccard": as_float(frozen_j96.get("main_lobe_region_jaccard")),
        "frozen_j96_capture": as_float(frozen_j96.get("reference_lobe_region_capture")),
        "frozen_j96_precision": as_float(frozen_j96.get("predicted_lobe_region_precision")),
    }


def summarize_trial(plan_row: dict[str, str]) -> dict[str, Any]:
    summary_path = resolve_repo_path(plan_row.get("summary_out", ""))
    summary = read_json(summary_path)
    solver_logs = summary.get("solver_logs", {}) if summary else {}
    artifacts = solver_logs.get("result_artifacts", {}) if summary else {}
    solver_start = summary.get("solver_start_result", {}) if summary else {}
    return {
        "execution_order": plan_row.get("execution_order", ""),
        "ladder_id": plan_row.get("ladder_id", ""),
        "sample_id": plan_row.get("sample_id", ""),
        "probe_mode": plan_row.get("probe_mode", ""),
        "probe_rows": plan_row.get("probe_rows", ""),
        "planned_timeout_seconds": plan_row.get("timeout_seconds", ""),
        "actual_timeout_seconds": as_int(summary.get("timeout_seconds")) if summary else None,
        "summary_path": display_path(summary_path),
        "summary_exists": summary_path.exists(),
        "status": str(summary.get("status", "not_run")) if summary else "not_run",
        "checkpoint": str(summary.get("checkpoint", "")) if summary else "",
        "real_cst_api_used": bool(summary.get("real_cst_api_used", False)) if summary else False,
        "solver_start_ok": bool(solver_start.get("ok", False) and solver_start.get("value", False)),
        "elapsed_seconds": as_float(summary.get("elapsed_seconds")) if summary else None,
        "result_tree_count_after": as_int(summary.get("result_tree_count_after")) if summary else None,
        "artifact_count": as_int(artifacts.get("artifact_count")) if artifacts else 0,
        "has_nearfield_artifact": bool(artifacts.get("has_nearfield_artifact", False)),
        "has_farfield_artifact": bool(artifacts.get("has_farfield_artifact", False)),
        "aborted_keeping_results_detected": bool(solver_logs.get("aborted_keeping_results_detected", False)),
        "generate_command": plan_row.get("generate_command", ""),
        "solve_command": plan_row.get("solve_command", ""),
        "gate_interpretation": plan_row.get("gate_interpretation", ""),
    }


def determine_stage(plan_exists: bool, rows: list[dict[str, Any]]) -> str:
    if not plan_exists:
        return "source_family_solver_safe_plan_missing"
    if not rows or not any(row["summary_exists"] for row in rows):
        return "source_family_solver_safe_pilot_plan_ready"
    finished = [row for row in rows if row["status"] in FINISHED_STATUSES]
    timed_out = [row for row in rows if row["status"] in TIMEOUT_STATUSES]
    full_finished = any(row["ladder_id"] == "efield96" and row["status"] in FINISHED_STATUSES for row in rows)
    matched_hfield_finished = any(
        row["ladder_id"] == "hfield96"
        and row["status"] in FINISHED_STATUSES
        and row["has_nearfield_artifact"]
        and row["has_farfield_artifact"]
        for row in rows
    )
    all_run = all(row["summary_exists"] for row in rows)
    if full_finished and matched_hfield_finished:
        return "source_family_solver_safe_matched_eh_finished"
    if full_finished:
        return "source_family_solver_safe_full_efield_finished"
    if finished and all_run and not timed_out:
        return "source_family_solver_safe_ladder_completed"
    if finished:
        return "source_family_solver_safe_ladder_partial"
    if timed_out:
        return "source_family_solver_safe_trials_timed_out"
    return "source_family_solver_safe_trials_started"


def write_markdown(path: Path, summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# CST source-family solver-safe status",
        "",
        "This report summarizes the diagnostic ladder created for the first source-family CST solver timeout.",
        "",
        "## Status",
        "",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Tracked trials: `{summary['planned_trial_count']}`",
        f"- Solver-safe ladder trials: `{summary['diagnostic_planned_trial_count']}`",
        f"- Supplemental matched-field trials: `{summary['supplemental_trial_count']}`",
        f"- Executed trials: `{summary['trial_count']}`",
        f"- Finished trials: `{summary['finished_count']}`",
        f"- Timed-out trials: `{summary['timed_out_count']}`",
        f"- Matched E/H ready: `{summary['matched_eh_ready']}`",
        f"- Matched E/H export ready: `{summary['matched_eh_export_ready']}`",
        f"- Matched E/H Huygens validation ready: `{summary['matched_eh_validation_ready']}`",
        "",
        "## Export and Huygens gate",
        "",
        f"- E-field CSV rows: `{summary['efield_export_rows']}` ({summary['efield_export_path']})",
        f"- H-field CSV rows: `{summary['hfield_export_rows']}` ({summary['hfield_export_path']})",
        f"- Far-field CSV rows: `{summary['farfield_export_rows']}` ({summary['farfield_export_path']})",
        (
            "- Best real E/H validation: "
            f"`{summary['validation_best_variant']}` / `{summary['validation_best_status']}`, "
            f"corr `{summary['validation_best_correlation']}`, "
            f"scaled NMSE `{summary['validation_best_scaled_power_nmse']}`, "
            f"region error deg `{summary['validation_best_region_error_deg']}`, "
            f"region Jaccard `{summary['validation_best_region_jaccard']}`"
        ),
        (
            "- Frozen j96 validation: "
            f"`{summary['frozen_j96_variant']}` / `{summary['frozen_j96_status']}`, "
            f"corr `{summary['frozen_j96_correlation']}`, "
            f"scaled NMSE `{summary['frozen_j96_scaled_power_nmse']}`, "
            f"region error deg `{summary['frozen_j96_region_error_deg']}`, "
            f"region Jaccard `{summary['frozen_j96_region_jaccard']}`"
        ),
        "",
        "## Trial rows",
        "",
        "| Order | Ladder | Mode | Probes | Timeout / s | Status | Elapsed / s | Artifacts | Abort warn |",
        "|---:|---|---|---:|---:|---|---:|---:|---|",
    ]
    for row in rows:
        elapsed = "" if row["elapsed_seconds"] is None else f"{float(row['elapsed_seconds']):.1f}"
        timeout_seconds = row["actual_timeout_seconds"] or row["planned_timeout_seconds"]
        abort_warn = "yes" if row["aborted_keeping_results_detected"] else ""
        lines.append(
            f"| {row['execution_order']} | `{row['ladder_id']}` | `{row['probe_mode']}` | "
            f"{row['probe_rows']} | {timeout_seconds} | `{row['status']}` | {elapsed} | "
            f"{row['artifact_count']} | {abort_warn} |"
        )
    lines.extend(["", "## Next command", ""])
    if summary.get("next_ladder_id"):
        lines.extend(
            [
                f"Next diagnostic row: `{summary['next_ladder_id']}`.",
                "",
                "```powershell",
                str(summary.get("next_generate_command", "")),
                str(summary.get("next_solve_command", "")),
                "python code\\build_cst_source_family_solver_safe_status.py",
                "python code\\build_g3_model_dashboard.py",
                "```",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "All planned diagnostic rows have a trial summary.",
                "",
                f"Next gate: {summary.get('next_gate', '')}.",
                "",
                "```powershell",
                "python code\\build_cst_source_family_solver_safe_status.py",
                "python code\\build_g3_model_dashboard.py",
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_status(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan_dir = Path(args.plan_dir)
    plan_summary_path = plan_dir / "solver_safe_pilot_plan_summary.json"
    commands_path = plan_dir / "solver_safe_pilot_commands.csv"
    plan_summary = read_json(plan_summary_path)
    plan_rows = read_csv_rows(commands_path)
    supplemental_rows = [dict(row) for row in SUPPLEMENTAL_TRIAL_ROWS]
    trial_rows = [summarize_trial(row) for row in plan_rows + supplemental_rows]
    stage_status = determine_stage(plan_summary_path.exists(), trial_rows)
    sample_id = str(plan_summary.get("target_sample_id", "")) or TARGET_SAMPLE_ID
    export_validation = summarize_export_validation(sample_id)
    if stage_status == "source_family_solver_safe_matched_eh_finished":
        if export_validation["validation_ready"]:
            stage_status = "source_family_solver_safe_matched_eh_validated"
        elif export_validation["export_ready"]:
            stage_status = "source_family_solver_safe_matched_eh_exported"
    trial_count = sum(1 for row in trial_rows if row["summary_exists"])
    next_row = next((row for row in trial_rows if not row["summary_exists"]), None)
    if next_row:
        next_gate = (
            f"run next diagnostic row {next_row['ladder_id']}: generate the CST project, solve it, "
            "then rebuild solver-safe status and the G3 dashboard"
        )
        next_ladder_id = next_row["ladder_id"]
        next_generate_command = next_row["generate_command"]
        next_solve_command = next_row["solve_command"]
    else:
        if stage_status == "source_family_solver_safe_matched_eh_validated":
            next_gate = (
                "short x source-family pilot has completed matched 96-point local E/H CST solves, "
                "ResultTree CSV export, CST far-field reference export, and real/frozen E/H Huygens "
                "region-shape validation; next expand to reduced layouts and additional source-family "
                "cases without retuning the frozen operator"
            )
        elif stage_status == "source_family_solver_safe_matched_eh_exported":
            next_gate = (
                "matched local E/H CSVs and the CST far-field reference are exported for the short x case; "
                "next run the frozen Huygens validation and update the dashboard"
            )
        elif stage_status == "source_family_solver_safe_matched_eh_finished":
            next_gate = (
                "matched 96-point local E/H probe solves are now runtime-feasible on the short x case; "
                "next export matched local E/H CSVs and far-field references, then apply the frozen "
                "eh_love_equivalence_minus_j96 Huygens rule without retuning"
            )
        else:
            next_gate = (
                "full local E-field probe solve is now runtime-feasible on the short x case; "
                "next run a matching long-window H-field pilot for the same sample, then export matched E/H and far-field "
                "references before applying the frozen Huygens rule"
            )
        next_ladder_id = ""
        next_generate_command = ""
        next_solve_command = ""
    matched_eh_ready = stage_status in (
        "source_family_solver_safe_matched_eh_finished",
        "source_family_solver_safe_matched_eh_exported",
        "source_family_solver_safe_matched_eh_validated",
    )
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stage_status": stage_status,
        "plan_summary_path": display_path(plan_summary_path),
        "commands_path": display_path(commands_path),
        "plan_exists": plan_summary_path.exists(),
        "target_sample_id": plan_summary.get("target_sample_id", ""),
        "full_probe_row_count": plan_summary.get("full_probe_row_count", ""),
        "planned_trial_count": len(trial_rows),
        "diagnostic_planned_trial_count": len(plan_rows),
        "supplemental_trial_count": len(supplemental_rows),
        "trial_count": trial_count,
        "finished_count": sum(1 for row in trial_rows if row["status"] in FINISHED_STATUSES),
        "timed_out_count": sum(1 for row in trial_rows if row["status"] in TIMEOUT_STATUSES),
        "solver_start_ok_count": sum(1 for row in trial_rows if row["solver_start_ok"]),
        "artifact_ready_count": sum(
            1 for row in trial_rows if row["has_nearfield_artifact"] or row["has_farfield_artifact"]
        ),
        "abort_warning_count": sum(1 for row in trial_rows if row["aborted_keeping_results_detected"]),
        "next_gate": next_gate,
        "next_ladder_id": next_ladder_id,
        "next_generate_command": next_generate_command,
        "next_solve_command": next_solve_command,
        "matched_eh_ready": matched_eh_ready,
        "matched_eh_export_ready": bool(export_validation["export_ready"]),
        "matched_eh_validation_ready": bool(export_validation["validation_ready"]),
        **export_validation,
        "trials": trial_rows,
    }
    return summary, trial_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize CST source-family solver-safe ladder status.")
    parser.add_argument("--plan-dir", type=Path, default=DEFAULT_PLAN_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary, rows = build_status(args)
    (out_dir / "solver_safe_status_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(
        out_dir / "solver_safe_trial_status.csv",
        rows,
        [
            "execution_order",
            "ladder_id",
            "sample_id",
            "probe_mode",
            "probe_rows",
            "planned_timeout_seconds",
            "actual_timeout_seconds",
            "summary_path",
            "summary_exists",
            "status",
            "checkpoint",
            "real_cst_api_used",
            "solver_start_ok",
            "elapsed_seconds",
            "result_tree_count_after",
            "artifact_count",
            "has_nearfield_artifact",
            "has_farfield_artifact",
            "aborted_keeping_results_detected",
            "generate_command",
            "solve_command",
            "gate_interpretation",
        ],
    )
    write_markdown(out_dir / "solver_safe_status.md", summary, rows)
    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "out_dir": display_path(out_dir),
                "planned_trial_count": summary["planned_trial_count"],
                "trial_count": summary["trial_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
