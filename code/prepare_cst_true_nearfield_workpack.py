from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_LAYOUT_CANDIDATES = ROOT / "data" / "sampling_layouts" / "hemisphere_sampling_candidates.csv"
DEFAULT_SPHERICAL_TRADEOFF_BEST = (
    ROOT
    / "data"
    / "sampling_layouts"
    / "spherical_nf_ff_tradeoff"
    / "spherical_nf_ff_tradeoff_best_by_candidate.csv"
)
DEFAULT_OUT = ROOT / "data" / "cst_true_nearfield_workpack"

TRADEOFF_METRIC_COLUMNS = [
    "tradeoff_status",
    "lmax",
    "lambda_reg",
    "mode_count",
    "min_correlation",
    "max_nmse",
    "max_main_lobe_error_deg",
    "max_nearfield_fit_relative_error",
    "max_basis_condition",
]


def read_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing input table: {path}")
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def priority_rank(priority: str) -> int:
    return {"required": 0, "recommended": 1, "optional": 2}.get(str(priority).strip(), 99)


def json_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    normalized = frame.where(pd.notna(frame), None)
    return json.loads(normalized.to_json(orient="records", force_ascii=False))


def blank_metrics() -> dict[str, object]:
    return {column: "" for column in TRADEOFF_METRIC_COLUMNS}


def metrics_from_tradeoff(row: pd.Series) -> dict[str, object]:
    values = blank_metrics()
    values.update(
        {
            "tradeoff_status": row.get("status", ""),
            "lmax": row.get("lmax", ""),
            "lambda_reg": row.get("lambda_reg", ""),
            "mode_count": row.get("mode_count", ""),
            "min_correlation": row.get("min_correlation", ""),
            "max_nmse": row.get("max_nmse", ""),
            "max_main_lobe_error_deg": row.get("max_main_lobe_error_deg", ""),
            "max_nearfield_fit_relative_error": row.get("max_nearfield_fit_relative_error", ""),
            "max_basis_condition": row.get("max_basis_condition", ""),
        }
    )
    return values


def source_endpoint_rows(source: pd.Series) -> dict[str, float]:
    center = [float(source["center_x_m"]), float(source["center_y_m"]), float(source["center_z_m"])]
    orient = [float(source["orientation_x"]), float(source["orientation_y"]), float(source["orientation_z"])]
    half = 0.5 * float(source["length_m"])
    start = [center[idx] - half * orient[idx] for idx in range(3)]
    end = [center[idx] + half * orient[idx] for idx in range(3)]
    return {
        "start_x_m": start[0],
        "start_y_m": start[1],
        "start_z_m": start[2],
        "end_x_m": end[0],
        "end_y_m": end[1],
        "end_z_m": end[2],
    }


def build_sensor_shell(sensor_layout: pd.DataFrame) -> pd.DataFrame:
    required = {
        "sensor_id",
        "x_m",
        "y_m",
        "z_m",
        "theta_deg",
        "phi_deg",
        "radius_m",
        "e_theta_x",
        "e_theta_y",
        "e_theta_z",
        "e_phi_x",
        "e_phi_y",
        "e_phi_z",
    }
    missing = sorted(required - set(sensor_layout.columns))
    if missing:
        raise ValueError(f"sensor layout missing required columns: {missing}")

    shell = sensor_layout.copy()
    shell["sample_surface"] = "upper_hemisphere_2pi"
    shell["intended_monitor_kind"] = "true_nearfield_field_monitor"
    shell["coordinate_unit"] = "m"
    shell["angle_unit"] = "deg"
    shell["field_components_required"] = "Ex;Ey;Ez complex"
    order_cols = [
        "sensor_id",
        "sample_surface",
        "x_m",
        "y_m",
        "z_m",
        "theta_deg",
        "phi_deg",
        "radius_m",
        "e_theta_x",
        "e_theta_y",
        "e_theta_z",
        "e_phi_x",
        "e_phi_y",
        "e_phi_z",
        "intended_monitor_kind",
        "coordinate_unit",
        "angle_unit",
        "field_components_required",
    ]
    return shell[order_cols].sort_values("sensor_id")


