# S22 Level 2 简化结构遮挡对照

## 做了什么

本阶段新增并运行 `code/run_cst_structure_comparison.py`，在已经完成的 Level 2 full48 CST-derived element-library 数据上施加简化航空载体遮挡迁移函数，生成结构感知版本的 nearfield/farfield，并统计方向图变化和跨域识别结果。

当前脚本覆盖 48 个 Level 2 样本、5 个频点，共 240 个 sample-frequency 案例。输出写入 `outputs/cst_structure_comparison`。

## 为什么这样做

Level 2 full48 当前证据来自三方向短偶极子 element-library 的线性叠加，能够证明多源、多频、多测点识别链路可运行，但不能直接声称已经完成复杂航空载体 full-wave airframe scattering。为了把这个边界讲清，同时避免报告只停留在口头说明，本阶段引入简化机身/机翼/尾翼遮挡迁移：

1. 量化结构/安装效应会给方向图带来多大偏差。
2. 检查当前空-频-极化特征在结构扰动下是否仍能保持识别稳定。
3. 为报告、PPT、视频提供“已做对照，但不是 full-wave”的明确证据口径。

## 核心结果

| 指标 | 数值 |
|---|---:|
| 样本数 | 48 |
| 样本-频点数 | 240 |
| mean shadow | 3.06 dB |
| P95 shadow | 6.63 dB |
| max shadow | 13.33 dB |
| mean pattern correlation | 0.730 |
| cross-domain accuracy | 1.000 |
| best cross-domain model | SVM RBF |

结论是双重的：结构遮挡确实会改变方向图形态，因此不能把 element-library full48 外推成 full-wave airframe 结论；但在这个简化结构扰动下，当前识别特征仍保持 1.000 跨域准确率，说明识别链路具有一定安装效应鲁棒性。

## 产物与文件意义

| 文件 | 意义 |
|---|---|
| `code/run_cst_structure_comparison.py` | 生成简化结构遮挡迁移、方向图偏差统计和跨域识别验证的脚本 |
| `outputs/cst_structure_comparison/README_cst_structure_comparison.md` | 结构对照目录说明和报告口径 |
| `outputs/cst_structure_comparison/structure_comparison_summary.json` | 总体指标摘要，供 scorecard、report package 和 dashboard 读取 |
| `outputs/cst_structure_comparison/structure_comparison_metrics.csv` | 每个 sample/frequency 的遮挡、NMSE、相关系数和主瓣误差 |
| `outputs/cst_structure_comparison/structure_effect_by_class.csv` | 四类状态的结构效应均值和极值 |
| `outputs/cst_structure_comparison/structure_recognition_metrics.json` | 无结构训练、简化结构测试的识别结果 |
| `outputs/cst_structure_comparison/structure_cross_domain_confusion_matrix.png` | 跨域识别混淆矩阵 |
| `outputs/cst_structure_comparison/plots/*_structure_compare.png` | 代表样本的无结构/简化结构方向图对照 |

## 如何验证

运行命令：

```powershell
python code\run_cst_structure_comparison.py
```

本阶段已完成一次刷新，脚本输出 `Structure comparison written to ...\outputs\cst_structure_comparison`，并生成 `structure_comparison_summary.json`。后续可用下列文件快速复核：

```text
outputs/cst_structure_comparison/structure_comparison_summary.json
outputs/cst_structure_comparison/structure_effect_by_class.csv
outputs/cst_structure_comparison/structure_recognition_metrics.json
```

## 对总目标的影响

本阶段把 G5 中“Level 2 结构散射/遮挡边界不清”的风险从缺证据推进到“已有 bounded structure evidence，需写入最终材料”。它不能关闭 full-wave airframe 增强项，但已经足以在报告中保守说明 element-library 证据的适用范围和结构扰动下的识别稳健性。

## 下一步

1. 将本阶段指标写入 `docs/solution_report_draft.md`、报告成稿素材包、PPT/视频 storyboard。
2. 刷新 scorecard、赛题要求矩阵、completion audit、master dashboard 和 submission draft。
3. 最终成稿时明确：该结果是 simplified aircraft occlusion transfer，不是 full-wave CST airframe scattering。
