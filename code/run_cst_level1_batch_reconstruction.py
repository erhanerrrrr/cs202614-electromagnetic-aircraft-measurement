from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_STATUS = ROOT / "outputs" / "cst_level1_merge_report" / "level1_case_status.csv"
DEFAULT_OUT_ROOT = ROOT / "outputs" / "cst_reconstruction"
DEFAULT_BATCH_DIR = ROOT / "outputs" / "cst_level1_reconstruction_batch"


def resolve_path(path_text: object, base_dir: Path) -> Path:
    path = Path(str(path_text).strip())
    if path.is_absolute():
        return path
    return base_dir / path


def display_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.relative_to(base_dir))
    except ValueError:
        return str(path)


def load_case_status(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"case status not found: {path}. Run src\\merge_cst_level1_exports.py first.")
    status = pd.read_csv(path, encoding="utf-8-sig")
    required = {"sample_id", "priority", "frequency_hz", "nearfield_path", "farfield_path", "case_complete"}
    missing = sorted(required - set(status.columns))
    if missing:
        raise ValueError(f"case status missing required columns: {missing}")
    return status


def filter_cases(status: pd.DataFrame, priority: str) -> pd.DataFrame:
    work = status.copy()
    work["case_complete"] = work["case_complete"].astype(str).str.lower().isin({"true", "1", "yes"})
    work = work[work["case_complete"]].copy()
    if priority != "all":
        work = work[work["priority"].astype(str).str.strip().eq(priority)].copy()
    priority_rank = {"required": 0, "recommended": 1, "optional": 2}
    work["_priority_rank"] = work["priority"].astype(str).str.strip().map(priority_rank).fillna(99)
    return work.sort_values(["_priority_rank", "sample_id"]).drop(columns=["_priority_rank"])


def command_for_case(row, base_dir: Path, out_root: Path) -> tuple[list[str], str, Path]:
    sample_id = str(row.sample_id)
    nearfield = resolve_path(row.nearfield_path, base_dir)
    farfield = resolve_path(row.farfield_path, base_dir)
    out_dir = out_root / sample_id
    args = [
        sys.executable,
        str(ROOT / "code" / "run_cst_reconstruction.py"),
        "--nearfield",
        str(nearfield),
        "--farfield",
        str(farfield),
        "--sample-id",
        sample_id,
        "--frequency-hz",
        str(float(row.frequency_hz)),
        "--out-dir",
        str(out_dir),
    ]
    display = (
        "python code\\run_cst_reconstruction.py "
        f"--nearfield {display_path(nearfield, base_dir)} "
        f"--farfield {display_path(farfield, base_dir)} "
        f"--sample-id {sample_id} "
        f"--frequency-hz {float(row.frequency_hz):.0f} "
        f"--out-dir {display_path(out_dir, base_dir)}"
    )
    return args, display, out_dir


def read_metrics(out_dir: Path) -> dict[str, object]:
    path = out_dir / "cst_reconstruction_metrics.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run batch reconstruction for completed CST Level 1 cases.")
    parser.add_argument("--case-status", default=str(DEFAULT_CASE_STATUS), help="Path to level1_case_status.csv.")
    parser.add_argument("--base-dir", default=str(ROOT), help="Base directory used to resolve relative paths.")
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT), help="Root directory for per-case reconstruction outputs.")
    parser.add_argument("--batch-dir", default=str(DEFAULT_BATCH_DIR), help="Directory for batch summary files.")
    parser.add_argument(
        "--priority",
        choices=["required", "recommended", "optional", "all"],
        default="required",
        help="Which completed Level 1 cases to reconstruct.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Write the command queue without running reconstruction.")
    parser.add_argument("--require-cases", action="store_true", help="Return non-zero if no completed cases match the filter.")
    parser.add_argument("--stop-on-error", action="store_true", help="Stop at the first failed reconstruction.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir)
    out_root = Path(args.out_root)
    batch_dir = Path(args.batch_dir)
    batch_dir.mkdir(parents=True, exist_ok=True)

    status = load_case_status(Path(args.case_status))
    cases = filter_cases(status, args.priority)
    queue_rows: list[dict[str, object]] = []
    result_rows: list[dict[str, object]] = []

    for row in cases.itertuples(index=False):
        command_args, command_display, out_dir = command_for_case(row, base_dir, out_root)
        queue_rows.append(
            {
                "sample_id": row.sample_id,
                "priority": row.priority,
                "frequency_hz": float(row.frequency_hz),
                "out_dir": display_path(out_dir, base_dir),
                "command": command_display,
            }
        )
        if args.dry_run:
            result_rows.append({"sample_id": row.sample_id, "priority": row.priority, "exit_code": "", "status": "dry_run"})
            continue

        completed = subprocess.run(command_args, cwd=base_dir, check=False)  # noqa: S603
        metrics = read_metrics(out_dir)
        result = {
            "sample_id": row.sample_id,
            "priority": row.priority,
            "frequency_hz": float(row.frequency_hz),
            "exit_code": int(completed.returncode),
            "status": "ok" if completed.returncode == 0 else "failed",
            "out_dir": display_path(out_dir, base_dir),
            "nmse": metrics.get("nmse", ""),
            "correlation": metrics.get("correlation", ""),
            "main_lobe_error_deg": metrics.get("main_lobe_error_deg", ""),
            "metrics_json": display_path(out_dir / "cst_reconstruction_metrics.json", base_dir),
        }
        result_rows.append(result)
        if args.stop_on_error and completed.returncode != 0:
            break

    queue_columns = ["sample_id", "priority", "frequency_hz", "out_dir", "command"]
    result_columns = [
        "sample_id",
        "priority",
        "frequency_hz",
        "exit_code",
        "status",
        "out_dir",
        "nmse",
        "correlation",
        "main_lobe_error_deg",
        "metrics_json",
    ]
    queue_df = pd.DataFrame(queue_rows, columns=queue_columns)
    result_df = pd.DataFrame(result_rows, columns=result_columns)
    queue_df.to_csv(batch_dir / "level1_batch_reconstruction_queue.csv", index=False, encoding="utf-8-sig")
    result_df.to_csv(batch_dir / "level1_batch_reconstruction_results.csv", index=False, encoding="utf-8-sig")

    any_failures = bool(len(result_df) and (result_df.get("status") == "failed").any())
    summary = {
        "case_status": str(Path(args.case_status)),
        "priority": args.priority,
        "dry_run": bool(args.dry_run),
        "queued_cases": int(len(queue_df)),
        "completed_runs": int((result_df.get("status") == "ok").sum()) if "status" in result_df else 0,
        "failed_runs": int((result_df.get("status") == "failed").sum()) if "status" in result_df else 0,
        "queue_csv": str(batch_dir / "level1_batch_reconstruction_queue.csv"),
        "results_csv": str(batch_dir / "level1_batch_reconstruction_results.csv"),
    }
    (batch_dir / "level1_batch_reconstruction_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Level 1 batch reconstruction summary written to {batch_dir}")
    print(f"queued cases: {summary['queued_cases']}")
    print(f"completed runs: {summary['completed_runs']}")
    print(f"failed runs: {summary['failed_runs']}")
    if args.require_cases and not len(queue_df):
        print("no completed Level 1 cases matched the selected priority")
        return 2
    if any_failures:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
