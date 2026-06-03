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
    parse_held_out_families,
    stress_family,
    test_cases_for,
    training_cases_for,
)
from run_cst_recognition_seed_stability import aggregate_results, parse_seeds
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


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_dropout_mitigation"
DEFAULT_SEEDS = [202614, 202615, 202616]
DEFAULT_LAYOUT_CANDIDATES = ["geometric_farthest_32", "task_driven_48"]
DEFAULT_HELD_OUT_FAMILIES = ["dropout"]

STRATEGIES: dict[str, dict[str, bool]] = {
    "zero_fill": {"impute": False, "mask": False},
    "mask_features": {"impute": False, "mask": True},
    "freq_sensor_median_impute": {"impute": True, "mask": False},
    "freq_sensor_median_impute_mask": {"impute": True, "mask": True},
}


def parse_focused_layout_candidates(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_LAYOUT_CANDIDATES
    return parse_layout_candidates(raw)


def parse_strategies(raw: str | None) -> list[str]:
    if not raw:
        return list(STRATEGIES)
    strategies = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(strategies) - set(STRATEGIES))
    if unknown:
        raise ValueError(f"unknown dropout mitigation strategies: {unknown}; valid choices are {sorted(STRATEGIES)}")
    if not strategies:
        raise ValueError("--strategies was provided but no strategy names were parsed")
    return strategies


def normalized_channel_table(nearfield: pd.DataFrame) -> pd.DataFrame:
    work = ensure_theta_phi(nearfield).copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["polarization"] = work["polarization"].astype(str).str.strip().str.lower()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    work["e_real"] = pd.to_numeric(work["e_real"], errors="coerce").astype(float)
    work["e_imag"] = pd.to_numeric(work["e_imag"], errors="coerce").astype(float)
    return work[work["polarization"].isin(["theta", "phi"])].copy()


def missing_channel_mask(work: pd.DataFrame, zero_tolerance: float) -> pd.Series:
    magnitude = np.hypot(work["e_real"].to_numpy(dtype=float), work["e_imag"].to_numpy(dtype=float))
    return pd.Series(magnitude <= zero_tolerance, index=work.index)


def frequency_sensor_median_impute(nearfield: pd.DataFrame, zero_tolerance: float) -> pd.DataFrame:
    work = normalized_channel_table(nearfield)
    missing = missing_channel_mask(work, zero_tolerance)

    for _, group in work.groupby(["sample_id", "sensor_id", "polarization"], sort=False):
        idx = group.index
        group_missing = missing.loc[idx].to_numpy(dtype=bool)
        if not group_missing.any() or group_missing.all():
            continue
        missing_idx = idx[group_missing]
        valid_idx = idx[~group_missing]
        work.loc[missing_idx, "e_real"] = float(work.loc[valid_idx, "e_real"].median())
        work.loc[missing_idx, "e_imag"] = float(work.loc[valid_idx, "e_imag"].median())

    missing = missing_channel_mask(work, zero_tolerance)
    for _, group in work.groupby(["sample_id", "frequency_hz", "polarization"], sort=False):
        idx = group.index
        group_missing = missing.loc[idx].to_numpy(dtype=bool)
        if not group_missing.any() or group_missing.all():
            continue
        missing_idx = idx[group_missing]
        valid_idx = idx[~group_missing]
        work.loc[missing_idx, "e_real"] = float(work.loc[valid_idx, "e_real"].median())
        work.loc[missing_idx, "e_imag"] = float(work.loc[valid_idx, "e_imag"].median())

    return work


