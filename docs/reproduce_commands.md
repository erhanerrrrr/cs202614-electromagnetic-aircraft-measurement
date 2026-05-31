# 复现命令清单

版本：v0.1  
用途：最终提交代码包中的复现说明。所有命令默认在项目根目录运行：

```powershell
cd C:\Users\heh20\Desktop\复杂航空载体电磁辐射空域特性测量技术比赛
```

## 1. 环境准备

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果不使用虚拟环境，也至少确认：

```powershell
python -m compileall src
```

## 2. 合成 baseline

```powershell
python code\run_baseline.py
```

输出：

```text
outputs/baseline
```

用途：

- 2π 半球测点布局。
- 合成等效源重建。
- 初始测点优化对照。
- 合成识别 baseline。

## 3. CST Level 1 模板

```powershell
python code\prepare_cst_templates.py
python code\prepare_cst_level1_manifest.py
```

输出：

```text
outputs/cst_templates
outputs/cst_level1_plan
```

校验 demo 模板：

```powershell
python code\check_cst_export.py --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv
```

验证幅值/相位导出转换：

```powershell
python code\normalize_cst_complex_columns.py --make-phase-demo --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv --out-dir outputs\cst_phase_demo
python code\run_cst_reconstruction.py --nearfield outputs\cst_phase_demo\normalized_nearfield.csv --farfield outputs\cst_phase_demo\normalized_farfield.csv --out-dir outputs\cst_phase_demo\reconstruction
```

运行 CST 格式重建 demo：

```powershell
python code\run_cst_reconstruction.py --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv --out-dir outputs\cst_reconstruction_demo
```

## 4. 真实 CST Level 1 接入

本机 CST API 生成两个 required 标准源工程：

```powershell
python code\run_cst_level1_required_automation.py
```

输出：

```text
outputs/cst_real_level1_projects/projects
outputs/cst_real_level1_projects/cst_level1_project_manifest.csv
outputs/cst_real_level1_projects/vba_history
```

说明：这一步会调用 CST Studio Suite 2025 自带 Python，生成真实 `.cst` 工程和 VBA history；它不等同于求解完成，仍需在 CST 中运行 solver 并导出 nearfield/farfield CSV。

本机 solver-safe 路线使用 `efarfield` probe mode，避免 13 m Cartesian E-field probes 扩大网格：

```powershell
python code\run_cst_level1_required_automation.py --out-dir outputs\cst_solver_ready_level1_projects --probe-mode efarfield
```

求解两个 required 标准源：

```powershell
python code\run_cst_solver_project.py `
  --project outputs\cst_solver_ready_level1_projects\projects\CST_L1_short_dipole_z_1p2G.cst `
  --out-dir outputs\cst_solver_trials\short_solver_safe `
  --trial-name CST_L1_short_dipole_z_1p2G_solver_safe_trial.cst `
  --summary-out outputs\cst_solver_trials\short_solver_safe\short_solver_safe_trial_summary.json `
  --stdout-log outputs\cst_solver_trials\short_solver_safe\short_solver_safe_trial_stdout.log `
  --timeout-seconds 900

python code\run_cst_solver_project.py `
  --project outputs\cst_solver_ready_level1_projects\projects\CST_L1_halfwave_dipole_z_1p2G.cst `
  --out-dir outputs\cst_solver_trials\halfwave_solver_safe `
  --trial-name CST_L1_halfwave_dipole_z_1p2G_solver_safe_trial.cst `
  --summary-out outputs\cst_solver_trials\halfwave_solver_safe\halfwave_solver_safe_trial_summary.json `
  --stdout-log outputs\cst_solver_trials\halfwave_solver_safe\halfwave_solver_safe_trial_stdout.log `
  --timeout-seconds 900
```

从已求解工程导出 Level 1 required CSV：

```powershell
python code\export_cst_farfield_results.py `
  --project outputs\cst_solver_trials\short_solver_safe\CST_L1_short_dipole_z_1p2G_solver_safe_trial.cst `
  --sample-id L1_short_dipole_z_1p2G `
  --source-config short_dipole_z `
  --nearfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv `
  --summary-out outputs\cst_farfield_export\L1_short_dipole_z_1p2G_export_summary.json `
  --stdout-log outputs\cst_farfield_export\L1_short_dipole_z_1p2G_cst_python_stdout.log `
  --farfield-item "Farfields\farfield_1200MHz [1]"

