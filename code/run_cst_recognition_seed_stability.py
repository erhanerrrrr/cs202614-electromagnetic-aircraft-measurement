from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from cst_io import read_table, validate_nearfield
from run_cst_recognition import build_feature_matrix, ensure_theta_phi
from run_cst_recognition_augmented_stress_test import evaluate_models, train_augmented_models
from run_cst_recognition_leave_one_family_out import (
    STRESS_CASE_FAMILIES,
    build_family_out_train_matrix,
    parse_held_out_families,
    test_cases_for,
)
from run_cst_recognition_stress_test import (
    DEFAULT_DECISION_MATRIX,
    DEFAULT_LABELS,
    DEFAULT_LAYOUTS,
    DEFAULT_NEARFIELD,
    ROOT,
    filter_case,
    frequencies_from_nearfield,
    load_decision_rows,
    load_layouts,
    parse_layout_candidates,
    perturb_nearfield,
    rel,
    split_indices,
)


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_seed_stability"
DEFAULT_SEEDS = [202614, 202615, 202616]
DEFAULT_HELD_OUT_FAMILIES = ["noise", "dropout"]


def parse_seeds(raw: str | None) -> list[int]:
    if not raw:
        return DEFAULT_SEEDS
    seeds = [int(item.strip()) for item in raw.split(",") if item.strip()]
    if not seeds:
        raise ValueError("--seeds was provided but no seed values were parsed")
    return seeds


def t_critical_95(n: int) -> float:
    lookup = {
        2: 12.706,
        3: 4.303,
        4: 3.182,
        5: 2.776,
        6: 2.571,
        7: 2.447,
        8: 2.365,
        9: 2.306,
        10: 2.262,
        11: 2.228,
        12: 2.201,
        13: 2.179,
        14: 2.160,
        15: 2.145,
        16: 2.131,
        17: 2.120,
        18: 2.110,
        19: 2.101,
        20: 2.093,
    }
    if n <= 1:
        return 0.0
    return lookup.get(n, 1.96)


def ci95(values: pd.Series) -> tuple[float, float, float]:
    arr = pd.to_numeric(values, errors="coerce").dropna().to_numpy(dtype=float)
    if arr.size == 0:
        return np.nan, np.nan, np.nan
    mean = float(np.mean(arr))
    if arr.size == 1:
        return mean, mean, 0.0
    std = float(np.std(arr, ddof=1))
    half_width = t_critical_95(int(arr.size)) * std / np.sqrt(arr.size)
    return max(0.0, mean - half_width), min(1.0, mean + half_width), std


