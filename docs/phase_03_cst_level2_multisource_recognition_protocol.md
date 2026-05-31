# G4/G6：CST Level 2 多源多状态识别实验规程

版本：v0.1  
目标：在 Level 1 标准源闭环通过后，构建可用于“空间-频谱辐射特征辨识”的 CST 多源、多频、多状态数据集，并接入 `code/run_cst_recognition.py` 与 `code/run_cst_recognition_ablation.py`，形成准确率、F1、混淆矩阵和测点/频点删减对照证据。

## 1. 与评分项的关系

| 评分要求 | Level 2 实验响应 | 证据文件 |
|---|---|---|
| 覆盖 2π 半球/半柱空间 | 继续使用 13 m 半球面 162 测点 | `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` |
| 三维场重建与少测点 | Level 2 数据可继续接入等效源重建，并做 100%/75%/50%/25% 测点对比 | `code/run_cst_reconstruction.py` |
| 空间频率特征识别 >= 85% | 四类源状态、五个频点、多极化近场特征分类 | `code/run_cst_recognition.py` |
| 测试方案完整性 | sample_id、源表、频点表、导出字段、校验命令完整 | `outputs/cst_level2_plan` |

## 2. 实验对象与类别

先不加入复杂机体，只做“多源无载体”版本，用于识别算法和数据接口校准。通过后再加入 Level 3 简化航空载体。

| 类别 | 物理含义 | 源数量 | 典型位置 |
|---|---|---:|---|
| `comm_pair` | 左右通信链路源同时工作 | 2 | 左后/右前中高度 |
| `radar_top` | 顶部前后雷达/告警类源 | 2 | 机体顶部前后 |
| `mixed_avionics` | 导航、链路、信标混合 | 3 | 腹部、顶部、侧向 |
| `multi_state_on` | 多设备同时工作强耦合状态 | 3 | 顶部、腹部、中心 |

默认使用 12 个幅相扰动变体，每类 12 个样本，共 48 个 sample_id。每个 sample_id 在 5 个频点上导出近场与远场。

## 3. 频点与测量面

频点：

```text
0.90 GHz, 1.05 GHz, 1.20 GHz, 1.35 GHz, 1.50 GHz
```

测量面：

- 13 m 上半球面。
- 162 个空间测点。
- CST 导出 Ex/Ey/Ez 复数电场。
- Python 统一投影为 theta/phi 双极化。

远场真值：

- theta：建议 2 deg 到 88 deg。
- phi：0 deg 到 360 deg。
- 当前 manifest 默认 19 x 36 网格，真实报告可按算力提升到 37 x 72。

## 4. 数据清单生成

运行：

```powershell
python code\prepare_cst_level2_manifest.py
```

输出目录：

```text
outputs/cst_level2_plan
```

核心文件：

| 文件 | 用途 |
|---|---|
| `level2_case_manifest.csv` | 每个 sample_id/频点的 CST 工程、监视器、导出文件名和预期行数 |
| `level2_source_manifest.csv` | 每个 sample_id 内各辐射源的位置、方向、相对幅度和相位 |
| `level2_labels.csv` | 识别模型使用的 sample_id 到 class_label 映射 |
| `level2_manifest_summary.json` | 样本数、频点、测点、网格等摘要 |
| `README_level2_manifest.md` | CST 执行交接说明 |

## 5. CST 建模与导出规则

### 5.1 工程组织

每个 `sample_id` 对应一个可复制的 CST 工程：

```text
CST_L2_<class_label>_<variant_index>.cst
```

若 CST 支持参数扫描，可用一个工程完成同类别 12 个变体；若不方便参数化，则复制工程并按 `level2_source_manifest.csv` 改源参数。

### 5.2 源实现建议

初期采用理想偶极子、小离散端口或短线天线作为等效辐射源。每个源需要固定：

- 位置：`x_m, y_m, z_m`。
- 方向：`orientation_x, orientation_y, orientation_z`。
- 相对幅度：`relative_amplitude`。
- 相对相位：`relative_phase_deg`。

源之间的相对幅相必须记录；如果 CST 只支持端口激励幅相表，则按 `source_index` 对应端口编号。

### 5.3 导出文件

每个 sample_id 最终应形成两个 CSV：

