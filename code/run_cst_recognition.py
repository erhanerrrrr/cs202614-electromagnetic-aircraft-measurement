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
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from cst_io import cartesian_to_theta_phi_rows, read_table, validate_nearfield


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "cst_recognition_demo"


def ensure_theta_phi(nearfield: pd.DataFrame) -> pd.DataFrame:
    pols = set(nearfield["polarization"].astype(str).str.strip().str.lower())
    if {"theta", "phi"}.issubset(pols):
        work = nearfield.copy()
        work["polarization"] = work["polarization"].astype(str).str.strip().str.lower()
        return work
    return cartesian_to_theta_phi_rows(nearfield)


def normalized_nearfield(nearfield: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    work = ensure_theta_phi(nearfield)
    work = work.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["polarization"] = work["polarization"].astype(str).str.strip().str.lower()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    work["e_complex"] = pd.to_numeric(work["e_real"], errors="coerce") + 1j * pd.to_numeric(work["e_imag"], errors="coerce")
    work = work[work["polarization"].isin(["theta", "phi"])].copy()

    sensors = np.array(sorted(work["sensor_id"].unique()), dtype=int)
    frequencies = np.array(sorted(work["frequency_hz"].unique()), dtype=float)
    coords = (
        work.drop_duplicates("sensor_id")
        .set_index("sensor_id")
        .reindex(sensors)[["x_m", "y_m", "z_m"]]
        .astype(float)
        .to_numpy()
    )
    if np.isnan(coords).any():
        raise ValueError("nearfield has missing sensor coordinates")
    return work, sensors, frequencies, coords


def spatial_summary(sensor_power: np.ndarray, sensor_positions: np.ndarray) -> np.ndarray:
    total = float(np.sum(sensor_power))
    if total <= 0:
        return np.zeros(11, dtype=float)
    weights = sensor_power / total
    radius = np.linalg.norm(sensor_positions, axis=1, keepdims=True)
    directions = sensor_positions / np.maximum(radius, 1e-15)
    centroid = weights @ directions
    spread = np.sqrt(np.sum(weights * np.sum((directions - centroid[None, :]) ** 2, axis=1)))
    entropy = -np.sum(weights * np.log(weights + 1e-15)) / np.log(len(weights))
    top_values = np.sort(weights)[-5:]
    return np.concatenate(
        [
            np.array([entropy, spread], dtype=float),
            centroid.astype(float),
            top_values.astype(float),
            np.array([float(np.max(weights))], dtype=float),
        ]
    )


def response_features(response: np.ndarray, sensor_positions: np.ndarray) -> tuple[np.ndarray, float]:
    n_sensors = sensor_positions.shape[0]
    theta_values = response[:n_sensors]
    phi_values = response[n_sensors:]
    mag = np.abs(response)
    log_mag = np.log10(mag + 1e-15)
    norm_log_mag = log_mag - np.mean(log_mag)

    anchor_idx = int(np.argmax(mag))
    anchor_phase = np.angle(response[anchor_idx]) if mag[anchor_idx] > 0 else 0.0
    relative_phase = np.angle(response * np.exp(-1j * anchor_phase))

    theta_power = float(np.sum(np.abs(theta_values) ** 2))
    phi_power = float(np.sum(np.abs(phi_values) ** 2))
    total_power = theta_power + phi_power
    sensor_power = np.abs(theta_values) ** 2 + np.abs(phi_values) ** 2
    summaries = np.array(
        [
            np.log10(total_power + 1e-30),
            np.log10(theta_power + 1e-30),
            np.log10(phi_power + 1e-30),
            np.log10((theta_power + 1e-30) / (phi_power + 1e-30)),
            float(np.mean(log_mag)),
            float(np.std(log_mag)),
            float(np.max(log_mag)),
            float(np.min(log_mag)),
        ],
        dtype=float,
    )
    features = np.concatenate(
        [
            norm_log_mag,
            np.cos(relative_phase),
            np.sin(relative_phase),
            summaries,
            spatial_summary(sensor_power, sensor_positions),
        ]
    )
    return features, float(np.log10(total_power + 1e-30))


def build_feature_matrix(
    nearfield: pd.DataFrame,
    labels: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray, list[str], list[str], dict[str, object]]:
    work, sensors, frequencies, sensor_positions = normalized_nearfield(nearfield)
    dedup = work.drop_duplicates(["sample_id", "frequency_hz", "sensor_id", "polarization"], keep="first")
    pivot = dedup.pivot(
        index=["sample_id", "frequency_hz", "sensor_id"],
        columns="polarization",
        values="e_complex",
    )
    if not {"theta", "phi"}.issubset(set(pivot.columns)):
        raise ValueError("theta/phi near-field fields are required for recognition")

    labels = labels.copy()
    labels["sample_id"] = labels["sample_id"].astype(str).str.strip()
    if "class_label" not in labels.columns:
        raise ValueError("labels file must include a class_label column")
    labels["class_label"] = labels["class_label"].astype(str).str.strip()
    labels = labels.drop_duplicates("sample_id", keep="first")

    x_rows: list[np.ndarray] = []
    y_labels: list[str] = []
    sample_ids: list[str] = []
    skipped: list[str] = []

    for row in labels.itertuples(index=False):
        sample_id = str(row.sample_id)
        feature_blocks: list[np.ndarray] = []
        spectral_log_power: list[float] = []
        complete = True
        for frequency_hz in frequencies:
            try:
                sub = pivot.loc[(sample_id, frequency_hz)].reindex(sensors)
            except KeyError:
                complete = False
                break
            if sub[["theta", "phi"]].isna().any().any():
                complete = False
                break
            response = np.concatenate(
                [
                    sub["theta"].to_numpy(dtype=np.complex128),
                    sub["phi"].to_numpy(dtype=np.complex128),
                ]
            )
            block, log_power = response_features(response, sensor_positions)
            feature_blocks.append(block)
            spectral_log_power.append(log_power)
        if not complete:
            skipped.append(sample_id)
            continue

        spectral = np.asarray(spectral_log_power, dtype=float)
        feature_blocks.append(spectral)
        if spectral.size > 1:
            feature_blocks.append(np.diff(spectral))
            feature_blocks.append(np.array([float(np.polyfit(frequencies / 1e9, spectral, deg=1)[0])], dtype=float))
        x_rows.append(np.concatenate(feature_blocks))
        y_labels.append(str(row.class_label))
        sample_ids.append(sample_id)

    if not x_rows:
        raise ValueError("no complete samples could be converted to recognition features")

    class_names = sorted(set(y_labels))
    class_to_idx = {name: idx for idx, name in enumerate(class_names)}
    y = np.array([class_to_idx[name] for name in y_labels], dtype=int)
    x = np.vstack(x_rows)
    metadata = {
        "sample_count": len(sample_ids),
        "skipped_samples": skipped[:20],
        "skipped_sample_count": len(skipped),
        "frequency_hz": [float(freq) for freq in frequencies],
        "sensor_count": int(len(sensors)),
        "feature_count": int(x.shape[1]),
        "feature_blocks_per_frequency": "normalized log magnitude, relative phase cosine/sine, power/polarization summary, spatial power summary",
    }
    return x, y, class_names, sample_ids, metadata


def plot_confusion_matrix(cm: np.ndarray, labels: list[str], model_name: str, accuracy: float, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.0, 5.8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(np.arange(len(labels)), labels=labels, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
    ax.set_title(f"CST-format recognition: {model_name}, acc={accuracy:.3f}")
    threshold = cm.max() * 0.55 if cm.size else 0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > threshold else "black")
    fig.colorbar(im, ax=ax, shrink=0.82)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def train_and_evaluate(
    x: np.ndarray,
    y: np.ndarray,
    class_names: list[str],
    sample_ids: list[str],
    out_dir: Path,
    test_size: float,
    seed: int,
) -> dict[str, object]:
    unique, counts = np.unique(y, return_counts=True)
    if len(unique) < 2:
        raise ValueError("recognition requires at least two classes")
    if int(np.min(counts)) < 2:
        raise ValueError("each class needs at least two complete samples for stratified train/test split")

    indices = np.arange(len(y))
    x_train, x_test, y_train, y_test, idx_train, idx_test = train_test_split(
        x,
        y,
        indices,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )
    models = {
        "svm_rbf": make_pipeline(StandardScaler(), SVC(C=8.0, gamma="scale", kernel="rbf", class_weight="balanced")),
        "random_forest": RandomForestClassifier(
            n_estimators=320,
            random_state=seed,
            max_depth=None,
            class_weight="balanced_subsample",
        ),
    }

    model_results: dict[str, object] = {}
    best_name = ""
    best_acc = -1.0
    best_pred: np.ndarray | None = None
    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        acc = accuracy_score(y_test, pred)
        model_results[name] = {
            "accuracy": float(acc),
            "classification_report": classification_report(
                y_test,
                pred,
                target_names=class_names,
                output_dict=True,
                zero_division=0,
            ),
        }
        if acc > best_acc:
            best_name = name
            best_acc = float(acc)
            best_pred = pred

    if best_pred is None:
        raise RuntimeError("no recognition model was evaluated")

    cm = confusion_matrix(y_test, best_pred, labels=np.arange(len(class_names)))
    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(
        out_dir / "cst_recognition_confusion_matrix.csv",
        encoding="utf-8-sig",
    )
    plot_confusion_matrix(cm, class_names, best_name, best_acc, out_dir / "cst_recognition_confusion_matrix.png")

    report = classification_report(y_test, best_pred, target_names=class_names, output_dict=True, zero_division=0)
    pd.DataFrame(report).transpose().to_csv(
        out_dir / "cst_recognition_classification_report.csv",
        encoding="utf-8-sig",
    )
    predictions = pd.DataFrame(
        {
            "sample_id": [sample_ids[idx] for idx in idx_test],
            "true_label": [class_names[item] for item in y_test],
            "predicted_label": [class_names[item] for item in best_pred],
            "correct": y_test == best_pred,
        }
    )
    predictions.to_csv(out_dir / "cst_recognition_predictions.csv", index=False, encoding="utf-8-sig")

    return {
        "best_model": best_name,
        "best_accuracy": best_acc,
        "class_names": class_names,
        "train_sample_count": int(len(y_train)),
        "test_sample_count": int(len(y_test)),
        "models": model_results,
    }


def evidence_note(nearfield_path: str) -> str:
    path_text = str(nearfield_path).replace("\\", "/").lower()
    if "synthetic" in path_text or "demo" in path_text:
        return "Accuracy from synthetic/demo CST-format data validates the interface only; replace input paths with CST exports for final evidence."
    if "data/cst_exports" in path_text:
        return (
            "Accuracy is computed from the current CST export table. Check the nearfield extraction_method column "
            "and stage notes to distinguish full-wave CST evidence from CST-derived element-library superposition."
        )
    return "Accuracy is computed from the provided nearfield table; verify the data provenance before using it as final evidence."


def main() -> None:
    parser = argparse.ArgumentParser(description="Train CST-format spatial-frequency-polarization recognition models.")
    parser.add_argument("--nearfield", required=True, help="Path to CST near-field CSV/XLSX.")
    parser.add_argument("--labels", required=True, help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified test split size.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    nearfield = read_table(args.nearfield)
    labels = read_table(args.labels)
    nf_report = validate_nearfield(nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    x, y, class_names, sample_ids, feature_metadata = build_feature_matrix(nearfield, labels)
    results = train_and_evaluate(
        x=x,
        y=y,
        class_names=class_names,
        sample_ids=sample_ids,
        out_dir=out_dir,
        test_size=args.test_size,
        seed=args.seed,
    )
    payload = {
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "feature_metadata": feature_metadata,
        "recognition": results,
        "note": evidence_note(args.nearfield),
    }
    (out_dir / "cst_recognition_metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"CST-format recognition complete: {out_dir}")
    print(f"feature matrix: {x.shape[0]} samples x {x.shape[1]} features")
    print(f"best model: {results['best_model']}, accuracy={results['best_accuracy']:.3f}")


if __name__ == "__main__":
    main()
