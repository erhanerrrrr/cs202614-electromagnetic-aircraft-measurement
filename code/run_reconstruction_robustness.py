from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from em_core import (
    add_complex_noise,
    build_measurement_matrix,
    farfield_grid,
    farfield_pattern,
    farthest_point_subset,
    make_equivalent_grid,
    make_hemisphere_layout,
    make_reference_sources,
    pattern_metrics,
    random_subset,
    sensor_response,
    vector_to_source_set,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "outputs" / "reconstruction_robustness"
FREQ_HZ = 1_200_000_000.0
SNR_VALUES_DB = [20.0, 25.0, 30.0, 35.0, 40.0]
LAMBDA_VALUES = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2]


def solve_tikhonov_fast(matrix: np.ndarray, values: np.ndarray, lam: float) -> np.ndarray:
    gram = matrix.conj().T @ matrix
    rhs = matrix.conj().T @ values
    reg = lam * np.eye(matrix.shape[1], dtype=np.complex128)
    return np.linalg.solve(gram + reg, rhs)


def sensor_cases(layout, rng: np.random.Generator) -> dict[str, np.ndarray]:
    n_total = layout.positions.shape[0]
    return {
        "full_100": np.arange(n_total, dtype=int),
        "optimized_75": farthest_point_subset(layout, int(round(0.75 * n_total))),
        "optimized_50": farthest_point_subset(layout, int(round(0.50 * n_total))),
        "optimized_25": farthest_point_subset(layout, int(round(0.25 * n_total))),
        "random_50": random_subset(n_total, int(round(0.50 * n_total)), rng),
    }


def run_scan(out_dir: Path, trials: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    layout = make_hemisphere_layout(n_theta=9, n_phi=18, radius_m=13.0)
    grid_positions = make_equivalent_grid(nx=4, ny=3, nz=3)
    sources = make_reference_sources(grid_positions)
    theta, phi, _ = farfield_grid(n_theta=37, n_phi=72)
    true_power, _, _ = farfield_pattern(sources, theta, phi, FREQ_HZ)

    cases = sensor_cases(layout, rng)
    matrices = {
        name: build_measurement_matrix(layout, grid_positions, FREQ_HZ, indices)
        for name, indices in cases.items()
    }
    clean_values = {
        name: sensor_response(layout, sources, FREQ_HZ, indices)
        for name, indices in cases.items()
    }

    rows: list[dict[str, object]] = []
    for case_name, indices in cases.items():
        matrix = matrices[case_name]
        values = clean_values[case_name]
        for snr_db in SNR_VALUES_DB:
            for trial_idx in range(trials):
                noisy = add_complex_noise(values, snr_db, rng)
                for lam in LAMBDA_VALUES:
                    solution = solve_tikhonov_fast(matrix, noisy, lam)
                    reconstructed = vector_to_source_set(grid_positions, solution)
                    rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, FREQ_HZ)
                    metrics = pattern_metrics(true_power, rec_power, theta, phi)
                    rows.append(
                        {
                            "case": case_name,
                            "sensor_points": int(len(indices)),
                            "measurement_channels": int(2 * len(indices)),
                            "sensor_fraction": float(len(indices) / layout.positions.shape[0]),
                            "snr_db": float(snr_db),
                            "trial": int(trial_idx),
                            "lambda": float(lam),
                            "frequency_hz": float(FREQ_HZ),
                            **metrics,
                        }
                    )

    raw = pd.DataFrame(rows)
    summary = (
        raw.groupby(["case", "sensor_points", "measurement_channels", "sensor_fraction", "snr_db", "lambda"], as_index=False)
        .agg(
            nmse_mean=("nmse", "mean"),
            nmse_std=("nmse", "std"),
            correlation_mean=("correlation", "mean"),
            correlation_std=("correlation", "std"),
            main_lobe_error_deg_mean=("main_lobe_error_deg", "mean"),
            peak_error_db_mean=("peak_error_db", "mean"),
        )
        .sort_values(["case", "snr_db", "nmse_mean"])
    )
    best_idx = summary.groupby(["case", "snr_db"])["nmse_mean"].idxmin()
    best = summary.loc[best_idx].sort_values(["snr_db", "sensor_points", "case"]).reset_index(drop=True)

    raw.to_csv(out_dir / "reconstruction_robustness_raw.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(out_dir / "reconstruction_robustness_summary.csv", index=False, encoding="utf-8-sig")
    best.to_csv(out_dir / "reconstruction_robustness_best.csv", index=False, encoding="utf-8-sig")
    return raw, summary, best


def plot_noise_robustness(best: pd.DataFrame, out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    for case_name in ["full_100", "optimized_75", "optimized_50", "optimized_25", "random_50"]:
        sub = best[best["case"] == case_name].sort_values("snr_db")
        if sub.empty:
            continue
        ax.plot(sub["snr_db"], sub["nmse_mean"], marker="o", linewidth=1.8, label=case_name)
    ax.set_yscale("log")
    ax.set_xlabel("SNR / dB")
    ax.set_ylabel("far-field NMSE")
    ax.set_title("Reconstruction robustness vs noise")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "reconstruction_noise_robustness.png", dpi=220)
    plt.close(fig)


def plot_sensor_tradeoff(best: pd.DataFrame, out_dir: Path, snr_db: float = 30.0) -> None:
    sub = best[np.isclose(best["snr_db"], snr_db)].copy()
    sub = sub[sub["case"] != "random_50"].sort_values("sensor_points")
    fig, ax1 = plt.subplots(figsize=(8.0, 5.2))
    ax1.plot(sub["sensor_points"], sub["nmse_mean"], "o-", color="#2563eb", label="NMSE")
    ax1.set_yscale("log")
    ax1.set_xlabel("sensor points")
    ax1.set_ylabel("NMSE", color="#2563eb")
    ax1.tick_params(axis="y", labelcolor="#2563eb")
    ax2 = ax1.twinx()
    ax2.plot(sub["sensor_points"], sub["correlation_mean"], "s--", color="#ea580c", label="correlation")
    ax2.set_ylabel("correlation", color="#ea580c")
    ax2.tick_params(axis="y", labelcolor="#ea580c")
    ax1.set_title(f"Sensor-count tradeoff at SNR={snr_db:.0f} dB")
    ax1.grid(True, which="both", alpha=0.25)
    for _, row in sub.iterrows():
        ax1.annotate(row["case"], (row["sensor_points"], row["nmse_mean"]), fontsize=8, xytext=(4, 4), textcoords="offset points")
    fig.tight_layout()
    fig.savefig(out_dir / "reconstruction_sensor_tradeoff_30dB.png", dpi=220)
    plt.close(fig)


def plot_lambda_scan(summary: pd.DataFrame, out_dir: Path, case_name: str = "optimized_50", snr_db: float = 30.0) -> None:
    sub = summary[(summary["case"] == case_name) & np.isclose(summary["snr_db"], snr_db)].sort_values("lambda")
    fig, ax = plt.subplots(figsize=(7.6, 5.0))
    ax.plot(sub["lambda"], sub["nmse_mean"], "o-", color="#0f766e")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("lambda")
    ax.set_ylabel("far-field NMSE")
    ax.set_title(f"Tikhonov regularization scan: {case_name}, SNR={snr_db:.0f} dB")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_dir / "reconstruction_lambda_scan_optimized50_30dB.png", dpi=220)
    plt.close(fig)


