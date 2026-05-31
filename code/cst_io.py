from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from em_core import SensorLayout, spherical_basis


NEARFIELD_REQUIRED = {
    "sample_id",
    "sensor_id",
    "x_m",
    "y_m",
    "z_m",
    "frequency_hz",
    "polarization",
    "e_real",
    "e_imag",
}

FARFIELD_REQUIRED = {
    "sample_id",
    "theta_deg",
    "phi_deg",
    "frequency_hz",
}

FARFIELD_COMPLEX_REQUIRED = {
    "e_theta_real",
    "e_theta_imag",
    "e_phi_real",
    "e_phi_imag",
}


@dataclass
class ValidationReport:
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: dict[str, object] = field(default_factory=dict)

    def add_error(self, message: str) -> None:
        self.ok = False
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def merge(self, other: "ValidationReport") -> "ValidationReport":
        self.ok = self.ok and other.ok
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.summary.update(other.summary)
        return self


def read_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    return pd.read_csv(path, encoding="utf-8-sig")


def _check_required(df: pd.DataFrame, required: set[str], report: ValidationReport, table_name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        report.add_error(f"{table_name} missing required columns: {', '.join(missing)}")


def _check_numeric(df: pd.DataFrame, cols: list[str], report: ValidationReport, table_name: str) -> None:
    for col in cols:
        if col not in df.columns:
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        bad_count = int(converted.isna().sum())
        if bad_count:
            report.add_error(f"{table_name}.{col} has {bad_count} non-numeric or empty values")


def validate_nearfield(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport()
    _check_required(df, NEARFIELD_REQUIRED, report, "nearfield")
    if not report.ok:
        return report

    numeric_cols = ["sensor_id", "x_m", "y_m", "z_m", "frequency_hz", "e_real", "e_imag"]
    _check_numeric(df, numeric_cols, report, "nearfield")
    if not report.ok:
        return report

    work = df.copy()
    work["sensor_id"] = pd.to_numeric(work["sensor_id"], errors="coerce").astype("Int64")
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    work["polarization"] = work["polarization"].astype(str).str.strip()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()

    duplicate_cols = ["sample_id", "frequency_hz", "sensor_id", "polarization"]
    duplicate_count = int(work.duplicated(duplicate_cols).sum())
    if duplicate_count:
        report.add_error(f"nearfield has {duplicate_count} duplicated sample/frequency/sensor/polarization rows")

    sensor_coord_spread = (
        work.groupby("sensor_id")[["x_m", "y_m", "z_m"]]
        .nunique(dropna=False)
        .max(axis=1)
    )
    inconsistent = sensor_coord_spread[sensor_coord_spread > 1]
    if len(inconsistent):
        report.add_error(f"{len(inconsistent)} sensor_id values have inconsistent coordinates")

    pols = sorted(work["polarization"].unique().tolist())
    samples = sorted(work["sample_id"].unique().tolist())
    frequencies = sorted(float(x) for x in work["frequency_hz"].unique())
    sensors = sorted(int(x) for x in work["sensor_id"].dropna().unique())

    pol_set = set(pols)
    has_theta_phi = {"theta", "phi"}.issubset(pol_set)
    has_cartesian = {"Ex", "Ey", "Ez"}.issubset(pol_set) or {"ex", "ey", "ez"}.issubset({p.lower() for p in pol_set})
    if not has_theta_phi and not has_cartesian:
        report.add_warning("nearfield is not directly reconstruction-ready: provide theta/phi or complete Ex/Ey/Ez fields")
    if has_cartesian and not has_theta_phi:
        report.add_warning("nearfield uses Ex/Ey/Ez; Python can convert to theta/phi if coordinates are correct")

    expected_rows_per_sample_frequency = len(sensors) * len(pols)
    counts = work.groupby(["sample_id", "frequency_hz"]).size()
    incomplete = counts[counts != expected_rows_per_sample_frequency]
    if len(incomplete):
        report.add_warning(f"{len(incomplete)} sample/frequency groups have incomplete polarization or sensor coverage")

    radius = np.sqrt(work[["x_m", "y_m", "z_m"]].astype(float).pow(2).sum(axis=1))
    report.summary.update(
        {
            "nearfield_rows": int(len(work)),
            "sample_count": int(len(samples)),
            "samples": samples[:10],
            "frequency_count": int(len(frequencies)),
            "frequencies_hz": frequencies[:10],
            "sensor_count": int(len(sensors)),
            "polarizations": pols,
            "radius_min_m": float(radius.min()),
            "radius_max_m": float(radius.max()),
            "reconstruction_ready": bool(has_theta_phi or has_cartesian),
        }
    )
    return report


def validate_farfield(df: pd.DataFrame) -> ValidationReport:
    report = ValidationReport()
    _check_required(df, FARFIELD_REQUIRED, report, "farfield")
    if not report.ok:
        return report

    has_complex = FARFIELD_COMPLEX_REQUIRED.issubset(set(df.columns))
    has_gain = "gain_db" in df.columns or "power" in df.columns
    if not has_complex and not has_gain:
        report.add_error("farfield must include Etheta/Ephi complex columns or gain_db/power")

    numeric_cols = ["theta_deg", "phi_deg", "frequency_hz"]
    if has_complex:
        numeric_cols.extend(sorted(FARFIELD_COMPLEX_REQUIRED))
    if "gain_db" in df.columns:
        numeric_cols.append("gain_db")
    if "power" in df.columns:
        numeric_cols.append("power")
    _check_numeric(df, numeric_cols, report, "farfield")
    if not report.ok:
        return report

    work = df.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    samples = sorted(work["sample_id"].unique().tolist())
    frequencies = sorted(float(x) for x in work["frequency_hz"].unique())
    duplicate_cols = ["sample_id", "frequency_hz", "theta_deg", "phi_deg"]
    duplicate_count = int(work.duplicated(duplicate_cols).sum())
    if duplicate_count:
        report.add_error(f"farfield has {duplicate_count} duplicated sample/frequency/theta/phi rows")

    report.summary.update(
        {
            "farfield_rows": int(len(work)),
            "farfield_sample_count": int(len(samples)),
            "farfield_samples": samples[:10],
            "farfield_frequency_count": int(len(frequencies)),
            "farfield_frequencies_hz": frequencies[:10],
            "has_complex_farfield": bool(has_complex),
            "has_gain_or_power": bool(has_gain),
        }
    )
    return report


def validate_pair(nearfield: pd.DataFrame, farfield: pd.DataFrame) -> ValidationReport:
    report = ValidationReport()
    nf_samples = set(nearfield["sample_id"].astype(str).str.strip())
    ff_samples = set(farfield["sample_id"].astype(str).str.strip())
    missing_ff = sorted(nf_samples - ff_samples)
    missing_nf = sorted(ff_samples - nf_samples)
    if missing_ff:
        report.add_error(f"farfield missing sample_id values present in nearfield: {missing_ff[:5]}")
    if missing_nf:
        report.add_warning(f"farfield has extra sample_id values not present in nearfield: {missing_nf[:5]}")

    nf_freq = set(pd.to_numeric(nearfield["frequency_hz"], errors="coerce").dropna().astype(float))
    ff_freq = set(pd.to_numeric(farfield["frequency_hz"], errors="coerce").dropna().astype(float))
    missing_ff_freq = sorted(nf_freq - ff_freq)
    if missing_ff_freq:
        report.add_error(f"farfield missing frequencies present in nearfield: {missing_ff_freq[:5]}")
    report.summary["pair_checked"] = True
    return report


def cartesian_to_theta_phi_rows(df: pd.DataFrame) -> pd.DataFrame:
    required = NEARFIELD_REQUIRED
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"missing required nearfield columns: {missing}")

    work = df.copy()
    work["polarization_norm"] = work["polarization"].astype(str).str.lower()
    pivot_index = [
        "sample_id",
        "sensor_id",
        "x_m",
        "y_m",
        "z_m",
        "frequency_hz",
        "source_config",
        "carrier_model",
        "working_state",
    ]
    for col in pivot_index:
        if col not in work.columns:
            work[col] = ""

    work["e_complex"] = pd.to_numeric(work["e_real"], errors="coerce") + 1j * pd.to_numeric(work["e_imag"], errors="coerce")
    dedup = work.drop_duplicates(pivot_index + ["polarization_norm"], keep="first")
    pivot = dedup.pivot(index=pivot_index, columns="polarization_norm", values="e_complex").reset_index()
    if not {"ex", "ey", "ez"}.issubset(set(pivot.columns)):
        raise ValueError("Ex/Ey/Ez rows are required for Cartesian to theta/phi conversion")

    positions = pivot[["x_m", "y_m", "z_m"]].astype(float).to_numpy()
    radius = np.linalg.norm(positions, axis=1)
    theta = np.arccos(np.clip(positions[:, 2] / np.maximum(radius, 1e-15), -1.0, 1.0))
    phi = np.mod(np.arctan2(positions[:, 1], positions[:, 0]), 2.0 * np.pi)
    _, e_theta, e_phi = spherical_basis(theta, phi)
    e_cart = np.column_stack([pivot["ex"].to_numpy(), pivot["ey"].to_numpy(), pivot["ez"].to_numpy()])
    theta_values = np.sum(e_cart * e_theta, axis=1)
    phi_values = np.sum(e_cart * e_phi, axis=1)

    rows = []
    for pol, values in [("theta", theta_values), ("phi", phi_values)]:
        out = pivot[pivot_index].copy()
        out["theta_deg"] = np.rad2deg(theta)
        out["phi_deg"] = np.rad2deg(phi)
        out["polarization"] = pol
        out["e_real"] = np.real(values)
        out["e_imag"] = np.imag(values)
        rows.append(out)
    return pd.concat(rows, ignore_index=True)


def measurement_vector_from_nearfield(
    df: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    polarizations: tuple[str, ...] = ("theta", "phi"),
) -> tuple[np.ndarray, np.ndarray]:
    work = df.copy()
    if not set(polarizations).issubset(set(work["polarization"].astype(str))):
        work = cartesian_to_theta_phi_rows(work)

    mask = (work["sample_id"].astype(str) == sample_id) & np.isclose(pd.to_numeric(work["frequency_hz"], errors="coerce"), frequency_hz)
    sub = work.loc[mask].copy()
    if sub.empty:
        raise ValueError(f"no rows for sample_id={sample_id}, frequency_hz={frequency_hz}")
    sub["sensor_id"] = pd.to_numeric(sub["sensor_id"], errors="coerce").astype(int)
    sub["e_complex"] = pd.to_numeric(sub["e_real"], errors="coerce") + 1j * pd.to_numeric(sub["e_imag"], errors="coerce")

    sensor_ids = np.array(sorted(sub["sensor_id"].unique()), dtype=int)
    blocks = []
    for pol in polarizations:
        block = (
            sub[sub["polarization"].astype(str) == pol]
            .set_index("sensor_id")
            .reindex(sensor_ids)["e_complex"]
        )
        if block.isna().any():
            raise ValueError(f"missing {pol} values for some sensors")
        blocks.append(block.to_numpy(dtype=np.complex128))
    return np.concatenate(blocks), sensor_ids


def layout_from_nearfield(
    df: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
    sensor_ids: np.ndarray | None = None,
) -> SensorLayout:
    work = df.copy()
    mask = (work["sample_id"].astype(str) == sample_id) & np.isclose(pd.to_numeric(work["frequency_hz"], errors="coerce"), frequency_hz)
    sub = work.loc[mask].copy()
    if sub.empty:
        raise ValueError(f"no nearfield rows for sample_id={sample_id}, frequency_hz={frequency_hz}")
    sub["sensor_id"] = pd.to_numeric(sub["sensor_id"], errors="coerce").astype(int)
    if sensor_ids is None:
        sensor_ids = np.array(sorted(sub["sensor_id"].unique()), dtype=int)
    coords = (
        sub.drop_duplicates("sensor_id")
        .set_index("sensor_id")
        .reindex(sensor_ids)[["x_m", "y_m", "z_m"]]
        .astype(float)
    )
    if coords.isna().any().any():
        raise ValueError("missing coordinates for one or more requested sensor_ids")
    positions = coords.to_numpy()
    radius_values = np.linalg.norm(positions, axis=1)
    theta = np.arccos(np.clip(positions[:, 2] / np.maximum(radius_values, 1e-15), -1.0, 1.0))
    phi = np.mod(np.arctan2(positions[:, 1], positions[:, 0]), 2.0 * np.pi)
    _, e_theta, e_phi = spherical_basis(theta, phi)
    radius_m = float(np.median(radius_values))
    return SensorLayout(positions=positions, theta=theta, phi=phi, e_theta=e_theta, e_phi=e_phi, radius_m=radius_m)


def available_sample_frequency_pairs(df: pd.DataFrame) -> list[tuple[str, float]]:
    work = df.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    pairs = work[["sample_id", "frequency_hz"]].drop_duplicates().dropna()
    return [(str(row.sample_id), float(row.frequency_hz)) for row in pairs.itertuples(index=False)]


def farfield_power_from_table(
    df: pd.DataFrame,
    sample_id: str,
    frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, tuple[int, int] | None]:
    work = df.copy()
    work["sample_id"] = work["sample_id"].astype(str).str.strip()
    work["frequency_hz"] = pd.to_numeric(work["frequency_hz"], errors="coerce")
    mask = (work["sample_id"] == sample_id) & np.isclose(work["frequency_hz"], frequency_hz)
    sub = work.loc[mask].copy()
    if sub.empty:
        raise ValueError(f"no farfield rows for sample_id={sample_id}, frequency_hz={frequency_hz}")

    theta = np.deg2rad(pd.to_numeric(sub["theta_deg"], errors="coerce").to_numpy(dtype=float))
    phi = np.deg2rad(pd.to_numeric(sub["phi_deg"], errors="coerce").to_numpy(dtype=float))
    if FARFIELD_COMPLEX_REQUIRED.issubset(set(sub.columns)):
        e_theta = pd.to_numeric(sub["e_theta_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
            sub["e_theta_imag"], errors="coerce"
        ).to_numpy(dtype=float)
        e_phi = pd.to_numeric(sub["e_phi_real"], errors="coerce").to_numpy(dtype=float) + 1j * pd.to_numeric(
            sub["e_phi_imag"], errors="coerce"
        ).to_numpy(dtype=float)
        power = np.abs(e_theta) ** 2 + np.abs(e_phi) ** 2
    elif "power" in sub.columns:
        power = pd.to_numeric(sub["power"], errors="coerce").to_numpy(dtype=float)
    elif "gain_db" in sub.columns:
        gain_db = pd.to_numeric(sub["gain_db"], errors="coerce").to_numpy(dtype=float)
        power = 10.0 ** (gain_db / 10.0)
    else:
        raise ValueError("farfield table must include complex Etheta/Ephi, power, or gain_db")

    if np.isnan(theta).any() or np.isnan(phi).any() or np.isnan(power).any():
        raise ValueError("farfield table contains non-numeric theta/phi/power values")

    theta_unique = np.unique(np.round(np.rad2deg(theta), 10))
    phi_unique = np.unique(np.round(np.rad2deg(phi), 10))
    shape = None
    if theta_unique.size * phi_unique.size == sub.shape[0]:
        shape = (int(theta_unique.size), int(phi_unique.size))
    return theta, phi, power, shape
