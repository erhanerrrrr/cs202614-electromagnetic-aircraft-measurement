from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from cst_io import read_table
from run_cst_sampling_tradeoff import DEFAULT_LAYOUTS, load_candidate_layouts, subset_nearfield, validate_inputs
from run_spherical_nf_ff_baseline import (
    DEFAULT_FARFIELD,
    DEFAULT_LAMBDAS,
    DEFAULT_LMAX_VALUES,
    DEFAULT_NEARFIELD,
    rel,
    run_one_case,
    safe_float,
    select_pairs,
    status_for_row,
    status_rank,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "sampling_layouts" / "spherical_nf_ff_tradeoff"
PASSING_STATUS_RANK = 1


def numeric_sensor_ids(candidate_group: pd.DataFrame) -> np.ndarray:
    sensor_ids = pd.to_numeric(candidate_group["sensor_id"], errors="coerce").dropna().astype(int).to_numpy()
    sensor_ids = np.unique(sensor_ids)
    if sensor_ids.size == 0:
        raise ValueError("candidate layout has no numeric sensor_id values")
    return sensor_ids


def present_sensor_ids(nearfield: pd.DataFrame) -> set[int]:
    values = pd.to_numeric(nearfield["sensor_id"], errors="coerce").dropna().astype(int)
    return set(int(value) for value in values.unique())


def row_record(row: pd.Series) -> dict[str, object]:
    return {
        "candidate": str(row["candidate"]),
        "method": str(row["candidate_method"]),
        "sensor_count": int(row["requested_sensor_count"]),
        "lmax": int(row["lmax"]),
        "lambda_reg": float(row["lambda_reg"]),
        "include_l0": bool(row["include_l0"]),
        "mode_count": int(row["mode_count"]),
        "status": str(row["status"]),
        "min_correlation": float(row["min_correlation"]),
        "max_nmse": float(row["max_nmse"]),
        "max_main_lobe_error_deg": float(row["max_main_lobe_error_deg"]),
        "max_nearfield_fit_relative_error": float(row["max_nearfield_fit_relative_error"]),
        "min_farfield_total_complex_correlation_abs": safe_float(
            row.get("min_farfield_total_complex_correlation_abs")
        ),
        "max_farfield_total_complex_relative_l2_error": safe_float(
            row.get("max_farfield_total_complex_relative_l2_error")
        ),
        "max_basis_condition": float(row["max_basis_condition"]),
    }


def run_sweep(args: argparse.Namespace) -> pd.DataFrame:
    nearfield = read_table(args.nearfield)
    farfield = read_table(args.farfield)
    validate_inputs(nearfield, farfield)

    layouts = load_candidate_layouts(Path(args.layouts), args.candidates)
    pairs = select_pairs(nearfield, args.samples, args.frequencies_hz)

    rows: list[dict[str, object]] = []
    for candidate_name, candidate_group in layouts.items():
        sensor_ids = numeric_sensor_ids(candidate_group)
        candidate_method = str(candidate_group["method"].iloc[0])
        candidate_nearfield = subset_nearfield(nearfield, sensor_ids)
        present_ids = present_sensor_ids(candidate_nearfield)
        missing_ids = sorted(set(int(value) for value in sensor_ids) - present_ids)

        for sample_id, frequency_hz in pairs:
            for lmax in args.lmax_values:
                for lambda_reg in args.lambda_regs:
                    row = run_one_case(
                        nearfield=candidate_nearfield,
                        farfield=farfield,
                        sample_id=sample_id,
                        frequency_hz=frequency_hz,
                        lmax=lmax,
                        lambda_reg=lambda_reg,
                        include_l0=bool(args.include_l0),
                    )
                    sensor_count = int(row["sensor_count"])
                    mode_count = int(row["mode_count"])
                    row.update(
                        {
                            "candidate": candidate_name,
                            "candidate_method": candidate_method,
                            "requested_sensor_count": int(sensor_ids.size),
                            "missing_sensor_count": int(len(missing_ids)),
                            "layout_path": rel(Path(args.layouts)),
                            "component_sample_count": sensor_count,
                            "channel_count": int(2 * sensor_count),
                            "mode_sensor_ratio": float(mode_count / max(sensor_count, 1)),
                            "is_component_underdetermined": bool(mode_count > sensor_count),
                        }
                    )
                    rows.append(row)

    results = pd.DataFrame(rows)
    if results.empty:
        raise ValueError("spherical NF-FF tradeoff produced no rows")
    return results


def build_tables(results: pd.DataFrame, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_setting = (
        results.groupby(
            [
                "candidate",
                "candidate_method",
                "requested_sensor_count",
                "sensor_count",
                "missing_sensor_count",
                "lmax",
                "lambda_reg",
                "include_l0",
                "mode_count",
            ],
            as_index=False,
        )
        .agg(
            case_count=("sample_id", "count"),
            sample_count=("sample_id", "nunique"),
            mean_correlation=("correlation", "mean"),
            min_correlation=("correlation", "min"),
            mean_nmse=("nmse", "mean"),
            max_nmse=("nmse", "max"),
            mean_main_lobe_error_deg=("main_lobe_error_deg", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
            mean_nearfield_fit_relative_error=("nearfield_fit_relative_error", "mean"),
            max_nearfield_fit_relative_error=("nearfield_fit_relative_error", "max"),
            min_farfield_total_complex_correlation_abs=("farfield_total_complex_correlation_abs", "min"),
            max_farfield_total_complex_relative_l2_error=("farfield_total_complex_relative_l2_error", "max"),
            min_theta_farfield_complex_correlation_abs=("theta_farfield_complex_correlation_abs", "min"),
            min_phi_farfield_complex_correlation_abs=("phi_farfield_complex_correlation_abs", "min"),
            max_theta_farfield_error_to_total_norm=("theta_farfield_error_to_total_norm", "max"),
            max_phi_farfield_error_to_total_norm=("phi_farfield_error_to_total_norm", "max"),
            max_basis_condition=("basis_condition", "max"),
            max_mode_sensor_ratio=("mode_sensor_ratio", "max"),
            any_component_underdetermined=("is_component_underdetermined", "max"),
        )
    )
    by_setting["status"] = by_setting.apply(status_for_row, axis=1)
    by_setting["status_rank"] = by_setting["status"].map(status_rank)
    by_setting = by_setting.sort_values(
        [
            "candidate",
            "status_rank",
            "max_main_lobe_error_deg",
            "max_basis_condition",
            "mode_count",
            "max_nearfield_fit_relative_error",
            "max_nmse",
            "min_correlation",
        ],
        ascending=[True, True, True, True, True, True, True, False],
    )

    best_by_candidate = by_setting.groupby("candidate", sort=False).head(1).copy()
    best_by_candidate = best_by_candidate.sort_values(
        [
            "status_rank",
            "requested_sensor_count",
            "max_main_lobe_error_deg",
            "max_basis_condition",
            "max_nmse",
            "min_correlation",
        ],
        ascending=[True, True, True, True, True, False],
    )

    by_setting.to_csv(out_dir / "spherical_nf_ff_tradeoff_by_setting.csv", index=False, encoding="utf-8-sig")
    best_by_candidate.to_csv(
        out_dir / "spherical_nf_ff_tradeoff_best_by_candidate.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return by_setting, best_by_candidate


def summarize(
    results: pd.DataFrame,
    by_setting: pd.DataFrame,
    best_by_candidate: pd.DataFrame,
    out_dir: Path,
    args: argparse.Namespace,
) -> dict[str, object]:
    reduced = best_by_candidate[best_by_candidate["candidate"] != "full_grid_162"].copy()
    strict_reduced = reduced[reduced["status"] == "strict_pass"].sort_values(
        ["requested_sensor_count", "max_nmse", "max_basis_condition", "min_correlation"],
        ascending=[True, True, True, False],
    )
    sanity_reduced = reduced[reduced["status_rank"] <= PASSING_STATUS_RANK].sort_values(
        ["requested_sensor_count", "status_rank", "max_nmse", "max_basis_condition", "min_correlation"],
        ascending=[True, True, True, True, False],
    )
    overall = best_by_candidate.sort_values(
        [
            "status_rank",
            "requested_sensor_count",
            "max_nmse",
            "max_basis_condition",
            "max_nearfield_fit_relative_error",
            "min_correlation",
        ],
        ascending=[True, True, True, True, True, False],
    ).iloc[0]

    summary = {
        "generated_by": "code/run_spherical_nf_ff_tradeoff.py",
        "nearfield": rel(Path(args.nearfield)),
        "farfield": rel(Path(args.farfield)),
        "layouts": rel(Path(args.layouts)),
        "out_dir": rel(out_dir),
        "basis": "independent scalar spherical-harmonic fit for tangential Etheta/Ephi components",
        "is_full_vector_swe": False,
        "purpose": "Reduced-layout NF-FF/SWE diagnostic for prioritizing CST true near-field monitor reruns.",
        "candidate_count": int(best_by_candidate.shape[0]),
        "case_count": int(results.shape[0]),
        "sample_frequency_pair_count": int(results[["sample_id", "frequency_hz"]].drop_duplicates().shape[0]),
        "lmax_values": [int(value) for value in sorted(results["lmax"].unique())],
        "lambda_regs": [float(value) for value in sorted(results["lambda_reg"].unique())],
        "include_l0": bool(args.include_l0),
        "best_overall_setting": row_record(overall),
        "smallest_strict_reduced_candidate": None if strict_reduced.empty else row_record(strict_reduced.iloc[0]),
        "smallest_sanity_or_better_reduced_candidate": None if sanity_reduced.empty else row_record(sanity_reduced.iloc[0]),
        "boundary": (
            "This is a scalar angular NF-FF diagnostic on the current FarfieldPlot-derived near-field table. "
            "Use it to rank sampling layouts before true CST near-field monitor reruns, not as final vector SWE proof."
        ),
        "files": {
            "raw_results": rel(out_dir / "spherical_nf_ff_tradeoff_results.csv"),
            "by_setting": rel(out_dir / "spherical_nf_ff_tradeoff_by_setting.csv"),
            "best_by_candidate": rel(out_dir / "spherical_nf_ff_tradeoff_best_by_candidate.csv"),
        },
    }
    (out_dir / "spherical_nf_ff_tradeoff_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def write_readme(out_dir: Path, best_by_candidate: pd.DataFrame, summary: dict[str, object]) -> None:
    rows = []
    for row in best_by_candidate.itertuples(index=False):
        rows.append(
            f"| {row.candidate} | {int(row.requested_sensor_count)} | {row.candidate_method} | "
            f"{int(row.lmax)} | {row.lambda_reg:.0e} | {int(row.mode_count)} | {row.status} | "
            f"{row.min_correlation:.4f} | {row.max_nmse:.4e} | {row.max_main_lobe_error_deg:.2f} | "
            f"{row.max_nearfield_fit_relative_error:.4e} | "
            f"{row.min_farfield_total_complex_correlation_abs:.4f} | "
            f"{row.max_farfield_total_complex_relative_l2_error:.4e} | {row.max_basis_condition:.3e} |"
        )

    strict = summary["smallest_strict_reduced_candidate"]
    sanity = summary["smallest_sanity_or_better_reduced_candidate"]
    if strict:
        reading = (
            f"- The smallest strict reduced layout is `{strict['candidate']}` with "
            f"{strict['sensor_count']} sensors, `lmax={strict['lmax']}`, and "
            f"`lambda={strict['lambda_reg']:.0e}`.\n"
            "- Promote this layout, plus one conservative 120-sensor layout, into the next true CST near-field monitor workpack.\n"
            "- Keep the full 162-point grid as the physical reference and report anchor."
        )
    elif sanity:
        reading = (
            f"- No reduced layout reaches the strict gate, but `{sanity['candidate']}` reaches "
            f"`{sanity['status']}` with {sanity['sensor_count']} sensors.\n"
            "- Treat this as a candidate-prioritization result only; do not report it as final reduced-sampling evidence.\n"
            "- Rerun the true near-field monitor export before tightening the sampling claim."
        )
    else:
        best = summary["best_overall_setting"]
        reading = (
            "- Reduced layouts remain diagnostic under this scalar angular NF-FF check.\n"
            f"- The best overall setting is `{best['candidate']}` with status `{best['status']}`.\n"
            "- Focus next on true near-field monitor exports and vector SWE/Huygens model calibration."
        )

    content = f"""# Spherical NF-FF Reduced-Layout Tradeoff

This directory stores a reduced-layout extension of the spherical near-field to
far-field sanity baseline. It fits each candidate sensor subset with scalar
spherical-harmonic expansions for tangential `Etheta` and `Ephi`, then evaluates
the fitted field on the far-field angular grid.

This is not a full vector spherical-wave expansion. Its job is to rank reduced
sampling layouts before spending CST time on true near-field monitor reruns.

## Inputs

| Item | Path |
|---|---|
| Near field | `{summary['nearfield']}` |
| Far field | `{summary['farfield']}` |
| Layout table | `{summary['layouts']}` |

## Best Candidate Per Layout

| Candidate | Sensors | Method | Lmax | Lambda | Modes | Status | Min power Corr | Max power NMSE | Max lobe error / deg | Max NF fit error | Min FF complex Corr | Max FF complex L2 | Max condition |
|---|---:|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

## Reading

{reading}

## Files

| File | Purpose |
|---|---|
| `spherical_nf_ff_tradeoff_results.csv` | Raw case-level results across candidates, samples, `lmax`, and regularization. |
| `spherical_nf_ff_tradeoff_by_setting.csv` | Aggregated setting-level results for each candidate. |
| `spherical_nf_ff_tradeoff_best_by_candidate.csv` | One best setting per candidate layout. |
| `spherical_nf_ff_tradeoff_summary.json` | Machine-readable summary and recommended reduced candidate. |

## Command

```powershell
python code\\run_spherical_nf_ff_tradeoff.py
```

## Boundary

{summary['boundary']}
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run spherical NF-FF diagnostics on reduced sampling layouts.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Near-field CSV/XLSX.")
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD), help="Far-field CSV/XLSX.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory.")
    parser.add_argument("--candidate", action="append", dest="candidates", help="Candidate name to include. Repeatable.")
    parser.add_argument("--lmax", action="append", dest="lmax_values", type=int, help="Maximum spherical harmonic degree. Repeatable.")
    parser.add_argument("--lambda-reg", action="append", dest="lambda_regs", type=float, help="Ridge regularization value. Repeatable.")
    parser.add_argument("--include-l0", action="store_true", help="Include l=0 scalar basis functions.")
    parser.add_argument("--sample-id", action="append", dest="samples", help="Sample id to include. Repeatable.")
    parser.add_argument("--frequency-hz", action="append", dest="frequencies_hz", type=float, help="Frequency to include. Repeatable.")
    args = parser.parse_args()
    args.lmax_values = args.lmax_values or list(DEFAULT_LMAX_VALUES)
    args.lambda_regs = args.lambda_regs or list(DEFAULT_LAMBDAS)
    if any(value < 1 for value in args.lmax_values):
        raise ValueError("lmax values must be >= 1")
    return args


def main() -> int:
    args = parse_args()
    results = run_sweep(args)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(out_dir / "spherical_nf_ff_tradeoff_results.csv", index=False, encoding="utf-8-sig")
    by_setting, best_by_candidate = build_tables(results, out_dir)
    summary = summarize(results, by_setting, best_by_candidate, out_dir, args)
    write_readme(out_dir, best_by_candidate, summary)

    strict = summary["smallest_strict_reduced_candidate"]
    sanity = summary["smallest_sanity_or_better_reduced_candidate"]
    print(f"spherical NF-FF reduced-layout tradeoff written to {out_dir}")
    if strict:
        print(
            "smallest strict reduced layout: "
            f"{strict['candidate']} ({strict['sensor_count']} sensors), "
            f"lmax={strict['lmax']}, lambda={strict['lambda_reg']:.0e}, "
            f"max_nmse={strict['max_nmse']:.4e}"
        )
    elif sanity:
        print(
            "smallest sanity-or-better reduced layout: "
            f"{sanity['candidate']} ({sanity['sensor_count']} sensors), "
            f"status={sanity['status']}, max_nmse={sanity['max_nmse']:.4e}"
        )
    else:
        best = summary["best_overall_setting"]
        print(
            "best diagnostic layout: "
            f"{best['candidate']} ({best['sensor_count']} sensors), "
            f"status={best['status']}, max_nmse={best['max_nmse']:.4e}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
