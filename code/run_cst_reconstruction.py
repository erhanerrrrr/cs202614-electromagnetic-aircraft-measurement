from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from cst_io import (
    available_sample_frequency_pairs,
    farfield_power_from_table,
    layout_from_nearfield,
    measurement_vector_from_nearfield,
    read_table,
    validate_farfield,
    validate_nearfield,
    validate_pair,
)
from em_core import build_measurement_matrix, farfield_pattern, make_equivalent_grid, pattern_metrics, solve_tikhonov, vector_to_source_set


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run equivalent-source reconstruction from CST near-field/far-field exports.")
    parser.add_argument("--nearfield", required=True, help="Path to CST near-field CSV/XLSX.")
    parser.add_argument("--farfield", help="Optional CST far-field truth CSV/XLSX.")
    parser.add_argument("--sample-id", help="Sample id to reconstruct. Defaults to the first near-field sample.")
    parser.add_argument("--frequency-hz", type=float, help="Frequency in Hz. Defaults to the first near-field frequency.")
    parser.add_argument("--out-dir", default=str(ROOT / "outputs" / "cst_reconstruction"), help="Output directory.")
    parser.add_argument("--grid-nx", type=int, default=5, help="Equivalent source grid count in x.")
    parser.add_argument("--grid-ny", type=int, default=3, help="Equivalent source grid count in y.")
    parser.add_argument("--grid-nz", type=int, default=3, help="Equivalent source grid count in z.")
    parser.add_argument("--lambda-reg", type=float, default=1e-4, help="Tikhonov regularization lambda.")
    return parser.parse_args()


def normalize_db(power: np.ndarray) -> np.ndarray:
    return 10.0 * np.log10(power / np.maximum(np.max(power), 1e-15) + 1e-12)


def infer_grid_shape(theta: np.ndarray, phi: np.ndarray, shape: tuple[int, int] | None) -> tuple[np.ndarray, np.ndarray, tuple[int, int]] | None:
    if shape is None:
        return None
    theta_deg = np.round(np.rad2deg(theta), 10)
    phi_deg = np.round(np.rad2deg(phi), 10)
    order = np.lexsort((phi_deg, theta_deg))
    return theta[order], phi[order], shape


def plot_farfield_compare(
    true_power: np.ndarray,
    rec_power: np.ndarray,
    theta: np.ndarray,
    phi: np.ndarray,
    shape: tuple[int, int] | None,
    out_path: Path,
) -> None:
    grid_info = infer_grid_shape(theta, phi, shape)
    if grid_info is None:
        fig, ax = plt.subplots(figsize=(7.5, 5.4))
        sc = ax.scatter(np.rad2deg(phi), np.rad2deg(theta), c=normalize_db(rec_power) - normalize_db(true_power), cmap="coolwarm", s=12, vmin=-6, vmax=6)
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        ax.set_title("Far-field difference / dB")
        fig.colorbar(sc, ax=ax)
        fig.tight_layout()
        fig.savefig(out_path, dpi=220)
        plt.close(fig)
        return

    theta_ordered, phi_ordered, grid_shape = grid_info
    theta_deg = np.round(np.rad2deg(theta), 10)
    phi_deg = np.round(np.rad2deg(phi), 10)
    order = np.lexsort((phi_deg, theta_deg))
    true_db = normalize_db(true_power[order]).reshape(grid_shape)
    rec_db = normalize_db(rec_power[order]).reshape(grid_shape)
    diff = rec_db - true_db

    panels = [true_db, rec_db, diff]
    titles = ["CST far-field truth", "Equivalent-source reconstruction", "Difference / dB"]
    cmaps = ["magma", "magma", "coolwarm"]
    vmins = [-35, -35, -6]
    vmaxs = [0, 0, 6]
    extent = [
        float(np.min(np.rad2deg(phi_ordered))),
        float(np.max(np.rad2deg(phi_ordered))),
        float(np.min(np.rad2deg(theta_ordered))),
        float(np.max(np.rad2deg(theta_ordered))),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, data, title, cmap, vmin, vmax in zip(axes, panels, titles, cmaps, vmins, vmaxs):
        im = ax.imshow(data, origin="lower", aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax, extent=extent)
        ax.set_title(title)
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        fig.colorbar(im, ax=ax, shrink=0.82)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_reconstructed_only(rec_power: np.ndarray, theta: np.ndarray, phi: np.ndarray, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5.4))
    sc = ax.scatter(np.rad2deg(phi), np.rad2deg(theta), c=normalize_db(rec_power), cmap="magma", s=12, vmin=-35, vmax=0)
    ax.set_xlabel("phi / deg")
    ax.set_ylabel("theta / deg")
    ax.set_title("Reconstructed far-field / dB")
    fig.colorbar(sc, ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220)
    plt.close(fig)