def build_case_table(cases: pd.DataFrame, sources: pd.DataFrame, sensor_count: int) -> pd.DataFrame:
    source_by_id = sources.set_index(sources["sample_id"].astype(str))
    rows: list[dict[str, object]] = []
    for manifest_order, (_, case) in enumerate(cases.iterrows()):
        sample_id = str(case["sample_id"])
        if sample_id not in source_by_id.index:
            raise ValueError(f"missing source row for sample_id={sample_id}")
        source = source_by_id.loc[sample_id]
        endpoints = source_endpoint_rows(source)
        frequency_hz = int(case["frequency_hz"])
        freq_mhz = int(round(frequency_hz / 1e6))
        true_export = f"data/cst_exports/level1_true_nearfield/{sample_id}_true_nearfield.csv"
        reference_export = str(case["nearfield_export"])
        rows.append(
            {
                "_manifest_order": manifest_order,
                "sample_id": sample_id,
                "priority": case["priority"],
                "frequency_hz": frequency_hz,
                "frequency_label": case.get("frequency_label", f"{freq_mhz}MHz"),
                "cst_project": case["cst_project"],
                "source_type": case["source_type"],
                "orientation_axis": case["orientation_axis"],
                "center_x_m": source["center_x_m"],
                "center_y_m": source["center_y_m"],
                "center_z_m": source["center_z_m"],
                "orientation_x": source["orientation_x"],
                "orientation_y": source["orientation_y"],
                "orientation_z": source["orientation_z"],
                "length_m": source["length_m"],
                "feed_gap_m": source["feed_gap_m"],
                **endpoints,
                "true_nearfield_monitor": f"true_nf_shell_{freq_mhz}MHz",
                "sample_shell_csv": "data/cst_true_nearfield_workpack/true_nearfield_sensor_shell.csv",
                "true_nearfield_export": true_export,
                "farfieldplot_reference_export": reference_export,
                "farfield_reference_export": case["farfield_export"],
                "expected_sensor_points": sensor_count,
                "expected_export_rows": sensor_count * 3,
                "required_components": "Ex;Ey;Ez",
                "phase_format_allowed": "real_imag preferred; magnitude_phase allowed after normalization",
                "post_export_validation": (
                    "python code\\check_cst_export.py --nearfield "
                    f"{true_export} --farfield {case['farfield_export']}"
                ),
                "post_export_comparison": (
                    "python code\\compare_true_nearfield_exports.py --true-nearfield "
                    f"{true_export} --reference-nearfield {reference_export} "
                    f"--out-dir data\\cst_true_nearfield_workpack\\comparison\\{sample_id}"
                ),
                "comparison_role": "compare_true_nf_monitor_against_farfieldplot_derived_current_baseline",
            }
        )
    out = pd.DataFrame(rows)
    out["_priority_order"] = out["priority"].astype(str).map(priority_rank)
    return out.sort_values(["_priority_order", "_manifest_order"]).drop(columns=["_priority_order", "_manifest_order"])


