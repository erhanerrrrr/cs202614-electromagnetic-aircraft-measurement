from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


C0 = 299_792_458.0


@dataclass(frozen=True)
class SensorLayout:
    positions: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    e_theta: np.ndarray
    e_phi: np.ndarray
    radius_m: float


@dataclass(frozen=True)
class SourceSet:
    positions: np.ndarray
    moments: np.ndarray
    label: str


def unit_vector(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(norm, 1e-15)


def spherical_basis(theta: np.ndarray, phi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sin_t = np.sin(theta)
    cos_t = np.cos(theta)
    sin_p = np.sin(phi)
    cos_p = np.cos(phi)
    r_hat = np.column_stack([sin_t * cos_p, sin_t * sin_p, cos_t])
    e_theta = np.column_stack([cos_t * cos_p, cos_t * sin_p, -sin_t])
    e_phi = np.column_stack([-sin_p, cos_p, np.zeros_like(phi)])
    return r_hat, e_theta, e_phi


def make_hemisphere_layout(
    n_theta: int = 9,
    n_phi: int = 18,
    radius_m: float = 13.0,
    theta_min_deg: float = 6.0,
    theta_max_deg: float = 86.0,
) -> SensorLayout:
    theta_grid = np.linspace(np.deg2rad(theta_min_deg), np.deg2rad(theta_max_deg), n_theta)
    phi_grid = np.linspace(0.0, 2.0 * np.pi, n_phi, endpoint=False)
    theta, phi = np.meshgrid(theta_grid, phi_grid, indexing="ij")
    theta = theta.ravel()
    phi = phi.ravel()
    r_hat, e_theta, e_phi = spherical_basis(theta, phi)
    positions = radius_m * r_hat
    return SensorLayout(positions=positions, theta=theta, phi=phi, e_theta=e_theta, e_phi=e_phi, radius_m=radius_m)


def make_equivalent_grid(
    nx: int = 5,
    ny: int = 4,
    nz: int = 3,
    x_span_m: tuple[float, float] = (-5.5, 5.5),
    y_span_m: tuple[float, float] = (-4.5, 4.5),
    z_span_m: tuple[float, float] = (1.0, 7.0),
) -> np.ndarray:
    xs = np.linspace(*x_span_m, nx)
    ys = np.linspace(*y_span_m, ny)
    zs = np.linspace(*z_span_m, nz)
    xx, yy, zz = np.meshgrid(xs, ys, zs, indexing="ij")
    return np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])


def _field_from_dipole(
    obs_positions: np.ndarray,
    source_position: np.ndarray,
    moment: np.ndarray,
    frequency_hz: float,
) -> np.ndarray:
    k = 2.0 * np.pi * frequency_hz / C0
    rel = obs_positions - source_position[None, :]
    distance = np.linalg.norm(rel, axis=1)
    r_hat = rel / np.maximum(distance[:, None], 1e-15)
    transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
    phase = np.exp(-1j * k * distance) / np.maximum(distance, 1e-12)
    return transverse * phase[:, None]


def sensor_response(
    layout: SensorLayout,
    sources: SourceSet,
    frequency_hz: float,
    sensor_indices: np.ndarray | None = None,
) -> np.ndarray:
    if sensor_indices is None:
        sensor_indices = np.arange(layout.positions.shape[0])
    positions = layout.positions[sensor_indices]
    e_theta = layout.e_theta[sensor_indices]
    e_phi = layout.e_phi[sensor_indices]
    field = np.zeros((positions.shape[0], 3), dtype=np.complex128)
    for source_position, moment in zip(sources.positions, sources.moments):
        field += _field_from_dipole(positions, source_position, moment, frequency_hz)
    theta_pol = np.sum(field * e_theta, axis=1)
    phi_pol = np.sum(field * e_phi, axis=1)
    return np.concatenate([theta_pol, phi_pol])


def cartesian_field_response(
    positions: np.ndarray,
    sources: SourceSet,
    frequency_hz: float,
) -> np.ndarray:
    field = np.zeros((positions.shape[0], 3), dtype=np.complex128)
    for source_position, moment in zip(sources.positions, sources.moments):
        field += _field_from_dipole(positions, source_position, moment, frequency_hz)
    return field