python code\export_cst_farfield_results.py `
  --project outputs\cst_solver_trials\halfwave_solver_safe\CST_L1_halfwave_dipole_z_1p2G_solver_safe_trial.cst `
  --sample-id L1_halfwave_dipole_z_1p2G `
  --source-config halfwave_dipole_z `
  --nearfield-out data\cst_exports\level1\L1_halfwave_dipole_z_1p2G_nearfield.csv `
  --farfield-out data\cst_exports\level1\L1_halfwave_dipole_z_1p2G_farfield.csv `
  --summary-out outputs\cst_farfield_export\L1_halfwave_dipole_z_1p2G_export_summary.json `
  --stdout-log outputs\cst_farfield_export\L1_halfwave_dipole_z_1p2G_cst_python_stdout.log `
  --farfield-item "Farfields\farfield_1200MHz [1]"
```

先查看执行清单：

```text
outputs/cst_level1_plan/level1_case_manifest.csv
outputs/cst_level1_plan/level1_source_manifest.csv
outputs/cst_level1_plan/level1_validation_targets.csv
```

将 CST 导出放入：

```text
data/cst_exports/level1/
```

生成 CST 主责任务包：

```powershell
python code\prepare_cst_level1_workpack.py
```

输出：

```text
outputs/cst_level1_workpack/level1_cst_work_items.csv
outputs/cst_level1_workpack/level1_cst_export_checklist.csv
outputs/cst_level1_workpack/case_cards/
```

批量审计缺漏和行数：

```powershell
python code\merge_cst_level1_exports.py
```

必做标准源严格验收：

```powershell
python code\merge_cst_level1_exports.py --strict
```

若要要求 6 个计划案例全部齐全：

```powershell
python code\merge_cst_level1_exports.py --strict-all
```

完整案例的重建命令会写入：

```text
outputs/cst_level1_merge_report/level1_reconstruction_queue.csv
```

批量重建已完整必做标准源：

```powershell
python code\run_cst_level1_batch_reconstruction.py --priority required --require-cases --stop-on-error
```

针对 solver-safe FarfieldPlot-derived Level 1 导出，运行角域校准：

```powershell
python code\run_cst_level1_angular_calibration.py
```

输出：

```text
outputs/cst_level1_angular_calibration
```

说明：该步骤用 162 个半球方向 E-field 样本拟合 Legendre/Fourier 角域基函数，并预测 CST 远场网格。它用于证明 FarfieldPlot-derived 数据的角域一致性；不要把它写成 full-wave near-field monitor 反演。

仅生成队列、不执行重建：

```powershell
python code\run_cst_level1_batch_reconstruction.py --dry-run
```

同形合成 Level 1 闭环验证：

```powershell
python code\generate_synthetic_cst_level1_dataset.py

python code\merge_cst_level1_exports.py `
  --manifest outputs\synthetic_cst_level1_dataset\level1_case_manifest.csv `
  --report-dir outputs\synthetic_cst_level1_dataset\merge_report `
  --out-dir outputs\synthetic_cst_level1_dataset\merged `
  --strict-all

python code\check_cst_export.py `
  --nearfield outputs\synthetic_cst_level1_dataset\merged\all_nearfield.csv `
  --farfield outputs\synthetic_cst_level1_dataset\merged\all_farfield.csv `
  --json-out outputs\synthetic_cst_level1_dataset\validation_report.json

python code\run_cst_level1_batch_reconstruction.py `
  --case-status outputs\synthetic_cst_level1_dataset\merge_report\level1_case_status.csv `
  --out-root outputs\synthetic_cst_level1_dataset\reconstruction `
  --batch-dir outputs\synthetic_cst_level1_dataset\reconstruction_batch `
  --priority all `
  --require-cases
```

说明：该数据是 dipole surrogate，只验证 Python/CST 表格接口和批处理流程，不能作为真实 CST 评分证据。

Level 1 解析方向图 sanity reference：

```powershell
python code\build_level1_analytic_reference.py
```

输出：

```text
outputs/level1_analytic_reference
```

用途：真实 CST 标准源 farfield 到位后，辅助检查主瓣、坐标轴和极化约定是否明显错误；不替代严格审计和重建指标。

示例校验：

```powershell
python code\normalize_cst_complex_columns.py `
  --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield_phase.csv `
  --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield_phase.csv `
  --nearfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield-out data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv `
  --phase-unit deg `
  --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_phase_conversion.json

python code\check_cst_export.py `
  --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv `
  --json-out outputs\cst_reconstruction\L1_short_dipole_z_1p2G_validation.json
```

示例重建：