def result_row(
    seed: int,
    candidate: str,
    held_out_family: str,
    stress: dict[str, Any],
    decision_rows: dict[str, dict[str, str]],
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
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    accuracy = float(best["accuracy"])
    return {
        "seed": int(seed),
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": "leave_one_stress_family_out_seed_stability",
        "held_out_family": held_out_family,
        "stress_family": STRESS_CASE_FAMILIES[str(stress["stress_case"])],
        "stress_case": str(stress["stress_case"]),
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
        "passes_085": bool(accuracy >= 0.85),
        "claim_boundary": decision.get("claim_boundary", ""),
        "stress_description": str(stress["description"]),
    }


def aggregate_results(results: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key, group in results.groupby(group_cols, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        row = {col: value for col, value in zip(group_cols, key)}
        lower, upper, std = ci95(group["best_accuracy"])
        worst = group.sort_values("best_accuracy", ascending=True).iloc[0]
        row.update(
            {
                "seed_count": int(group["seed"].nunique()),
                "row_count": int(group.shape[0]),
                "mean_accuracy": float(pd.to_numeric(group["best_accuracy"]).mean()),
                "std_accuracy": std,
                "ci95_low_accuracy": lower,
                "ci95_high_accuracy": upper,
                "min_accuracy": float(pd.to_numeric(group["best_accuracy"]).min()),
                "max_accuracy": float(pd.to_numeric(group["best_accuracy"]).max()),
                "worst_seed": int(worst["seed"]),
                "worst_case": str(worst["stress_case"]),
                "all_rows_pass_085": bool((pd.to_numeric(group["best_accuracy"]) >= 0.85).all()),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame, by_case: pd.DataFrame, by_layout: pd.DataFrame) -> dict[str, object]:
    worst = results.sort_values("best_accuracy", ascending=True).iloc[0]
    tightest_case = by_case.sort_values("min_accuracy", ascending=True).iloc[0]
    return {
        "seed_count": int(results["seed"].nunique()),
        "seeds": [int(value) for value in sorted(results["seed"].unique())],
        "layout_count": int(results["candidate"].nunique()),
        "held_out_family_count": int(results["held_out_family"].nunique()),
        "stress_case_count": int(results["stress_case"].nunique()),
        "row_count": int(results.shape[0]),
        "all_rows_pass_085": bool((pd.to_numeric(results["best_accuracy"]) >= 0.85).all()),
        "worst_row": {
            "seed": int(worst["seed"]),
            "candidate": str(worst["candidate"]),
            "held_out_family": str(worst["held_out_family"]),
            "stress_case": str(worst["stress_case"]),
            "best_accuracy": float(worst["best_accuracy"]),
            "best_macro_f1": float(worst["best_macro_f1"]),
        },
        "tightest_case_summary": {
            "candidate": str(tightest_case["candidate"]),
            "held_out_family": str(tightest_case["held_out_family"]),
            "stress_case": str(tightest_case["stress_case"]),
            "mean_accuracy": float(tightest_case["mean_accuracy"]),
            "min_accuracy": float(tightest_case["min_accuracy"]),
            "ci95_low_accuracy": float(tightest_case["ci95_low_accuracy"]),
            "ci95_high_accuracy": float(tightest_case["ci95_high_accuracy"]),
        },
        "layout_summaries": by_layout.to_dict(orient="records"),
        "case_summaries": by_case.to_dict(orient="records"),
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    by_case: pd.DataFrame,
    by_family: pd.DataFrame,
    by_layout: pd.DataFrame,
    inputs: dict[str, str],
) -> None:
    lines = [
        "# Level 2 Recognition Seed Stability",
        "",
        "This directory stores the repeated-seed follow-up for the G5",
        "leave-one-stress-family-out recognition check. The default run repeats",
        "held-out noise and dropout families across three random seeds, varying",
        "the stratified split and the stochastic perturbation draws.",
        "",
        "## Current Result",
        "",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}.",
        f"- Layouts tested: {summary['layout_count']}.",
        f"- Held-out families tested: {summary['held_out_family_count']}.",
        f"- Stress cases tested: {summary['stress_case_count']}.",
        f"- Total rows: {summary['row_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst single row: "
            f"seed `{summary['worst_row']['seed']}`, "
            f"`{summary['worst_row']['candidate']}` / "
            f"`{summary['worst_row']['held_out_family']}` / "
            f"`{summary['worst_row']['stress_case']}` with accuracy "
            f"`{summary['worst_row']['best_accuracy']:.3f}`."
        ),
        (
            "- Tightest case summary: "
            f"`{summary['tightest_case_summary']['candidate']}` / "
            f"`{summary['tightest_case_summary']['held_out_family']}` / "
            f"`{summary['tightest_case_summary']['stress_case']}`, "
            f"mean `{summary['tightest_case_summary']['mean_accuracy']:.3f}`, "
            f"min `{summary['tightest_case_summary']['min_accuracy']:.3f}`, "
            f"95% CI approx "
            f"[`{summary['tightest_case_summary']['ci95_low_accuracy']:.3f}`, "
            f"`{summary['tightest_case_summary']['ci95_high_accuracy']:.3f}`]."
        ),
        "",
        "## Family Summary",
        "",
        "| Held-out family | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Passes 0.85 |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in by_family.to_dict(orient="records"):
        lines.append(
            "| {family} | {seeds} | {rows} | {mean:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {passes} |".format(
                family=row["held_out_family"],
                seeds=int(row["seed_count"]),
                rows=int(row["row_count"]),
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                low=float(row["ci95_low_accuracy"]),
                high=float(row["ci95_high_accuracy"]),
                passes=str(row["all_rows_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Tightest Case Rows",
            "",
            "| Candidate | Family | Stress case | Seeds | Mean accuracy | Std | Min | 95% CI low | 95% CI high | Passes 0.85 |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in by_case.sort_values("min_accuracy", ascending=True).head(10).to_dict(orient="records"):
        lines.append(
            "| {candidate} | {family} | {case} | {seeds} | {mean:.3f} | {std:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {passes} |".format(
                candidate=row["candidate"],
                family=row["held_out_family"],
                case=row["stress_case"],
                seeds=int(row["seed_count"]),
                mean=float(row["mean_accuracy"]),
                std=float(row["std_accuracy"]),
                minv=float(row["min_accuracy"]),
                low=float(row["ci95_low_accuracy"]),
                high=float(row["ci95_high_accuracy"]),
                passes=str(row["all_rows_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Layout Summary",
            "",
            "| Candidate | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Passes 0.85 |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in by_layout.to_dict(orient="records"):
        lines.append(
            "| {candidate} | {seeds} | {rows} | {mean:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {passes} |".format(
                candidate=row["candidate"],
                seeds=int(row["seed_count"]),
                rows=int(row["row_count"]),
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                low=float(row["ci95_low_accuracy"]),
                high=float(row["ci95_high_accuracy"]),
                passes=str(row["all_rows_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `recognition_seed_stability_metrics.csv` | Per-seed/per-layout/per-stress accuracy and macro-F1. |",
            "| `recognition_seed_stability_by_case.csv` | Aggregated mean/std/min/95% CI by layout and stress case. |",
            "| `recognition_seed_stability_by_family.csv` | Aggregated stability by held-out family. |",
            "| `recognition_seed_stability_by_layout.csv` | Aggregated stability by layout. |",
            "| `recognition_seed_stability_summary.json` | Machine-readable summary, inputs, and aggregate tables. |",
            "| `README.md` | Human-facing interpretation and claim boundary. |",
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\run_cst_recognition_seed_stability.py",
            "```",
            "",
            "## Boundary",
            "",
            "This is still Level 2 CST-derived element-library evidence. It improves",
            "the statistical confidence of the internal perturbation checks, but it",
            "does not replace real measurement calibration, full-wave airframe",
            "validation, or the true CST near-field monitor gate.",
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
        description="Repeat focused leave-one-family recognition checks across random seeds.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument("--layout-candidates", default="", help="Comma-separated candidate list. Defaults to the G2 decision set.")
    parser.add_argument(
        "--held-out-families",
        default=",".join(DEFAULT_HELD_OUT_FAMILIES),
        help="Comma-separated subset of noise,phase,dropout,combined.",
    )
    parser.add_argument("--seeds", default=",".join(str(seed) for seed in DEFAULT_SEEDS), help="Comma-separated random seeds.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified held-out test split size.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    held_out_families = parse_held_out_families(args.held_out_families)
    seeds = parse_seeds(args.seeds)
    layout_ids = load_layouts(layouts_path, candidate_names)
    decision_rows = load_decision_rows(decision_path)

    raw_nearfield = read_table(nearfield_path)
    labels = read_table(labels_path)
    nf_report = validate_nearfield(raw_nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    nearfield = ensure_theta_phi(raw_nearfield)
    frequencies = frequencies_from_nearfield(nearfield)

    rows: list[dict[str, object]] = []
    for seed in seeds:
        for layout_index, candidate in enumerate(candidate_names):
            sensor_ids = layout_ids[candidate]
            clean_case = filter_case(nearfield, sensor_ids, frequencies)
            _, y, class_names, sample_ids, _ = build_feature_matrix(clean_case, labels)
            train_idx, test_idx = split_indices(y, args.test_size, seed)

            for family_index, held_out_family in enumerate(held_out_families):
                family_seed = seed + layout_index * 1000 + family_index * 179
                train_x, train_y, train_manifest = build_family_out_train_matrix(
                    clean_case=clean_case,
                    labels=labels,
                    train_idx=train_idx,
                    y=y,
                    sample_ids=sample_ids,
                    held_out_family=held_out_family,
                    seed=family_seed,
                )
                trained_models = train_augmented_models(train_x, train_y, seed)

                for stress_index, stress in enumerate(test_cases_for(held_out_family)):
                    stress_seed = seed + layout_index * 1000 + family_index * 179 + stress_index * 41
                    perturbed = perturb_nearfield(clean_case, stress, stress_seed)
                    test_x_full, y_perturbed, _, test_sample_ids, test_metadata = build_feature_matrix(
                        perturbed,
                        labels,
                    )
                    if sample_ids != test_sample_ids or not np.array_equal(y, y_perturbed):
                        raise ValueError(
                            f"sample order changed for seed={seed}/{candidate}/{held_out_family}/{stress['stress_case']}"
                        )
                    best, models = evaluate_models(
                        models=trained_models,
                        test_x=test_x_full[test_idx],
                        test_y=y[test_idx],
                        class_names=class_names,
                    )
                    row = result_row(
                        seed=seed,
                        candidate=candidate,
                        held_out_family=held_out_family,
                        stress=stress,
                        decision_rows=decision_rows,
                        sensor_count=len(sensor_ids),
                        frequency_count=len(frequencies),
                        feature_count=int(test_metadata["feature_count"]),
                        sample_count=int(test_metadata["sample_count"]),
                        base_train_count=len(train_idx),
                        augmented_train_count=train_x.shape[0],
                        test_count=len(test_idx),
                        augmentation_profile_count=len(train_manifest),
                        best=best,
                        models=models,
                    )
                    rows.append(row)
                    print(
                        f"seed={seed}/{candidate}/holdout={held_out_family}/{stress['stress_case']}: "
                        f"accuracy={float(best['accuracy']):.3f}"
                    )

    results = pd.DataFrame(rows)
    by_case = aggregate_results(results, ["candidate", "held_out_family", "stress_case"])
    by_family = aggregate_results(results, ["held_out_family"])
    by_layout = aggregate_results(results, ["candidate"])
    summary = summarize(results, by_case, by_layout)

    results.to_csv(out_dir / "recognition_seed_stability_metrics.csv", index=False, encoding="utf-8-sig")
    by_case.to_csv(out_dir / "recognition_seed_stability_by_case.csv", index=False, encoding="utf-8-sig")
    by_family.to_csv(out_dir / "recognition_seed_stability_by_family.csv", index=False, encoding="utf-8-sig")
    by_layout.to_csv(out_dir / "recognition_seed_stability_by_layout.csv", index=False, encoding="utf-8-sig")

    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_seed_stability.py",
        "purpose": "G5 repeated-seed stability check for focused leave-one-family recognition robustness.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "seeds": seeds,
        "held_out_families": held_out_families,
        "stress_case_families": STRESS_CASE_FAMILIES,
        "summary": summary,
        "by_case": by_case.to_dict(orient="records"),
        "by_family": by_family.to_dict(orient="records"),
        "by_layout": by_layout.to_dict(orient="records"),
        "boundary": (
            "Level 2 CST-derived element-library seed-stability evidence only. "
            "It does not replace real measurement calibration, full-wave airframe validation, "
            "or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_seed_stability_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary, by_case, by_family, by_layout, inputs)
    print(f"seed stability recognition check complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
