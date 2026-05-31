from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from cst_io import read_table, validate_farfield, validate_nearfield, validate_pair


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "outputs" / "cst_level2_plan" / "level2_case_manifest.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "cst_exports" / "level2"
DEFAULT_REPORT_DIR = ROOT / "outputs" / "cst_level2_merge_report"


def resolve_path(path_text: str, base_dir: Path) -> Path:
    path = Path(str(path_text).strip())
    if path.is_absolute():
        return path
    return base_dir / path


def report_validation(prefix: str, report) -> dict[str, object]:
    return {
        f"{prefix}_ok": bool(report.ok),
        f"{prefix}_errors": " | ".join(report.errors),
        f"{prefix}_warnings": " | ".join(report.warnings),
    }


def expected_rows(manifest: pd.DataFrame, sample_id: str, frequency_hz: float, col: str) -> int:
    mask = (manifest["sample_id"].astype(str) == sample_id) & (
        pd.to_numeric(manifest["frequency_hz"], errors="coerce").astype(float) == float(frequency_hz)
    )
    values = pd.to_numeric(manifest.loc[mask, col], errors="coerce").dropna()
    return int(values.iloc[0]) if len(values) else 0


def count_rows(df: pd.DataFrame, sample_id: str, frequency_hz: float) -> int:
    if df.empty or "sample_id" not in df.columns or "frequency_hz" not in df.columns:
        return 0
    sample = df["sample_id"].astype(str).str.strip()
    freq = pd.to_numeric(df["frequency_hz"], errors="coerce").astype(float)
    return int(((sample == sample_id) & (freq == float(frequency_hz))).sum())


def read_optional_table(path: Path) -> tuple[pd.DataFrame | None, str]:
    if not path.exists():
        return None, "missing"
    try:
        return read_table(path), "read"
    except Exception as exc:  # noqa: BLE001
        return None, f"read_error: {exc}"


def analyze_sample(
    sample_id: str,
    sample_manifest: pd.DataFrame,
    base_dir: Path,
) -> tuple[pd.DataFrame | None, pd.DataFrame | None, list[dict[str, object]], dict[str, object]]:
    nearfield_path = resolve_path(str(sample_manifest["nearfield_export"].iloc[0]), base_dir)
    farfield_path = resolve_path(str(sample_manifest["farfield_export"].iloc[0]), base_dir)
    expected_freqs = sorted(pd.to_numeric(sample_manifest["frequency_hz"], errors="coerce").dropna().astype(float).unique())

    nearfield, nearfield_status = read_optional_table(nearfield_path)
    farfield, farfield_status = read_optional_table(farfield_path)

    sample_summary: dict[str, object] = {
        "sample_id": sample_id,
        "class_label": str(sample_manifest["class_label"].iloc[0]),
        "nearfield_path": str(nearfield_path),
        "farfield_path": str(farfield_path),
        "nearfield_file_status": nearfield_status,
        "farfield_file_status": farfield_status,
        "expected_frequency_count": int(len(expected_freqs)),
    }

    nearfield_ok = False
    farfield_ok = False
    if nearfield is not None:
        nf_report = validate_nearfield(nearfield)
        sample_summary.update(report_validation("nearfield", nf_report))
        nearfield_ok = nf_report.ok
    else:
        sample_summary.update({"nearfield_ok": False, "nearfield_errors": nearfield_status, "nearfield_warnings": ""})

    if farfield is not None:
        ff_report = validate_farfield(farfield)
        sample_summary.update(report_validation("farfield", ff_report))
        farfield_ok = ff_report.ok
        if nearfield is not None and nearfield_ok and ff_report.ok:
            pair_report = validate_pair(nearfield, farfield)
            sample_summary.update(report_validation("pair", pair_report))
        else:
            sample_summary.update({"pair_ok": False, "pair_errors": "nearfield/farfield not both valid", "pair_warnings": ""})
    else:
        sample_summary.update({"farfield_ok": False, "farfield_errors": farfield_status, "farfield_warnings": ""})
        sample_summary.update({"pair_ok": False, "pair_errors": "farfield missing", "pair_warnings": ""})

    frequency_rows: list[dict[str, object]] = []
    for frequency_hz in expected_freqs:
        expected_nf = expected_rows(sample_manifest, sample_id, frequency_hz, "expected_nearfield_rows_per_frequency")
        expected_ff = expected_rows(sample_manifest, sample_id, frequency_hz, "expected_farfield_rows_per_frequency")
        nearfield_rows = count_rows(nearfield, sample_id, frequency_hz) if nearfield is not None else 0
        farfield_rows = count_rows(farfield, sample_id, frequency_hz) if farfield is not None else 0
        frequency_rows.append(
            {
                "sample_id": sample_id,
                "class_label": str(sample_manifest["class_label"].iloc[0]),
                "frequency_hz": int(round(frequency_hz)),
                "nearfield_expected_rows": expected_nf,
                "nearfield_rows": nearfield_rows,
                "nearfield_complete": bool(nearfield_rows == expected_nf and nearfield_ok),
                "farfield_expected_rows": expected_ff,
                "farfield_rows": farfield_rows,
                "farfield_complete": bool(farfield_rows == expected_ff and farfield_ok),
            }
        )

    sample_summary["nearfield_complete"] = bool(all(row["nearfield_complete"] for row in frequency_rows))
    sample_summary["farfield_complete"] = bool(all(row["farfield_complete"] for row in frequency_rows))
    sample_summary["sample_complete"] = bool(sample_summary["nearfield_complete"] and sample_summary["farfield_complete"])
    sample_summary["nearfield_rows_total"] = int(sum(row["nearfield_rows"] for row in frequency_rows))
    sample_summary["farfield_rows_total"] = int(sum(row["farfield_rows"] for row in frequency_rows))
    return nearfield, farfield, frequency_rows, sample_summary


