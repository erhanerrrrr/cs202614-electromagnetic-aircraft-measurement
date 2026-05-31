from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from cst_io import read_table, validate_nearfield
from run_cst_recognition import build_feature_matrix, ensure_theta_phi


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_recognition_ablation"


def sensor_table(nearfield: pd.DataFrame) -> pd.DataFrame:
    work = nearfield.copy()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    sensors = (
        work.drop_duplicates("sensor_id")
        .sort_values("sensor_id")
        [["sensor_id", "x_m", "y_m", "z_m"]]
        .copy()
    )
    sensors[["x_m", "y_m", "z_m"]] = sensors[["x_m", "y_m", "z_m"]].astype(float)
    return sensors.reset_index(drop=True)


def farthest_sensor_ids(sensors: pd.DataFrame, count: int) -> np.ndarray:
    positions = sensors[["x_m", "y_m", "z_m"]].to_numpy(dtype=float)
    directions = positions / np.maximum(np.linalg.norm(positions, axis=1, keepdims=True), 1e-15)
    selected = [0]
    min_distance = np.linalg.norm(directions - directions[0], axis=1)
    while len(selected) < count:
        idx = int(np.argmax(min_distance))
        selected.append(idx)
        new_distance = np.linalg.norm(directions - directions[idx], axis=1)
        min_distance = np.minimum(min_distance, new_distance)
    return sensors.iloc[selected]["sensor_id"].to_numpy(dtype=int)


def center_frequency_sets(frequencies: np.ndarray) -> dict[str, list[float]]:
    frequencies = np.array(sorted(frequencies), dtype=float)
    mid = len(frequencies) // 2
    if len(frequencies) >= 3:
        three = frequencies[max(0, mid - 1) : min(len(frequencies), mid + 2)]
    else:
        three = frequencies
    return {
        "5freq": frequencies.tolist(),
        "3freq": three.tolist(),
        "1freq": [float(frequencies[mid])],
    }


def make_cases(sensors: pd.DataFrame, frequencies: np.ndarray) -> list[dict[str, object]]:
    total = len(sensors)
    freq_sets = center_frequency_sets(frequencies)
    return [
        {"case": "full_5freq_100", "sensor_ids": sensors["sensor_id"].to_numpy(dtype=int), "frequencies": freq_sets["5freq"]},
        {"case": "farthest_5freq_75", "sensor_ids": farthest_sensor_ids(sensors, int(round(total * 0.75))), "frequencies": freq_sets["5freq"]},
        {"case": "farthest_5freq_50", "sensor_ids": farthest_sensor_ids(sensors, int(round(total * 0.50))), "frequencies": freq_sets["5freq"]},
        {"case": "farthest_5freq_25", "sensor_ids": farthest_sensor_ids(sensors, int(round(total * 0.25))), "frequencies": freq_sets["5freq"]},
        {"case": "full_3freq_100", "sensor_ids": sensors["sensor_id"].to_numpy(dtype=int), "frequencies": freq_sets["3freq"]},
        {"case": "full_1freq_100", "sensor_ids": sensors["sensor_id"].to_numpy(dtype=int), "frequencies": freq_sets["1freq"]},
        {"case": "farthest_3freq_50", "sensor_ids": farthest_sensor_ids(sensors, int(round(total * 0.50))), "frequencies": freq_sets["3freq"]},
        {"case": "farthest_1freq_50", "sensor_ids": farthest_sensor_ids(sensors, int(round(total * 0.50))), "frequencies": freq_sets["1freq"]},
    ]


def filter_nearfield(nearfield: pd.DataFrame, sensor_ids: np.ndarray, frequencies: list[float]) -> pd.DataFrame:
    work = nearfield.copy()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    return work[work["sensor_id"].isin(sensor_ids) & work["frequency_hz"].isin(frequencies)].copy()


def evaluate_feature_matrix(
    x: np.ndarray,
    y: np.ndarray,
    class_names: list[str],
    test_size: float,
    seed: int,
) -> dict[str, object]:
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )
    models = {
        "svm_rbf": make_pipeline(StandardScaler(), SVC(C=8.0, gamma="scale", kernel="rbf", class_weight="balanced")),
        "random_forest": RandomForestClassifier(
            n_estimators=260,
            random_state=seed,
            class_weight="balanced_subsample",
        ),
    }
    best: dict[str, object] = {"model": "", "accuracy": -1.0, "macro_f1": -1.0}
    model_rows: dict[str, object] = {}
    for model_name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        accuracy = float(accuracy_score(y_test, pred))
        macro_f1 = float(f1_score(y_test, pred, average="macro", zero_division=0))
        model_rows[model_name] = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "classification_report": classification_report(
                y_test,
                pred,
                target_names=class_names,
                output_dict=True,
                zero_division=0,
            ),
        }
        if accuracy > float(best["accuracy"]):
            best = {"model": model_name, "accuracy": accuracy, "macro_f1": macro_f1}
    return {"best": best, "models": model_rows}


