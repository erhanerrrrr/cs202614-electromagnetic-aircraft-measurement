from __future__ import annotations

import argparse
import csv
import json
import math
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

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
    sensor_response,
    solve_tikhonov,
    unit_vector,
    vector_to_source_set,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts"
DEFAULT_COUNTS = (120, 81, 48, 32)
FREQ_HZ = 1.2e9
CLASSIFICATION_FREQS_HZ = np.array([0.9e9, 1.05e9, 1.2e9, 1.35e9, 1.5e9])


@dataclass(frozen=True)
class CandidateLayout:
    name: str
    method: str
    indices: np.ndarray
    note: str


def stable_seed(text: str) -> int:
    return 202614 + int(zlib.crc32(text.encode("utf-8")) % 100_000)


def write_csv(path: Path, rows: list[dict[str, object]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def angular_distance_matrix(directions: np.ndarray) -> np.ndarray:
    dots = np.clip(directions @ directions.T, -1.0, 1.0)
    return np.rad2deg(np.arccos(dots))


def spatial_metrics(layout, indices: np.ndarray) -> dict[str, float]:
    directions = unit_vector(layout.positions[indices])
    if len(indices) <= 1:
        return {
            "min_angular_sep_deg": 0.0,
            "median_nn_angular_sep_deg": 0.0,
            "mean_theta_deg": float(np.rad2deg(np.mean(layout.theta[indices]))),
            "theta_span_deg": 0.0,
        }
    distances = angular_distance_matrix(directions)
    np.fill_diagonal(distances, np.inf)
    nearest = np.min(distances, axis=1)
    theta_deg = np.rad2deg(layout.theta[indices])
    return {
        "min_angular_sep_deg": float(np.min(nearest)),
        "median_nn_angular_sep_deg": float(np.median(nearest)),
        "mean_theta_deg": float(np.mean(theta_deg)),
        "theta_span_deg": float(np.max(theta_deg) - np.min(theta_deg)),
    }


def fibonacci_hemisphere_directions(
    count: int,
    theta_min_deg: float,
    theta_max_deg: float,
) -> np.ndarray:
    z_max = math.cos(math.radians(theta_min_deg))
    z_min = math.cos(math.radians(theta_max_deg))
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    k = np.arange(count, dtype=float)
    z = z_max - (k + 0.5) * (z_max - z_min) / count
    radius = np.sqrt(np.maximum(1.0 - z**2, 0.0))
    phi = (k * golden_angle) % (2.0 * math.pi)
    return np.column_stack([radius * np.cos(phi), radius * np.sin(phi), z])


def fill_by_farthest(layout, selected: list[int], count: int) -> np.ndarray:
    directions = unit_vector(layout.positions)
    chosen = list(dict.fromkeys(int(i) for i in selected))
    if not chosen:
        chosen = [0]
    while len(chosen) < count:
        selected_dirs = directions[np.asarray(chosen, dtype=int)]
        distances = np.linalg.norm(directions[:, None, :] - selected_dirs[None, :, :], axis=2)
        min_distance = np.min(distances, axis=1)
        min_distance[np.asarray(chosen, dtype=int)] = -1.0
        chosen.append(int(np.argmax(min_distance)))
    return np.asarray(chosen[:count], dtype=int)


def nearest_unique_snap(layout, target_directions: np.ndarray, count: int) -> np.ndarray:
    directions = unit_vector(layout.positions)
    selected: list[int] = []
    used: set[int] = set()
    for target in target_directions:
        order = np.argsort(-(directions @ target))
        for idx in order:
            idx = int(idx)
            if idx not in used:
                selected.append(idx)
                used.add(idx)
                break
    return fill_by_farthest(layout, selected, count)


def weighted_farthest_subset(layout, count: int, weights: np.ndarray) -> np.ndarray:
    directions = unit_vector(layout.positions)
    weights = np.asarray(weights, dtype=float)
    weights = weights - np.min(weights)
    if np.max(weights) > 0:
        weights = weights / np.max(weights)
    else:
        weights = np.ones_like(weights)

    selected = [int(np.argmax(weights))]
    min_distance = np.linalg.norm(directions - directions[selected[0]], axis=1)
    while len(selected) < count:
        score = min_distance * (0.70 + 0.30 * weights)
        score[np.asarray(selected, dtype=int)] = -1.0
        idx = int(np.argmax(score))
        selected.append(idx)
        new_distance = np.linalg.norm(directions - directions[idx], axis=1)
        min_distance = np.minimum(min_distance, new_distance)
    return np.asarray(selected, dtype=int)


def dictionary_sensor_weights(full_matrix: np.ndarray, n_sensors: int) -> np.ndarray:
    theta_energy = np.sum(np.abs(full_matrix[:n_sensors, :]) ** 2, axis=1)
    phi_energy = np.sum(np.abs(full_matrix[n_sensors:, :]) ** 2, axis=1)
    return theta_energy + phi_energy


def task_sensor_weights(layout, grid_positions: np.ndarray, frequencies_hz: np.ndarray) -> np.ndarray:
    templates = class_templates(grid_positions)
    n_sensors = layout.positions.shape[0]
    scores = np.zeros(n_sensors, dtype=float)
    for sensor_idx in range(n_sensors):
        class_features = []
        for template in templates:
            blocks = []
            for freq_hz in frequencies_hz:
                response = sensor_response(layout, template, float(freq_hz), np.asarray([sensor_idx]))
                blocks.append(np.log10(np.abs(response) + 1e-12))
                blocks.append(np.cos(np.angle(response)))
                blocks.append(np.sin(np.angle(response)))
            class_features.append(np.concatenate(blocks))
        features = np.vstack(class_features)
        scores[sensor_idx] = float(np.mean(np.var(features, axis=0)))
    return scores


def make_candidates(
    layout,
    full_matrix: np.ndarray,
    grid_positions: np.ndarray,
    counts: list[int],
) -> list[CandidateLayout]:
    n_total = layout.positions.shape[0]
    candidates = [
        CandidateLayout(
            name=f"full_grid_{n_total}",
            method="full_grid",
            indices=np.arange(n_total, dtype=int),
            note="Reference 9 x 18 upper-hemisphere grid.",
        )
    ]
    dictionary_weights = dictionary_sensor_weights(full_matrix, n_total)
    task_weights = task_sensor_weights(layout, grid_positions, CLASSIFICATION_FREQS_HZ)

    for count in counts:
        if count >= n_total:
            continue
        candidates.append(
            CandidateLayout(
                name=f"geometric_farthest_{count}",
                method="geometric_farthest",
                indices=farthest_point_subset(layout, count),
                note="Greedy farthest-point coverage on the 2pi hemisphere.",
            )
        )
        target_dirs = fibonacci_hemisphere_directions(count, theta_min_deg=6.0, theta_max_deg=86.0)
        candidates.append(
            CandidateLayout(
                name=f"fibonacci_snap_{count}",
                method="fibonacci_snap",
                indices=nearest_unique_snap(layout, target_dirs, count),
                note="Low-discrepancy Fibonacci directions snapped to the CST grid.",
            )
        )
        candidates.append(
            CandidateLayout(
                name=f"dictionary_weighted_{count}",
                method="dictionary_weighted",
                indices=weighted_farthest_subset(layout, count, dictionary_weights),
                note="Coverage weighted by equivalent-source dictionary row energy.",
            )
        )
        candidates.append(
            CandidateLayout(
                name=f"task_driven_{count}",
                method="task_driven",
                indices=weighted_farthest_subset(layout, count, task_weights),
                note="Coverage weighted by class-template feature separation.",
            )
        )
    return candidates


def matrix_metrics(full_matrix: np.ndarray, n_sensors: int, indices: np.ndarray) -> dict[str, float | int]:
    row_indices = np.concatenate([indices, indices + n_sensors])
    matrix = full_matrix[row_indices, :]
    column_norm = np.linalg.norm(matrix, axis=0)
    active = column_norm > 1e-14
    if np.count_nonzero(active) < 2:
        mutual_coherence = 0.0
    else:
        normalized = matrix[:, active] / column_norm[active][None, :]
        gram = np.abs(normalized.conj().T @ normalized)
        np.fill_diagonal(gram, 0.0)
        mutual_coherence = float(np.max(gram))

    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size:
        tol = float(singular_values[0] * 1e-10)
        rank = int(np.sum(singular_values > tol))
        stable_condition = float(singular_values[0] / singular_values[rank - 1]) if rank else math.inf
    else:
        rank = 0
        stable_condition = math.inf

    unknowns = int(full_matrix.shape[1])
    channels = int(matrix.shape[0])
    return {
        "measurement_channels": channels,
        "dictionary_unknowns": unknowns,
        "channel_unknown_ratio": float(channels / unknowns),
        "effective_rank": rank,
        "rank_ratio": float(rank / unknowns),
        "stable_condition": stable_condition,
        "mutual_coherence": mutual_coherence,
    }


def reconstruction_metrics(
    layout,
    grid_positions: np.ndarray,
    full_matrix: np.ndarray,
    candidate: CandidateLayout,
    snr_db: float,
    lam: float,
) -> dict[str, float]:
    rng = np.random.default_rng(stable_seed(candidate.name))
    sources = make_reference_sources(grid_positions)
    theta, phi, _ = farfield_grid()
    true_power, _, _ = farfield_pattern(sources, theta, phi, FREQ_HZ)
    values = sensor_response(layout, sources, FREQ_HZ, candidate.indices)
    values = add_complex_noise(values, snr_db, rng)
    rows = np.concatenate([candidate.indices, candidate.indices + layout.positions.shape[0]])
    matrix = full_matrix[rows, :]
    solution = solve_tikhonov(matrix, values, lam=lam)
    reconstructed = vector_to_source_set(grid_positions, solution, label=candidate.name)
    rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, FREQ_HZ)
    return pattern_metrics(true_power, rec_power, theta, phi)


def feature_vector(layout, sources, frequencies_hz: np.ndarray, indices: np.ndarray, snr_db: float, rng) -> np.ndarray:
    blocks = []
    for freq_hz in frequencies_hz:
        response = sensor_response(layout, sources, float(freq_hz), indices)
        response = add_complex_noise(response, snr_db, rng)
        blocks.append(np.log10(np.abs(response) + 1e-12))
        blocks.append(np.cos(np.angle(response)))
        blocks.append(np.sin(np.angle(response)))
    return np.concatenate(blocks)


def nearest_centroid_accuracy(
    layout,
    grid_positions: np.ndarray,
    candidate: CandidateLayout,
    samples_per_class: int,
    snr_db: float,
) -> float:
    rng = np.random.default_rng(stable_seed(candidate.name + "_classification"))
    templates = class_templates(grid_positions)
    x_rows = []
    y_rows = []
    for class_idx, template in enumerate(templates):
        for _ in range(samples_per_class):
            sample = jitter_sources(template, rng)
            x_rows.append(feature_vector(layout, sample, CLASSIFICATION_FREQS_HZ, candidate.indices, snr_db, rng))
            y_rows.append(class_idx)
    x = np.vstack(x_rows)
    y = np.asarray(y_rows, dtype=int)

    train_mask = np.zeros_like(y, dtype=bool)
    for class_idx in range(len(templates)):
        class_positions = np.flatnonzero(y == class_idx)
        split = int(round(0.70 * len(class_positions)))
        train_mask[class_positions[:split]] = True
    test_mask = ~train_mask

    mean = np.mean(x[train_mask], axis=0)
    std = np.std(x[train_mask], axis=0)
    std = np.where(std < 1e-12, 1.0, std)
    x_train = (x[train_mask] - mean) / std
    x_test = (x[test_mask] - mean) / std
    y_train = y[train_mask]
    y_test = y[test_mask]

    centroids = []
    for class_idx in range(len(templates)):
        centroids.append(np.mean(x_train[y_train == class_idx], axis=0))
    centroid_matrix = np.vstack(centroids)
    distances = np.linalg.norm(x_test[:, None, :] - centroid_matrix[None, :, :], axis=2)
    predictions = np.argmin(distances, axis=1)
    return float(np.mean(predictions == y_test))


def candidate_sensor_rows(layout, candidates: list[CandidateLayout]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for candidate in candidates:
        for order, sensor_idx in enumerate(candidate.indices):
            rows.append(
                {
                    "candidate": candidate.name,
                    "method": candidate.method,
                    "sensor_count": int(len(candidate.indices)),
                    "selection_order": int(order),
                    "sensor_id": int(sensor_idx),
                    "x_m": float(layout.positions[sensor_idx, 0]),
                    "y_m": float(layout.positions[sensor_idx, 1]),
                    "z_m": float(layout.positions[sensor_idx, 2]),
                    "theta_deg": float(np.rad2deg(layout.theta[sensor_idx])),
                    "phi_deg": float(np.rad2deg(layout.phi[sensor_idx])),
                    "radius_m": float(layout.radius_m),
                    "polarization_channels": "theta;phi",
                }
            )
    return rows


def write_readme(out_dir: Path, summary_rows: list[dict[str, object]]) -> None:
    ordered = sorted(summary_rows, key=lambda row: (int(row["sensor_count"]), float(row["mutual_coherence"])))
    candidate_lines = []
    for row in ordered:
        candidate_lines.append(
            "| {candidate} | {sensor_count} | {method} | {correlation:.4f} | {nmse:.4e} | {classification_accuracy:.3f} | {mutual_coherence:.4f} |".format(
                **row
            )
        )
    content = """# Sampling Layouts

This directory stores small, versionable candidate sensor layouts for the 2pi
hemisphere measurement workflow. The CSV files are generated by:

```powershell
python code\\optimize_sampling_layout.py
```

## Files

| File | Purpose |
|---|---|
| `hemisphere_sampling_candidates.csv` | One row per selected sensor in each candidate layout. |
| `sampling_layout_summary.csv` | Reconstruction, matrix, spatial, and classification proxy metrics. |
| `sampling_layout_summary.json` | Machine-readable summary metadata for scripts and dashboards. |

## Current Candidate Summary

| Candidate | Sensors | Method | Corr | NMSE | Accuracy | Mutual coherence |
|---|---:|---|---:|---:|---:|---:|
""" + "\n".join(candidate_lines) + """

These results are synthetic equivalent-source proxy evidence. They select the
next CST export cases; they do not replace validation on real CST near-field
and far-field CSV data.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, object]:
    layout = make_hemisphere_layout(
        n_theta=args.n_theta,
        n_phi=args.n_phi,
        radius_m=args.radius_m,
        theta_min_deg=args.theta_min_deg,
        theta_max_deg=args.theta_max_deg,
    )
    grid_positions = make_equivalent_grid()
    full_matrix = build_measurement_matrix(layout, grid_positions, FREQ_HZ)
    counts = sorted({int(c) for c in args.counts}, reverse=True)
    candidates = make_candidates(layout, full_matrix, grid_positions, counts)

    summary_rows: list[dict[str, object]] = []
    for candidate in candidates:
        row: dict[str, object] = {
            "candidate": candidate.name,
            "method": candidate.method,
            "sensor_count": int(len(candidate.indices)),
            "note": candidate.note,
            "frequency_hz": float(FREQ_HZ),
        }
        row.update(spatial_metrics(layout, candidate.indices))
        row.update(matrix_metrics(full_matrix, layout.positions.shape[0], candidate.indices))
        row.update(reconstruction_metrics(layout, grid_positions, full_matrix, candidate, args.snr_db, args.lambda_reg))
        if args.skip_classification:
            row["classification_accuracy"] = math.nan
        else:
            row["classification_accuracy"] = nearest_centroid_accuracy(
                layout,
                grid_positions,
                candidate,
                samples_per_class=args.samples_per_class,
                snr_db=args.classification_snr_db,
            )
        summary_rows.append(row)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sensor_columns = [
        "candidate",
        "method",
        "sensor_count",
        "selection_order",
        "sensor_id",
        "x_m",
        "y_m",
        "z_m",
        "theta_deg",
        "phi_deg",
        "radius_m",
        "polarization_channels",
    ]
    summary_columns = [
        "candidate",
        "method",
        "sensor_count",
        "measurement_channels",
        "dictionary_unknowns",
        "channel_unknown_ratio",
        "effective_rank",
        "rank_ratio",
        "stable_condition",
        "mutual_coherence",
        "min_angular_sep_deg",
        "median_nn_angular_sep_deg",
        "mean_theta_deg",
        "theta_span_deg",
        "nmse",
        "correlation",
        "main_lobe_error_deg",
        "peak_error_db",
        "classification_accuracy",
        "frequency_hz",
        "note",
    ]
    write_csv(out_dir / "hemisphere_sampling_candidates.csv", candidate_sensor_rows(layout, candidates), sensor_columns)
    write_csv(out_dir / "sampling_layout_summary.csv", summary_rows, summary_columns)
    summary = {
        "generated_by": "code/optimize_sampling_layout.py",
        "base_layout": {
            "n_theta": int(args.n_theta),
            "n_phi": int(args.n_phi),
            "sensor_count": int(layout.positions.shape[0]),
            "radius_m": float(args.radius_m),
            "theta_min_deg": float(args.theta_min_deg),
            "theta_max_deg": float(args.theta_max_deg),
        },
        "equivalent_source_unknowns": int(full_matrix.shape[1]),
        "frequency_hz": float(FREQ_HZ),
        "classification_frequencies_hz": [float(v) for v in CLASSIFICATION_FREQS_HZ],
        "summary_rows": summary_rows,
    }
    (out_dir / "sampling_layout_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, summary_rows)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate non-redundant 2pi hemisphere sampling layout candidates.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for candidate CSVs.")
    parser.add_argument("--counts", nargs="+", type=int, default=list(DEFAULT_COUNTS), help="Candidate sensor counts.")
    parser.add_argument("--n-theta", type=int, default=9, help="Base grid theta count.")
    parser.add_argument("--n-phi", type=int, default=18, help="Base grid phi count.")
    parser.add_argument("--radius-m", type=float, default=13.0, help="Hemisphere radius in meters.")
    parser.add_argument("--theta-min-deg", type=float, default=6.0, help="Smallest theta angle in degrees.")
    parser.add_argument("--theta-max-deg", type=float, default=86.0, help="Largest theta angle in degrees.")
    parser.add_argument("--snr-db", type=float, default=35.0, help="Reconstruction proxy SNR.")
    parser.add_argument("--classification-snr-db", type=float, default=25.0, help="Classification proxy SNR.")
    parser.add_argument("--samples-per-class", type=int, default=24, help="Synthetic samples per class for centroid accuracy.")
    parser.add_argument("--lambda-reg", type=float, default=1e-4, help="Tikhonov regularization strength.")
    parser.add_argument("--skip-classification", action="store_true", help="Skip centroid classification proxy.")
    args = parser.parse_args()

    summary = run(args)
    out_dir = Path(args.out_dir)
    print(f"sampling layout candidates written to {out_dir}")
    print(f"base sensors: {summary['base_layout']['sensor_count']}")
    print(f"candidates: {len(summary['summary_rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