def dropout_mask_features(
    nearfield: pd.DataFrame,
    sample_ids: list[str],
    zero_tolerance: float,
) -> tuple[np.ndarray, dict[str, object]]:
    work = normalized_channel_table(nearfield)
    work["is_missing_channel"] = missing_channel_mask(work, zero_tolerance)

    sensors = np.array(sorted(work["sensor_id"].unique()), dtype=int)
    frequencies = np.array(sorted(work["frequency_hz"].unique()), dtype=float)
    dedup = work.drop_duplicates(["sample_id", "frequency_hz", "sensor_id", "polarization"], keep="first")
    pivot = dedup.pivot(
        index=["sample_id", "frequency_hz", "sensor_id"],
        columns="polarization",
        values="is_missing_channel",
    )
    if not {"theta", "phi"}.issubset(set(pivot.columns)):
        raise ValueError("theta/phi near-field fields are required for dropout-mask features")

    rows: list[np.ndarray] = []
    for sample_id in sample_ids:
        per_frequency: list[list[float]] = []
        for frequency_hz in frequencies:
            try:
                sub = pivot.loc[(sample_id, frequency_hz)].reindex(sensors)
            except KeyError:
                sub = pd.DataFrame(index=sensors, columns=["theta", "phi"], data=True)
            theta_missing = sub["theta"].fillna(True).to_numpy(dtype=bool)
            phi_missing = sub["phi"].fillna(True).to_numpy(dtype=bool)
            either_missing = theta_missing | phi_missing
            both_missing = theta_missing & phi_missing
            per_frequency.append(
                [
                    float(theta_missing.mean()),
                    float(phi_missing.mean()),
                    float(either_missing.mean()),
                    float(both_missing.mean()),
                ]
            )
        freq_features = np.asarray(per_frequency, dtype=float)
        channel_missing = freq_features[:, :2].mean(axis=1)
        aggregate = np.array(
            [
                float(channel_missing.mean()),
                float(channel_missing.max()),
                float(channel_missing.std()),
                float(freq_features[:, 2].max()),
                float(freq_features[:, 3].mean()),
                float((channel_missing > 0.0).mean()),
            ],
            dtype=float,
        )
        rows.append(np.concatenate([freq_features.ravel(), aggregate]))

    feature_matrix = np.vstack(rows)
    metadata = {
        "mask_feature_count": int(feature_matrix.shape[1]),
        "mask_features_per_frequency": "theta_missing_fraction, phi_missing_fraction, any_polarization_missing_fraction, both_polarizations_missing_fraction",
        "mask_aggregate_features": [
            "mean_channel_missing_fraction",
            "max_channel_missing_fraction",
            "std_channel_missing_fraction",
            "max_sensor_missing_fraction",
            "mean_both_polarizations_missing_fraction",
            "frequency_fraction_with_any_missing_channel",
        ],
        "zero_tolerance": float(zero_tolerance),
    }
    return feature_matrix, metadata


def build_strategy_feature_matrix(
    nearfield: pd.DataFrame,
    labels: pd.DataFrame,
    strategy: str,
    zero_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, list[str], list[str], dict[str, object]]:
    config = STRATEGIES[strategy]
    transformed = frequency_sensor_median_impute(nearfield, zero_tolerance) if config["impute"] else nearfield
    x, y, class_names, sample_ids, metadata = build_feature_matrix(transformed, labels)
    metadata = dict(metadata)
    metadata["strategy"] = strategy
    metadata["imputation"] = "frequency_sensor_then_local_polarization_median" if config["impute"] else "none"
    metadata["dropout_mask_features"] = bool(config["mask"])
    metadata["base_feature_count"] = int(x.shape[1])
    metadata["mask_feature_count"] = 0

    if config["mask"]:
        mask_x, mask_metadata = dropout_mask_features(nearfield, sample_ids, zero_tolerance)
        x = np.hstack([x, mask_x])
        metadata.update(mask_metadata)
        metadata["feature_count"] = int(x.shape[1])
    return x, y, class_names, sample_ids, metadata