def add_complex_noise(values: np.ndarray, snr_db: float, rng: np.random.Generator) -> np.ndarray:
    signal_power = np.mean(np.abs(values) ** 2)
    noise_power = signal_power / (10.0 ** (snr_db / 10.0))
    sigma = np.sqrt(noise_power / 2.0)
    noise = sigma * (rng.standard_normal(values.shape) + 1j * rng.standard_normal(values.shape))
    return values + noise


def build_measurement_matrix(
    layout: SensorLayout,
    grid_positions: np.ndarray,
    frequency_hz: float,
    sensor_indices: np.ndarray | None = None,
) -> np.ndarray:
    if sensor_indices is None:
        sensor_indices = np.arange(layout.positions.shape[0])
    n_sensors = sensor_indices.size
    n_grid = grid_positions.shape[0]
    matrix = np.zeros((2 * n_sensors, 3 * n_grid), dtype=np.complex128)
    basis = np.eye(3)
    for source_idx, source_position in enumerate(grid_positions):
        for component_idx, moment in enumerate(basis):
            dummy = SourceSet(
                positions=source_position[None, :],
                moments=moment[None, :].astype(np.complex128),
                label="basis",
            )
            col = 3 * source_idx + component_idx
            matrix[:, col] = sensor_response(layout, dummy, frequency_hz, sensor_indices)
    return matrix


def solve_tikhonov(matrix: np.ndarray, values: np.ndarray, lam: float = 1e-3) -> np.ndarray:
    n_unknown = matrix.shape[1]
    lhs = np.vstack([matrix, np.sqrt(lam) * np.eye(n_unknown, dtype=np.complex128)])
    rhs = np.concatenate([values, np.zeros(n_unknown, dtype=np.complex128)])
    solution, *_ = np.linalg.lstsq(lhs, rhs, rcond=None)
    return solution


def vector_to_source_set(grid_positions: np.ndarray, solution: np.ndarray, label: str = "reconstructed") -> SourceSet:
    moments = solution.reshape(grid_positions.shape[0], 3)
    return SourceSet(positions=grid_positions, moments=moments, label=label)


