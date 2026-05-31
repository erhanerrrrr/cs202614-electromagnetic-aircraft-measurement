from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import time
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "submission"
FINAL_FILE_REL_PATHS = [
    ("final PDF", Path("01_report/solution_report.pdf")),
    ("final DOCX", Path("01_report/solution_report.docx")),
    ("final PPTX", Path("02_presentation/defense_slides.pptx")),
    ("final PPT PDF", Path("02_presentation/defense_slides.pdf")),
    ("final MP4", Path("03_video/demo_video.mp4")),
]
IGNORED_COPY_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    ".venv",
    "node_modules",
}
IGNORED_COPY_SUFFIXES = {".pyc", ".pyo", ".tmp", ".log"}


def final_file_state(out_dir: Path) -> tuple[int, int, str]:
    missing = [name for name, rel_path in FINAL_FILE_REL_PATHS if not (out_dir / rel_path).exists()]
    ready = len(FINAL_FILE_REL_PATHS) - len(missing)
    missing_text = ", ".join(missing) if missing else "none"
    return ready, len(FINAL_FILE_REL_PATHS), missing_text


def final_blocker_text(out_dir: Path) -> str:
    ready, total, missing_text = final_file_state(out_dir)
    if ready == total:
        return (
            "All required final delivery files are present. Human playback, administrative "
            "metadata,报名表, and final zip naming still need manual review before submission."
        )
    return (
        "Final delivery files are incomplete "
        f"({ready}/{total} ready; missing: {missing_text}); "
        "Level 1 angular/near-field model-boundary wording and Level 2 simplified "
        "structure-boundary wording remain to be finalized."
    )


def handle_remove_error(func, path: str, exc: BaseException) -> None:
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        func(path)
    except Exception:
        raise exc


def remove_tree(path: Path) -> None:
    for attempt in range(5):
        if not path.exists():
            return
        try:
            shutil.rmtree(path, onexc=handle_remove_error)
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def copy_file(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() == dst.resolve():
        return True
    shutil.copy2(src, dst)
    return True


def copy_dir(src: Path, dst: Path) -> bool:
    if not src.exists() or not src.is_dir():
        return False
    if dst.exists():
        remove_tree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=ignore_generated_files)
    return True


