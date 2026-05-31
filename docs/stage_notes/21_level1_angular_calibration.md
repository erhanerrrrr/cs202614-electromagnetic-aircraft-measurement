# S21 Level 1 FarfieldPlot-derived 角域校准

## 做了什么

- 复核 Level 1 required 重建指标偏弱的原因，确认当前 `nearfield.csv` 是 CST `FarfieldPlot` 在 13 m 半球方向上的线性 E-field 列表值，经球坐标到 Cartesian 转换得到，并不是 full-wave near-field monitor 直接导出。
- 新增 `code/run_cst_level1_angular_calibration.py`，对 FarfieldPlot-derived 角域样本进行 Legendre/Fourier 正则化拟合，再预测 CST 远场网格。
- 对两个 required 标准源运行角域校准 sweep，并保存最佳指标、对比图、基函数系数和汇总说明。

## 为什么这样做

- 原 `code/run_cst_reconstruction.py` 使用有限距离等效源近场传播模型，适合真实近场 monitor 或与该模型匹配的数据。
- 当前 solver-safe 路线为了避免 13 m 探针导致 CST 网格爆炸，采用 FarfieldPlot 角域列表值作为测点合同数据。把这类 farfield-derived 角域数据直接当作 full-wave 近场输入，会造成模型不匹配。
- 角域校准能回答一个更准确的问题：当前 solver-safe 导出的 162 个半球方向样本能否稳定重建更密的 CST 远场方向图。结果显示该链路高度自洽。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/run_cst_level1_angular_calibration.py` | Level 1 角域校准脚本，读取 strict 完成案例并批量 sweep | `python code\run_cst_level1_angular_calibration.py` |
| `outputs/cst_level1_angular_calibration/angular_calibration_summary.json` | 两个 required case 的角域校准总指标 | 报告/PPT 中引用 max NMSE、min correlation、主瓣误差 |
| `outputs/cst_level1_angular_calibration/angular_calibration_batch_results.csv` | 每个 case 的最佳配置和指标 | 对比短偶极子/半波振子 |
| `outputs/cst_level1_angular_calibration/angular_calibration_sweep_results.csv` | 全部基函数阶数和正则化 sweep | 证明不是只跑单一参数 |
| `outputs/cst_level1_angular_calibration/L1_short_dipole_z_1p2G/angular_farfield_compare.png` | 短偶极子 CST 真值、角域校准和差值图 | PPT/报告图 |
| `outputs/cst_level1_angular_calibration/L1_halfwave_dipole_z_1p2G/angular_farfield_compare.png` | 半波振子 CST 真值、角域校准和差值图 | 报告补充图 |

## 验证方式

```powershell
python code\run_cst_level1_angular_calibration.py
python code\build_scorecard.py
python code\build_problem_requirements_matrix.py
python code\build_report_package.py
python code\build_presentation_package.py
python code\build_completion_audit.py
python code\build_master_dashboard.py
python -m compileall src
```

关键结果：

- required cases：2/2。
- sweep rows：128。
- 最大 NMSE：`8.41e-5`。
- 最小相关系数：`0.99988`。
- 最大主瓣误差：`0.00 deg`。

## 当前不足

- 角域校准不等同于 full-wave near-field monitor 反演，不能把它包装成完整物理近场测量闭环。
- 原等效源近场反演结果仍需作为模型风险保留，除非后续补真实近场 monitor 或重新设计匹配 FarfieldPlot 数据的传播模型。
- 复杂航空载体结构散射/遮挡对照仍未补齐。

## 下一步

1. 将角域校准结果写入正式报告第 5/8/9 章和答辩 PPT 第 6 页。
2. 把原等效源反演偏弱解释为“数据类型与传播模型不匹配”，避免让评委误解为 CST 数据失败。
3. 继续补 Level 2/Level 3 结构散射或遮挡对照，用来增强复杂航空载体适用性。
