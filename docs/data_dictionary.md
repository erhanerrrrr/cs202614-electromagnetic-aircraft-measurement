# 数据字典与命名规范

版本：v0.1  
用途：统一 CST 导出、Python 处理、识别标签、重建指标和最终提交数据字段，避免 sample_id、频点、坐标和极化约定混乱。

## 1. 全局约定

| 项目 | 约定 |
|---|---|
| 坐标单位 | m |
| 频率单位 | Hz |
| 角度单位 | deg |
| 复数场 | 实部/虚部分列保存，禁止只保存幅值 |
| 坐标系 | x 为机身纵向，y 为横向，z 为高度方向 |
| 被测包络 | x in [-6, 6] m, y in [-5, 5] m, z in [0, 8] m |
| 测量面 | 13 m 上半球面，162 个空间测点 |
| 推荐近场分量 | Ex/Ey/Ez，由 Python 投影为 theta/phi |
| 文件编码 | UTF-8 with BOM 或 UTF-8 均可，Python 以 `utf-8-sig` 读取 |

若 CST 只能导出幅值/相位，可以先保存为 `e_mag/e_phase_deg` 或 `e_theta_mag/e_theta_phase_deg` 形式，再用 `code/normalize_cst_complex_columns.py` 转换成标准实部/虚部列。

## 2. sample_id 命名

| 阶段 | 格式 | 示例 |
|---|---|---|
| Level 1 标准源 | `L1_<source>_<orientation>_<freq>` | `L1_short_dipole_z_1p2G` |
| Level 2 多源 | `L2_<class_label>_<variant>` | `L2_comm_pair_000` |
| 合成 demo | `SYN_<class_label>_<variant>` | `SYN_radar_top_003` |
| Level 3 简化载体 | `L3_<airframe>_<class_label>_<variant>` | `L3_simple_airframe_mixed_avionics_000` |

同一个 sample_id 必须在 nearfield、farfield、labels 和报告图表中完全一致。

当前 CST 执行测量面固定为半球面 2π 布局，测点表为 `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv`。

## 3. nearfield 表

最低必需字段由 `code/cst_io.py` 校验：

| 字段 | 类型 | 单位/取值 | 是否必需 | 说明 |
|---|---|---|---|---|
| `sample_id` | string | - | 是 | 样本编号 |
| `sensor_id` | int | 0..N-1 | 是 | 测点编号，必须与坐标稳定对应 |
| `x_m` | float | m | 是 | 测点 x 坐标 |
| `y_m` | float | m | 是 | 测点 y 坐标 |
| `z_m` | float | m | 是 | 测点 z 坐标 |
| `frequency_hz` | float/int | Hz | 是 | 频点 |
| `polarization` | string | `Ex`, `Ey`, `Ez`, `theta`, `phi` | 是 | 场分量或投影极化 |
| `e_real` | float | V/m 或归一化场 | 是 | 电场复数实部 |
| `e_imag` | float | V/m 或归一化场 | 是 | 电场复数虚部 |
| `e_mag` | float | V/m 或归一化场 | 转换前可选 | 电场幅值，需配合 `e_phase_deg` 或 `e_phase_rad` |
| `e_phase_deg` | float | deg | 转换前可选 | 电场相位，转换后生成 `e_real/e_imag` |
| `e_phase_rad` | float | rad | 转换前可选 | 电场相位，转换后生成 `e_real/e_imag` |
| `theta_deg` | float | deg | 建议 | 测点球坐标 theta |
| `phi_deg` | float | deg | 建议 | 测点球坐标 phi |
| `source_config` | string | - | 建议 | 源组合，如 `comm_pair` |
| `carrier_model` | string | - | 建议 | `standard_source`, `level2_multisource_no_airframe` 等 |
| `working_state` | string | - | 建议 | 工作状态标签 |
| `cst_project` | string | - | 建议 | CST 工程文件名 |
| `monitor_name` | string | - | 建议 | CST 监视器名称 |

完整性要求：

- 每个 `(sample_id, frequency_hz, sensor_id, polarization)` 只能有一行。
- Ex/Ey/Ez 三分量或 theta/phi 双极化必须完整。
- 同一个 `sensor_id` 的坐标不能随 sample_id 或频点变化。

## 4. farfield 表

最低必需字段由 `code/cst_io.py` 校验：

