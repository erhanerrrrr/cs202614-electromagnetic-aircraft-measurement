from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score

from cst_io import read_table, validate_nearfield
from run_cst_recognition import build_feature_matrix, ensure_theta_phi
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
    make_models,
    parse_layout_candidates,
    perturb_nearfield,
    rel,
    split_indices,
    summarize_results,
)


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_augmented_robustness"
DEFAULT_CLEAN_BASELINE = (
    ROOT / "data" / "recognition_stress_tests" / "level2_robustness" / "recognition_stress_metrics.csv"
)


AUGMENTATION_CASES = STRESS_CASES


def load_clean_baseline(path: Path) -> dict[tuple[str, str], dict[str, object]]:
    if not path.exists():
        return {}
    baseline = pd.read_csv(path)
    rows: dict[tuple[str, str], dict[str, object]] = {}
    for row in baseline.to_dict(orient="records"):
        key = (str(row.get("candidate", "")), str(row.get("stress_case", "")))
        rows[key] = row
    return rows


def build_augmented_train_matrix(
    clean_case: pd.DataFrame,
    labels: pd.DataFrame,
    train_idx: np.ndarray,
    y: np.ndarray,
    sample_ids: list[str],
    seed: int,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    manifest: list[dict[str, object]] = []
    for aug_index, augmentation in enumerate(AUGMENTATION_CASES):
        aug_seed = seed + 10000 + aug_index * 113
        augmented = perturb_nearfield(clean_case, augmentation, aug_seed)
        aug_x, aug_y, _, aug_sample_ids, aug_metadata = build_feature_matrix(augmented, labels)
        if sample_ids != aug_sample_ids or not np.array_equal(y, aug_y):
            raise ValueError(f"sample order changed for augmentation {augmentation['stress_case']}")
        x_parts.append(aug_x[train_idx])
        y_parts.append(aug_y[train_idx])
        manifest.append(
            {
                "augmentation_case": str(augmentation["stress_case"]),
                "noise_snr_db": augmentation.get("noise_snr_db"),
                "phase_jitter_deg": float(augmentation.get("phase_jitter_deg") or 0.0),
                "dropout_fraction": float(augmentation.get("dropout_fraction") or 0.0),
                "train_rows_added": int(len(train_idx)),
                "feature_count": int(aug_metadata["feature_count"]),
            }
        )
    return np.vstack(x_parts), np.concatenate(y_parts), manifest


def train_augmented_models(train_x: np.ndarray, train_y: np.ndarray, seed: int) -> dict[str, object]:
    trained: dict[str, object] = {}
    for model_name, model in make_models(seed).items():
        model.fit(train_x, train_y)
        trained[model_name] = model
    return trained


def evaluate_models(
    models: dict[str, object],
    test_x: np.ndarray,
    test_y: np.ndarray,
    class_names: list[str],
) -> tuple[dict[str, object], dict[str, object]]:
    model_rows: dict[str, object] = {}
    best: dict[str, object] = {"model": "", "accuracy": -1.0, "macro_f1": -1.0}
    for model_name, model in models.items():
        pred = model.predict(test_x)
        accuracy = float(accuracy_score(test_y, pred))
        macro_f1 = float(f1_score(test_y, pred, average="macro", zero_division=0))
        model_rows[model_name] = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "classification_report": classification_report(
                test_y,
                pred,
                target_names=class_names,
                output_dict=True,
                zero_division=0,
            ),
        }
        if accuracy > float(best["accuracy"]):
            best = {"model": model_name, "accuracy": accuracy, "macro_f1": macro_f1}
    return best, model_rows


