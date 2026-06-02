from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import read_table
from em_core import make_equivalent_grid
from run_cst_sampling_tradeoff import (
    DEFAULT_FARFIELD,
    DEFAULT_LAYOUTS,
    DEFAULT_NEARFIELD,
    ROOT,
    display_path,
    load_candidate_layouts,
    reconstruct_candidate,
    select_pairs,
    validate_inputs,
)


DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "cst_level1_source_model_sweep"
DEFAULT_LAMBDAS = (1e-2, 1e-3, 1e-4, 1e-5)
DEFAULT_CANDIDATES = ("full_grid_162",)


@dataclass(frozen=True)
class GridConfig:
    model_id: str
    note: str
    nx: int
    ny: int
    nz: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float


def default_grid_configs() -> tuple[GridConfig, ...]:
    return (
        GridConfig("single_center", "Known Level 1 source prior at (0, 0, 4 m).", 1, 1, 1, 0.0, 0.0, 0.0, 0.0, 4.0, 4.0),
        GridConfig("z_line_3", "Three possible source depths around the Level 1 center.", 1, 1, 3, 0.0, 0.0, 0.0, 0.0, 3.75, 4.25),
        GridConfig("xy_plane_3x3", "Lateral uncertainty at the known Level 1 height.", 3, 3, 1, -0.25, 0.25, -0.25, 0.25, 4.0, 4.0),
        GridConfig("compact_cube_3x3x3", "Compact local uncertainty volume around the Level 1 source.", 3, 3, 3, -0.10, 0.10, -0.10, 0.10, 3.90, 4.10),
        GridConfig("default_cube_5x3x3", "Current generic grid used by cst_level1_tradeoff.", 5, 3, 3, -0.25, 0.25, -0.25, 0.25, 3.75, 4.25),
        GridConfig("wide_cube_5x5x3", "Wider local uncertainty volume for stress testing.", 5, 5, 3, -0.50, 0.50, -0.50, 0.50, 3.50, 4.50),
    )


def acceptance_status(row: pd.Series) -> str:
    min_corr = float(row["min_correlation"])
    max_nmse = float(row["max_nmse"])
    max_lobe_error = float(row["max_main_lobe_error_deg"])
    if min_corr >= 0.95 and max_nmse <= 1e-2 and max_lobe_error <= 5.0:
        return "strict_pass"
    if min_corr >= 0.95 and max_nmse <= 3e-2 and max_lobe_error <= 5.0:
        return "corr_pass_nmse_near"
    if min_corr >= 0.95 and max_lobe_error <= 5.0:
        return "corr_lobe_pass_nmse_open"
    return "diagnostic_only"


def status_rank(status: str) -> int:
    order = {
        "strict_pass": 0,
        "corr_pass_nmse_near": 1,
        "corr_lobe_pass_nmse_open": 2,
        "diagnostic_only": 3,
    }
    return order.get(status, 99)


def select_configs(names: list[str] | None) -> list[GridConfig]:
    configs = list(default_grid_configs())
    if not names:
        return configs
    by_name = {config.model_id: config for config in configs}
    missing = sorted(set(names) - set(by_name))
    if missing:
        raise ValueError(f"unknown grid configs: {missing}")
    return [by_name[name] for name in names]


def config_to_grid(config: GridConfig) -> np.ndarray:
    return make_equivalent_grid(
        nx=config.nx,
        ny=config.ny,
        nz=config.nz,
        x_span_m=(config.x_min, config.x_max),
        y_span_m=(config.y_min, config.y_max),
        z_span_m=(config.z_min, config.z_max),
    )


def run_sweep(args: argparse.Namespace) -> pd.DataFrame:
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)

    layouts = load_candidate_layouts(Path(args.layouts), args.candidates)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)
    configs = select_configs(args.configs)
    lambda_regs = args.lambda_regs or list(DEFAULT_LAMBDAS)

    rows: list[dict[str, object]] = []
    for config in configs:
        grid_positions = config_to_grid(config)
        config_payload = asdict(config)
        for lambda_reg in lambda_regs:
            for sample_id, frequency_hz in pairs:
                for candidate_name, candidate_group in layouts.items():
                    row = reconstruct_candidate(
                        nearfield=nearfield,
                        farfield=farfield,
                        candidate_name=candidate_name,
                        candidate_group=candidate_group,
                        sample_id=sample_id,
                        frequency_hz=frequency_hz,
                        grid_positions=grid_positions,
                        lambda_reg=lambda_reg,
                    )
                    row.update(config_payload)
                    row["grid_points"] = int(grid_positions.shape[0])
                    rows.append(row)
    return pd.DataFrame(rows)


