from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WORKPACK = ROOT / "data" / "cst_true_nearfield_workpack"
DEFAULT_CASES = WORKPACK / "true_nearfield_monitor_cases.csv"
DEFAULT_QUEUE = WORKPACK / "true_nearfield_priority_layout_queue.csv"
DEFAULT_CONTRACT = WORKPACK / "true_nearfield_export_contract.csv"
DEFAULT_GATE_STATUS = WORKPACK / "gate_report" / "true_nearfield_gate_status.csv"
DEFAULT_OUT_DIR = WORKPACK / "operator_packet"


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


def require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = sorted(columns - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def json_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    clean = frame.where(pd.notna(frame), None)
    return json.loads(clean.to_json(orient="records", force_ascii=False))


def path_exists(path: str | Path) -> bool:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.exists()


def case_lookup(cases: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if cases.empty:
        return {}
    require_columns(cases, {"sample_id"}, "case table")
    normalized = cases.copy()
    normalized["sample_id"] = normalized["sample_id"].astype(str).str.strip()
    return {str(row.sample_id): row._asdict() for row in normalized.itertuples(index=False)}


def gate_lookup(gate_status: pd.DataFrame) -> dict[tuple[str, str], dict[str, Any]]:
    if gate_status.empty or not {"sample_id", "candidate"}.issubset(gate_status.columns):
        return {}
    normalized = gate_status.copy()
    normalized["sample_id"] = normalized["sample_id"].astype(str).str.strip()
    normalized["candidate"] = normalized["candidate"].astype(str).str.strip()
    return {
        (str(row.sample_id), str(row.candidate)): row._asdict()
        for row in normalized.itertuples(index=False)
    }


def select_required_full_grid(queue: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        queue,
        {
            "queue_order",
            "sample_id",
            "case_priority",
            "frequency_hz",
            "frequency_label",
            "candidate",
            "layout_role",
            "sensor_count",
            "expected_export_rows",
            "preferred_export_path",
            "farfieldplot_reference_export",
            "post_export_comparison",
        },
        "priority queue",
    )
    selected = queue.copy()
    selected["sample_id"] = selected["sample_id"].astype(str).str.strip()
    selected["case_priority"] = selected["case_priority"].astype(str).str.strip()
    selected["candidate"] = selected["candidate"].astype(str).str.strip()
    selected = selected[
        selected["case_priority"].eq("required")
        & selected["candidate"].eq("full_grid_162")
    ].copy()
    if selected.empty:
        raise ValueError("no required full_grid_162 rows found in true-nearfield queue")
    selected["queue_order"] = pd.to_numeric(selected["queue_order"], errors="coerce").astype(int)
    return selected.sort_values("queue_order", kind="stable")


def build_required_manifest(
    queue: pd.DataFrame,
    cases: pd.DataFrame,
    gate_status: pd.DataFrame,
) -> pd.DataFrame:
    cases_by_id = case_lookup(cases)
    gates = gate_lookup(gate_status)
    rows: list[dict[str, Any]] = []
    for item in queue.itertuples(index=False):
        sample_id = str(item.sample_id)
        case = cases_by_id.get(sample_id, {})
        gate = gates.get((sample_id, "full_grid_162"), {})
        target_path = str(item.preferred_export_path)
        sample_shell = str(case.get("sample_shell_csv", "data/cst_true_nearfield_workpack/true_nearfield_sensor_shell.csv"))
        monitor_name = str(case.get("true_nearfield_monitor", f"true_nf_shell_{int(float(item.frequency_hz) / 1e6)}MHz"))
        rows.append(
            {
                "queue_order": int(item.queue_order),
                "sample_id": sample_id,
                "case_priority": str(item.case_priority),
                "frequency_hz": int(float(item.frequency_hz)),
                "frequency_label": str(item.frequency_label),
                "cst_project": str(case.get("cst_project", "")),
                "source_type": str(case.get("source_type", "")),
                "orientation_axis": str(case.get("orientation_axis", "")),
                "source_center_m": f"{case.get('center_x_m', '')},{case.get('center_y_m', '')},{case.get('center_z_m', '')}",
                "source_start_m": f"{case.get('start_x_m', '')},{case.get('start_y_m', '')},{case.get('start_z_m', '')}",
                "source_end_m": f"{case.get('end_x_m', '')},{case.get('end_y_m', '')},{case.get('end_z_m', '')}",
                "true_nearfield_monitor": monitor_name,
                "sample_shell_csv": rel(sample_shell),
                "target_export_path": rel(target_path),
                "target_export_exists": path_exists(target_path),
                "expected_sensor_count": int(float(item.sensor_count)),
                "expected_export_rows": int(float(item.expected_export_rows)),
                "required_components": str(case.get("required_components", "Ex;Ey;Ez")),
                "reference_nearfield_export": rel(str(item.farfieldplot_reference_export)),
                "reference_export_exists": path_exists(str(item.farfieldplot_reference_export)),
                "gate_status": str(gate.get("gate_status", "missing_gate_status")),
                "source_status": str(gate.get("source_status", "")),
                "operator_action": "export_full_grid_true_monitor_csv",
                "dropzone_command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
                "gate_command": "python code\\run_true_nearfield_gate.py --required-only --candidate full_grid_162",
                "comparison_command": str(item.post_export_comparison),
            }
        )
    return pd.DataFrame(rows)


def build_acceptance_commands(manifest: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = [
        {
            "order": 1,
            "owner": "CST operator",
            "stage": "export_required_full_grid",
            "command": "export the two required full_grid_162 true-monitor CSV files listed in required_full_grid_manifest.csv",
            "expected_result": "Both target CSV files exist with 486 rows each.",
            "blocked_by": "CST true near-field monitor export",
        },
        {
            "order": 2,
            "owner": "Algorithm operator",
            "stage": "dropzone_preflight",
            "command": "python code\\check_true_nearfield_dropzone.py --required-only --full-grid-only",
            "expected_result": "Required full-grid rows are ready_for_gate.",
            "blocked_by": "required true-monitor CSV files",
        },
        {
            "order": 3,
            "owner": "Algorithm operator",
            "stage": "required_gate",
            "command": "python code\\run_true_nearfield_gate.py --required-only --candidate full_grid_162",
            "expected_result": "Required full-grid rows leave pending_source.",
            "blocked_by": "ready_for_gate dropzone status",
        },
    ]
    order = 4
    for row in manifest.itertuples(index=False):
        rows.append(
            {
                "order": order,
                "owner": "Algorithm operator",
                "stage": "derive_required_reduced_layouts",
                "command": f"python code\\derive_true_nearfield_layout_exports.py --sample-id {row.sample_id}",
                "expected_result": "The queued 32-point and 120-point reduced-layout CSVs are derived from the full-grid monitor CSV.",
                "blocked_by": f"{row.target_export_path}",
            }
        )
        order += 1
    rows.extend(
        [
            {
                "order": order,
                "owner": "Algorithm operator",
                "stage": "reduced_layout_gate",
                "command": "python code\\run_true_nearfield_gate.py --required-only",
                "expected_result": "Full-grid and reduced-layout required rows are compared.",
                "blocked_by": "derived reduced-layout CSV files",
            },
            {
                "order": order + 1,
                "owner": "Algorithm operator",
                "stage": "workflow_decision_refresh",
                "command": "python code\\run_true_nearfield_workflow_decision.py",
                "expected_result": "The next G3 action is refreshed from current dropzone and gate evidence.",
                "blocked_by": "",
            },
            {
                "order": order + 2,
                "owner": "Algorithm operator",
                "stage": "g3_dashboard_refresh",
                "command": "python code\\build_g3_model_dashboard.py",
                "expected_result": "G3 dashboard records true-monitor gate status.",
                "blocked_by": "",
            },
        ]
    )
    return pd.DataFrame(rows)


def contract_column_list(contract: pd.DataFrame) -> list[str]:
    if contract.empty or "column_name" not in contract.columns:
        return []
    return [str(value).strip() for value in contract["column_name"].tolist() if str(value).strip()]


def write_task_cards(out_dir: Path, manifest: pd.DataFrame, contract: pd.DataFrame) -> None:
    columns = contract_column_list(contract)
    lines: list[str] = [
        "# Required CST True Near-Field Task Cards",
        "",
        "These cards are generated by `python code\\prepare_cst_true_nearfield_operator_packet.py`.",
        "They describe the CST-side exports that unblock the G3 true-monitor gate.",
        "",
        "## Shared Export Contract",
        "",
        "- Export Cartesian complex electric-field components as three component rows per sensor: `Ex`, `Ey`, and `Ez`.",
        "- Use the 162 rows in `data\\cst_true_nearfield_workpack\\true_nearfield_sensor_shell.csv` as the sampling shell.",
        "- Each required full-grid case must produce `162 sensors * 3 components = 486` rows.",
        "- Keep the extraction method text as `CST true near-field monitor interpolated on spherical shell`.",
        "",
    ]
    if columns:
        lines.extend(["Required CSV columns:", "", ", ".join(f"`{column}`" for column in columns), ""])
    for row in manifest.itertuples(index=False):
        lines.extend(
            [
                f"## {row.sample_id}",
                "",
                f"- CST project: `{row.cst_project}`",
                f"- Source: `{row.source_type}`, orientation `{row.orientation_axis}`",
                f"- Frequency: `{row.frequency_hz}` Hz (`{row.frequency_label}`)",
                f"- Monitor name: `{row.true_nearfield_monitor}`",
                f"- Sampling shell: `{row.sample_shell_csv}`",
                f"- Target CSV: `{row.target_export_path}`",
                f"- Expected rows: `{row.expected_export_rows}`",
                f"- Current gate status: `{row.gate_status}`",
                "",
                "Operator steps:",
                "",
                "1. Open or rebuild the listed CST Level 1 project.",
                "2. Confirm the source geometry and feed correspond to this `sample_id`.",
                "3. Add or verify a true E-field near-field monitor at the listed frequency.",
                "4. Solve the case if the monitor result is not current.",
                "5. Interpolate or sample the monitor at every coordinate in the sampling shell.",
                "6. Write the target CSV with the required columns and row count.",
                "7. Run the dropzone preflight before any comparison claim.",
                "",
            ]
        )
    (out_dir / "required_full_grid_task_cards.md").write_text("\n".join(lines), encoding="utf-8")


def write_readme(out_dir: Path, summary: dict[str, Any]) -> None:
    content = f"""# CST True Near-Field Operator Packet

This tracked packet is generated by:

```powershell
python code\\prepare_cst_true_nearfield_operator_packet.py
```

It is the GitHub-visible CST handoff for the G3 true near-field monitor gate.
It does not contain solved CST evidence; it records the exact required exports
and acceptance commands.

## Current State

- Required full-grid exports: {summary["required_full_grid_count"]}
- Required full-grid files already present: {summary["required_full_grid_present_count"]}
- Required full-grid files still missing: {summary["required_full_grid_missing_count"]}
- Next required action: `{summary["next_required_action"]}`

## Files

| File | Purpose |
|---|---|
| `required_full_grid_manifest.csv` | Exact CST projects, sample ids, monitor names, target CSVs, and row counts for the required full-grid exports. |
| `required_full_grid_task_cards.md` | Human-readable CST operator cards for the two required Level 1 z-dipole exports. |
| `post_export_acceptance_commands.csv` | Ordered commands after CST files are dropped into `data/cst_exports/level1_true_nearfield/`. |
| `operator_packet_summary.json` | Machine-readable packet summary and current blocker. |

Do not treat this packet as final G3 evidence. The gate closes only after the
target CSV files pass dropzone validation and `run_true_nearfield_gate.py`.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def build_summary(manifest: pd.DataFrame, commands: pd.DataFrame) -> dict[str, Any]:
    present = int(manifest["target_export_exists"].astype(bool).sum()) if not manifest.empty else 0
    total = int(manifest.shape[0])
    missing = max(total - present, 0)
    next_action = (
        "run_dropzone_preflight"
        if total > 0 and present == total
        else "export_required_full_grid_true_monitor_csvs"
    )
    return {
        "generated_by": "code/prepare_cst_true_nearfield_operator_packet.py",
        "required_full_grid_count": total,
        "required_full_grid_present_count": present,
        "required_full_grid_missing_count": missing,
        "next_required_action": next_action,
        "claim_boundary": (
            "This packet is an operator handoff. It is not full-wave evidence until the required "
            "true-monitor CSVs pass dropzone validation and the true-nearfield gate."
        ),
        "manifest_records": json_records(manifest),
        "acceptance_command_records": json_records(commands),
        "output_files": {
            "readme": "data\\cst_true_nearfield_workpack\\operator_packet\\README.md",
            "task_cards": "data\\cst_true_nearfield_workpack\\operator_packet\\required_full_grid_task_cards.md",
            "manifest": "data\\cst_true_nearfield_workpack\\operator_packet\\required_full_grid_manifest.csv",
            "commands": "data\\cst_true_nearfield_workpack\\operator_packet\\post_export_acceptance_commands.csv",
            "summary": "data\\cst_true_nearfield_workpack\\operator_packet\\operator_packet_summary.json",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tracked CST true near-field operator packet.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--gate-status", type=Path, default=DEFAULT_GATE_STATUS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = read_csv(Path(args.cases))
    queue = select_required_full_grid(read_csv(Path(args.queue)))
    contract = read_csv(Path(args.contract))
    gate_status = read_csv(Path(args.gate_status))
    manifest = build_required_manifest(queue, cases, gate_status)
    commands = build_acceptance_commands(manifest)
    summary = build_summary(manifest, commands)

    manifest.to_csv(out_dir / "required_full_grid_manifest.csv", index=False, encoding="utf-8-sig")
    commands.to_csv(out_dir / "post_export_acceptance_commands.csv", index=False, encoding="utf-8-sig")
    write_task_cards(out_dir, manifest, contract)
    (out_dir / "operator_packet_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"CST true near-field operator packet written to {rel(out_dir)}")
    print(f"required full-grid present: {summary['required_full_grid_present_count']}/{summary['required_full_grid_count']}")
    print(f"next required action: {summary['next_required_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
