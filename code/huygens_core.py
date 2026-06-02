from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from em_core import C0, SensorLayout, spherical_basis


@dataclass(frozen=True)
class HuygensSurface:
    prior_id: str
    positions: np.ndarray
    normals: np.ndarray
    tangent1: np.ndarray
    tangent2: np.ndarray
    weights_m2: np.ndarray


def load_huygens_surface(path: Path) -> HuygensSurface:
    table = pd.read_csv(path)
    required = {
        "prior_id",
        "x_m",
        "y_m",
        "z_m",
        "normal_x",
        "normal_y",
        "normal_z",
        "tangent1_x",
        "tangent1_y",
        "tangent1_z",
        "tangent2_x",
        "tangent2_y",
        "tangent2_z",
        "weight_m2",
    }
    missing = sorted(required - set(table.columns))
    if missing:
        raise ValueError(f"Huygens surface table missing required columns: {missing}")
    prior_ids = sorted(table["prior_id"].astype(str).unique())
    if len(prior_ids) != 1:
        raise ValueError(f"Huygens surface table must contain one prior_id, got {prior_ids}")
    return HuygensSurface(
        prior_id=prior_ids[0],
        positions=table[["x_m", "y_m", "z_m"]].to_numpy(dtype=float),
        normals=table[["normal_x", "normal_y", "normal_z"]].to_numpy(dtype=float),
        tangent1=table[["tangent1_x", "tangent1_y", "tangent1_z"]].to_numpy(dtype=float),
        tangent2=table[["tangent2_x", "tangent2_y", "tangent2_z"]].to_numpy(dtype=float),
        weights_m2=table["weight_m2"].to_numpy(dtype=float),
    )


def surface_basis_count(include_magnetic: bool) -> int:
    return 4 if include_magnetic else 2


def surface_unknown_count(surface: HuygensSurface, include_magnetic: bool) -> int:
    return int(surface.positions.shape[0] * surface_basis_count(include_magnetic))


def column_weight_factors(surface: HuygensSurface, weight_mode: str) -> np.ndarray:
    if weight_mode == "sqrt_area":
        node_weights = np.sqrt(np.maximum(surface.weights_m2, 0.0))
    elif weight_mode == "area":
        node_weights = surface.weights_m2.copy()
    elif weight_mode == "none":
        node_weights = np.ones_like(surface.weights_m2)
    else:
        raise ValueError(f"unsupported Huygens weight mode: {weight_mode}")
    return node_weights


def electric_dipole_near_field(
    obs_positions: np.ndarray,
    source_position: np.ndarray,
    moment: np.ndarray,
    frequency_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    k = 2.0 * np.pi * frequency_hz / C0
    rel = obs_positions - source_position[None, :]
    distance = np.linalg.norm(rel, axis=1)
    r_hat = rel / np.maximum(distance[:, None], 1e-15)
    transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
    phase = np.exp(-1j * k * distance) / np.maximum(distance, 1e-12)
    return transverse * phase[:, None], r_hat


def electric_dipole_far_field(
    r_hat: np.ndarray,
    source_position: np.ndarray,
    moment: np.ndarray,
    frequency_hz: float,
) -> np.ndarray:
    k = 2.0 * np.pi * frequency_hz / C0
    phase = np.exp(1j * k * (r_hat @ source_position))
    transverse = moment[None, :] - r_hat * np.sum(r_hat * moment[None, :], axis=1, keepdims=True)
    return transverse * phase[:, None]


def magnetic_dual_field(r_hat: np.ndarray, electric_like_field: np.ndarray, sign: float = 1.0) -> np.ndarray:
    return sign * np.cross(r_hat, electric_like_field)


def project_theta_phi(field: np.ndarray, e_theta: np.ndarray, e_phi: np.ndarray) -> np.ndarray:
    theta_pol = np.sum(field * e_theta, axis=1)
    phi_pol = np.sum(field * e_phi, axis=1)
    return np.concatenate([theta_pol, phi_pol])


def build_huygens_measurement_matrix(
    layout: SensorLayout,
    surface: HuygensSurface,
    frequency_hz: float,
    sensor_indices: np.ndarray | None = None,
    include_magnetic: bool = True,
    magnetic_sign: float = 1.0,
    weight_mode: str = "sqrt_area",
) -> np.ndarray:
    if sensor_indices is None:
        sensor_indices = np.arange(layout.positions.shape[0])
    positions = layout.positions[sensor_indices]
    e_theta = layout.e_theta[sensor_indices]
    e_phi = layout.e_phi[sensor_indices]
    n_sensors = int(sensor_indices.size)
    basis_per_node = surface_basis_count(include_magnetic)
    matrix = np.zeros((2 * n_sensors, surface.positions.shape[0] * basis_per_node), dtype=np.complex128)
    factors = column_weight_factors(surface, weight_mode)

    for node_idx, source_position in enumerate(surface.positions):
        tangents = (surface.tangent1[node_idx], surface.tangent2[node_idx])
        for tangent_idx, moment in enumerate(tangents):
            electric_field, r_hat = electric_dipole_near_field(positions, source_position, moment, frequency_hz)
            col = basis_per_node * node_idx + tangent_idx
            matrix[:, col] = project_theta_phi(electric_field, e_theta, e_phi) * factors[node_idx]
            if include_magnetic:
                magnetic_field = magnetic_dual_field(r_hat, electric_field, sign=magnetic_sign)
                matrix[:, col + 2] = project_theta_phi(magnetic_field, e_theta, e_phi) * factors[node_idx]
    return matrix


def build_huygens_farfield_matrix(
    surface: HuygensSurface,
    theta: np.ndarray,
    phi: np.ndarray,
    frequency_hz: float,
    include_magnetic: bool = True,
    magnetic_sign: float = 1.0,
    weight_mode: str = "sqrt_area",
) -> np.ndarray:
    r_hat, e_theta, e_phi = spherical_basis(theta, phi)
    basis_per_node = surface_basis_count(include_magnetic)
    matrix = np.zeros((2 * theta.size, surface.positions.shape[0] * basis_per_node), dtype=np.complex128)
    factors = column_weight_factors(surface, weight_mode)

    for node_idx, source_position in enumerate(surface.positions):
        tangents = (surface.tangent1[node_idx], surface.tangent2[node_idx])
        for tangent_idx, moment in enumerate(tangents):
            electric_field = electric_dipole_far_field(r_hat, source_position, moment, frequency_hz)
            col = basis_per_node * node_idx + tangent_idx
            matrix[:, col] = project_theta_phi(electric_field, e_theta, e_phi) * factors[node_idx]
            if include_magnetic:
                magnetic_field = magnetic_dual_field(r_hat, electric_field, sign=magnetic_sign)
                matrix[:, col + 2] = project_theta_phi(magnetic_field, e_theta, e_phi) * factors[node_idx]
    return matrix
