from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_case_manifest.csv"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs" / "cst_level1_plan" / "level1_source_manifest.csv"
DEFAULT_TARGETS = ROOT / "outputs" / "cst_level1_plan" / "level1_validation_targets.csv"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_OUT = ROOT / "outputs" / "cst_level1_workpack"


def read_table(path: Path) -> pd.DataFrame:
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


def source_endpoint_rows(source: pd.Series) -> dict[str, object]:
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


def command_for_case(row: pd.Series) -> str:
    return (
        "python code\\run_cst_reconstruction.py "
        f"--nearfield {row['nearfield_export']} "
        f"--farfield {row['farfield_export']} "
        f"--sample-id {row['sample_id']} "
        f"--frequency-hz {int(row['frequency_hz'])} "
        f"--out-dir outputs\\cst_reconstruction\\{row['sample_id']}"
    )


def write_case_card(out_dir: Path, row: pd.Series, source: pd.Series, target: pd.Series, sensor_count: int) -> None:
    endpoints = source_endpoint_rows(source)
    content = f"""# {row['sample_id']}

Priority: `{row['priority']}`  
Purpose: CST Level 1 standard-source validation case.

## CST Project

| Item | Value |
|---|---|
| CST project | `{row['cst_project']}` |
| Frequency | `{row['frequency_hz']}` Hz (`{row['frequency_label']}`) |
| Boundary | `{source['boundary_condition']}` |
| Solver note | {source['solver_note']} |
| Current measurement surface | 2π upper hemisphere |
| Near-field monitor | `{row['nearfield_monitor']}` |
| Far-field monitor | `{row['farfield_monitor']}` |

## Source Parameters

| Item | Value |
|---|---:|
| Source type | `{row['source_type']}` |
| Orientation axis | `{row['orientation_axis']}` |
| Center x/y/z m | `{source['center_x_m']}`, `{source['center_y_m']}`, `{source['center_z_m']}` |
| Orientation vector | `{source['orientation_x']}`, `{source['orientation_y']}`, `{source['orientation_z']}` |
| Length m | `{source['length_m']}` |
| Feed gap m | `{source['feed_gap_m']}` |
| Relative amplitude | `{source['relative_amplitude']}` |
| Relative phase deg | `{source['relative_phase_deg']}` |
| Start x/y/z m | `{endpoints['start_x_m']}`, `{endpoints['start_y_m']}`, `{endpoints['start_z_m']}` |
| End x/y/z m | `{endpoints['end_x_m']}`, `{endpoints['end_y_m']}`, `{endpoints['end_z_m']}` |

## Export Targets

| Export | Path | Expected rows |
|---|---|---:|
| Near-field real/imag | `{row['nearfield_export']}` | {int(row['expected_nearfield_rows'])} |
| Far-field real/imag | `{row['farfield_export']}` | {int(row['expected_farfield_rows'])} |
| Near-field magnitude/phase fallback | `{row['phase_format_nearfield_export']}` | {int(row['expected_nearfield_rows'])} |
| Far-field magnitude/phase fallback | `{row['phase_format_farfield_export']}` | {int(row['expected_farfield_rows'])} |

Required sensor points: `{sensor_count}` on the selected 2π upper-hemisphere layout.

## Acceptance Targets

| Metric | Threshold |
|---|---:|
| Correlation | >= {float(target['min_correlation'])} |
| Main-lobe error deg | <= {float(target['max_main_lobe_error_deg'])} |
| NMSE | <= {float(target['max_nmse'])} |

## Commands After Export

```powershell
python code\\check_cst_export.py --nearfield {row['nearfield_export']} --farfield {row['farfield_export']} --json-out outputs\\cst_reconstruction\\{row['sample_id']}_validation.json
{command_for_case(row)}
```

If CST exports magnitude/phase instead of real/imag:

```powershell
python code\\normalize_cst_complex_columns.py --nearfield {row['phase_format_nearfield_export']} --farfield {row['phase_format_farfield_export']} --nearfield-out {row['nearfield_export']} --farfield-out {row['farfield_export']} --phase-unit deg
```

## Manual Checks

- `sample_id`, `frequency_hz`, and export filenames match this card exactly.
- Coordinates are in meters, not millimeters.
- Near-field rows include complete `Ex`, `Ey`, `Ez` values for all upper-hemisphere sensor ids.
- Far-field rows include complex `e_theta`/`e_phi` or at least `gain_db`/`power`.
- Screenshots of model, source, boundary, monitors, and export dialog are saved.
"""
    (out_dir / "case_cards" / f"{row['sample_id']}.md").write_text(content, encoding="utf-8")


