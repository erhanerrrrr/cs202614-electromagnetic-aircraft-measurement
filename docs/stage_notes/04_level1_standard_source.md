# S04 Level 1 标准源说明

## 做了什么

完成 Level 1 标准源阶段的执行清单、源参数、验证阈值、半球面 CST 建模任务包、导出审计脚本、批量重建脚本，以及同形合成闭环预演。

## 为什么这样做

Level 1 是整个赛题的校准关卡。只有短偶极子和半波振子这类标准源在 CST 中能被正确导出、校验和重建，后续 Level 2 多源识别才有可信基础。

本阶段分为两类证据：

- 执行证据：manifest、workpack、case cards，指导 CST 建模。
- 管线证据：synthetic Level 1 数据，证明 Python 审计和批量重建链路能跑通。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/prepare_cst_level1_manifest.py` | 生成 Level 1 标准源 manifest | 固定 sample_id、源参数和导出文件名 |
| `outputs/cst_level1_plan` | 标准源执行清单、源参数、验证阈值 | CST 主责建模输入 |
| `code/prepare_cst_level1_workpack.py` | 生成半球面建模任务包 | 生成单案例任务卡和核对表 |
| `outputs/cst_level1_workpack` | CST 主责任务包 | 逐案例建模和截图归档 |
| `code/merge_cst_level1_exports.py` | 审计 Level 1 导出是否完整 | 真实 CST 文件到位后运行 |
| `code/run_cst_level1_batch_reconstruction.py` | 批量重建完整案例 | 审计通过后运行 |
| `outputs/cst_level1_merge_report` | 当前真实导出缺漏报告 | 显示 required 尚未完成 |
| `outputs/synthetic_cst_level1_dataset` | 同形合成闭环验证 | 证明接口和批处理可用 |
| `docs/level1_cst_sprint_handoff.md` | 三人冲刺交接单 | 分工和执行 gate |
| `outputs/cst_execution_logs/level1_execution_log.csv` | 真实 CST 执行日志模板 | 记录每个 required/recommended 案例的运行、导出和重建结果 |

## 验证方式

```powershell
python code\prepare_cst_level1_manifest.py
python code\prepare_cst_level1_workpack.py
python code\merge_cst_level1_exports.py
python code\generate_synthetic_cst_level1_dataset.py
python code\merge_cst_level1_exports.py --manifest outputs\synthetic_cst_level1_dataset\level1_case_manifest.csv --report-dir outputs\synthetic_cst_level1_dataset\merge_report --out-dir outputs\synthetic_cst_level1_dataset\merged --strict-all
python code\run_cst_level1_batch_reconstruction.py --case-status outputs\synthetic_cst_level1_dataset\merge_report\level1_case_status.csv --out-root outputs\synthetic_cst_level1_dataset\reconstruction --batch-dir outputs\synthetic_cst_level1_dataset\reconstruction_batch --priority all --require-cases
python code\prepare_cst_execution_log_templates.py
```

## 当前不足

- 真实 CST required 案例还没有导出，`required_complete=false`。
- 缺 CST 工程文件、模型截图、monitor 截图和真实重建指标。

## 下一步

1. 按 `outputs/cst_level1_workpack/case_cards` 完成两个 required 案例。
2. 运行 `python code\merge_cst_level1_exports.py --strict`。
3. 运行 `python code\run_cst_level1_batch_reconstruction.py --require-cases`。