def build_strategy_family_out_train_matrix(
    clean_case: pd.DataFrame,
    labels: pd.DataFrame,
    train_idx: np.ndarray,
    y: np.ndarray,
    sample_ids: list[str],
    held_out_family: str,
    strategy: str,
    seed: int,
    zero_tolerance: float,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, object]]]:
    x_parts: list[np.ndarray] = []
    y_parts: list[np.ndarray] = []
    manifest: list[dict[str, object]] = []
    for aug_index, augmentation in enumerate(training_cases_for(held_out_family)):
        aug_seed = seed + 20000 + aug_index * 137
        augmented = perturb_nearfield(clean_case, augmentation, aug_seed)
        aug_x, aug_y, _, aug_sample_ids, aug_metadata = build_strategy_feature_matrix(
            augmented,
            labels,
            strategy,
            zero_tolerance,
        )
        if sample_ids != aug_sample_ids or not np.array_equal(y, aug_y):
            raise ValueError(
                f"sample order changed for {held_out_family}/{strategy} training case {augmentation['stress_case']}"
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
                "mask_feature_count": int(aug_metadata["mask_feature_count"]),
            }
        )
    return np.vstack(x_parts), np.concatenate(y_parts), manifest


def add_zero_fill_deltas(results: pd.DataFrame) -> pd.DataFrame:
    work = results.copy()
    key_cols = ["seed", "candidate", "held_out_family", "stress_case"]
    baseline = work[work["strategy"] == "zero_fill"].set_index(key_cols)["best_accuracy"]

    def delta_for(row: pd.Series) -> float:
        key = tuple(row[col] for col in key_cols)
        if key not in baseline.index:
            return np.nan
        return float(row["best_accuracy"]) - float(baseline.loc[key])

    work["accuracy_delta_vs_zero_fill"] = work.apply(delta_for, axis=1)
    return work


