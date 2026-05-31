# S15 赛题要求到证据矩阵

## 做了什么

- 新增 `code/build_problem_requirements_matrix.py`，把赛题 PDF 中的交付物、报告内容、40 分主观项、60 分客观项、提交时间和提交方式整理成矩阵。
- 生成赛题要求矩阵、交付物检查表和机器可读摘要。
- 将该矩阵接入总控 dashboard、completion audit、提交索引、提交草稿包、复现命令和项目文件索引。

## 为什么这样做

- 总目标是完成赛题，最终不能只看我们自己定义的阶段是否完成，必须逐条对照赛题原文。
- 评分项中既有算法/CST 硬指标，也有报告、PPT、视频、代码、提交命名、报名表等交付要求。
- 该矩阵能避免后期出现“技术结果做了，但交付材料或提交规则漏了”的问题。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_problem_requirements_matrix.py` | 赛题要求矩阵生成脚本 | 每次 scorecard、submission index 或 completion audit 更新后运行 |
| `outputs/problem_requirements/problem_requirements_matrix.md` | 人可读的赛题要求-证据矩阵 | 对照原文判断缺口 |
| `outputs/problem_requirements/problem_requirements_matrix.csv` | 逐条 requirement 机器可读表 | 可并入最终审计/汇报 |
| `outputs/problem_requirements/problem_deliverable_checklist.csv` | 报告、PPT、视频、代码、CST、压缩包交付物检查表 | 打包前逐项核验 |
| `outputs/problem_requirements/problem_requirements_summary.json` | 要求数量、分值和缺口数摘要 | 供总控 dashboard 读取 |

## 验证方式

```powershell
python -m compileall src\build_problem_requirements_matrix.py
python code\build_problem_requirements_matrix.py
```

本阶段验证结果：

- requirement_count：12
- deliverable_count：7
- subjective_points：40
- objective_points：60
- total_scored_points：100
- blocked_or_missing_count：7
- completion_proven：false

## 当前不足

- 矩阵证明“我们知道要交什么、怎么评”，但不替代真实 CST 证据。
- 所有 requirement 当前都不是最终 ready，因为真实 CST、最终 PDF/DOCX/PPTX/MP4、人工报名信息和压缩包提交仍未完成。
- 提交命名、学校全称、申报人姓名、电话和报名表扫描件需要队伍最终人工补充。

## 下一步

1. 按 `outputs/master_dashboard/master_status_dashboard.md` 先关闭 G2。
2. 每完成一个真实 CST 或交付物阶段，重跑 `build_problem_requirements_matrix.py`。
3. 最终提交前用 `problem_deliverable_checklist.csv` 和 `submission_checklist.csv` 双重核验。
