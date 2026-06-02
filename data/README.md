# data 目录说明

本目录存放真实或当前主线 CST 导出数据，以及可进入 GitHub 的小型算法输入表。它是 Python 重建、识别和校验脚本的主要输入区。

## 子目录

| 子目录 | 说明 |
|---|---|
| `cst_exports/level1/` | Level 1 标准源 nearfield/farfield CSV、合并结果与 dropzone 说明。大型 CSV 默认不进入普通 Git。 |
| `cst_exports/level2/` | Level 2 多源多状态样本 nearfield/farfield CSV、合并结果与 dropzone 说明。大型 CSV 默认不进入普通 Git。 |
| `sampling_layouts/` | 162/120/81/48/32 点半球采样候选表、代理验证指标和当前 CST Level 1 采样诊断结果。 |

## 使用约定

- 真实 CST 导出优先放在 `data/cst_exports/`，不要混入临时仿真缓存。
- 合成数据和中间结果优先由脚本生成到 `outputs/`。
- 少测点采样候选由 `python code\optimize_sampling_layout.py` 生成到 `data/sampling_layouts/`。
- CST 采样诊断由 `python code\run_cst_sampling_tradeoff.py` 生成到 `data/sampling_layouts/cst_level1_tradeoff/`。
- Level 1 标准源校准检查由 `python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check` 生成。
- Level 1 等效源模型扫描由 `python code\run_cst_source_model_sweep.py` 生成到 `data/sampling_layouts/cst_level1_source_model_sweep/`。
- 大体量数据如需长期协作，建议后续启用 Git LFS 或发布到 Release/网盘，只在仓库保留索引和校验摘要。
