# S00 项目结构说明

## 做了什么

本阶段把当前工作区整理为“代码、文档、CST、文献、数据、输出证据、提交草稿”几条主线，并新增/补齐目录说明。主源码入口已调整为 `code/`；大型 CST 求解缓存和自动生成结果仍保留在 `outputs/` 与 `submission/` 的既有路径中，用 `.gitignore` 控制 GitHub 协作范围，避免破坏已形成的审计和复现链。

## 为什么这样做

赛题周期较长，产物会持续增加。若直接移动文件，容易导致脚本路径、报告引用和复现命令失效。当前整理策略是：

- 保持 `code`、`docs`、`data`、`outputs` 四个核心目录的职责清晰。
- 用 `CST`、`文档`、`文献` 作为人读入口，分别解释 CST 工作流、Word/PDF/PPT 材料和文献依据。
- 用 `submission` 预排最终提交目录，方便检查报告、代码、CST、数据和附录是否齐套。
- 用 `docs/project_file_index.md` 解释各目录意义。
- 用 `docs/stage_notes` 对每一阶段分别说明。
- 后续若确需移动文件，先更新脚本路径和复现命令，再移动。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `README.md` | 项目总入口和常用命令 | 从这里了解当前路线、主要脚本和下一步 |
| `code` | Python 算法、CST 接口、manifest、审计和索引脚本 | 运行复现、生成计划、校验数据 |
| `CST` | CST 建模/自动化入口索引 | 查找 CST 模板、工程、导出和 Python 调 CST 流程 |
| `docs` | 方案文档、规程、数据字典、阶段说明 | 写报告和给队友交接 |
| `文档` | 原始赛题和历史 Word/PDF 材料 | 人工阅读和交付核对 |
| `文献` | 文献矩阵与新增推荐文献入口 | 支撑调研和未来方案 |
| `outputs` | 所有脚本生成的证据、图表、manifest、审计结果 | 作为报告/PPT/提交包素材 |
| `submission` | 当前提交草稿包 | 检查最终材料结构和缺口 |
| `docs/stage_notes` | 分阶段说明 | 每完成阶段后更新 |
| `docs/project_file_index.md` | 文件组织总览 | 查找文件含义和阅读顺序 |

## 验证方式

```powershell
python -m compileall code
python code\build_scorecard.py
python code\build_submission_index.py
python code\build_completion_audit.py
python code\build_submission_draft.py
```

## 当前不足

- 真实 CST 工程和导出尚未补齐，因此最终提交物仍不能成稿。
- `submission` 目前只是草稿结构，正式 PDF/DOCX/PPTX/MP4 还没有生成。

## 下一步

1. 继续保持新增源码进入 `code`，新增方案/说明进入 `docs`，真实 CST 导出进入 `data`，自动生成结果进入 `outputs`，并通过 `submission` 汇总成提交草稿。
2. 每次新增阶段产物，同步更新阶段说明和文件索引。
