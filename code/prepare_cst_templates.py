from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from em_core import SourceSet, cartesian_field_response, farfield_grid, farfield_pattern, make_hemisphere_layout


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "cst_templates"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    layout = make_hemisphere_layout(n_theta=9, n_phi=18, radius_m=13.0)

    sensor_df = pd.DataFrame(
        {
            "sensor_id": np.arange(layout.positions.shape[0]),
            "x_m": layout.positions[:, 0],
            "y_m": layout.positions[:, 1],
            "z_m": layout.positions[:, 2],
            "theta_deg": np.rad2deg(layout.theta),
            "phi_deg": np.rad2deg(layout.phi),
            "e_theta_x": layout.e_theta[:, 0],
            "e_theta_y": layout.e_theta[:, 1],
            "e_theta_z": layout.e_theta[:, 2],
            "e_phi_x": layout.e_phi[:, 0],
            "e_phi_y": layout.e_phi[:, 1],
            "e_phi_z": layout.e_phi[:, 2],
            "radius_m": layout.radius_m,
        }
    )
    sensor_df.to_csv(OUT / "sensor_layout_hemisphere_for_cst.csv", index=False, encoding="utf-8-sig")

    nearfield_rows = []
    for _, row in sensor_df.iterrows():
        for polarization in ["Ex", "Ey", "Ez"]:
            nearfield_rows.append(
                {
                    "sample_id": "L1_short_dipole_z_1p2G",
                    "sensor_id": int(row["sensor_id"]),
                    "x_m": row["x_m"],
                    "y_m": row["y_m"],
                    "z_m": row["z_m"],
                    "theta_deg": row["theta_deg"],
                    "phi_deg": row["phi_deg"],
                    "frequency_hz": 1_200_000_000,
                    "polarization": polarization,
                    "e_real": "",
                    "e_imag": "",
                    "source_config": "short_dipole_z",
                    "carrier_model": "standard_source",
                    "working_state": "single_source_on",
                    "cst_project": "CST_L1_short_dipole_1p2GHz.cst",
                    "monitor_name": "nearfield_hemisphere_1p2GHz",
                }
            )
    pd.DataFrame(nearfield_rows).to_csv(OUT / "nearfield_import_template.csv", index=False, encoding="utf-8-sig")

    theta, phi, _ = farfield_grid(n_theta=37, n_phi=72)
    farfield_df = pd.DataFrame(
        {
            "sample_id": "L1_short_dipole_z_1p2G",
            "theta_deg": np.rad2deg(theta),
            "phi_deg": np.rad2deg(phi),
            "frequency_hz": 1_200_000_000,
            "e_theta_real": "",
            "e_theta_imag": "",
            "e_phi_real": "",
            "e_phi_imag": "",
            "gain_db": "",
            "source_config": "short_dipole_z",
            "carrier_model": "standard_source",
            "working_state": "single_source_on",
            "cst_project": "CST_L1_short_dipole_1p2GHz.cst",
            "monitor_name": "farfield_1p2GHz",
        }
    )
    farfield_df.to_csv(OUT / "farfield_truth_template.csv", index=False, encoding="utf-8-sig")

    demo_source = SourceSet(
        positions=np.array([[0.0, 0.0, 4.0]]),
        moments=np.array([[0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j]]),
        label="demo_short_dipole_z",
    )
    cart_field = cartesian_field_response(layout.positions, demo_source, 1_200_000_000)
    demo_rows = []
    for sensor_idx, row in sensor_df.iterrows():
        for component_idx, polarization in enumerate(["Ex", "Ey", "Ez"]):
            value = cart_field[sensor_idx, component_idx]
            demo_rows.append(
                {
                    "sample_id": "L1_short_dipole_z_1p2G",
                    "sensor_id": int(row["sensor_id"]),
                    "x_m": row["x_m"],
                    "y_m": row["y_m"],
                    "z_m": row["z_m"],
                    "theta_deg": row["theta_deg"],
                    "phi_deg": row["phi_deg"],
                    "frequency_hz": 1_200_000_000,
                    "polarization": polarization,
                    "e_real": float(np.real(value)),
                    "e_imag": float(np.imag(value)),
                    "source_config": "short_dipole_z",
                    "carrier_model": "standard_source_demo",
                    "working_state": "single_source_on",
                    "cst_project": "synthetic_demo_not_cst.cst",
                    "monitor_name": "nearfield_hemisphere_1p2GHz",
                }
            )
    pd.DataFrame(demo_rows).to_csv(OUT / "nearfield_demo_valid.csv", index=False, encoding="utf-8-sig")

    demo_power, demo_e_theta, demo_e_phi = farfield_pattern(demo_source, theta, phi, 1_200_000_000)
    demo_farfield_df = farfield_df.copy()
    demo_farfield_df["e_theta_real"] = np.real(demo_e_theta)
    demo_farfield_df["e_theta_imag"] = np.imag(demo_e_theta)
    demo_farfield_df["e_phi_real"] = np.real(demo_e_phi)
    demo_farfield_df["e_phi_imag"] = np.imag(demo_e_phi)
    demo_farfield_df["gain_db"] = 10.0 * np.log10(demo_power / np.max(demo_power) + 1e-12)
    demo_farfield_df["carrier_model"] = "standard_source_demo"
    demo_farfield_df["cst_project"] = "synthetic_demo_not_cst.cst"
    demo_farfield_df.to_csv(OUT / "farfield_demo_valid.csv", index=False, encoding="utf-8-sig")

    metadata = {
        "contest": "CS-202614",
        "stage": "G2_CST_Level_1_standard_source",
        "sample_id": "L1_short_dipole_z_1p2G",
        "frequency_hz": 1_200_000_000,
        "coordinate_system": {
            "x": "future fuselage longitudinal axis",
            "y": "lateral axis",
            "z": "height axis",
            "unit": "m",
            "origin": "test object geometric center or fixed project origin",
        },
        "measurement_layout": {
            "type": "2pi upper hemisphere",
            "radius_m": 13.0,
            "sensor_points": int(layout.positions.shape[0]),
            "polarization_plan": "Export Ex/Ey/Ez from CST; Python will convert to theta/phi if needed.",
        },
        "object_envelope_m": {"x": [-6, 6], "y": [-5, 5], "z": [0, 8]},
        "required_outputs": [
            "sensor_layout_hemisphere_for_cst.csv",
            "nearfield csv with Ex/Ey/Ez complex field",
            "farfield csv with Etheta/Ephi complex field or gain_db",
            "CST parameter screenshots and project file",
        ],
    }
    (OUT / "metadata_template.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    checklist = """# CST Level 1 export checklist

1. Use the coordinates in `sensor_layout_hemisphere_for_cst.csv`.
2. Export near-field complex Ex/Ey/Ez at 1.2 GHz.
3. Fill `nearfield_import_template.csv` or create an equivalent CSV with the same columns.
4. Export far-field Etheta/Ephi complex values or gain_db on theta/phi grid.
5. Keep `sample_id` identical between near-field and far-field files.
6. Run:

```powershell
python code\\check_cst_export.py --nearfield outputs\\cst_templates\\nearfield_import_template.csv
```

Template files intentionally contain blank field values and should fail numeric validation until CST values are filled.
Use `nearfield_demo_valid.csv` and `farfield_demo_valid.csv` only to test the Python interface; they are synthetic data, not CST evidence.
"""
    (OUT / "README_cst_templates.md").write_text(checklist, encoding="utf-8")
    print(f"CST templates written to {OUT}")


if __name__ == "__main__":
    main()
