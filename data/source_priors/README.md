# source_priors 目录说明

本目录存放反演算法使用的结构化源先验。它回答的是“等效源或等效电流允许分布在哪里、每个位置有哪些未知量”，不同于 `data/sampling_layouts/` 的“测量点选在哪里”。

## 子目录

| 子目录 | 说明 |
|---|---|
| `huygens_surface/` | Huygens 面源先验节点表、法向/切向基、面积权重、四复未知量合同和摘要。 |

## 使用约定

- 这里的 CSV/JSON 是小型协作输入，可以进入 GitHub。
- 它们不是 CST 原始导出，也不是最终重建结果。
- 后续若新增贴体面、机翼/机身分区面或多频共享支撑先验，应在本目录下新增子目录并附 README。

## 当前生成命令

```powershell
python code\prepare_huygens_surface_prior.py
```

## 当前 baseline 入口

```powershell
python code\run_cst_huygens_baseline.py
```

该脚本读取 `huygens_surface/level1_local_sphere_r0p35_nodes.csv` 并输出
`data/sampling_layouts/cst_level1_huygens_baseline/`。当前结果仍为
`diagnostic_only`，所以它是面源矩阵调试证据，不是最终少测点采样证明。
