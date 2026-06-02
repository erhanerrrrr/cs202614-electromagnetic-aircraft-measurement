# docs 目录说明

本目录存放项目技术文档、文献矩阵、数据字典、阶段说明、复现命令、进度汇报和方案草稿。建议队友先读本文件，再按下面顺序进入具体材料。

## 推荐阅读顺序

1. `project_workflow.md`：从采样方案、CST/Python 数据接口、反演外推到分类识别的完整工作流。
2. `future_engineering_plan.md`：结合导师 DeepSeek 记录和推荐文献形成的后续工程路线。
3. `nonredundant_sampling_design.md`：非冗余半球采样方案，包含 120/81/48/32 点候选布局和指标解释。
4. `cst_level1_sampling_calibration_findings.md`：当前 CST Level 1 采样评估和等效源模型校准结论。
5. `g3_source_model_calibration_plan.md`：下一步反演模型校准、稀疏化、约定检查和球面 NF-FF sanity check 路线。
6. `true_nearfield_monitor_workflow.md`：CST 真近场 monitor 导出、FarfieldPlot-derived 基线对照和后续 G3 复跑逻辑。
7. `current_work_detailed_explanation.md`：当前工程进展和已有证据链。
8. `project_file_index.md`：文件夹与关键产物索引。
9. `literature_matrix.md`、`literature_screening_and_strategy.md`、`literature_to_algorithm_traceability.md`：文献依据与算法迁移关系。

## 子目录

| 子目录 | 说明 |
|---|---|
| `stage_notes/` | 按阶段记录做了什么、为什么做、产物在哪里。 |
| `progress_reports/` | 面向导师/组会的进度报告、风险登记、下一步行动和证据映射。 |

## 当前协作重点

- 不要把 120/81/48/32 点候选直接写成最终采样结论；目前它们是待 CST 校准验证的候选方案。
- 真实 CST Level 1 数据路径已经通过中心源 sanity check，但通用等效源网格仍是反演瓶颈。
- 后续 G3 工作优先级：CST 真近场 monitor 对照、源先验校准、Huygens/SWE 物理基线、多频共享支撑和最终 reduced-layout 复跑。
