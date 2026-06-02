from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = ROOT / "data" / "source_priors" / "huygens_surface"


@dataclass(frozen=True)
class SurfaceConfig:
    prior_id: str
    surface_type: str
    note: str
    node_count_hint: int
    center_x_m: float
    center_y_m: float
    center_z_m: float
    radius_m: float | None = None
    x_half_span_m: float | None = None
    y_half_span_m: float | None = None
    z_half_span_m: float | None = None
    nx: int | None = None
    ny: int | None = None
    nz: int | None = None


def default_configs() -> tuple[SurfaceConfig, ...]:
    return (
        SurfaceConfig(
            prior_id="level1_local_sphere_r0p35",
            surface_type="sphere",
            note="Closed local Huygens sphere around the Level 1 known source center at (0, 0, 4 m).",
            node_count_hint=96,
            center_x_m=0.0,
            center_y_m=0.0,
            center_z_m=4.0,
            radius_m=0.35,
        ),
        SurfaceConfig(
            prior_id="airframe_box_coarse",
            surface_type="box",
            note="Coarse box Huygens surface enclosing the 12 m x 10 m x 8 m aircraft envelope with margin.",
            node_count_hint=0,
            center_x_m=0.0,
            center_y_m=0.0,
            center_z_m=4.0,
            x_half_span_m=6.5,
            y_half_span_m=5.5,
            z_half_span_m=4.5,
            nx=9,
            ny=9,
            nz=7,
        ),
        SurfaceConfig(
            prior_id="airframe_box_medium",
            surface_type="box",
            note="Medium box Huygens surface for later Level 2/Level 3 structure-aware reconstruction tests.",
            node_count_hint=0,
            center_x_m=0.0,
            center_y_m=0.0,
            center_z_m=4.0,
            x_half_span_m=6.5,
            y_half_span_m=5.5,
            z_half_span_m=4.5,
            nx=13,
            ny=11,
            nz=9,
        ),
    )


