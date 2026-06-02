from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

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
DEFAULT_NEARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_nearfield.csv"
DEFAULT_FARFIELD = ROOT / "data" / "cst_exports" / "level1" / "all_farfield.csv"
DEFAULT_LAYOUTS = ROOT / "data" / "sampling_layouts" / "hemisphere_sampling_candidates.csv"
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_level1_tradeoff"
DEFAULT_CANDIDATES = (
    "full_grid_162",
    "geometric_farthest_120",
    "fibonacci_snap_120",
    "dictionary_weighted_120",
    "dictionary_weighted_81",
    "task_driven_48",
)
DEFAULT_X_SPAN = (-0.25, 0.25)
DEFAULT_Y_SPAN = (-0.25, 0.25)
DEFAULT_Z_SPAN = (3.75, 4.25)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def validate_inputs(nearfield: pd.DataFrame, farfield: pd.DataFrame) -> None:
    nf_report = validate_nearfield(nearfield)
    if not nf_report.ok:
        raise ValueError("nearfield validation failed: " + "; ".join(nf_report.errors))
    ff_report = validate_farfield(farfield)
    if not ff_report.ok:
        raise ValueError("farfield validation failed: " + "; ".join(ff_report.errors))
    pair_report = validate_pair(nearfield, farfield)
    if not pair_report.ok:
        raise ValueError("nearfield/farfield pair validation failed: " + "; ".join(pair_report.errors))


def load_candidate_layouts(path: Path, candidate_names: list[str] | None) -> dict[str, pd.DataFrame]:
    layouts = read_table(path)
    required = {"candidate", "method", "sensor_count", "selection_order", "sensor_id"}
    missing = sorted(required - set(layouts.columns))
    if missing:
        raise ValueError(f"layout table missing required columns: {missing}")
    layouts["candidate"] = layouts["candidate"].astype(str)
    if candidate_names:
        wanted = set(candidate_names)
        layouts = layouts[layouts["candidate"].isin(wanted)].copy()
        missing_candidates = sorted(wanted - set(layouts["candidate"]))
        if missing_candidates:
            raise ValueError(f"requested candidates not found in layout table: {missing_candidates}")

    grouped: dict[str, pd.DataFrame] = {}
    for name, group in layouts.groupby("candidate", sort=False):
        group = group.sort_values("selection_order").copy()
        grouped[str(name)] = group
    return grouped


def select_pairs(nearfield: pd.DataFrame, samples: list[str] | None, frequencies_hz: list[float] | None) -> list[tuple[str, float]]:
    pairs = available_sample_frequency_pairs(nearfield)
    if samples:
        sample_set = set(samples)
        pairs = [pair for pair in pairs if pair[0] in sample_set]
    if frequencies_hz:
        pairs = [pair for pair in pairs if any(np.isclose(pair[1], freq) for freq in frequencies_hz)]
    if not pairs:
        raise ValueError("no sample/frequency pairs match the selected filters")
    return pairs


def subset_nearfield(nearfield: pd.DataFrame, sensor_ids: np.ndarray) -> pd.DataFrame:
    work = nearfield.copy()
    work["sensor_id_numeric"] = pd.to_numeric(work["sensor_id"], errors="coerce")
    sub = work[work["sensor_id_numeric"].isin(sensor_ids)].drop(columns=["sensor_id_numeric"]).copy()
    return sub


def matrix_health(matrix: np.ndarray) -> dict[str, float | int]:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size == 0:
        return {"effective_rank": 0, "rank_ratio": 0.0, "stable_condition": math.inf}
    tol = float(singular_values[0] * 1e-10)
    rank = int(np.sum(singular_values > tol))
    if rank:
        condition = float(singular_values[0] / singular_values[rank - 1])
    else:
        condition = math.inf
    return {
        "effective_rank": rank,
        "rank_ratio": float(rank / matrix.shape[1]),
        "stable_condition": condition,
    }