def farfield_pattern(
    sources: SourceSet,
    theta: np.ndarray,
    phi: np.ndarray,
    frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k = 2.0 * np.pi * frequency_hz / C0
    r_hat, e_theta, e_phi = spherical_basis(theta, phi)
    field = np.zeros((theta.size, 3), dtype=np.complex128)
    for source_position, moment in zip(sources.positions, sources.moments):
        phase = np.exp(1j * k * (r_hat @ source_position))
        transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
        field += transverse * phase[:, None]
    theta_pol = np.sum(field * e_theta, axis=1)
    phi_pol = np.sum(field * e_phi, axis=1)
    power = np.abs(theta_pol) ** 2 + np.abs(phi_pol) ** 2
    return power, theta_pol, phi_pol


def farfield_grid(n_theta: int = 37, n_phi: int = 72) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    theta_values = np.linspace(np.deg2rad(2.0), np.deg2rad(88.0), n_theta)
    phi_values = np.linspace(0.0, 2.0 * np.pi, n_phi, endpoint=False)
    theta, phi = np.meshgrid(theta_values, phi_values, indexing="ij")
    return theta.ravel(), phi.ravel(), (n_theta, n_phi)


def pattern_metrics(true_power: np.ndarray, rec_power: np.ndarray, theta: np.ndarray, phi: np.ndarray) -> dict[str, float]:
    true_norm = true_power / np.maximum(np.max(true_power), 1e-15)
    rec_norm = rec_power / np.maximum(np.max(rec_power), 1e-15)
    nmse = np.sum((true_norm - rec_norm) ** 2) / np.maximum(np.sum(true_norm**2), 1e-15)
    corr = np.corrcoef(true_norm, rec_norm)[0, 1]
    true_peak = int(np.argmax(true_norm))
    rec_peak = int(np.argmax(rec_norm))
    if rec_norm[true_peak] >= 0.98 and true_norm[rec_peak] >= 0.98:
        angle_error_deg = 0.0
    else:
        true_vec, _, _ = spherical_basis(theta[true_peak : true_peak + 1], phi[true_peak : true_peak + 1])
        rec_vec, _, _ = spherical_basis(theta[rec_peak : rec_peak + 1], phi[rec_peak : rec_peak + 1])
        dot = float(np.clip(np.sum(true_vec[0] * rec_vec[0]), -1.0, 1.0))
        angle_error_deg = float(np.rad2deg(np.arccos(dot)))
    peak_error_db = float(10.0 * np.log10(np.maximum(np.max(rec_power), 1e-15) / np.maximum(np.max(true_power), 1e-15)))
    return {
        "nmse": float(nmse),
        "correlation": float(corr),
        "main_lobe_error_deg": angle_error_deg,
        "peak_error_db": peak_error_db,
    }


def farthest_point_subset(layout: SensorLayout, count: int) -> np.ndarray:
    directions = unit_vector(layout.positions)
    selected = [0]
    min_distance = np.linalg.norm(directions - directions[0], axis=1)
    while len(selected) < count:
        idx = int(np.argmax(min_distance))
        selected.append(idx)
        new_distance = np.linalg.norm(directions - directions[idx], axis=1)
        min_distance = np.minimum(min_distance, new_distance)
    return np.array(selected, dtype=int)


def random_subset(n_total: int, count: int, rng: np.random.Generator) -> np.ndarray:
    return np.sort(rng.choice(n_total, size=count, replace=False))


def make_reference_sources(grid_positions: np.ndarray) -> SourceSet:
    def nearest(point: Iterable[float]) -> int:
        point_arr = np.array(point, dtype=float)
        return int(np.argmin(np.linalg.norm(grid_positions - point_arr[None, :], axis=1)))

    indices = [
        nearest((-2.75, -1.5, 4.0)),
        nearest((2.75, 1.5, 4.0)),
        nearest((0.0, 4.5, 7.0)),
    ]
    positions = grid_positions[indices]
    moments = np.array(
        [
            [1.0 + 0.0j, 0.15 + 0.25j, 0.25 - 0.05j],
            [0.35 - 0.2j, 0.9 + 0.15j, -0.2 + 0.1j],
            [0.15 + 0.1j, -0.2 + 0.0j, 0.75 + 0.25j],
        ],
        dtype=np.complex128,
    )
    return SourceSet(positions=positions, moments=moments, label="three_source_reference")


def class_templates(grid_positions: np.ndarray) -> list[SourceSet]:
    def nearest(point: Iterable[float]) -> np.ndarray:
        point_arr = np.array(point, dtype=float)
        return grid_positions[int(np.argmin(np.linalg.norm(grid_positions - point_arr[None, :], axis=1)))]

    templates = [
        SourceSet(
            positions=np.array([nearest((-5.5, -4.5, 4.0)), nearest((5.5, 4.5, 4.0))]),
            moments=np.array([[1.0, 0.2j, 0.1], [0.7j, 0.9, -0.1]], dtype=np.complex128),
            label="comm_pair",
        ),
        SourceSet(
            positions=np.array([nearest((0.0, -4.5, 7.0)), nearest((0.0, 4.5, 7.0))]),
            moments=np.array([[0.1, 0.2, 1.2], [0.2j, 0.1, 0.9j]], dtype=np.complex128),
            label="radar_top",
        ),
        SourceSet(
            positions=np.array([nearest((-2.75, 1.5, 1.0)), nearest((2.75, -1.5, 7.0)), nearest((0.0, 4.5, 4.0))]),
            moments=np.array([[0.8, 0.1, 0.6j], [0.2, 1.1j, 0.1], [0.5j, 0.4, 0.5]], dtype=np.complex128),
            label="mixed_avionics",
        ),
        SourceSet(
            positions=np.array([nearest((-5.5, 4.5, 7.0)), nearest((5.5, -4.5, 1.0)), nearest((0.0, 0.0, 4.0))]),
            moments=np.array([[1.0j, 0.2, 0.3], [0.1, 0.8, 0.8j], [0.9, 0.9j, 0.1]], dtype=np.complex128),
            label="multi_state_on",
        ),
    ]
    return templates


def jitter_sources(template: SourceSet, rng: np.random.Generator, amp_jitter: float = 0.08, phase_jitter_deg: float = 10.0) -> SourceSet:
    amp = 1.0 + amp_jitter * rng.standard_normal(template.moments.shape)
    phase = np.exp(1j * np.deg2rad(phase_jitter_deg) * rng.standard_normal(template.moments.shape))
    moments = template.moments * amp * phase
    return SourceSet(positions=template.positions, moments=moments, label=template.label)