def unit(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(norm, 1e-15)


def tangent_basis(normals: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    refs = np.tile(np.array([0.0, 0.0, 1.0]), (normals.shape[0], 1))
    parallel = np.abs(np.sum(normals * refs, axis=1)) > 0.9
    refs[parallel] = np.array([1.0, 0.0, 0.0])
    tangent_1 = unit(np.cross(refs, normals))
    tangent_2 = unit(np.cross(normals, tangent_1))
    return tangent_1, tangent_2


def fibonacci_sphere(config: SurfaceConfig) -> pd.DataFrame:
    if config.radius_m is None:
        raise ValueError(f"{config.prior_id} is missing radius_m")
    n_nodes = int(config.node_count_hint)
    if n_nodes <= 0:
        raise ValueError(f"{config.prior_id} node_count_hint must be positive")

    idx = np.arange(n_nodes, dtype=float)
    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    z = 1.0 - 2.0 * (idx + 0.5) / n_nodes
    radius_xy = np.sqrt(np.maximum(1.0 - z**2, 0.0))
    phi = idx * golden_angle
    normals = np.column_stack([radius_xy * np.cos(phi), radius_xy * np.sin(phi), z])
    center = np.array([config.center_x_m, config.center_y_m, config.center_z_m])
    positions = center[None, :] + config.radius_m * normals
    tangent_1, tangent_2 = tangent_basis(normals)
    weights = np.full(n_nodes, 4.0 * math.pi * config.radius_m**2 / n_nodes)
    return rows_from_arrays(config, positions, normals, tangent_1, tangent_2, weights)


def face_grid(
    fixed_axis: int,
    fixed_value: float,
    axis_a: int,
    values_a: np.ndarray,
    axis_b: int,
    values_b: np.ndarray,
    normal: np.ndarray,
    area: float,
    config: SurfaceConfig,
) -> pd.DataFrame:
    aa, bb = np.meshgrid(values_a, values_b, indexing="ij")
    positions = np.zeros((aa.size, 3), dtype=float)
    positions[:, fixed_axis] = fixed_value
    positions[:, axis_a] = aa.ravel()
    positions[:, axis_b] = bb.ravel()
    normals = np.tile(normal, (positions.shape[0], 1))
    tangent_1, tangent_2 = tangent_basis(normals)
    weights = np.full(positions.shape[0], area / positions.shape[0])
    return rows_from_arrays(config, positions, normals, tangent_1, tangent_2, weights)


def box_surface(config: SurfaceConfig) -> pd.DataFrame:
    required = (config.x_half_span_m, config.y_half_span_m, config.z_half_span_m, config.nx, config.ny, config.nz)
    if any(value is None for value in required):
        raise ValueError(f"{config.prior_id} is missing box parameters")

    cx, cy, cz = config.center_x_m, config.center_y_m, config.center_z_m
    hx = float(config.x_half_span_m)
    hy = float(config.y_half_span_m)
    hz = float(config.z_half_span_m)
    xs = np.linspace(cx - hx, cx + hx, int(config.nx))
    ys = np.linspace(cy - hy, cy + hy, int(config.ny))
    zs = np.linspace(cz - hz, cz + hz, int(config.nz))

    frames = [
        face_grid(0, cx + hx, 1, ys, 2, zs, np.array([1.0, 0.0, 0.0]), 4.0 * hy * hz, config),
        face_grid(0, cx - hx, 1, ys, 2, zs, np.array([-1.0, 0.0, 0.0]), 4.0 * hy * hz, config),
        face_grid(1, cy + hy, 0, xs, 2, zs, np.array([0.0, 1.0, 0.0]), 4.0 * hx * hz, config),
        face_grid(1, cy - hy, 0, xs, 2, zs, np.array([0.0, -1.0, 0.0]), 4.0 * hx * hz, config),
        face_grid(2, cz + hz, 0, xs, 1, ys, np.array([0.0, 0.0, 1.0]), 4.0 * hx * hy, config),
        face_grid(2, cz - hz, 0, xs, 1, ys, np.array([0.0, 0.0, -1.0]), 4.0 * hx * hy, config),
    ]
    return pd.concat(frames, ignore_index=True)


def rows_from_arrays(
    config: SurfaceConfig,
    positions: np.ndarray,
    normals: np.ndarray,
    tangent_1: np.ndarray,
    tangent_2: np.ndarray,
    weights: np.ndarray,
) -> pd.DataFrame:
    n_nodes = positions.shape[0]
    return pd.DataFrame(
        {
            "prior_id": config.prior_id,
            "node_id": np.arange(n_nodes, dtype=int),
            "surface_type": config.surface_type,
            "x_m": positions[:, 0],
            "y_m": positions[:, 1],
            "z_m": positions[:, 2],
            "normal_x": normals[:, 0],
            "normal_y": normals[:, 1],
            "normal_z": normals[:, 2],
            "tangent1_x": tangent_1[:, 0],
            "tangent1_y": tangent_1[:, 1],
            "tangent1_z": tangent_1[:, 2],
            "tangent2_x": tangent_2[:, 0],
            "tangent2_y": tangent_2[:, 1],
            "tangent2_z": tangent_2[:, 2],
            "weight_m2": weights,
            "unknowns_per_node": 4,
            "unknown_vector": "J_t1,J_t2,M_t1,M_t2",
            "include_initial": True,
            "note": config.note,
        }
    )


def build_nodes(config: SurfaceConfig) -> pd.DataFrame:
    if config.surface_type == "sphere":
        return fibonacci_sphere(config)
    if config.surface_type == "box":
        return box_surface(config)
    raise ValueError(f"unsupported surface_type: {config.surface_type}")


def write_readme(out_dir: Path, configs: list[SurfaceConfig], summary_rows: list[dict[str, object]]) -> None:
    table_rows = [
        (
            f"| `{row['prior_id']}` | `{row['surface_type']}` | {row['node_count']} | "
            f"{row['complex_unknown_count']} | `{row['file']}` |"
        )
        for row in summary_rows
    ]
    content = f"""# Huygens Surface Source Priors

This directory stores candidate Huygens-surface node sets for the next G3
source-prior upgrade. These files define geometry and unknown-vector contracts;
they are not yet final reconstruction results.

## Generated Files

| Prior | Surface | Nodes | Complex unknowns | File |
|---|---|---:|---:|---|
{chr(10).join(table_rows)}

`huygens_surface_configs.csv` stores the parameters used to generate the node
sets. `huygens_surface_prior_summary.json` stores the same information in a
script-friendly summary.

## Unknown Contract

Each node has four complex tangential current unknowns:

```text
q_i = [J_t1, J_t2, M_t1, M_t2]
```

`J` is the equivalent electric surface current and `M` is the equivalent
magnetic surface current. `tangent1` and `tangent2` are local unit vectors
orthogonal to the outward normal. The future Huygens measurement matrix should
map these unknowns to the same measured vector already used by the CST scripts:

```text
y = [Etheta(sensor_1..N), Ephi(sensor_1..N)]
```

## Current Role

- `level1_local_sphere_r0p35` is the first Level 1 diagnostic prior around the
  known source center at `(0, 0, 4 m)`.
- `airframe_box_coarse` and `airframe_box_medium` are geometry contracts for
  later Level 2/Level 3 structure-aware reconstruction.
- Use these priors only after the CST true near-field monitor gate is checked,
  or state clearly that the input is still FarfieldPlot-derived angular data.

## Generation Command

```powershell
python code\\prepare_huygens_surface_prior.py
```
"""
    (out_dir / "README.md").write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Huygens-surface source-prior node sets.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Output directory for source-prior files.")
    parser.add_argument("--prior", action="append", dest="priors", help="Prior id to generate. Repeatable.")
    parser.add_argument("--list-priors", action="store_true", help="List available prior ids and exit.")
    args = parser.parse_args()
    if args.list_priors:
        for config in default_configs():
            print(f"{config.prior_id}: {config.note}")
        raise SystemExit(0)
    return args


def main() -> int:
    args = parse_args()
    configs = list(default_configs())
    if args.priors:
        by_id = {config.prior_id: config for config in configs}
        missing = sorted(set(args.priors) - set(by_id))
        if missing:
            raise ValueError(f"unknown prior ids: {missing}")
        configs = [by_id[prior_id] for prior_id in args.priors]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: list[dict[str, object]] = []
    for config in configs:
        nodes = build_nodes(config)
        file_name = f"{config.prior_id}_nodes.csv"
        nodes.to_csv(out_dir / file_name, index=False, encoding="utf-8-sig")
        summary_rows.append(
            {
                "prior_id": config.prior_id,
                "surface_type": config.surface_type,
                "file": file_name,
                "node_count": int(nodes.shape[0]),
                "complex_unknown_count": int(nodes.shape[0] * 4),
                "area_sum_m2": float(nodes["weight_m2"].sum()),
                "note": config.note,
            }
        )

    pd.DataFrame([asdict(config) for config in configs]).to_csv(
        out_dir / "huygens_surface_configs.csv",
        index=False,
        encoding="utf-8-sig",
    )
    summary = {
        "generated_by": "code/prepare_huygens_surface_prior.py",
        "out_dir": str(out_dir.relative_to(ROOT)),
        "purpose": "Geometry and unknown-vector contract for Huygens-surface source-prior reconstruction.",
        "unknowns_per_node": 4,
        "unknown_vector": "J_t1,J_t2,M_t1,M_t2",
        "priors": summary_rows,
    }
    (out_dir / "huygens_surface_prior_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_readme(out_dir, configs, summary_rows)

    print(f"Huygens surface priors written to {out_dir}")
    for row in summary_rows:
        print(f"{row['prior_id']}: {row['node_count']} nodes, {row['complex_unknown_count']} complex unknowns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
