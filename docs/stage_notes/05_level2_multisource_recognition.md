# S05 Level 2 多源多状态识别说明

## 做了什么

完成 Level 2 多源多状态执行清单、源配置、标签表、半球面 CST 建模任务包、批量合并审计脚本、合成 CST 格式识别数据和识别/删减验证脚本。

## 为什么这样做

赛题要求不仅要重建场，还要辨识空间-频谱特征。Level 2 用 4 类工作状态、48 个样本、5 个频点构成识别任务，验证算法能否从半球面近场复数数据中提取稳定特征。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/prepare_cst_level2_manifest.py` | 生成 Level 2 多源多状态 manifest | 固定 48 个样本和 240 个频点任务 |
| `outputs/cst_level2_plan` | case manifest、source manifest、labels | CST 主责和识别训练输入 |
| `code/prepare_cst_level2_workpack.py` | 生成半球面 Level 2 CST 任务包 | 分解为 48 张样本卡和 240 个频点任务 |
| `outputs/cst_level2_workpack` | Level 2 建模任务包 | CST 主责按 sample 执行 |
| `code/merge_cst_level2_exports.py` | 合并并审计 Level 2 导出 | 真实导出后运行 |
| `outputs/cst_level2_merge_report` | 当前缺漏报告 | 显示真实完整样本仍为 0 |
| `code/generate_synthetic_cst_dataset.py` | 生成合成 CST 格式多源数据 | 预演识别链路 |
| `code/run_cst_recognition.py` | 空-频-极化特征提取和识别 | 真实 Level 2 合并后运行 |
| `code/run_cst_recognition_ablation.py` | 测点/频点删减验证 | 证明少测点或少频点鲁棒性 |
| `outputs/cst_execution_logs/level2_execution_log.csv` | 真实 CST Level 2 执行日志模板 | 记录每个样本的工程、导出、合并和识别准备状态 |

## 验证方式

```powershell
python code\prepare_cst_level2_manifest.py
python code\prepare_cst_level2_workpack.py
python code\merge_cst_level2_exports.py
python code\generate_synthetic_cst_dataset.py
python code\run_cst_recognition.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_demo
python code\run_cst_recognition_ablation.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_ablation
python code\prepare_cst_execution_log_templates.py
```

## 当前不足

- 真实 Level 2 CST nearfield/farfield 尚未导出。
- 当前 accuracy=1.0 来自合成 demo，不能作为最终识别证据。

## 下一步

1. Level 1 required 通过后，按 `outputs/cst_level2_workpack/case_cards` 分批跑 48 个样本。
2. 运行 `python code\merge_cst_level2_exports.py --strict`。
3. 运行真实识别和删减验证脚本。
