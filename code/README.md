# code 目录说明

本目录存放项目可运行源码、CST/Python 接口脚本、数据处理脚本、报告生成脚本和早期工作计划生成脚本。

## 主要内容

| 内容 | 说明 |
|---|---|
| `em_core.py` | 半球面测点、球坐标基、等效源传播矩阵、Tikhonov 重建、远场计算与指标函数。 |
| `run_baseline.py` | 合成数据 baseline：测点布局、少测点选择、远场重建和识别基线。 |
| `cst_io.py`, `check_cst_export.py` | CST 导出 CSV 读取、字段归一化和近/远场数据校验。 |
| `prepare_cst_*.py`, `run_cst_*.py`, `export_cst_*.py` | CST 建模任务包、宏模板、本机 CST API 工程生成、求解与导出接口。 |
| `merge_cst_*.py`, `run_cst_reconstruction.py` | CST 数据合并、等效源反演和远场外推。 |
| `run_cst_recognition*.py` | 空-频-极化特征提取、分类识别与消融实验。 |
| `build_*.py` | 报告、PPT、提交包、审计、总控看板等自动生成脚本。 |
| `legacy_workplan/` | 早期工作计划文档生成脚本，保留用于追溯。 |

## 常用入口

```powershell
python code\run_baseline.py
python code\prepare_cst_templates.py
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
python code\run_cst_level1_batch_reconstruction.py
python code\run_cst_recognition.py
```

脚本默认以项目根目录为 `ROOT`，因此请在项目根目录执行命令。
