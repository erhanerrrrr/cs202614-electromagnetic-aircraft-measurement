# S18 CST Level 2 element-library pilot

## 做了什么

本阶段把 G3 从“Level 2 真实 CST 数据 0/48”推进到“8 个真实 CST-derived pilot 样本可校验、可合并、可训练识别模型”。

完成事项：

1. 审计当前 G3 缺口：`outputs/cst_level2_merge_report/level2_merge_summary.json` 原本显示 `complete_samples=0/48`。
2. 新增 CST Level 2 element-library 建模脚本：`code/run_cst_level2_element_library.py`。
3. 新增 Level 2 superposition 导出脚本：`code/export_cst_level2_superposed_results.py`。
4. 通过本机 CST API 生成 x/y/z 三个短偶极子 element 工程，每个工程含 5 个 farfield monitor：
   - 900 MHz
   - 1050 MHz
   - 1200 MHz
   - 1350 MHz
   - 1500 MHz
5. 用 `code/run_cst_solver_project.py` 求解三个 element 工程，并确认每个工程都有 5 个 `Farfields\farfield_* [1]` 结果。
6. 按 Level 2 manifest 的源位置、方向、相对幅度和相位，导出 8 个 pilot 样本：
   - `L2_comm_pair_000`
   - `L2_comm_pair_001`
   - `L2_radar_top_000`
   - `L2_radar_top_001`
   - `L2_mixed_avionics_000`
   - `L2_mixed_avionics_001`
   - `L2_multi_state_on_000`
   - `L2_multi_state_on_001`
7. 运行 Level 2 合并审计、合并文件校验、pilot 识别和 pilot 消融。

## 为什么这样做

如果把 Level 2 多个源直接按 12 m x 10 m x 8 m 包络放进一个全尺寸 CST 空域，网格会被大型计算域拉大，极可能重复 Level 1 原始 13 m Cartesian probe 的不可求解问题。本阶段采用 solver-safe 的 element-library 路线：

1. CST 负责真实求解紧凑 x/y/z 单元源电磁响应。
2. Python 按线性叠加原理组合多源位置、方向、幅度和相位。
3. 输出仍严格满足现有 Level 2 CSV 合同和识别脚本输入格式。

这不是最终的复杂载体 full-wave 多源模型；它是 G3 的本机可执行 pilot 闭环。它的价值是先证明：

- CST 真实求解可以覆盖 5 频点；
- Level 2 sample-level nearfield/farfield CSV 可由真实 CST element 数据生成；
- 4 类多源状态能进入识别模型；
- 后续批量扩展到 48 样本时，数据结构、行数、标签和脚本链路已经可用。

## 产物有哪些

### 新增脚本

| 文件 | 意义 |
|---|---|
| `code/run_cst_level2_element_library.py` | 生成 x/y/z 三方向短偶极子 element-library CST 工程，每个工程含 5 个 farfield monitor。 |
| `code/export_cst_level2_superposed_results.py` | 打开已求解的 x/y/z element 工程，用 CST FarfieldPlot 取数，并按 Level 2 source manifest 做位置/幅相叠加导出 sample-level CSV。 |

### CST element 工程与求解日志

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_level2_element_library/` | x/y/z element 工程生成记录、VBA history、project manifest。 |
| `outputs/cst_level2_element_trials/x_solver_safe/` | x 方向 element 已求解 CST 工程和 solver summary。 |
| `outputs/cst_level2_element_trials/y_solver_safe/` | y 方向 element 已求解 CST 工程和 solver summary。 |
| `outputs/cst_level2_element_trials/z_solver_safe/` | z 方向 element 已求解 CST 工程和 solver summary。 |

### Level 2 pilot 数据

| 文件/目录 | 意义 |
|---|---|
| `data/cst_exports/level2/L2_*_nearfield.csv` | 每个 pilot 样本 2430 行，5 频点 × 162 测点 × Ex/Ey/Ez。 |
| `data/cst_exports/level2/L2_*_farfield.csv` | 每个 pilot 样本 3420 行，5 频点 × 684 远场网格点。 |
| `data/cst_exports/level2/all_nearfield.csv` | 8 个 pilot 样本合并 nearfield，共 19440 行。 |
| `data/cst_exports/level2/all_farfield.csv` | 8 个 pilot 样本合并 farfield，共 27360 行。 |
| `outputs/cst_level2_superposed_export/` | 每个 pilot 样本的导出 summary、stdout 和合并校验 JSON。 |

### 审计和识别指标

| 文件/目录 | 意义 |
|---|---|
| `outputs/cst_level2_merge_report/level2_merge_summary.json` | 当前 `complete_samples=8/48`，合并 nearfield 19440 行，farfield 27360 行。 |
| `outputs/cst_recognition_level2_pilot/` | 8 样本 pilot 识别结果，特征矩阵 8 × 4965，SVM accuracy=1.000。 |
| `outputs/cst_recognition_level2_pilot_ablation/` | pilot 消融：5 频下 100/75/50/25% 测点均为 1.000，1 频下降到 0.750。 |

## 如何验证

已运行并通过：

```powershell
python code\run_cst_level2_element_library.py --out-dir outputs\cst_level2_element_library --axes x,y,z --timeout-seconds 900
python code\merge_cst_level2_exports.py
python code\check_cst_export.py --nearfield data\cst_exports\level2\all_nearfield.csv --farfield data\cst_exports\level2\all_farfield.csv
python code\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_pilot --test-size 0.5
python code\run_cst_recognition_ablation.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_pilot_ablation --test-size 0.5
python -m compileall src
```

关键结果：

- Level 2 complete samples：8/48。
- 合并 nearfield：19440 行。
- 合并 farfield：27360 行。
- 合并校验：nearfield/farfield/pair 均 `ok=True`。
- pilot 识别：8 samples × 4965 features，best model `svm_rbf`，accuracy `1.000`。
- pilot 消融：5 频下测点删减到 25% 仍为 1.000；1 频为 0.750。
- element-library 清单：x/y/z 三方向工程均存在；在已有工程上刷新清单时 CST API 可能给出 `RuntimeError()` 保存警告，脚本会记录为 `project_exists_after_runtime_warning`，实际导出以 `outputs/cst_level2_element_trials/*_solver_safe` 中已求解工程为准。

## 当前限制

1. 这仍是 pilot，不是最终 48 样本 full dataset。
2. 当前 Level 2 使用 compact element-library + 线性叠加，尚未包含复杂航空载体结构散射、遮挡和耦合。
3. 8 样本 pilot 的 accuracy 只能证明链路可行，不能作为最终“识别准确率 >= 85%”的强证据。
4. 最终仍需扩展到更多变体，并尽量引入简化载体结构或等效遮挡/散射修正。

## 下一步

建议继续按三人分工推进：

| 角色 | 当前主责 | 技术细节 |
|---|---|---|
| A：算法/识别 | 扩展 pilot 到 48 样本识别并做统计稳定性 | 复用 `code/export_cst_level2_superposed_results.py` 批量导出 48 个样本；运行 recognition/ablation，记录多次 split 或交叉验证结果。 |
| B：CST 仿真 | 评估是否加入简化载体结构 | 在 element-library 路线稳定后，选择 1 到 2 个代表样本做 full-domain 或简化 PEC box/plate 对照，估计结构散射对特征的影响。 |
| C：报告/材料 | 把 Level 2 pilot 写入报告证据链 | 明确区分 “CST-derived pilot” 与 “最终 full 48 sample evidence”，把 solver-safe 原因、行数审计和 pilot 识别结果写入阶段性材料。 |
