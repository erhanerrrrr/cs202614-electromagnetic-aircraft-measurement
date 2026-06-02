from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_OUT = ROOT / "data" / "cst_true_nearfield_workpack"


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
Const EXPORT_CONTRACT_CSV = "data\\cst_true_nearfield_workpack\\true_nearfield_export_contract.csv"

Sub Main()
    MsgBox "Use " & CASE_CSV & " and " & SENSOR_SHELL_CSV & " as the authoritative true near-field monitor workpack." & vbCrLf & _
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
    AddToHistory "CS202614_TrueNearfield_Metadata", "' sample_id=" & sampleId & ", frequency_hz=" & CStr(freqHz) & ", monitor=" & monitorName
End Sub
"""
    path.write_text(content, encoding="utf-8")


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
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
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    case_manifest = Path(args.case_manifest)
    source_manifest = Path(args.source_manifest)
    sensor_layout_path = Path(args.sensor_layout)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    cases = read_table(case_manifest)
    sources = read_table(source_manifest)
    sensor_layout = read_table(sensor_layout_path)

    sensor_shell = build_sensor_shell(sensor_layout)
    case_table = build_case_table(cases, sources, sensor_count=int(len(sensor_shell)))
    export_contract = build_export_contract()
    checklist = build_checklist(case_table)

    case_table.to_csv(out_dir / "true_nearfield_monitor_cases.csv", index=False, encoding="utf-8-sig")
    sensor_shell.to_csv(out_dir / "true_nearfield_sensor_shell.csv", index=False, encoding="utf-8-sig")
    export_contract.to_csv(out_dir / "true_nearfield_export_contract.csv", index=False, encoding="utf-8-sig")
    checklist.to_csv(out_dir / "true_nearfield_vs_farfieldplot_checklist.csv", index=False, encoding="utf-8-sig")
    write_macro_template(out_dir / "cst_true_nearfield_monitor_template.bas")

    priority_counts = case_table["priority"].astype(str).value_counts().to_dict()
    summary = {
        "purpose": "CST true near-field monitor export workpack for Level 1 validation",
        "source_files": {
            "case_manifest": rel(case_manifest),
            "source_manifest": rel(source_manifest),
            "sensor_layout": rel(sensor_layout_path),
        },
        "output_dir": rel(out_dir),
        "case_count": int(len(case_table)),
        "priority_counts": {str(key): int(value) for key, value in priority_counts.items()},
        "required_cases": case_table.loc[case_table["priority"].astype(str).eq("required"), "sample_id"].astype(str).tolist(),
        "sensor_count": int(len(sensor_shell)),
        "field_components": ["Ex", "Ey", "Ez"],
        "expected_rows_per_case": int(len(sensor_shell) * 3),
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


if __name__ == "__main__":
    main()
