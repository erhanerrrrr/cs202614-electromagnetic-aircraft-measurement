from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKPACK = ROOT / "data" / "cst_true_nearfield_workpack"
DEFAULT_OUT_DIR = ROOT / "outputs" / "cst_true_nearfield_handoff"
DEFAULT_CASES = WORKPACK / "true_nearfield_monitor_cases.csv"
DEFAULT_QUEUE = WORKPACK / "true_nearfield_priority_layout_queue.csv"
DEFAULT_CONTRACT = WORKPACK / "true_nearfield_export_contract.csv"
DEFAULT_GATE_STATUS = WORKPACK / "gate_report" / "true_nearfield_gate_status.csv"
DEFAULT_GATE_SUMMARY = WORKPACK / "gate_report" / "true_nearfield_gate_summary.json"


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: str | Path) -> str:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    try:
        return str(full.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(full)


def file_exists(path: str | Path) -> bool:
    full = Path(path)
    if not full.is_absolute():
        full = ROOT / full
    return full.exists()


def truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def status_lookup(gate_status: pd.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    if gate_status.empty:
        return {}
    if not {"sample_id", "candidate"}.issubset(gate_status.columns):
        return {}
    normalized = gate_status.copy()
    normalized["sample_id"] = normalized["sample_id"].astype(str).str.strip()
    normalized["candidate"] = normalized["candidate"].astype(str).str.strip()
    return {
        (str(row.sample_id), str(row.candidate)): row._asdict()
        for row in normalized.itertuples(index=False)
    }


def action_kind(row: Any) -> str:
    candidate = str(row.candidate)
    if candidate == "full_grid_162":
        return "export_full_grid_in_cst"
    if truthy(row.can_derive_from_full_grid_export):
        return "derive_after_full_grid_export"
    return "export_subset_in_cst"


def action_phase(row: Any) -> str:
    candidate = str(row.candidate)
    priority = str(row.case_priority)
    if candidate == "full_grid_162" and priority == "required":
        return "01_now_required_full_grid"
    if candidate == "full_grid_162" and priority == "recommended":
        return "02_recommended_full_grid"
    if candidate == "full_grid_162":
        return "03_optional_full_grid"
    if priority == "required":
        return "04_derive_required_reduced"
    if priority == "recommended":
        return "05_derive_recommended_reduced"
    return "06_derive_optional_reduced"


def phase_rank(phase: str) -> int:
    try:
        return int(phase.split("_", 1)[0])
    except (ValueError, IndexError):
        return 99


def case_lookup(cases: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if cases.empty or "sample_id" not in cases.columns:
        return {}
    normalized = cases.copy()
    normalized["sample_id"] = normalized["sample_id"].astype(str).str.strip()
    return {str(row.sample_id): row._asdict() for row in normalized.itertuples(index=False)}


def build_action_sheet(queue: pd.DataFrame, gate_status: pd.DataFrame, cases: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        queue,
        {
            "queue_order",
            "sample_id",
            "case_priority",
            "frequency_hz",
            "candidate",
            "layout_role",
            "sensor_count",
            "expected_export_rows",
            "preferred_export_path",
            "full_grid_export_path",
            "farfieldplot_reference_export",
            "can_derive_from_full_grid_export",
            "post_export_comparison",
            "role_reason",
        },
        "queue",
    )
    gate = status_lookup(gate_status)
    cases_by_id = case_lookup(cases)
    rows: list[dict[str, Any]] = []
    for item in queue.sort_values("queue_order").itertuples(index=False):
        key = (str(item.sample_id), str(item.candidate))
        gate_row = gate.get(key, {})
        case_row = cases_by_id.get(str(item.sample_id), {})
        phase = action_phase(item)
        kind = action_kind(item)
        preferred_path = str(item.preferred_export_path)
        full_grid_path = str(item.full_grid_export_path)
        preferred_exists = file_exists(preferred_path)
        full_grid_exists = file_exists(full_grid_path)
        rows.append(
            {
                "phase_rank": phase_rank(phase),
                "handoff_phase": phase,
                "queue_order": int(item.queue_order),
                "sample_id": str(item.sample_id),
                "case_priority": str(item.case_priority),
                "frequency_hz": int(item.frequency_hz),
                "cst_project": case_row.get("cst_project", ""),
                "source_type": case_row.get("source_type", ""),
                "orientation_axis": case_row.get("orientation_axis", ""),
                "true_nearfield_monitor": case_row.get("true_nearfield_monitor", ""),
                "sample_shell_csv": rel(str(case_row.get("sample_shell_csv", ""))) if case_row.get("sample_shell_csv", "") else "",
                "candidate": str(item.candidate),
                "layout_role": str(item.layout_role),
                "action_kind": kind,
                "sensor_count": int(float(item.sensor_count)),
                "expected_export_rows": int(float(item.expected_export_rows)),
                "target_export_path": rel(preferred_path),
                "target_export_exists": preferred_exists,
                "full_grid_export_path": rel(full_grid_path),
                "full_grid_export_exists": full_grid_exists,
                "reference_export": rel(str(item.farfieldplot_reference_export)),
                "reference_export_exists": file_exists(str(item.farfieldplot_reference_export)),
                "gate_status": gate_row.get("gate_status", gate_row.get("status", "not_checked")),
                "source_status": gate_row.get("source_status", ""),
                "post_export_command": post_export_command(kind, item),
                "preferred_operator_action": operator_action(kind, item),
                "role_reason": str(item.role_reason),
            }
        )
    action_sheet = pd.DataFrame(rows)
    return action_sheet.sort_values(["phase_rank", "queue_order"]).drop(columns=["phase_rank"])


def operator_action(kind: str, row: Any) -> str:
    if kind == "export_full_grid_in_cst":
        return (
            "Export Ex/Ey/Ez complex samples on the 162-point shell, write the target CSV, "
            "then run python code\\run_true_nearfield_gate.py."
        )
    if kind == "derive_after_full_grid_export":
        return (
            "Do not reopen CST unless needed; derive this reduced layout from the full-grid CSV "
            f"with python code\\derive_true_nearfield_layout_exports.py --sample-id {row.sample_id}."
        )
    return "Export this subset directly only if full-grid export or derivation is unavailable."


def post_export_command(kind: str, row: Any) -> str:
    if kind == "export_full_grid_in_cst":
        return "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only"
    if kind == "derive_after_full_grid_export":
        return f"python code\\derive_true_nearfield_layout_exports.py --sample-id {row.sample_id}"
    return "python code\\run_true_nearfield_gate.py"


def build_expected_files(action_sheet: pd.DataFrame) -> pd.DataFrame:
    full_grid = action_sheet[action_sheet["candidate"].astype(str).eq("full_grid_162")].copy()
    columns = [
        "handoff_phase",
        "sample_id",
        "case_priority",
        "frequency_hz",
        "cst_project",
        "source_type",
        "orientation_axis",
        "true_nearfield_monitor",
        "sample_shell_csv",
        "target_export_path",
        "target_export_exists",
        "sensor_count",
        "expected_export_rows",
        "gate_status",
        "source_status",
        "reference_export",
        "reference_export_exists",
    ]
    return full_grid[columns].reset_index(drop=True)


def build_algorithm_commands(action_sheet: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "order": 1,
            "gate": "after_full_grid_exports",
            "command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
            "purpose": "Preflight the required true-monitor CSV contract, row counts, components, and sensor subsets.",
        },
        {
            "order": 2,
            "gate": "after_full_grid_exports",
            "command": "python code\\run_true_nearfield_gate.py --required-only",
            "purpose": "Confirm required full-grid true-monitor files are no longer pending_source.",
        },
        {
            "order": 3,
            "gate": "after_required_full_grid_passes_file_count",
            "command": "python code\\derive_true_nearfield_layout_exports.py --sample-id L1_short_dipole_z_1p2G",
            "purpose": "Derive queued 32/120 layouts for the first required case from the full-grid monitor CSV.",
        },
        {
            "order": 4,
            "gate": "after_required_full_grid_passes_file_count",
            "command": "python code\\derive_true_nearfield_layout_exports.py --sample-id L1_halfwave_dipole_z_1p2G",
            "purpose": "Derive queued 32/120 layouts for the second required case from the full-grid monitor CSV.",
        },
        {
            "order": 5,
            "gate": "after_derivation",
            "command": "python code\\run_true_nearfield_gate.py --required-only",
            "purpose": "Compare full/reduced required layouts and decide reference_match versus needs_physical_rerun.",
        },
        {
            "order": 6,
            "gate": "if_needs_physical_rerun",
            "command": "python code\\run_cst_source_model_sweep.py",
            "purpose": "Rerun source-model support calibration on authoritative monitor data.",
        },
        {
            "order": 7,
            "gate": "if_needs_physical_rerun",
            "command": "python code\\run_spherical_nf_ff_baseline.py",
            "purpose": "Rerun the scalar SWE sanity baseline before any reduced-layout claim.",
        },
        {
            "order": 8,
            "gate": "if_needs_physical_rerun",
            "command": "python code\\run_cst_huygens_baseline.py",
            "purpose": "Rerun the Huygens diagnostic and keep it separate from report-safe proof until it passes.",
        },
    ]
    if not action_sheet.empty and not action_sheet["target_export_exists"].any():
        rows.insert(
            0,
            {
                "order": 0,
                "gate": "current_state",
                "command": "CST export required before algorithm rerun.",
                "purpose": "All queued true-monitor source files are still absent.",
            },
        )
    return pd.DataFrame(rows)


def write_markdown(
    out_dir: Path,
    action_sheet: pd.DataFrame,
    expected_files: pd.DataFrame,
    commands: pd.DataFrame,
    contract: pd.DataFrame,
    gate_summary: dict[str, Any],
) -> None:
    required_full = expected_files[expected_files["case_priority"].astype(str).eq("required")]
    pending_required = required_full[~required_full["target_export_exists"].astype(bool)]
    lines: list[str] = [
        "# CST True Near-Field Handoff",
        "",
        "This handoff turns the true-monitor workpack into an operator action list.",
        "It is generated by `python code\\build_true_nearfield_handoff.py`.",
        "",
        "## Immediate Decision",
        "",
    ]
    if not pending_required.empty:
        lines.extend(
            [
                "- Export the two required `full_grid_162` true near-field monitor CSV files first.",
                "- Do not spend CST time on 32/120 reduced layouts before the full-grid monitor files exist; they can be derived from the 162-point CSV.",
                "- After export, run `python code\\run_true_nearfield_gate.py --required-only`.",
            ]
        )
    else:
        lines.extend(
            [
                "- Required full-grid files are present; run the true-monitor gate and derive queued reduced layouts.",
                "- If the gate reports `needs_physical_rerun`, rerun the G3 baselines before reporting reduced sampling.",
            ]
        )

    lines.extend(
        [
            "",
            "## Required Full-Grid Exports",
            "",
            "| Sample | Priority | Target CSV | Expected rows | Exists | Gate status |",
            "|---|---|---|---:|---|---|",
        ]
    )
    for item in required_full.itertuples(index=False):
        lines.append(
            f"| {item.sample_id} | {item.case_priority} | `{item.target_export_path}` | "
            f"{item.expected_export_rows} | {item.target_export_exists} | {item.gate_status} |"
        )

    lines.extend(
        [
            "",
            "## CSV Contract",
            "",
            "- One row per `sample_id, frequency_hz, sensor_id, polarization`.",
            "- The required full-grid row count is `162 sensors * 3 components = 486` per case.",
            "- Use Cartesian components `Ex`, `Ey`, and `Ez`; keep complex values as `e_real` and `e_imag`.",
            "- Keep `extraction_method` as `CST true near-field monitor interpolated on spherical shell`.",
            "",
            "Required columns:",
            "",
        ]
    )
    if contract.empty:
        lines.append("- Contract CSV missing.")
    else:
        lines.append(", ".join(f"`{name}`" for name in contract["column_name"].astype(str).tolist()))

    lines.extend(
        [
            "",
            "## Algorithm Follow-Up Commands",
            "",
            "| Order | Gate | Command | Purpose |",
            "|---:|---|---|---|",
        ]
    )
    for item in commands.itertuples(index=False):
        lines.append(f"| {item.order} | {item.gate} | `{item.command}` | {item.purpose} |")

    lines.extend(
        [
            "",
            "## Current Gate Summary",
            "",
            f"- Queue rows: {gate_summary.get('queue_row_count', '')}",
            f"- Pending source rows: {gate_summary.get('pending_source_count', '')}",
            f"- Status counts: {gate_summary.get('status_counts', {})}",
            "",
            "## Generated Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `cst_operator_action_sheet.csv` | Full queue with action kind, target paths, file existence, and gate status. |",
            "| `expected_true_monitor_files.csv` | Full-grid monitor CSVs that CST should produce first. |",
            "| `post_export_algorithm_commands.csv` | Commands for the algorithm operator after export. |",
            "| `handoff_summary.json` | Machine-readable counts and blockers. |",
            "",
        ]
    )
    (out_dir / "cst_true_nearfield_handoff.md").write_text("\n".join(lines), encoding="utf-8")


def build_summary(
    action_sheet: pd.DataFrame,
    expected_files: pd.DataFrame,
    commands: pd.DataFrame,
    gate_summary: dict[str, Any],
) -> dict[str, Any]:
    required = expected_files[expected_files["case_priority"].astype(str).eq("required")]
    pending_required = required[~required["target_export_exists"].astype(bool)]
    action_counts = action_sheet["action_kind"].value_counts().to_dict() if not action_sheet.empty else {}
    return {
        "generated_by": "code/build_true_nearfield_handoff.py",
        "required_full_grid_count": int(required.shape[0]),
        "required_full_grid_pending_count": int(pending_required.shape[0]),
        "all_full_grid_count": int(expected_files.shape[0]),
        "action_counts": {str(k): int(v) for k, v in action_counts.items()},
        "gate_status_counts": gate_summary.get("status_counts", {}),
        "next_required_action": (
            "export_required_full_grid_true_monitor_csvs"
            if not pending_required.empty
            else "run_true_nearfield_gate_and_derive_reduced_layouts"
        ),
        "output_files": {
            "handoff": "outputs\\cst_true_nearfield_handoff\\cst_true_nearfield_handoff.md",
            "action_sheet": "outputs\\cst_true_nearfield_handoff\\cst_operator_action_sheet.csv",
            "expected_files": "outputs\\cst_true_nearfield_handoff\\expected_true_monitor_files.csv",
            "algorithm_commands": "outputs\\cst_true_nearfield_handoff\\post_export_algorithm_commands.csv",
        },
        "algorithm_command_count": int(commands.shape[0]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the CST true near-field monitor handoff.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--gate-status", type=Path, default=DEFAULT_GATE_STATUS)
    parser.add_argument("--gate-summary", type=Path, default=DEFAULT_GATE_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = read_csv(Path(args.cases))
    queue = read_csv(Path(args.queue))
    contract = read_csv(Path(args.contract))
    gate_status = read_csv(Path(args.gate_status))
    gate_summary = read_json(Path(args.gate_summary))

    if cases.empty:
        raise FileNotFoundError(f"missing or empty cases table: {args.cases}")
    if queue.empty:
        raise FileNotFoundError(f"missing or empty queue table: {args.queue}")

    action_sheet = build_action_sheet(queue, gate_status, cases)
    expected_files = build_expected_files(action_sheet)
    commands = build_algorithm_commands(action_sheet)
    summary = build_summary(action_sheet, expected_files, commands, gate_summary)

    action_sheet.to_csv(out_dir / "cst_operator_action_sheet.csv", index=False, encoding="utf-8-sig")
    expected_files.to_csv(out_dir / "expected_true_monitor_files.csv", index=False, encoding="utf-8-sig")
    commands.to_csv(out_dir / "post_export_algorithm_commands.csv", index=False, encoding="utf-8-sig")
    (out_dir / "handoff_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(out_dir, action_sheet, expected_files, commands, contract, gate_summary)

    print(f"CST true near-field handoff written to {rel(out_dir)}")
    print(f"next required action: {summary['next_required_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
