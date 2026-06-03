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
from run_cst_recognition_dropout_mitigation import (
    STRATEGIES,
    add_zero_fill_deltas,
    aggregate_with_delta,
    build_strategy_feature_matrix,
    parse_strategies,
    summarize,
)
from run_cst_recognition_instrument_error import INSTRUMENT_ERROR_CASES, apply_instrument_error
from run_cst_recognition_seed_stability import parse_seeds
from run_cst_recognition_stress_test import (
    DEFAULT_DECISION_MATRIX,
    DEFAULT_LABELS,
    DEFAULT_LAYOUTS,
    DEFAULT_LAYOUT_CANDIDATES,
    DEFAULT_NEARFIELD,
    ROOT,
    STRESS_CASES,
    filter_case,
    frequencies_from_nearfield,
    load_decision_rows,
    load_layouts,
    parse_layout_candidates,
    rel,
    split_indices,
)
from run_cst_recognition_structured_dropout import (
    STRUCTURED_DROPOUT_CASES,
    apply_structured_dropout,
    build_known_augmentation_train_matrix,
    observed_missing_fraction,
)


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_compound_stress"
DEFAULT_SEEDS = [202614, 202615, 202616]
DEFAULT_COMPOUND_CASES = [
    "sensor_gain3db_sensor_node_dropout25pct",
    "mixed_amp_phase_sensor_node_dropout25pct",
    "mixed_amp_phase_azimuth_sector60deg",
    "polarization_imbalance_pair_dropout10pct",
]

COMPOUND_STRESS_CASES: list[dict[str, Any]] = [
    {
        "stress_case": "sensor_gain3db_sensor_node_dropout25pct",
        "instrument_case": "sensor_gain_bias_3db",
        "structured_dropout_case": "sensor_node_dropout_25pct",
        "description": "Severe per-sensor amplitude bias combined with 25 percent correlated sensor-node dropout.",
    },
    {
        "stress_case": "mixed_amp_phase_sensor_node_dropout25pct",
        "instrument_case": "mixed_amp_phase_bias",
        "structured_dropout_case": "sensor_node_dropout_25pct",
        "description": "Mixed amplitude/phase calibration bias combined with 25 percent correlated sensor-node dropout.",
    },
    {
        "stress_case": "mixed_amp_phase_azimuth_sector60deg",
        "instrument_case": "mixed_amp_phase_bias",
        "structured_dropout_case": "azimuth_sector_dropout_60deg",
        "description": "Mixed amplitude/phase calibration bias combined with a contiguous 60 degree azimuth-sector dropout.",
    },
    {
        "stress_case": "polarization_imbalance_pair_dropout10pct",
        "instrument_case": "polarization_imbalance_2db",
        "structured_dropout_case": "polarization_pair_dropout_10pct",
        "description": "Theta/phi amplitude imbalance combined with paired polarization dropout at sensor-frequency channels.",
    },
]


def parse_compound_cases(raw: str | None) -> list[dict[str, Any]]:
    lookup = {case["stress_case"]: case for case in COMPOUND_STRESS_CASES}
    names = DEFAULT_COMPOUND_CASES if not raw else [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(names) - set(lookup))
    if unknown:
        raise ValueError(f"unknown compound stress cases: {unknown}; valid choices are {sorted(lookup)}")
    if not names:
        raise ValueError("--compound-cases was provided but no case names were parsed")
    return [lookup[name] for name in names]