| 字段 | 类型 | 单位/取值 | 是否必需 | 说明 |
|---|---|---|---|---|
| `sample_id` | string | - | 是 | 必须与 nearfield 对齐 |
| `theta_deg` | float | deg | 是 | 远场 theta |
| `phi_deg` | float | deg | 是 | 远场 phi |
| `frequency_hz` | float/int | Hz | 是 | 频点 |
| `e_theta_real` | float | - | 与 Etheta/Ephi 模式二选一 | Etheta 实部 |
| `e_theta_imag` | float | - | 与 Etheta/Ephi 模式二选一 | Etheta 虚部 |
| `e_phi_real` | float | - | 与 Etheta/Ephi 模式二选一 | Ephi 实部 |
| `e_phi_imag` | float | - | 与 Etheta/Ephi 模式二选一 | Ephi 虚部 |
| `e_theta_mag` | float | - | 转换前可选 | Etheta 幅值 |
| `e_theta_phase_deg` | float | deg | 转换前可选 | Etheta 相位 |
| `e_phi_mag` | float | - | 转换前可选 | Ephi 幅值 |
| `e_phi_phase_deg` | float | deg | 转换前可选 | Ephi 相位 |
| `gain_db` | float | dB | 与 power/复数场二选一 | 远场增益 |
| `power` | float | linear | 与 gain/复数场二选一 | 远场功率 |
| `source_config` | string | - | 建议 | 源组合 |
| `carrier_model` | string | - | 建议 | 模型类别 |
| `working_state` | string | - | 建议 | 工作状态 |
| `cst_project` | string | - | 建议 | CST 工程名 |
| `monitor_name` | string | - | 建议 | 远场监视器名称 |

完整性要求：

- 每个 `(sample_id, frequency_hz, theta_deg, phi_deg)` 只能有一行。
- nearfield 中出现的 sample_id 和 frequency_hz 必须在 farfield 中存在。

## 5. labels 表

用于 `code/run_cst_recognition.py`。

| 字段 | 类型 | 是否必需 | 说明 |
|---|---|---|---|
| `sample_id` | string | 是 | 对应 nearfield 中的 sample_id |
| `class_label` | string | 是 | 分类标签 |
| `source_config` | string | 建议 | 源组合编号 |
| `carrier_model` | string | 建议 | 模型类别 |
| `working_state` | string | 建议 | 工作状态 |
| `frequencies_hz` | string | 建议 | 以分号连接的频点列表 |

## 6. Level 2 manifest 表

由 `code/prepare_cst_level2_manifest.py` 生成。

## 6A. Level 1 manifest 表

由 `code/prepare_cst_level1_manifest.py` 生成。

### `level1_case_manifest.csv`

| 字段 | 说明 |
|---|---|
| `sample_id` | Level 1 样本编号 |
| `priority` | `required` / `recommended` / `optional` |
| `source_config` | 源配置，如 `short_dipole_z` |
| `source_type` | `short_dipole` 或 `halfwave_dipole` |
| `orientation_axis` | `x` / `y` / `z` |
| `frequency_hz` | 频点 |
| `cst_project` | 建议 CST 工程文件名 |
| `nearfield_monitor` | 近场监视器名称 |
| `farfield_monitor` | 远场监视器名称 |
| `nearfield_export` | 标准复数近场导出路径 |
| `farfield_export` | 标准复数远场导出路径 |
| `phase_format_nearfield_export` | 幅相格式近场导出路径 |
| `phase_format_farfield_export` | 幅相格式远场导出路径 |
| `expected_nearfield_rows` | 当前为 162 x 3 = 486 |
| `expected_farfield_rows` | 当前为 37 x 72 = 2664 |

### `level1_source_manifest.csv`

| 字段 | 说明 |
|---|---|
| `sample_id` | 样本编号 |
| `source_type` | 标准源类型 |
| `center_x_m`, `center_y_m`, `center_z_m` | 源中心位置 |
| `orientation_x`, `orientation_y`, `orientation_z` | 方向向量 |
| `length_m` | 建议源长度 |
| `feed_gap_m` | 建议馈电间隙 |
| `relative_amplitude` | 激励幅度 |
| `relative_phase_deg` | 激励相位 |
| `boundary_condition` | 建议边界条件 |
| `solver_note` | 求解器备注 |

### `level1_validation_targets.csv`