def build_work_items(cases: pd.DataFrame, sources: pd.DataFrame, targets: pd.DataFrame) -> pd.DataFrame:
    source_by_id = sources.set_index(sources["sample_id"].astype(str))
    target_by_id = targets.set_index(targets["sample_id"].astype(str))
    rows: list[dict[str, object]] = []
    for _, case in cases.iterrows():
        sample_id = str(case["sample_id"])
        source = source_by_id.loc[sample_id]
        target = target_by_id.loc[sample_id]
        endpoints = source_endpoint_rows(source)
        rows.append(
            {
                "priority_order": priority_rank(case["priority"]),
                "sample_id": sample_id,
                "priority": case["priority"],
                "cst_project": case["cst_project"],
                "frequency_hz": int(case["frequency_hz"]),
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
                "nearfield_monitor": case["nearfield_monitor"],
                "farfield_monitor": case["farfield_monitor"],
                "nearfield_export": case["nearfield_export"],
                "farfield_export": case["farfield_export"],
                "expected_nearfield_rows": int(case["expected_nearfield_rows"]),
                "expected_farfield_rows": int(case["expected_farfield_rows"]),
                "min_correlation": target["min_correlation"],
                "max_main_lobe_error_deg": target["max_main_lobe_error_deg"],
                "max_nmse": target["max_nmse"],
                "post_export_command": command_for_case(case),
            }
        )
    return pd.DataFrame(rows).sort_values(["priority_order", "sample_id"]).drop(columns=["priority_order"])


def build_export_checklist(work_items: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in work_items.itertuples(index=False):
        rows.extend(
            [
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "CST project saved",
                    "expected": item.cst_project,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "Near-field CSV exported",
                    "expected": item.nearfield_export,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "Far-field CSV exported",
                    "expected": item.farfield_export,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "Export audit passed",
                    "expected": "merge_cst_level1_exports.py case_complete=True",
                    "owner": "A_algorithm",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "Reconstruction metrics produced",
                    "expected": f"outputs/cst_reconstruction/{item.sample_id}/cst_reconstruction_metrics.json",
                    "owner": "A_algorithm",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "priority": item.priority,
                    "check_item": "Screenshots archived",
                    "expected": f"submission/05_cst/screenshots/level1/{item.sample_id}_*.png",
                    "owner": "C_docs",
                    "status": "todo",
                },
            ]
        )
    return pd.DataFrame(rows)


