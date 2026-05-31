# S12 Level 1 解析方向图参考说明

## 做了什么

本阶段为 Level 1 标准源生成了解析方向图参考，包括短偶极子和半波振子在当前上半球 farfield 网格上的归一化方向图、热力图、theta cut 和真实 CST 到位后的比对状态表。

## 为什么这样做

Level 1 的核心目的不是追求复杂模型，而是检查坐标、相位、极化和主瓣方向是否可靠。短偶极子和半波振子有明确的理论方向图，因此可以作为真实 CST 导出后的 sanity check：

- CST farfield 主瓣方向是否大体符合源方向。
- x/y/z 轴方向是否被交换。
- 极化投影是否明显异常。
- farfield 网格和 sample_id 是否能与 Python 脚本对齐。

它不能替代真实 CST 重建验收，只是更早发现“模型或导出设置明显错了”的问题。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_level1_analytic_reference.py` | 生成解析方向图参考和真实 CST 比对状态 | 每次 Level 1 manifest 或真实 farfield 更新后运行 |
| `outputs/level1_analytic_reference/README_level1_analytic_reference.md` | 使用说明 | 先读这里 |
| `outputs/level1_analytic_reference/level1_analytic_farfield_reference.csv` | 6 个 Level 1 案例的解析 farfield 表 | 与 CST farfield 网格对齐 |
| `outputs/level1_analytic_reference/level1_analytic_reference_summary.csv` | 每个案例的峰值位置和行数摘要 | sanity check |
| `outputs/level1_analytic_reference/level1_analytic_compare_status.csv` | 若真实 CST farfield 存在，则输出相关系数/NMSE/主瓣误差 | 当前显示缺失真实 CST |
| `outputs/level1_analytic_reference/*_heatmap.png` | 解析归一化方向图热力图 | 报告/答辩辅助图 |
| `outputs/level1_analytic_reference/*_theta_cuts.png` | 0/90/180/270 deg theta cut | 快速查看方向图形态 |

## 验证方式

```powershell
python code\build_level1_analytic_reference.py
python code\build_scorecard.py
python code\build_submission_index.py
python code\build_completion_audit.py
```

当前结果：

- Level 1 解析案例：6 个。
- required 解析案例：2 个。
- 每案例 farfield 行数：2664。
- 已比对真实 CST 案例：0 个。

## 当前不足

- 当前没有真实 CST farfield 文件，因此 `level1_analytic_compare_status.csv` 只显示 `missing_real_cst_farfield`。
- 解析方向图只适用于标准源 sanity check，复杂载体、多源散射和安装效应必须依赖 CST 全波仿真。

## 下一步

1. 将真实 Level 1 farfield 放入 `data/cst_exports/level1`。
2. 重新运行 `python code\build_level1_analytic_reference.py`。
3. 检查解析比对状态，再运行严格合并审计和批量重建。
