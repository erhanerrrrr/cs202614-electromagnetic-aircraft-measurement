# S24 演示视频 MP4 导出

## 做了什么

本阶段生成了 G5 所需的演示视频文件：

- `submission/03_video/demo_video.mp4`

视频由最终答辩 PPTX 自动计时导出，来源为：

- `submission/02_presentation/defense_slides.pptx`

当前视频为自动计时静音版，计划时长 171 秒，Windows Shell 读取时长为 `00:02:51`。它解决了“没有 MP4 文件”的提交缺口，但正式提交前仍建议人工完整播放一次；如果竞赛明确要求讲解录屏或语音讲解，应优先替换为带人工讲解或可听旁白的版本。

## 为什么这样做

本机环境没有 `ffmpeg`，Python 环境中也没有 `moviepy`、`imageio_ffmpeg` 或 `cv2`。为避免引入新的网络依赖，本阶段采用本机 PowerPoint 的 `CreateVideo` 能力，从已经通过 layout 检查的 PPTX 直接导出 MP4。

曾尝试使用 Windows SAPI 中文语音生成旁白，但当前 SAPI COM 在本会话中返回 `HRESULT: 0x8004503A`，无法稳定输出 WAV。因此本阶段保守生成静音自动播放版，并在审计摘要中明确标记 `has_narration=false`。

## 产物与文件意义

| 文件 | 意义 |
|---|---|
| `code/export_demo_video_powerpoint.ps1` | 使用 PowerPoint COM 设置自动放映时长并导出 MP4 的脚本；可选 `-WithNarration`，但当前 SAPI 旁白不可用。 |
| `submission/03_video/demo_video.mp4` | 当前演示视频 MP4，自动计时静音版。 |
| `outputs/video_artifact/demo_video_summary.json` | 视频来源、时长、文件大小、PowerPoint 导出状态、是否有旁白和 QA 备注。 |
| `outputs/video_artifact/defense_slides_with_timing_and_narration.pptx` | 带自动切页时长的 PPTX 中间文件。 |
| `outputs/video_artifact/narration/` | 旁白 WAV 预留目录；当前无有效音频文件。 |

## 关键指标

| 指标 | 当前值 |
|---|---:|
| slide_count | 12 |
| planned_duration_seconds | 171 |
| Windows Shell 时长 | 00:02:51 |
| PowerPoint CreateVideo status | 3 |
| MP4 文件大小 | 7,856,755 bytes |
| has_narration | false |

## 如何验证

导出命令：

```powershell
powershell -ExecutionPolicy Bypass -File .\src\export_demo_video_powerpoint.ps1
```

文件存在性和时长检查：

```powershell
Get-Item submission\03_video\demo_video.mp4
```

本阶段还通过 Windows Shell 扩展属性读取到 `Length = 00:02:51`，说明 MP4 元数据可被系统识别。

## 对总目标的影响

本阶段补齐了 G5 的最后一个文件缺口。后续重跑完成度审计后，`completion_audit_summary.json` 应从 `7 complete / 1 partial` 推进到 `8 complete / 0 partial`。不过，自动静音视频仍存在展示质量风险，正式报送前建议由队员人工播放检查并视竞赛要求替换为带讲解版本。

## 下一步

1. 重跑 report package、presentation package、submission index、completion audit、problem requirements、master dashboard 和 submission draft。
2. 检查 `outputs/completion_audit/completion_audit_summary.json` 是否为 `completion_proven=true`。
3. 人工完整播放 `submission/03_video/demo_video.mp4`。
4. 若确认视频质量可接受，再整理最终压缩包命名、报名表和人工提交信息。
