# S27 G5 复合扰动材料刷新

## 做了什么

- 将 Level 2 复合仪器误差与结构缺测压力测试写入报告草稿、最终提交计划和生成脚本。
- 把特征辨识指标从单纯 `accuracy=1.000` 改成更完整的三段证据：clean full48 达标、简化结构遮挡跨域稳定、复合扰动下需要插补缓解。
- 明确 raw `zero_fill`/`mask_features` 在强复合扰动下会低于 0.85，而 `freq_sensor_median_impute` 当前可把最小 accuracy 提升到 `0.867`。

## 为什么这样做

- G5 的 85% 识别指标不能只依赖 clean Level 2 样本，否则答辩时容易被追问仪器误差、测点缺失和结构遮挡同时出现时是否仍稳健。
- 复合压力测试暴露了真实边界：直接补零和只加 mask 特征不够稳健。把这个失败边界写清楚，比把结论写得过满更有工程可信度。
- 插补策略给了一个可执行的后续工作流：CST/Python 导出后先做频点-传感器维度的稳健插补，再进入空-频-极化特征识别。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_scorecard.py` | scorecard 读取 compound stress 指标并降低过度乐观状态 | 运行 `python code\build_scorecard.py` |
| `code/build_report_package.py` | 报告替换清单加入 compound stress 图表和写作门槛 | 运行 `python code\build_report_package.py` |
| `code/build_presentation_package.py` | PPT/视频脚本加入结构遮挡与复合扰动边界页 | 运行 `python code\build_presentation_package.py` |
| `docs/solution_report_draft.md` | 人工报告草稿加入 7.6 复合扰动压力测试章节 | 作为正式报告叙事来源 |
| `docs/final_submission_package_plan.md` | 最终提交计划加入复合扰动验收门槛 | 用于打包前核对 |
| `data/recognition_stress_tests/level2_compound_stress` | 复合压力测试数据与摘要 | 作为报告/PPT证据源 |

## 验证方式

```powershell
python -m py_compile code\build_scorecard.py code\build_report_package.py code\build_presentation_package.py
python code\build_scorecard.py
python code\build_report_package.py
python code\build_presentation_package.py
```

## 当前不足

- 复合扰动仍是 CST-derived Level 2 数据上的可复现压力测试，不是实测仪器标定数据。
- 简化结构遮挡不是 full-wave airframe scattering，不能替代真实机体散射、多径和安装点耦合求解。
- 插补策略已经通过当前压力测试，但还需要在后续 full-wave true nearfield monitor 数据上复验。

## 下一步

1. 重跑 scorecard、report package 和 presentation package，确认复合扰动表述进入自动产物。
2. 继续推进 true nearfield monitor 或 full-wave airframe 数据闭环。
3. 将插补策略固定为后续 CST 导出到识别模型之间的默认预处理候选。