def ignore_generated_files(_src_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in IGNORED_COPY_NAMES or Path(name).suffix in IGNORED_COPY_SUFFIXES:
            ignored.add(name)
    return ignored


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def stage_file(rows: list[dict[str, object]], label: str, src: str, dst: str) -> None:
    ok = copy_file(ROOT / src, DEFAULT_OUT / dst)
    rows.append({"label": label, "source": src, "target": str(Path("submission") / dst), "status": "copied" if ok else "missing"})


def stage_dir(rows: list[dict[str, object]], label: str, src: str, dst: str) -> None:
    ok = copy_dir(ROOT / src, DEFAULT_OUT / dst)
    rows.append({"label": label, "source": src, "target": str(Path("submission") / dst), "status": "copied" if ok else "missing"})


def write_report_readme(out_dir: Path) -> None:
    content = """# Report folder

This is a draft staging folder. The final required files are:

- `solution_report.pdf`
- `solution_report.docx`

Current draft source:

- `solution_report_draft.md`

Do not treat this folder as final until Level 1 angular/near-field model-boundary notes, Level 2 simplified structure-boundary notes, and final report/PPT/video files are stable.
"""
    write_text(out_dir / "01_report" / "README_report_status.md", content)


def write_presentation_outline(out_dir: Path) -> None:
    content = """# Defense slides outline

The slide outline is currently maintained in `docs/final_submission_package_plan.md`.

Final required files:

- `defense_slides.pptx`
- `defense_slides.pdf`

Slides should be generated only after final CST figures, Level 1 model-boundary notes, and report wording are stable.
"""
    write_text(out_dir / "02_presentation" / "defense_slides_outline.md", content)


def write_video_script_stub(out_dir: Path) -> None:
    content = """# Demo video script draft

Use the video script skeleton in `docs/final_submission_package_plan.md`.

Final required file:

- `demo_video.mp4`

Record only after report/PPT metrics, CST screenshots, and code commands are aligned.
"""
    write_text(out_dir / "03_video" / "demo_script.md", content)


def build_draft(out_dir: Path) -> list[dict[str, object]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    stage_file(rows, "admin submission template", "docs/admin_submission_template.md", "00_admin/admin_submission_template.md")
    stage_file(rows, "report draft", "docs/solution_report_draft.md", "01_report/solution_report_draft.md")
    stage_file(rows, "final report PDF", "submission/01_report/solution_report.pdf", "01_report/solution_report.pdf")
    stage_file(rows, "final report DOCX", "submission/01_report/solution_report.docx", "01_report/solution_report.docx")
    write_report_readme(out_dir)
    rows.append({"label": "report status readme", "source": "generated", "target": "submission/01_report/README_report_status.md", "status": "generated"})

    stage_file(rows, "presentation plan", "docs/final_submission_package_plan.md", "02_presentation/final_submission_package_plan.md")
    stage_file(rows, "final defense PPTX", "submission/02_presentation/defense_slides.pptx", "02_presentation/defense_slides.pptx")
    stage_file(rows, "final defense PDF", "submission/02_presentation/defense_slides.pdf", "02_presentation/defense_slides.pdf")
    stage_dir(rows, "presentation package", "outputs/presentation_package", "02_presentation/presentation_package")
    write_presentation_outline(out_dir)
    rows.append({"label": "presentation outline", "source": "generated", "target": "submission/02_presentation/defense_slides_outline.md", "status": "generated"})

    stage_file(rows, "video plan", "docs/final_submission_package_plan.md", "03_video/final_submission_package_plan.md")
    stage_file(rows, "final demo video MP4", "submission/03_video/demo_video.mp4", "03_video/demo_video.mp4")
    stage_dir(rows, "video package", "outputs/presentation_package", "03_video/video_package")
    stage_dir(rows, "video artifact", "outputs/video_artifact", "03_video/video_artifact")
    write_video_script_stub(out_dir)
    rows.append({"label": "video script draft", "source": "generated", "target": "submission/03_video/demo_script.md", "status": "generated"})

    stage_dir(rows, "code src", "code", "04_code/src")
    stage_file(rows, "code README", "README.md", "04_code/README.md")
    stage_file(rows, "requirements", "requirements.txt", "04_code/requirements.txt")
    stage_file(rows, "reproduce commands", "docs/reproduce_commands.md", "04_code/reproduce_commands.md")
    stage_file(rows, "data dictionary", "docs/data_dictionary.md", "04_code/data_dictionary.md")

    stage_dir(rows, "Level 1 manifest", "outputs/cst_level1_plan", "05_cst/level1_manifest")
    stage_dir(rows, "Level 1 workpack", "outputs/cst_level1_workpack", "05_cst/level1_workpack")
    stage_dir(rows, "Level 1 CST project automation", "outputs/cst_real_level1_projects", "05_cst/level1_project_automation")
    stage_dir(rows, "Level 1 CST solver-safe projects", "outputs/cst_solver_ready_level1_projects", "05_cst/level1_solver_ready_projects")
    stage_dir(rows, "Level 1 CST solver trials", "outputs/cst_solver_trials", "05_cst/level1_solver_trials")
    stage_dir(rows, "Level 1 CST farfield exports", "outputs/cst_farfield_export", "05_cst/level1_farfield_export_logs")
    stage_dir(rows, "Level 1 analytic reference", "outputs/level1_analytic_reference", "05_cst/level1_analytic_reference")
    stage_dir(rows, "Level 1 merge report", "outputs/cst_level1_merge_report", "05_cst/level1_merge_report")
    stage_dir(rows, "Level 1 reconstruction batch", "outputs/cst_level1_reconstruction_batch", "05_cst/level1_reconstruction_batch")
    stage_dir(rows, "Level 1 angular calibration", "outputs/cst_level1_angular_calibration", "05_cst/level1_angular_calibration")
    stage_dir(rows, "Level 2 plan", "outputs/cst_level2_plan", "05_cst/level2_manifest")
    stage_dir(rows, "Level 2 workpack", "outputs/cst_level2_workpack", "05_cst/level2_workpack")
    stage_dir(rows, "Level 2 element library", "outputs/cst_level2_element_library", "05_cst/level2_element_library")
    stage_dir(rows, "Level 2 element solver trials", "outputs/cst_level2_element_trials", "05_cst/level2_element_solver_trials")
    stage_dir(rows, "Level 2 superposed export logs", "outputs/cst_level2_superposed_export", "05_cst/level2_superposed_export_logs")
    stage_dir(rows, "Level 2 merge report", "outputs/cst_level2_merge_report", "05_cst/level2_merge_report")
    stage_dir(rows, "Level 2 simplified structure comparison", "outputs/cst_structure_comparison", "05_cst/level2_structure_comparison")
    stage_dir(rows, "CST macro templates", "outputs/cst_macro_templates", "05_cst/macro_templates")
    stage_dir(rows, "CST execution dashboard", "outputs/cst_execution_dashboard", "05_cst/execution_dashboard")
    stage_dir(rows, "CST operator runbook", "outputs/cst_operator_runbook", "05_cst/operator_runbook")
    stage_dir(rows, "CST execution logs", "outputs/cst_execution_logs", "05_cst/execution_logs")
    stage_dir(rows, "CST export dropzone", "data/cst_exports", "06_data/cst_exports")

    stage_dir(rows, "phase conversion demo", "outputs/cst_phase_demo", "06_data/phase_conversion_demo")
    stage_dir(rows, "synthetic Level 1 dataset", "outputs/synthetic_cst_level1_dataset", "06_data/synthetic_cst_level1_dataset")
    stage_dir(rows, "synthetic recognition dataset", "outputs/synthetic_cst_dataset", "06_data/synthetic_cst_dataset")
    stage_dir(rows, "baseline outputs", "outputs/baseline", "06_data/processed_outputs/baseline")
    stage_dir(rows, "robustness outputs", "outputs/reconstruction_robustness", "06_data/processed_outputs/reconstruction_robustness")
    stage_dir(rows, "Level 1 angular calibration outputs", "outputs/cst_level1_angular_calibration", "06_data/processed_outputs/cst_level1_angular_calibration")
    stage_dir(rows, "Level 2 full48 recognition outputs", "outputs/cst_recognition_level2", "06_data/processed_outputs/cst_recognition_level2")
    stage_dir(rows, "Level 2 full48 ablation outputs", "outputs/cst_recognition_level2_ablation", "06_data/processed_outputs/cst_recognition_level2_ablation")
    stage_dir(rows, "Level 2 simplified structure comparison outputs", "outputs/cst_structure_comparison", "06_data/processed_outputs/cst_structure_comparison")
    stage_dir(rows, "Level 2 pilot recognition outputs", "outputs/cst_recognition_level2_pilot", "06_data/processed_outputs/cst_recognition_level2_pilot")
    stage_dir(rows, "Level 2 pilot ablation outputs", "outputs/cst_recognition_level2_pilot_ablation", "06_data/processed_outputs/cst_recognition_level2_pilot_ablation")
    stage_dir(rows, "report package outputs", "outputs/report_package", "06_data/metrics/report_package")
    stage_dir(rows, "scorecard outputs", "outputs/scorecard", "06_data/metrics/scorecard")
    stage_dir(rows, "problem requirements outputs", "outputs/problem_requirements", "06_data/metrics/problem_requirements")
    stage_dir(rows, "submission index outputs", "outputs/submission_index", "06_data/metrics/submission_index")
    stage_dir(rows, "completion audit outputs", "outputs/completion_audit", "06_data/metrics/completion_audit")
    stage_dir(rows, "master dashboard outputs", "outputs/master_dashboard", "06_data/metrics/master_dashboard")
    stage_dir(rows, "progress report outputs", "outputs/progress_report", "06_data/metrics/progress_report")

    stage_file(rows, "literature matrix", "docs/literature_matrix.md", "07_appendix/literature_matrix.md")
    stage_file(rows, "literature strategy", "docs/literature_screening_and_strategy.md", "07_appendix/literature_screening_and_strategy.md")
    stage_file(rows, "literature algorithm traceability", "docs/literature_to_algorithm_traceability.md", "07_appendix/literature_to_algorithm_traceability.md")
    stage_file(rows, "problem requirements matrix", "outputs/problem_requirements/problem_requirements_matrix.md", "07_appendix/problem_requirements_matrix.md")
    stage_file(rows, "scorecard", "outputs/scorecard/scorecard.md", "07_appendix/scorecard.md")
    stage_file(rows, "completion audit", "outputs/completion_audit/completion_audit.md", "07_appendix/completion_audit.md")
    stage_file(rows, "master dashboard", "outputs/master_dashboard/master_status_dashboard.md", "07_appendix/master_status_dashboard.md")
    stage_file(rows, "CST operator runbook", "outputs/cst_operator_runbook/README_cst_operator_runbook.md", "07_appendix/README_cst_operator_runbook.md")
    stage_file(rows, "data dictionary", "docs/data_dictionary.md", "07_appendix/data_dictionary.md")
    stage_file(rows, "final package plan", "docs/final_submission_package_plan.md", "07_appendix/final_submission_package_plan.md")
    stage_file(rows, "project file index", "docs/project_file_index.md", "07_appendix/project_file_index.md")
    stage_file(rows, "project progress report", "docs/project_progress_report.md", "07_appendix/project_progress_report.md")
    stage_file(
        rows,
        "current work detailed explanation",
        "docs/current_work_detailed_explanation.md",
        "07_appendix/current_work_detailed_explanation.md",
    )
    stage_dir(rows, "mentor progress reports", "docs/progress_reports", "07_appendix/progress_reports")
    stage_file(rows, "Level 1 sprint handoff", "docs/level1_cst_sprint_handoff.md", "07_appendix/level1_cst_sprint_handoff.md")
    stage_dir(rows, "stage notes", "docs/stage_notes", "07_appendix/stage_notes")

    return rows


def write_package_readme(out_dir: Path, rows: list[dict[str, object]]) -> None:
    copied = sum(1 for row in rows if row["status"] in {"copied", "generated"})
    missing = sum(1 for row in rows if row["status"] == "missing")
    final_blocker = final_blocker_text(out_dir)
    content = f"""# CS-202614 submission draft

This is a draft staging package generated from the current workspace.

It is not final because {final_blocker}

## Summary

- Generated/copied items: {copied}
- Missing source items: {missing}

## Final gates before submission

1. `python code\\merge_cst_level1_exports.py --strict`
2. `python code\\run_cst_level1_batch_reconstruction.py --require-cases`
3. `python code\\run_cst_level1_angular_calibration.py`
4. `python code\\merge_cst_level2_exports.py --strict`
5. Full Level 2 recognition and ablation complete.
6. `python code\\build_completion_audit.py` reports `completion_proven=true`.
7. Regenerate this draft with `python code\\build_submission_draft.py`.

See `07_appendix/completion_audit.md` for the current status.
"""
    write_text(out_dir / "README_submission_draft.md", content)


def main() -> None:
    global DEFAULT_OUT
    parser = argparse.ArgumentParser(description="Build a draft submission folder from current source artifacts.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Draft submission directory.")
    args = parser.parse_args()

    DEFAULT_OUT = Path(args.out_dir)
    rows = build_draft(DEFAULT_OUT)
    write_package_readme(DEFAULT_OUT, rows)

    df = pd.DataFrame(rows)
    df.to_csv(DEFAULT_OUT / "submission_draft_manifest.csv", index=False, encoding="utf-8-sig")
    summary = {
        "out_dir": str(DEFAULT_OUT),
        "item_count": int(len(df)),
        "copied_or_generated": int(df["status"].isin(["copied", "generated"]).sum()),
        "missing": int(df["status"].eq("missing").sum()),
        "is_final": False,
        "final_blocker": final_blocker_text(DEFAULT_OUT),
    }
    (DEFAULT_OUT / "submission_draft_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Submission draft written to {DEFAULT_OUT}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