def result_row(
    candidate: str,
    decision_rows: dict[str, dict[str, str]],
    baseline_rows: dict[tuple[str, str], dict[str, object]],
    stress: dict[str, Any],
    sensor_count: int,
    frequency_count: int,
    feature_count: int,
    sample_count: int,
    base_train_count: int,
    augmented_train_count: int,
    test_count: int,
    augmentation_profile_count: int,
    best: dict[str, object],
    models: dict[str, object],
) -> dict[str, object]:
    decision = decision_rows.get(candidate, {})
    stress_case = str(stress["stress_case"])
    baseline = baseline_rows.get((candidate, stress_case), {})
    clean_accuracy = baseline.get("best_accuracy", "")
    clean_macro_f1 = baseline.get("best_macro_f1", "")
    accuracy = float(best["accuracy"])
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    if clean_accuracy == "":
        delta = ""
    else:
        delta = accuracy - float(clean_accuracy)
    return {
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": "perturbation_augmented",
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
        "augmentation_profile_count": int(augmentation_profile_count),
        "test_sample_count": int(test_count),
        "best_model": str(best["model"]),
        "best_accuracy": accuracy,
        "best_macro_f1": float(best["macro_f1"]),
        "svm_accuracy": float(svm.get("accuracy", np.nan)),
        "svm_macro_f1": float(svm.get("macro_f1", np.nan)),
        "random_forest_accuracy": float(forest.get("accuracy", np.nan)),
        "random_forest_macro_f1": float(forest.get("macro_f1", np.nan)),
        "clean_train_accuracy": clean_accuracy,
        "clean_train_macro_f1": clean_macro_f1,
        "accuracy_delta_vs_clean_train": delta,
        "passes_085": bool(accuracy >= 0.85),
        "claim_boundary": decision.get("claim_boundary", ""),
        "stress_description": str(stress["description"]),
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    rows: list[dict[str, object]],
    inputs: dict[str, str],
    augmentation_manifest: list[dict[str, object]],
) -> None:
    failing_rows = sorted(
        [row for row in rows if not bool(row["passes_085"])],
        key=lambda row: float(row["best_accuracy"]),
    )
    deltas = [
        float(row["accuracy_delta_vs_clean_train"])
        for row in rows
        if row["accuracy_delta_vs_clean_train"] != ""
    ]
    mean_delta = float(np.mean(deltas)) if deltas else 0.0
    lines = [
        "# Level 2 Augmented Recognition Stress Test",
        "",
        "This directory stores the perturbation-aware training follow-up to the",
        "clean-train Level 2 stress test. The held-out test split and stress cases",
        "are unchanged; only the training set is expanded with clean, noise, phase",
        "jitter, dropout, and combined perturbation variants of the training samples.",
        "",
        "## Current Result",
        "",
        f"- Layouts tested: {summary['layout_count']}.",
        f"- Stress cases per layout: {summary['stress_case_count']}.",
        f"- Augmentation profiles per layout: {len(augmentation_manifest)}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst case: "
            f"`{summary['worst_case']['candidate']}` / `{summary['worst_case']['stress_case']}` "
            f"with accuracy `{summary['worst_case']['best_accuracy']:.3f}`."
        ),
        f"- Mean accuracy delta vs clean-train baseline: `{mean_delta:+.3f}`.",
        "",
        "## Layout Summary",
        "",
        "| Candidate | Sensors | Recommendation | Clean accuracy | Worst accuracy | Worst case | Passes 0.85 |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for row in summary["layouts"]:
        clean_acc = row["clean_accuracy"]
        lines.append(
            "| {candidate} | {sensor_count} | {recommendation} | {clean} | {worst:.3f} | {worst_case} | {passes} |".format(
                candidate=row["candidate"],
                sensor_count=row["sensor_count"],
                recommendation=row["recommendation"],
                clean="n/a" if clean_acc is None else f"{clean_acc:.3f}",
                worst=float(row["worst_accuracy"]),
                worst_case=row["worst_case"],
                passes=str(row["all_cases_pass_085"]).lower(),
            )
        )
    lines.extend(["", "## Rows Below 0.85", ""])
    if failing_rows:
        lines.extend(
            [
                "| Candidate | Stress case | Accuracy | Macro-F1 | Best model | Delta vs clean-train |",
                "|---|---|---:|---:|---|---:|",
            ]
        )
        for row in failing_rows:
            delta = row["accuracy_delta_vs_clean_train"]
            lines.append(
                "| {candidate} | {stress_case} | {accuracy:.3f} | {macro_f1:.3f} | {best_model} | {delta} |".format(
                    candidate=row["candidate"],
                    stress_case=row["stress_case"],
                    accuracy=float(row["best_accuracy"]),
                    macro_f1=float(row["best_macro_f1"]),
                    best_model=row["best_model"],
                    delta="n/a" if delta == "" else f"{float(delta):+.3f}",
                )
            )
    else:
        lines.append("No tested row falls below the `0.85` threshold.")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `recognition_augmented_stress_metrics.csv` | Per-layout/per-stress accuracy and macro-F1 after perturbation-aware training. |",
            "| `recognition_augmented_stress_summary.json` | Machine-readable summary, inputs, augmentation profiles, and detailed model reports. |",
            "| `README.md` | Human-facing interpretation and claim boundary. |",
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\run_cst_recognition_augmented_stress_test.py",
            "```",
            "",
            "## Boundary",
            "",
            "This is an augmentation experiment on Level 2 CST-derived element-library",
            "data. It is evidence that compound measurement-error sensitivity can be",
            "reduced by perturbation-aware training. It is not full-wave complex-airframe",
            "validation and does not replace the true CST near-field monitor gate.",
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
        description="Run perturbation-aware training follow-up for CST Level 2 recognition stress tests.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument("--clean-baseline", default=str(DEFAULT_CLEAN_BASELINE), help="Clean-train stress metrics CSV.")
    parser.add_argument("--layout-candidates", default="", help="Comma-separated candidate list. Defaults to the G2 decision set.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified held-out test split size.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    clean_baseline_path = Path(args.clean_baseline)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    layout_ids = load_layouts(layouts_path, candidate_names)
    decision_rows = load_decision_rows(decision_path)
    baseline_rows = load_clean_baseline(clean_baseline_path)

    raw_nearfield = read_table(nearfield_path)
    labels = read_table(labels_path)
    nf_report = validate_nearfield(raw_nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    nearfield = ensure_theta_phi(raw_nearfield)
    frequencies = frequencies_from_nearfield(nearfield)

    rows: list[dict[str, object]] = []
    details: dict[str, object] = {}
    augmentation_manifest: list[dict[str, object]] = []
    for layout_index, candidate in enumerate(candidate_names):
        sensor_ids = layout_ids[candidate]
        clean_case = filter_case(nearfield, sensor_ids, frequencies)
        clean_x, y, class_names, sample_ids, clean_metadata = build_feature_matrix(clean_case, labels)
        train_idx, test_idx = split_indices(y, args.test_size, args.seed)
        train_x, train_y, candidate_aug_manifest = build_augmented_train_matrix(
            clean_case=clean_case,
            labels=labels,
            train_idx=train_idx,
            y=y,
            sample_ids=sample_ids,
            seed=args.seed + layout_index * 1000,
        )
        if not augmentation_manifest:
            augmentation_manifest = candidate_aug_manifest
        trained_models = train_augmented_models(train_x, train_y, args.seed)

        details[candidate] = {
            "class_names": class_names,
            "sample_ids": sample_ids,
            "clean_feature_metadata": clean_metadata,
            "augmentation_manifest": candidate_aug_manifest,
            "base_train_sample_count": int(len(train_idx)),
            "augmented_train_sample_count": int(train_x.shape[0]),
            "test_sample_count": int(len(test_idx)),
            "stress_cases": {},
        }

        for stress_index, stress in enumerate(STRESS_CASES):
            stress_seed = args.seed + layout_index * 1000 + stress_index * 37
            perturbed = perturb_nearfield(clean_case, stress, stress_seed)
            test_x_full, y_perturbed, _, test_sample_ids, test_metadata = build_feature_matrix(perturbed, labels)
            if sample_ids != test_sample_ids or not np.array_equal(y, y_perturbed):
                raise ValueError(f"sample order changed after perturbation for {candidate}/{stress['stress_case']}")
            best, models = evaluate_models(
                models=trained_models,
                test_x=test_x_full[test_idx],
                test_y=y[test_idx],
                class_names=class_names,
            )
            row = result_row(
                candidate=candidate,
                decision_rows=decision_rows,
                baseline_rows=baseline_rows,
                stress=stress,
                sensor_count=len(sensor_ids),
                frequency_count=len(frequencies),
                feature_count=int(test_metadata["feature_count"]),
                sample_count=int(test_metadata["sample_count"]),
                base_train_count=len(train_idx),
                augmented_train_count=train_x.shape[0],
                test_count=len(test_idx),
                augmentation_profile_count=len(candidate_aug_manifest),
                best=best,
                models=models,
            )
            rows.append(row)
            details[candidate]["stress_cases"][str(stress["stress_case"])] = {
                "best": best,
                "models": models,
                "feature_metadata": test_metadata,
            }
            delta = row["accuracy_delta_vs_clean_train"]
            delta_text = "n/a" if delta == "" else f"{float(delta):+.3f}"
            print(
                f"{candidate}/{stress['stress_case']}: "
                f"accuracy={float(best['accuracy']):.3f}, delta={delta_text}"
            )

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "recognition_augmented_stress_metrics.csv", index=False, encoding="utf-8-sig")

    summary = summarize_results(results)
    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
        "clean_baseline": rel(clean_baseline_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_augmented_stress_test.py",
        "purpose": "G5 perturbation-aware training follow-up for Level 2 recognition robustness.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "augmentation_cases": AUGMENTATION_CASES,
        "stress_cases": STRESS_CASES,
        "summary": summary,
        "details": details,
        "boundary": (
            "Level 2 CST-derived element-library augmentation evidence only. "
            "It does not replace true-monitor reconstruction gates or full-wave complex-airframe validation."
        ),
    }
    (out_dir / "recognition_augmented_stress_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary, rows, inputs, augmentation_manifest)
    print(f"augmented recognition stress test complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
