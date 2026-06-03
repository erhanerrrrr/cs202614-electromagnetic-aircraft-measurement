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
    missing_channel_mask,
    normalized_channel_table,
    parse_strategies,
    summarize,
)
from run_cst_recognition_seed_stability import parse_seeds
from run_cst_recognition_stress_test import (
    DEFAULT_DECISION_MATRIX,
    DEFAULT_LABELS,
    DEFAULT_LAYOUTS,
    DEFAULT_NEARFIELD,
    DEFAULT_LAYOUT_CANDIDATES,
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


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_structured_dropout"
DEFAULT_SEEDS = [202614, 202615, 202616]
DEFAULT_STRUCTURED_CASES = [
    "sensor_node_dropout_10pct",
    "sensor_node_dropout_25pct",
    "polarization_pair_dropout_10pct",
    "azimuth_sector_dropout_60deg",
]

STRUCTURED_DROPOUT_CASES: list[dict[str, Any]] = [
    {
        "stress_case": "sensor_node_dropout_10pct",
        "dropout_mode": "sensor_node",
        "dropout_fraction": 0.10,
        "sector_width_deg": 0.0,
        "description": "Per-sample correlated sensor-node dropout: selected sensors lose all frequencies and both polarizations.",
    },
    {
        "stress_case": "sensor_node_dropout_25pct",
        "dropout_mode": "sensor_node",
        "dropout_fraction": 0.25,
        "sector_width_deg": 0.0,
        "description": "Severe per-sample sensor-node dropout at 25 percent of selected layout sensors.",
    },
    {
        "stress_case": "polarization_pair_dropout_10pct",
        "dropout_mode": "polarization_pair",
        "dropout_fraction": 0.10,
        "sector_width_deg": 0.0,
        "description": "Per-sample sensor-frequency dropout where theta and phi channels fail together.",
    },
    {
        "stress_case": "azimuth_sector_dropout_60deg",
        "dropout_mode": "azimuth_sector",
        "dropout_fraction": 0.0,
        "sector_width_deg": 60.0,
        "description": "Per-sample contiguous azimuth-sector dropout over a 60 degree sector.",
    },
]


def parse_structured_cases(raw: str | None) -> list[dict[str, Any]]:
    lookup = {case["stress_case"]: case for case in STRUCTURED_DROPOUT_CASES}
    names = DEFAULT_STRUCTURED_CASES if not raw else [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(names) - set(lookup))
    if unknown:
        raise ValueError(f"unknown structured dropout cases: {unknown}; valid choices are {sorted(lookup)}")
    if not names:
        raise ValueError("--structured-cases was provided but no case names were parsed")
    return [lookup[name] for name in names]


def angular_distance_deg(values: np.ndarray, center_deg: float) -> np.ndarray:
    return np.abs((values - center_deg + 180.0) % 360.0 - 180.0)


def observed_missing_fraction(nearfield: pd.DataFrame, zero_tolerance: float) -> float:
    work = normalized_channel_table(nearfield)
    if work.empty:
        return 0.0
    return float(missing_channel_mask(work, zero_tolerance).mean())


def apply_known_noise_phase(case_nearfield: pd.DataFrame, stress: dict[str, Any], seed: int) -> pd.DataFrame:
    base_stress = dict(stress)
    base_stress["dropout_fraction"] = 0.0
    return perturb_nearfield(case_nearfield, base_stress, seed)


def apply_structured_dropout(
    case_nearfield: pd.DataFrame,
    stress: dict[str, Any],
    seed: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    work = apply_known_noise_phase(case_nearfield, stress, seed).copy()
    rng = np.random.default_rng(seed)
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    work["phi_deg"] = pd.to_numeric(work["phi_deg"], errors="coerce").astype(float) % 360.0

    mode = str(stress["dropout_mode"])
    zero_mask = pd.Series(False, index=work.index)
    selected_entity_counts: list[int] = []
    selected_sensor_counts: list[int] = []
    selected_sector_centers: list[float] = []

    for sample_id, group in work.groupby("sample_id", sort=False):
        idx = group.index
        sensors = np.array(sorted(group["sensor_id"].unique()), dtype=int)
        if sensors.size == 0:
            continue

        if mode == "sensor_node":
            count = max(1, int(np.ceil(float(stress["dropout_fraction"]) * sensors.size)))
            count = min(count, sensors.size)
            chosen = set(int(value) for value in rng.choice(sensors, size=count, replace=False))
            zero_mask.loc[idx] = group["sensor_id"].isin(chosen).to_numpy(dtype=bool)
            selected_entity_counts.append(count)
            selected_sensor_counts.append(count)

        elif mode == "polarization_pair":
            pairs = group[["sensor_id", "frequency_hz"]].drop_duplicates().sort_values(["sensor_id", "frequency_hz"])
            pair_keys = list(zip(pairs["sensor_id"].astype(int), pairs["frequency_hz"].astype(float)))
            count = max(1, int(np.ceil(float(stress["dropout_fraction"]) * len(pair_keys))))
            count = min(count, len(pair_keys))
            chosen_indices = rng.choice(np.arange(len(pair_keys)), size=count, replace=False)
            chosen = {pair_keys[int(index)] for index in chosen_indices}
            group_keys = list(zip(group["sensor_id"].astype(int), group["frequency_hz"].astype(float)))
            zero_mask.loc[idx] = [key in chosen for key in group_keys]
            selected_entity_counts.append(count)
            selected_sensor_counts.append(len({sensor_id for sensor_id, _ in chosen}))

        elif mode == "azimuth_sector":
            sensor_phi = group[["sensor_id", "phi_deg"]].drop_duplicates().sort_values(["sensor_id"])
            unique_phi = np.array(sorted(sensor_phi["phi_deg"].unique()), dtype=float)
            center = float(rng.choice(unique_phi))
            width = float(stress["sector_width_deg"])
            distances = angular_distance_deg(sensor_phi["phi_deg"].to_numpy(dtype=float), center)
            selected_sensors = sensor_phi.loc[distances <= width / 2.0, "sensor_id"].astype(int).tolist()
            if not selected_sensors:
                nearest = int(sensor_phi.iloc[int(np.argmin(distances))]["sensor_id"])
                selected_sensors = [nearest]
            zero_mask.loc[idx] = group["sensor_id"].isin(selected_sensors).to_numpy(dtype=bool)
            selected_entity_counts.append(len(selected_sensors))
            selected_sensor_counts.append(len(selected_sensors))
            selected_sector_centers.append(center)

        else:
            raise ValueError(f"unknown structured dropout mode: {mode!r}")

    work.loc[zero_mask, "e_real"] = 0.0
    work.loc[zero_mask, "e_imag"] = 0.0
    info = {
        "dropout_mode": mode,
        "target_dropout_fraction": float(stress.get("dropout_fraction") or 0.0),
        "sector_width_deg": float(stress.get("sector_width_deg") or 0.0),
        "zeroed_row_fraction": float(zero_mask.mean()) if len(zero_mask) else 0.0,
        "mean_selected_entity_count": float(np.mean(selected_entity_counts)) if selected_entity_counts else 0.0,
        "mean_selected_sensor_count": float(np.mean(selected_sensor_counts)) if selected_sensor_counts else 0.0,
        "mean_sector_center_deg": float(np.mean(selected_sector_centers)) if selected_sector_centers else "",
    }
    return work, info


def build_known_augmentation_train_matrix(
    clean_case: pd.DataFrame,
    labels: pd.DataFrame,
    train_idx: np.ndarray,
    y: np.ndarray,
    sample_ids: list[str],
    strategy: str,
    seed: int,
    zero_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    manifest: list[dict[str, object]] = []
    for aug_index, augmentation in enumerate(STRESS_CASES):
        aug_seed = seed + 20000 + aug_index * 137
        augmented = perturb_nearfield(clean_case, augmentation, aug_seed)
        aug_x, aug_y, _, aug_sample_ids, aug_metadata = build_strategy_feature_matrix(
            augmented,
            labels,
            strategy,
            zero_tolerance,
        )
        if sample_ids != aug_sample_ids or not np.array_equal(y, aug_y):
            raise ValueError(f"sample order changed for {strategy} training case {augmentation['stress_case']}")
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
                "mask_feature_count": int(aug_metadata["mask_feature_count"]),
            }
        )
    return np.vstack(x_parts), np.concatenate(y_parts), manifest


def result_row(
    seed: int,
    candidate: str,
    strategy: str,
    stress: dict[str, Any],
    dropout_info: dict[str, object],
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
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    accuracy = float(best["accuracy"])
    return {
        "seed": int(seed),
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": "known_perturbation_augmented_structured_dropout_test",
        "strategy": strategy,
        "imputation": str(feature_metadata["imputation"]),
        "dropout_mask_features": bool(feature_metadata["dropout_mask_features"]),
        "held_out_family": "structured_dropout",
        "stress_family": "structured_dropout",
        "stress_case": str(stress["stress_case"]),
        "dropout_mode": str(dropout_info["dropout_mode"]),
        "target_dropout_fraction": float(dropout_info["target_dropout_fraction"]),
        "sector_width_deg": float(dropout_info["sector_width_deg"]),
        "zeroed_row_fraction": float(dropout_info["zeroed_row_fraction"]),
        "observed_missing_channel_fraction": float(observed_missing),
        "mean_selected_entity_count": float(dropout_info["mean_selected_entity_count"]),
        "mean_selected_sensor_count": float(dropout_info["mean_selected_sensor_count"]),
        "mean_sector_center_deg": dropout_info["mean_sector_center_deg"],
        "sensor_count": int(sensor_count),
        "frequency_count": int(frequency_count),
        "noise_snr_db": "" if stress.get("noise_snr_db") is None else float(stress["noise_snr_db"]),
        "phase_jitter_deg": float(stress.get("phase_jitter_deg") or 0.0),
        "dropout_fraction": float(stress.get("dropout_fraction") or 0.0),
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
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    by_strategy: pd.DataFrame,
    by_case: pd.DataFrame,
    inputs: dict[str, str],
    regenerate_command: str,
) -> None:
    lines = [
        "# Level 2 Structured Dropout Check",
        "",
        "This directory stores the G5 follow-up for structured missing-channel",
        "recognition robustness. Models are trained with the existing clean,",
        "noise, phase-jitter, random dropout, and combined augmentation profiles,",
        "then tested on unseen structured dropout patterns.",
        "",
        "## Current Result",
        "",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}.",
        f"- Layouts tested: {', '.join(summary['layouts'])}.",
        f"- Strategies tested: {', '.join(summary['strategies'])}.",
        f"- Structured cases tested: {', '.join(summary['stress_cases'])}.",
        f"- Total rows: {summary['row_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst single row: "
            f"seed `{summary['worst_row']['seed']}`, "
            f"`{summary['worst_row']['candidate']}` / "
            f"`{summary['worst_row']['strategy']}` / "
            f"`{summary['worst_row']['stress_case']}` with accuracy "
            f"`{summary['worst_row']['best_accuracy']:.3f}`."
        ),
        (
            "- Best average strategy: "
            f"`{summary['best_overall_strategy']['strategy']}` with mean accuracy "
            f"`{summary['best_overall_strategy']['mean_accuracy']:.3f}`, min accuracy "
            f"`{summary['best_overall_strategy']['min_accuracy']:.3f}`, and mean delta vs zero-fill "
            f"`{summary['best_overall_strategy']['mean_delta_vs_zero_fill']:+.3f}`."
        ),
        (
            "- Tightest aggregate row: "
            f"`{summary['tightest_case_summary']['candidate']}` / "
            f"`{summary['tightest_case_summary']['strategy']}` / "
            f"`{summary['tightest_case_summary']['stress_case']}`, mean "
            f"`{summary['tightest_case_summary']['mean_accuracy']:.3f}`, min "
            f"`{summary['tightest_case_summary']['min_accuracy']:.3f}`, mean delta vs zero-fill "
            f"`{summary['tightest_case_summary']['mean_delta_vs_zero_fill']:+.3f}`."
        ),
        "",
        "## Strategy Summary",
        "",
        "| Strategy | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs zero-fill | Passes 0.85 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in by_strategy.to_dict(orient="records"):
        lines.append(
            "| {strategy} | {seeds} | {rows} | {mean:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {delta:+.3f} | {passes} |".format(
                strategy=row["strategy"],
                seeds=int(row["seed_count"]),
                rows=int(row["row_count"]),
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
            "| `recognition_structured_dropout_metrics.csv` | Per-seed/per-layout/per-strategy structured dropout accuracy and macro-F1. |",
            "| `recognition_structured_dropout_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |",
            "| `recognition_structured_dropout_by_case.csv` | Aggregate comparison by layout, structured dropout case, and strategy. |",
            "| `recognition_structured_dropout_by_layout.csv` | Aggregate comparison by layout and strategy. |",
            "| `recognition_structured_dropout_summary.json` | Machine-readable summary, inputs, strategy definitions, structured cases, and aggregate tables. |",
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
            "This is a Level 2 CST-derived element-library structured dropout check.",
            "It tests internal simulated sensor-node, polarization-pair, and angular-sector",
            "missing-channel patterns. It does not replace real measurement calibration,",
            "full-wave airframe validation, or the true CST near-field monitor gate.",
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
        description="Test mitigation strategies on structured sensor/polarization/sector dropout.",
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
        "--structured-cases",
        default=",".join(DEFAULT_STRUCTURED_CASES),
        help="Comma-separated structured dropout case list.",
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
    structured_cases = parse_structured_cases(args.structured_cases)
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

                for stress_index, stress in enumerate(structured_cases):
                    stress_seed = base_seed + stress_index * 41
                    perturbed, dropout_info = apply_structured_dropout(clean_case, stress, stress_seed)
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
                            dropout_info=dropout_info,
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

    results.to_csv(out_dir / "recognition_structured_dropout_metrics.csv", index=False, encoding="utf-8-sig")
    by_strategy.to_csv(out_dir / "recognition_structured_dropout_by_strategy.csv", index=False, encoding="utf-8-sig")
    by_case.to_csv(out_dir / "recognition_structured_dropout_by_case.csv", index=False, encoding="utf-8-sig")
    by_layout.to_csv(out_dir / "recognition_structured_dropout_by_layout.csv", index=False, encoding="utf-8-sig")

    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_structured_dropout.py",
        "purpose": "G5 structured missing-channel robustness check for Level 2 recognition.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "seeds": seeds,
        "structured_dropout_cases": structured_cases,
        "strategies": STRATEGIES,
        "zero_tolerance": float(args.zero_tolerance),
        "training_cases": STRESS_CASES,
        "training_manifests": manifests,
        "summary": summary,
        "by_strategy": by_strategy.to_dict(orient="records"),
        "by_case": by_case.to_dict(orient="records"),
        "by_layout": by_layout.to_dict(orient="records"),
        "boundary": (
            "Level 2 CST-derived structured dropout evidence only. It does not replace real measurement calibration, "
            "full-wave airframe validation, or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_structured_dropout_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    regenerate_command = (
        "python code\\run_cst_recognition_structured_dropout.py "
        f"--layout-candidates {','.join(candidate_names)} "
        f"--structured-cases {','.join(str(case['stress_case']) for case in structured_cases)} "
        f"--strategies {','.join(strategies)} "
        f"--seeds {','.join(str(seed) for seed in seeds)} "
        f"--out-dir {rel(out_dir)}"
    )
    write_readme(out_dir, summary, by_strategy, by_case, inputs, regenerate_command)
    print(f"structured dropout recognition check complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
