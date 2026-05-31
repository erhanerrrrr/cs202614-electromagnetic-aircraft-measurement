# S08 CST 宏模板与批量执行说明

## 做了什么

本阶段把已有 Level 1/Level 2 manifest 转成了 CST 可执行前的宏输入表、pilot 队列和宏模板骨架。重点不是替代 CST 仿真，而是把人工建模和导出的关键参数固定下来，减少队友在 CST 中逐项复制时出错。

## 为什么这样做

当前完成度审计的最短阻塞点是 `G2`：真实 Level 1 required 标准源还没有通过 CST 导出、审计和重建。直接进入完整 Level 2 批量仿真风险较高，因此先把 CST 执行拆成：

1. Level 1 两个 required 标准源先跑通。
2. Level 1 推荐源用于坐标轴和极化复核。
3. Level 2 先跑每类 1 个 pilot 样本。
4. pilot 通过后再扩展到 48 个样本全量批处理。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/prepare_cst_macro_templates.py` | 生成 CST 宏输入表和模板的脚本 | 每次 manifest 改动后重新运行 |
| `outputs/cst_macro_templates/level1_macro_parameters.csv` | Level 1 每个标准源的完整参数表 | CST 操作员按行建模或导入宏 |
| `outputs/cst_macro_templates/level1_required_launch_order.csv` | G2 必做的两个标准源顺序 | 先跑短偶极子，再跑半波振子 |
| `outputs/cst_macro_templates/level2_macro_sample_parameters.csv` | Level 2 每个样本的频点、导出路径和预计行数 | 全量批处理前检查项目命名 |
| `outputs/cst_macro_templates/level2_macro_source_parameters.csv` | Level 2 每个源的坐标、方向、幅度和相位 | 构建多源激励表 |
| `outputs/cst_macro_templates/level2_pilot_cases.csv` | 每个类别 1 个 pilot 样本 | 先验证 4 个样本再跑 48 个 |
| `outputs/cst_macro_templates/cst_macro_execution_checklist.csv` | 宏执行和证据清单 | 记录每个样本是否已建模、导出、审计 |
| `outputs/cst_macro_templates/*.bas` | CST VBA 宏骨架 | 在 CST 中按版本适配具体 API |
| `outputs/cst_macro_templates/README_cst_macro_templates.md` | 使用说明 | 交给 CST 负责同学 |

## 验证方式

```powershell
python code\prepare_cst_macro_templates.py
python -m compileall src
```

当前生成结果：

- Level 1 案例：6 个。
- Level 1 required 案例：2 个，`L1_short_dipole_z_1p2G`、`L1_halfwave_dipole_z_1p2G`。
- Level 2 样本：48 个。
- Level 2 sample-frequency 任务：240 个。
- Level 2 源行：120 条。
- 半球面测点：162 个。

## 当前不足

- `.bas` 文件是 CST 宏骨架，尚未在本机 CST 中实际运行验证。
- 这些文件不能作为仿真证据；真实证据仍然必须来自 CST 工程、nearfield/farfield 导出、审计脚本和重建/识别结果。

## 下一步

1. CST 负责同学先按 `level1_required_launch_order.csv` 完成两个 required 标准源。
2. 导出后运行 `merge_cst_level1_exports.py --strict` 和 `run_cst_level1_batch_reconstruction.py --require-cases`。
3. 若 G2 通过，再按 `level2_pilot_cases.csv` 做 4 个 Level 2 pilot 样本。