```text
data/cst_exports/level2/<sample_id>_nearfield.csv
data/cst_exports/level2/<sample_id>_farfield.csv
```

当所有 sample_id 导出完成后，再合并为：

```text
data/cst_exports/level2/all_nearfield.csv
data/cst_exports/level2/all_farfield.csv
```

近场字段必须满足 `code/check_cst_export.py`，远场字段必须含 Etheta/Ephi 复数值或 gain/power。

### 5.4 批量合并与缺漏定位

CST 导出通常会产生几十个 sample_id 文件，禁止手工复制粘贴拼表。导出后运行：

```powershell
python code\merge_cst_level2_exports.py
```

该脚本会读取 `outputs/cst_level2_plan/level2_case_manifest.csv`，检查每个计划文件是否存在、每个频点行数是否满足预期，并在文件齐全时自动生成：

```text
data/cst_exports/level2/all_nearfield.csv
data/cst_exports/level2/all_farfield.csv
```

缺漏报告位于：

| 文件 | 用途 |
|---|---|
| `outputs/cst_level2_merge_report/level2_sample_status.csv` | 按 sample_id 定位缺文件、校验失败或不完整样本 |
| `outputs/cst_level2_merge_report/level2_frequency_completeness.csv` | 按 sample_id/频点定位 nearfield/farfield 行数缺漏 |
| `outputs/cst_level2_merge_report/level2_merge_summary.json` | 汇总完整样本数、合并行数和下一步命令 |

正式进入识别前，使用严格模式：

```powershell
python code\merge_cst_level2_exports.py --strict
```

严格模式必须通过后，才允许把 `all_nearfield.csv` 作为正式识别输入。

## 6. 校验与识别命令

单样本校验：

```powershell
python code\check_cst_export.py `
  --nearfield data\cst_exports\level2\L2_comm_pair_000_nearfield.csv `
  --farfield data\cst_exports\level2\L2_comm_pair_000_farfield.csv
```

全部样本识别：

```powershell
python code\run_cst_recognition.py `
  --nearfield data\cst_exports\level2\all_nearfield.csv `
  --labels outputs\cst_level2_plan\level2_labels.csv `
  --out-dir outputs\cst_recognition_level2
```

测点/频点删减验证：

```powershell
python code\run_cst_recognition_ablation.py `
  --nearfield data\cst_exports\level2\all_nearfield.csv `
  --labels outputs\cst_level2_plan\level2_labels.csv `
  --out-dir outputs\cst_recognition_level2_ablation
```

## 7. 通过判据

Level 2 通过后，报告中应具备：

1. CST 多源模型截图和源位置图。
2. `check_cst_export.py` 的 `ok: True` 校验结果。
3. 识别准确率 >= 0.85，且给出 macro F1。
4. 混淆矩阵能够说明哪些状态容易混淆。
5. 至少一个测点删减结果，例如 50% 测点仍能达到或接近 0.85。
6. 说明合成 demo 与 CST 真实仿真的边界：demo 只验证接口，正式指标以 CST 导出为准。

## 8. 三人分工技术细节

| 角色 | 当前阶段任务 | 技术细节 | 交付物 |
|---|---|---|---|
| A：算法/重建主责 | 维护 Python 管线 | 校验 Level 2 nearfield/farfield，必要时调正则化、测点删减和特征维度 | 识别 metrics、混淆矩阵、ablation 曲线 |
| B：CST 主责 | 执行 Level 2 建模与导出 | 按 `level2_source_manifest.csv` 配置源位置、方向、幅相；按 `level2_case_manifest.csv` 建监视器 | `.cst` 工程、nearfield/farfield CSV、模型截图 |
| C：数据/报告主责 | 维护样本命名和实验记录 | 核对 sample_id、频点、标签、截图编号；把结果写入报告第 7/8/9 章 | 数据记录表、报告段落、PPT 图表素材 |

## 9. 进入 Level 3 的条件

满足以下条件后再加入简化航空载体：

- Level 1 标准源重建通过。
- Level 2 多源识别准确率达到 85% 以上。
- Level 2 数据能在 50% 或 75% 测点下保持可解释的识别结果。
- 文件命名和 sample_id 管理无错误。

Level 3 目标是证明机身、机翼、尾翼和安装效应会改变空间辐射指纹，而不是重新调试基础数据接口。
