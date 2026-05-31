# S20 G5 报告与答辩材料口径刷新

## 做了什么

- 核对 `docs/solution_report_draft.md`、`docs/final_submission_package_plan.md`、`code/build_report_package.py` 和 `code/build_presentation_package.py` 中的 G5 状态表述。
- 将提交计划从“仍缺真实 CST Level 1/Level 2 结果”更新为当前事实：Level 1 required 与 Level 2 full48 已有证据，但 Level 1 指标风险、Level 2 结构边界和最终文件导出尚未关闭。
- 调整报告素材包与答辩素材包生成逻辑，使其区分“真实 CST 缺口”“G5 风险待复核”和“算法参考图”，避免把合成鲁棒性图误写成最终真实 CST 结论。
- 更新 README 中 baseline 的定位：baseline 只作为算法接口和测点压缩参考，最终主证据转向 Level 1/Level 2 CST 数据链。

## 为什么这样做

- 赛题最终提交不只看脚本是否跑通，还要看报告、PPT、视频中的说法是否与证据一致。
- 当前真实数据状态已经从“缺 CST 文件”推进到“有 CST 证据但需解释风险”。如果提交计划和素材包仍保留旧口径，后续三人分工会重复做已完成的导出工作，反而漏掉真正阻塞 G5 的精度风险和成稿导出。
- 把 reference-only 图表单独标出，可以在报告中安全使用鲁棒性和少测点曲线，同时避免把早期合成参考夸大为真实 CST 高精度证明。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `docs/final_submission_package_plan.md` | 最终提交包结构、报告/PPT/视频大纲、三人分工和验收门槛 | 作为 G5 后半程的提交材料总清单 |
| `code/build_report_package.py` | 生成报告章节状态、图表清单、引用短表和替换任务 | 运行后查看 `outputs/report_package` |
| `code/build_presentation_package.py` | 生成答辩 12 页 storyboard、视频分镜和展示素材清单 | 运行后查看 `outputs/presentation_package` |
| `README.md` | 项目入口与当前证据状态 | 给队员快速判断当前主线和剩余风险 |
| `docs/stage_notes/20_g5_report_material_refresh.md` | 本阶段说明 | 解释本轮为什么改材料口径、改了哪些文件 |

## 验证方式

```powershell
python code\build_report_package.py
python code\build_presentation_package.py
python code\build_scorecard.py
python code\build_problem_requirements_matrix.py
python code\build_submission_index.py
python code\build_completion_audit.py
python code\build_master_dashboard.py
python code\build_submission_draft.py
python -m compileall src
```

## 当前不足

- 本阶段没有新跑 CST 结构散射/遮挡对照样本。
- 尚未导出正式 `solution_report.docx/pdf`、`defense_slides.pptx/pdf` 和 `demo_video.mp4`。
- Level 1 required 重建指标仍偏弱，需要下一阶段继续算法复核或形成更严谨的误差机理说明。

## 下一步

1. 用刷新后的 `outputs/report_package` 和 `outputs/presentation_package` 制作正式报告与答辩材料。
2. 优先处理 Level 1 重建精度风险，必要时复核等效源基函数、正则化、坐标/极化转换和远场比较口径。
3. 通过 CST MCP/桌面控制补充简化结构散射/遮挡对照或至少补充工程截图证据。
4. 导出最终 DOCX/PDF/PPTX/MP4 后重跑完成度审计。
