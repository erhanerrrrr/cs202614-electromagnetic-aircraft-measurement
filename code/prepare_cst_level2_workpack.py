from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_MANIFEST = ROOT / "outputs" / "cst_level2_plan" / "level2_case_manifest.csv"
DEFAULT_SOURCE_MANIFEST = ROOT / "outputs" / "cst_level2_plan" / "level2_source_manifest.csv"
DEFAULT_LABELS = ROOT / "outputs" / "cst_level2_plan" / "level2_labels.csv"
DEFAULT_SENSOR_LAYOUT = ROOT / "outputs" / "cst_templates" / "sensor_layout_hemisphere_for_cst.csv"
DEFAULT_OUT = ROOT / "outputs" / "cst_level2_workpack"


def read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, encoding="utf-8-sig")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("/", "\\")
    except ValueError:
        return str(path)


def parse_frequency_list(text: object) -> list[int]:
    values: list[int] = []
    for item in str(text).replace(",", ";").split(";"):
        item = item.strip()
        if item:
            values.append(int(float(item)))
    return values


def class_rank(label: str) -> int:
    order = {"comm_pair": 0, "radar_top": 1, "mixed_avionics": 2, "multi_state_on": 3}
    return order.get(str(label), 99)


def summarize_cases(cases: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for sample_id, group in cases.groupby(cases["sample_id"].astype(str), sort=False):
        first = group.iloc[0]
        label_match = labels[labels["sample_id"].astype(str).eq(sample_id)]
        frequencies = sorted(pd.to_numeric(group["frequency_hz"], errors="coerce").dropna().astype(int).unique().tolist())
        nearfield_expected = int(pd.to_numeric(group["expected_nearfield_rows_per_frequency"], errors="coerce").sum())
        farfield_expected = int(pd.to_numeric(group["expected_farfield_rows_per_frequency"], errors="coerce").sum())
        rows.append(
            {
                "class_rank": class_rank(str(first["class_label"])),
                "sample_id": sample_id,
                "class_label": first["class_label"],
                "variant_index": int(first["variant_index"]),
                "carrier_model": first["carrier_model"],
                "working_state": first["working_state"],
                "source_config": label_match["source_config"].iloc[0] if not label_match.empty else first["class_label"],
                "cst_project": first["cst_project"],
                "frequency_count": len(frequencies),
                "frequencies_hz": ";".join(str(freq) for freq in frequencies),
                "frequency_labels": ";".join(str(x) for x in group["frequency_label"].astype(str).tolist()),
                "nearfield_export": first["nearfield_export"],
                "farfield_export": first["farfield_export"],
                "expected_nearfield_rows_total": nearfield_expected,
                "expected_farfield_rows_total": farfield_expected,
                "nearfield_monitors": ";".join(group["nearfield_monitor"].astype(str).tolist()),
                "farfield_monitors": ";".join(group["farfield_monitor"].astype(str).tolist()),
                "post_merge_command": "python code\\merge_cst_level2_exports.py --strict",
                "recognition_command": (
                    "python code\\run_cst_recognition.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv "
                    "--labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2"
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["class_rank", "variant_index"]).drop(columns=["class_rank"])


def build_frequency_tasks(cases: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for row in cases.itertuples(index=False):
        rows.append(
            {
                "sample_id": row.sample_id,
                "class_label": row.class_label,
                "variant_index": int(row.variant_index),
                "frequency_hz": int(row.frequency_hz),
                "frequency_label": row.frequency_label,
                "cst_project": row.cst_project,
                "nearfield_monitor": row.nearfield_monitor,
                "farfield_monitor": row.farfield_monitor,
                "nearfield_export": row.nearfield_export,
                "farfield_export": row.farfield_export,
                "expected_nearfield_rows": int(row.expected_nearfield_rows_per_frequency),
                "expected_farfield_rows": int(row.expected_farfield_rows_per_frequency),
                "status": "todo",
            }
        )
    return pd.DataFrame(rows).sort_values(["class_label", "variant_index", "frequency_hz"])


def build_export_checklist(sample_summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for item in sample_summary.itertuples(index=False):
        rows.extend(
            [
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "CST project saved",
                    "expected": item.cst_project,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "All source excitations set",
                    "expected": "source positions/orientations/amplitudes/phases match source manifest",
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "Hemisphere near-field monitors exported",
                    "expected": item.nearfield_export,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "Far-field monitors exported",
                    "expected": item.farfield_export,
                    "owner": "B_CST",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "Merge audit sample_complete",
                    "expected": "merge_cst_level2_exports.py reports sample_complete=True",
                    "owner": "A_algorithm",
                    "status": "todo",
                },
                {
                    "sample_id": item.sample_id,
                    "class_label": item.class_label,
                    "check_item": "Screenshots archived",
                    "expected": f"submission/05_cst/screenshots/level2/{item.sample_id}_*.png",
                    "owner": "C_docs",
                    "status": "todo",
                },
            ]
        )
    return pd.DataFrame(rows)


def write_case_card(out_dir: Path, sample_row: pd.Series, sources: pd.DataFrame) -> None:
    sample_id = str(sample_row["sample_id"])
    source_table = sources[sources["sample_id"].astype(str).eq(sample_id)].copy()
    source_lines = []
    for src in source_table.sort_values("source_index").itertuples(index=False):
        source_lines.append(
            f"| {int(src.source_index)} | `{src.source_role}` | `{src.antenna_model}` | "
            f"{src.x_m} | {src.y_m} | {src.z_m} | "
            f"{src.orientation_x} | {src.orientation_y} | {src.orientation_z} | "
            f"{src.relative_amplitude} | {src.relative_phase_deg} |"
        )
    source_body = "\n".join(source_lines)

    frequency_rows = []
    freqs = parse_frequency_list(sample_row["frequencies_hz"])
    labels = str(sample_row["frequency_labels"]).split(";")
    near_monitors = str(sample_row["nearfield_monitors"]).split(";")
    far_monitors = str(sample_row["farfield_monitors"]).split(";")
    for idx, freq in enumerate(freqs):
        frequency_rows.append(
            f"| {freq} | `{labels[idx] if idx < len(labels) else ''}` | "
            f"`{near_monitors[idx] if idx < len(near_monitors) else ''}` | "
            f"`{far_monitors[idx] if idx < len(far_monitors) else ''}` |"
        )
    frequency_body = "\n".join(frequency_rows)

    content = f"""# {sample_id}

Class label: `{sample_row['class_label']}`  
Variant index: `{sample_row['variant_index']}`  
Current measurement surface: 2π upper hemisphere.

## CST Project

| Item | Value |
|---|---|
| CST project | `{sample_row['cst_project']}` |
| Carrier model | `{sample_row['carrier_model']}` |
| Working state | `{sample_row['working_state']}` |
| Source config | `{sample_row['source_config']}` |
| Frequency count | {int(sample_row['frequency_count'])} |
| Near-field export | `{sample_row['nearfield_export']}` |
| Far-field export | `{sample_row['farfield_export']}` |
| Expected near-field rows total | {int(sample_row['expected_nearfield_rows_total'])} |
| Expected far-field rows total | {int(sample_row['expected_farfield_rows_total'])} |

## Sources

| idx | role | antenna model | x m | y m | z m | ox | oy | oz | amplitude | phase deg |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
{source_body}

## Frequency Tasks

| frequency Hz | label | near-field monitor | far-field monitor |
|---:|---|---|---|
{frequency_body}

## After Export

```powershell
python code\\merge_cst_level2_exports.py
```

Only after all planned samples are complete:

```powershell
python code\\merge_cst_level2_exports.py --strict
python code\\run_cst_recognition.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2
python code\\run_cst_recognition_ablation.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2_ablation
```

## Manual Checks

- The CST project uses the 2π upper-hemisphere sensor layout.
- Every listed source has matching position, orientation, relative amplitude, and phase.
- Near-field exports include all 5 frequencies in one sample-level CSV.
- Far-field exports include all 5 frequencies in one sample-level CSV.
- `sample_id` and `frequency_hz` are present and match the manifest exactly.
"""
    (out_dir / "case_cards" / f"{sample_id}.md").write_text(content, encoding="utf-8")


def write_class_summary(out_dir: Path, sample_summary: pd.DataFrame, source_manifest: pd.DataFrame) -> None:
    rows: list[dict[str, object]] = []
    for class_label, group in sample_summary.groupby("class_label", sort=False):
        sample_ids = group["sample_id"].astype(str).tolist()
        sources = source_manifest[source_manifest["sample_id"].astype(str).isin(sample_ids)]
        rows.append(
            {
                "class_label": class_label,
                "sample_count": int(len(group)),
                "source_count_min": int(sources.groupby("sample_id").size().min()),
                "source_count_max": int(sources.groupby("sample_id").size().max()),
                "variant_indices": ";".join(str(int(v)) for v in sorted(group["variant_index"].unique())),
                "frequencies_hz": group["frequencies_hz"].iloc[0],
            }
        )
    pd.DataFrame(rows).to_csv(out_dir / "level2_class_summary.csv", index=False, encoding="utf-8-sig")


def write_readme(out_dir: Path, sample_count: int, frequency_rows: int, sensor_layout: Path) -> None:
    content = f"""# CST Level 2 workpack

This folder converts the Level 2 multi-source manifest into CST execution assets.

Current selected measurement surface: 2π upper hemisphere.

Sensor layout source:

```text
{rel(sensor_layout)}
```

## Files

| File | Use |
|---|---|
| `level2_cst_sample_work_items.csv` | One row per CST sample/project. |
| `level2_cst_frequency_tasks.csv` | One row per sample-frequency monitor/export task. |
| `level2_cst_export_checklist.csv` | Project/export/audit/screenshot checklist. |
| `level2_class_summary.csv` | Class-level sample and source summary. |
| `case_cards/<sample_id>.md` | Human-readable CST task card for each sample. |

Planned samples: {sample_count}  
Sample-frequency tasks: {frequency_rows}

## Required Commands After Export

```powershell
python code\\merge_cst_level2_exports.py
python code\\merge_cst_level2_exports.py --strict
python code\\run_cst_recognition.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2
python code\\run_cst_recognition_ablation.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2_ablation
```

Run Level 2 only after Level 1 required cases pass.
"""
    (out_dir / "README_level2_workpack.md").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a CST Level 2 multi-source workpack.")
    parser.add_argument("--case-manifest", default=str(DEFAULT_CASE_MANIFEST), help="Path to level2_case_manifest.csv.")
    parser.add_argument("--source-manifest", default=str(DEFAULT_SOURCE_MANIFEST), help="Path to level2_source_manifest.csv.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="Path to level2_labels.csv.")
    parser.add_argument("--sensor-layout", default=str(DEFAULT_SENSOR_LAYOUT), help="Path to hemisphere sensor layout CSV.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    (out_dir / "case_cards").mkdir(parents=True, exist_ok=True)

    case_manifest = read_table(Path(args.case_manifest))
    source_manifest = read_table(Path(args.source_manifest))
    labels = read_table(Path(args.labels))
    sensor_layout_path = Path(args.sensor_layout)
    sensor_count = int(len(read_table(sensor_layout_path))) if sensor_layout_path.exists() else 0

    sample_summary = summarize_cases(case_manifest, labels)
    frequency_tasks = build_frequency_tasks(case_manifest)
    export_checklist = build_export_checklist(sample_summary)

    sample_summary.to_csv(out_dir / "level2_cst_sample_work_items.csv", index=False, encoding="utf-8-sig")
    frequency_tasks.to_csv(out_dir / "level2_cst_frequency_tasks.csv", index=False, encoding="utf-8-sig")
    export_checklist.to_csv(out_dir / "level2_cst_export_checklist.csv", index=False, encoding="utf-8-sig")
    write_class_summary(out_dir, sample_summary, source_manifest)

    for _, sample_row in sample_summary.iterrows():
        write_case_card(out_dir, sample_row, source_manifest)

    summary = {
        "case_manifest": rel(Path(args.case_manifest)),
        "source_manifest": rel(Path(args.source_manifest)),
        "labels": rel(Path(args.labels)),
        "sensor_layout": rel(sensor_layout_path),
        "selected_measurement_surface": "2pi_upper_hemisphere",
        "sensor_count": sensor_count,
        "sample_count": int(len(sample_summary)),
        "sample_frequency_tasks": int(len(frequency_tasks)),
        "class_count": int(sample_summary["class_label"].nunique()),
        "frequency_count_per_sample": int(sample_summary["frequency_count"].max()),
        "output_files": {
            "sample_work_items": rel(out_dir / "level2_cst_sample_work_items.csv"),
            "frequency_tasks": rel(out_dir / "level2_cst_frequency_tasks.csv"),
            "export_checklist": rel(out_dir / "level2_cst_export_checklist.csv"),
            "class_summary": rel(out_dir / "level2_class_summary.csv"),
            "case_cards": rel(out_dir / "case_cards"),
        },
        "gate_commands": [
            "python code\\merge_cst_level1_exports.py --strict",
            "python code\\merge_cst_level2_exports.py --strict",
            "python code\\run_cst_recognition.py --nearfield data\\cst_exports\\level2\\all_nearfield.csv --labels outputs\\cst_level2_plan\\level2_labels.csv --out-dir outputs\\cst_recognition_level2",
        ],
        "note": "This workpack is a CST execution aid. It is not simulation output.",
    }
    (out_dir / "level2_workpack_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(out_dir, sample_count=len(sample_summary), frequency_rows=len(frequency_tasks), sensor_layout=sensor_layout_path)

    print(f"CST Level 2 workpack written to {out_dir}")
    print(f"samples: {len(sample_summary)}")
    print(f"sample-frequency tasks: {len(frequency_tasks)}")


if __name__ == "__main__":
    main()