def reconstruct_candidate(
    nearfield: pd.DataFrame,
    farfield: pd.DataFrame,
    candidate_name: str,
    candidate_group: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    grid_positions: np.ndarray,
    lambda_reg: float,
) -> dict[str, object]:
    sensor_ids_requested = pd.to_numeric(candidate_group["sensor_id"], errors="coerce").dropna().astype(int).to_numpy()
    candidate_nf = subset_nearfield(nearfield, sensor_ids_requested)
    measurement, sensor_ids_used = measurement_vector_from_nearfield(candidate_nf, sample_id, frequency_hz)
    layout = layout_from_nearfield(candidate_nf, sample_id, frequency_hz, sensor_ids_used)
    matrix = build_measurement_matrix(layout, grid_positions, frequency_hz, np.arange(layout.positions.shape[0]))
    solution = solve_tikhonov(matrix, measurement, lam=lambda_reg)
    reconstructed = vector_to_source_set(grid_positions, solution, label=f"{sample_id}_{candidate_name}")
    theta, phi, true_power, _ = farfield_power_from_table(farfield, sample_id, frequency_hz)
    rec_power, _, _ = farfield_pattern(reconstructed, theta, phi, frequency_hz)
    metrics = pattern_metrics(true_power, rec_power, theta, phi)
    row: dict[str, object] = {
        "sample_id": sample_id,
        "frequency_hz": float(frequency_hz),
        "candidate": candidate_name,
        "method": str(candidate_group["method"].iloc[0]),
        "sensor_count": int(len(sensor_ids_used)),
        "measurement_channels": int(measurement.size),
        "equivalent_source_points": int(grid_positions.shape[0]),
        "unknown_count": int(matrix.shape[1]),
        "channel_unknown_ratio": float(measurement.size / matrix.shape[1]),
        "lambda_reg": float(lambda_reg),
    }
    row.update(matrix_health(matrix))
    row.update(metrics)
    return row


