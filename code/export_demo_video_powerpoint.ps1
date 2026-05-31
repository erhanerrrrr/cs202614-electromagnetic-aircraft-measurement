param(
    [string]$PptxPath = "submission\02_presentation\defense_slides.pptx",
    [string]$VideoPath = "submission\03_video\demo_video.mp4",
    [string]$OutDir = "outputs\video_artifact",
    [switch]$WithNarration
)

$ErrorActionPreference = "Stop"

function Resolve-ProjectPath([string]$PathText) {
    if ([System.IO.Path]::IsPathRooted($PathText)) {
        return $PathText
    }
    return (Join-Path (Get-Location) $PathText)
}

function Get-WavDurationSeconds([string]$PathText) {
    $bytes = [System.IO.File]::ReadAllBytes($PathText)
    $ascii = [System.Text.Encoding]::ASCII.GetString($bytes)
    $fmt = $ascii.IndexOf("fmt ")
    $data = $ascii.LastIndexOf("data")
    if ($fmt -lt 0 -or $data -lt 0) {
        return 12
    }
    $byteRate = [System.BitConverter]::ToInt32($bytes, $fmt + 16)
    $dataSize = [System.BitConverter]::ToInt32($bytes, $data + 4)
    if ($byteRate -le 0) {
        return 12
    }
    return [Math]::Ceiling($dataSize / $byteRate) + 1
}

$pptx = Resolve-ProjectPath $PptxPath
$video = Resolve-ProjectPath $VideoPath
$out = Resolve-ProjectPath $OutDir
$narrationDir = Join-Path $out "narration"
$timedPptx = Join-Path $out "defense_slides_with_timing_and_narration.pptx"
$summaryPath = Join-Path $out "demo_video_summary.json"

New-Item -ItemType Directory -Force -Path (Split-Path $video) | Out-Null
New-Item -ItemType Directory -Force -Path $narrationDir | Out-Null
if (-not $WithNarration) {
    Get-ChildItem -Path $narrationDir -Filter "*.wav" -ErrorAction SilentlyContinue | Remove-Item -Force
}

$slideNotes = @(
    "本方案面向复杂航空载体电磁辐射空域测量，采用半球面二派测量和 CST Python 闭环，支撑三维场重建、少测点优化和多源状态识别。",
    "赛题的一百分评分项已经映射到可审计文件。当前报告和答辩材料已生成，视频是最后一个 G5 文件缺口。",
    "方法不是从零拼装，而是从标准近场测量、等效源重构、压缩采样和射频指纹识别四条文献主线迁移到赛题。",
    "总体路线由 CST 负责可信电磁数据源，Python 负责导出校验、重建、识别和审计闭环，保证结果可复现。",
    "当前选择十三米半径上半球面，一百六十二个测点覆盖十二米乘十米乘八米被测包络，半柱面保留为工程扩展。",
    "Level 1 标准源的 FarfieldPlot 角域样本与 CST 远场真值高度一致；同时我们保守说明近场等效源反演的 full wave 模型边界。",
    "重建算法把有限半球面观测转成等效源，再用正则化控制病态反演，输出可外推远场方向图和误差指标。",
    "少测点实验显示七十五百分比测点更稳，五十百分比可作为压缩候选，二十五百分比只保留为极限对照。",
    "Level 2 使用空间、频率和极化联合特征，四十八个 CST derived 样本上识别准确率达到一，超过百分之八十五指标线。",
    "简化结构遮挡会改变方向图，但当前特征在跨域测试中仍保持稳定；该证据不是 full wave airframe scattering。",
    "创新点集中在受限域等效源、半球面少测点、空频极化指纹和 CST Python 可复现审计的组合。",
    "当前技术证据已经基本齐套，最终提交还需要由本视频和后续压缩包审计关闭 G5。"
)

$durations = @(14, 12, 14, 13, 13, 17, 15, 15, 15, 16, 13, 14)
$audioGenerated = $false
$selectedVoiceDescription = "not requested"

