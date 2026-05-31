from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from cst_io import read_table, validate_farfield, validate_nearfield, validate_pair


ROOT = Path(__file__).resolve().parents[1]


def first_existing(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    lower_map = {col.lower(): col for col in df.columns}
    for candidate in candidates:
        if candidate.lower() in lower_map:
            return lower_map[candidate.lower()]
    return None


def phase_to_radians(values: pd.Series, column_name: str, phase_unit: str) -> np.ndarray:
    numeric = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    name = column_name.lower()
    if phase_unit == "rad" or (phase_unit == "auto" and "rad" in name):
        return numeric
    return np.deg2rad(numeric)


def complex_from_mag_phase(mag: pd.Series, phase: pd.Series, phase_col: str, phase_unit: str) -> np.ndarray:
    magnitude = pd.to_numeric(mag, errors="coerce").to_numpy(dtype=float)
    phase_rad = phase_to_radians(phase, phase_col, phase_unit)
    return magnitude * np.exp(1j * phase_rad)


def normalize_nearfield(df: pd.DataFrame, phase_unit: str) -> tuple[pd.DataFrame, list[str]]:
    work = df.copy()
    changes: list[str] = []
    if {"e_real", "e_imag"}.issubset(set(work.columns)):
        work["e_real"] = pd.to_numeric(work["e_real"], errors="coerce")
        work["e_imag"] = pd.to_numeric(work["e_imag"], errors="coerce")
        return work, ["nearfield already had e_real/e_imag"]

    mag_col = first_existing(
        work,
        ["e_mag", "e_magnitude", "e_abs", "e_amplitude", "field_mag", "magnitude", "mag", "abs"],
    )
    phase_col = first_existing(
        work,
        ["e_phase_deg", "e_phase_degree", "phase_deg", "phase_degree", "e_phase_rad", "phase_rad", "e_phase", "phase"],
    )
    if not mag_col or not phase_col:
        raise ValueError("nearfield needs e_real/e_imag or magnitude/phase columns such as e_mag/e_phase_deg")

    values = complex_from_mag_phase(work[mag_col], work[phase_col], phase_col, phase_unit)
    work["e_real"] = np.real(values)
    work["e_imag"] = np.imag(values)
    changes.append(f"nearfield converted {mag_col}/{phase_col} -> e_real/e_imag")
    return work, changes


def normalize_farfield_component(work: pd.DataFrame, component: str, phase_unit: str) -> tuple[pd.DataFrame, list[str]]:
    real_col = f"{component}_real"
    imag_col = f"{component}_imag"
    if {real_col, imag_col}.issubset(set(work.columns)):
        work[real_col] = pd.to_numeric(work[real_col], errors="coerce")
        work[imag_col] = pd.to_numeric(work[imag_col], errors="coerce")
        return work, [f"farfield already had {real_col}/{imag_col}"]

    short = component.replace("e_", "")
    mag_col = first_existing(
        work,
        [
            f"{component}_mag",
            f"{component}_magnitude",
            f"{component}_abs",
            f"{short}_mag",
            f"{short}_magnitude",
            f"{short}_abs",
        ],
    )
    phase_col = first_existing(
        work,
        [
            f"{component}_phase_deg",
            f"{component}_phase_degree",
            f"{component}_phase_rad",
            f"{component}_phase",
            f"{short}_phase_deg",
            f"{short}_phase_rad",
            f"{short}_phase",
        ],
    )
    if not mag_col or not phase_col:
        return work, [f"farfield did not include complex or magnitude/phase columns for {component}"]

    values = complex_from_mag_phase(work[mag_col], work[phase_col], phase_col, phase_unit)
    work[real_col] = np.real(values)
    work[imag_col] = np.imag(values)
    return work, [f"farfield converted {mag_col}/{phase_col} -> {real_col}/{imag_col}"]


def normalize_farfield(df: pd.DataFrame, phase_unit: str) -> tuple[pd.DataFrame, list[str]]:
    work = df.copy()
    changes: list[str] = []
    for component in ["e_theta", "e_phi"]:
        work, component_changes = normalize_farfield_component(work, component, phase_unit)
        changes.extend(component_changes)
    return work, changes


def write_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False, encoding="utf-8-sig")


def default_out_path(path: Path, suffix: str = "_normalized") -> Path:
    return path.with_name(f"{path.stem}{suffix}.csv")


def report_payload(report) -> dict[str, object]:
    return {
        "ok": bool(report.ok),
        "errors": report.errors,
        "warnings": report.warnings,
        "summary": report.summary,
    }