```powershell
python code\run_cst_reconstruction.py `
  --nearfield data\cst_exports\level1\L1_short_dipole_z_1p2G_nearfield.csv `
  --farfield data\cst_exports\level1\L1_short_dipole_z_1p2G_farfield.csv `
  --sample-id L1_short_dipole_z_1p2G `
  --frequency-hz 1200000000 `
  --out-dir outputs\cst_reconstruction\L1_short_dipole_z_1p2G
```

## 5. 重建鲁棒性扫描

```powershell
python code\run_reconstruction_robustness.py
```

输出：

```text
outputs/reconstruction_robustness
```

说明：当前脚本使用合成三源参考场。Level 1 solver-safe 数据已另用 `run_cst_level1_angular_calibration.py` 做角域一致性校准；若后续取得 full-wave near-field monitor 数据，再用本节思路复核测点/正则化结论。

## 6. CST 格式多状态识别 demo

生成合成 CST 格式数据：

```powershell
python code\generate_synthetic_cst_dataset.py
```

校验：

```powershell
python code\check_cst_export.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --farfield outputs\synthetic_cst_dataset\farfield_multistate.csv --json-out outputs\synthetic_cst_dataset\validation_report.json
```

识别：

```powershell
python code\run_cst_recognition.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_demo
```

测点/频点删减：

```powershell
python code\run_cst_recognition_ablation.py --nearfield outputs\synthetic_cst_dataset\nearfield_multistate.csv --labels outputs\synthetic_cst_dataset\labels.csv --out-dir outputs\cst_recognition_ablation
```

## 7. CST Level 2 执行清单

```powershell
python code\prepare_cst_level2_manifest.py
```

输出：

```text
outputs/cst_level2_plan
```

队员按下列文件在 CST 中建模和导出：

```text
outputs/cst_level2_plan/level2_case_manifest.csv
outputs/cst_level2_plan/level2_source_manifest.csv
outputs/cst_level2_plan/level2_labels.csv
```

生成半球面 Level 2 CST 任务包：

```powershell
python code\prepare_cst_level2_workpack.py
```

输出：

```text
outputs/cst_level2_workpack/level2_cst_sample_work_items.csv
outputs/cst_level2_workpack/level2_cst_frequency_tasks.csv
outputs/cst_level2_workpack/level2_cst_export_checklist.csv
outputs/cst_level2_workpack/case_cards/
```

## 8. CST 宏模板与 pilot 队列

```powershell
python code\prepare_cst_macro_templates.py
```

输出：

```text
outputs/cst_macro_templates
```

用途：

- `level1_required_launch_order.csv`：先执行 G2 的两个 required 标准源。
- `level2_pilot_cases.csv`：每类 1 个 pilot 样本，先验证再跑 48 个全量样本。
- `*.bas`：CST VBA 宏骨架，需要按本机 CST 版本适配具体 API。

## 9. CST 执行 dashboard 与真实数据 dropzone

```powershell
python code\build_cst_execution_dashboard.py
```

输出：

```text
outputs/cst_execution_dashboard
data/cst_exports
```

用途：

- `cst_execution_dashboard.md`：当前 G2/G3 状态、先跑哪些、导出到哪里。
- `level1_required_action_sheet.csv`：两个 Level 1 required 标准源的执行表。
- `level2_pilot_action_sheet.csv`：每类 1 个 Level 2 pilot 样本。
- `missing_real_cst_files.csv`：当前缺失的真实 CST nearfield/farfield 文件。

## 10. 真实 CST Level 2 full48、合并和识别

当前采用 solver-safe 的 Level 2 element-library full48 路线：CST 先求解 x/y/z 三方向短偶极子 element，再由 Python 按 Level 2 source manifest 叠加为 sample-level CSV。

生成或刷新 element 工程清单：

```powershell
python code\run_cst_level2_element_library.py --out-dir outputs\cst_level2_element_library --axes x,y,z --timeout-seconds 900
```

求解三方向 element 工程：

```powershell
python code\run_cst_solver_project.py `
  --project outputs\cst_level2_element_library\projects\CST_L2_element_short_dipole_x_5freq.cst `
  --out-dir outputs\cst_level2_element_trials\x_solver_safe `
  --trial-name CST_L2_element_short_dipole_x_5freq_solver_safe.cst `
  --summary-out outputs\cst_level2_element_trials\x_solver_safe\x_element_solver_summary.json `
  --stdout-log outputs\cst_level2_element_trials\x_solver_safe\x_element_solver_stdout.log `
  --timeout-seconds 900

