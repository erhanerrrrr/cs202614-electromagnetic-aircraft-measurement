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
    build_augmented_train_matrix,
    evaluate_models,
    train_augmented_models,
)
from run_cst_recognition_seed_stability import parse_seeds
from run_cst_recognition_stress_test import (
    DEFAULT_DECISION_MATRIX,
    DEFAULT_LABELS,
    DEFAULT_LAYOUTS,
    DEFAULT_LAYOUT_CANDIDATES,
    DEFAULT_NEARFIELD,
    ROOT,
    filter_case,
    frequencies_from_nearfield,
    load_decision_rows,
    load_layouts,
    make_models,
    parse_layout_candidates,
    rel,
    split_indices,
)


DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_instrument_error"
DEFAULT_SEEDS = [202614, 202615, 202616]
DEFAULT_INSTRUMENT_CASES = [
    "global_gain_drift_3db",
    "sensor_gain_bias_3db",
    "frequency_slope_3db",
    "polarization_imbalance_2db",
    "mixed_amp_phase_bias",
]

INSTRUMENT_ERROR_CASES: list[dict[str, Any]] = [
    {
        "stress_case": "global_gain_drift_3db",
        "global_gain_sigma_db": 3.0,
        "sensor_gain_sigma_db": 0.0,
        "frequency_slope_pp_db": 0.0,
        "polarization_imbalance_sigma_db": 0.0,
        "sensor_phase_sigma_deg": 0.0,
        "frequency_phase_slope_pp_deg": 0.0,
        "description": "Per-sample global amplitude calibration drift with 3 dB standard deviation.",
    },
    {
        "stress_case": "sensor_gain_bias_3db",
        "global_gain_sigma_db": 0.0,
        "sensor_gain_sigma_db": 3.0,
        "frequency_slope_pp_db": 0.0,
        "polarization_imbalance_sigma_db": 0.0,
        "sensor_phase_sigma_deg": 0.0,
        "frequency_phase_slope_pp_deg": 0.0,
        "description": "Correlated per-sensor amplitude bias, shared by frequency and polarization channels.",
    },
    {
        "stress_case": "frequency_slope_3db",
        "global_gain_sigma_db": 0.0,
        "sensor_gain_sigma_db": 0.0,
        "frequency_slope_pp_db": 3.0,
        "polarization_imbalance_sigma_db": 0.0,
        "sensor_phase_sigma_deg": 0.0,
        "frequency_phase_slope_pp_deg": 0.0,
        "description": "Per-sample linear frequency-response slope with 3 dB peak-to-peak span.",
    },
    {
        "stress_case": "polarization_imbalance_2db",
        "global_gain_sigma_db": 0.0,
        "sensor_gain_sigma_db": 0.0,
        "frequency_slope_pp_db": 0.0,
        "polarization_imbalance_sigma_db": 2.0,
        "sensor_phase_sigma_deg": 0.0,
        "frequency_phase_slope_pp_deg": 0.0,
        "description": "Theta/phi relative amplitude calibration imbalance with 2 dB standard deviation.",
    },
    {
        "stress_case": "mixed_amp_phase_bias",
        "global_gain_sigma_db": 1.5,
        "sensor_gain_sigma_db": 2.0,
        "frequency_slope_pp_db": 3.0,
        "polarization_imbalance_sigma_db": 1.5,
        "sensor_phase_sigma_deg": 10.0,
        "frequency_phase_slope_pp_deg": 20.0,
        "description": "Mixed amplitude and correlated phase calibration bias across sensor, frequency, and polarization groups.",
    },
]


def parse_instrument_cases(raw: str | None) -> list[dict[str, Any]]:
    lookup = {case["stress_case"]: case for case in INSTRUMENT_ERROR_CASES}
    names = DEFAULT_INSTRUMENT_CASES if not raw else [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(names) - set(lookup))
    if unknown:
        raise ValueError(f"unknown instrument cases: {unknown}; valid choices are {sorted(lookup)}")
    if not names:
        raise ValueError("--instrument-cases was provided but no case names were parsed")
    return [lookup[name] for name in names]


def normalized_frequency_position(frequencies: pd.Series) -> pd.Series:
    values = pd.to_numeric(frequencies, errors="coerce").astype(float)
    min_freq = float(values.min())
    max_freq = float(values.max())
    if np.isclose(max_freq, min_freq):
        return pd.Series(np.zeros(len(values)), index=values.index)
    return 2.0 * (values - min_freq) / (max_freq - min_freq) - 1.0