| 字段 | 说明 |
|---|---|
| `min_correlation` | 重建方向图相关系数下限 |
| `max_main_lobe_error_deg` | 主瓣误差上限 |
| `max_nmse` | NMSE 上限 |
| `must_check` | 失败时优先检查项 |

### `level1_case_status.csv`

由 `code/merge_cst_level1_exports.py` 生成。

| 字段 | 说明 |
|---|---|
| `sample_id` | 标准源案例编号 |
| `priority` | required/recommended/optional |
| `nearfield_file_status`, `farfield_file_status` | 标准实部/虚部导出文件读取状态 |
| `phase_nearfield_file_status`, `phase_farfield_file_status` | 幅相导出文件是否存在 |
| `expected_nearfield_rows`, `expected_farfield_rows` | manifest 给出的预期行数 |
| `nearfield_rows`, `farfield_rows` | 实际匹配 sample_id/frequency_hz 的行数 |
| `nearfield_ok`, `farfield_ok`, `pair_ok` | 字段级、数值级和 nearfield/farfield 配对校验结果 |
| `nearfield_complete`, `farfield_complete`, `case_complete` | 是否满足进入 Level 1 重建的完整性条件 |
| `nearfield_action`, `farfield_action` | 若只发现幅相文件，给出转换动作提示 |

### `level1_reconstruction_queue.csv`

| 字段 | 说明 |
|---|---|
| `sample_id` | 已完整的标准源案例 |
| `out_dir` | 建议重建输出目录 |
| `command` | 可直接执行的 `run_cst_reconstruction.py` 命令 |

### `level1_batch_reconstruction_results.csv`

由 `code/run_cst_level1_batch_reconstruction.py` 生成。

| 字段 | 说明 |
|---|---|
| `sample_id` | 已批量重建的标准源案例 |
| `priority` | 案例优先级 |
| `exit_code` | 单案例重建脚本返回码 |
| `status` | `ok` / `failed` / `dry_run` |
| `out_dir` | 单案例重建输出目录 |
| `nmse`, `correlation`, `main_lobe_error_deg` | 若重建成功，则从指标 JSON 聚合 |
| `metrics_json` | 单案例指标文件路径 |

### `outputs/cst_level1_workpack`

由 `code/prepare_cst_level1_workpack.py` 生成，用于 CST 主责执行半球面 Level 1 标准源建模。

| 文件 | 说明 |
|---|---|
| `level1_cst_work_items.csv` | 每个案例的源端点、monitor、导出路径、预期行数、验收阈值 |
| `level1_cst_export_checklist.csv` | 工程保存、nearfield/farfield 导出、审计、重建、截图归档核对项 |
| `case_cards/<sample_id>.md` | 单案例 CST 任务卡 |
| `level1_workpack_summary.json` | 案例数量、半球面测点来源、gate 命令 |

### `outputs/synthetic_cst_level1_dataset`

由 `code/generate_synthetic_cst_level1_dataset.py` 生成，是与 Level 1 manifest 同形的合成 CST 格式数据。

| 文件 | 说明 |
|---|---|
| `level1_case_manifest.csv` | 指向合成 nearfield/farfield 导出的 manifest 副本 |
| `exports/<sample_id>_nearfield.csv` | 每个标准源案例的 Ex/Ey/Ez 合成近场 |
| `exports/<sample_id>_farfield.csv` | 每个标准源案例的 Etheta/Ephi 合成远场 |
| `merged/all_nearfield.csv`, `merged/all_farfield.csv` | 由 Level 1 合并审计脚本生成的合并文件 |
| `validation_report.json` | 合并文件的 nearfield/farfield/pair 校验报告 |
| `reconstruction_batch/level1_batch_reconstruction_results.csv` | 6 个合成案例的批量重建指标 |

注意：该目录只证明表格接口、manifest 审计和批处理链路可用，不能作为真实 CST 全波仿真证据。

### `level2_case_manifest.csv`

