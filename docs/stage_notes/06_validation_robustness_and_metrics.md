# S06 验证、鲁棒性与指标说明

## 做了什么

建立了重建鲁棒性扫描、识别删减验证、评分项证据板、提交包索引和完成度审计。它们用于回答“当前证据够不够交付、还差哪些硬门槛”。

## 为什么这样做

赛题最终评分涉及研究思路、测试方案、传感布局、重建精度、少测点、识别准确率和提交材料。单个脚本跑通不等于赛题完成，因此需要自动化审计：

- scorecard 看评分项证据。
- submission index 看提交物状态。
- completion audit 看完整目标是否被证明。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/run_reconstruction_robustness.py` | 噪声、测点比例、正则化扫描 | 支撑少测点和鲁棒性分析 |
| `outputs/reconstruction_robustness` | 鲁棒性指标和图表 | 报告/PPT 的算法证据 |
| `code/run_cst_recognition_ablation.py` | 识别测点/频点删减验证 | 证明识别特征冗余度 |
| `outputs/cst_recognition_ablation` | 删减实验结果 | 后续用真实 CST 替换 |
| `code/build_scorecard.py` | 评分项证据汇总 | 每轮更新当前得分证据状态 |
| `outputs/scorecard` | scorecard 输出 | 识别哪些评分项仍需 CST 证据 |
| `code/build_submission_index.py` | 提交物索引 | 检查最终包缺哪些文件 |
| `outputs/submission_index` | 提交包清单 | 打包前逐项复核 |
| `code/build_completion_audit.py` | 完成度审计 | 判断总目标是否已经被证明完成 |
| `outputs/completion_audit` | gate 表和最短 gate 顺序 | 指导下一步执行 |

## 验证方式

```powershell
python code\run_reconstruction_robustness.py
python code\build_scorecard.py
python code\build_submission_index.py
python code\build_completion_audit.py
```

## 当前不足

- 该阶段当时多个指标仍来自 synthetic/demo；后续 S17-S20 已把 Level 1 required 与 Level 2 full48 证据接入。
- completion audit 当时已明确 `completion_proven=false`；最新阻塞 gate 以 `outputs/completion_audit/completion_audit_summary.json` 为准。

## 下一步

1. 每次真实 CST 数据更新后，重新运行三个审计脚本。
2. 当前应转向 G5：报告/PPT/视频成稿、Level 1 指标风险说明和 Level 2 结构边界说明。
