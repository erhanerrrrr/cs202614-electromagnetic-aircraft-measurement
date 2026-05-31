from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from em_core import pattern_metrics, spherical_basis
from run_cst_recognition import build_feature_matrix, plot_confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEARFIELD = ROOT / "data" / "cst_exports" / "level2" / "all_nearfield.csv"
DEFAULT_FARFIELD = ROOT / "data" / "cst_exports" / "level2" / "all_farfield.csv"
DEFAULT_LABELS = ROOT / "outputs" / "cst_level2_plan" / "level2_labels.csv"
DEFAULT_SOURCES = ROOT / "outputs" / "cst_level2_plan" / "level2_source_manifest.csv"
DEFAULT_OUT = ROOT / "outputs" / "cst_structure_comparison"


def unit_rows(values: np.ndarray) -> np.ndarray:
    return values / np.maximum(np.linalg.norm(values, axis=1, keepdims=True), 1e-15)


def directions_from_angles(theta_deg: np.ndarray, phi_deg: np.ndarray) -> np.ndarray:
    theta = np.deg2rad(theta_deg.astype(float))
    phi = np.deg2rad(phi_deg.astype(float))
    r_hat, _, _ = spherical_basis(theta, phi)
    return r_hat


def ray_box_length(origin: np.ndarray, direction: np.ndarray, center: np.ndarray, half_size: np.ndarray) -> np.ndarray:
    p = origin[None, :] - center[None, :]
    d = direction
    inv = np.full_like(d, np.inf, dtype=float)
    np.divide(1.0, d, out=inv, where=np.abs(d) > 1e-12)
    t1 = (-half_size[None, :] - p) * inv
    t2 = (half_size[None, :] - p) * inv
    tmin = np.maximum.reduce(np.minimum(t1, t2), axis=1)
    tmax = np.minimum.reduce(np.maximum(t1, t2), axis=1)
    length = np.maximum(0.0, tmax - np.maximum(tmin, 0.0))
    valid = tmax > np.maximum(tmin, 0.0)
    return np.where(valid, length, 0.0)


def ray_ellipsoid_length(origin: np.ndarray, direction: np.ndarray, center: np.ndarray, radii: np.ndarray) -> np.ndarray:
    p = (origin[None, :] - center[None, :]) / radii[None, :]
    d = direction / radii[None, :]
    a = np.sum(d * d, axis=1)
    b = 2.0 * np.sum(p * d, axis=1)
    c = np.sum(p * p, axis=1) - 1.0
    disc = b * b - 4.0 * a * c
    length = np.zeros(direction.shape[0], dtype=float)
    valid = disc > 0
    if not np.any(valid):
        return length
    root = np.sqrt(np.maximum(disc[valid], 0.0))
    a_valid = np.maximum(a[valid], 1e-15)
    t0 = (-b[valid] - root) / (2.0 * a_valid)
    t1 = (-b[valid] + root) / (2.0 * a_valid)
    length_valid = np.maximum(0.0, t1 - np.maximum(t0, 0.0))
    length[valid] = np.where(t1 > np.maximum(t0, 0.0), length_valid, 0.0)
    return length


def source_shadow_db(source: pd.Series, directions: np.ndarray, theta_deg: np.ndarray) -> np.ndarray:
    source_pos = np.array([float(source.x_m), float(source.y_m), float(source.z_m)], dtype=float)
    orient = np.array([float(source.orientation_x), float(source.orientation_y), float(source.orientation_z)], dtype=float)
    radial = source_pos - np.array([0.0, 0.0, 4.0], dtype=float)
    normal = orient if np.linalg.norm(orient) > 1e-6 else radial
    if np.linalg.norm(normal) < 1e-6:
        normal = np.array([0.0, 0.0, 1.0], dtype=float)
    normal = normal / np.linalg.norm(normal)

    cos_out = directions @ normal
    backside = np.clip((0.25 - cos_out) / 1.25, 0.0, 1.0) ** 1.35
    role = str(source.source_role)
    base_shadow = 4.0 if "radar" in role else 7.0 if "comm" in role else 9.0
    if float(source.z_m) < 3.0:
        base_shadow += 2.0
    if abs(float(source.y_m)) < 0.8 and abs(float(source.x_m)) < 1.0:
        base_shadow += 4.0

    fuselage = ray_ellipsoid_length(
        source_pos,
        directions,
        center=np.array([0.0, 0.0, 4.0], dtype=float),
        radii=np.array([6.0, 0.85, 0.9], dtype=float),
    )
    wing = ray_box_length(
        source_pos,
        directions,
        center=np.array([0.0, 0.0, 4.0], dtype=float),
        half_size=np.array([2.2, 5.2, 0.16], dtype=float),
    )
    vertical_tail = ray_box_length(
        source_pos,
        directions,
        center=np.array([-5.1, 0.0, 5.6], dtype=float),
        half_size=np.array([0.35, 0.28, 1.8], dtype=float),
    )
    theta_factor = np.clip((theta_deg.astype(float) - 2.0) / 70.0, 0.0, 1.0)
    structure_db = 8.0 * np.tanh(fuselage / 1.3) + 4.5 * np.tanh(wing / 0.28) + 3.5 * np.tanh(vertical_tail / 0.45)
    horizon_extra = 1.5 * theta_factor * np.clip(1.0 - cos_out, 0.0, 2.0)
    return np.clip(base_shadow * backside + structure_db + horizon_extra, 0.0, 22.0)