def aggregate_with_delta(results: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    aggregate = aggregate_results(results, group_cols)
    delta_rows: list[dict[str, object]] = []
    for key, group in results.groupby(group_cols, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        row = {col: value for col, value in zip(group_cols, key)}
        deltas = pd.to_numeric(group["accuracy_delta_vs_zero_fill"], errors="coerce").dropna()
        row.update(
            {
                "mean_delta_vs_zero_fill": float(deltas.mean()) if not deltas.empty else np.nan,
                "min_delta_vs_zero_fill": float(deltas.min()) if not deltas.empty else np.nan,
                "max_delta_vs_zero_fill": float(deltas.max()) if not deltas.empty else np.nan,
            }
        )
        delta_rows.append(row)
    deltas = pd.DataFrame(delta_rows)
    return aggregate.merge(deltas, on=group_cols, how="left")


def summarize(results: pd.DataFrame, by_case: pd.DataFrame, by_strategy: pd.DataFrame) -> dict[str, object]:
    worst = results.sort_values("best_accuracy", ascending=True).iloc[0]
    best_strategy = by_strategy.sort_values(["mean_accuracy", "min_accuracy"], ascending=False).iloc[0]
    tightest_case = by_case.sort_values("min_accuracy", ascending=True).iloc[0]

    best_case_rows: list[dict[str, object]] = []
    for (candidate, stress_case), group in by_case.groupby(["candidate", "stress_case"], sort=False):
        best = group.sort_values(["mean_accuracy", "min_accuracy"], ascending=False).iloc[0]
        zero = group[group["strategy"] == "zero_fill"]
        zero_mean = np.nan if zero.empty else float(zero.iloc[0]["mean_accuracy"])
        best_case_rows.append(
            {
                "candidate": str(candidate),
                "stress_case": str(stress_case),
                "best_strategy": str(best["strategy"]),
                "best_mean_accuracy": float(best["mean_accuracy"]),
                "best_min_accuracy": float(best["min_accuracy"]),
                "zero_fill_mean_accuracy": zero_mean,
                "best_mean_delta_vs_zero_fill": float(best["mean_accuracy"]) - zero_mean,
            }
        )

    return {
        "seed_count": int(results["seed"].nunique()),
        "seeds": [int(value) for value in sorted(results["seed"].unique())],
        "layout_count": int(results["candidate"].nunique()),
        "layouts": [str(value) for value in sorted(results["candidate"].unique())],
        "strategy_count": int(results["strategy"].nunique()),
        "strategies": [str(value) for value in results["strategy"].drop_duplicates().tolist()],
        "held_out_families": [str(value) for value in sorted(results["held_out_family"].unique())],
        "stress_cases": [str(value) for value in sorted(results["stress_case"].unique())],
        "row_count": int(results.shape[0]),
        "all_rows_pass_085": bool((pd.to_numeric(results["best_accuracy"]) >= 0.85).all()),
        "worst_row": {
            "seed": int(worst["seed"]),
            "candidate": str(worst["candidate"]),
            "strategy": str(worst["strategy"]),
            "stress_case": str(worst["stress_case"]),
            "best_accuracy": float(worst["best_accuracy"]),
            "best_macro_f1": float(worst["best_macro_f1"]),
        },
        "best_overall_strategy": {
            "strategy": str(best_strategy["strategy"]),
            "mean_accuracy": float(best_strategy["mean_accuracy"]),
            "min_accuracy": float(best_strategy["min_accuracy"]),
            "mean_delta_vs_zero_fill": float(best_strategy["mean_delta_vs_zero_fill"]),
        },
        "tightest_case_summary": {
            "candidate": str(tightest_case["candidate"]),
            "strategy": str(tightest_case["strategy"]),
            "stress_case": str(tightest_case["stress_case"]),
            "mean_accuracy": float(tightest_case["mean_accuracy"]),
            "min_accuracy": float(tightest_case["min_accuracy"]),
            "mean_delta_vs_zero_fill": float(tightest_case["mean_delta_vs_zero_fill"]),
        },
        "best_strategy_by_candidate_case": best_case_rows,
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    by_strategy: pd.DataFrame,
    by_case: pd.DataFrame,
    inputs: dict[str, str],
    zero_tolerance: float,
    regenerate_command: str,
) -> None:
    lines = [
        "# Level 2 Dropout Mitigation Check",
        "",
        "This directory stores the focused G5 follow-up for missing-channel",
        "recognition robustness. It keeps the leave-one-stress-family-out",
        "protocol, focuses on held-out dropout or dropout-bearing cases, and",
        "compares zero-fill against lightweight mask-feature and imputation",
        "strategies.",
        "",
        "## Current Result",
        "",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}.",
        f"- Layouts tested: {', '.join(summary['layouts'])}.",
        f"- Held-out families tested: {', '.join(summary['held_out_families'])}.",
        f"- Strategies tested: {', '.join(summary['strategies'])}.",
        f"- Stress cases tested: {', '.join(summary['stress_cases'])}.",
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
            "| `recognition_dropout_mitigation_metrics.csv` | Per-seed/per-layout/per-strategy stress accuracy and macro-F1. |",
            "| `recognition_dropout_mitigation_by_strategy.csv` | Aggregate comparison of zero-fill, mask features, and imputation. |",
            "| `recognition_dropout_mitigation_by_case.csv` | Aggregate comparison by layout, stress case, and strategy. |",
            "| `recognition_dropout_mitigation_by_layout.csv` | Aggregate comparison by layout and strategy. |",
            "| `recognition_dropout_mitigation_summary.json` | Machine-readable summary, inputs, strategy definitions, and aggregate tables. |",
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
            "This is a focused Level 2 CST-derived element-library check. It compares",
            "test-time missing-channel handling strategies under internal stochastic",
            "dropout or dropout-bearing compound perturbations. It does not replace",
            "real measurement calibration, full-wave airframe validation, or the true",
            "CST near-field monitor gate.",
            "",
            f"Zero-valued channels are treated as missing with tolerance `{zero_tolerance:g}`.",
            "",
            "## Inputs",
            "",
        ]
    )
    for name, path in inputs.items():
        lines.append(f"- {name}: `{path}`")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def result_row(
    seed: int,
    candidate: str,
    strategy: str,
    held_out_family: str,
    stress: dict[str, Any],
    decision_rows: dict[str, dict[str, str]],
    sensor_count: int,
    frequency_count: int,
    feature_metadata: dict[str, object],
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
        "training_profile": "leave_one_stress_family_dropout_mitigation",
        "strategy": strategy,
        "imputation": str(feature_metadata["imputation"]),
        "dropout_mask_features": bool(feature_metadata["dropout_mask_features"]),
        "held_out_family": held_out_family,
        "stress_family": STRESS_CASE_FAMILIES[str(stress["stress_case"])],
        "stress_case": str(stress["stress_case"]),
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare lightweight missing-channel mitigation strategies for Level 2 recognition dropout.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument(
        "--layout-candidates",
        default=",".join(DEFAULT_LAYOUT_CANDIDATES),
        help="Comma-separated candidate list. Defaults to the two tightest dropout layouts.",
    )
    parser.add_argument(
        "--held-out-families",
        default=",".join(DEFAULT_HELD_OUT_FAMILIES),
        help="Comma-separated subset of noise,phase,dropout,combined. Default focuses on dropout.",
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

    candidate_names = parse_focused_layout_candidates(args.layout_candidates)
    held_out_families = parse_held_out_families(args.held_out_families)
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

            for family_index, held_out_family in enumerate(held_out_families):
                base_seed = seed + layout_index * 1000 + family_index * 179
                for strategy in strategies:
                    train_x, train_y, train_manifest = build_strategy_family_out_train_matrix(
                        clean_case=clean_case,
                        labels=labels,
                        train_idx=train_idx,
                        y=y,
                        sample_ids=sample_ids,
                        held_out_family=held_out_family,
                        strategy=strategy,
                        seed=base_seed,
                        zero_tolerance=args.zero_tolerance,
                    )
                    manifests.setdefault(f"{held_out_family}/{strategy}", train_manifest)
                    trained_models = train_augmented_models(train_x, train_y, seed)

                    for stress_index, stress in enumerate(test_cases_for(held_out_family)):
                        stress_seed = base_seed + stress_index * 41
                        perturbed = perturb_nearfield(clean_case, stress, stress_seed)
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
                                held_out_family=held_out_family,
                                stress=stress,
                                decision_rows=decision_rows,
                                sensor_count=len(sensor_ids),
                                frequency_count=len(frequencies),
                                feature_metadata=test_metadata,
                                sample_count=int(test_metadata["sample_count"]),
                                base_train_count=len(train_idx),
                                augmented_train_count=train_x.shape[0],
                                test_count=len(test_idx),
                                augmentation_profile_count=len(train_manifest),
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

    results.to_csv(out_dir / "recognition_dropout_mitigation_metrics.csv", index=False, encoding="utf-8-sig")
    by_strategy.to_csv(out_dir / "recognition_dropout_mitigation_by_strategy.csv", index=False, encoding="utf-8-sig")
    by_case.to_csv(out_dir / "recognition_dropout_mitigation_by_case.csv", index=False, encoding="utf-8-sig")
    by_layout.to_csv(out_dir / "recognition_dropout_mitigation_by_layout.csv", index=False, encoding="utf-8-sig")

    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_dropout_mitigation.py",
        "purpose": "G5 focused missing-channel/dropout mitigation comparison for Level 2 recognition robustness.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "seeds": seeds,
        "held_out_families": held_out_families,
        "stress_case_families": STRESS_CASE_FAMILIES,
        "strategies": STRATEGIES,
        "zero_tolerance": float(args.zero_tolerance),
        "training_manifests": manifests,
        "summary": summary,
        "by_strategy": by_strategy.to_dict(orient="records"),
        "by_case": by_case.to_dict(orient="records"),
        "by_layout": by_layout.to_dict(orient="records"),
        "boundary": (
            "Focused Level 2 CST-derived dropout mitigation comparison only. "
            "It does not replace real measurement calibration, full-wave airframe validation, "
            "or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_dropout_mitigation_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    regenerate_command = (
        "python code\\run_cst_recognition_dropout_mitigation.py "
        f"--layout-candidates {','.join(candidate_names)} "
        f"--held-out-families {','.join(held_out_families)} "
        f"--strategies {','.join(strategies)} "
        f"--seeds {','.join(str(seed) for seed in seeds)} "
        f"--out-dir {rel(out_dir)}"
    )
    write_readme(out_dir, summary, by_strategy, by_case, inputs, args.zero_tolerance, regenerate_command)
    print(f"dropout mitigation recognition check complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