def write_readme(out_dir: Path, required_count: int, total_count: int, sensor_layout: Path) -> None:
    content = f"""# CST Level 1 workpack

This folder converts the Level 1 manifest into execution assets for the CST owner.

## Files

| File | Use |
|---|---|
| `level1_cst_work_items.csv` | One row per CST case with source endpoints, monitor names, exports, and validation thresholds. |
| `level1_cst_export_checklist.csv` | Per-case checklist for project, export, audit, reconstruction, and screenshots. |
| `case_cards/<sample_id>.md` | Human-readable CST task card for each standard source. |
| `level1_workpack_summary.json` | Counts, required gate, and command hints. |

## Immediate gate

Run the {required_count} required cases first. The full pack contains {total_count} cases.

Current selected measurement surface: 2π upper hemisphere.

Sensor layout source:

```text
{rel(sensor_layout)}
```

After CST exports are placed under `data/cst_exports/level1`, run:

```powershell
python code\\merge_cst_level1_exports.py --strict
python code\\run_cst_level1_batch_reconstruction.py --require-cases
```

If the required cases pass, run the recommended x/y short dipoles before Level 2 whenever schedule allows.
"""
    (out_dir / "README_level1_workpack.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a CST Level 1 standard-source workpack.")
    parser.add_argument("--case-manifest", default=str(DEFAULT_CASE_MANIFEST), help="Path to level1_case_manifest.csv.")
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST), help="Path to level1_source_manifest.csv.")
    parser.add_argument("--targets", default=str(DEFAULT_TARGETS), help="Path to level1_validation_targets.csv.")
    parser.add_argument("--sensor-layout", default=str(DEFAULT_SENSOR_LAYOUT), help="Path to sensor_layout_hemisphere_for_cst.csv.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    (out_dir / "case_cards").mkdir(parents=True, exist_ok=True)

    cases = read_table(Path(args.case_manifest))
    sources = read_table(Path(args.source_manifest))
    targets = read_table(Path(args.targets))
    sensor_layout_path = Path(args.sensor_layout)
    sensor_count = int(len(read_table(sensor_layout_path))) if sensor_layout_path.exists() else 0

    required_cols = {"sample_id", "priority", "frequency_hz", "nearfield_export", "farfield_export"}
    missing = sorted(required_cols - set(cases.columns))
    if missing:
        raise ValueError(f"case manifest missing required columns: {missing}")

    work_items = build_work_items(cases, sources, targets)
    checklist = build_export_checklist(work_items)
    work_items.to_csv(out_dir / "level1_cst_work_items.csv", index=False, encoding="utf-8-sig")
    checklist.to_csv(out_dir / "level1_cst_export_checklist.csv", index=False, encoding="utf-8-sig")

    source_by_id = sources.set_index(sources["sample_id"].astype(str))
    target_by_id = targets.set_index(targets["sample_id"].astype(str))
    for _, row in cases.sort_values(by=["priority"], key=lambda col: col.map(priority_rank)).iterrows():
        sample_id = str(row["sample_id"])
        write_case_card(out_dir, row, source_by_id.loc[sample_id], target_by_id.loc[sample_id], sensor_count)

    priority_counts = cases["priority"].astype(str).value_counts().to_dict()
    summary = {
        "case_manifest": rel(Path(args.case_manifest)),
        "source_manifest": rel(Path(args.source_manifest)),
        "targets": rel(Path(args.targets)),
        "sensor_layout": rel(sensor_layout_path),
        "selected_measurement_surface": "2pi_upper_hemisphere",
        "sensor_count": sensor_count,
        "case_count": int(len(cases)),
        "priority_counts": {str(key): int(value) for key, value in priority_counts.items()},
        "required_cases": cases.loc[cases["priority"].astype(str).eq("required"), "sample_id"].astype(str).tolist(),
        "output_files": {
            "work_items": rel(out_dir / "level1_cst_work_items.csv"),
            "export_checklist": rel(out_dir / "level1_cst_export_checklist.csv"),
            "case_cards": rel(out_dir / "case_cards"),
        },
        "gate_commands": [
            "python code\\merge_cst_level1_exports.py --strict",
            "python code\\run_cst_level1_batch_reconstruction.py --require-cases",
        ],
        "note": "This workpack is a CST execution aid. It is not simulation output.",
    }
    (out_dir / "level1_workpack_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, required_count=int(priority_counts.get("required", 0)), total_count=int(len(cases)), sensor_layout=sensor_layout_path)

    print(f"CST Level 1 workpack written to {out_dir}")
    print(f"cases: {len(cases)}")
    print(f"required cases: {int(priority_counts.get('required', 0))}")


if __name__ == "__main__":
    main()
