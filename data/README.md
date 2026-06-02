# data 目录说明

本目录存放真实或主线 CST 导出数据，以及适合进入 GitHub 的小型算法输入表和诊断结果。大体量 CST 导出 CSV 默认由 `.gitignore` 排除，仓库中保留可复现脚本、索引、摘要和小型结果表。

## 子目录

| 子目录 | 说明 |
|---|---|
| `cst_exports/level1/` | Level 1 标准源 nearfield/farfield CSV、合并结果和 dropzone 说明。真实大 CSV 本地保留，默认不进入普通 Git。 |
| `cst_exports/level2/` | Level 2 多源、多状态样本 nearfield/farfield CSV、合并结果和 dropzone 说明。 |
| `cst_true_nearfield_workpack/` | CST 真近场 monitor 导出工作包、162 点采样壳层、宏骨架、对照清单和 reference self-check。 |
| `sampling_layouts/` | 162/120/81/48/32 点半球采样候选表、代理指标和当前 CST Level 1 诊断结果。 |

## 主要生成物

| 路径 | 生成命令 | 作用 |
|---|---|---|
| `sampling_layouts/hemisphere_sampling_candidates.csv` | `python code\optimize_sampling_layout.py` | 候选测点布局。 |
| `sampling_layouts/sampling_layout_summary.csv` | `python code\optimize_sampling_layout.py` | 候选布局代理指标摘要。 |
| `sampling_layouts/cst_level1_tradeoff/` | `python code\run_cst_sampling_tradeoff.py` | 通用等效源网格下的 CST Level 1 采样诊断。 |
| `sampling_layouts/cst_level1_center_source_check/` | `python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check` | 已知中心源先验下的数据路径 sanity check。 |
| `sampling_layouts/cst_level1_source_model_sweep/` | `python code\run_cst_source_model_sweep.py` | 等效源支撑和 Tikhonov 正则化扫描。 |
| `sampling_layouts/cst_level1_sparse_calibration/` | `python code\run_cst_sparse_reconstruction.py` | group-sparse 等效源校准结果。 |
| `sampling_layouts/cst_level1_convention_check/` | `python code\run_cst_level1_convention_check.py` | 相位、复共轭和极化约定诊断。 |
| `cst_true_nearfield_workpack/` | `python code\prepare_cst_true_nearfield_workpack.py` | 真近场 monitor 导出任务包和 FarfieldPlot-derived 基线对照入口。 |
| `cst_true_nearfield_workpack/reference_self_check/` | `python code\compare_true_nearfield_exports.py --true-nearfield data\cst_exports\level1\all_nearfield.csv --reference-nearfield data\cst_exports\level1\all_nearfield.csv --out-dir data\cst_true_nearfield_workpack\reference_self_check` | 对照脚本自检结果，不是新增 CST 物理证据。 |

## 使用约定

- 真实 CST 导出优先放在 `data/cst_exports/`，不要混入临时仿真缓存。
- 合成数据和大体量中间结果优先由脚本生成到 `outputs/`。
- 可协作的小型 CSV/JSON/README 摘要放入 `data/sampling_layouts/` 并进入 Git。
- CST 真近场 monitor 当前先提交工作包和对照自检；真实 monitor 大 CSV 后续仍按 `data/cst_exports/` 大文件策略处理。
- 如后续需要长期共享大 CST 文件，建议启用 Git LFS、GitHub Release 或网盘；仓库中只保留索引、校验摘要和复现命令。
