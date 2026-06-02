# code 目录说明

本目录存放项目可运行源代码、CST/Python 接口脚本、数据处理脚本、算法实验脚本和报告生成脚本。建议在项目根目录执行命令。

## 核心算法与数据接口

| 文件 | 作用 |
|---|---|
| `em_core.py` | 半球测点、球坐标基、等效源传播矩阵、Tikhonov 反演、远场外推与指标函数。 |
| `cst_io.py` | CST near/far-field CSV 读取、字段校验、Ex/Ey/Ez 到 theta/phi 投影、样本频点配对。 |
| `check_cst_export.py` | 检查 CST 导出表是否满足 Python 重建链路要求。 |
| `normalize_cst_complex_columns.py` | 统一 CST 复数字段命名与格式。 |

## 采样与反演实验

| 文件 | 作用 |
|---|---|
| `optimize_sampling_layout.py` | 生成 162/120/81/48/32 点半球非冗余采样候选，并输出几何、矩阵、重建和分类代理指标。 |
| `run_cst_sampling_tradeoff.py` | 用当前 CST Level 1 near/far-field 导出评估候选采样布局。 |
| `run_cst_source_model_sweep.py` | 扫描 Level 1 等效源支撑和 Tikhonov 正则化，定位源模型校准瓶颈。 |
| `run_cst_sparse_reconstruction.py` | 用 group-sparse FISTA/ElasticNet 思路检查通用等效源网格的能量泄漏问题。 |
| `run_cst_level1_convention_check.py` | 诊断相位符号、复共轭、theta/phi 极化约定是否造成 Level 1 反演瓶颈。 |
| `compare_true_nearfield_exports.py` | 对比 CST 真近场 monitor 导出与当前 FarfieldPlot-derived nearfield 基线。 |
| `run_spherical_nf_ff_baseline.py` | 用切向球谐拟合建立轻量 NF-FF/SWE sanity baseline，独立检查角度、极化和远场比较链路。 |
| `run_cst_reconstruction.py` | CST 数据等效源反演与远场外推入口。 |
| `run_reconstruction_robustness.py` | 重建鲁棒性实验。 |

## CST 工作流脚本

| 文件 | 作用 |
|---|---|
| `prepare_cst_templates.py`、`prepare_cst_macro_templates.py` | 生成 CST 建模和导出宏模板。 |
| `prepare_cst_level1_workpack.py`、`prepare_cst_level2_workpack.py` | 生成 Level 1/2 CST 执行任务包。 |
| `prepare_cst_true_nearfield_workpack.py` | 生成 CST 真近场 monitor 导出工作包、采样壳层、宏骨架和对照清单。 |
| `merge_cst_level1_exports.py`、`merge_cst_level2_exports.py` | 合并 CST 导出的 near/far-field 数据。 |
| `run_cst_solver_project.py`、`export_cst_farfield_results.py` | 本机 CST 求解和结果导出辅助入口。 |

## 识别与报告生成

| 文件 | 作用 |
|---|---|
| `run_cst_recognition.py`、`run_cst_recognition_ablation.py` | 空域、频率、极化等特征提取与分类识别实验。 |
| `run_cst_structure_comparison.py` | 结构/安装影响对比实验。 |
| `build_*.py` | 报告、PPT、提交包、仪表盘和审查材料生成脚本。 |

## 常用命令

```powershell
python code\optimize_sampling_layout.py
python code\run_cst_sampling_tradeoff.py
python code\run_cst_sampling_tradeoff.py --level1-center-source-grid --out-dir data\sampling_layouts\cst_level1_center_source_check
python code\run_cst_source_model_sweep.py
python code\run_cst_sparse_reconstruction.py
python code\run_cst_level1_convention_check.py
python code\prepare_cst_true_nearfield_workpack.py
python code\compare_true_nearfield_exports.py --true-nearfield data\cst_exports\level1\all_nearfield.csv --reference-nearfield data\cst_exports\level1\all_nearfield.csv --out-dir data\cst_true_nearfield_workpack\reference_self_check
python code\run_spherical_nf_ff_baseline.py
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
python code\run_cst_recognition.py
```

## 当前重点

G2 已生成非冗余半球采样候选。G3 正在校准真实 CST Level 1 数据链：中心源先验和轻量球谐 NF-FF baseline 共同证明角度/极化/比较链路可信，通用等效源网格仍未达到最终采样证明要求；下一步应补 CST 真近场 monitor 实测，并推进 Huygens/结构先验。
