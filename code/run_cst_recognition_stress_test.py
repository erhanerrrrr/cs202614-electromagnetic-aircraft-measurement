from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from cst_io import read_table, validate_nearfield
from run_cst_recognition import build_feature_matrix, ensure_theta_phi


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEARFIELD = ROOT / "data" / "cst_exports" / "level2" / "all_nearfield.csv"
DEFAULT_LABELS = ROOT / "outputs" / "cst_level2_plan" / "level2_labels.csv"
DEFAULT_LAYOUTS = ROOT / "data" / "sampling_layouts" / "hemisphere_sampling_candidates.csv"
DEFAULT_DECISION_MATRIX = ROOT / "data" / "sampling_layouts" / "sampling_decision_matrix" / "sampling_decision_matrix.csv"
DEFAULT_OUT = ROOT / "data" / "recognition_stress_tests" / "level2_robustness"


DEFAULT_LAYOUT_CANDIDATES = [
    "full_grid_162",
    "geometric_farthest_32",
    "fibonacci_snap_120",
    "task_driven_32",
    "task_driven_48",
]

STRESS_CASES = [
    {
        "stress_case": "clean",
        "noise_snr_db": None,
        "phase_jitter_deg": 0.0,
        "dropout_fraction": 0.0,
        "description": "Clean held-out test set.",
    },
    {
        "stress_case": "noise_20db",
        "noise_snr_db": 20.0,
        "phase_jitter_deg": 0.0,
        "dropout_fraction": 0.0,
        "description": "Complex additive channel noise at 20 dB SNR.",
    },
    {
        "stress_case": "noise_10db",
        "noise_snr_db": 10.0,
        "phase_jitter_deg": 0.0,
        "dropout_fraction": 0.0,
        "description": "Complex additive channel noise at 10 dB SNR.",
    },
    {
        "stress_case": "phase_15deg",
        "noise_snr_db": None,
        "phase_jitter_deg": 15.0,
        "dropout_fraction": 0.0,
        "description": "Independent complex phase jitter with 15 deg standard deviation.",
    },
    {
        "stress_case": "phase_45deg",
        "noise_snr_db": None,
        "phase_jitter_deg": 45.0,
        "dropout_fraction": 0.0,
        "description": "Independent complex phase jitter with 45 deg standard deviation.",
    },
    {
        "stress_case": "dropout_10pct",
        "noise_snr_db": None,
        "phase_jitter_deg": 0.0,
        "dropout_fraction": 0.10,
        "description": "Random theta/phi channel dropout with zero-fill at 10 percent.",
    },
    {
        "stress_case": "dropout_25pct",
        "noise_snr_db": None,
        "phase_jitter_deg": 0.0,
        "dropout_fraction": 0.25,
        "description": "Random theta/phi channel dropout with zero-fill at 25 percent.",
    },
    {
        "stress_case": "noise10_phase15_dropout10",
        "noise_snr_db": 10.0,
        "phase_jitter_deg": 15.0,
        "dropout_fraction": 0.10,
        "description": "Combined 10 dB noise, 15 deg phase jitter, and 10 percent channel dropout.",
    },
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_layout_candidates(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_LAYOUT_CANDIDATES
    candidates = [item.strip() for item in raw.split(",") if item.strip()]
    if not candidates:
        raise ValueError("--layout-candidates was provided but no candidates were parsed")
    return candidates


def load_layouts(path: Path, candidate_names: list[str]) -> dict[str, list[int]]:
    if not path.exists():
        raise FileNotFoundError(path)
    layouts = pd.read_csv(path)
    required = {"candidate", "sensor_id"}
    missing = required - set(layouts.columns)
    if missing:
        raise ValueError(f"layout table missing columns: {sorted(missing)}")

    result: dict[str, list[int]] = {}
    for candidate in candidate_names:
        sub = layouts[layouts["candidate"].astype(str) == candidate].copy()
        if sub.empty:
            raise ValueError(f"candidate {candidate!r} not found in {path}")
        if "selection_order" in sub.columns:
            sub["_order"] = pd.to_numeric(sub["selection_order"], errors="coerce")
            sub = sub.sort_values("_order")
        result[candidate] = pd.to_numeric(sub["sensor_id"], errors="coerce").dropna().astype(int).tolist()
    return result


def load_decision_rows(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    decision = pd.read_csv(path)
    rows: dict[str, dict[str, str]] = {}
    for row in decision.to_dict(orient="records"):
        candidate = str(row.get("candidate", ""))
        if not candidate:
            continue
        rows[candidate] = {
            "recommendation": str(row.get("recommendation", "")),
            "evidence_role": str(row.get("evidence_role", "")),
            "claim_boundary": str(row.get("claim_boundary", "")),
        }
    return rows


def frequencies_from_nearfield(nearfield: pd.DataFrame) -> list[float]:
    frequencies = pd.to_numeric(nearfield["frequency_hz"], errors="coerce").dropna().unique()
    return [float(value) for value in sorted(frequencies)]


def filter_case(nearfield: pd.DataFrame, sensor_ids: list[int], frequencies: list[float]) -> pd.DataFrame:
    work = nearfield.copy()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype(int)
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce").astype(float)
    return work[work["sensor_id"].isin(sensor_ids) & work["frequency_hz"].isin(frequencies)].copy()


def perturb_nearfield(case_nearfield: pd.DataFrame, stress: dict[str, Any], seed: int) -> pd.DataFrame:
    work = case_nearfield.copy()
    rng = np.random.default_rng(seed)
    field = pd.to_numeric(work["e_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
        work["e_imag"],
        errors="coerce",
    ).to_numpy(dtype=float)

    noise_snr_db = stress.get("noise_snr_db")
    if noise_snr_db is not None:
        signal_power = float(np.mean(np.abs(field) ** 2))
        noise_power = signal_power / (10.0 ** (float(noise_snr_db) / 10.0))
        sigma = np.sqrt(max(noise_power, 0.0) / 2.0)
        noise = rng.normal(0.0, sigma, size=field.shape[0]) + 1j * rng.normal(0.0, sigma, size=field.shape[0])
        field = field + noise

    phase_jitter_deg = float(stress.get("phase_jitter_deg") or 0.0)
    if phase_jitter_deg > 0.0:
        phase = rng.normal(0.0, np.deg2rad(phase_jitter_deg), size=field.shape[0])
        field = field * np.exp(1j * phase)

    dropout_fraction = float(stress.get("dropout_fraction") or 0.0)
    if dropout_fraction > 0.0:
        dropout_mask = rng.random(field.shape[0]) < dropout_fraction
        field = field.copy()
        field[dropout_mask] = 0.0 + 0.0j

    work["e_real"] = np.real(field)
    work["e_imag"] = np.imag(field)
    return work


def make_models(seed: int) -> dict[str, object]:
    return {
        "svm_rbf": make_pipeline(StandardScaler(), SVC(C=8.0, gamma="scale", kernel="rbf", class_weight="balanced")),
        "random_forest": RandomForestClassifier(
            n_estimators=260,
            random_state=seed,
            class_weight="balanced_subsample",
        ),
    }


def split_indices(y: np.ndarray, test_size: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    indices = np.arange(len(y))
    _, _, _, _, train_idx, test_idx = train_test_split(
        np.zeros((len(y), 1)),
        y,
        indices,
        test_size=test_size,
        random_state=seed,
        stratify=y,
    )
    return train_idx, test_idx


def evaluate_clean_train_perturbed_test(
    clean_x: np.ndarray,
    perturbed_x: np.ndarray,
    y: np.ndarray,
    class_names: list[str],
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    seed: int,
) -> tuple[dict[str, object], dict[str, object]]:
    models = make_models(seed)
    model_rows: dict[str, object] = {}
    best: dict[str, object] = {"model": "", "accuracy": -1.0, "macro_f1": -1.0}
    for model_name, model in models.items():
        model.fit(clean_x[train_idx], y[train_idx])
        pred = model.predict(perturbed_x[test_idx])
        accuracy = float(accuracy_score(y[test_idx], pred))
        macro_f1 = float(f1_score(y[test_idx], pred, average="macro", zero_division=0))
        model_rows[model_name] = {
            "accuracy": accuracy,
            "macro_f1": macro_f1,
            "classification_report": classification_report(
                y[test_idx],
                pred,
                target_names=class_names,
                output_dict=True,
                zero_division=0,
            ),
        }
        if accuracy > float(best["accuracy"]):
            best = {"model": model_name, "accuracy": accuracy, "macro_f1": macro_f1}
    return best, model_rows


def row_for_result(
    candidate: str,
    decision_rows: dict[str, dict[str, str]],
    stress: dict[str, Any],
    sensor_count: int,
    frequency_count: int,
    feature_count: int,
    sample_count: int,
    train_count: int,
    test_count: int,
    best: dict[str, object],
    models: dict[str, object],
) -> dict[str, object]:
    decision = decision_rows.get(candidate, {})
    svm = models.get("svm_rbf", {})
    forest = models.get("random_forest", {})
    accuracy = float(best["accuracy"])
    return {
        "candidate": candidate,
        "recommendation": decision.get("recommendation", ""),
        "evidence_role": decision.get("evidence_role", ""),
        "stress_case": str(stress["stress_case"]),
        "sensor_count": int(sensor_count),
        "frequency_count": int(frequency_count),
        "noise_snr_db": "" if stress.get("noise_snr_db") is None else float(stress["noise_snr_db"]),
        "phase_jitter_deg": float(stress.get("phase_jitter_deg") or 0.0),
        "dropout_fraction": float(stress.get("dropout_fraction") or 0.0),
        "feature_count": int(feature_count),
        "sample_count": int(sample_count),
        "train_sample_count": int(train_count),
        "test_sample_count": int(test_count),
        "best_model": str(best["model"]),
        "best_accuracy": accuracy,
        "best_macro_f1": float(best["macro_f1"]),
        "svm_accuracy": float(svm.get("accuracy", np.nan)),
        "svm_macro_f1": float(svm.get("macro_f1", np.nan)),
        "random_forest_accuracy": float(forest.get("accuracy", np.nan)),
        "random_forest_macro_f1": float(forest.get("macro_f1", np.nan)),
        "passes_085": bool(accuracy >= 0.85),
        "claim_boundary": decision.get("claim_boundary", ""),
        "stress_description": str(stress["description"]),
    }


def summarize_results(results: pd.DataFrame) -> dict[str, object]:
    layout_rows: list[dict[str, object]] = []
    for candidate, group in results.groupby("candidate", sort=False):
        clean = group[group["stress_case"] == "clean"]
        layout_rows.append(
            {
                "candidate": str(candidate),
                "sensor_count": int(group["sensor_count"].iloc[0]),
                "recommendation": str(group["recommendation"].iloc[0]),
                "clean_accuracy": float(clean["best_accuracy"].iloc[0]) if not clean.empty else None,
                "worst_accuracy": float(group["best_accuracy"].min()),
                "worst_case": str(group.sort_values("best_accuracy", ascending=True).iloc[0]["stress_case"]),
                "all_cases_pass_085": bool((group["best_accuracy"] >= 0.85).all()),
            }
        )
    worst = results.sort_values("best_accuracy", ascending=True).iloc[0]
    return {
        "layout_count": int(results["candidate"].nunique()),
        "stress_case_count": int(results["stress_case"].nunique()),
        "row_count": int(results.shape[0]),
        "all_rows_pass_085": bool((results["best_accuracy"] >= 0.85).all()),
        "worst_case": {
            "candidate": str(worst["candidate"]),
            "stress_case": str(worst["stress_case"]),
            "best_accuracy": float(worst["best_accuracy"]),
            "best_macro_f1": float(worst["best_macro_f1"]),
        },
        "layouts": layout_rows,
    }


def write_readme(out_dir: Path, summary: dict[str, object], rows: list[dict[str, object]], inputs: dict[str, str]) -> None:
    layout_rows = summary["layouts"]
    lines = [
        "# Level 2 Recognition Stress Test",
        "",
        "This directory stores the G5 robustness check for the current Level 2",
        "CST-derived recognition pipeline. Models are trained on clean training",
        "samples and evaluated on clean or perturbed held-out samples.",
        "",
        "## Current Result",
        "",
        f"- Layouts tested: {summary['layout_count']}.",
        f"- Stress cases per layout: {summary['stress_case_count']}.",
        f"- All rows pass accuracy >= 0.85: `{str(summary['all_rows_pass_085']).lower()}`.",
        (
            "- Worst case: "
            f"`{summary['worst_case']['candidate']}` / `{summary['worst_case']['stress_case']}` "
            f"with accuracy `{summary['worst_case']['best_accuracy']:.3f}`."
        ),
        "",
        "## Layout Summary",
        "",
        "| Candidate | Sensors | Recommendation | Clean accuracy | Worst accuracy | Worst case | Passes 0.85 |",
        "|---|---:|---|---:|---:|---|---|",
    ]
    for row in layout_rows:
        clean_acc = row["clean_accuracy"]
        lines.append(
            "| {candidate} | {sensor_count} | {recommendation} | {clean} | {worst:.3f} | {worst_case} | {passes} |".format(
                candidate=row["candidate"],
                sensor_count=row["sensor_count"],
                recommendation=row["recommendation"],
                clean="n/a" if clean_acc is None else f"{clean_acc:.3f}",
                worst=float(row["worst_accuracy"]),
                worst_case=row["worst_case"],
                passes=str(row["all_cases_pass_085"]).lower(),
            )
        )

    failing_rows = sorted(
        [row for row in rows if not bool(row["passes_085"])],
        key=lambda row: float(row["best_accuracy"]),
    )
    lines.extend(["", "## Rows Below 0.85", ""])
    if failing_rows:
        lines.extend(
            [
                "| Candidate | Stress case | Accuracy | Macro-F1 | Best model |",
                "|---|---|---:|---:|---|",
            ]
        )
        for row in failing_rows:
            lines.append(
                "| {candidate} | {stress_case} | {accuracy:.3f} | {macro_f1:.3f} | {best_model} |".format(
                    candidate=row["candidate"],
                    stress_case=row["stress_case"],
                    accuracy=float(row["best_accuracy"]),
                    macro_f1=float(row["best_macro_f1"]),
                    best_model=row["best_model"],
                )
            )
    else:
        lines.append("No tested row falls below the `0.85` threshold.")

    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Purpose |",
            "|---|---|",
            "| `recognition_stress_metrics.csv` | Per-layout/per-stress accuracy and macro-F1 for clean-trained models. |",
            "| `recognition_stress_summary.json` | Machine-readable summary, inputs, and layout-level worst cases. |",
            "| `README.md` | Human-facing interpretation and claim boundary. |",
            "",
            "## Regenerate",
            "",
            "```powershell",
            "python code\\run_cst_recognition_stress_test.py",
            "```",
            "",
            "## Boundary",
            "",
            "This is a Level 2 CST-derived element-library robustness check. It",
            "strengthens the recognition/generalization evidence, but it is not a",
            "full-wave complex-airframe scattering validation and does not replace the",
            "true CST near-field monitor gate used for reduced-layout reconstruction",
            "claims.",
            "",
            "## Inputs",
            "",
        ]
    )
    for name, path in inputs.items():
        lines.append(f"- {name}: `{path}`")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run clean-train/perturbed-test robustness checks for CST Level 2 recognition.",
    )
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD), help="Path to Level 2 near-field CSV/XLSX.")
    parser.add_argument("--labels", default=str(DEFAULT_LABELS), help="CSV/XLSX with sample_id and class_label.")
    parser.add_argument("--layouts", default=str(DEFAULT_LAYOUTS), help="Candidate layout table.")
    parser.add_argument("--decision-matrix", default=str(DEFAULT_DECISION_MATRIX), help="Sampling decision matrix CSV.")
    parser.add_argument("--layout-candidates", default="", help="Comma-separated candidate list. Defaults to the G2 decision set.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), help="Output directory.")
    parser.add_argument("--test-size", type=float, default=0.30, help="Stratified held-out test split size.")
    parser.add_argument("--seed", type=int, default=202614, help="Random seed.")
    args = parser.parse_args()

    nearfield_path = Path(args.nearfield)
    labels_path = Path(args.labels)
    layouts_path = Path(args.layouts)
    decision_path = Path(args.decision_matrix)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_names = parse_layout_candidates(args.layout_candidates)
    layout_ids = load_layouts(layouts_path, candidate_names)
    decision_rows = load_decision_rows(decision_path)

    raw_nearfield = read_table(nearfield_path)
    labels = read_table(labels_path)
    nf_report = validate_nearfield(raw_nearfield)
    if not nf_report.ok:
        raise ValueError(f"nearfield validation failed: {nf_report.errors}")

    nearfield = ensure_theta_phi(raw_nearfield)
    frequencies = frequencies_from_nearfield(nearfield)

    rows: list[dict[str, object]] = []
    details: dict[str, object] = {}
    for layout_index, candidate in enumerate(candidate_names):
        sensor_ids = layout_ids[candidate]
        clean_case = filter_case(nearfield, sensor_ids, frequencies)
        clean_x, y, class_names, sample_ids, clean_metadata = build_feature_matrix(clean_case, labels)
        train_idx, test_idx = split_indices(y, args.test_size, args.seed)

        details[candidate] = {
            "class_names": class_names,
            "sample_ids": sample_ids,
            "feature_metadata": clean_metadata,
            "stress_cases": {},
        }

        for stress_index, stress in enumerate(STRESS_CASES):
            stress_seed = args.seed + layout_index * 1000 + stress_index * 37
            perturbed = perturb_nearfield(clean_case, stress, stress_seed)
            perturbed_x, y_perturbed, _, perturbed_sample_ids, perturbed_metadata = build_feature_matrix(perturbed, labels)
            if sample_ids != perturbed_sample_ids or not np.array_equal(y, y_perturbed):
                raise ValueError(f"sample order changed after perturbation for {candidate}/{stress['stress_case']}")
            best, models = evaluate_clean_train_perturbed_test(
                clean_x=clean_x,
                perturbed_x=perturbed_x,
                y=y,
                class_names=class_names,
                train_idx=train_idx,
                test_idx=test_idx,
                seed=args.seed,
            )
            row = row_for_result(
                candidate=candidate,
                decision_rows=decision_rows,
                stress=stress,
                sensor_count=len(sensor_ids),
                frequency_count=len(frequencies),
                feature_count=int(perturbed_metadata["feature_count"]),
                sample_count=int(perturbed_metadata["sample_count"]),
                train_count=len(train_idx),
                test_count=len(test_idx),
                best=best,
                models=models,
            )
            rows.append(row)
            details[candidate]["stress_cases"][str(stress["stress_case"])] = {
                "best": best,
                "models": models,
                "feature_metadata": perturbed_metadata,
            }
            print(
                f"{candidate}/{stress['stress_case']}: "
                f"accuracy={float(best['accuracy']):.3f}, macro_f1={float(best['macro_f1']):.3f}"
            )

    results = pd.DataFrame(rows)
    results.to_csv(out_dir / "recognition_stress_metrics.csv", index=False, encoding="utf-8-sig")

    summary = summarize_results(results)
    inputs = {
        "nearfield": rel(nearfield_path),
        "labels": rel(labels_path),
        "layouts": rel(layouts_path),
        "decision_matrix": rel(decision_path),
    }
    payload = {
        "generated_by": "code/run_cst_recognition_stress_test.py",
        "purpose": "G5 clean-train/perturbed-test recognition robustness check for selected G2 layouts.",
        "inputs": inputs,
        "nearfield_validation": {
            "ok": nf_report.ok,
            "warnings": nf_report.warnings,
            "summary": nf_report.summary,
        },
        "stress_cases": STRESS_CASES,
        "summary": summary,
        "details": details,
        "boundary": (
            "Level 2 CST-derived element-library robustness evidence only. "
            "It does not replace true-monitor reconstruction gates or full-wave complex-airframe validation."
        ),
    }
    (out_dir / "recognition_stress_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary, rows, inputs)
    print(f"recognition stress test complete: {rel(out_dir)}")


if __name__ == "__main__":
    main()