def write_metrics(out_dir: Path, metrics: dict[str, float | str | int]) -> None:
    pd.DataFrame([metrics]).to_csv(out_dir / "cst_reconstruction_metrics.csv", index=False, encoding="utf-8-sig")
    (out_dir / "cst_reconstruction_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    nearfield = read_table(args.nearfield)
    nf_report = validate_nearfield(nearfield)
    if not nf_report.ok:
        print("Near-field validation failed:")
        print("\n".join(nf_report.errors))
        return 2

    farfield = None
    ff_report = None
    if args.farfield:
        farfield = read_table(args.farfield)
        ff_report = validate_farfield(farfield)
        pair_report = validate_pair(nearfield, farfield) if ff_report.ok else None
        if not ff_report.ok or (pair_report is not None and not pair_report.ok):
            print("Far-field validation failed:")
            print("\n".join(ff_report.errors))
            if pair_report is not None:
                print("\n".join(pair_report.errors))
            return 2

    pairs = available_sample_frequency_pairs(nearfield)
    if not pairs:
        raise ValueError("nearfield has no sample/frequency pairs")
    sample_id = args.sample_id or pairs[0][0]
    frequency_hz = float(args.frequency_hz if args.frequency_hz is not None else pairs[0][1])

    measurement, sensor_ids = measurement_vector_from_nearfield(nearfield, sample_id, frequency_hz)
    layout = layout_from_nearfield(nearfield, sample_id, frequency_hz, sensor_ids)
    grid_positions = make_equivalent_grid(nx=args.grid_nx, ny=args.grid_ny, nz=args.grid_nz)
    matrix = build_measurement_matrix(layout, grid_positions, frequency_hz, np.arange(layout.positions.shape[0]))
    solution = solve_tikhonov(matrix, measurement, lam=args.lambda_reg)
    reconstructed = vector_to_source_set(grid_positions, solution, label=f"{sample_id}_reconstructed")

    metrics: dict[str, float | str | int] = {
        "sample_id": sample_id,
        "frequency_hz": frequency_hz,
        "sensor_points": int(layout.positions.shape[0]),
        "measurement_channels": int(measurement.size),
        "equivalent_source_points": int(grid_positions.shape[0]),
        "unknown_count": int(matrix.shape[1]),
        "lambda_reg": float(args.lambda_reg),
        "nearfield_path": str(Path(args.nearfield)),
    }

    if farfield is not None:
        theta, phi, true_power, shape = farfield_power_from_table(farfield, sample_id, frequency_hz)
        rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, frequency_hz)
        metrics.update(pattern_metrics(true_power, rec_power, theta, phi))
        metrics["farfield_path"] = str(Path(args.farfield))
        plot_farfield_compare(true_power, rec_power, theta, phi, shape, out_dir / "cst_farfield_reconstruction_compare.png")
    else:
        theta = layout.theta
        phi = layout.phi
        rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, frequency_hz)
        plot_reconstructed_only(rec_power, theta, phi, out_dir / "cst_farfield_reconstruction.png")

    source_df = pd.DataFrame(
        {
            "source_id": np.arange(grid_positions.shape[0]),
            "x_m": grid_positions[:, 0],
            "y_m": grid_positions[:, 1],
            "z_m": grid_positions[:, 2],
            "jx_real": np.real(reconstructed.moments[:, 0]),
            "jx_imag": np.imag(reconstructed.moments[:, 0]),
            "jy_real": np.real(reconstructed.moments[:, 1]),
            "jy_imag": np.imag(reconstructed.moments[:, 1]),
            "jz_real": np.real(reconstructed.moments[:, 2]),
            "jz_imag": np.imag(reconstructed.moments[:, 2]),
            "moment_norm": np.linalg.norm(reconstructed.moments, axis=1),
        }
    )
    source_df.to_csv(out_dir / "equivalent_source_solution.csv", index=False, encoding="utf-8-sig")
    write_metrics(out_dir, metrics)

    print(f"CST reconstruction complete: {out_dir}")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