python code\run_cst_solver_project.py `
  --project outputs\cst_level2_element_library\projects\CST_L2_element_short_dipole_y_5freq.cst `
  --out-dir outputs\cst_level2_element_trials\y_solver_safe `
  --trial-name CST_L2_element_short_dipole_y_5freq_solver_safe.cst `
  --summary-out outputs\cst_level2_element_trials\y_solver_safe\y_element_solver_summary.json `
  --stdout-log outputs\cst_level2_element_trials\y_solver_safe\y_element_solver_stdout.log `
  --timeout-seconds 900

python code\run_cst_solver_project.py `
  --project outputs\cst_level2_element_library\projects\CST_L2_element_short_dipole_z_5freq.cst `
  --out-dir outputs\cst_level2_element_trials\z_solver_safe `
  --trial-name CST_L2_element_short_dipole_z_5freq_solver_safe.cst `
  --summary-out outputs\cst_level2_element_trials\z_solver_safe\z_element_solver_summary.json `
  --stdout-log outputs\cst_level2_element_trials\z_solver_safe\z_element_solver_stdout.log `
  --timeout-seconds 900
```

导出缺失样本。若只导出单个样本，用 `--sample-id <sample_id>`；若批量补齐剩余样本，用：

```powershell
python code\export_cst_level2_superposed_results.py `
  --all-samples `
  --missing-only `
  --summary-out outputs\cst_level2_superposed_export\level2_remaining_missing_batch_summary.json `
  --stdout-log outputs\cst_level2_superposed_export\level2_remaining_missing_batch_stdout.log `
  --timeout-seconds 7200
```

当前已完成 48 个样本；批量 summary 为 `outputs/cst_level2_superposed_export/level2_remaining_missing_batch_summary.json`。

将每个 sample_id 的导出放入 manifest 指定路径：

```text
data/cst_exports/level2/<sample_id>_nearfield.csv
data/cst_exports/level2/<sample_id>_farfield.csv
```

非严格缺漏报告：

```powershell
python code\merge_cst_level2_exports.py
```

严格验收：

```powershell
python code\merge_cst_level2_exports.py --strict
```

真实 Level 2 识别：

```powershell
python code\run_cst_recognition.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2
```

真实 Level 2 删减验证：

```powershell
python code\run_cst_recognition_ablation.py --nearfield data\cst_exports\level2\all_nearfield.csv --labels outputs\cst_level2_plan\level2_labels.csv --out-dir outputs\cst_recognition_level2_ablation
```

当前 full48 验证结果：48/48 个完整样本，合并 nearfield 116640 行，farfield 164160 行；full48 识别 accuracy=`1.000`，5/3/1 频点与 100/75/50/25% 测点组合均为 `1.000`。这不是最终 full-wave 复杂载体结构证据，需结合下一节的简化结构遮挡对照说明边界。

## 11. CST Level 2 简化结构遮挡对照

在 Level 2 full48 数据已合并后运行：

```powershell
python code\run_cst_structure_comparison.py
```

输出：

```text
outputs/cst_structure_comparison
```

核心文件：

| 文件 | 用途 |
|---|---|
| `structure_aware_nearfield.csv` | 施加简化机身/机翼/尾翼遮挡迁移后的 Level 2 nearfield |
| `structure_aware_farfield.csv` | 施加简化遮挡迁移后的 Level 2 farfield |
| `structure_comparison_metrics.csv` | 每个 sample/frequency 的方向图偏差、遮挡和主瓣变化 |
| `structure_effect_by_class.csv` | 按四类运行状态统计结构遮挡效应 |
| `structure_recognition_metrics.json` | 无结构训练、简化结构测试的 cross-domain 识别结果 |
| `plots/*_structure_compare.png` | 代表样本方向图对照图 |

当前结果：mean shadow 约 `3.06 dB`，P95 shadow 约 `6.63 dB`，max shadow 约 `13.33 dB`，cross-domain accuracy=`1.000`。该步骤是 simplified aircraft occlusion transfer，不是 full-wave CST airframe scattering。

## 12. 汇总与最终提交检查

生成 CST 真实执行日志模板：

```powershell
python code\prepare_cst_execution_log_templates.py
python code\build_cst_execution_dashboard.py
```

评分证据板：

```powershell
python code\build_scorecard.py
```

赛题要求-证据矩阵：

```powershell
python code\build_problem_requirements_matrix.py
```

报告成稿素材包：

```powershell
python code\build_report_package.py
```

生成正式报告 DOCX：

```powershell
python code\build_final_report_docx.py
```

当前正式报告 PDF 由本机 Microsoft Word COM 从 `submission\01_report\solution_report.docx` 导出；导出后用 `pdftoppm` 渲染页面并检查 `outputs\final_report\final_report_contact_sheet.png`。