if ($WithNarration) {
    try {
        $voice = New-Object -ComObject SAPI.SpVoice
        $selectedVoice = $null
        foreach ($candidate in $voice.GetVoices()) {
            if ($candidate.GetDescription() -like "*Chinese*") {
                $selectedVoice = $candidate
                break
            }
        }
        if ($selectedVoice -ne $null) {
            $voice.Voice = $selectedVoice
            $selectedVoiceDescription = $selectedVoice.GetDescription()
        }
        $voice.Rate = 0
        $voice.Volume = 100

        $generatedDurations = @()
        for ($i = 0; $i -lt $slideNotes.Count; $i++) {
            $wav = Join-Path $narrationDir ("slide-{0:D2}.wav" -f ($i + 1))
            $stream = New-Object -ComObject SAPI.SpFileStream
            $stream.Open($wav, 3, $false)
            $voice.AudioOutputStream = $stream
            [void]$voice.Speak($slideNotes[$i], 0)
            $stream.Close()
            $voice.AudioOutputStream = $null
            $duration = [double](Get-WavDurationSeconds $wav)
            if ($duration -lt 8) { $duration = 8 }
            if ($duration -gt 28) { $duration = 28 }
            $generatedDurations += $duration
        }
        $durations = $generatedDurations
        $audioGenerated = $true
    }
    catch {
        Write-Warning "Narration generation failed; exporting a silent timed MP4 instead. $($_.Exception.Message)"
        $audioGenerated = $false
    }
}

$pp = New-Object -ComObject PowerPoint.Application
$deck = $null
try {
    $pp.Visible = 1
    $deck = $pp.Presentations.Open($pptx, $true, $false, $false)
    if ($deck.Slides.Count -ne $slideNotes.Count) {
        throw "Slide count $($deck.Slides.Count) does not match narration count $($slideNotes.Count)."
    }

    for ($i = 1; $i -le $deck.Slides.Count; $i++) {
        $slide = $deck.Slides.Item($i)
        $slide.SlideShowTransition.AdvanceOnClick = $false
        $slide.SlideShowTransition.AdvanceOnTime = $true
        $slide.SlideShowTransition.AdvanceTime = [double]$durations[$i - 1]
        if ($audioGenerated) {
            $wav = Join-Path $narrationDir ("slide-{0:D2}.wav" -f $i)
            $slide.SlideShowTransition.SoundEffect.ImportFromFile($wav)
        }
    }

    $deck.SaveAs($timedPptx)
    if (Test-Path $video) {
        Remove-Item -LiteralPath $video -Force
    }
    $totalDuration = [Math]::Ceiling(($durations | Measure-Object -Sum).Sum)
    $deck.CreateVideo($video, $true, 10, 720, 24, 85)

    $deadline = (Get-Date).AddMinutes(20)
    do {
        Start-Sleep -Seconds 5
        $status = [int]$deck.CreateVideoStatus
        if ((Get-Date) -gt $deadline) {
            throw "Timed out waiting for PowerPoint video export. Last status: $status"
        }
    } while ($status -eq 1 -or $status -eq 2)

    if ($status -ne 3 -or -not (Test-Path $video)) {
        throw "PowerPoint video export failed. Status: $status"
    }

    $item = Get-Item $video
    $summary = [ordered]@{
        video = (Resolve-Path $video).Path
        source_pptx = (Resolve-Path $pptx).Path
        timed_pptx = (Resolve-Path $timedPptx).Path
        narration_dir = (Resolve-Path $narrationDir).Path
        slide_count = $deck.Slides.Count
        audio_file_count = if ($audioGenerated) { $slideNotes.Count } else { 0 }
        has_narration = $audioGenerated
        planned_duration_seconds = $totalDuration
        powerpoint_create_video_status = $status
        length_bytes = $item.Length
        last_write_time = $item.LastWriteTime.ToString("s")
        voice = $selectedVoiceDescription
        visual_source = "submission\\02_presentation\\defense_slides.pptx"
        is_final_video = $true
        qa_note = if ($audioGenerated) { "Auto-generated narrated MP4 from final PPTX using PowerPoint CreateVideo; recommend one human playback before submission." } else { "Auto-generated silent timed MP4 from final PPTX using PowerPoint CreateVideo; recommend replacing with a narrated recording if contest rules expect voiceover." }
    }
    $summary | ConvertTo-Json -Depth 4 | Set-Content -Path $summaryPath -Encoding UTF8
    $summary | ConvertTo-Json -Depth 4
}
finally {
    if ($deck -ne $null) {
        try { $deck.Close() } catch {}
    }
    if ($pp -ne $null) {
        try { $pp.Quit() } catch {}
    }
}