def sample_shadow_db(
    source_rows: pd.DataFrame,
    sample_id: str,
    directions: np.ndarray,
    theta_deg: np.ndarray,
) -> np.ndarray:
    sample_sources = source_rows[source_rows["sample_id"].astype(str).eq(sample_id)].copy()
    if sample_sources.empty:
        return np.zeros(directions.shape[0], dtype=float)
    weights = pd.to_numeric(sample_sources["relative_amplitude"], errors="coerce").fillna(1.0).to_numpy(dtype=float) ** 2
    weights = weights / np.maximum(np.sum(weights), 1e-15)
    out = np.zeros(directions.shape[0], dtype=float)
    for weight, source in zip(weights, sample_sources.itertuples(index=False)):
        out += weight * source_shadow_db(source, directions, theta_deg)
    return out


def apply_structure_to_farfield(farfield: pd.DataFrame, source_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = farfield.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    metrics: list[dict[str, Any]] = []
    out_groups: list[pd.DataFrame] = []
    for (sample_id, frequency_hz), group in work.groupby(["sample_id", "frequency_hz"], sort=False):
        group = group.copy()
        theta_deg = pd.to_numeric(group["theta_deg"], errors="coerce").to_numpy(dtype=float)
        phi_deg = pd.to_numeric(group["phi_deg"], errors="coerce").to_numpy(dtype=float)
        directions = directions_from_angles(theta_deg, phi_deg)
        shadow_db = sample_shadow_db(source_rows, str(sample_id), directions, theta_deg)
        amp = 10.0 ** (-shadow_db / 20.0)
        baseline_power = pd.to_numeric(group["power"], errors="coerce").to_numpy(dtype=float)

        for real_col, imag_col in [("e_theta_real", "e_theta_imag"), ("e_phi_real", "e_phi_imag")]:
            complex_values = pd.to_numeric(group[real_col], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
                group[imag_col], errors="coerce"
            ).to_numpy(dtype=float)
            complex_values = complex_values * amp
            group[real_col] = np.real(complex_values)
            group[imag_col] = np.imag(complex_values)
        structured_power = (
            group["e_theta_real"].to_numpy(dtype=float) ** 2
            + group["e_theta_imag"].to_numpy(dtype=float) ** 2
            + group["e_phi_real"].to_numpy(dtype=float) ** 2
            + group["e_phi_imag"].to_numpy(dtype=float) ** 2
        )
        group["power"] = structured_power
        group["carrier_model"] = "simplified_airframe_occlusion_surrogate"
        group["extraction_method"] = group["extraction_method"].astype(str) + "; simplified airframe occlusion transfer"
        out_groups.append(group)

        theta = np.deg2rad(theta_deg)
        phi = np.deg2rad(phi_deg)
        metric = pattern_metrics(baseline_power, structured_power, theta, phi)
        delta_db = 10.0 * np.log10(np.maximum(structured_power, 1e-30) / np.maximum(baseline_power, 1e-30))
        metrics.append(
            {
                "sample_id": str(sample_id),
                "frequency_hz": float(frequency_hz),
                "mean_shadow_db": float(np.mean(shadow_db)),
                "p95_shadow_db": float(np.percentile(shadow_db, 95)),
                "max_shadow_db": float(np.max(shadow_db)),
                "mean_abs_delta_db": float(np.mean(np.abs(delta_db))),
                "p95_abs_delta_db": float(np.percentile(np.abs(delta_db), 95)),
                **metric,
            }
        )
    return pd.concat(out_groups, ignore_index=True), pd.DataFrame(metrics)


def apply_structure_to_nearfield(nearfield: pd.DataFrame, source_rows: pd.DataFrame) -> pd.DataFrame:
    work = nearfield.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    out_groups: list[pd.DataFrame] = []
    for (sample_id, frequency_hz), group in work.groupby(["sample_id", "frequency_hz"], sort=False):
        group = group.copy()
        point_rows = group.drop_duplicates("sensor_id").sort_values("sensor_id")
        theta_deg = pd.to_numeric(point_rows["theta_deg"], errors="coerce").to_numpy(dtype=float)
        phi_deg = pd.to_numeric(point_rows["phi_deg"], errors="coerce").to_numpy(dtype=float)
        directions = directions_from_angles(theta_deg, phi_deg)
        shadow_db = sample_shadow_db(source_rows, str(sample_id), directions, theta_deg)
        amp_by_sensor = dict(zip(pd.to_numeric(point_rows["sensor_id"], errors="coerce").astype(int), 10.0 ** (-shadow_db / 20.0)))
        amp = pd.to_numeric(group["sensor_id"], errors="coerce").astype(int).map(amp_by_sensor).to_numpy(dtype=float)
        values = pd.to_numeric(group["e_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
            group["e_imag"], errors="coerce"
        ).to_numpy(dtype=float)
        values = values * amp
        group["e_real"] = np.real(values)
        group["e_imag"] = np.imag(values)
        group["carrier_model"] = "simplified_airframe_occlusion_surrogate"
        group["extraction_method"] = group["extraction_method"].astype(str) + "; simplified airframe occlusion transfer"
        out_groups.append(group)
    return pd.concat(out_groups, ignore_index=True)


def plot_structure_compare(
    baseline: pd.DataFrame,
    structured: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    out_path: Path,
) -> None:
    def sub(df: pd.DataFrame) -> pd.DataFrame:
        mask = df["sample_id"].astype(str).eq(sample_id) & np.isclose(pd.to_numeric(df["frequency_hz"], errors="coerce"), frequency_hz)
        return df.loc[mask].copy()

    base = sub(baseline)
    struct = sub(structured)
    merged = base[["theta_deg", "phi_deg", "power"]].rename(columns={"power": "base_power"}).merge(
        struct[["theta_deg", "phi_deg", "power"]].rename(columns={"power": "struct_power"}),
        on=["theta_deg", "phi_deg"],
        how="inner",
    )
    theta_vals = np.array(sorted(merged["theta_deg"].unique()), dtype=float)
    phi_vals = np.array(sorted(merged["phi_deg"].unique()), dtype=float)
    order = np.lexsort((merged["phi_deg"].to_numpy(dtype=float), merged["theta_deg"].to_numpy(dtype=float)))
    base_power = merged["base_power"].to_numpy(dtype=float)[order]
    struct_power = merged["struct_power"].to_numpy(dtype=float)[order]
    base_db = 10.0 * np.log10(base_power / np.maximum(np.max(base_power), 1e-30) + 1e-12).reshape((len(theta_vals), len(phi_vals)))
    struct_db = 10.0 * np.log10(struct_power / np.maximum(np.max(struct_power), 1e-30) + 1e-12).reshape((len(theta_vals), len(phi_vals)))
    diff = struct_db - base_db
    extent = [float(phi_vals.min()), float(phi_vals.max()), float(theta_vals.min()), float(theta_vals.max())]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), constrained_layout=True)
    for ax, data, title, cmap, vmin, vmax in [
        (axes[0], base_db, "No-airframe baseline / dB", "magma", -35, 0),
        (axes[1], struct_db, "Simplified airframe / dB", "magma", -35, 0),
        (axes[2], diff, "Structure delta / dB", "coolwarm", -12, 4),
    ]:
        im = ax.imshow(data, origin="lower", aspect="auto", extent=extent, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_xlabel("phi / deg")
        ax.set_ylabel("theta / deg")
        ax.set_title(title)
        fig.colorbar(im, ax=ax, shrink=0.82)
    fig.suptitle(f"{sample_id}, {frequency_hz / 1e9:.2f} GHz")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def recognition_domain_shift(
    baseline_nearfield: pd.DataFrame,
    structured_nearfield: pd.DataFrame,
    labels: pd.DataFrame,
    out_dir: Path,
) -> dict[str, Any]:
    x_base, y_base, class_names, sample_ids_base, meta_base = build_feature_matrix(baseline_nearfield, labels)
    x_struct, y_struct, class_names_struct, sample_ids_struct, meta_struct = build_feature_matrix(structured_nearfield, labels)
    if class_names != class_names_struct or sample_ids_base != sample_ids_struct or not np.array_equal(y_base, y_struct):
        raise ValueError("baseline and structured feature matrices are not aligned")

    models = {
        "svm_rbf": make_pipeline(StandardScaler(), SVC(C=8.0, gamma="scale", kernel="rbf", class_weight="balanced")),
        "random_forest": RandomForestClassifier(n_estimators=320, random_state=42, class_weight="balanced_subsample"),
    }
    rows: list[dict[str, Any]] = []
    best_name = ""
    best_acc = -1.0
    best_pred: np.ndarray | None = None
    for name, model in models.items():
        model.fit(x_base, y_base)
        pred = model.predict(x_struct)
        acc = float(accuracy_score(y_struct, pred))
        rows.append({"model": name, "train_domain": "no_airframe", "test_domain": "simplified_airframe", "accuracy": acc})
        if acc > best_acc:
            best_name = name
            best_acc = acc
            best_pred = pred

    if best_pred is None:
        raise RuntimeError("no recognition model was evaluated")
    cm = confusion_matrix(y_struct, best_pred, labels=np.arange(len(class_names)))
    plot_confusion_matrix(cm, class_names, f"cross-domain {best_name}", best_acc, out_dir / "structure_cross_domain_confusion_matrix.png")
    report = classification_report(y_struct, best_pred, target_names=class_names, output_dict=True, zero_division=0)
    pd.DataFrame(rows).to_csv(out_dir / "structure_recognition_domain_shift.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(
        out_dir / "structure_cross_domain_confusion_matrix.csv",
        encoding="utf-8-sig",
    )
    return {
        "baseline_feature_metadata": meta_base,
        "structured_feature_metadata": meta_struct,
        "best_cross_domain_model": best_name,
        "cross_domain_accuracy": best_acc,
        "class_names": class_names,
        "models": rows,
        "classification_report": report,
    }


def write_readme(out_dir: Path, summary: dict[str, Any]) -> None:
    content = f"""# CST Level 2 simplified structure comparison

This folder quantifies the boundary between the current CST-derived element-library Level 2 evidence and a simplified aircraft installation/occlusion model.

It is **not** a full-wave CST aircraft-body solution. It applies a transparent, reproducible fuselage/wing/tail occlusion transfer function to the existing Level 2 nearfield/farfield tables, then measures direction-pattern change and recognition robustness.

## Current Summary

- Samples: {summary["sample_count"]}
- Sample-frequency cases: {summary["sample_frequency_count"]}
- Mean shadow: {summary["mean_shadow_db"]:.3f} dB
- P95 shadow: {summary["p95_shadow_db"]:.3f} dB
- Max shadow: {summary["max_shadow_db"]:.3f} dB
- Cross-domain recognition accuracy: {summary["cross_domain_accuracy"]:.3f}

## Files

| File | Meaning |
|---|---|
| `structure_aware_nearfield.csv` | Level 2 nearfield after simplified airframe occlusion transfer. |
| `structure_aware_farfield.csv` | Level 2 farfield after simplified airframe occlusion transfer. |
| `structure_comparison_metrics.csv` | Per sample/frequency direction-pattern delta metrics. |
| `structure_effect_by_class.csv` | Class-level averaged structure effects. |
| `structure_recognition_metrics.json` | Cross-domain recognition result, trained on no-airframe and tested on simplified-airframe data. |
| `plots/*_structure_compare.png` | Representative no-airframe versus simplified-airframe direction plots. |

## Report Wording

Use this output as a bounded structure comparison: it estimates installation and occlusion sensitivity and demonstrates recognition robustness under a simplified carrier transfer model. The report should still state that full-wave CST airframe scattering is a future enhancement or needs separate execution if time allows.
"""
    (out_dir / "README_cst_structure_comparison.md").write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build simplified airframe structure/occlusion comparison for Level 2 CST-derived data.")
    parser.add_argument("--nearfield", default=str(DEFAULT_NEARFIELD))
    parser.add_argument("--farfield", default=str(DEFAULT_FARFIELD))
    parser.add_argument("--labels", default=str(DEFAULT_LABELS))
    parser.add_argument("--sources", default=str(DEFAULT_SOURCES))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--plot-frequency-hz", type=float, default=1.2e9)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    nearfield = pd.read_csv(args.nearfield, encoding="utf-8-sig")
    farfield = pd.read_csv(args.farfield, encoding="utf-8-sig")
    labels = pd.read_csv(args.labels, encoding="utf-8-sig")
    sources = pd.read_csv(args.sources, encoding="utf-8-sig")

    structured_farfield, metrics = apply_structure_to_farfield(farfield, sources)
    structured_nearfield = apply_structure_to_nearfield(nearfield, sources)

    structured_farfield.to_csv(out_dir / "structure_aware_farfield.csv", index=False, encoding="utf-8-sig")
    structured_nearfield.to_csv(out_dir / "structure_aware_nearfield.csv", index=False, encoding="utf-8-sig")
    metrics.to_csv(out_dir / "structure_comparison_metrics.csv", index=False, encoding="utf-8-sig")

    labels_small = labels[["sample_id", "class_label"]].drop_duplicates("sample_id")
    metrics_with_class = metrics.merge(labels_small, on="sample_id", how="left")
    class_effect = (
        metrics_with_class.groupby("class_label", dropna=False)
        .agg(
            sample_frequency_count=("sample_id", "count"),
            mean_shadow_db=("mean_shadow_db", "mean"),
            p95_shadow_db=("p95_shadow_db", "mean"),
            max_shadow_db=("max_shadow_db", "max"),
            mean_abs_delta_db=("mean_abs_delta_db", "mean"),
            p95_abs_delta_db=("p95_abs_delta_db", "mean"),
            mean_nmse=("nmse", "mean"),
            mean_correlation=("correlation", "mean"),
            max_main_lobe_error_deg=("main_lobe_error_deg", "max"),
        )
        .reset_index()
    )
    class_effect.to_csv(out_dir / "structure_effect_by_class.csv", index=False, encoding="utf-8-sig")

    first_by_class = labels_small.groupby("class_label")["sample_id"].first().tolist()
    for sample_id in first_by_class:
        plot_structure_compare(
            farfield,
            structured_farfield,
            sample_id=sample_id,
            frequency_hz=args.plot_frequency_hz,
            out_path=plots_dir / f"{sample_id}_{int(args.plot_frequency_hz / 1e6)}MHz_structure_compare.png",
        )

    recognition = recognition_domain_shift(nearfield, structured_nearfield, labels, out_dir)
    (out_dir / "structure_recognition_metrics.json").write_text(
        json.dumps(recognition, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "out_dir": str(out_dir.relative_to(ROOT)) if out_dir.is_relative_to(ROOT) else str(out_dir),
        "sample_count": int(metrics["sample_id"].nunique()),
        "sample_frequency_count": int(len(metrics)),
        "mean_shadow_db": float(metrics["mean_shadow_db"].mean()),
        "p95_shadow_db": float(metrics["p95_shadow_db"].mean()),
        "max_shadow_db": float(metrics["max_shadow_db"].max()),
        "mean_abs_delta_db": float(metrics["mean_abs_delta_db"].mean()),
        "p95_abs_delta_db": float(metrics["p95_abs_delta_db"].mean()),
        "mean_pattern_nmse": float(metrics["nmse"].mean()),
        "mean_pattern_correlation": float(metrics["correlation"].mean()),
        "max_main_lobe_error_deg": float(metrics["main_lobe_error_deg"].max()),
        "cross_domain_accuracy": float(recognition["cross_domain_accuracy"]),
        "best_cross_domain_model": recognition["best_cross_domain_model"],
        "is_full_wave_cst_airframe": False,
        "evidence_type": "simplified airframe occlusion transfer on CST-derived Level 2 element-library fields",
        "final_use": "bounded structure/installation sensitivity evidence for G5 report wording",
    }
    (out_dir / "structure_comparison_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, summary)

    print(f"Structure comparison written to {out_dir}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