def apply_compound_stress(
    case_nearfield: pd.DataFrame,
    stress: dict[str, Any],
    seed: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    instrument_lookup = {case["stress_case"]: case for case in INSTRUMENT_ERROR_CASES}
    structured_lookup = {case["stress_case"]: case for case in STRUCTURED_DROPOUT_CASES}
    instrument_case = instrument_lookup[str(stress["instrument_case"])]
    structured_case = structured_lookup[str(stress["structured_dropout_case"])]

    instrumented, instrument_info = apply_instrument_error(case_nearfield, instrument_case, seed + 17)
    perturbed, dropout_info = apply_structured_dropout(instrumented, structured_case, seed + 31)
    info: dict[str, object] = {
        "instrument_case": str(instrument_case["stress_case"]),
        "structured_dropout_case": str(structured_case["stress_case"]),
        "instrument_description": str(instrument_case["description"]),
        "structured_dropout_description": str(structured_case["description"]),
    }
    info.update(instrument_info)
    info.update(dropout_info)
    return perturbed, info


def result_row(
    seed: int,
    candidate: str,
    strategy: str,
    stress: dict[str, Any],
    compound_info: dict[str, object],
    decision_rows: dict[str, dict[str, str]],
    sensor_count: int,
    frequency_count: int,
    feature_metadata: dict[str, object],
    sample_count: int,
    base_train_count: int,
    augmented_train_count: int,
    test_count: int,
    augmentation_profile_count: int,
    observed_missing: float,
    best: dict[str, object],
    models: dict[str, object],
) -> dict[str, object]:
    decision = decision_rows.get(candidate, {})
    accuracy = float(best["accuracy"])
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    return {
        "seed": int(seed),
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": "known_perturbation_augmented_compound_test",
        "strategy": strategy,
        "imputation": str(feature_metadata["imputation"]),
        "dropout_mask_features": bool(feature_metadata["dropout_mask_features"]),
        "held_out_family": "compound_instrument_dropout",
        "stress_family": "compound_instrument_dropout",
        "stress_case": str(stress["stress_case"]),
        "instrument_case": str(compound_info["instrument_case"]),
        "structured_dropout_case": str(compound_info["structured_dropout_case"]),
        "dropout_mode": str(compound_info["dropout_mode"]),
        "target_dropout_fraction": float(compound_info["target_dropout_fraction"]),
        "sector_width_deg": float(compound_info["sector_width_deg"]),
        "zeroed_row_fraction": float(compound_info["zeroed_row_fraction"]),
        "observed_missing_channel_fraction": float(observed_missing),
        "mean_selected_entity_count": float(compound_info["mean_selected_entity_count"]),
        "mean_selected_sensor_count": float(compound_info["mean_selected_sensor_count"]),
        "mean_sector_center_deg": compound_info["mean_sector_center_deg"],
        "global_gain_sigma_db": float(compound_info["global_gain_sigma_db"]),
        "sensor_gain_sigma_db": float(compound_info["sensor_gain_sigma_db"]),
        "frequency_slope_pp_db": float(compound_info["frequency_slope_pp_db"]),
        "polarization_imbalance_sigma_db": float(compound_info["polarization_imbalance_sigma_db"]),
        "sensor_phase_sigma_deg": float(compound_info["sensor_phase_sigma_deg"]),
        "frequency_phase_slope_pp_deg": float(compound_info["frequency_phase_slope_pp_deg"]),
        "mean_abs_gain_db": float(compound_info["mean_abs_gain_db"]),
        "p95_abs_gain_db": float(compound_info["p95_abs_gain_db"]),
        "max_abs_gain_db": float(compound_info["max_abs_gain_db"]),
        "mean_abs_phase_deg": float(compound_info["mean_abs_phase_deg"]),
        "p95_abs_phase_deg": float(compound_info["p95_abs_phase_deg"]),
        "max_abs_phase_deg": float(compound_info["max_abs_phase_deg"]),
        "sensor_count": int(sensor_count),
        "frequency_count": int(frequency_count),
        "noise_snr_db": "",
        "phase_jitter_deg": 0.0,
        "dropout_fraction": float(compound_info["target_dropout_fraction"]),
        "feature_count": int(feature_metadata["feature_count"]),
        "base_feature_count": int(feature_metadata["base_feature_count"]),
        "mask_feature_count": int(feature_metadata["mask_feature_count"]),
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
        "instrument_description": str(compound_info["instrument_description"]),
        "structured_dropout_description": str(compound_info["structured_dropout_description"]),
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    by_strategy: pd.DataFrame,
    by_case: pd.DataFrame,
    inputs: dict[str, str],
    regenerate_command: str,
) -> None:
    worst = summary["worst_row"]
    tightest = summary["tightest_case_summary"]
    lines = [
        "# Level 2 Compound Instrument-Dropout Check",
        "",
        "This directory stores the G5 severe compound stress follow-up for Level 2",
        "recognition. Models are trained with the existing clean, noise, phase,",
        "random-dropout, and combined perturbation profiles, then tested on unseen",
        "compound cases that apply correlated instrument bias and structured",
        "missing-channel patterns together.",
        "",
        "## Current Result",
        "",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}.",
        f"- Layouts tested: {', '.join(summary['layouts'])}.",
        f"- Strategies tested: {', '.join(summary['strategies'])}.",
        f"- Compound cases tested: {', '.join(summary['stress_cases'])}.",
        f"- Total rows: {summary['row_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst row: "
            f"`{worst['candidate']}` / `{worst['strategy']}` / `{worst['stress_case']}` "
            f"at accuracy `{float(worst['best_accuracy']):.3f}`."
        ),
        (
            "- Tightest aggregate: "
            f"`{tightest['candidate']}` / `{tightest['strategy']}` / `{tightest['stress_case']}` "
            f"with mean accuracy `{float(tightest['mean_accuracy']):.3f}` and "
            f"minimum `{float(tightest['min_accuracy']):.3f}`."
        ),
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs zero-fill | Passes 0.85 |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in by_strategy.to_dict(orient="records"):
        lines.append(
            "| {strategy} | {mean:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {delta:+.3f} | {passes} |".format(
                strategy=row["strategy"],
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                low=float(row["ci95_low_accuracy"]),
                high=float(row["ci95_high_accuracy"]),
                delta=float(row["mean_delta_vs_zero_fill"]),
                passes=str(row["all_rows_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Tightest Case Rows",
            "",
            "| Candidate | Stress case | Strategy | Mean accuracy | Min accuracy | Mean delta vs zero-fill | Passes 0.85 |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in by_case.sort_values(["min_accuracy", "mean_accuracy"], ascending=True).head(12).to_dict(
        orient="records"
    ):
        lines.append(
            "| {candidate} | {case} | {strategy} | {mean:.3f} | {minv:.3f} | {delta:+.3f} | {passes} |".format(
                candidate=row["candidate"],
                case=row["stress_case"],
                strategy=row["strategy"],
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                delta=float(row["mean_delta_vs_zero_fill"]),
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
            "| `recognition_compound_stress_metrics.csv` | Per-seed/per-layout/per-strategy compound stress accuracy and macro-F1. |",
            "| `recognition_compound_stress_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |",
            "| `recognition_compound_stress_by_case.csv` | Aggregate comparison by layout, compound case, and strategy. |",
            "| `recognition_compound_stress_by_layout.csv` | Aggregate comparison by layout and strategy. |",
            "| `recognition_compound_stress_summary.json` | Machine-readable summary, inputs, compound cases, strategy definitions, and aggregate tables. |",
            "| `README.md` | Human-facing interpretation and claim boundary. |",
            "",
            "## Regenerate",
            "",
            "```powershell",
            regenerate_command,
            "```",
            "",
            "## Boundary",
            "",
            "This is a Level 2 CST-derived element-library compound stress check.",
            "It tests simulated correlated instrument bias plus structured missing",
            "channels. It does not replace real instrument calibration, full-wave",
            "airframe validation, or the true CST near-field monitor gate.",
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
        description="Test Level 2 recognition under compound instrument-bias and structured-dropout stress cases.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument(
        "--layout-candidates",
        default=",".join(DEFAULT_LAYOUT_CANDIDATES),
        help="Comma-separated candidate list. Defaults to all five G2 representative layouts.",
    )
    parser.add_argument(
        "--compound-cases",
        default=",".join(DEFAULT_COMPOUND_CASES),
        help="Comma-separated compound stress case list.",
    )
    parser.add_argument(
        "--strategies",
        default=",".join(STRATEGIES),
        help="Comma-separated mitigation strategies.",
    )
    parser.add_argument("--seeds", default=",".join(str(seed) for seed in DEFAULT_SEEDS), help="Comma-separated seeds.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified held-out test split size.")
    parser.add_argument("--zero-tolerance", type=float, default=1e-30, help="Magnitude below this is treated as missing.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    compound_cases = parse_compound_cases(args.compound_cases)
    strategies = parse_strategies(args.strategies)
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
    manifests: dict[str, list[dict[str, object]]] = {}
    for seed in seeds:
        for layout_index, candidate in enumerate(candidate_names):
            sensor_ids = layout_ids[candidate]
            clean_case = filter_case(nearfield, sensor_ids, frequencies)
            _, y, class_names, sample_ids, _ = build_feature_matrix(clean_case, labels)
            train_idx, test_idx = split_indices(y, args.test_size, seed)
            base_seed = seed + layout_index * 1000

            for strategy in strategies:
                train_x, train_y, train_manifest = build_known_augmentation_train_matrix(
                    clean_case=clean_case,
                    labels=labels,
                    train_idx=train_idx,
                    y=y,
                    sample_ids=sample_ids,
                    strategy=strategy,
                    seed=base_seed,
                    zero_tolerance=args.zero_tolerance,
                )
                manifests.setdefault(strategy, train_manifest)
                trained_models = train_augmented_models(train_x, train_y, seed)

                for stress_index, stress in enumerate(compound_cases):
                    stress_seed = base_seed + stress_index * 59
                    perturbed, compound_info = apply_compound_stress(clean_case, stress, stress_seed)
                    observed_missing = observed_missing_fraction(perturbed, args.zero_tolerance)
                    test_x_full, y_perturbed, _, test_sample_ids, test_metadata = build_strategy_feature_matrix(
                        perturbed,
                        labels,
                        strategy,
                        args.zero_tolerance,
                    )
                    if sample_ids != test_sample_ids or not np.array_equal(y, y_perturbed):
                        raise ValueError(
                            f"sample order changed for seed={seed}/{candidate}/{strategy}/{stress['stress_case']}"
                        )
                    best, models = evaluate_models(
                        models=trained_models,
                        test_x=test_x_full[test_idx],
                        test_y=y[test_idx],
                        class_names=class_names,
                    )
                    rows.append(
                        result_row(
                            seed=seed,
                            candidate=candidate,
                            strategy=strategy,
                            stress=stress,
                            compound_info=compound_info,
                            decision_rows=decision_rows,
                            sensor_count=len(sensor_ids),
                            frequency_count=len(frequencies),
                            feature_metadata=test_metadata,
                            sample_count=int(test_metadata["sample_count"]),
                            base_train_count=len(train_idx),
                            augmented_train_count=train_x.shape[0],
                            test_count=len(test_idx),
                            augmentation_profile_count=len(train_manifest),
                            observed_missing=observed_missing,
                            best=best,
                            models=models,
                        )
                    )
                    print(
                        f"seed={seed}/{candidate}/{strategy}/{stress['stress_case']}: "
                        f"accuracy={float(best['accuracy']):.3f}"
                    )

    results = add_zero_fill_deltas(pd.DataFrame(rows))
    by_strategy = aggregate_with_delta(results, ["strategy"])
    by_case = aggregate_with_delta(results, ["candidate", "stress_case", "strategy"])
    by_layout = aggregate_with_delta(results, ["candidate", "strategy"])
    summary = summarize(results, by_case, by_strategy)
    tightest_case = by_case.sort_values(["min_accuracy", "mean_accuracy"], ascending=True).iloc[0]
    summary["tightest_case_summary"] = {
        "candidate": str(tightest_case["candidate"]),
        "strategy": str(tightest_case["strategy"]),
        "stress_case": str(tightest_case["stress_case"]),
        "mean_accuracy": float(tightest_case["mean_accuracy"]),
        "min_accuracy": float(tightest_case["min_accuracy"]),
        "mean_delta_vs_zero_fill": float(tightest_case["mean_delta_vs_zero_fill"]),
    }

    results.to_csv(out_dir / "recognition_compound_stress_metrics.csv", index=False, encoding="utf-8-sig")
    by_strategy.to_csv(out_dir / "recognition_compound_stress_by_strategy.csv", index=False, encoding="utf-8-sig")
    by_case.to_csv(out_dir / "recognition_compound_stress_by_case.csv", index=False, encoding="utf-8-sig")
    by_layout.to_csv(out_dir / "recognition_compound_stress_by_layout.csv", index=False, encoding="utf-8-sig")

    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_compound_stress.py",
        "purpose": "G5 severe compound instrument-bias plus structured-dropout robustness check.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "seeds": seeds,
        "compound_stress_cases": compound_cases,
        "instrument_error_cases": INSTRUMENT_ERROR_CASES,
        "structured_dropout_cases": STRUCTURED_DROPOUT_CASES,
        "strategies": STRATEGIES,
        "zero_tolerance": float(args.zero_tolerance),
        "training_cases": STRESS_CASES,
        "training_manifests": manifests,
        "summary": summary,
        "by_strategy": by_strategy.to_dict(orient="records"),
        "by_case": by_case.to_dict(orient="records"),
        "by_layout": by_layout.to_dict(orient="records"),
        "boundary": (
            "Level 2 CST-derived compound stress evidence only. It does not replace real measurement calibration, "
            "full-wave airframe validation, or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_compound_stress_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    regenerate_command = (
        "python code\\run_cst_recognition_compound_stress.py "
        f"--layout-candidates {','.join(candidate_names)} "
        f"--compound-cases {','.join(str(case['stress_case']) for case in compound_cases)} "
        f"--strategies {','.join(strategies)} "
        f"--seeds {','.join(str(seed) for seed in seeds)} "
        f"--out-dir {rel(out_dir)}"
    )
    write_readme(out_dir, summary, by_strategy, by_case, inputs, regenerate_command)
    print(f"compound stress recognition check complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
