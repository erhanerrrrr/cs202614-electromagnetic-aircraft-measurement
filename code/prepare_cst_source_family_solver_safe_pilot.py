from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAMILY_WORKPACK = ROOT / "data" / "cst_meshsafe_huygens_source_family_workpack"
DEFAULT_CASE_CSV = SOURCE_FAMILY_WORKPACK / "level1_source_family_axis_aligned_cases.csv"
DEFAULT_PROBE_CSV = SOURCE_FAMILY_WORKPACK / "level1_source_family_probe_points.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "cst_meshsafe_huygens_source_family_solver_safe_pilot"
DEFAULT_SOLVER_TRIAL_DIR = (
    ROOT / "outputs" / "cst_solver_trials" / "meshsafe_huygens_source_family_solver_safe"
)
DEFAULT_PROJECT_ROOT = Path(r"C:\csttmp")
DEFAULT_SAMPLE_ID = "L1_short_dipole_x_1p2G"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def command_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_csv_with_fields(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sample_rows(rows: list[dict[str, str]], sample_id: str) -> list[dict[str, str]]:
    return [row for row in rows if str(row.get("sample_id", "")).strip() == sample_id]


def sort_probes(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    def key(row: dict[str, str]) -> tuple[int, int]:
        try:
            sensor_id = int(row.get("sensor_id", "0"))
        except ValueError:
            sensor_id = 0
        try:
            node_id = int(row.get("node_id", "0"))
        except ValueError:
            node_id = 0
        return sensor_id, node_id

    return sorted(rows, key=key)


def shell_join(parts: list[str]) -> str:
    quoted: list[str] = []
    for part in parts:
        if not part:
            continue
        if any(char.isspace() for char in part):
            quoted.append(f'"{part}"')
        else:
            quoted.append(part)
    return " ".join(quoted)


def planned_ladder() -> list[dict[str, Any]]:
    return [
        {
            "ladder_id": "none",
            "probe_mode": "none",
            "probe_rows": 0,
            "timeout_seconds": 240,
            "purpose": "Geometry, port, near-field monitor, and far-field monitor solve without local probes.",
            "gate_interpretation": (
                "If this times out, the bottleneck is the base time-domain solve rather than probe count."
            ),
        },
        {
            "ladder_id": "efarfield96",
            "probe_mode": "efarfield",
            "probe_rows": 96,
            "timeout_seconds": 300,
            "purpose": "Preserve angular sampling with CST far-field probes before local Cartesian E probes.",
            "gate_interpretation": (
                "If this passes but local probes time out, keep far-field probe extraction separate from Huygens surface export."
            ),
        },
        {
            "ladder_id": "efield24",
            "probe_mode": "efield",
            "probe_rows": 24,
            "timeout_seconds": 360,
            "purpose": "Small local Cartesian E-field probe subset on the same 0.35 m Huygens sphere.",
            "gate_interpretation": (
                "If this passes, increase local probe count before retrying the full 96-probe pilot."
            ),
        },
        {
            "ladder_id": "hfield24",
            "probe_mode": "hfield",
            "probe_rows": 24,
            "timeout_seconds": 360,
            "purpose": "Small local Cartesian H-field probe subset using the same sample and nodes as efield24.",
            "gate_interpretation": (
                "If E passes and H fails, keep the E/H export queues separated and inspect H-field probe cost."
            ),
        },
        {
            "ladder_id": "efield48",
            "probe_mode": "efield",
            "probe_rows": 48,
            "timeout_seconds": 1800,
            "purpose": "Intermediate local E-field probe count with a long window calibrated by the 48-probe pilot.",
            "gate_interpretation": (
                "Use this as the scaling bridge between 24-probe and full 96-probe local export; "
                "the first successful run needed about 15.8 minutes."
            ),
        },
        {
            "ladder_id": "efield96",
            "probe_mode": "efield",
            "probe_rows": 96,
            "timeout_seconds": 5400,
            "purpose": "Full local E-field source-family pilot with a ninety-minute diagnostic window.",
            "gate_interpretation": (
                "Only run this after the lower-cost gates have shown that the base solve and reduced probes finish; "
                "the first successful full E run needed about 56 minutes, so future runs need margin. "
                "If it still fails, split local probes or change CST solver/export strategy."
            ),
        },
    ]


def build_command_rows(
    case: dict[str, str],
    out_dir: Path,
    project_root: Path,
    solver_trial_dir: Path,
    sample_id: str,
) -> list[dict[str, Any]]:
    case_csv = out_dir / "solver_safe_pilot_case.csv"
    probe_csv_by_count = {
        0: out_dir / "solver_safe_probe_none.csv",
        24: out_dir / "solver_safe_probe_24.csv",
        48: out_dir / "solver_safe_probe_48.csv",
        96: out_dir / "solver_safe_probe_96.csv",
    }
    cst_project_name = case["cst_project"]
    rows: list[dict[str, Any]] = []
    previous = ""
    for order, item in enumerate(planned_ladder(), start=1):
        ladder_id = str(item["ladder_id"])
        project_out = project_root / f"huy_sf_safe_{ladder_id}"
        trial_out = project_root / f"huy_sf_safe_{ladder_id}_s"
        project_path = project_out / "projects" / cst_project_name
        probe_csv = probe_csv_by_count[int(item["probe_rows"])]
        timeout_seconds = int(item["timeout_seconds"])
        summary_out = solver_trial_dir / f"{sample_id}_{ladder_id}_solver_summary.json"
        stdout_log = solver_trial_dir / f"{sample_id}_{ladder_id}_stdout.log"
        generate_command = shell_join(
            [
                "python",
                r"code\run_cst_level1_required_automation.py",
                "--level1-csv",
                command_path(case_csv),
                "--probe-csv",
                command_path(probe_csv),
                "--out-dir",
                str(project_out),
                "--probe-mode",
                str(item["probe_mode"]),
                "--timeout-seconds",
                "900",
            ]
        )
        solve_command = shell_join(
            [
                "python",
                r"code\run_cst_solver_project.py",
                "--project",
                str(project_path),
                "--out-dir",
                str(trial_out),
                "--trial-name",
                f"{sample_id}_{ladder_id}.cst",
                "--summary-out",
                command_path(summary_out),
                "--stdout-log",
                command_path(stdout_log),
                "--timeout-seconds",
                str(timeout_seconds),
                "--poll-seconds",
                "10",
            ]
        )
        rows.append(
            {
                "execution_order": order,
                "ladder_id": ladder_id,
                "run_after": previous,
                "sample_id": sample_id,
                "probe_mode": item["probe_mode"],
                "probe_rows": item["probe_rows"],
                "timeout_seconds": timeout_seconds,
                "project_out_dir": str(project_out),
                "trial_out_dir": str(trial_out),
                "expected_project": str(project_path),
                "summary_out": command_path(summary_out),
                "stdout_log": command_path(stdout_log),
                "purpose": item["purpose"],
                "gate_interpretation": item["gate_interpretation"],
                "generate_command": generate_command,
                "solve_command": solve_command,
            }
        )
        previous = ladder_id
    return rows


def write_readme(path: Path, summary: dict[str, Any], commands: list[dict[str, Any]]) -> None:
    lines = [
        "# CST source-family solver-safe pilot",
        "",
        "Purpose: diagnose the first source-family CST solver timeout without changing the frozen Huygens rule.",
        "",
        "The current blocker is not CST startup. The previous pilot started through the real CST API and populated ResultTree probe entries, but the default time-domain solve did not finish export inside the timeout. This workpack turns that blocker into a short diagnostic ladder.",
        "",
        "## Status",
        "",
        f"- Stage status: `{summary['stage_status']}`",
        f"- Target sample: `{summary['target_sample_id']}`",
        f"- Full local probe rows: `{summary['full_probe_row_count']}`",
        f"- Planned CST diagnostic trials: `{summary['planned_trial_count']}`",
        "",
        "## Ladder",
        "",
        "| Order | Ladder | Probe mode | Probe rows | Timeout / s | Purpose |",
        "|---:|---|---|---:|---:|---|",
    ]
    for row in commands:
        lines.append(
            f"| {row['execution_order']} | `{row['ladder_id']}` | `{row['probe_mode']}` | "
            f"{row['probe_rows']} | {row['timeout_seconds']} | {row['purpose']} |"
        )
    lines.extend(
        [
            "",
            "## Run order",
            "",
            "Run the `generate_command` and then the `solve_command` for each ladder row. Stop at the first repeated timeout and summarize with:",
            "",
            "```powershell",
            "python code\\build_cst_source_family_solver_safe_status.py",
            "python code\\build_g3_model_dashboard.py",
            "```",
            "",
            "Important files:",
            "",
            "- `solver_safe_pilot_case.csv`: one-case CST source-family pilot input.",
            "- `solver_safe_probe_*.csv`: probe subsets used by the ladder.",
            "- `solver_safe_pilot_commands.csv`: ordered generation and solver commands.",
            "- `solver_safe_pilot_plan_summary.json`: machine-readable plan summary.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir)
    solver_trial_dir = Path(args.solver_trial_dir)
    case_rows, case_fields = read_csv_with_fields(Path(args.case_csv))
    probe_rows, probe_fields = read_csv_with_fields(Path(args.probe_csv))
    selected_cases = sample_rows(case_rows, args.sample_id)
    if len(selected_cases) != 1:
        raise ValueError(f"Expected exactly one case for {args.sample_id!r}, found {len(selected_cases)}")
    selected_case = selected_cases[0]
    selected_probes = sort_probes(sample_rows(probe_rows, args.sample_id))
    if not selected_probes:
        raise ValueError(f"No probe rows found for {args.sample_id!r}")

    out_dir.mkdir(parents=True, exist_ok=True)
    solver_trial_dir.mkdir(parents=True, exist_ok=True)
    write_csv(out_dir / "solver_safe_pilot_case.csv", selected_cases, case_fields)
    write_csv(out_dir / "solver_safe_probe_none.csv", [], probe_fields)
    write_csv(out_dir / "solver_safe_probe_24.csv", selected_probes[:24], probe_fields)
    write_csv(out_dir / "solver_safe_probe_48.csv", selected_probes[:48], probe_fields)
    write_csv(out_dir / "solver_safe_probe_96.csv", selected_probes[:96], probe_fields)

    commands = build_command_rows(
        selected_case,
        out_dir,
        Path(args.project_root),
        solver_trial_dir,
        args.sample_id,
    )
    command_fields = [
        "execution_order",
        "ladder_id",
        "run_after",
        "sample_id",
        "probe_mode",
        "probe_rows",
        "timeout_seconds",
        "project_out_dir",
        "trial_out_dir",
        "expected_project",
        "summary_out",
        "stdout_log",
        "purpose",
        "gate_interpretation",
        "generate_command",
        "solve_command",
    ]
    write_csv(out_dir / "solver_safe_pilot_commands.csv", commands, command_fields)

    summary = {
        "generated_at": now_iso(),
        "stage_status": "source_family_solver_safe_pilot_plan_ready",
        "target_sample_id": args.sample_id,
        "source_case_csv": display_path(Path(args.case_csv)),
        "source_probe_csv": display_path(Path(args.probe_csv)),
        "out_dir": display_path(out_dir),
        "solver_trial_dir": display_path(solver_trial_dir),
        "selected_case_count": len(selected_cases),
        "full_probe_row_count": len(selected_probes),
        "planned_trial_count": len(commands),
        "probe_subset_counts": {"none": 0, "probe_24": 24, "probe_48": 48, "probe_96": 96},
        "blocked_previous_stage": "source_family_solver_pilot_timed_out",
        "diagnostic_question": (
            "Does the x-oriented source-family timeout come from the base CST solve, far-field monitor setup, "
            "or local Cartesian probe count?"
        ),
        "commands_csv": display_path(out_dir / "solver_safe_pilot_commands.csv"),
        "status_command": "python code\\build_cst_source_family_solver_safe_status.py",
        "dashboard_command": "python code\\build_g3_model_dashboard.py",
        "next_gate": "run none first, then efarfield96, efield24, hfield24, efield48, and only then efield96",
        "commands": commands,
    }
    write_json(out_dir / "solver_safe_pilot_plan_summary.json", summary)
    write_readme(out_dir / "README.md", summary, commands)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a CST solver-safe diagnostic ladder for the source-family timeout."
    )
    parser.add_argument("--case-csv", type=Path, default=DEFAULT_CASE_CSV)
    parser.add_argument("--probe-csv", type=Path, default=DEFAULT_PROBE_CSV)
    parser.add_argument("--sample-id", default=DEFAULT_SAMPLE_ID)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--solver-trial-dir", type=Path, default=DEFAULT_SOLVER_TRIAL_DIR)
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = prepare(args)
    print(
        json.dumps(
            {
                "stage_status": summary["stage_status"],
                "out_dir": summary["out_dir"],
                "planned_trial_count": summary["planned_trial_count"],
                "target_sample_id": summary["target_sample_id"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