def build_priority_layouts(layout_candidates: pd.DataFrame, spherical_tradeoff_best: pd.DataFrame) -> pd.DataFrame:
    required = {"candidate", "method", "sensor_count", "selection_order", "sensor_id"}
    missing = sorted(required - set(layout_candidates.columns))
    if missing:
        raise ValueError(f"layout candidates missing required columns: {missing}")

    candidate_meta = (
        layout_candidates.groupby("candidate", as_index=False)
        .agg(candidate_method=("method", "first"), sensor_count=("sensor_id", "count"))
        .sort_values(["sensor_count", "candidate"])
    )
    meta_by_candidate = candidate_meta.set_index("candidate")

    selected: list[dict[str, object]] = []

    def append_candidate(
        candidate: str,
        layout_role: str,
        role_reason: str,
        metrics: dict[str, object] | None = None,
    ) -> None:
        if candidate not in meta_by_candidate.index:
            return
        if any(item["candidate"] == candidate for item in selected):
            return
        meta = meta_by_candidate.loc[candidate]
        selected.append(
            {
                "priority_order": len(selected) + 1,
                "candidate": candidate,
                "layout_role": layout_role,
                "role_reason": role_reason,
                "candidate_method": meta["candidate_method"],
                "sensor_count": int(meta["sensor_count"]),
                **(metrics if metrics is not None else blank_metrics()),
            }
        )

    append_candidate(
        "full_grid_162",
        "full_grid_reference",
        "First true near-field CST export should keep all 162 sensors as the monitor-confirmed reference.",
    )

    if spherical_tradeoff_best.empty:
        append_candidate(
            "geometric_farthest_32",
            "smallest_strict_scalar_nf_ff",
            "Fallback reduced layout named by the current Level 1 plan; rerun only after the full-grid true monitor export.",
        )
        append_candidate(
            "fibonacci_snap_120",
            "conservative_120_crosscheck",
            "Fallback conservative layout for a higher-density reduced-shell check.",
        )
        return pd.DataFrame(selected)

    tradeoff = spherical_tradeoff_best.copy()
    numeric_columns = [
        "sensor_count",
        "max_nmse",
        "max_basis_condition",
        "min_correlation",
        "max_nearfield_fit_relative_error",
    ]
    for column in numeric_columns:
        if column in tradeoff.columns:
            tradeoff[column] = pd.to_numeric(tradeoff[column], errors="coerce")

    tradeoff = tradeoff[tradeoff["candidate"].isin(meta_by_candidate.index)].copy()
    strict = tradeoff[tradeoff["status"].astype(str).eq("strict_pass")].copy()

    reduced = strict[strict["candidate"].astype(str).ne("full_grid_162")].copy()
    if not reduced.empty:
        smallest = reduced.sort_values(
            ["sensor_count", "max_nmse", "max_basis_condition", "candidate"],
            na_position="last",
        ).iloc[0]
        append_candidate(
            str(smallest["candidate"]),
            "smallest_strict_scalar_nf_ff",
            "Smallest strict-pass reduced layout under the scalar spherical NF-FF angular diagnostic.",
            metrics_from_tradeoff(smallest),
        )

    conservative = strict[strict["sensor_count"].eq(120)].copy()
    if conservative.empty:
        conservative = strict[
            strict["sensor_count"].ge(100) & strict["candidate"].astype(str).ne("full_grid_162")
        ].copy()
    if not conservative.empty:
        best_120 = conservative.sort_values(
            ["max_nmse", "max_basis_condition", "sensor_count", "candidate"],
            na_position="last",
        ).iloc[0]
        append_candidate(
            str(best_120["candidate"]),
            "conservative_120_crosscheck",
            "Higher-density strict-pass layout for checking whether the 32-point result survives CST true-monitor data.",
            metrics_from_tradeoff(best_120),
        )

    append_candidate(
        "geometric_farthest_32",
        "smallest_strict_scalar_nf_ff",
        "Fallback reduced layout named by the current Level 1 plan; rerun only after the full-grid true monitor export.",
    )
    append_candidate(
        "fibonacci_snap_120",
        "conservative_120_crosscheck",
        "Fallback conservative layout for a higher-density reduced-shell check.",
    )
    return pd.DataFrame(selected)


def build_priority_sensor_subsets(
    sensor_shell: pd.DataFrame,
    layout_candidates: pd.DataFrame,
    priority_layouts: pd.DataFrame,
) -> pd.DataFrame:
    layout_rows = layout_candidates[
        layout_candidates["candidate"].astype(str).isin(priority_layouts["candidate"].astype(str))
    ][["candidate", "method", "sensor_count", "selection_order", "sensor_id"]].copy()

    subset = layout_rows.merge(
        priority_layouts[
            [
                "priority_order",
                "candidate",
                "layout_role",
                "role_reason",
                "tradeoff_status",
                "lmax",
                "lambda_reg",
                "min_correlation",
                "max_nmse",
                "max_basis_condition",
            ]
        ],
        on="candidate",
        how="left",
    )
    subset = subset.merge(sensor_shell, on="sensor_id", how="left", validate="many_to_one")
    if subset["x_m"].isna().any():
        missing = sorted(subset.loc[subset["x_m"].isna(), "sensor_id"].astype(str).unique())
        raise ValueError(f"priority layout references sensor ids missing from shell: {missing}")

    subset = subset.rename(columns={"method": "candidate_method", "sensor_count": "layout_sensor_count"})
    order_cols = [
        "priority_order",
        "candidate",
        "layout_role",
        "role_reason",
        "candidate_method",
        "layout_sensor_count",
        "selection_order",
        "sensor_id",
        "x_m",
        "y_m",
        "z_m",
        "theta_deg",
        "phi_deg",
        "radius_m",
        "e_theta_x",
        "e_theta_y",
        "e_theta_z",
        "e_phi_x",
        "e_phi_y",
        "e_phi_z",
        "tradeoff_status",
        "lmax",
        "lambda_reg",
        "min_correlation",
        "max_nmse",
        "max_basis_condition",
    ]
    return subset[order_cols].sort_values(["priority_order", "selection_order"])