答辩 PPT 与演示视频素材包：

```powershell
python code\build_presentation_package.py
```

生成正式答辩 PPTX：

```powershell
python code\build_defense_pptx_artifact.py
```

PPT layout 检查：

```powershell
node C:\Users\heh20\.codex\plugins\cache\openai-primary-runtime\presentations\26.521.10419\skills\presentations\scripts\check_layout_quality.mjs --layout outputs\019e6c77-5e27-7972-93a0-90d6bdd77225\presentations\cs202614-defense\layout\final
```

当前正式答辩 PDF 由本机 Microsoft PowerPoint COM 从 `submission\02_presentation\defense_slides.pptx` 导出；导出后用 `pdftoppm` 渲染页面并检查 `outputs\presentation_artifact\defense_slides_pdf_contact_sheet.png`。

生成演示视频 MP4：

```powershell
powershell -ExecutionPolicy Bypass -File .\src\export_demo_video_powerpoint.ps1
```

当前脚本默认生成自动计时静音版 MP4；如本机 SAPI 语音可用，可尝试追加 `-WithNarration`。

生成最终提交压缩包：

```powershell
python code\build_final_archive.py
```

压缩包完整性检查：

```powershell
python -c "import zipfile; z=zipfile.ZipFile('outputs/final_archive/CS-202614_submission.zip'); print(z.testzip(), len(z.infolist()))"
```

最终提交索引：

```powershell
python code\build_submission_index.py
```

完成度审计：

```powershell
python code\build_completion_audit.py
```

总控 dashboard：

```powershell
python code\build_master_dashboard.py
```

项目进展跟踪和导师汇报：

```powershell
python code\build_progress_report.py --note "本阶段完成了某项关键进展"
```

脚本会同步刷新 `docs/progress_reports/mentor_portal.md` 导师阅读门户、`docs/progress_reports/meeting_brief.md` 组会汇报稿、`docs/progress_reports/daily_digest.md` 每日进展汇总、`docs/progress_reports/evidence_map.md` 导师证据映射、`docs/progress_reports/decision_brief.md` 导师决策清单、`docs/progress_reports/mentor_qa.md` 导师问答卡、`docs/progress_reports/g5_closure_brief.md` G5 关闭路线、`docs/progress_reports/mentor_snapshot.md` 导师 30 秒快照、`docs/progress_reports/latest_change_note.md` 本次变化说明、`docs/progress_reports/next_action_brief.md` 下一步行动清单、`docs/progress_reports/risk_register.md` 风险登记表、`docs/progress_reports/submission_readiness.md` 提交就绪清单、`docs/progress_reports/progress_index.md` 阶段时间线和 `docs/progress_reports/latest_mentor_brief.md` 最新导师汇报固定入口；`docs/progress_reports/watch_scope.md` 记录长期巡检覆盖的关键文件和最终交付物，`docs/progress_reports/progress_update_protocol.md` 记录阶段标记、跳过复核、submission 同步和汇报口径规则，`docs/progress_reports/status_review_log.md` 记录无变化巡检台账。

若只是定时巡检，且希望无变化时不新增阶段归档：

```powershell
python code\build_progress_report.py --only-if-changed
```

CST G2 真机操作包：

```powershell
python code\build_cst_operator_runbook.py
```

生成当前提交草稿包：

```powershell
python code\build_submission_draft.py
```

输出：

```text
outputs/scorecard
outputs/problem_requirements
outputs/report_package
outputs/final_report
outputs/presentation_package
outputs/presentation_artifact
outputs/video_artifact
outputs/final_archive
outputs/submission_index
outputs/completion_audit
outputs/master_dashboard
outputs/progress_report
outputs/cst_operator_runbook
outputs/cst_execution_dashboard
data/cst_exports
docs/project_progress_report.md
docs/progress_reports
submission
```

正式提交前必须确保：

1. `outputs/scorecard/scorecard.md` 不再只依赖 synthetic/demo 证据。
2. `outputs/submission_index/submission_package_index.md` 中 CST 和 data 项不再 blocked。
3. `submission/01_report/solution_report.pdf`、`submission/01_report/solution_report.docx`、`submission/02_presentation/defense_slides.pptx`、`submission/02_presentation/defense_slides.pdf` 和 `submission/03_video/demo_video.mp4` 都存在并通过人工预览。
4. `outputs/completion_audit/completion_audit_summary.json` 中 `completion_proven=true`。
5. 报告、PPT、视频中的指标一致。