def normalize_files(args) -> int:
    reports: dict[str, object] = {"changes": []}
    nearfield = None
    farfield = None

    if args.nearfield:
        nearfield_in = Path(args.nearfield)
        nearfield_out = Path(args.nearfield_out) if args.nearfield_out else default_out_path(nearfield_in)
        nearfield, changes = normalize_nearfield(read_table(nearfield_in), args.phase_unit)
        write_table(nearfield, nearfield_out)
        reports["changes"].extend(changes)
        reports["nearfield_out"] = str(nearfield_out)
        nf_report = validate_nearfield(nearfield)
        reports["nearfield_validation"] = report_payload(nf_report)

    if args.farfield:
        farfield_in = Path(args.farfield)
        farfield_out = Path(args.farfield_out) if args.farfield_out else default_out_path(farfield_in)
        farfield, changes = normalize_farfield(read_table(farfield_in), args.phase_unit)
        write_table(farfield, farfield_out)
        reports["changes"].extend(changes)
        reports["farfield_out"] = str(farfield_out)
        ff_report = validate_farfield(farfield)
        reports["farfield_validation"] = report_payload(ff_report)

    if nearfield is not None and farfield is not None:
        pair_report = validate_pair(nearfield, farfield)
        reports["pair_validation"] = report_payload(pair_report)

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = True
    for key, value in reports.items():
        if key.endswith("_validation") and isinstance(value, dict):
            ok = ok and bool(value.get("ok"))
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def to_phase_nearfield(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    values = pd.to_numeric(work["e_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
        work["e_imag"], errors="coerce"
    ).to_numpy(dtype=float)
    work["e_mag"] = np.abs(values)
    work["e_phase_deg"] = np.rad2deg(np.angle(values))
    return work.drop(columns=["e_real", "e_imag"])


def to_phase_farfield(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for component in ["e_theta", "e_phi"]:
        real_col = f"{component}_real"
        imag_col = f"{component}_imag"
        values = pd.to_numeric(work[real_col], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
            work[imag_col], errors="coerce"
        ).to_numpy(dtype=float)
        work[f"{component}_mag"] = np.abs(values)
        work[f"{component}_phase_deg"] = np.rad2deg(np.angle(values))
        work = work.drop(columns=[real_col, imag_col])
    return work


def make_phase_demo(args) -> int:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    phase_nearfield = to_phase_nearfield(read_table(args.nearfield))
    phase_farfield = to_phase_farfield(read_table(args.farfield))
    phase_nearfield_path = out_dir / "nearfield_phase_input.csv"
    phase_farfield_path = out_dir / "farfield_phase_input.csv"
    normalized_nearfield_path = out_dir / "normalized_nearfield.csv"
    normalized_farfield_path = out_dir / "normalized_farfield.csv"
    report_path = out_dir / "phase_conversion_report.json"

    write_table(phase_nearfield, phase_nearfield_path)
    write_table(phase_farfield, phase_farfield_path)

    demo_args = argparse.Namespace(
        nearfield=str(phase_nearfield_path),
        farfield=str(phase_farfield_path),
        nearfield_out=str(normalized_nearfield_path),
        farfield_out=str(normalized_farfield_path),
        phase_unit="deg",
        json_out=str(report_path),
    )
    result = normalize_files(demo_args)
    print(f"Phase demo written to {out_dir}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize CST complex field exports to real/imag columns.")
    parser.add_argument("--nearfield", help="Near-field CSV/XLSX input.")
    parser.add_argument("--farfield", help="Far-field CSV/XLSX input.")
    parser.add_argument("--nearfield-out", help="Normalized near-field output path.")
    parser.add_argument("--farfield-out", help="Normalized far-field output path.")
    parser.add_argument("--phase-unit", choices=["auto", "deg", "rad"], default="auto", help="Phase unit for generic phase columns.")
    parser.add_argument("--json-out", help="Optional JSON conversion/validation report.")
    parser.add_argument("--make-phase-demo", action="store_true", help="Create a phase-format demo from complex inputs and normalize it back.")
    parser.add_argument("--out-dir", default=str(ROOT / "outputs" / "cst_phase_demo"), help="Demo output directory.")
    args = parser.parse_args()

    if args.make_phase_demo:
        if not args.nearfield or not args.farfield:
            raise ValueError("--make-phase-demo requires --nearfield and --farfield complex demo inputs")
        return make_phase_demo(args)

    if not args.nearfield and not args.farfield:
        raise ValueError("provide --nearfield and/or --farfield")
    return normalize_files(args)


if __name__ == "__main__":
    raise SystemExit(main())