def plot_ablation(results: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    labels = results["case"].tolist()
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, results["best_accuracy"], color="#3b82f6")
    ax.axhline(0.85, color="#dc2626", linestyle="--", linewidth=1.4, label="contest threshold 0.85")
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("accuracy")
    ax.set_xticks(x_pos, labels=labels, rotation=35, ha="right")
    ax.set_title("CST-format recognition ablation")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="lower right")
    for idx, value in enumerate(results["best_accuracy"]):
        ax.text(idx, min(1.02, value + 0.025), f"{value:.3f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def evidence_note(nearfield_path: str) -> str:
    path_text = str(nearfield_path).replace("\\", "/").lower()
    if "synthetic" in path_text or "demo" in path_text:
        return "Synthetic/demo CST-format ablation validates the recognition interface under sensor and frequency reduction."
    if "data/cst_exports" in path_text:
        return (
            "Ablation is computed from the current CST export table. Check the nearfield extraction_method column "
            "and stage notes to distinguish full-wave CST evidence from CST-derived element-library superposition."
        )
    return "Ablation is computed from the provided nearfield table; verify the data provenance before using it as final evidence."


def main() -> None:
    parser = argparse.ArgumentParser(description="Run sensor/frequency ablation for CST-format recognition data.")
    parser.add_argument("--nearfield", required=True, help="Path to CST near-field CSV/XLSX.")
    parser.add_argument("--labels", required=True, help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified test split size.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_nearfield = read_table(args.nearfield)
    labels = read_table(args.labels)
    nf_report = validate_nearfield(raw_nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    theta_phi_nearfield = ensure_theta_phi(raw_nearfield)
    sensors = sensor_table(theta_phi_nearfield)
    frequencies = np.array(sorted(pd.to_numeric(theta_phi_nearfield["frequency_hz"], errors="coerce").dropna().unique()), dtype=float)
    cases = make_cases(sensors, frequencies)

    rows: list[dict[str, object]] = []
    details: dict[str, object] = {}
    for case in cases:
        case_name = str(case["case"])
        sensor_ids = np.asarray(case["sensor_ids"], dtype=int)
        selected_frequencies = [float(freq) for freq in case["frequencies"]]
        case_nearfield = filter_nearfield(theta_phi_nearfield, sensor_ids, selected_frequencies)
        x, y, class_names, sample_ids, feature_metadata = build_feature_matrix(case_nearfield, labels)
        evaluation = evaluate_feature_matrix(x, y, class_names, args.test_size, args.seed)
        best = evaluation["best"]
        rows.append(
            {
                "case": case_name,
                "sensor_count": int(len(sensor_ids)),
                "sensor_fraction": float(len(sensor_ids) / len(sensors)),
                "frequency_count": int(len(selected_frequencies)),
                "frequency_hz": ";".join(str(int(round(freq))) for freq in selected_frequencies),
                "measurement_channels_per_sample": int(2 * len(sensor_ids) * len(selected_frequencies)),
                "feature_count": int(feature_metadata["feature_count"]),
                "sample_count": int(feature_metadata["sample_count"]),
                "best_model": str(best["model"]),
                "best_accuracy": float(best["accuracy"]),
                "best_macro_f1": float(best["macro_f1"]),
            }
        )
        details[case_name] = {
            "feature_metadata": feature_metadata,
            "class_names": class_names,
            "sample_ids_preview": sample_ids[:10],
            "evaluation": evaluation,
        }
        print(f"{case_name}: accuracy={float(best['accuracy']):.3f}, sensors={len(sensor_ids)}, freqs={len(selected_frequencies)}")

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "recognition_ablation_metrics.csv", index=False, encoding="utf-8-sig")
    plot_ablation(results, out_dir / "recognition_ablation_accuracy.png")

    payload = {
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "ablation_cases": rows,
        "details": details,
        "note": evidence_note(args.nearfield),
    }
    (out_dir / "recognition_ablation_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Ablation complete: {out_dir}")


if __name__ == "__main__":
    main()
