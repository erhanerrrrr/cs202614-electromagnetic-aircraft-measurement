# code 目录说明

本目录存放项目可运行源代码、CST/Python 接口脚本、数据处理脚本、报告生成脚本和早期工作计划生成脚本。

## 主要内容

| 内容 | 说明 |
|---|---|
| `em_core.py` | 半球测点、球坐标基、等效源传播矩阵、Tikhonov 重建、远场计算与指标函数。 |
| `optimize_sampling_layout.py` | 生成 162/120/81/48/32 点半球非冗余采样候选，并输出几何、矩阵、重建和分类代理指标。 |
| `run_cst_sampling_tradeoff.py` | 用当前 CST Level 1 near/far-field 导出数据评估候选采样布局，生成可提交的诊断表。 |
| `run_cst_source_model_sweep.py` | 扫描 Level 1 等效源网格和正则化参数，定位反演模型校准瓶颈。 |
| `run_baseline.py` | 合成数据 baseline：测点布局、少测点选择、远场重建和识别基线。 |
| `cst_io.py`, `check_cst_export.py` | CST 导出 CSV 读取、字段归一化、近/远场数据校验和坐标投影。 |
| `prepare_cst_*.py`, `run_cst_*.py`, `export_cst_*.py` | CST 建模任务包、宏模板、本机 CST API 工程生成、求解与导出接口。 |
| `merge_cst_*.py`, `run_cst_reconstruction.py` | CST 数据合并、等效源反演和远场外推。 |
| `run_cst_recognition*.py` | 空域、频率、极化特征提取，分类识别与消融实验。 |
| `build_*.py` | 报告、PPT、提交包、审查和总控看板等自动生成脚本。 |
| `legacy_workplan/` | 早期工作计划文档生成脚本，保留用于追溯。 |

## 常用入口

```powershell
python code\run_baseline.py
python code\optimize_sampling_layout.py
python code\run_cst_sampling_tradeoff.py
python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check
python code\run_cst_source_model_sweep.py
python code\prepare_cst_templates.py
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
python code\run_cst_level1_batch_reconstruction.py
python code\run_cst_recognition.py
```

脚本默认以项目根目录为 `ROOT`，请在项目根目录执行命令。

## 本轮新增

`optimize_sampling_layout.py` 对应未来工作方案中的 G2“采样方案升级”。它会生成可进入 GitHub 的小型候选测点表：

- `data/sampling_layouts/hemisphere_sampling_candidates.csv`
- `data/sampling_layouts/sampling_layout_summary.csv`
- `data/sampling_layouts/sampling_layout_summary.json`

`run_cst_sampling_tradeoff.py` 对应 G3“真实 CST 数据校准”。它会生成：

- `data/sampling_layouts/cst_level1_tradeoff/`
- `data/sampling_layouts/cst_level1_center_source_check/`
- `data/sampling_layouts/cst_level1_source_model_sweep/`

设计依据见 `docs/nonredundant_sampling_design.md`，CST 校准结论见 `docs/cst_level1_sampling_calibration_findings.md`。
