# S25 最终压缩包与校验清单

## 做了什么

本阶段把 `submission` 目录打包为最终技术提交压缩包，并生成文件级校验清单：

- `outputs/final_archive/CS-202614_submission.zip`
- `outputs/final_archive/final_archive_manifest.csv`
- `outputs/final_archive/final_archive_summary.json`
- `submission/README_FINAL_SUBMISSION.md`

压缩包已通过 Python `zipfile.testzip()` 完整性检查，返回 `bad=None`。

## 为什么这样做

前一阶段已经完成报告、PPT、MP4 和审计闭环，但“完成赛题”还需要一个可交付的压缩包。手工压缩不利于复现，也无法留下清单和 hash，因此本阶段新增 `code/build_final_archive.py`，用脚本完成：

1. 写入最终提交 README。
2. 遍历 `submission` 目录。
3. 生成每个文件的 SHA256。
4. 打包为统一 zip。
5. 生成压缩包级 SHA256 和摘要 JSON。

## 产物与文件意义

| 文件 | 意义 |
|---|---|
| `code/build_final_archive.py` | 最终归档脚本，负责 README、manifest、zip 和 SHA256。 |
| `docs/admin_submission_template.md` | 人工报名与提交信息模板。 |
| `submission/00_admin/admin_submission_template.md` | 提交包内的人工信息模板副本。 |
| `outputs/final_archive/CS-202614_submission.zip` | 当前可提交技术压缩包。 |
| `outputs/final_archive/final_archive_manifest.csv` | 压缩包来源文件清单，含相对路径、大小和 SHA256。 |
| `outputs/final_archive/final_archive_summary.json` | 压缩包摘要、hash、文件数、人工事项。 |
| `submission/README_FINAL_SUBMISSION.md` | 提交包内最终说明和人工提交前检查清单。 |

## 关键结果

| 指标 | 当前值 |
|---|---:|
| zip 文件数 | 5102 |
| 未压缩总大小 | 677,197,711 bytes |
| zip 大小 | 146,109,517 bytes |
| archive SHA256 | `5f7388754f9bf17ce7ce09697e92fbb4d33786dd0196a18c0ff731eb6c181d84` |
| expected_missing | 0 |
| completion_proven | true |
| is_final_archive | true |
| zip integrity | bad=None |

## 如何验证

生成压缩包：

```powershell
python code\build_final_archive.py
```

检查压缩包完整性：

```powershell
python -c "import zipfile; z=zipfile.ZipFile('outputs/final_archive/CS-202614_submission.zip'); print(z.testzip(), len(z.infolist()))"
```

本阶段输出为：

```text
bad=None
count=5102
```

## 对总目标的影响

本阶段把“有交付目录”推进为“有可提交 zip、可核验清单和 hash”。技术侧已经具备完整提交条件：`completion_proven=true`、`submission_blocked=0`、最终报告/PPT/视频/代码/CST/data/附录齐套。

## 仍需人工确认

以下事项不是算法或文件生成问题，但正式报送前必须由队伍人工处理：

1. 完整播放 `submission/03_video/demo_video.mp4`。
2. 若竞赛要求讲解录屏，替换当前自动计时静音版 MP4。
3. 补齐学校、队名、申报人、电话、邮箱、报名表等真实信息。
4. 按赛事系统或邮箱要求重命名 zip。
