# S19 CST Level 2 full48 recognition

## 做了什么

本阶段把 Level 2 从 8 个 pilot 样本扩展到 48/48 个 CST-derived full48 样本，并完成严格合并、总表校验、识别和测点/频点消融。

完成事项：

1. 将 `code/export_cst_level2_superposed_results.py` 从单样本导出扩展为批量模式，支持 `--all-samples`、`--missing-only`、`--sample-ids` 和 `--limit`。
2. 用本机 CST API 打开已求解的 x/y/z element 工程，批量导出剩余 40 个 Level 2 样本。
3. 运行 `python code\merge_cst_level2_exports.py --strict`，确认 48 个计划样本全部完整。
4. 运行 full48 nearfield/farfield 总表校验。
5. 运行 full48 识别和 full48 测点/频点消融。
6. 修正识别脚本输出说明，使其按输入路径区分 synthetic/demo 与 `data/cst_exports` 当前导出表。
7. 更新 scorecard、completion audit、README、复现命令、项目文件索引和提交索引。

## 为什么这样做

G3 的要求不是只证明单个 pilot 可行，而是要证明 Level 2 多源多状态数据完整并可训练识别模型。上阶段 8 个 pilot 已经证明了 CST element-library 叠加链路可运行；本阶段继续扩展到 manifest 中全部 48 个样本，让识别准确率、混淆矩阵和删减实验拥有完整样本支撑。

同时，批量导出模式避免了每个样本重复打开/关闭 CST 工程，减少接口开销和人工操作误差。

## 产物有哪些

| 文件/目录 | 意义 |
|---|---|
| `code/export_cst_level2_superposed_results.py` | 支持单样本和批量导出；批量时一次打开 element 工程并循环导出缺失样本。 |
| `outputs/cst_level2_superposed_export/batch_smoke_one_summary.json` | 批量模式冒烟测试，导出 `L2_comm_pair_002`。 |
| `outputs/cst_level2_superposed_export/level2_remaining_missing_batch_summary.json` | 剩余 39 个样本批量导出 summary。 |
| `data/cst_exports/level2/L2_*_nearfield.csv` | 48 个样本 nearfield，每个样本 2430 行。 |
| `data/cst_exports/level2/L2_*_farfield.csv` | 48 个样本 farfield，每个样本 3420 行。 |
| `data/cst_exports/level2/all_nearfield.csv` | 48 样本合并 nearfield，共 116640 行。 |
| `data/cst_exports/level2/all_farfield.csv` | 48 样本合并 farfield，共 164160 行。 |
| `outputs/cst_level2_merge_report/level2_merge_summary.json` | `complete_samples=48/48`，`all_complete=true`，strict 通过。 |
| `outputs/cst_level2_superposed_export/level2_full48_merged_validation.json` | full48 nearfield/farfield/pair 校验报告。 |
| `outputs/cst_recognition_level2/` | full48 识别结果，48 samples × 4965 features，accuracy=1.000。 |
| `outputs/cst_recognition_level2_ablation/` | full48 消融结果，5/3/1 频点与 100/75/50/25% 测点组合均为 1.000。 |

## 如何验证

已运行并通过：

```powershell
python code\export_cst_level2_superposed_results.py --all-samples --missing-only --summary-out outputs\cst_level2_superposed_export\level2_remaining_missing_batch_summary.json --stdout-log outputs\cst_level2_superposed_export\level2_remaining_missing_batch_stdout.log --timeout-seconds 7200
python code\merge_cst_level2_exports.py --strict
python code\check_cst_export.py --nearfield data\cst_exports\level2\all_nearfield.csv --farfield data\cst_exports\level2\all_farfield.csv --json-out outputs\cst_level2_superposed_export\level2_full48_merged_validation.json
python code\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
python code\run_cst_recognition_ablation.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_ablation
python code\build_scorecard.py
python code\build_submission_index.py
python code\build_completion_audit.py
```

关键结果：

- Level 2 complete samples：48/48。
- 合并 nearfield：116640 行。
- 合并 farfield：164160 行。
- full48 识别：best model `svm_rbf`，accuracy `1.000`。
- full48 消融：所有 8 个删减组合 accuracy 和 macro F1 均为 `1.000`。
- completion audit：G3 与 G4 均为 `complete`，下一阻塞门槛为 G5。

## 当前限制

1. Level 2 full48 仍是 CST-derived element-library 线性叠加，不是复杂航空载体结构 full-wave 仿真。
2. Level 1 required 已有真实 CST solver-safe 重建，但当前重建相关系数偏低，属于报告前必须处理的技术风险。
3. 最终 PDF/DOCX/PPTX/MP4 尚未生成，因此总目标仍未完成。

## 下一步

| 角色 | 当前主责 | 技术细节 |
|---|---|---|
| A：算法/识别 | 处理 Level 1 重建精度风险 | 检查 FarfieldPlot 近远场一致性、等效源基函数、归一化和正则化；必要时给出失败机理和改进版本。 |
| B：CST 仿真 | 做结构散射/遮挡对照 | 选择 1 到 2 个代表 Level 2 样本，加入简化 PEC 机体/板/盒结构，比较 full-wave 对 element-library 结果的偏差。 |
| C：报告/材料 | 进入正式成稿 | 把 Level 1、Level 2 full48、消融、限制和风险写入报告，随后生成 PDF/DOCX/PPTX/视频。 |
