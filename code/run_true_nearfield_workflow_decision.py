from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_true_nearfield_workflow_decision"
DEFAULT_DROPZONE_SUMMARY = ROOT / "outputs" / "cst_true_nearfield_dropzone_check" / "true_nearfield_dropzone_summary.json"
DEFAULT_DROPZONE_STATUS = ROOT / "outputs" / "cst_true_nearfield_dropzone_check" / "true_nearfield_dropzone_status.csv"
DEFAULT_GATE_SUMMARY = ROOT / "data" / "cst_true_nearfield_workpack" / "gate_report" / "true_nearfield_gate_summary.json"
DEFAULT_GATE_STATUS = ROOT / "data" / "cst_true_nearfield_workpack" / "gate_report" / "true_nearfield_gate_status.csv"
DEFAULT_HANDOFF_SUMMARY = ROOT / "outputs" / "cst_true_nearfield_handoff" / "handoff_summary.json"
DEFAULT_EXPECTED_FILES = ROOT / "outputs" / "cst_true_nearfield_handoff" / "expected_true_monitor_files.csv"
DEFAULT_G3_SUMMARY = ROOT / "outputs" / "g3_model_dashboard" / "g3_dashboard_summary.json"

READY_FOR_GATE = "ready_for_gate"
BLOCKING_DROPZONE_STATUSES = {
    "invalid_contract",
    "read_error",
    "row_count_mismatch",
    "sample_id_mismatch",
    "frequency_mismatch",
    "sensor_subset_mismatch",
}
BLOCKING_GATE_STATUSES = {"row_count_mismatch", "pending_comparison"}


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: str | Path) -> str:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    try:
        return str(candidate.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(candidate)


def json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    normalized = frame.where(pd.notna(frame), None)
    return json.loads(normalized.to_json(orient="records", force_ascii=False))


def table_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame.columns:
        return {}
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).to_dict().items()}


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def required_expected_files(expected_files: pd.DataFrame, dropzone_status: pd.DataFrame) -> pd.DataFrame:
    if not expected_files.empty:
        work = expected_files.copy()
        if "case_priority" in work.columns:
            work = work[work["case_priority"].astype(str).str.strip().eq("required")]
        if "handoff_phase" in work.columns:
            phase = work["handoff_phase"].astype(str)
            phase_selected = work[phase.str.contains("required_full_grid", case=False, na=False)]
            if not phase_selected.empty:
                work = phase_selected
        if not work.empty:
            return work.sort_values(["sample_id", "target_export_path"], kind="stable")

    if dropzone_status.empty:
        return pd.DataFrame()
    if {"case_priority", "candidate", "target_export_path"}.difference(dropzone_status.columns):
        return pd.DataFrame()
    required = dropzone_status.copy()
    required = required[
        required["case_priority"].astype(str).str.strip().eq("required")
        & required["candidate"].astype(str).str.strip().eq("full_grid_162")
    ]
    if required.empty:
        return pd.DataFrame()
    expected = required.rename(columns={"target_export_path": "target_export_path"}).copy()
    return expected.sort_values(["sample_id", "target_export_path"], kind="stable")


def required_full_grid_dropzone(dropzone_status: pd.DataFrame) -> pd.DataFrame:
    if dropzone_status.empty:
        return pd.DataFrame()
    required_columns = {"case_priority", "candidate", "status"}
    if not required_columns.issubset(dropzone_status.columns):
        return pd.DataFrame()
    work = dropzone_status.copy()
    return work[
        work["case_priority"].astype(str).str.strip().eq("required")
        & work["candidate"].astype(str).str.strip().eq("full_grid_162")
    ].copy()


def required_gate_rows(gate_status: pd.DataFrame) -> pd.DataFrame:
    if gate_status.empty:
        return pd.DataFrame()
    required_columns = {"case_priority", "candidate", "gate_status"}
    if not required_columns.issubset(gate_status.columns):
        return pd.DataFrame()
    work = gate_status.copy()
    return work[
        work["case_priority"].astype(str).str.strip().eq("required")
        & work["candidate"].astype(str).str.strip().eq("full_grid_162")
    ].copy()


