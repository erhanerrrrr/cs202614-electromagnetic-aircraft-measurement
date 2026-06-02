from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from cst_io import read_table, validate_nearfield
from run_cst_recognition import build_feature_matrix, ensure_theta_phi
from run_cst_recognition_augmented_stress_test import (
    DEFAULT_CLEAN_BASELINE,
    evaluate_models,
    load_clean_baseline,
    train_augmented_models,
)
from run_cst_recognition_stress_test import (
    DEFAULT_DECISION_MATRIX,
    DEFAULT_LABELS,
    DEFAULT_LAYOUTS,
    DEFAULT_NEARFIELD,
    ROOT,
    STRESS_CASES,
    filter_case,
    frequencies_from_nearfield,
    load_decision_rows,
    load_layouts,
    parse_layout_candidates,
    perturb_nearfield,
    rel,
    split_indices,
)


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_leave_one_family_out"
DEFAULT_FULL_AUGMENTED_BASELINE = (
    ROOT
    / "data"
    / "recognition_stress_tests"
    / "level2_augmented_robustness"
    / "recognition_augmented_stress_metrics.csv"
)

STRESS_CASE_FAMILIES = {
    "clean": "clean",
    "noise_20db": "noise",
    "noise_10db": "noise",
    "phase_15deg": "phase",
    "phase_45deg": "phase",
    "dropout_10pct": "dropout",
    "dropout_25pct": "dropout",
    "noise10_phase15_dropout10": "combined",
}

DEFAULT_HELD_OUT_FAMILIES = ["noise", "phase", "dropout", "combined"]


def stress_family(stress: dict[str, Any]) -> str:
    name = str(stress["stress_case"])
    if name not in STRESS_CASE_FAMILIES:
        raise KeyError(f"stress case {name!r} has no family mapping")
    return STRESS_CASE_FAMILIES[name]


