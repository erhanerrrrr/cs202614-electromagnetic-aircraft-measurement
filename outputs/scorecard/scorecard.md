# CS-202614 scorecard

Generated from the current workspace. This scorecard is intentionally conservative: synthetic/demo outputs are treated as pipeline evidence, and CST-derived element-library outputs are separated from full-wave airframe evidence.

## Overall Status

- Goal status: in progress.
- Strongest current assets: literature matrix, CST data schema, Level 1 required CST exports/reconstruction, Level 2 48-sample CST-derived exports/recognition, simplified structure comparison, compound instrument/dropout stress test, manifests, merge audits, and robustness scans.
- Critical gap: Level 1 equivalent-source reconstruction quality is weak, simplified structure/occlusion evidence is ready but not full-wave airframe scattering, and severe compound recognition stress needs the median-imputation mitigation caveat in report/PPT wording.
- Submission gap: exported report/PPT/video/archive files exist, but they need review or regeneration after the latest G5 compound-stress wording update; administrative metadata and human playback review remain outside the code pipeline.

## Score Items

| Item | Points | Status | Current evidence | Missing for final | 
|---|---:|---|---|---|
| 国内外发展调研分析 | 10 | Draft evidence | 已形成文献筛查和矩阵，当前矩阵约 31 条。 | 补充最终引用格式，把文献到算法迁移证据链转成报告正文。 |
| 研究思路合理性 | 10 | CST evidence ready; write-up pending | 已形成标准源 -> 多源 -> 简化载体 -> 扰动鲁棒性的递进路线；Level 1 required_complete=True，Level 2 all_complete=True，简化结构对照样本=48。 | 补充 CST solver-safe、element-library 叠加、简化结构遮挡对照和调参过程说明。 |
| 技术路线可行性 | 10 | CST evidence ready; model risk bounded | CST 模板、校验、重建、识别、合并、鲁棒性扫描脚本均已具备；Level 1 真实 required 重建 2 个案例，角域校准 2 个案例，Level 2 完整样本 48/48，结构遮挡对照 cross-domain accuracy=1.0。 | 角域校准已证明 solver-safe FarfieldPlot-derived 数据自洽；简化结构遮挡对照已给出安装效应敏感性，但 full-wave 近场等效源反演和 full-wave airframe 结构散射仍需边界说明。 |
| 测试方案完整性 | 10 | CST evidence ready; screenshots pending | 已具备 Level 1/2 规程、Level 1 manifest 6 个案例、半球面 Level 1 任务包 6 个案例、Level 1 解析方向图 sanity reference 6 个案例、Level 2 任务包 48 个样本、CST dashboard required action 2 个、Level 2 strict all_complete=True。 | 最终报告需要补充 CST 参数截图、简化结构对照图和最终测试日志。 |
| 2π 传感布局与 12m x 10m x 8m 包络 | 10 | Ready | 13 m 半球面 162 测点方案已生成，并已用于 Level 1/2 CST-derived 导出合同。 | 最终报告/PPT 需补充半球面布局图和 CST 参数截图。 |
| 三维场重建高精度与少测点 | 30 | CST angular calibration ready; near-field model risk | 真实 Level 1 required 重建已完成 2 个案例；等效源近场反演最大 NMSE=6.087e-01、最小相关系数=0.36657；FarfieldPlot-derived 角域校准最大 NMSE=8.406e-05、最小相关系数=0.99988、最大主瓣误差=0.00 deg。 | solver-safe nearfield 是 FarfieldPlot-derived 角域样本，不是 full-wave 近场 monitor；正式报告必须区分角域高一致性和近场等效源模型风险。 |
| 空间-频谱特征辨识准确率 >= 85% | 20 | Ready with compound-stress mitigation caveat | Level 2 48 样本 CST-derived 数据已完成；识别样本 48 个、特征 4965 维，accuracy=1.0，消融最低 accuracy=1.0；简化结构 cross-domain accuracy=1.0，平均遮挡=3.06 dB；复合仪器误差+结构缺测 240 行，原始最差 accuracy=0.7333333333333333，最佳缓解策略=freq_sensor_median_impute，min accuracy=0.8666666666666667。 | 当前证据为 element-library 线性叠加 + 简化结构遮挡迁移 + 仿真复合仪器/缺测压力测试；尚不是复杂载体 full-wave airframe 结构散射解或真实仪器校准结论。 |