def build_required_status(
    expected_files: pd.DataFrame,
    dropzone_required: pd.DataFrame,
    gate_required: pd.DataFrame,
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    if expected_files.empty and dropzone_required.empty:
        return pd.DataFrame(records)

    by_sample_dropzone = {
        str(row.sample_id): row._asdict()
        for row in dropzone_required.itertuples(index=False)
        if hasattr(row, "sample_id")
    }
    by_sample_gate = {
        str(row.sample_id): row._asdict()
        for row in gate_required.itertuples(index=False)
        if hasattr(row, "sample_id")
    }

    source = expected_files if not expected_files.empty else dropzone_required
    for row in source.itertuples(index=False):
        item = row._asdict()
        sample_id = str(item.get("sample_id", ""))
        drop = by_sample_dropzone.get(sample_id, {})
        gate = by_sample_gate.get(sample_id, {})
        records.append(
            {
                "sample_id": sample_id,
                "case_priority": item.get("case_priority", drop.get("case_priority", "required")),
                "candidate": drop.get("candidate", "full_grid_162"),
                "target_export_path": item.get("target_export_path", drop.get("target_export_path", "")),
                "expected_export_rows": item.get("expected_export_rows", drop.get("expected_export_rows", "")),
                "target_export_exists": item.get("target_export_exists", drop.get("target_export_exists", "")),
                "dropzone_status": drop.get("status", "missing_dropzone_status"),
                "dropzone_errors": drop.get("errors", ""),
                "gate_status": gate.get("gate_status", "missing_gate_status"),
                "gate_source_status": gate.get("source_status", ""),
                "gate_row_count": gate.get("row_count", ""),
                "gate_comparison_status": gate.get("comparison_status", ""),
            }
        )
    return pd.DataFrame(records)


def infer_decision(
    handoff_summary: dict[str, Any],
    dropzone_summary: dict[str, Any],
    gate_summary: dict[str, Any],
    required_status: pd.DataFrame,
    gate_status: pd.DataFrame,
) -> dict[str, Any]:
    required_count = as_int(handoff_summary.get("required_full_grid_count"), 0)
    if required_count == 0:
        required_count = int(required_status.shape[0])

    ready_count = 0
    invalid_count = 0
    missing_count = 0
    if not required_status.empty and "dropzone_status" in required_status.columns:
        statuses = required_status["dropzone_status"].astype(str)
        ready_count = int(statuses.eq(READY_FOR_GATE).sum())
        missing_count = int(statuses.eq("missing_file").sum())
        invalid_count = int(statuses.isin(BLOCKING_DROPZONE_STATUSES).sum())

    required_ready = required_count > 0 and ready_count >= required_count

    if invalid_count > 0 or as_int(dropzone_summary.get("invalid_or_read_error_count")) > 0:
        return {
            "decision_id": "fix_cst_export_contract",
            "decision_label": "Fix CST export contract before algorithm gate",
            "blocker": f"{invalid_count} required full-grid export rows are invalid or unreadable.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "high",
        }

    if not required_ready:
        missing_note = missing_count if missing_count else max(required_count - ready_count, 0)
        return {
            "decision_id": "await_required_full_grid_exports",
            "decision_label": "Await required full-grid true-monitor exports",
            "blocker": f"{missing_note} required full-grid CST true-monitor CSV files are missing.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "high",
        }

    gate_required = required_gate_rows(gate_status)
    if gate_required.empty:
        return {
            "decision_id": "run_required_gate",
            "decision_label": "Run the required true-monitor comparison gate",
            "blocker": "Dropzone is ready, but the required gate report is missing.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "medium",
        }

    gate_statuses = gate_required["gate_status"].astype(str)
    if gate_statuses.eq("pending_source").any():
        return {
            "decision_id": "run_required_gate",
            "decision_label": "Run the required true-monitor comparison gate",
            "blocker": "Dropzone is ready, but the gate report still says pending_source.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "high",
        }

    if gate_statuses.isin(BLOCKING_GATE_STATUSES).any():
        return {
            "decision_id": "fix_gate_inputs",
            "decision_label": "Fix true-monitor gate inputs",
            "blocker": "The gate found row-count or comparison input problems.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "high",
        }

    if gate_statuses.eq("needs_physical_rerun").any():
        return {
            "decision_id": "rerun_physical_g3_baselines",
            "decision_label": "Rerun physical G3 baselines on true-monitor data",
            "blocker": "True-monitor exports differ materially from the FarfieldPlot-derived reference.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "high",
        }

    required_layouts = gate_status.copy()
    if not required_layouts.empty and {"case_priority", "gate_status"}.issubset(required_layouts.columns):
        required_layouts = required_layouts[required_layouts["case_priority"].astype(str).str.strip().eq("required")]
        if not required_layouts.empty and required_layouts["gate_status"].astype(str).eq("reference_match").all():
            return {
                "decision_id": "refresh_dashboard_and_report",
                "decision_label": "Refresh dashboard and report wording",
                "blocker": "",
                "required_full_grid_ready": ready_count,
                "required_full_grid_count": required_count,
                "confidence": "medium",
            }

    if gate_statuses.eq("reference_match").all():
        return {
            "decision_id": "derive_and_compare_reduced_layouts",
            "decision_label": "Derive and compare required reduced layouts",
            "blocker": "Required full-grid rows match; reduced 32/120 layouts still need gate evidence.",
            "required_full_grid_ready": ready_count,
            "required_full_grid_count": required_count,
            "confidence": "medium",
        }

    return {
        "decision_id": "inspect_gate_report",
        "decision_label": "Inspect the true-monitor gate report",
        "blocker": "Gate status is mixed or not covered by the automated decision rules.",
        "required_full_grid_ready": ready_count,
        "required_full_grid_count": required_count,
        "confidence": "medium",
    }


def commands_for_decision(decision_id: str) -> pd.DataFrame:
    common_regenerate = {
        "priority": 99,
        "owner": "Algorithm operator",
        "stage": "decision_refresh",
        "command": "python code\\run_true_nearfield_workflow_decision.py",
        "expected_result": "Refresh this decision report after the upstream action finishes.",
        "blocked_by": "",
    }
    command_sets: dict[str, list[dict[str, Any]]] = {
        "await_required_full_grid_exports": [
            {
                "priority": 1,
                "owner": "CST operator",
                "stage": "manual_cst_export",
                "command": "export the two required full_grid_162 true-monitor CSV files listed in this report",
                "expected_result": "The required target CSV paths exist with 486 rows each and Ex/Ey/Ez component rows.",
                "blocked_by": "CST true near-field monitor export",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "dropzone_preflight",
                "command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
                "expected_result": "Required full-grid rows become ready_for_gate.",
                "blocked_by": "required true-monitor CSV files",
            },
            {
                "priority": 3,
                "owner": "Algorithm operator",
                "stage": "required_gate",
                "command": "python code\\run_true_nearfield_gate.py --required-only",
                "expected_result": "Required rows leave pending_source and produce comparison status.",
                "blocked_by": "ready_for_gate dropzone status",
            },
        ],
        "fix_cst_export_contract": [
            {
                "priority": 1,
                "owner": "CST operator",
                "stage": "contract_fix",
                "command": "repair the CSV columns, frequency, sample_id, sensor subset, and 486-row full-grid contract",
                "expected_result": "Dropzone preflight has no invalid_contract, read_error, or row_count_mismatch rows.",
                "blocked_by": "invalid CST export file",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "dropzone_preflight",
                "command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
                "expected_result": "Required full-grid rows become ready_for_gate.",
                "blocked_by": "fixed CST export file",
            },
        ],
        "run_required_gate": [
            {
                "priority": 1,
                "owner": "Algorithm operator",
                "stage": "dropzone_preflight",
                "command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
                "expected_result": "Confirm required full-grid rows are still ready_for_gate.",
                "blocked_by": "",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "required_gate",
                "command": "python code\\run_true_nearfield_gate.py --required-only",
                "expected_result": "Gate report classifies required rows as reference_match, needs_physical_rerun, or input-fix status.",
                "blocked_by": "",
            },
        ],
        "fix_gate_inputs": [
            {
                "priority": 1,
                "owner": "Algorithm operator",
                "stage": "gate_input_fix",
                "command": "inspect data\\cst_true_nearfield_workpack\\gate_report\\true_nearfield_gate_status.csv",
                "expected_result": "Identify row-count, reference, or comparison input issue.",
                "blocked_by": "mixed gate status",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "required_gate",
                "command": "python code\\run_true_nearfield_gate.py --required-only",
                "expected_result": "Gate input status clears.",
                "blocked_by": "fixed gate inputs",
            },
        ],
        "rerun_physical_g3_baselines": [
            {
                "priority": 1,
                "owner": "Algorithm operator",
                "stage": "physical_baseline",
                "command": "rerun source-model, SWE, reduced-layout, and Huygens diagnostics on authoritative true-monitor input",
                "expected_result": "A physical full-grid baseline reaches strict_pass or an approved near-pass.",
                "blocked_by": "true-monitor mismatch",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "dashboard_refresh",
                "command": "python code\\build_g3_model_dashboard.py",
                "expected_result": "G3 dashboard reflects the true-monitor rerun evidence.",
                "blocked_by": "rerun metrics",
            },
        ],
        "derive_and_compare_reduced_layouts": [
            {
                "priority": 1,
                "owner": "Algorithm operator",
                "stage": "required_reduced_gate",
                "command": "python code\\run_true_nearfield_gate.py --required-only",
                "expected_result": "Gate derives and compares geometric_farthest_32 and fibonacci_snap_120 for required cases.",
                "blocked_by": "",
            },
            {
                "priority": 2,
                "owner": "Algorithm operator",
                "stage": "dashboard_refresh",
                "command": "python code\\build_g3_model_dashboard.py",
                "expected_result": "G3 dashboard records reduced-layout true-monitor status.",
                "blocked_by": "",
            },
        ],
        "refresh_dashboard_and_report": [
            {
                "priority": 1,
                "owner": "Algorithm operator",
                "stage": "dashboard_refresh",
                "command": "python code\\build_g3_model_dashboard.py",
                "expected_result": "Dashboard and next actions reflect the closed true-monitor gate.",
                "blocked_by": "",
            },
            {
                "priority": 2,
                "owner": "Report/PPT operator",
                "stage": "wording_refresh",
                "command": "update report wording using true-monitor gate evidence, without overstating reduced-layout proof",
                "expected_result": "Report claims are tied to physical gate status.",
                "blocked_by": "",
            },
        ],
    }
    rows = command_sets.get(decision_id, [])
    rows.append(common_regenerate)
    return pd.DataFrame(rows).sort_values("priority", kind="stable")


def write_markdown(
    out_dir: Path,
    decision: dict[str, Any],
    summary: dict[str, Any],
    required_status: pd.DataFrame,
    commands: pd.DataFrame,
) -> None:
    lines: list[str] = [
        "# CST True Near-Field Workflow Decision",
        "",
        "This report is generated by:",
        "",
        "```powershell",
        "python code\\run_true_nearfield_workflow_decision.py",
        "```",
        "",
        "It reads the handoff, dropzone, true-monitor gate, and G3 dashboard status.",
        "It does not create CST data and does not convert FarfieldPlot-derived samples into physical evidence.",
        "",
        "## Executive Decision",
        "",
        f"- Decision: `{decision['decision_id']}`",
        f"- Label: {decision['decision_label']}",
        f"- Confidence: {decision['confidence']}",
        f"- Required full-grid ready: {decision['required_full_grid_ready']}/{decision['required_full_grid_count']}",
        f"- Blocker: {decision['blocker'] or 'none'}",
        "",
        "## Current Counts",
        "",
        f"- Dropzone status counts: `{summary['dropzone_status_counts']}`",
        f"- Gate status counts: `{summary['gate_status_counts']}`",
        f"- G3 dashboard true-monitor status: `{summary['g3_true_monitor_status']}`",
        "",
        "## Required Full-Grid Files",
        "",
        "| Sample | Target CSV | Expected rows | Dropzone | Gate |",
        "|---|---|---:|---|---|",
    ]
    if required_status.empty:
        lines.append("| missing | missing |  | missing | missing |")
    else:
        for row in required_status.itertuples(index=False):
            lines.append(
                f"| {row.sample_id} | `{row.target_export_path}` | {row.expected_export_rows} | "
                f"{row.dropzone_status} | {row.gate_status} |"
            )

    lines.extend(
        [
            "",
            "## Next Commands",
            "",
            "| Priority | Owner | Stage | Command | Expected result | Blocked by |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in commands.itertuples(index=False):
        lines.append(
            f"| {row.priority} | {row.owner} | {row.stage} | `{row.command}` | "
            f"{row.expected_result} | {row.blocked_by} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- Keep `geometric_farthest_32` as a true-monitor rerun priority, not a final reduced-sampling proof.",
            "- Do not write report-level reduced-layout claims until required full-grid true-monitor evidence and a physical/vector baseline pass the gate.",
            "- If true-monitor data disagrees with the FarfieldPlot-derived reference, rerun the G3 physical baselines before refreshing report wording.",
            "",
        ]
    )
    (out_dir / "true_nearfield_workflow_decision.md").write_text("\n".join(lines), encoding="utf-8")


def build_summary(
    args: argparse.Namespace,
    decision: dict[str, Any],
    required_status: pd.DataFrame,
    commands: pd.DataFrame,
    dropzone_status: pd.DataFrame,
    gate_status: pd.DataFrame,
    g3_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_by": "code/run_true_nearfield_workflow_decision.py",
        "decision_id": decision["decision_id"],
        "decision_label": decision["decision_label"],
        "blocker": decision["blocker"],
        "confidence": decision["confidence"],
        "required_full_grid_ready": int(decision["required_full_grid_ready"]),
        "required_full_grid_count": int(decision["required_full_grid_count"]),
        "dropzone_status_counts": table_counts(dropzone_status, "status"),
        "gate_status_counts": table_counts(gate_status, "gate_status"),
        "g3_true_monitor_status": str(g3_summary.get("true_monitor_status", "missing")),
        "inputs": {
            "dropzone_summary": rel(args.dropzone_summary),
            "dropzone_status": rel(args.dropzone_status),
            "gate_summary": rel(args.gate_summary),
            "gate_status": rel(args.gate_status),
            "handoff_summary": rel(args.handoff_summary),
            "expected_files": rel(args.expected_files),
            "g3_summary": rel(args.g3_summary),
        },
        "output_files": {
            "decision_markdown": "outputs\\cst_true_nearfield_workflow_decision\\true_nearfield_workflow_decision.md",
            "summary": "outputs\\cst_true_nearfield_workflow_decision\\workflow_decision_summary.json",
            "next_commands": "outputs\\cst_true_nearfield_workflow_decision\\workflow_next_commands.csv",
            "required_status": "outputs\\cst_true_nearfield_workflow_decision\\required_full_grid_status.csv",
        },
        "required_status_records": json_records(required_status),
        "next_command_records": json_records(commands),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decide the next step after CST true near-field monitor export.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--dropzone-summary", type=Path, default=DEFAULT_DROPZONE_SUMMARY)
    parser.add_argument("--dropzone-status", type=Path, default=DEFAULT_DROPZONE_STATUS)
    parser.add_argument("--gate-summary", type=Path, default=DEFAULT_GATE_SUMMARY)
    parser.add_argument("--gate-status", type=Path, default=DEFAULT_GATE_STATUS)
    parser.add_argument("--handoff-summary", type=Path, default=DEFAULT_HANDOFF_SUMMARY)
    parser.add_argument("--expected-files", type=Path, default=DEFAULT_EXPECTED_FILES)
    parser.add_argument("--g3-summary", type=Path, default=DEFAULT_G3_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dropzone_summary = read_json(args.dropzone_summary)
    gate_summary = read_json(args.gate_summary)
    handoff_summary = read_json(args.handoff_summary)
    g3_summary = read_json(args.g3_summary)
    dropzone_status = read_csv(args.dropzone_status)
    gate_status = read_csv(args.gate_status)
    expected_files = read_csv(args.expected_files)

    dropzone_required = required_full_grid_dropzone(dropzone_status)
    gate_required = required_gate_rows(gate_status)
    required_files = required_expected_files(expected_files, dropzone_status)
    required_status = build_required_status(required_files, dropzone_required, gate_required)
    decision = infer_decision(handoff_summary, dropzone_summary, gate_summary, required_status, gate_status)
    commands = commands_for_decision(str(decision["decision_id"]))
    summary = build_summary(args, decision, required_status, commands, dropzone_status, gate_status, g3_summary)

    required_status.to_csv(out_dir / "required_full_grid_status.csv", index=False, encoding="utf-8-sig")
    commands.to_csv(out_dir / "workflow_next_commands.csv", index=False, encoding="utf-8-sig")
    (out_dir / "workflow_decision_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(out_dir, decision, summary, required_status, commands)

    print(f"true near-field workflow decision written to {rel(out_dir)}")
    print(f"decision: {decision['decision_id']}")
    print(f"required full-grid ready: {decision['required_full_grid_ready']}/{decision['required_full_grid_count']}")
    if decision["blocker"]:
        print(f"blocker: {decision['blocker']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
