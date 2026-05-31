from __future__ import annotations

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

from em_core import (
    add_complex_noise,
    build_measurement_matrix,
    class_templates,
    farfield_grid,
    farfield_pattern,
    farthest_point_subset,
    jitter_sources,
    make_equivalent_grid,
    make_hemisphere_layout,
    make_reference_sources,
    pattern_metrics,
    random_subset,
    sensor_response,
    solve_tikhonov,
    vector_to_source_set,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "baseline"
FREQ_HZ = 1.2e9
RNG = np.random.default_rng(202614)


def ensure_dirs() -> None:
    OUT.mkdir(parents=True, exist_ok=True)


def save_sensor_layout(layout) -> None:
    df = pd.DataFrame(
        {
            "sensor_id": np.arange(layout.positions.shape[0]),
            "x_m": layout.positions[:, 0],
            "y_m": layout.positions[:, 1],
            "z_m": layout.positions[:, 2],
            "theta_deg": np.rad2deg(layout.theta),
            "phi_deg": np.rad2deg(layout.phi),
            "radius_m": layout.radius_m,
            "polarization_1": "theta",
            "polarization_2": "phi",
        }
    )
    df.to_csv(OUT / "sensor_layout_hemisphere.csv", index=False, encoding="utf-8-sig")


def plot_sensor_layout(layout) -> None:
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(layout.positions[:, 0], layout.positions[:, 1], layout.positions[:, 2], s=16, c=layout.theta, cmap="viridis")
    box_x = [-6, 6, 6, -6, -6]
    box_y = [-5, -5, 5, 5, -5]
    for z in [0, 8]:
        ax.plot(box_x, box_y, [z] * len(box_x), color="tab:red", linewidth=1.2)
    for x in [-6, 6]:
        for y in [-5, 5]:
            ax.plot([x, x], [y, y], [0, 8], color="tab:red", linewidth=1.0)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_zlabel("z / m")
    ax.set_title("2pi hemisphere sensor layout, R=13 m")
    ax.view_init(elev=24, azim=38)
    fig.tight_layout()
    fig.savefig(OUT / "sensor_layout_hemisphere.png", dpi=220)
    plt.close(fig)


def reconstruct_one(layout, grid_positions, sources, sensor_indices, lam=1e-4, snr_db=35.0):
    values = sensor_response(layout, sources, FREQ_HZ, sensor_indices)
    noisy = add_complex_noise(values, snr_db, RNG)
    matrix = build_measurement_matrix(layout, grid_positions, FREQ_HZ, sensor_indices)
    solution = solve_tikhonov(matrix, noisy, lam=lam)
    return vector_to_source_set(grid_positions, solution)


def run_reconstruction_experiments(layout, grid_positions, sources):
    theta, phi, shape = farfield_grid()
    true_power, _, _ = farfield_pattern(sources, theta, phi, FREQ_HZ)

    experiments = []
    n_total = layout.positions.shape[0]
    for name, indices in [
        ("full_100", np.arange(n_total)),
        ("random_75", random_subset(n_total, int(round(0.75 * n_total)), RNG)),
        ("random_50", random_subset(n_total, int(round(0.50 * n_total)), RNG)),
        ("random_25", random_subset(n_total, int(round(0.25 * n_total)), RNG)),
        ("optimized_75", farthest_point_subset(layout, int(round(0.75 * n_total)))),
        ("optimized_50", farthest_point_subset(layout, int(round(0.50 * n_total)))),
    ]:
        reconstructed = reconstruct_one(layout, grid_positions, sources, np.asarray(indices, dtype=int))
        rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, FREQ_HZ)
        metrics = pattern_metrics(true_power, rec_power, theta, phi)
        metrics.update(
            {
                "experiment": name,
                "sensor_points": int(len(indices)),
                "measurement_channels": int(2 * len(indices)),
                "frequency_hz": FREQ_HZ,
            }
        )
        experiments.append(metrics)
        if name in {"full_100", "optimized_50"}:
            plot_farfield_comparison(true_power, rec_power, shape, name)

    df = pd.DataFrame(experiments)
    df = df[
        [
            "experiment",
            "sensor_points",
            "measurement_channels",
            "nmse",
            "correlation",
            "main_lobe_error_deg",
            "peak_error_db",
            "frequency_hz",
        ]
    ]
    df.to_csv(OUT / "reconstruction_metrics.csv", index=False, encoding="utf-8-sig")
    plot_sampling_tradeoff(df)
    return df


