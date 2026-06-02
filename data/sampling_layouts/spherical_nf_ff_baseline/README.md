# Spherical NF-FF Sanity Baseline

This directory stores a lightweight spherical near-field to far-field sanity
baseline for the current CST Level 1 exports.

The method fits the tangential near-field samples, `Etheta` and `Ephi`, with
independent scalar spherical-harmonic expansions and evaluates the fitted field
on the far-field angular grid. This is a useful convention and data-path check,
but it is not a full vector spherical-wave expansion.

## Inputs

| Item | Path |
|---|---|
| Near field | `data\cst_exports\level1\all_nearfield.csv` |
| Far field | `data\cst_exports\level1\all_farfield.csv` |

## Best Setting

| Field | Value |
|---|---|
| Lmax | `4` |
| Lambda | `0e+00` |
| Modes per component | `24` |
| Status | `strict_pass` |
| Min Corr | `0.9990` |
| Max NMSE | `9.2604e-04` |
| Max main-lobe error / deg | `0.00` |
| Max near-field fit relative error | `2.5766e-02` |

## Top Settings

| Lmax | Lambda | Modes | Status | Min Corr | Max NMSE | Max lobe error / deg | Max NF fit error | Max condition |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 4 | 0e+00 | 24 | strict_pass | 0.9990 | 9.2604e-04 | 0.00 | 2.5766e-02 | 1.051e+02 |
| 4 | 1e-10 | 24 | strict_pass | 0.9990 | 9.2604e-04 | 0.00 | 2.5766e-02 | 1.051e+02 |
| 4 | 1e-08 | 24 | strict_pass | 0.9990 | 9.2604e-04 | 0.00 | 2.5766e-02 | 1.051e+02 |
| 4 | 1e-06 | 24 | strict_pass | 0.9990 | 9.2580e-04 | 0.00 | 2.5766e-02 | 1.051e+02 |
| 6 | 0e+00 | 48 | strict_pass | 0.9995 | 1.3790e-03 | 0.00 | 1.1791e-02 | 4.531e+03 |
| 6 | 1e-10 | 48 | strict_pass | 0.9995 | 1.3790e-03 | 0.00 | 1.1791e-02 | 4.531e+03 |
| 6 | 1e-08 | 48 | strict_pass | 0.9995 | 1.3786e-03 | 0.00 | 1.1791e-02 | 4.531e+03 |
| 6 | 1e-06 | 48 | strict_pass | 0.9995 | 1.3439e-03 | 0.00 | 1.1791e-02 | 4.531e+03 |
| 10 | 1e-06 | 120 | strict_pass | 0.9999 | 1.6088e-04 | 0.00 | 2.7559e-03 | 1.169e+16 |
| 5 | 1e-10 | 35 | strict_pass | 0.9990 | 6.7071e-04 | 4.78 | 1.9526e-02 | 6.346e+02 |
| 5 | 0e+00 | 35 | strict_pass | 0.9990 | 6.7071e-04 | 4.78 | 1.9526e-02 | 6.346e+02 |
| 5 | 1e-08 | 35 | strict_pass | 0.9990 | 6.7071e-04 | 4.78 | 1.9526e-02 | 6.346e+02 |

## Best-Setting Case Results

| Sample | Frequency Hz | Corr | NMSE | Lobe error / deg | NF fit error | True peak theta/phi | Pred peak theta/phi |
|---|---:|---:|---:|---:|---:|---|---|
| L1_halfwave_dipole_z_1p2G | 1200000000 | 0.9997 | 3.0115e-04 | 0.00 | 1.9084e-02 | (88.0, 315.0) | (88.0, 315.0) |
| L1_short_dipole_z_1p2G | 1200000000 | 0.9990 | 9.2604e-04 | 0.00 | 2.5766e-02 | (88.0, 185.0) | (88.0, 185.0) |

## Reading

- The angular spherical-harmonic baseline passes the current Level 1 sanity gate.
- This supports the coordinate, polarization, and far-field comparison chain for
  the current Level 1 data path.
- It still does not prove reduced 120/81/48/32 sampling layouts; those must be
  rerun after the full-grid physical baseline is frozen.

## Boundary

The current near-field input is still FarfieldPlot-derived angular data. Once
true CST near-field monitor exports are available, rerun this script on that
authoritative table before upgrading the wording in the report.