## Key Metrics

| Metric | Value |
|---|---:|
| 文献矩阵条目 | 31 |
| Level 1 计划案例 | 6 |
| Level 1 必做案例 | 2 |
| Level 1 完整案例 | 2 |
| Level 1 完整必做案例 | 2 |
| Level 1 批量重建完成数 | 2 |
| Level 1 角域校准案例数 | 2 |
| Level 1 角域校准最大 NMSE | 8.40556336030498e-05 |
| Level 1 角域校准最小相关系数 | 0.9998782818365388 |
| Level 1 半球面任务包案例数 | 6 |
| Level 1 半球面测点数 | 162 |
| Level 1 同形合成重建完成数 | 6 |
| Level 1 同形合成最大 NMSE | 4.513301387435835e-06 |
| Level 1 同形合成最小相关系数 | 0.9999966226839192 |
| Level 2 计划样本 | 48 |
| Level 2 半球面任务包样本 | 48 |
| Level 2 半球面频点任务 | 240 |
| CST dashboard Level 1 required action | 2 |
| CST dashboard Level 2 pilot action | 4 |
| CST dashboard required-now missing files | 0 |
| Level 1 解析参考案例数 | 6 |
| Level 1 解析参考每案例行数 | 2664 |
| Level 1 解析参考已比对真实 CST 案例数 | 0 |
| Level 2 完整样本 | 48 |
| Level 2 strict all_complete | True |
| Level 2 识别样本 | 48 |
| Level 2 识别特征数 | 4965 |
| Level 2 识别 accuracy | 1.0 |
| Level 2 消融最低 accuracy | 1.0 |
| Level 2 结构对照样本 | 48 |
| Level 2 结构对照样本-频点 | 240 |
| Level 2 结构平均遮挡 dB | 3.059749694260782 |
| Level 2 结构 P95 遮挡 dB | 6.632975065705098 |
| Level 2 结构最大遮挡 dB | 13.32862611170669 |
| Level 2 结构方向图平均相关系数 | 0.7300355010466705 |
| Level 2 结构 cross-domain accuracy | 1.0 |
| Level 2 结构 cross-domain model | svm_rbf |
| Level 2 结构对照是否 full-wave airframe | False |
| Level 2 复合压力测试行数 | 240 |
| Level 2 复合压力测试全行通过 0.85 | False |
| Level 2 复合压力测试原始最差 accuracy | 0.7333333333333333 |
| Level 2 复合压力测试原始最差策略 | zero_fill |
| Level 2 复合压力测试原始最差场景 | sensor_gain3db_sensor_node_dropout25pct |
| Level 2 复合压力测试最佳缓解策略 | freq_sensor_median_impute |
| Level 2 复合压力测试最佳策略最小 accuracy | 0.8666666666666667 |
| Level 2 复合压力测试最佳策略平均提升 | 0.05444444444444443 |
| Level 1 真实重建完成数 | 2 |
| Level 1 真实重建最大 NMSE | 0.6086845328151742 |
| Level 1 真实重建最小相关系数 | 0.3665721711770728 |
| Level 1 真实重建最大主瓣误差 | 22.016476605353944 |
| 合成 CST 重建 demo NMSE | 1.2556290223865832e-06 |
| 合成 CST 重建 demo 相关系数 | 0.9999992368907393 |
| 30 dB optimized_75 NMSE | 0.0011336665143435 |
| 30 dB optimized_75 相关系数 | 0.998337100528421 |
| CST 格式识别 demo accuracy | 1.0 |
| 识别删减 demo 最低 accuracy | 1.0 |

## Next Actions

1. Improve or explain the weak Level 1 solver-safe reconstruction metrics.
2. Write the simplified airframe/occlusion comparison into the report and keep full-wave airframe scattering as an optional enhancement.
3. Add the compound instrument/dropout stress boundary: raw zero-fill/mask can fall below 0.85, while frequency/sensor median imputation is the current mitigation candidate.
4. Replace demo values in `docs/solution_report_draft.md` with the current Level 1/2 CST-derived evidence.
5. Review or regenerate final report, PPT, video script, and code/package checklist with the compound-stress wording included.
6. Rebuild completion audit and submission package after refreshed artifacts are accepted.