def parse_held_out_families(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_HELD_OUT_FAMILIES
    families = [item.strip() for item in raw.split(",") if item.strip()]
    valid = set(DEFAULT_HELD_OUT_FAMILIES)
    unknown = sorted(set(families) - valid)
    if unknown:
        raise ValueError(f"unknown held-out stress families: {unknown}; valid choices are {sorted(valid)}")
    return families


def training_cases_for(held_out_family: str) -> list[dict[str, Any]]:
    cases = [stress for stress in STRESS_CASES if stress_family(stress) != held_out_family]
    if not any(stress_family(stress) == "clean" for stress in cases):
        raise ValueError("clean augmentation case must remain in every leave-one-family-out training set")
    return cases


def test_cases_for(held_out_family: str) -> list[dict[str, Any]]:
    cases = [stress for stress in STRESS_CASES if stress_family(stress) == held_out_family]
    if not cases:
        raise ValueError(f"held-out family {held_out_family!r} has no stress cases")
    return cases


def build_family_out_train_matrix(
    clean_case: pd.DataFrame,
    labels: pd.DataFrame,
    train_idx: np.ndarray,
    y: np.ndarray,
    sample_ids: list[str],
    held_out_family: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    manifest: list[dict[str, object]] = []
    for aug_index, augmentation in enumerate(training_cases_for(held_out_family)):
        aug_seed = seed + 20000 + aug_index * 137
        augmented = perturb_nearfield(clean_case, augmentation, aug_seed)
        aug_x, aug_y, _, aug_sample_ids, aug_metadata = build_feature_matrix(augmented, labels)
        if sample_ids != aug_sample_ids or not np.array_equal(y, aug_y):
            raise ValueError(
                f"sample order changed for {held_out_family} training case {augmentation['stress_case']}"
            )
        x_parts.append(aug_x[train_idx])
        y_parts.append(aug_y[train_idx])
        manifest.append(
            {
                "augmentation_case": str(augmentation["stress_case"]),
                "augmentation_family": stress_family(augmentation),
                "noise_snr_db": augmentation.get("noise_snr_db"),
                "phase_jitter_deg": float(augmentation.get("phase_jitter_deg") or 0.0),
                "dropout_fraction": float(augmentation.get("dropout_fraction") or 0.0),
                "train_rows_added": int(len(train_idx)),
                "feature_count": int(aug_metadata["feature_count"]),
            }
        )
    return np.vstack(x_parts), np.concatenate(y_parts), manifest


def result_row(
    candidate: str,
    decision_rows: dict[str, dict[str, str]],
    clean_baseline_rows: dict[tuple[str, str], dict[str, object]],
    full_augmented_rows: dict[tuple[str, str], dict[str, object]],
    held_out_family: str,
    train_manifest: list[dict[str, object]],
    stress: dict[str, Any],
    sensor_count: int,
    frequency_count: int,
    feature_count: int,
    sample_count: int,
    base_train_count: int,
    augmented_train_count: int,
    test_count: int,
    best: dict[str, object],
    models: dict[str, object],
) -> dict[str, object]:
    decision = decision_rows.get(candidate, {})
    stress_case = str(stress["stress_case"])
    clean_baseline = clean_baseline_rows.get((candidate, stress_case), {})
    full_augmented = full_augmented_rows.get((candidate, stress_case), {})
    accuracy = float(best["accuracy"])
    clean_accuracy = clean_baseline.get("best_accuracy", "")
    full_augmented_accuracy = full_augmented.get("best_accuracy", "")
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    train_families = sorted({str(row["augmentation_family"]) for row in train_manifest})
    return {
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": "leave_one_stress_family_out",
        "held_out_family": held_out_family,
        "train_families": "|".join(train_families),
        "stress_family": stress_family(stress),
        "stress_case": stress_case,
        "sensor_count": int(sensor_count),
        "frequency_count": int(frequency_count),
        "noise_snr_db": "" if stress.get("noise_snr_db") is None else float(stress["noise_snr_db"]),
        "phase_jitter_deg": float(stress.get("phase_jitter_deg") or 0.0),
        "dropout_fraction": float(stress.get("dropout_fraction") or 0.0),
        "feature_count": int(feature_count),
        "sample_count": int(sample_count),
        "base_train_sample_count": int(base_train_count),
        "augmented_train_sample_count": int(augmented_train_count),
        "augmentation_profile_count": int(len(train_manifest)),
        "test_sample_count": int(test_count),
        "best_model": str(best["model"]),
        "best_accuracy": accuracy,
        "best_macro_f1": float(best["macro_f1"]),
        "svm_accuracy": float(svm.get("accuracy", np.nan)),
        "svm_macro_f1": float(svm.get("macro_f1", np.nan)),
        "random_forest_accuracy": float(forest.get("accuracy", np.nan)),
        "random_forest_macro_f1": float(forest.get("macro_f1", np.nan)),
        "clean_train_accuracy": clean_accuracy,
        "full_augmented_accuracy": full_augmented_accuracy,
        "accuracy_delta_vs_clean_train": "" if clean_accuracy == "" else accuracy - float(clean_accuracy),
        "accuracy_delta_vs_full_augmented": (
            "" if full_augmented_accuracy == "" else accuracy - float(full_augmented_accuracy)
        ),
        "passes_085": bool(accuracy >= 0.85),
        "claim_boundary": decision.get("claim_boundary", ""),
        "stress_description": str(stress["description"]),
    }


def summarize_leave_one_results(results: pd.DataFrame) -> dict[str, object]:
    family_rows: list[dict[str, object]] = []
    for family, group in results.groupby("held_out_family", sort=False):
        worst = group.sort_values("best_accuracy", ascending=True).iloc[0]
        family_rows.append(
            {
                "held_out_family": str(family),
                "stress_case_count": int(group["stress_case"].nunique()),
                "row_count": int(group.shape[0]),
                "mean_accuracy": float(group["best_accuracy"].mean()),
                "worst_accuracy": float(group["best_accuracy"].min()),
                "worst_case": f"{worst['candidate']}/{worst['stress_case']}",
                "all_cases_pass_085": bool((group["best_accuracy"] >= 0.85).all()),
            }
        )

    layout_rows: list[dict[str, object]] = []
    for candidate, group in results.groupby("candidate", sort=False):
        worst = group.sort_values("best_accuracy", ascending=True).iloc[0]
        layout_rows.append(
            {
                "candidate": str(candidate),
                "sensor_count": int(group["sensor_count"].iloc[0]),
                "recommendation": str(group["recommendation"].iloc[0]),
                "worst_accuracy": float(group["best_accuracy"].min()),
                "worst_case": f"{worst['held_out_family']}/{worst['stress_case']}",
                "all_cases_pass_085": bool((group["best_accuracy"] >= 0.85).all()),
            }
        )

    worst = results.sort_values("best_accuracy", ascending=True).iloc[0]
    return {
        "layout_count": int(results["candidate"].nunique()),
        "held_out_family_count": int(results["held_out_family"].nunique()),
        "stress_case_count": int(results["stress_case"].nunique()),
        "row_count": int(results.shape[0]),
        "all_rows_pass_085": bool((results["best_accuracy"] >= 0.85).all()),
        "worst_case": {
            "candidate": str(worst["candidate"]),
            "held_out_family": str(worst["held_out_family"]),
            "stress_case": str(worst["stress_case"]),
            "best_accuracy": float(worst["best_accuracy"]),
            "best_macro_f1": float(worst["best_macro_f1"]),
        },
        "families": family_rows,
        "layouts": layout_rows,
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    rows: list[dict[str, object]],
    inputs: dict[str, str],
    family_manifests: dict[str, list[dict[str, object]]],
) -> None:
    failing_rows = sorted(
        [row for row in rows if not bool(row["passes_085"])],
        key=lambda row: float(row["best_accuracy"]),
    )
    full_augmented_deltas = [
        float(row["accuracy_delta_vs_full_augmented"])
        for row in rows
        if row["accuracy_delta_vs_full_augmented"] != ""
    ]
    min_full_augmented_delta = min(full_augmented_deltas) if full_augmented_deltas else 0.0
    lines = [
        "# Level 2 Leave-One-Stress-Family-Out Recognition Test",
        "",
        "This directory stores the next G5 robustness check after full",
        "perturbation-aware training. For each run, one stress family is withheld",
        "from augmentation, models train on clean plus the remaining known",
        "families, and the held-out test split is evaluated on the unseen family.",
        "",
        "## Current Result",
        "",
        f"- Layouts tested: {summary['layout_count']}.",
        f"- Held-out families tested: {summary['held_out_family_count']}.",
        f"- Held-out stress cases: {summary['stress_case_count']}.",
        f"- Total layout/family/stress rows: {summary['row_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst case: "
            f"`{summary['worst_case']['candidate']}` / "
            f"`{summary['worst_case']['held_out_family']}` / "
            f"`{summary['worst_case']['stress_case']}` with accuracy "
            f"`{summary['worst_case']['best_accuracy']:.3f}`."
        ),
        f"- Minimum delta vs full augmented training: `{min_full_augmented_delta:+.3f}`.",
        "",
        "## Held-Out Family Summary",
        "",
        "| Held-out family | Stress cases | Rows | Mean accuracy | Worst accuracy | Worst row | Passes 0.85 |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for row in summary["families"]:
        lines.append(
            "| {family} | {case_count} | {row_count} | {mean:.3f} | {worst:.3f} | {worst_case} | {passes} |".format(
                family=row["held_out_family"],
                case_count=row["stress_case_count"],
                row_count=row["row_count"],
                mean=float(row["mean_accuracy"]),
                worst=float(row["worst_accuracy"]),
                worst_case=row["worst_case"],
                passes=str(row["all_cases_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Layout Summary",
            "",
            "| Candidate | Sensors | Recommendation | Worst accuracy | Worst case | Passes 0.85 |",
            "|---|---:|---|---:|---|---|",
        ]
    )
    for row in summary["layouts"]:
        lines.append(
            "| {candidate} | {sensor_count} | {recommendation} | {worst:.3f} | {worst_case} | {passes} |".format(
                candidate=row["candidate"],
                sensor_count=row["sensor_count"],
                recommendation=row["recommendation"],
                worst=float(row["worst_accuracy"]),
                worst_case=row["worst_case"],
                passes=str(row["all_cases_pass_085"]).lower(),
            )
        )

    lines.extend(["", "## Rows Below 0.85", ""])
    if failing_rows:
        lines.extend(
            [
                "| Candidate | Held-out family | Stress case | Accuracy | Macro-F1 | Best model |",
                "|---|---|---|---:|---:|---|",
            ]
        )
        for row in failing_rows:
            lines.append(
                "| {candidate} | {family} | {stress_case} | {accuracy:.3f} | {macro_f1:.3f} | {best_model} |".format(
                    candidate=row["candidate"],
                    family=row["held_out_family"],
                    stress_case=row["stress_case"],
                    accuracy=float(row["best_accuracy"]),
                    macro_f1=float(row["best_macro_f1"]),
                    best_model=row["best_model"],
                )
            )
    else:
        lines.append("No tested row falls below the `0.85` threshold.")

    lines.extend(
        [
            "",
            "## Training Manifests",
            "",
            "| Held-out family | Augmentation cases used in training |",
            "|---|---|",
        ]
    )
    for family, manifest in family_manifests.items():
        cases = ", ".join(str(row["augmentation_case"]) for row in manifest)
        lines.append(f"| {family} | {cases} |")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `recognition_leave_one_family_metrics.csv` | Per-layout/per-held-out-family recognition accuracy and macro-F1. |",
            "| `recognition_leave_one_family_summary.json` | Machine-readable summary, training manifests, inputs, and model reports. |",
            "| `README.md` | Human-facing interpretation and claim boundary. |",
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\run_cst_recognition_leave_one_family_out.py",
            "```",
            "",
            "## Boundary",
            "",
            "This is a stronger internal generalization check than full augmentation",
            "because each tested family is unseen during augmentation. It is still",
            "Level 2 CST-derived element-library evidence, not real measurement",
            "calibration, full-wave airframe scattering validation, or a replacement",
            "for the true CST near-field monitor gate.",
            "",
            "## Inputs",
            "",
        ]
    )
    for name, path in inputs.items():
        lines.append(f"- {name}: `{path}`")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run leave-one-stress-family-out recognition robustness checks for CST Level 2 data.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument("--clean-baseline", default=str(DEFAULT_CLEAN_BASELINE), help="Clean-train stress metrics CSV.")
    parser.add_argument(
        "--full-augmented-baseline",
        default=str(DEFAULT_FULL_AUGMENTED_BASELINE),
        help="Full perturbation-aware stress metrics CSV.",
    )
    parser.add_argument("--layout-candidates", default="", help="Comma-separated candidate list. Defaults to the G2 decision set.")
    parser.add_argument(
        "--held-out-families",
        default="",
        help="Comma-separated subset of noise,phase,dropout,combined. Defaults to all four.",
    )
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified held-out test split size.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    clean_baseline_path = Path(args.clean_baseline)
    full_augmented_path = Path(args.full_augmented_baseline)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    held_out_families = parse_held_out_families(args.held_out_families)
    layout_ids = load_layouts(layouts_path, candidate_names)
    decision_rows = load_decision_rows(decision_path)
    clean_baseline_rows = load_clean_baseline(clean_baseline_path)
    full_augmented_rows = load_clean_baseline(full_augmented_path)

    raw_nearfield = read_table(nearfield_path)
    labels = read_table(labels_path)
    nf_report = validate_nearfield(raw_nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    nearfield = ensure_theta_phi(raw_nearfield)
    frequencies = frequencies_from_nearfield(nearfield)

    rows: list[dict[str, object]] = []
    details: dict[str, object] = {}
    family_manifests: dict[str, list[dict[str, object]]] = {}
    for layout_index, candidate in enumerate(candidate_names):
        sensor_ids = layout_ids[candidate]
        clean_case = filter_case(nearfield, sensor_ids, frequencies)
        _, y, class_names, sample_ids, clean_metadata = build_feature_matrix(clean_case, labels)
        train_idx, test_idx = split_indices(y, args.test_size, args.seed)

        details[candidate] = {
            "class_names": class_names,
            "sample_ids": sample_ids,
            "clean_feature_metadata": clean_metadata,
            "base_train_sample_count": int(len(train_idx)),
            "test_sample_count": int(len(test_idx)),
            "held_out_families": {},
        }

        for family_index, held_out_family in enumerate(held_out_families):
            train_seed = args.seed + layout_index * 1000 + family_index * 179
            train_x, train_y, train_manifest = build_family_out_train_matrix(
                clean_case=clean_case,
                labels=labels,
                train_idx=train_idx,
                y=y,
                sample_ids=sample_ids,
                held_out_family=held_out_family,
                seed=train_seed,
            )
            family_manifests.setdefault(held_out_family, train_manifest)
            trained_models = train_augmented_models(train_x, train_y, args.seed)
            details[candidate]["held_out_families"][held_out_family] = {
                "training_manifest": train_manifest,
                "augmented_train_sample_count": int(train_x.shape[0]),
                "stress_cases": {},
            }

            for stress_index, stress in enumerate(test_cases_for(held_out_family)):
                stress_seed = args.seed + layout_index * 1000 + family_index * 179 + stress_index * 41
                perturbed = perturb_nearfield(clean_case, stress, stress_seed)
                test_x_full, y_perturbed, _, test_sample_ids, test_metadata = build_feature_matrix(
                    perturbed,
                    labels,
                )
                if sample_ids != test_sample_ids or not np.array_equal(y, y_perturbed):
                    raise ValueError(
                        f"sample order changed for {candidate}/{held_out_family}/{stress['stress_case']}"
                    )
                best, models = evaluate_models(
                    models=trained_models,
                    test_x=test_x_full[test_idx],
                    test_y=y[test_idx],
                    class_names=class_names,
                )
                row = result_row(
                    candidate=candidate,
                    decision_rows=decision_rows,
                    clean_baseline_rows=clean_baseline_rows,
                    full_augmented_rows=full_augmented_rows,
                    held_out_family=held_out_family,
                    train_manifest=train_manifest,
                    stress=stress,
                    sensor_count=len(sensor_ids),
                    frequency_count=len(frequencies),
                    feature_count=int(test_metadata["feature_count"]),
                    sample_count=int(test_metadata["sample_count"]),
                    base_train_count=len(train_idx),
                    augmented_train_count=train_x.shape[0],
                    test_count=len(test_idx),
                    best=best,
                    models=models,
                )
                rows.append(row)
                details[candidate]["held_out_families"][held_out_family]["stress_cases"][
                    str(stress["stress_case"])
                ] = {
                    "best": best,
                    "models": models,
                    "feature_metadata": test_metadata,
                }
                delta = row["accuracy_delta_vs_full_augmented"]
                delta_text = "n/a" if delta == "" else f"{float(delta):+.3f}"
                print(
                    f"{candidate}/holdout={held_out_family}/{stress['stress_case']}: "
                    f"accuracy={float(best['accuracy']):.3f}, delta_full_aug={delta_text}"
                )

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "recognition_leave_one_family_metrics.csv", index=False, encoding="utf-8-sig")

    summary = summarize_leave_one_results(results)
    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
        "clean_baseline": rel(clean_baseline_path),
        "full_augmented_baseline": rel(full_augmented_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_leave_one_family_out.py",
        "purpose": "G5 leave-one-stress-family-out generalization check for Level 2 recognition robustness.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "stress_case_families": STRESS_CASE_FAMILIES,
        "held_out_families": held_out_families,
        "summary": summary,
        "family_manifests": family_manifests,
        "details": details,
        "boundary": (
            "Level 2 CST-derived element-library leave-one-family evidence only. "
            "It does not replace real measurement calibration, full-wave airframe validation, "
            "or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_leave_one_family_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary, rows, inputs, family_manifests)
    print(f"leave-one-family recognition stress test complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