def write_summary_markdown(best: pd.DataFrame, out_dir: Path) -> None:
    key = best[np.isclose(best["snr_db"], 30.0)].copy().sort_values(["sensor_points", "case"])
    rows = []
    for _, row in key.iterrows():
        rows.append(
            f"| {row['case']} | {int(row['sensor_points'])} | {int(row['measurement_channels'])} | "
            f"{row['lambda']:.0e} | {row['nmse_mean']:.3e} | {row['correlation_mean']:.5f} | "
            f"{row['main_lobe_error_deg_mean']:.2f} |"
        )
    content = f"""# Reconstruction robustness evidence

This is a synthetic physics robustness scan for the equivalent-source reconstruction path.
It validates the experiment machinery before real CST Level 1/Level 2 exports are available.

## 30 dB SNR best-lambda summary

| Case | Sensors | Channels | Lambda | NMSE mean | Correlation mean | Main-lobe error / deg |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Output files

| File | Use |
|---|---|
| `reconstruction_robustness_raw.csv` | Every trial/case/SNR/lambda metric row. |
| `reconstruction_robustness_summary.csv` | Mean/std grouped by case, SNR, lambda. |
| `reconstruction_robustness_best.csv` | Best lambda for every case and SNR. |
| `reconstruction_noise_robustness.png` | NMSE versus SNR. |
| `reconstruction_sensor_tradeoff_30dB.png` | Sensor-count versus NMSE/correlation. |
| `reconstruction_lambda_scan_optimized50_30dB.png` | Lambda scan for the 50% optimized case. |

These numbers must be replaced or repeated with real CST exports before final submission.
"""
    (out_dir / "reconstruction_robustness_evidence.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run synthetic reconstruction robustness scans for CS-202614.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--trials", type=int, default=4, help="Noise trials per case/SNR/lambda.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw, summary, best = run_scan(out_dir, args.trials, args.seed)
    plot_noise_robustness(best, out_dir)
    plot_sensor_tradeoff(best, out_dir)
    plot_lambda_scan(summary, out_dir)
    write_summary_markdown(best, out_dir)

    payload = {
        "frequency_hz": FREQ_HZ,
        "snr_values_db": SNR_VALUES_DB,
        "lambda_values": LAMBDA_VALUES,
        "trials_per_case": args.trials,
        "raw_rows": int(len(raw)),
        "summary_rows": int(len(summary)),
        "best_rows": int(len(best)),
        "note": "Synthetic robustness evidence only. Repeat with real CST exports for final scoring evidence.",
    }
    (out_dir / "reconstruction_robustness_metadata.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Reconstruction robustness complete: {out_dir}")
    print(best[np.isclose(best["snr_db"], 30.0)][["case", "sensor_points", "lambda", "nmse_mean", "correlation_mean"]].to_string(index=False))


if __name__ == "__main__":
    main()