def apply_instrument_error(
    case_nearfield: pd.DataFrame,
    stress: dict[str, Any],
    seed: int,
) -> tuple[pd.DataFrame, dict[str, object]]:
    work = ensure_theta_phi(case_nearfield).copy().reset_index(drop=True)
    rng = np.random.default_rng(seed)
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    work["polarization"] = work["polarization"].astype(str).str.strip().str.lower()
    field = pd.to_numeric(work["e_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
        work["e_imag"],
        errors="coerce",
    ).to_numpy(dtype=float)

    gain_db = np.zeros(work.shape[0], dtype=float)
    phase_deg = np.zeros(work.shape[0], dtype=float)

    global_sigma = float(stress.get("global_gain_sigma_db") or 0.0)
    sensor_sigma = float(stress.get("sensor_gain_sigma_db") or 0.0)
    slope_pp_db = float(stress.get("frequency_slope_pp_db") or 0.0)
    pol_sigma = float(stress.get("polarization_imbalance_sigma_db") or 0.0)
    sensor_phase_sigma = float(stress.get("sensor_phase_sigma_deg") or 0.0)
    freq_phase_pp = float(stress.get("frequency_phase_slope_pp_deg") or 0.0)

    for sample_id, group in work.groupby("sample_id", sort=False):
        idx = group.index.to_numpy()
        local_gain = np.zeros(idx.shape[0], dtype=float)
        local_phase = np.zeros(idx.shape[0], dtype=float)

        if global_sigma > 0.0:
            local_gain += rng.normal(0.0, global_sigma)

        if sensor_sigma > 0.0 or sensor_phase_sigma > 0.0:
            sensors = np.array(sorted(group["sensor_id"].unique()), dtype=int)
            sensor_gain = {
                int(sensor): rng.normal(0.0, sensor_sigma) if sensor_sigma > 0.0 else 0.0 for sensor in sensors
            }
            sensor_phase = {
                int(sensor): rng.normal(0.0, sensor_phase_sigma) if sensor_phase_sigma > 0.0 else 0.0
                for sensor in sensors
            }
            sensor_values = group["sensor_id"].astype(int).to_numpy()
            local_gain += np.array([sensor_gain[int(sensor)] for sensor in sensor_values], dtype=float)
            local_phase += np.array([sensor_phase[int(sensor)] for sensor in sensor_values], dtype=float)

        if slope_pp_db > 0.0:
            slope = rng.uniform(-slope_pp_db, slope_pp_db)
            freq_pos = normalized_frequency_position(group["frequency_hz"]).to_numpy(dtype=float)
            local_gain += 0.5 * slope * freq_pos

        if freq_phase_pp > 0.0:
            phase_slope = rng.uniform(-freq_phase_pp, freq_phase_pp)
            freq_pos = normalized_frequency_position(group["frequency_hz"]).to_numpy(dtype=float)
            local_phase += 0.5 * phase_slope * freq_pos

        if pol_sigma > 0.0:
            imbalance = rng.normal(0.0, pol_sigma)
            pol = group["polarization"].astype(str).str.lower().to_numpy()
            local_gain += np.where(pol == "theta", 0.5 * imbalance, -0.5 * imbalance)

        gain_db[idx] = local_gain
        phase_deg[idx] = local_phase

    gain = 10.0 ** (gain_db / 20.0)
    phase = np.exp(1j * np.deg2rad(phase_deg))
    perturbed = field * gain * phase
    work["e_real"] = np.real(perturbed)
    work["e_imag"] = np.imag(perturbed)

    info = {
        "global_gain_sigma_db": global_sigma,
        "sensor_gain_sigma_db": sensor_sigma,
        "frequency_slope_pp_db": slope_pp_db,
        "polarization_imbalance_sigma_db": pol_sigma,
        "sensor_phase_sigma_deg": sensor_phase_sigma,
        "frequency_phase_slope_pp_deg": freq_phase_pp,
        "mean_abs_gain_db": float(np.mean(np.abs(gain_db))) if gain_db.size else 0.0,
        "p95_abs_gain_db": float(np.percentile(np.abs(gain_db), 95)) if gain_db.size else 0.0,
        "max_abs_gain_db": float(np.max(np.abs(gain_db))) if gain_db.size else 0.0,
        "mean_abs_phase_deg": float(np.mean(np.abs(phase_deg))) if phase_deg.size else 0.0,
        "p95_abs_phase_deg": float(np.percentile(np.abs(phase_deg), 95)) if phase_deg.size else 0.0,
        "max_abs_phase_deg": float(np.max(np.abs(phase_deg))) if phase_deg.size else 0.0,
    }
    return work, info


def train_clean_models(clean_x: np.ndarray, y: np.ndarray, train_idx: np.ndarray, seed: int) -> dict[str, object]:
    trained: dict[str, object] = {}
    for model_name, model in make_models(seed).items():
        model.fit(clean_x[train_idx], y[train_idx])
        trained[model_name] = model
    return trained


def row_for_result(
    seed: int,
    candidate: str,
    training_profile: str,
    stress: dict[str, Any],
    error_info: dict[str, object],
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
    accuracy = float(best["accuracy"])
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    row = {
        "seed": int(seed),
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "training_profile": training_profile,
        "stress_family": "instrument_error",
        "stress_case": str(stress["stress_case"]),
        "sensor_count": int(sensor_count),
        "frequency_count": int(frequency_count),
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
    row.update(error_info)
    return row


def add_profile_deltas(results: pd.DataFrame) -> pd.DataFrame:
    work = results.copy()
    key_cols = ["seed", "candidate", "stress_case"]
    baseline = (
        work[work["training_profile"] == "clean_train"][key_cols + ["best_accuracy"]]
        .rename(columns={"best_accuracy": "clean_train_profile_accuracy"})
        .copy()
    )
    work = work.merge(baseline, on=key_cols, how="left")
    work["accuracy_delta_vs_clean_train_profile"] = (
        pd.to_numeric(work["best_accuracy"], errors="coerce")
        - pd.to_numeric(work["clean_train_profile_accuracy"], errors="coerce")
    )
    work.loc[work["training_profile"] == "clean_train", "accuracy_delta_vs_clean_train_profile"] = 0.0
    return work


def aggregate(results: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for key_values, group in results.groupby(keys, dropna=False, sort=False):
        if not isinstance(key_values, tuple):
            key_values = (key_values,)
        accuracy = pd.to_numeric(group["best_accuracy"], errors="coerce")
        delta = pd.to_numeric(group["accuracy_delta_vs_clean_train_profile"], errors="coerce")
        std = float(accuracy.std(ddof=1)) if len(accuracy) > 1 else 0.0
        ci = 1.96 * std / np.sqrt(max(len(accuracy), 1))
        worst = group.loc[accuracy.idxmin()]
        row = {key: value for key, value in zip(keys, key_values)}
        row.update(
            {
                "seed_count": int(group["seed"].nunique()),
                "row_count": int(group.shape[0]),
                "mean_accuracy": float(accuracy.mean()),
                "std_accuracy": std,
                "ci95_low_accuracy": float(max(0.0, accuracy.mean() - ci)),
                "ci95_high_accuracy": float(min(1.0, accuracy.mean() + ci)),
                "min_accuracy": float(accuracy.min()),
                "max_accuracy": float(accuracy.max()),
                "mean_delta_vs_clean_train_profile": float(delta.mean()),
                "min_delta_vs_clean_train_profile": float(delta.min()),
                "max_delta_vs_clean_train_profile": float(delta.max()),
                "worst_seed": int(worst["seed"]),
                "worst_case": str(worst["stress_case"]),
                "all_rows_pass_085": bool((accuracy >= 0.85).all()),
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def summarize(
    results: pd.DataFrame,
    by_profile: pd.DataFrame,
    by_case: pd.DataFrame,
    by_layout: pd.DataFrame,
) -> dict[str, object]:
    worst = results.sort_values(["best_accuracy", "candidate", "stress_case"], ascending=True).iloc[0]
    best_profile = by_profile.sort_values(["mean_accuracy", "min_accuracy"], ascending=False).iloc[0]
    tightest_case = by_case.sort_values(["min_accuracy", "mean_accuracy"], ascending=True).iloc[0]
    tightest_layout = by_layout.sort_values(["min_accuracy", "mean_accuracy"], ascending=True).iloc[0]
    return {
        "seed_count": int(results["seed"].nunique()),
        "seeds": [int(value) for value in sorted(results["seed"].unique())],
        "layout_count": int(results["candidate"].nunique()),
        "layouts": [str(value) for value in sorted(results["candidate"].unique())],
        "training_profiles": [str(value) for value in results["training_profile"].drop_duplicates().tolist()],
        "stress_cases": [str(value) for value in sorted(results["stress_case"].unique())],
        "row_count": int(results.shape[0]),
        "all_rows_pass_085": bool((pd.to_numeric(results["best_accuracy"]) >= 0.85).all()),
        "worst_row": {
            "seed": int(worst["seed"]),
            "candidate": str(worst["candidate"]),
            "training_profile": str(worst["training_profile"]),
            "stress_case": str(worst["stress_case"]),
            "best_accuracy": float(worst["best_accuracy"]),
            "best_macro_f1": float(worst["best_macro_f1"]),
        },
        "best_training_profile": {
            "training_profile": str(best_profile["training_profile"]),
            "mean_accuracy": float(best_profile["mean_accuracy"]),
            "min_accuracy": float(best_profile["min_accuracy"]),
            "mean_delta_vs_clean_train_profile": float(best_profile["mean_delta_vs_clean_train_profile"]),
        },
        "tightest_case_summary": {
            "candidate": str(tightest_case["candidate"]),
            "training_profile": str(tightest_case["training_profile"]),
            "stress_case": str(tightest_case["stress_case"]),
            "mean_accuracy": float(tightest_case["mean_accuracy"]),
            "min_accuracy": float(tightest_case["min_accuracy"]),
            "mean_delta_vs_clean_train_profile": float(tightest_case["mean_delta_vs_clean_train_profile"]),
        },
        "tightest_layout_summary": {
            "candidate": str(tightest_layout["candidate"]),
            "training_profile": str(tightest_layout["training_profile"]),
            "mean_accuracy": float(tightest_layout["mean_accuracy"]),
            "min_accuracy": float(tightest_layout["min_accuracy"]),
            "mean_delta_vs_clean_train_profile": float(tightest_layout["mean_delta_vs_clean_train_profile"]),
        },
    }


def write_readme(
    out_dir: Path,
    summary: dict[str, object],
    by_profile: pd.DataFrame,
    by_case: pd.DataFrame,
    inputs: dict[str, str],
    regenerate_command: str,
) -> None:
    lines = [
        "# Level 2 Instrument Error Check",
        "",
        "This directory stores the G5 recognition follow-up for instrument-like",
        "calibration errors. It is separate from missing-channel/dropout tests:",
        "fields are not zeroed; instead, correlated amplitude and phase biases are",
        "applied by sample, sensor, frequency, and polarization groups.",
        "",
        "## Current Result",
        "",
        f"- Seeds: {', '.join(str(seed) for seed in summary['seeds'])}.",
        f"- Layouts tested: {', '.join(summary['layouts'])}.",
        f"- Training profiles: {', '.join(summary['training_profiles'])}.",
        f"- Instrument cases tested: {', '.join(summary['stress_cases'])}.",
        f"- Total rows: {summary['row_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst single row: "
            f"seed `{summary['worst_row']['seed']}`, "
            f"`{summary['worst_row']['candidate']}` / "
            f"`{summary['worst_row']['training_profile']}` / "
            f"`{summary['worst_row']['stress_case']}` with accuracy "
            f"`{summary['worst_row']['best_accuracy']:.3f}`."
        ),
        (
            "- Best average training profile: "
            f"`{summary['best_training_profile']['training_profile']}` with mean accuracy "
            f"`{summary['best_training_profile']['mean_accuracy']:.3f}`, min accuracy "
            f"`{summary['best_training_profile']['min_accuracy']:.3f}`, and mean delta vs clean-train profile "
            f"`{summary['best_training_profile']['mean_delta_vs_clean_train_profile']:+.3f}`."
        ),
        (
            "- Tightest aggregate row: "
            f"`{summary['tightest_case_summary']['candidate']}` / "
            f"`{summary['tightest_case_summary']['training_profile']}` / "
            f"`{summary['tightest_case_summary']['stress_case']}`, mean "
            f"`{summary['tightest_case_summary']['mean_accuracy']:.3f}`, min "
            f"`{summary['tightest_case_summary']['min_accuracy']:.3f}`, mean delta vs clean-train profile "
            f"`{summary['tightest_case_summary']['mean_delta_vs_clean_train_profile']:+.3f}`."
        ),
        "",
        "## Training Profile Summary",
        "",
        "| Training profile | Seeds | Rows | Mean accuracy | Min accuracy | 95% CI low | 95% CI high | Mean delta vs clean-train profile | Passes 0.85 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in by_profile.to_dict(orient="records"):
        lines.append(
            "| {profile} | {seeds} | {rows} | {mean:.3f} | {minv:.3f} | {low:.3f} | {high:.3f} | {delta:+.3f} | {passes} |".format(
                profile=row["training_profile"],
                seeds=int(row["seed_count"]),
                rows=int(row["row_count"]),
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                low=float(row["ci95_low_accuracy"]),
                high=float(row["ci95_high_accuracy"]),
                delta=float(row["mean_delta_vs_clean_train_profile"]),
                passes=str(row["all_rows_pass_085"]).lower(),
            )
        )

    lines.extend(
        [
            "",
            "## Tightest Case Rows",
            "",
            "| Candidate | Training profile | Stress case | Mean accuracy | Min accuracy | Mean delta vs clean-train profile | Passes 0.85 |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for row in by_case.sort_values(["min_accuracy", "mean_accuracy"], ascending=True).head(12).to_dict(
        orient="records"
    ):
        lines.append(
            "| {candidate} | {profile} | {case} | {mean:.3f} | {minv:.3f} | {delta:+.3f} | {passes} |".format(
                candidate=row["candidate"],
                profile=row["training_profile"],
                case=row["stress_case"],
                mean=float(row["mean_accuracy"]),
                minv=float(row["min_accuracy"]),
                delta=float(row["mean_delta_vs_clean_train_profile"]),
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
            "| `recognition_instrument_error_metrics.csv` | Per-seed/per-layout/per-profile/per-case accuracy and macro-F1. |",
            "| `recognition_instrument_error_by_profile.csv` | Aggregate comparison of clean-train and known-perturbation-augmented training profiles. |",
            "| `recognition_instrument_error_by_case.csv` | Aggregate comparison by layout, profile, and instrument error case. |",
            "| `recognition_instrument_error_by_layout.csv` | Aggregate comparison by layout and profile. |",
            "| `recognition_instrument_error_summary.json` | Machine-readable summary, inputs, cases, and aggregate tables. |",
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
            "This is a Level 2 CST-derived element-library instrument-error check.",
            "It tests simulated correlated gain/phase calibration biases. It does not",
            "replace real instrument calibration, full-wave airframe validation, or",
            "the true CST near-field monitor gate.",
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
        description="Run Level 2 recognition stress tests for correlated instrument calibration errors."
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="Level 2 labels CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Sampling-layout candidate CSV.")
    parser.add_argument(
        "--decision-matrix",
        default=str(DEFAULT_DECISION_MATRIX),
        help="Optional sampling decision matrix CSV.",
    )
    parser.add_argument(
        "--layout-candidates",
        default=",".join(DEFAULT_LAYOUT_CANDIDATES),
        help="Comma-separated layout candidates to test.",
    )
    parser.add_argument(
        "--instrument-cases",
        default=",".join(DEFAULT_INSTRUMENT_CASES),
        help="Comma-separated instrument error cases to test.",
    )
    parser.add_argument("--seeds", default=",".join(str(seed) for seed in DEFAULT_SEEDS), help="Comma-separated seeds.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified test split size.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    instrument_cases = parse_instrument_cases(args.instrument_cases)
    seeds = parse_seeds(args.seeds)

    nearfield = read_table(nearfield_path)
    labels = read_table(labels_path)
    nf_report = validate_nearfield(nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    layouts = load_layouts(layouts_path, candidate_names)
    decision_rows = load_decision_rows(decision_path)
    frequencies = frequencies_from_nearfield(nearfield)

    rows: list[dict[str, object]] = []
    train_manifests: dict[str, list[dict[str, object]]] = {}
    for seed in seeds:
        for candidate, sensor_ids in layouts.items():
            clean_case = filter_case(nearfield, sensor_ids, frequencies)
            clean_x, y, class_names, sample_ids, feature_metadata = build_feature_matrix(clean_case, labels)
            train_idx, test_idx = split_indices(y, args.test_size, seed)

            clean_models = train_clean_models(clean_x, y, train_idx, seed)
            train_x, train_y, manifest = build_augmented_train_matrix(
                clean_case=clean_case,
                labels=labels,
                train_idx=train_idx,
                y=y,
                sample_ids=sample_ids,
                seed=seed,
            )
            augmented_models = train_augmented_models(train_x, train_y, seed)
            train_manifests[f"{seed}/{candidate}"] = manifest

            profile_models = {
                "clean_train": (clean_models, int(len(train_idx)), int(len(train_idx)), 1),
                "known_perturbation_augmented": (
                    augmented_models,
                    int(len(train_idx)),
                    int(train_x.shape[0]),
                    int(len(manifest)),
                ),
            }

            for stress_index, stress in enumerate(instrument_cases):
                stress_seed = seed + 50000 + stress_index * 317
                perturbed, error_info = apply_instrument_error(clean_case, stress, stress_seed)
                test_x, test_y, _, test_sample_ids, test_metadata = build_feature_matrix(perturbed, labels)
                if sample_ids != test_sample_ids or not np.array_equal(y, test_y):
                    raise ValueError(f"sample order changed for instrument case {stress['stress_case']}")

                for training_profile, (models, base_train_count, augmented_train_count, profile_count) in profile_models.items():
                    best, model_rows = evaluate_models(
                        models=models,
                        test_x=test_x[test_idx],
                        test_y=y[test_idx],
                        class_names=class_names,
                    )
                    rows.append(
                        row_for_result(
                            seed=seed,
                            candidate=candidate,
                            training_profile=training_profile,
                            stress=stress,
                            error_info=error_info,
                            decision_rows=decision_rows,
                            sensor_count=len(sensor_ids),
                            frequency_count=len(frequencies),
                            feature_count=int(test_metadata["feature_count"]),
                            sample_count=int(test_metadata["sample_count"]),
                            base_train_count=base_train_count,
                            augmented_train_count=augmented_train_count,
                            test_count=len(test_idx),
                            augmentation_profile_count=profile_count,
                            best=best,
                            models=model_rows,
                        )
                    )
                    print(
                        f"seed={seed}/{candidate}/{training_profile}/{stress['stress_case']}: "
                        f"accuracy={float(best['accuracy']):.3f}"
                    )

    results = add_profile_deltas(pd.DataFrame(rows))
    by_profile = aggregate(results, ["training_profile"])
    by_case = aggregate(results, ["candidate", "training_profile", "stress_case"])
    by_layout = aggregate(results, ["candidate", "training_profile"])
    summary = summarize(results, by_profile, by_case, by_layout)

    results.to_csv(out_dir / "recognition_instrument_error_metrics.csv", index=False, encoding="utf-8-sig")
    by_profile.to_csv(out_dir / "recognition_instrument_error_by_profile.csv", index=False, encoding="utf-8-sig")
    by_case.to_csv(out_dir / "recognition_instrument_error_by_case.csv", index=False, encoding="utf-8-sig")
    by_layout.to_csv(out_dir / "recognition_instrument_error_by_layout.csv", index=False, encoding="utf-8-sig")

    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_instrument_error.py",
        "purpose": "G5 correlated instrument calibration error robustness check for Level 2 recognition.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "seeds": seeds,
        "instrument_error_cases": instrument_cases,
        "training_manifests": train_manifests,
        "summary": summary,
        "by_profile": by_profile.to_dict(orient="records"),
        "by_case": by_case.to_dict(orient="records"),
        "by_layout": by_layout.to_dict(orient="records"),
        "boundary": (
            "Level 2 CST-derived simulated instrument-error evidence only. It does not replace real measurement "
            "calibration, full-wave airframe validation, or true-monitor reconstruction gates."
        ),
    }
    (out_dir / "recognition_instrument_error_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    regenerate_command = (
        "python code\\run_cst_recognition_instrument_error.py "
        f"--layout-candidates {','.join(candidate_names)} "
        f"--instrument-cases {','.join(str(case['stress_case']) for case in instrument_cases)} "
        f"--seeds {','.join(str(seed) for seed in seeds)} "
        f"--out-dir {rel(out_dir)}"
    )
    write_readme(out_dir, summary, by_profile, by_case, inputs, regenerate_command)
    print(f"instrument error recognition check complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