def build_priority_layout_queue(case_table: pd.DataFrame, priority_layouts: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for case_order, case in enumerate(case_table.itertuples(index=False), start=1):
        for layout in priority_layouts.sort_values("priority_order").itertuples(index=False):
            candidate = str(layout.candidate)
            is_full_grid = candidate == "full_grid_162"
            export_path = (
                case.true_nearfield_export
                if is_full_grid
                else f"data/cst_exports/level1_true_nearfield/{case.sample_id}_{candidate}_true_nearfield.csv"
            )
            comparison_dir = f"data\\cst_true_nearfield_workpack\\comparison\\{case.sample_id}\\{candidate}"
            rows.append(
                {
                    "queue_order": len(rows) + 1,
                    "case_order": case_order,
                    "sample_id": case.sample_id,
                    "case_priority": case.priority,
                    "frequency_hz": case.frequency_hz,
                    "frequency_label": case.frequency_label,
                    "candidate": candidate,
                    "layout_role": layout.layout_role,
                    "candidate_method": layout.candidate_method,
                    "sensor_count": int(layout.sensor_count),
                    "expected_export_rows": int(layout.sensor_count) * 3,
                    "sensor_subset_csv": "data/cst_true_nearfield_workpack/true_nearfield_priority_sensor_subsets.csv",
                    "preferred_export_path": export_path,
                    "full_grid_export_path": case.true_nearfield_export,
                    "farfieldplot_reference_export": case.farfieldplot_reference_export,
                    "can_derive_from_full_grid_export": str(not is_full_grid).lower(),
                    "export_strategy": (
                        "export_full_162_shell_first"
                        if is_full_grid
                        else "derive_from_full_grid_export_or_export_subset_if_CST_time_is_limited"
                    ),
                    "comparison_scope": (
                        "all_162_sensors_against_case_reference"
                        if is_full_grid
                        else "common_sensor_rows_only_missing_candidate_rows_are_expected_against_unfiltered_162_reference"
                    ),
                    "tradeoff_status": layout.tradeoff_status,
                    "lmax": layout.lmax,
                    "lambda_reg": layout.lambda_reg,
                    "mode_count": layout.mode_count,
                    "min_correlation": layout.min_correlation,
                    "max_nmse": layout.max_nmse,
                    "max_main_lobe_error_deg": layout.max_main_lobe_error_deg,
                    "max_nearfield_fit_relative_error": layout.max_nearfield_fit_relative_error,
                    "max_basis_condition": layout.max_basis_condition,
                    "post_export_comparison": (
                        "python code\\compare_true_nearfield_exports.py --true-nearfield "
                        f"{export_path} --reference-nearfield {case.farfieldplot_reference_export} "
                        f"--out-dir {comparison_dir}"
                    ),
                    "role_reason": layout.role_reason,
                }
            )
    return pd.DataFrame(rows)


def build_export_contract() -> pd.DataFrame:
    rows = [
        ("sample_id", "string", "Level 1 case id, identical to the manifest sample_id."),
        ("frequency_hz", "integer", "Solved monitor frequency in Hz."),
        ("sensor_id", "integer", "Sensor id from true_nearfield_sensor_shell.csv."),
        ("x_m", "float", "Probe/interpolation x coordinate in meters."),
        ("y_m", "float", "Probe/interpolation y coordinate in meters."),
        ("z_m", "float", "Probe/interpolation z coordinate in meters."),
        ("theta_deg", "float", "Polar angle of the same coordinate, degrees."),
        ("phi_deg", "float", "Azimuth angle of the same coordinate, degrees."),
        ("radius_m", "float", "Sampling radius in meters."),
        ("polarization", "string", "One of Ex, Ey, Ez. Keep Cartesian fields for audit."),
        ("e_real", "float", "Real part of the complex electric field component."),
        ("e_imag", "float", "Imaginary part of the complex electric field component."),
        ("cst_project", "string", "CST project that produced the row."),
        ("cst_monitor_item", "string", "CST tree item or result path for the true near-field monitor."),
        ("extraction_method", "string", "Use 'CST true near-field monitor interpolated on spherical shell'."),
    ]
    return pd.DataFrame(rows, columns=["column_name", "type", "meaning"])


def build_checklist(case_table: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in case_table.itertuples(index=False):
        phase = "required_true_nf_gate" if item.priority == "required" else "true_nf_extension"
        rows.extend(
            [
                {
                    "phase": phase,
                    "sample_id": item.sample_id,
                    "owner": "CST_operator",
                    "action": "Create or update the Level 1 CST source project.",
                    "evidence": item.cst_project,
                    "status": "todo",
                },
                {
                    "phase": phase,
                    "sample_id": item.sample_id,
                    "owner": "CST_operator",
                    "action": "Add true near-field monitor or field export at the listed frequency.",
                    "evidence": item.true_nearfield_monitor,
                    "status": "todo",
                },
                {
                    "phase": phase,
                    "sample_id": item.sample_id,
                    "owner": "CST_operator",
                    "action": "Interpolate/export Ex/Ey/Ez on the spherical shell coordinates.",
                    "evidence": item.true_nearfield_export,
                    "status": "todo",
                },
                {
                    "phase": phase,
                    "sample_id": item.sample_id,
                    "owner": "Algorithm_operator",
                    "action": "Validate row count, components, units, and paired far-field table.",
                    "evidence": item.post_export_validation,
                    "status": "todo",
                },
                {
                    "phase": phase,
                    "sample_id": item.sample_id,
                    "owner": "Algorithm_operator",
                    "action": "Compare true near-field monitor samples with FarfieldPlot-derived samples.",
                    "evidence": item.farfieldplot_reference_export,
                    "status": "todo",
                },
            ]
        )
    return pd.DataFrame(rows)


def write_macro_template(path: Path) -> None:
    content = """' CST true near-field monitor workpack template for CS-202614
' Generated by code\\prepare_cst_true_nearfield_workpack.py
'
' This is a CST operator skeleton. CST API names differ by version, so keep the
' CSV contract stable and adapt only the CST-specific result-tree calls.

Option Explicit

Const CASE_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_monitor_cases.csv"
Const SENSOR_SHELL_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_sensor_shell.csv"
Const PRIORITY_QUEUE_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_priority_layout_queue.csv"
Const PRIORITY_SUBSETS_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_priority_sensor_subsets.csv"
Const EXPORT_CONTRACT_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_export_contract.csv"

Sub Main()
    MsgBox "Use " & CASE_CSV & " and " & SENSOR_SHELL_CSV & " as the authoritative true near-field monitor workpack." & vbCrLf & _
           "Use " & PRIORITY_QUEUE_CSV & " for full-grid and reduced-layout rerun order." & vbCrLf & _
           "Run required Level 1 z-dipole cases first, then compare against the FarfieldPlot-derived baseline."
End Sub

Sub BuildTrueNearfieldMonitor(ByVal sampleId, ByVal freqHz, ByVal monitorName)
    ' Suggested CST workflow:
    ' 1. Open or clone the Level 1 source project for sampleId.
    ' 2. Ensure units are meters and the solver/export frequency equals freqHz.
    ' 3. Add a true E-field near-field monitor at freqHz.
    ' 4. After solving, sample/interpolate the monitor at SENSOR_SHELL_CSV coordinates.
    ' 5. Export one row per sensor_id and Cartesian component Ex/Ey/Ez.
    ' 6. Keep the export columns listed in EXPORT_CONTRACT_CSV.
    ' 7. Reduced layouts in PRIORITY_SUBSETS_CSV can be derived from the full-grid export.
    AddToHistory "CS202614_TrueNearfield_Metadata", "' sample_id=" & sampleId & ", frequency_hz=" & CStr(freqHz) & ", monitor=" & monitorName
End Sub
"""
    path.write_text(content, encoding="utf-8")


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    layout_lines = "\n".join(
        [
            (
                f"- `{item['candidate']}` ({item['sensor_count']} sensors): "
                f"{item['layout_role']}; {item['role_reason']}"
            )
            for item in summary["priority_layout_candidates"]
        ]
    )
    content = f"""# CST true near-field monitor workpack

This folder is a collaboration package for replacing the current
FarfieldPlot-derived Level 1 angular samples with true CST near-field monitor
samples on the same upper-hemisphere shell.

It is not simulation evidence yet. It defines the CST task, CSV contract, and
comparison checklist that must be executed before stronger NF-FF/SWE claims are
made in the report.

## Files

| File | Purpose |
|---|---|
| `true_nearfield_monitor_cases.csv` | One row per Level 1 case with source coordinates, monitor name, export paths, and validation command. |
| `true_nearfield_sensor_shell.csv` | The 162-point upper-hemisphere shell to sample from the true near-field monitor. |
| `true_nearfield_priority_layout_queue.csv` | Case-by-case CST rerun queue for the full 162-point reference and reduced layouts. |
| `true_nearfield_priority_sensor_subsets.csv` | Sensor subsets for the queued full/reduced layouts. |
| `true_nearfield_export_contract.csv` | Required CSV columns for true near-field exports. |
| `true_nearfield_vs_farfieldplot_checklist.csv` | Operator and algorithm checklist for the comparison run. |
| `cst_true_nearfield_monitor_template.bas` | CST VBA skeleton for building/exporting the monitor. |
| `true_nearfield_workpack_summary.json` | Machine-readable counts and source paths. |

## Immediate gate

Run the required cases first:

```text
{", ".join(summary["required_cases"])}
```

For each case, export `Ex`, `Ey`, and `Ez` as complex values at every sensor in
`true_nearfield_sensor_shell.csv`. The expected row count per case is
`{summary["expected_rows_per_case"]}`.

## Reduced-layout rerun queue

The queue now carries three true-monitor layouts:

{layout_lines}

Use `true_nearfield_priority_layout_queue.csv` as the CST/operator task list.
Run or derive the full-grid `full_grid_162` reference first. The reduced
layouts should be treated as follow-up diagnostics: they can be derived from the
full 162-point export by filtering `true_nearfield_priority_sensor_subsets.csv`,
or exported directly from CST only if solver/export time is tight.

When a reduced-layout export is compared with the existing 162-point
FarfieldPlot-derived reference, `compare_true_nearfield_exports.py` computes
metrics on common sensor rows and reports the omitted full-grid rows as expected
`missing_candidate_rows`.

This is still a queue, not final evidence. The 32-point result came from the
scalar spherical NF-FF angular diagnostic and must be rerun against true CST
near-field monitor data before it is used as a competition claim.

After export, compare the true near-field monitor table against the existing
FarfieldPlot-derived table. The current FarfieldPlot-derived table is useful as
a solver-safe angular baseline, but it should not be described as a full-wave
near-field monitor.

Use this command pattern after each case export:

```powershell
python code\\compare_true_nearfield_exports.py --true-nearfield <true-monitor-csv> --reference-nearfield <farfieldplot-derived-csv> --out-dir data\\cst_true_nearfield_workpack\\comparison\\<sample-id>
```

## Acceptance logic

1. If true-monitor samples match the current baseline closely, keep the current
   reconstruction diagnostics and upgrade the wording from angular sample
   baseline to monitor-confirmed baseline.
2. If they differ in amplitude only, add an amplitude normalization step before
   rerunning source-model and sampling tradeoff scripts.
3. If they differ in phase, polarization, or main-lobe direction, use the true
   monitor export as the authoritative Level 1 baseline and rerun G3 before
   claiming reduced sampling performance.
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a CST true near-field monitor workpack.")
    parser.add_argument("--case-manifest", default=str(DEFAULT_CASE_MANIFEST))
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST))
    parser.add_argument("--sensor-layout", default=str(DEFAULT_SENSOR_LAYOUT))
    parser.add_argument("--layout-candidates", default=str(DEFAULT_LAYOUT_CANDIDATES))
    parser.add_argument("--spherical-tradeoff-best", default=str(DEFAULT_SPHERICAL_TRADEOFF_BEST))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    case_manifest = Path(args.case_manifest)
    source_manifest = Path(args.source_manifest)
    sensor_layout_path = Path(args.sensor_layout)
    layout_candidates_path = Path(args.layout_candidates)
    spherical_tradeoff_best_path = Path(args.spherical_tradeoff_best)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = read_table(case_manifest)
    sources = read_table(source_manifest)
    sensor_layout = read_table(sensor_layout_path)
    layout_candidates = read_table(layout_candidates_path)
    spherical_tradeoff_best = (
        read_table(spherical_tradeoff_best_path)
        if spherical_tradeoff_best_path.exists()
        else pd.DataFrame()
    )

    sensor_shell = build_sensor_shell(sensor_layout)
    case_table = build_case_table(cases, sources, sensor_count=int(len(sensor_shell)))
    priority_layouts = build_priority_layouts(layout_candidates, spherical_tradeoff_best)
    priority_sensor_subsets = build_priority_sensor_subsets(sensor_shell, layout_candidates, priority_layouts)
    priority_layout_queue = build_priority_layout_queue(case_table, priority_layouts)
    export_contract = build_export_contract()
    checklist = build_checklist(case_table)

    case_table.to_csv(out_dir / "true_nearfield_monitor_cases.csv", index=False, encoding="utf-8-sig")
    sensor_shell.to_csv(out_dir / "true_nearfield_sensor_shell.csv", index=False, encoding="utf-8-sig")
    priority_layout_queue.to_csv(
        out_dir / "true_nearfield_priority_layout_queue.csv",
        index=False,
        encoding="utf-8-sig",
    )
    priority_sensor_subsets.to_csv(
        out_dir / "true_nearfield_priority_sensor_subsets.csv",
        index=False,
        encoding="utf-8-sig",
    )
    export_contract.to_csv(out_dir / "true_nearfield_export_contract.csv", index=False, encoding="utf-8-sig")
    checklist.to_csv(out_dir / "true_nearfield_vs_farfieldplot_checklist.csv", index=False, encoding="utf-8-sig")
    write_macro_template(out_dir / "cst_true_nearfield_monitor_template.bas")

    priority_counts = case_table["priority"].astype(str).value_counts().to_dict()
    priority_layout_candidate_records = json_records(
        priority_layouts[
            [
                "priority_order",
                "candidate",
                "layout_role",
                "candidate_method",
                "sensor_count",
                "tradeoff_status",
                "lmax",
                "lambda_reg",
                "min_correlation",
                "max_nmse",
                "max_main_lobe_error_deg",
                "max_nearfield_fit_relative_error",
                "max_basis_condition",
                "role_reason",
            ]
        ]
    )
    summary = {
        "purpose": "CST true near-field monitor export workpack for Level 1 validation",
        "source_files": {
            "case_manifest": rel(case_manifest),
            "source_manifest": rel(source_manifest),
            "sensor_layout": rel(sensor_layout_path),
            "layout_candidates": rel(layout_candidates_path),
            "spherical_tradeoff_best": rel(spherical_tradeoff_best_path),
        },
        "output_dir": rel(out_dir),
        "case_count": int(len(case_table)),
        "priority_counts": {str(key): int(value) for key, value in priority_counts.items()},
        "required_cases": case_table.loc[case_table["priority"].astype(str).eq("required"), "sample_id"].astype(str).tolist(),
        "sensor_count": int(len(sensor_shell)),
        "field_components": ["Ex", "Ey", "Ez"],
        "expected_rows_per_case": int(len(sensor_shell) * 3),
        "priority_layout_count": int(len(priority_layouts)),
        "priority_layout_candidates": priority_layout_candidate_records,
        "priority_layout_queue_rows": int(len(priority_layout_queue)),
        "priority_sensor_subset_rows": int(len(priority_sensor_subsets)),
        "current_baseline_boundary": "Existing Level 1 samples are FarfieldPlot-derived angular samples, not true full-wave near-field monitor exports.",
        "next_algorithm_step": "After true monitor export, rerun Level 1 convention/source-model/sampling diagnostics before reduced-sampling claims.",
        "is_simulation_evidence": False,
    }
    (out_dir / "true_nearfield_workpack_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"CST true near-field monitor workpack written to {out_dir}")
    print(f"cases: {summary['case_count']}")
    print(f"required cases: {', '.join(summary['required_cases'])}")
    print(f"sensor points: {summary['sensor_count']}")
    print(
        "priority layouts: "
        + ", ".join(item["candidate"] for item in summary["priority_layout_candidates"])
    )


if __name__ == "__main__":
    main()
