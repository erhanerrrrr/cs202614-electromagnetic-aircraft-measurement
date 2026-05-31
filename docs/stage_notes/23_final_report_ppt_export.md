# S23 正式报告与答辩 PPT 导出

## 做了什么

本阶段把 G5 中的“正式报告”和“答辩材料”从草稿推进为可提交文件：

1. 生成正式方案报告 `DOCX/PDF`。
2. 生成 12 页答辩 `PPTX`，并导出 `PDF`。
3. 对报告和 PPT 做页面级视觉检查。
4. 刷新 report package、presentation package、submission index、problem requirements、completion audit、master dashboard 和 submission draft。

当前完成度审计结果为：`7 complete / 1 partial / 0 missing`，唯一未关闭 gate 仍是 `G5`，原因是 `submission/03_video/demo_video.mp4` 尚未生成。

## 为什么这样做

前一阶段已经把 Level 1 角域校准、Level 2 full48 识别、Level 2 简化结构遮挡对照写入技术证据链。G5 的主要风险不再是“没有指标”，而是“是否已经形成正式交付物”。因此本阶段优先做三件事：

1. 将 `docs/solution_report_draft.md` 转成可阅读、可提交、可视觉检查的正式报告。
2. 将 `outputs/presentation_package` 中的答辩逻辑转成真正的 PPTX/PDF。
3. 让所有审计脚本能识别这些正式文件，避免仪表盘仍按草稿状态统计。

## 产物与文件意义

| 文件 | 意义 |
|---|---|
| `code/build_final_report_docx.py` | 从报告草稿、指标 JSON 和图件生成正式 Word 报告的脚本。 |
| `submission/01_report/solution_report.docx` | 正式方案报告 Word 文件。 |
| `submission/01_report/solution_report.pdf` | 由 Word COM 导出的正式方案报告 PDF。 |
| `outputs/final_report/final_report_summary.json` | 报告导出、页数、插图和视觉 QA 摘要。 |
| `outputs/final_report/final_report_contact_sheet.png` | 报告 PDF 栅格化后的总览图，用于检查页面是否明显重叠或裁切。 |
| `code/build_defense_pptx_artifact.py` | 使用 presentation artifact-tool 生成答辩 PPTX 的脚本。 |
| `submission/02_presentation/defense_slides.pptx` | 正式答辩 PPTX，共 12 页。 |
| `submission/02_presentation/defense_slides.pdf` | 由 PowerPoint COM 从 PPTX 导出的答辩 PDF。 |
| `outputs/presentation_artifact/defense_pptx_summary.json` | PPTX/PDF 导出、页数、预览和 QA 摘要。 |
| `outputs/presentation_artifact/defense_slides_pdf_contact_sheet.png` | 答辩 PDF 栅格化后的总览图。 |
| `outputs/019e6c77-5e27-7972-93a0-90d6bdd77225/presentations/cs202614-defense` | artifact-tool 工作目录，含 slide 模块、layout JSON、PNG 预览和接触表。 |
| `outputs/submission_index/submission_index_summary.json` | 当前提交索引统计，已识别报告和 PPT/PDF。 |
| `outputs/completion_audit/completion_audit_summary.json` | 完成度审计，仍保守停在 G5。 |
| `submission/submission_draft_summary.json` | 当前提交草稿目录摘要，72 项全部复制/生成，无缺失。 |

## 关键指标

| 指标 | 当前值 |
|---|---:|
| 报告 PDF 页数 | 27 |
| 报告插图数 | 7 |
| PPT 页数 | 12 |
| PPT layout checker | 0 errors / 0 warnings |
| submission index ready | 61 |
| submission index blocked | 0 |
| submission draft copied/generated | 72 |
| submission draft missing | 0 |
| completion audit | 7C / 1P / 0M |

## 如何验证

报告验证：

```powershell
python code\build_final_report_docx.py
```

由于当前环境没有检测到 LibreOffice/soffice，报告 PDF 使用本机 Microsoft Word COM 导出，并用 `pdftoppm` 渲染为页面 PNG 后检查接触表。`pypdf` 验证报告 PDF 页数为 27。

PPT 验证：

```powershell
python code\build_defense_pptx_artifact.py
node C:\Users\heh20\.codex\plugins\cache\openai-primary-runtime\presentations\26.521.10419\skills\presentations\scripts\check_layout_quality.mjs --layout outputs\019e6c77-5e27-7972-93a0-90d6bdd77225\presentations\cs202614-defense\layout\final
```

本阶段检查结果为 `Checked 12 layout file(s): 0 error(s), 0 warning(s).`。PPT PDF 使用本机 PowerPoint COM 导出，并用 `pdftoppm` 渲染为 12 页 PNG 接触表。

审计链刷新：

```powershell
python code\build_report_package.py
python code\build_presentation_package.py
python code\build_submission_index.py
python code\build_problem_requirements_matrix.py
python code\build_completion_audit.py
python code\build_master_dashboard.py
python code\build_submission_draft.py
```

## 对总目标的影响

本阶段关闭了 G5 中的报告和 PPT/PDF 文件缺口，但没有关闭视频缺口。当前项目已经具备正式报告、正式答辩材料、完整代码/数据/审计索引和提交草稿目录；距离“完成赛题”的最后可执行动作是生成或录制 `submission/03_video/demo_video.mp4`，随后再次运行审计链，确认 `completion_proven=true`。

## 下一步

1. 基于 `submission/02_presentation/defense_slides.pptx` 和 `outputs/presentation_package/demo_video_storyboard.md` 生成或录制演示视频。
2. 视频中保持与报告/PPT 一致的边界表述：Level 1 角域校准是 FarfieldPlot-derived solver-safe 一致性，Level 2 结构对照是 simplified aircraft occlusion transfer，不是 full-wave airframe scattering。
3. 生成 MP4 后重跑审计链和提交草稿，若 G5 变为 complete，再整理最终压缩包和人工报名信息。
