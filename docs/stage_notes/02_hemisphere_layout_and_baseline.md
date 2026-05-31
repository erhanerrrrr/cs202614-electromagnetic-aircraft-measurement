# S02 半球面布局与 baseline 说明

## 做了什么

当前测量面固定为半球面 2π 布局，并生成了合成 baseline。布局采用 13 m 上半球面、162 个空间测点，用于覆盖 12 m x 10 m x 8 m 被测包络。

## 为什么这样做

用户明确补充“目前选择半球面”。因此当前 CST Level 1/Level 2、manifest、workpack、数据字典和报告均以半球面测点为唯一执行路线。半柱面只作为后续扩展备选，不进入本轮执行。

选择半球面的原因：

- 覆盖 2π 空间立体角，满足赛题测量面要求。
- 坐标和远场角度更容易与球坐标、theta/phi 极化对应。
- 适合标准源验证和多源识别前期闭环。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/run_baseline.py` | 生成 baseline 布局、重建、测点删减和识别 demo | 运行基础算法验证 |
| `code/em_core.py` | 核心电磁响应、等效源、远场方向图和指标函数 | 被多个脚本复用 |
| `outputs/baseline` | baseline 图表和指标 | 报告/PPT 中说明算法雏形 |
| `outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv` | CST 应使用的 162 个半球面测点 | CST 主责建模时导入或复现 |

## 验证方式

```powershell
python code\run_baseline.py
```

关键输出包括：

- `outputs/baseline/reconstruction_metrics.csv`
- `outputs/baseline/sensor_layout_hemisphere.png`

## 当前不足

- baseline 是合成偶极子模型，不能代替真实 CST 仿真证据。
- CST 工程中实际使用该半球面测点的截图仍缺失。

## 下一步

1. 在 CST Level 1 required 工程中复现 162 个半球面测点。
2. 保存测点布局、monitor 和导出设置截图。