| 字段 | 说明 |
|---|---|
| `sample_id` | Level 2 样本编号 |
| `class_label` | 识别类别 |
| `variant_index` | 幅相扰动变体编号 |
| `frequency_hz` | 频点 |
| `frequency_label` | 频点短标签 |
| `carrier_model` | 模型类别 |
| `working_state` | 工作状态 |
| `cst_project` | 建议 CST 工程文件名 |
| `nearfield_monitor` | 近场监视器名 |
| `farfield_monitor` | 远场监视器名 |
| `nearfield_export` | 单 sample nearfield 导出路径 |
| `farfield_export` | 单 sample farfield 导出路径 |
| `expected_nearfield_rows_per_frequency` | 每频点近场预期行数，当前为 162 x 3 = 486 |
| `expected_farfield_rows_per_frequency` | 每频点远场预期行数，当前为 19 x 36 = 684 |
| `status` | planned/exported/checked 等人工状态 |

### `level2_source_manifest.csv`

| 字段 | 说明 |
|---|---|
| `sample_id` | 样本编号 |
| `source_index` | 源编号 |
| `source_role` | 源角色 |
| `antenna_model` | CST 中的源/天线模型 |
| `x_m`, `y_m`, `z_m` | 源位置 |
| `orientation_x`, `orientation_y`, `orientation_z` | 源方向向量 |
| `relative_amplitude` | 相对幅度 |
| `relative_phase_deg` | 相对相位 |
| `implementation_note` | CST 操作备注 |

### `outputs/cst_level2_workpack`

由 `code/prepare_cst_level2_workpack.py` 生成，用于 CST 主责执行半球面 Level 2 多源多状态仿真。

| 文件 | 说明 |
|---|---|
| `level2_cst_sample_work_items.csv` | 48 个 sample/project 的汇总任务 |
| `level2_cst_frequency_tasks.csv` | 240 个 sample-frequency monitor/export 任务 |
| `level2_cst_export_checklist.csv` | 工程、源激励、nearfield/farfield 导出、审计和截图核对项 |
| `level2_class_summary.csv` | 每个 class_label 的样本数、源数范围和频点 |
| `case_cards/<sample_id>.md` | 单 sample CST 任务卡 |
| `level2_workpack_summary.json` | 案例数、频点任务数、半球面测点来源、gate 命令 |

## 7. 指标表

### 重建指标

| 字段 | 说明 |
|---|---|
| `nmse` | 归一化方向图均方误差，越小越好 |
| `correlation` | 方向图相关系数，越接近 1 越好 |
| `main_lobe_error_deg` | 主瓣方向误差 |
| `peak_error_db` | 峰值误差 |
| `sensor_points` | 空间测点数 |
| `measurement_channels` | 测量通道数，通常为测点数 x 极化数 |
| `lambda` | Tikhonov 正则化参数 |
| `snr_db` | 合成噪声信噪比 |

### 识别指标

| 字段 | 说明 |
|---|---|
| `accuracy` / `best_accuracy` | 分类准确率 |
| `macro_f1` / `best_macro_f1` | 宏平均 F1 |
| `precision` | 精确率 |
| `recall` | 召回率 |
| `confusion_matrix` | 混淆矩阵，行是真值，列是预测 |

## 8. 校验命令

```powershell
python code\normalize_cst_complex_columns.py --nearfield path\to\nearfield_phase.csv --farfield path\to\farfield_phase.csv --nearfield-out path\to\nearfield.csv --farfield-out path\to\farfield.csv --phase-unit deg
python code\check_cst_export.py --nearfield path\to\nearfield.csv --farfield path\to\farfield.csv
python code\merge_cst_level1_exports.py --strict
python code\run_cst_level1_batch_reconstruction.py
python code\merge_cst_level2_exports.py --strict
python code\run_cst_reconstruction.py --nearfield path\to\nearfield.csv --farfield path\to\farfield.csv --out-dir outputs\cst_reconstruction\case_name
python code\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
```

## 9. 常见错误

| 错误 | 表现 | 处理 |
|---|---|---|
| 频率单位写成 GHz | 校验通过但重建相位全错 | 统一写 Hz |
| 坐标单位混用 mm/m | 主瓣方向错误 | 导出后统一转换成 m |
| 只导出幅值 | 无法相干重建 | 必须导出实部/虚部或幅相并转换 |
| 相位列未注明单位 | 相干相位错误 | 文件名或列名使用 `_phase_deg` / `_phase_rad`，或转换时显式传 `--phase-unit` |
| sample_id 不一致 | merge 或 validate_pair 失败 | 以 manifest 为唯一来源 |
| sensor_id 坐标变化 | validate_nearfield 报错 | 固定测点表，不随样本改动 |