def write_if_available(frames: list[pd.DataFrame], out_path: Path) -> int:
    if not frames:
        return 0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    return int(len(merged))


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge and audit CST Level 2 near-field/far-field exports.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to level2_case_manifest.csv.")
    parser.add_argument("--base-dir", default=str(ROOT), help="Base directory used to resolve relative export paths.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Directory for all_nearfield.csv/all_farfield.csv.")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for audit CSV/JSON reports.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero if any planned export is missing or incomplete.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    base_dir = Path(args.base_dir)
    out_dir = Path(args.out_dir)
    report_dir = Path(args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    manifest = read_table(manifest_path)
    required = {
        "sample_id",
        "class_label",
        "frequency_hz",
        "nearfield_export",
        "farfield_export",
        "expected_nearfield_rows_per_frequency",
        "expected_farfield_rows_per_frequency",
    }
    missing = sorted(required - set(manifest.columns))
    if missing:
        raise ValueError(f"manifest missing required columns: {missing}")

    nearfield_frames: list[pd.DataFrame] = []
    farfield_frames: list[pd.DataFrame] = []
    sample_rows: list[dict[str, object]] = []
    frequency_rows: list[dict[str, object]] = []

    for sample_id, sample_manifest in manifest.groupby(manifest["sample_id"].astype(str).str.strip(), sort=True):
        nearfield, farfield, freq_report, sample_summary = analyze_sample(sample_id, sample_manifest, base_dir)
        if nearfield is not None:
            nearfield_frames.append(nearfield)
        if farfield is not None:
            farfield_frames.append(farfield)
        frequency_rows.extend(freq_report)
        sample_rows.append(sample_summary)

    sample_report = pd.DataFrame(sample_rows)
    frequency_report = pd.DataFrame(frequency_rows)
    sample_report.to_csv(report_dir / "level2_sample_status.csv", index=False, encoding="utf-8-sig")
    frequency_report.to_csv(report_dir / "level2_frequency_completeness.csv", index=False, encoding="utf-8-sig")

    nearfield_out = out_dir / "all_nearfield.csv"
    farfield_out = out_dir / "all_farfield.csv"
    merged_nearfield_rows = write_if_available(nearfield_frames, nearfield_out)
    merged_farfield_rows = write_if_available(farfield_frames, farfield_out)

    all_complete = bool(sample_report["sample_complete"].all()) if len(sample_report) else False
    summary = {
        "manifest": str(manifest_path),
        "base_dir": str(base_dir),
        "planned_samples": int(sample_report.shape[0]),
        "complete_samples": int(sample_report["sample_complete"].sum()) if len(sample_report) else 0,
        "planned_sample_frequency_rows": int(frequency_report.shape[0]),
        "complete_nearfield_frequency_rows": int(frequency_report["nearfield_complete"].sum()) if len(frequency_report) else 0,
        "complete_farfield_frequency_rows": int(frequency_report["farfield_complete"].sum()) if len(frequency_report) else 0,
        "merged_nearfield_rows": merged_nearfield_rows,
        "merged_farfield_rows": merged_farfield_rows,
        "nearfield_out": str(nearfield_out) if merged_nearfield_rows else "",
        "farfield_out": str(farfield_out) if merged_farfield_rows else "",
        "all_complete": all_complete,
        "strict_mode": bool(args.strict),
        "next_commands_if_complete": [
            f"python code\\check_cst_export.py --nearfield {nearfield_out} --farfield {farfield_out}",
            f"python code\\run_cst_recognition.py --nearfield {nearfield_out} --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2",
            f"python code\\run_cst_recognition_ablation.py --nearfield {nearfield_out} --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2_ablation",
        ],
    }
    (report_dir / "level2_merge_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Level 2 merge/audit report written to {report_dir}")
    print(f"planned samples: {summary['planned_samples']}")
    print(f"complete samples: {summary['complete_samples']}")
    print(f"merged nearfield rows: {merged_nearfield_rows}")
    print(f"merged farfield rows: {merged_farfield_rows}")
    if args.strict and not all_complete:
        print("strict mode: incomplete exports detected")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