def summarize(results: pd.DataFrame, out_dir: Path, args: argparse.Namespace) -> dict[str, object]:
    by_model = (
        results.groupby(
            [
                "model_id",
                "note",
                "candidate",
                "lambda_reg",
                "nx",
                "ny",
                "nz",
                "x_min",
                "x_max",
                "y_min",
                "y_max",
                "z_min",
                "z_max",
                "grid_points",
            ],
            as_index=False,
        )
        .agg(
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_stable_condition=("stable_condition", "mean"),
        )
    )
    by_model["status"] = by_model.apply(acceptance_status, axis=1)
    by_model["status_rank"] = by_model["status"].map(status_rank)
    by_model = by_model.sort_values(
        ["status_rank", "min_correlation", "max_nmse", "max_main_lobe_error_deg"],
        ascending=[True, False, True, True],
    )
    by_model = by_model.drop(columns=["status_rank"])
    by_model.to_csv(out_dir / "cst_source_model_sweep_by_model.csv", index=False, encoding="utf-8-sig")

    best = by_model.iloc[0]
    summary = {
        "generated_by": "code/run_cst_source_model_sweep.py",
        "nearfield": display_path(Path(args.nearfield)),
        "farfield": display_path(Path(args.farfield)),
        "layouts": display_path(Path(args.layouts)),
        "out_dir": display_path(out_dir),
        "pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "candidate_count": int(results["candidate"].nunique()),
        "model_count": int(results["model_id"].nunique()),
        "lambda_regs": [float(value) for value in sorted(results["lambda_reg"].unique())],
        "best_model": {
            "model_id": str(best["model_id"]),
            "candidate": str(best["candidate"]),
            "lambda_reg": float(best["lambda_reg"]),
            "status": str(best["status"]),
            "min_correlation": float(best["min_correlation"]),
            "max_nmse": float(best["max_nmse"]),
            "max_main_lobe_error_deg": float(best["max_main_lobe_error_deg"]),
        },
    }
    (out_dir / "cst_source_model_sweep_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown_summary(out_dir, by_model, summary)
    return summary


def write_markdown_summary(out_dir: Path, by_model: pd.DataFrame, summary: dict[str, object]) -> None:
    rows = []
    for row in by_model.itertuples(index=False):
        rows.append(
            f"| {row.model_id} | {row.candidate} | {row.lambda_reg:.0e} | {int(row.grid_points)} | {row.status} | "
            f"{row.min_correlation:.4f} | {row.max_nmse:.4e} | {row.max_main_lobe_error_deg:.2f} |"
        )

    best = summary["best_model"]
    best_status = best["status"]
    if best_status == "strict_pass":
        reading = """- At least one source model meets the strict Level 1 calibration target.
- Use that model as the next baseline before comparing lower-count layouts."""
    elif best_status == "corr_pass_nmse_near":
        reading = """- The best model passes correlation and main-lobe checks, but worst-case NMSE
  is still slightly above the strict target.
- The current data path is credible; the next work is NMSE-focused calibration
  through source priors, regularization, and phase/reference checks."""
    elif best_status == "corr_lobe_pass_nmse_open":
        reading = """- The best model passes correlation and main-lobe checks, but NMSE remains open.
- Treat this as source-model calibration evidence, not final sampling proof."""
    else:
        reading = """- No scanned source model meets the current Level 1 calibration target.
- Keep the result as a diagnostic and expand the model family before making
  lower-count sampling claims."""

    content = f"""# CST Level 1 Source-Model Sweep

This directory stores a compact calibration sweep for the Level 1 CST exports.
It tests whether the full 162-point measurement baseline can be explained by
different equivalent-source grids and Tikhonov regularization values.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Candidate layouts | `{summary['layouts']}` |

## Best Model

| Field | Value |
|---|---|
| Model | `{best['model_id']}` |
| Candidate | `{best['candidate']}` |
| Lambda | `{best['lambda_reg']:.0e}` |
| Status | `{best['status']}` |
| Min Corr | `{best['min_correlation']:.4f}` |
| Max NMSE | `{best['max_nmse']:.4e}` |
| Max main-lobe error / deg | `{best['max_main_lobe_error_deg']:.2f}` |

## Model Ranking

| Model | Candidate | Lambda | Grid points | Status | Min Corr | Max NMSE | Max lobe error / deg |
|---|---|---:|---:|---|---:|---:|---:|
{chr(10).join(rows)}

## Reading

{reading}
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sweep Level 1 CST equivalent-source model settings.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="CST near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="CST far-field CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for sweep tables.")
    parser.add_argument("--candidate", action="append", dest="candidates", help="Candidate layout to include. Repeatable.")
    parser.add_argument("--config", action="append", dest="configs", help="Grid config id to include. Repeatable.")
    parser.add_argument("--lambda-reg", action="append", dest="lambda_regs", type=float, help="Regularization value. Repeatable.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    parser.add_argument("--list-configs", action="store_true", help="Print available grid config ids and exit.")
    args = parser.parse_args()
    if args.list_configs:
        for config in default_grid_configs():
            print(f"{config.model_id}: {config.note}")
        raise SystemExit(0)
    args.candidates = args.candidates or list(DEFAULT_CANDIDATES)
    return args


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results = run_sweep(args)
    if results.empty:
        raise ValueError("source-model sweep produced no rows")
    results.to_csv(out_dir / "cst_source_model_sweep_results.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, out_dir, args)
    print(f"CST source-model sweep written to {out_dir}")
    print(f"best model: {summary['best_model']['model_id']} ({summary['best_model']['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
