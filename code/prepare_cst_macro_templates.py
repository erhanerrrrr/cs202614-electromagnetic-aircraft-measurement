from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LEVEL1_CASES = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_LEVEL1_SOURCES = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_LEVEL2_CASES = ROOT / "outputs" / "cst_level2_plan" / "level2_case_manifest.csv"
DEFAULT_LEVEL2_SOURCES = ROOT / "outputs" / "cst_level2_plan" / "level2_source_manifest.csv"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_OUT = ROOT / "outputs" / "cst_macro_templates"


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def priority_rank(priority: str) -> int:
    return {"required": 0, "recommended": 1, "optional": 2}.get(str(priority), 99)


def with_endpoints(df: pd.DataFrame, center_cols: tuple[str, str, str], orient_cols: tuple[str, str, str]) -> pd.DataFrame:
    out = df.copy()
    half_length = out.get("length_m", pd.Series([0.03] * len(out), index=out.index)).astype(float) * 0.5
    for axis, center_col, orient_col in zip("xyz", center_cols, orient_cols):
        center = out[center_col].astype(float)
        orient = out[orient_col].astype(float)
        out[f"start_{axis}_m"] = center - half_length * orient
        out[f"end_{axis}_m"] = center + half_length * orient
    return out


def build_level1_parameters(cases: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    ordered_cases = cases.copy()
    ordered_cases["_manifest_order"] = range(len(ordered_cases))
    source_cols = [
        "sample_id",
        "source_type",
        "source_role",
        "center_x_m",
        "center_y_m",
        "center_z_m",
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "length_m",
        "feed_gap_m",
        "relative_amplitude",
        "relative_phase_deg",
        "boundary_condition",
    ]
    joined = ordered_cases.merge(sources[source_cols], on="sample_id", how="left", suffixes=("", "_source"))
    joined = with_endpoints(joined, ("center_x_m", "center_y_m", "center_z_m"), ("orientation_x", "orientation_y", "orientation_z"))
    joined["_priority_order"] = joined["priority"].astype(str).map(priority_rank)
    order_cols = [
        "sample_id",
        "priority",
        "cst_project",
        "source_type",
        "source_role",
        "orientation_axis",
        "frequency_hz",
        "frequency_label",
        "center_x_m",
        "center_y_m",
        "center_z_m",
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "length_m",
        "feed_gap_m",
        "start_x_m",
        "start_y_m",
        "start_z_m",
        "end_x_m",
        "end_y_m",
        "end_z_m",
        "relative_amplitude",
        "relative_phase_deg",
        "nearfield_monitor",
        "farfield_monitor",
        "nearfield_export",
        "farfield_export",
        "phase_format_nearfield_export",
        "phase_format_farfield_export",
        "expected_nearfield_rows",
        "expected_farfield_rows",
        "boundary_condition",
    ]
    return joined.sort_values(["_priority_order", "_manifest_order"])[order_cols]


def build_level2_samples(cases: pd.DataFrame, sources: pd.DataFrame) -> pd.DataFrame:
    grouped = []
    for sample_id, group in cases.groupby("sample_id", sort=True):
        first = group.iloc[0]
        source_count = int(sources.loc[sources["sample_id"].astype(str).eq(str(sample_id)), "source_index"].nunique())
        frequencies = group["frequency_hz"].astype(int).drop_duplicates().tolist()
        grouped.append(
            {
                "sample_id": sample_id,
                "class_label": first["class_label"],
                "variant_index": int(first["variant_index"]),
                "cst_project": first["cst_project"],
                "carrier_model": first["carrier_model"],
                "working_state": first["working_state"],
                "source_count": source_count,
                "frequency_count": len(frequencies),
                "frequency_hz_list": ";".join(str(freq) for freq in frequencies),
                "frequency_label_list": ";".join(group["frequency_label"].astype(str).drop_duplicates().tolist()),
                "nearfield_export": first["nearfield_export"],
                "farfield_export": first["farfield_export"],
                "expected_nearfield_rows_total": int(first["expected_nearfield_rows_per_frequency"]) * len(frequencies),
                "expected_farfield_rows_total": int(first["expected_farfield_rows_per_frequency"]) * len(frequencies),
            }
        )
    return pd.DataFrame(grouped).sort_values(["class_label", "variant_index", "sample_id"])


def build_level2_sources(sources: pd.DataFrame) -> pd.DataFrame:
    source_df = with_endpoints(
        sources.copy(),
        ("x_m", "y_m", "z_m"),
        ("orientation_x", "orientation_y", "orientation_z"),
    )
    order_cols = [
        "sample_id",
        "class_label",
        "variant_index",
        "source_index",
        "source_role",
        "antenna_model",
        "x_m",
        "y_m",
        "z_m",
        "orientation_x",
        "orientation_y",
        "orientation_z",
        "start_x_m",
        "start_y_m",
        "start_z_m",
        "end_x_m",
        "end_y_m",
        "end_z_m",
        "relative_amplitude",
        "relative_phase_deg",
        "implementation_note",
    ]
    return source_df[order_cols].sort_values(["class_label", "variant_index", "sample_id", "source_index"])


def build_level2_pilot(samples: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for class_label, group in samples.groupby("class_label", sort=True):
        rows.append(group.sort_values("variant_index").iloc[0].to_dict())
    return pd.DataFrame(rows)


def build_checklist(level1_params: pd.DataFrame, level2_pilot: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in level1_params.itertuples(index=False):
        rows.extend(
            [
                {
                    "phase": "G2_Level1_required_first" if item.priority == "required" else "G2_Level1_extra",
                    "sample_id": item.sample_id,
                    "owner": "CST_operator",
                    "action": "Build or update CST project from macro parameter row",
                    "evidence": item.cst_project,
                    "status": "todo",
                },
                {
                    "phase": "G2_Level1_required_first" if item.priority == "required" else "G2_Level1_extra",
                    "sample_id": item.sample_id,
                    "owner": "CST_operator",
                    "action": "Export nearfield and farfield CSV",
                    "evidence": f"{item.nearfield_export}; {item.farfield_export}",
                    "status": "todo",
                },
                {
                    "phase": "G2_Level1_required_first" if item.priority == "required" else "G2_Level1_extra",
                    "sample_id": item.sample_id,
                    "owner": "Algorithm_operator",
                    "action": "Run merge and reconstruction audit",
                    "evidence": f"outputs/cst_reconstruction/{item.sample_id}/cst_reconstruction_metrics.json",
                    "status": "todo",
                },
            ]
        )
    for item in level2_pilot.itertuples(index=False):
        rows.append(
            {
                "phase": "G3_Level2_pilot_one_per_class",
                "sample_id": item.sample_id,
                "owner": "CST_operator",
                "action": "Run one pilot sample for this class before full 48-sample batch",
                "evidence": f"{item.nearfield_export}; {item.farfield_export}",
                "status": "todo",
            }
        )
    return pd.DataFrame(rows)


def write_level1_macro(path: Path) -> None:
    content = """' CST Level 1 standard-source macro template
' Generated from outputs/cst_macro_templates/level1_macro_parameters.csv
' This template fixes the CS-202614 naming contract. CST API calls can vary by version,
' so keep the CSV contract and adapt the CST-specific geometry/export procedures once.

Option Explicit

Const PARAM_CSV = "outputs\\cst_macro_templates\\level1_macro_parameters.csv"
Const SENSOR_CSV = "outputs\\cst_templates\\sensor_layout_hemisphere_for_cst.csv"

Sub Main()
    MsgBox "Use " & PARAM_CSV & " as the authoritative Level 1 case table." & vbCrLf & _
           "Run required rows first: L1_short_dipole_z_1p2G and L1_halfwave_dipole_z_1p2G." & vbCrLf & _
           "Keep all export names exactly as listed."
End Sub

Sub BuildLevel1Case(ByVal sampleId, ByVal freqHz, ByVal startX, ByVal startY, ByVal startZ, _
                   ByVal endX, ByVal endY, ByVal endZ, ByVal nearExport, ByVal farExport)
    ' Suggested CST workflow:
    ' 1. Clear or clone project.
    ' 2. Set units to meters and frequency to Hz/GHz consistently.
    ' 3. Create dipole or discrete port from start/end coordinates.
    ' 4. Set excitation amplitude=1.0 and phase=0 deg unless the CSV says otherwise.
    ' 5. Add 2pi upper-hemisphere near-field point/probe export using SENSOR_CSV.
    ' 6. Add far-field monitor at freqHz.
    ' 7. Solve, export nearExport and farExport, then save CST project.
    AddToHistory "CS202614_Level1_Metadata", "' sample_id=" & sampleId & ", frequency_hz=" & CStr(freqHz)
End Sub
"""
    path.write_text(content, encoding="utf-8")


def write_level2_macro(path: Path) -> None:
    content = """' CST Level 2 multisource macro template
' Generated from outputs/cst_macro_templates/level2_macro_sample_parameters.csv
' and outputs/cst_macro_templates/level2_macro_source_parameters.csv.

Option Explicit

Const SAMPLE_CSV = "outputs\\cst_macro_templates\\level2_macro_sample_parameters.csv"
Const SOURCE_CSV = "outputs\\cst_macro_templates\\level2_macro_source_parameters.csv"
Const SENSOR_CSV = "outputs\\cst_templates\\sensor_layout_hemisphere_for_cst.csv"

Sub Main()
    MsgBox "Run pilot cases in level2_pilot_cases.csv before the full 48-sample Level 2 batch." & vbCrLf & _
           "Each sample keeps one CST project and exports all listed frequencies to the sample-level CSV names."
End Sub

Sub BuildLevel2Sample(ByVal sampleId, ByVal frequencyList, ByVal nearExport, ByVal farExport)
    ' Suggested CST workflow:
    ' 1. Create all sources from SOURCE_CSV rows with matching sample_id.
    ' 2. Preserve relative amplitude and phase from the excitation table.
    ' 3. Add one far-field monitor per frequency in frequencyList.
    ' 4. Export all near-field rows with sample_id, frequency_hz, sensor_id, x/y/z, Ex/Ey/Ez.
    ' 5. Export all far-field rows with sample_id, frequency_hz, theta_deg, phi_deg, Etheta/Ephi or gain.
    AddToHistory "CS202614_Level2_Metadata", "' sample_id=" & sampleId & ", frequencies=" & frequencyList
End Sub
"""
    path.write_text(content, encoding="utf-8")


def write_export_contract(path: Path) -> None:
    content = """' CST export contract template for CS-202614
' Use these columns when configuring or post-processing CST exports.

Option Explicit

' Near-field required columns:
' sample_id, frequency_hz, sensor_id, x_m, y_m, z_m,
' Ex_real, Ex_imag, Ey_real, Ey_imag, Ez_real, Ez_imag
'
' Far-field required columns:
' sample_id, frequency_hz, theta_deg, phi_deg,
' Etheta_real, Etheta_imag, Ephi_real, Ephi_imag
' Optional but useful: gain_db
'
' If CST exports magnitude/phase, keep the filenames ending in _phase.csv and run:
' python code\\normalize_cst_complex_columns.py --phase-unit deg ...
"""
    path.write_text(content, encoding="utf-8")


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    content = f"""# CST macro templates

This folder turns the existing Level 1 and Level 2 manifests into CST macro inputs.
It is an execution aid, not CST simulation evidence.

## Why this exists

The current blocking gate is real CST execution. These files reduce manual copying:

- Level 1 required standard sources can be run first for G2.
- Level 2 pilot samples can be run one per class before launching the full 48-sample batch for G3.
- Export filenames and expected row counts stay synchronized with the Python audit scripts.

## Files

| File | Meaning |
|---|---|
| `level1_macro_parameters.csv` | One row per Level 1 source, including source endpoints, monitors, exports, and expected rows. |
| `level1_required_launch_order.csv` | The two required G2 cases to execute first. |
| `level2_macro_sample_parameters.csv` | One row per Level 2 sample, with frequency list and total expected export rows. |
| `level2_macro_source_parameters.csv` | One row per Level 2 source/feed, including amplitude and phase. |
| `level2_pilot_cases.csv` | One sample per class for a CST pilot run before the full batch. |
| `cst_macro_execution_checklist.csv` | Operator checklist linking each macro/action to evidence files. |
| `cst_level1_standard_source_template.bas` | CST VBA macro skeleton for Level 1. |
| `cst_level2_multisource_template.bas` | CST VBA macro skeleton for Level 2. |
| `cst_export_contract_template.bas` | Required near-field/far-field CSV column contract. |

## Current counts

- Level 1 cases: {summary["level1_case_count"]}
- Level 1 required cases: {summary["level1_required_count"]}
- Level 2 samples: {summary["level2_sample_count"]}
- Level 2 source rows: {summary["level2_source_count"]}
- Sensor points on 2π hemisphere: {summary["sensor_count"]}

## Immediate use

1. Open CST and create or clone the first required project from `level1_required_launch_order.csv`.
2. Import or manually apply the corresponding row in `level1_macro_parameters.csv`.
3. Keep export paths exactly as listed.
4. After exporting, run:

```powershell
python code\\merge_cst_level1_exports.py --strict
python code\\run_cst_level1_batch_reconstruction.py --require-cases
```

After G2 passes, use `level2_pilot_cases.csv` to run one sample per class before the full Level 2 batch.
"""
    (out_dir / "README_cst_macro_templates.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CST macro templates and macro input tables.")
    parser.add_argument("--level1-cases", default=str(DEFAULT_LEVEL1_CASES))
    parser.add_argument("--level1-sources", default=str(DEFAULT_LEVEL1_SOURCES))
    parser.add_argument("--level2-cases", default=str(DEFAULT_LEVEL2_CASES))
    parser.add_argument("--level2-sources", default=str(DEFAULT_LEVEL2_SOURCES))
    parser.add_argument("--sensor-layout", default=str(DEFAULT_SENSOR_LAYOUT))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    level1_cases = read_table(Path(args.level1_cases))
    level1_sources = read_table(Path(args.level1_sources))
    level2_cases = read_table(Path(args.level2_cases))
    level2_sources_raw = read_table(Path(args.level2_sources))
    sensor_count = int(len(read_table(Path(args.sensor_layout))))

    level1_params = build_level1_parameters(level1_cases, level1_sources)
    level1_required = level1_params[level1_params["priority"].astype(str).eq("required")].copy()
    level2_samples = build_level2_samples(level2_cases, level2_sources_raw)
    level2_sources = build_level2_sources(level2_sources_raw)
    level2_pilot = build_level2_pilot(level2_samples)
    checklist = build_checklist(level1_params, level2_pilot)

    level1_params.to_csv(out_dir / "level1_macro_parameters.csv", index=False, encoding="utf-8-sig")
    level1_required.to_csv(out_dir / "level1_required_launch_order.csv", index=False, encoding="utf-8-sig")
    level2_samples.to_csv(out_dir / "level2_macro_sample_parameters.csv", index=False, encoding="utf-8-sig")
    level2_sources.to_csv(out_dir / "level2_macro_source_parameters.csv", index=False, encoding="utf-8-sig")
    level2_pilot.to_csv(out_dir / "level2_pilot_cases.csv", index=False, encoding="utf-8-sig")
    checklist.to_csv(out_dir / "cst_macro_execution_checklist.csv", index=False, encoding="utf-8-sig")

    write_level1_macro(out_dir / "cst_level1_standard_source_template.bas")
    write_level2_macro(out_dir / "cst_level2_multisource_template.bas")
    write_export_contract(out_dir / "cst_export_contract_template.bas")

    summary = {
        "level1_case_count": int(len(level1_params)),
        "level1_required_count": int(len(level1_required)),
        "level1_required_cases": level1_required["sample_id"].astype(str).tolist(),
        "level2_sample_count": int(len(level2_samples)),
        "level2_frequency_task_count": int(len(level2_cases)),
        "level2_source_count": int(len(level2_sources)),
        "level2_pilot_cases": level2_pilot["sample_id"].astype(str).tolist(),
        "sensor_count": sensor_count,
        "selected_measurement_surface": "2pi_upper_hemisphere",
        "source_files": {
            "level1_cases": rel(Path(args.level1_cases)),
            "level1_sources": rel(Path(args.level1_sources)),
            "level2_cases": rel(Path(args.level2_cases)),
            "level2_sources": rel(Path(args.level2_sources)),
            "sensor_layout": rel(Path(args.sensor_layout)),
        },
        "output_dir": rel(out_dir),
        "is_simulation_evidence": False,
    }
    (out_dir / "cst_macro_template_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, summary)

    print(f"CST macro templates written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
