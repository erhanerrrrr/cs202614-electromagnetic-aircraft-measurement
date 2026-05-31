# Level 1 CST 标准源冲刺交接单

用途：把下一轮 CST 标准源仿真从“知道要做什么”落到“谁做、导出什么、如何验收”。本交接单对应 `outputs/cst_level1_plan`、`code/merge_cst_level1_exports.py` 和 `code/run_cst_level1_batch_reconstruction.py`。

## 1. 本轮目标

当前测量面固定选择：半球面 2π 测点布局。CST 建模和导出均以 `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` 为唯一测点来源，半柱面只作为后续扩展备选，不进入本轮 Level 1 执行。

先完成两个必做标准源：

| sample_id | 源类型 | 方向 | 频点 | 优先级 |
|---|---|---:|---:|---|
| `L1_short_dipole_z_1p2G` | 短偶极子 | z | 1.2 GHz | required |
| `L1_halfwave_dipole_z_1p2G` | 半波振子 | z | 1.2 GHz | required |

通过条件：

- `python code\merge_cst_level1_exports.py --strict` 返回 0。
- `python code\run_cst_level1_batch_reconstruction.py --require-cases` 至少完成 2 个必做案例。
- 每个案例输出 `cst_reconstruction_metrics.json`、`cst_farfield_reconstruction_compare.png`、`equivalent_source_solution.csv`。
- 重建指标优先达到：相关系数 `>= 0.95`、主瓣误差 `<= 5 deg`、NMSE `<= 1e-2`。

## 2. 三人分工

| 角色 | 主责 | 输入 | 输出 |
|---|---|---|---|
| A：算法/验收 | 运行审计、重建、指标归档，判断是否能进入 Level 2 | CST 导出的 nearfield/farfield CSV | `outputs/cst_level1_merge_report`、`outputs/cst_reconstruction/<sample_id>` |
| B：CST 建模 | 建立标准源工程、布置 162 个测点、导出复数近场和远场 | `level1_case_manifest.csv`、`level1_source_manifest.csv`、`sensor_layout_hemisphere_for_cst.csv` | `data/cst_exports/level1/*.csv`、CST 工程截图 |
| C：文档/展示 | 保存过程截图、记录参数、把真实指标替换到报告和 PPT 草稿 | A 的指标、B 的截图 | 报告第 5/6/8 章证据、PPT 第 6/8 页素材 |

## 3. B 的 CST 导出清单

执行前先打开：

```text
outputs/cst_level1_workpack/README_level1_workpack.md
outputs/cst_level1_workpack/level1_cst_work_items.csv
outputs/cst_level1_workpack/case_cards/<sample_id>.md
outputs/cst_level1_plan/level1_case_manifest.csv
outputs/cst_level1_plan/level1_source_manifest.csv
outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv
```

每个案例导出两个标准复数文件：

```text
data/cst_exports/level1/<sample_id>_nearfield.csv
data/cst_exports/level1/<sample_id>_farfield.csv
```

如果 CST 只能导出幅值/相位，则先按 manifest 文件名导出：

```text
data/cst_exports/level1/<sample_id>_nearfield_phase.csv
data/cst_exports/level1/<sample_id>_farfield_phase.csv
```

然后由 A 运行 `code/normalize_cst_complex_columns.py` 转成标准实部/虚部格式。

## 4. A 的验收命令

每收到一批 CSV，先审计：

```powershell
python code\merge_cst_level1_exports.py
```

必做案例严格验收：

```powershell
python code\merge_cst_level1_exports.py --strict
```

审计通过后批量重建：

```powershell
python code\run_cst_level1_batch_reconstruction.py --require-cases
```

真实 CST 导出前，可用同形合成数据预演 A 的审计和批处理：

```powershell
python code\generate_synthetic_cst_level1_dataset.py
python code\merge_cst_level1_exports.py --manifest outputs\synthetic_cst_level1_dataset\level1_case_manifest.csv --report-dir outputs\synthetic_cst_level1_dataset\merge_report --out-dir outputs\synthetic_cst_level1_dataset\merged --strict-all
python code\run_cst_level1_batch_reconstruction.py --case-status outputs\synthetic_cst_level1_dataset\merge_report\level1_case_status.csv --out-root outputs\synthetic_cst_level1_dataset\reconstruction --batch-dir outputs\synthetic_cst_level1_dataset\reconstruction_batch --priority all --require-cases
```

该预演只验证文件组织、表格字段和批处理脚本，不能替代 B 的 CST 全波仿真结果。

若某案例失败，优先检查：

1. `sample_id` 和 `frequency_hz` 是否与 manifest 完全一致。
2. 坐标单位是否为 m，不是 mm。
3. 近场是否包含完整 `Ex/Ey/Ez` 或 `theta/phi` 极化。
4. 远场角度定义是否与导出表中 `theta_deg`、`phi_deg` 一致。
5. 相位单位是否为 deg/rad 且转换命令显式指定。

## 5. C 的证据归档

每个完成案例至少保存：

| 证据 | 建议位置 |
|---|---|
| CST 模型和源参数截图 | `submission/05_cst/screenshots/level1/<sample_id>_model.png` |
| 测点布局或 monitor 截图 | `submission/05_cst/screenshots/level1/<sample_id>_monitors.png` |
| 导出文件审计表 | `outputs/cst_level1_merge_report/level1_case_status.csv` |
| 重建对比图 | `outputs/cst_reconstruction/<sample_id>/cst_farfield_reconstruction_compare.png` |
| 指标 JSON/CSV | `outputs/cst_reconstruction/<sample_id>/cst_reconstruction_metrics.*` |

完成后把真实指标替换到 `docs/solution_report_draft.md` 的 Level 1 标准源部分，并在 `docs/final_submission_package_plan.md` 中更新“当前最短路径”状态。

## 6. 是否进入 Level 2

进入 Level 2 的最低条件：

- 两个 required 案例全部通过 `merge_cst_level1_exports.py --strict`。
- 至少一个案例达到重建指标门槛；若另一个失败，需要有明确原因和修正计划。
- 坐标单位、极化定义、相位单位三项已在报告中形成固定口径。

建议条件：

- 追加 `L1_short_dipole_x_1p2G` 和 `L1_short_dipole_y_1p2G`，用于排除 x/y/z 轴或极化方向错配。
