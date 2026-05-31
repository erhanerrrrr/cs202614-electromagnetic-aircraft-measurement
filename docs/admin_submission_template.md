# 人工报名与提交信息模板

本文件用于正式提交前由队伍人工填写。技术包已由脚本生成，但以下信息不能由自动化脚本替代。

## 基本信息

| 项目 | 填写内容 |
|---|---|
| 赛题编号 | CS-202614 |
| 赛题名称 | 复杂航空载体电磁辐射空域特性测量技术 |
| 学校/单位 | 待填写 |
| 队伍名称 | 待填写 |
| 申报人/负责人 | 待填写 |
| 联系电话 | 待填写 |
| 邮箱 | 待填写 |
| 指导教师 | 待填写 |
| 队员 1 | 待填写 |
| 队员 2 | 待填写 |
| 队员 3 | 待填写 |

## 最终文件确认

| 文件 | 当前路径 | 人工确认 |
|---|---|---|
| 方案报告 PDF | `submission/01_report/solution_report.pdf` | 待确认 |
| 方案报告 DOCX | `submission/01_report/solution_report.docx` | 待确认 |
| 答辩 PPTX | `submission/02_presentation/defense_slides.pptx` | 待确认 |
| 答辩 PDF | `submission/02_presentation/defense_slides.pdf` | 待确认 |
| 演示视频 MP4 | `submission/03_video/demo_video.mp4` | 待确认 |
| 最终压缩包 | `outputs/final_archive/CS-202614_submission.zip` | 待确认 |

## 视频确认

当前 MP4 是 PowerPoint 自动计时静音版。正式提交前请确认：

- 是否完整播放无黑屏、错页、卡顿。
- 是否需要替换为带人工讲解或旁白的录屏。
- 如替换视频，重新运行：

```powershell
python code\build_submission_draft.py
python code\build_final_archive.py
python code\build_completion_audit.py
```

## 压缩包命名

当前自动生成文件：

```text
outputs/final_archive/CS-202614_submission.zip
```

如赛事系统或邮箱要求包含学校、队名、申报人，请在提交前复制并重命名，不要直接删除原始归档文件。

建议命名模板：

```text
CS-202614_<学校>_<队名>_<申报人>_复杂航空载体电磁辐射空域特性测量技术.zip
```

## 最后复核

| 检查项 | 结果 |
|---|---|
| `completion_proven=true` | 待确认 |
| `submission_blocked=0` | 待确认 |
| zip 可正常解压 | 待确认 |
| 报名表/系统信息已填写 | 待确认 |
| 文件命名符合赛事要求 | 待确认 |