def summarize(results: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    best_by_sample = []
    for (sample_id, frequency_hz), group in results.groupby(["sample_id", "frequency_hz"]):
        best = group.sort_values(["correlation", "nmse"], ascending=[False, True]).iloc[0]
        best_by_sample.append(
            {
                "sample_id": str(sample_id),
                "frequency_hz": float(frequency_hz),
                "best_candidate": str(best["candidate"]),
                "best_correlation": float(best["correlation"]),
                "best_nmse": float(best["nmse"]),
            }
        )

    by_candidate = (
        results.groupby(["candidate", "method", "sensor_count"], as_index=False)
        .agg(
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            mean_stable_condition=("stable_condition", "mean"),
        )
        .sort_values(["sensor_count", "mean_correlation"], ascending=[False, False])
    )
    by_candidate.to_csv(out_dir / "cst_sampling_tradeoff_by_candidate.csv", index=False, encoding="utf-8-sig")

    summary = {
        "generated_by": "code/run_cst_sampling_tradeoff.py",
        "nearfield": display_path(Path(args.nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "layouts": display_path(Path(args.layouts)),
        "out_dir": display_path(out_dir),
        "pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "candidate_count": int(results["candidate"].nunique()),
        "lambda_reg": float(args.lambda_reg),
        "grid_shape": [int(args.grid_nx), int(args.grid_ny), int(args.grid_nz)],
        "grid_span_m": {
            "x": [float(args.grid_x_min), float(args.grid_x_max)],
            "y": [float(args.grid_y_min), float(args.grid_y_max)],
            "z": [float(args.grid_z_min), float(args.grid_z_max)],
        },
        "best_by_sample": best_by_sample,
        "candidate_summary": by_candidate.to_dict(orient="records"),
    }
    (out_dir / "cst_sampling_tradeoff_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(out_dir, results, by_candidate, summary)
    return summary


def write_markdown_summary(out_dir: Path, results: pd.DataFrame, by_candidate: pd.DataFrame, summary: dict[str, object]) -> None:
    candidate_lines = []
    for row in by_candidate.itertuples(index=False):
        candidate_lines.append(
            f"| {row.candidate} | {int(row.sensor_count)} | {row.method} | {row.mean_correlation:.4f} | {row.min_correlation:.4f} | {row.mean_nmse:.4e} | {row.max_nmse:.4e} |"
        )

    detail_lines = []
    ordered = results.sort_values(["sample_id", "sensor_count", "candidate"], ascending=[True, False, True])
    for row in ordered.itertuples(index=False):
        detail_lines.append(
            f"| {row.sample_id} | {row.candidate} | {int(row.sensor_count)} | {row.correlation:.4f} | {row.nmse:.4e} | {row.main_lobe_error_deg:.2f} |"
        )

    full_grid = by_candidate[by_candidate["candidate"] == "full_grid_162"]
    if len(full_grid):
        full_min_corr = float(full_grid["min_correlation"].iloc[0])
        full_max_nmse = float(full_grid["max_nmse"].iloc[0])
    else:
        full_min_corr = float("nan")
        full_max_nmse = float("nan")
    if math.isfinite(full_min_corr) and full_min_corr >= 0.95 and full_max_nmse <= 1e-2:
        reading = """- Full-grid Level 1 reconstruction meets the current acceptance target.
- The 120-point candidates can be interpreted as real CST sampling tradeoff evidence.
- Lower-count candidates should still be kept for sparse/multifrequency reconstruction
  and recognition-priority experiments."""
    elif math.isfinite(full_min_corr) and full_min_corr >= 0.95 and full_max_nmse <= 3e-2:
        reading = """- Full-grid Level 1 reconstruction has passed the correlation and main-lobe sanity
  checks, but the worst-case NMSE is still above the strict `1e-2` target.
- This is useful CST calibration evidence: the near-field export, theta/phi
  projection, and far-field comparison chain are broadly consistent.
- Treat the sub-162 candidate ranking as calibration evidence for this Level 1
  source prior, not as the final airframe sampling conclusion."""
    else:
        reading = """- Full-grid Level 1 reconstruction does not yet meet the current acceptance target
  (`Corr >= 0.95`, `NMSE <= 1e-2`), so this table is a calibration diagnostic
  rather than a final sampling conclusion.
- The next action is to debug source-grid placement, CST near-field extraction,
  phase convention, theta/phi projection, and equivalent-source model settings.
- Candidate ranking below 162 sensors should not be used as the main report claim
  until the full-grid baseline is calibrated."""

    content = f"""# CST Level 1 Sampling Tradeoff

This compact evidence table evaluates the sampling candidates from
`data/sampling_layouts/hemisphere_sampling_candidates.csv` on the current local
Level 1 CST exports.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Candidate layouts | `{summary['layouts']}` |
| Equivalent-source grid | `{summary['grid_shape']}` over `{summary['grid_span_m']}` m |

## Candidate Summary

| Candidate | Sensors | Method | Mean Corr | Min Corr | Mean NMSE | Max NMSE |
|---|---:|---|---:|---:|---:|---:|
{chr(10).join(candidate_lines)}

## Per-Sample Results

| Sample | Candidate | Sensors | Corr | NMSE | Main-lobe error / deg |
|---|---|---:|---:|---:|---:|
{chr(10).join(detail_lines)}

## Reading

{reading}
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark sampling-layout candidates on CST near/far-field exports.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="CST near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="CST far-field CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for compact tradeoff tables.")
    parser.add_argument("--candidate", action="append", dest="candidates", help="Candidate name to include. Repeatable.")
    parser.add_argument("--all-candidates", action="store_true", help="Evaluate every candidate in the layout table.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    parser.add_argument("--grid-nx", type=int, default=5, help="Equivalent source grid count in x.")
    parser.add_argument("--grid-ny", type=int, default=3, help="Equivalent source grid count in y.")
    parser.add_argument("--grid-nz", type=int, default=3, help="Equivalent source grid count in z.")
    parser.add_argument("--grid-x-min", type=float, default=DEFAULT_X_SPAN[0], help="Equivalent source grid x min in meters.")
    parser.add_argument("--grid-x-max", type=float, default=DEFAULT_X_SPAN[1], help="Equivalent source grid x max in meters.")
    parser.add_argument("--grid-y-min", type=float, default=DEFAULT_Y_SPAN[0], help="Equivalent source grid y min in meters.")
    parser.add_argument("--grid-y-max", type=float, default=DEFAULT_Y_SPAN[1], help="Equivalent source grid y max in meters.")
    parser.add_argument("--grid-z-min", type=float, default=DEFAULT_Z_SPAN[0], help="Equivalent source grid z min in meters.")
    parser.add_argument("--grid-z-max", type=float, default=DEFAULT_Z_SPAN[1], help="Equivalent source grid z max in meters.")
    parser.add_argument(
        "--level1-center-source-grid",
        action="store_true",
        help="Use a single equivalent dipole at (0, 0, 4 m) for Level 1 standard-source calibration.",
    )
    parser.add_argument("--lambda-reg", type=float, default=1e-4, help="Tikhonov regularization lambda.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)

    candidate_names = None if args.all_candidates else list(args.candidates or DEFAULT_CANDIDATES)
    layouts = load_candidate_layouts(Path(args.layouts), candidate_names)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)
    if args.level1_center_source_grid:
        args.grid_nx = 1
        args.grid_ny = 1
        args.grid_nz = 1
        args.grid_x_min = 0.0
        args.grid_x_max = 0.0
        args.grid_y_min = 0.0
        args.grid_y_max = 0.0
        args.grid_z_min = 4.0
        args.grid_z_max = 4.0
    grid_positions = make_equivalent_grid(
        nx=args.grid_nx,
        ny=args.grid_ny,
        nz=args.grid_nz,
        x_span_m=(args.grid_x_min, args.grid_x_max),
        y_span_m=(args.grid_y_min, args.grid_y_max),
        z_span_m=(args.grid_z_min, args.grid_z_max),
    )

    rows: list[dict[str, object]] = []
    for sample_id, frequency_hz in pairs:
        for candidate_name, candidate_group in layouts.items():
            rows.append(
                reconstruct_candidate(
                    nearfield,
                    farfield,
                    candidate_name,
                    candidate_group,
                    sample_id,
                    frequency_hz,
                    grid_positions,
                    args.lambda_reg,
                )
            )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "cst_sampling_tradeoff_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, out_dir, args)

    print(f"CST sampling tradeoff written to {out_dir}")
    print(f"sample/frequency pairs: {summary['pair_count']}")
    print(f"candidates: {summary['candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
