# data 目录说明

本目录存放真实或当前主线 CST 导出数据，以及可进入 GitHub 的小型算法输入表。它是 Python 重建、识别和校验脚本的主要输入区。

## 子目录

| 子目录 | 说明 |
|---|---|
| `cst_exports/level1/` | Level 1 标准源 nearfield/farfield CSV、合并结果与 dropzone 说明。大型 CSV 默认不进入普通 Git。 |
| `cst_exports/level2/` | Level 2 多源多状态样本 nearfield/farfield CSV、合并结果与 dropzone 说明。大型 CSV 默认不进入普通 Git。 |
| `sampling_layouts/` | 162/120/81/48/32 点半球采样候选表和代理验证指标，可进入 GitHub 用于队友协作。 |

## 使用约定

- 真实 CST 导出优先放在 `data/cst_exports/`，不要混入临时仿真缓存。
- 合成数据和中间结果优先由脚本生成到 `outputs/`。
- 少测点采样候选由 `python code\optimize_sampling_layout.py` 生成到 `data/sampling_layouts/`。
- 大体量数据如需长期协作，建议后续启用 Git LFS 或发布到 Release/网盘，只在仓库保留索引和校验摘要。
