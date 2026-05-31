# S11 答辩 PPT 与演示视频素材包说明

## 做了什么

本阶段新增答辩 PPT 和演示视频素材包，包含 12 页答辩 storyboard、逐页讲稿、图表来源、替换要求、3-5 分钟视频分镜和素材清单。当前不生成最终 PPTX/MP4，避免把 demo/synthetic 占位误认为正式结果。

## 为什么这样做

最终提交不仅需要报告和代码，还需要 PPT 与视频。如果等真实 CST 数据全部到位后再临时组织叙事，会非常容易漏掉评分项或图表替换。先做 storyboard，可以把每一页/每一段视频都绑定到证据和 final gate。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/build_presentation_package.py` | 生成 PPT/视频素材包 | 报告素材或证据状态变化后重新运行 |
| `outputs/presentation_package/README_presentation_package.md` | 素材包说明 | 先读这里 |
| `outputs/presentation_package/defense_slide_storyboard.csv` | 12 页答辩 PPT 结构、视觉类型、证据来源和 final gate | 制作 PPTX 的主表 |
| `outputs/presentation_package/defense_slide_storyboard.md` | 人读版逐页讲稿 | 答辩排练与内容审查 |
| `outputs/presentation_package/demo_video_storyboard.csv` | 视频时间轴、画面、解说和替换要求 | 录制演示视频前检查 |
| `outputs/presentation_package/demo_video_storyboard.md` | 人读版视频脚本 | 录制时照着讲 |
| `outputs/presentation_package/presentation_asset_manifest.csv` | 当前可用图表素材 | 区分 draft 图和 final 图 |
| `outputs/presentation_package/presentation_replacement_todo.csv` | 真实 CST 与最终导出前任务 | 成稿前逐项清零 |

## 验证方式

```powershell
python code\build_presentation_package.py
python code\build_submission_index.py
python code\build_completion_audit.py
```

当前结果：

- PPT 页数：12。
- 视频分镜：7 段。
- 已存在 draft 素材：6 个。
- final-ready slides：0。
- 下一阻塞 gate：G2。

## 当前不足

- 没有生成 `defense_slides.pptx` 和 `demo_video.mp4`。
- 5 页左右仍依赖 demo/synthetic 图，必须由真实 CST 图替换。
- 答辩中所有核心数值必须等真实 Level 1/Level 2 审计通过后再写入。

## 下一步

1. 完成 G2 后替换标准源重建图和指标。
2. 完成 G3 后替换识别混淆矩阵和删减曲线。
3. 运行 completion audit 为 true 后再生成最终 PPTX/PDF/MP4。