def plot_farfield_comparison(true_power, rec_power, shape, name):
    true_db = 10 * np.log10(true_power / np.max(true_power) + 1e-12)
    rec_db = 10 * np.log10(rec_power / np.max(rec_power) + 1e-12)
    diff = rec_db - true_db
    panels = [true_db.reshape(shape), rec_db.reshape(shape), diff.reshape(shape)]
    titles = ["CST-like truth", "Equivalent-source reconstruction", "Difference / dB"]
    cmaps = ["magma", "magma", "coolwarm"]
    vmins = [-35, -35, -6]
    vmaxs = [0, 0, 6]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, data, title, cmap, vmin, vmax in zip(axes, panels, titles, cmaps, vmins, vmaxs):
        im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax, extent=[0, 360, 2, 88])
        ax.set_title(title)
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        fig.colorbar(im, ax=ax, shrink=0.82)
    fig.suptitle(f"Far-field pattern comparison: {name}", y=1.04)
    fig.savefig(OUT / f"farfield_comparison_{name}.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_sampling_tradeoff(df: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(7.5, 5))
    ordered = df.sort_values("sensor_points")
    ax1.plot(ordered["sensor_points"], ordered["nmse"], "o-", label="NMSE", color="tab:blue")
    ax1.set_xlabel("sensor points")
    ax1.set_ylabel("NMSE", color="tab:blue")
    ax1.tick_params(axis="y", labelcolor="tab:blue")
    ax2 = ax1.twinx()
    ax2.plot(ordered["sensor_points"], ordered["correlation"], "s--", label="Correlation", color="tab:orange")
    ax2.set_ylabel("pattern correlation", color="tab:orange")
    ax2.tick_params(axis="y", labelcolor="tab:orange")
    for _, row in ordered.iterrows():
        ax1.annotate(row["experiment"], (row["sensor_points"], row["nmse"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
    ax1.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT / "sampling_tradeoff.png", dpi=220)
    plt.close(fig)


def build_feature_dataset(layout, grid_positions):
    templates = class_templates(grid_positions)
    frequencies = np.array([0.9e9, 1.05e9, 1.2e9, 1.35e9, 1.5e9])
    selected = farthest_point_subset(layout, 72)
    x_rows = []
    y_rows = []
    labels = [template.label for template in templates]
    for class_idx, template in enumerate(templates):
        for _ in range(70):
            sample = jitter_sources(template, RNG)
            feature_blocks = []
            for freq in frequencies:
                response = sensor_response(layout, sample, freq, selected)
                response = add_complex_noise(response, 25.0, RNG)
                magnitude = np.abs(response)
                phase = np.unwrap(np.angle(response))
                feature_blocks.append(np.log10(magnitude + 1e-12))
                feature_blocks.append(np.cos(phase))
                feature_blocks.append(np.sin(phase))
            x_rows.append(np.concatenate(feature_blocks))
            y_rows.append(class_idx)
    return np.vstack(x_rows), np.array(y_rows), labels


def run_recognition_experiment(layout, grid_positions):
    x, y, labels = build_feature_dataset(layout, grid_positions)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.30, random_state=202614, stratify=y)

    models = {
        "svm_rbf": make_pipeline(StandardScaler(), SVC(C=6.0, gamma="scale", kernel="rbf")),
        "random_forest": RandomForestClassifier(n_estimators=260, random_state=202614, max_depth=None, class_weight="balanced"),
    }
    results = {}
    best_name = None
    best_acc = -1.0
    best_pred = None
    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        acc = accuracy_score(y_test, pred)
        results[name] = {
            "accuracy": float(acc),
            "report": classification_report(y_test, pred, target_names=labels, output_dict=True, zero_division=0),
        }
        if acc > best_acc:
            best_name = name
            best_acc = acc
            best_pred = pred

    cm = confusion_matrix(y_test, best_pred, labels=np.arange(len(labels)))
    pd.DataFrame(cm, index=labels, columns=labels).to_csv(OUT / "recognition_confusion_matrix.csv", encoding="utf-8-sig")
    with (OUT / "recognition_metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"best_model": best_name, "labels": labels, "models": results}, f, ensure_ascii=False, indent=2)
    plot_confusion_matrix(cm, labels, best_name, best_acc)
    return best_name, best_acc, cm


def plot_confusion_matrix(cm, labels, model_name, accuracy):
    fig, ax = plt.subplots(figsize=(6.4, 5.6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(np.arange(len(labels)), labels=labels, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(labels)), labels=labels)
    ax.set_xlabel("predicted")
    ax.set_ylabel("true")
    ax.set_title(f"Recognition confusion matrix: {model_name}, acc={accuracy:.3f}")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="white" if cm[i, j] > cm.max() * 0.55 else "black")
    fig.colorbar(im, ax=ax, shrink=0.82)
    fig.tight_layout()
    fig.savefig(OUT / "recognition_confusion_matrix.png", dpi=220)
    plt.close(fig)


def write_score_evidence(recon_df: pd.DataFrame, model_name: str, accuracy: float) -> None:
    best_sparse = recon_df[recon_df["experiment"] == "optimized_50"].iloc[0]
    full = recon_df[recon_df["experiment"] == "full_100"].iloc[0]
    content = f"""# Baseline score evidence

This is a synthetic physics baseline for algorithm validation before CST data is exported.

## Sensor layout

- Geometry: 2pi upper hemisphere.
- Radius: 13 m.
- Object envelope: 12 m x 10 m x 8 m.
- Spatial points: 162.
- Polarizations per point: theta and phi.
- Equivalent measurement channels at one frequency: 324.

## Reconstruction

| Case | Sensors | NMSE | Correlation | Main-lobe error / deg |
|---|---:|---:|---:|---:|
| Full 100% | {int(full.sensor_points)} | {full.nmse:.4e} | {full.correlation:.4f} | {full.main_lobe_error_deg:.2f} |
| Optimized 50% | {int(best_sparse.sensor_points)} | {best_sparse.nmse:.4e} | {best_sparse.correlation:.4f} | {best_sparse.main_lobe_error_deg:.2f} |

## Recognition

- Best baseline model: {model_name}
- Accuracy on synthetic multi-source states: {accuracy:.3f}
- Contest threshold: >= 0.850

## How to use this evidence

The numbers above cannot replace CST validation. They prove the intended data path and metrics are executable:

1. Generate or import near-field samples.
2. Reconstruct equivalent sources.
3. Extrapolate far-field pattern.
4. Compare with truth/reference far-field.
5. Reduce sensor count and rank layouts.
6. Extract spatial-frequency-polarization fingerprints for recognition.
"""
    (OUT / "score_evidence.md").write_text(content, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    layout = make_hemisphere_layout(n_theta=9, n_phi=18, radius_m=13.0)
    grid_positions = make_equivalent_grid(nx=4, ny=3, nz=3)
    sources = make_reference_sources(grid_positions)

    save_sensor_layout(layout)
    plot_sensor_layout(layout)
    recon_df = run_reconstruction_experiments(layout, grid_positions, sources)
    model_name, accuracy, _ = run_recognition_experiment(layout, grid_positions)
    write_score_evidence(recon_df, model_name, accuracy)
    print(f"Baseline complete: {OUT}")
    print(recon_df.to_string(index=False))
    print(f"Recognition best model: {model_name}, accuracy={accuracy:.3f}")


if __name__ == "__main__":
    main()
