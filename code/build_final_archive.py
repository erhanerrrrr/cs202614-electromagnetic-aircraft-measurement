from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"
OUT = ROOT / "outputs" / "final_archive"
ARCHIVE = OUT / "CS-202614_submission.zip"
MANIFEST = OUT / "final_archive_manifest.csv"
SUMMARY = OUT / "final_archive_summary.json"
README_FINAL = SUBMISSION / "README_FINAL_SUBMISSION.md"

EXPECTED_FILES = [
    SUBMISSION / "01_report" / "solution_report.pdf",
    SUBMISSION / "01_report" / "solution_report.docx",
    SUBMISSION / "02_presentation" / "defense_slides.pptx",
    SUBMISSION / "02_presentation" / "defense_slides.pdf",
    SUBMISSION / "03_video" / "demo_video.mp4",
    SUBMISSION / "04_code" / "src",
    SUBMISSION / "05_cst",
    SUBMISSION / "06_data",
    SUBMISSION / "07_appendix",
]

IGNORE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORE_SUFFIXES = {".pyc", ".pyo", ".tmp", ".log"}


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_NAMES for part in path.parts) or path.suffix in IGNORE_SUFFIXES


def iter_submission_files() -> list[Path]:
    files = [path for path in SUBMISSION.rglob("*") if path.is_file() and not should_skip(path)]
    return sorted(files, key=lambda item: item.relative_to(SUBMISSION).as_posix().lower())


def write_final_readme() -> None:
    completion = read_json(ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json")
    master = read_json(ROOT / "outputs" / "master_dashboard" / "master_dashboard_summary.json")
    video = read_json(ROOT / "outputs" / "video_artifact" / "demo_video_summary.json")
    content = f"""# CS-202614 Final Submission Package

This directory is the current final technical package for CS-202614.

## Auto-Audit Status

| Item | Value |
|---|---|
| completion_proven | `{completion.get("completion_proven", False)}` |
| complete / partial / missing gates | `{completion.get("complete", 0)} / {completion.get("partial", 0)} / {completion.get("missing", 0)}` |
| submission_ready | `{master.get("submission_ready", 0)}` |
| submission_blocked | `{master.get("submission_blocked", 0)}` |
| video_has_narration | `{video.get("has_narration", False)}` |
| video_duration_seconds_planned | `{video.get("planned_duration_seconds", "unknown")}` |

## Core Files

- `01_report/solution_report.pdf`
- `01_report/solution_report.docx`
- `02_presentation/defense_slides.pptx`
- `02_presentation/defense_slides.pdf`
- `03_video/demo_video.mp4`
- `04_code/src`
- `05_cst`
- `06_data`
- `07_appendix`

## Manual Checks Before Upload

- Play `03_video/demo_video.mp4` from start to end. The current generated version is an auto-timed silent PowerPoint video.
- Replace the video with a narrated screen recording if the contest requires spoken explanation.
- Fill in school, applicant, team, phone, email, and registration-form information according to the contest system.
- Rename the final archive according to the contest naming rule if the organizer requires a school/name prefix.
- Confirm that the PDF opens normally on another machine.

## Evidence Notes

- Level 1 angular calibration is FarfieldPlot-derived solver-safe angular consistency, not a claim of full-wave near-field monitor inversion.
- Level 2 structure evidence is a simplified aircraft occlusion transfer on CST-derived element-library data, not full-wave airframe scattering.
"""
    README_FINAL.write_text(content, encoding="utf-8")


def build_archive() -> dict[str, object]:
    OUT.mkdir(parents=True, exist_ok=True)
    write_final_readme()
    files = iter_submission_files()
    rows: list[dict[str, object]] = []
    total_size = 0

    for path in files:
        rel = path.relative_to(SUBMISSION).as_posix()
        size = path.stat().st_size
        total_size += size
        rows.append(
            {
                "relative_path": rel,
                "size_bytes": size,
                "sha256": sha256_file(path),
            }
        )

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["relative_path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in files:
            zf.write(path, arcname=f"CS-202614_submission/{path.relative_to(SUBMISSION).as_posix()}")

    expected_missing = [str(path.relative_to(ROOT)) for path in EXPECTED_FILES if not path.exists()]
    archive_hash = sha256_file(ARCHIVE)
    summary = {
        "archive": str(ARCHIVE.relative_to(ROOT)),
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "file_count": len(files),
        "total_uncompressed_bytes": total_size,
        "archive_size_bytes": ARCHIVE.stat().st_size,
        "archive_sha256": archive_hash,
        "expected_missing": expected_missing,
        "completion_proven": read_json(ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json").get(
            "completion_proven", False
        ),
        "manual_submission_items_remaining": [
            "human playback of demo_video.mp4",
            "school/team/applicant/contact metadata",
            "registration form",
            "organizer-specific archive naming",
        ],
        "is_final_archive": not expected_missing,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    if not SUBMISSION.exists():
        raise FileNotFoundError(f"Submission directory does not exist: {SUBMISSION}")
    summary = build_archive()
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
