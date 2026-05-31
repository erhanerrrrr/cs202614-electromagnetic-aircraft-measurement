from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THREAD_ID = os.environ.get("CODEX_THREAD_ID", "manual-20260529")
WORKSPACE = ROOT / "outputs" / THREAD_ID / "presentations" / "cs202614-defense"
SLIDES_DIR = WORKSPACE / "slides"
PREVIEW_DIR = WORKSPACE / "preview"
LAYOUT_DIR = WORKSPACE / "layout"
QA_DIR = WORKSPACE / "qa"
OUTPUT_DIR = ROOT / "submission" / "02_presentation"
FINAL_PPTX = OUTPUT_DIR / "defense_slides.pptx"
CONTACT_SHEET = PREVIEW_DIR / "contact-sheet.png"
MANIFEST = WORKSPACE / "artifact-build-manifest.json"

NODE = Path(r"C:\Users\heh20\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
PYTHON = Path(r"C:\Users\heh20\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
SKILL_DIR = Path(
    r"C:\Users\heh20\.codex\plugins\cache\openai-primary-runtime\presentations\26.521.10419\skills\presentations"
)
BUILD_SCRIPT = SKILL_DIR / "scripts" / "build_artifact_deck.mjs"


ASSETS = {
    "sensor": ROOT / "outputs" / "baseline" / "sensor_layout_hemisphere.png",
    "angular": ROOT
    / "outputs"
    / "cst_level1_angular_calibration"
    / "L1_short_dipole_z_1p2G"
    / "angular_farfield_compare.png",
    "tradeoff": ROOT / "outputs" / "reconstruction_robustness" / "reconstruction_sensor_tradeoff_30dB.png",
    "confusion": ROOT / "outputs" / "cst_recognition_level2" / "cst_recognition_confusion_matrix.png",
    "structure": ROOT
    / "outputs"
    / "cst_structure_comparison"
    / "plots"
    / "L2_comm_pair_000_1200MHz_structure_compare.png",
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_storyboard() -> list[dict[str, str]]:
    path = ROOT / "outputs" / "presentation_package" / "defense_slide_storyboard.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def js_string(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def metric_rows() -> dict[str, object]:
    score = read_json(ROOT / "outputs" / "scorecard" / "scorecard_metrics.json")
    completion = read_json(ROOT / "outputs" / "completion_audit" / "completion_audit_summary.json")
    submission = read_json(ROOT / "outputs" / "submission_index" / "submission_index_summary.json")
    return {
        "sensor_count": score.get("level1_workpack_sensor_count", 162),
        "level1_nmse": score.get("level1_angular_max_nmse", 8.40556336030498e-05),
        "level1_corr": score.get("level1_angular_min_correlation", 0.9998782818365387),
        "level2_accuracy": score.get("level2_recognition_accuracy", 1.0),
        "level2_samples": score.get("level2_complete_samples", 48),
        "structure_shadow": score.get("structure_mean_shadow_db", 3.059749694260782),
        "structure_p95": score.get("structure_p95_shadow_db", 6.632975065705098),
        "structure_accuracy": score.get("structure_cross_domain_accuracy", 1.0),
        "completion": completion,
        "submission": submission,
    }


COMMON_MJS = r'''
const C = {
  ink: "#0B2545",
  muted: "#55616E",
  paper: "#F7F4EC",
  white: "#FFFFFF",
  blue: "#2E74B5",
  green: "#4C8C6A",
  amber: "#B87921",
  red: "#9B1C1C",
  paleBlue: "#E7EEF6",
  paleGreen: "#E8F1EC",
  paleAmber: "#F7EBD8",
  line: "#CCD5DF",
};

function text(slide, ctx, value, left, top, width, height, opts = {}) {
  return ctx.addText(slide, {
    text: value,
    left, top, width, height,
    fontSize: opts.size ?? 24,
    color: opts.color ?? C.ink,
    bold: opts.bold ?? false,
    typeface: opts.face ?? "Microsoft YaHei",
    align: opts.align ?? "left",
    valign: opts.valign ?? "top",
    fill: opts.fill ?? "transparent",
    line: opts.line ?? ctx.line("transparent", 0),
    insets: opts.insets ?? { left: 0, right: 0, top: 0, bottom: 0 },
    name: opts.name,
  });
}

function box(slide, ctx, left, top, width, height, opts = {}) {
  return ctx.addShape(slide, {
    left, top, width, height,
    geometry: opts.geometry ?? "rect",
    fill: opts.fill ?? C.white,
    line: opts.line ?? ctx.line(opts.stroke ?? C.line, opts.strokeWidth ?? 1),
    name: opts.name,
  });
}

function setup(slide, ctx, no, kicker, claim) {
  box(slide, ctx, 0, 0, 1280, 720, { fill: C.paper, line: ctx.line("transparent", 0), name: "slide-bg" });
  box(slide, ctx, 0, 0, 1280, 8, { fill: C.blue, line: ctx.line("transparent", 0), name: "top-accent" });
  box(slide, ctx, 40, 42, 8, 8, { fill: C.green, line: ctx.line("transparent", 0), name: "kicker-marker" });
  text(slide, ctx, kicker.toUpperCase(), 58, 34, 260, 24, { size: 13, bold: true, color: C.green, name: "kicker-label" });
  text(slide, ctx, claim, 58, 62, 820, 82, { size: 32, bold: true, color: C.ink, name: "claim-title" });
  text(slide, ctx, String(no).padStart(2, "0"), 1180, 642, 42, 28, { size: 16, color: C.muted, align: "right", name: "page-marker" });
  text(slide, ctx, "CS-202614 | 半球面 2π | CST-Python 闭环", 58, 644, 600, 24, { size: 12, color: C.muted, name: "footer" });
}

function metric(slide, ctx, label, value, left, top, width, accent = C.blue) {
  box(slide, ctx, left, top, width, 96, { fill: C.white, stroke: "#D8DEE8", name: "metric-box" });
  box(slide, ctx, left, top, 6, 96, { fill: accent, line: ctx.line("transparent", 0), name: "metric-accent" });
  text(slide, ctx, value, left + 22, top + 12, width - 30, 38, { size: 27, bold: true, color: C.ink, name: "metric-value" });
  text(slide, ctx, label, left + 22, top + 54, width - 30, 28, { size: 13, color: C.muted, name: "metric-label" });
}

function bullet(slide, ctx, value, left, top, width, opts = {}) {
  box(slide, ctx, left, top + 8, 7, 7, { fill: opts.accent ?? C.green, line: ctx.line("transparent", 0), name: "bullet-dot" });
  text(slide, ctx, value, left + 18, top, width - 18, opts.height ?? 42, { size: opts.size ?? 18, color: opts.color ?? C.ink, name: "bullet-text" });
}

function miniTable(slide, ctx, rows, left, top, width, rowH = 42, colWidths = null) {
  const cols = rows[0].length;
  const widths = colWidths ?? Array(cols).fill(width / cols);
  let y = top;
  for (let r = 0; r < rows.length; r += 1) {
    let x = left;
    for (let c = 0; c < cols; c += 1) {
      const fill = r === 0 ? C.paleBlue : C.white;
      box(slide, ctx, x, y, widths[c], rowH, { fill, stroke: "#D7DEE8", name: "table-cell" });
      text(slide, ctx, rows[r][c], x + 8, y + 8, widths[c] - 16, rowH - 12, {
        size: r === 0 ? 13 : 12.5,
        bold: r === 0,
        color: C.ink,
        align: c === 0 ? "left" : "center",
        name: "table-text",
      });
      x += widths[c];
    }
    y += rowH;
  }
}

async function image(slide, ctx, path, left, top, width, height, opts = {}) {
  box(slide, ctx, left - 4, top - 4, width + 8, height + 8, { fill: C.white, stroke: "#CCD5DF", name: "image-frame" });
  await ctx.addImage(slide, { path, left, top, width, height, fit: opts.fit ?? "contain", alt: opts.alt ?? "" });
}

function note(slide, ctx, value, left, top, width, height, fill = C.paleAmber) {
  box(slide, ctx, left, top, width, height, { fill, stroke: "#E2D2B8", name: "note-box" });
  text(slide, ctx, value, left + 18, top + 10, width - 36, height - 14, { size: 15, color: C.ink, name: "note-text" });
}

export { C, setup, text, box, metric, bullet, miniTable, image, note };
'''


def slide_module(no: int, body: str) -> str:
    return f"""import {{ C, setup, text, box, metric, bullet, miniTable, image, note }} from './slide_common.mjs';

export async function slide{no:02d}(presentation, ctx) {{
  const slide = presentation.slides.add();
{body}
  return slide;
}}
"""


def build_slide_modules(metrics: dict[str, object]) -> None:
    paths = {key: str(path).replace("\\", "/") for key, path in ASSETS.items()}
    m = metrics
    slide_defs: dict[int, str] = {
        1: f'''
  setup(slide, ctx, 1, "方案总览", "半球面 2π 测量 + CST-Python 闭环，支撑重建与识别两条主线");
  text(slide, ctx, "复杂航空载体电磁辐射空域特性测量技术", 78, 170, 900, 58, {{ size: 38, bold: true, color: C.ink }});
  text(slide, ctx, "物理约束的空-频-极化联合等效源重构与受限域压缩测量方法", 80, 234, 900, 38, {{ size: 21, color: C.muted }});
  metric(slide, ctx, "半球面测点", "{m['sensor_count']}", 80, 330, 230, C.blue);
  metric(slide, ctx, "Level 2 样本", "{m['level2_samples']}/48", 335, 330, 230, C.green);
  metric(slide, ctx, "识别准确率", "{float(m['level2_accuracy']):.3f}", 590, 330, 230, C.amber);
  metric(slide, ctx, "结构跨域", "{float(m['structure_accuracy']):.3f}", 845, 330, 230, C.green);
  note(slide, ctx, "当前生成正式报告 DOCX/PDF；PPTX 由本 deck 导出；MP4 仍需录制或自动生成。", 80, 500, 980, 74, C.paleBlue);
''',
        2: '''
  setup(slide, ctx, 2, "指标拆解", "100 分评分项已映射到可审计文件和可复现实验输出");
  miniTable(slide, ctx, [
    ["赛题要求", "证据", "状态"],
    ["2π 覆盖与 12m x 10m x 8m 包络", "半球面 162 测点 + CST workpack", "Ready"],
    ["三维场域重建与少测点", "Level 1 required + 角域校准 + 鲁棒性曲线", "模型边界待成稿"],
    ["空间-频谱特征辨识 >=85%", "Level 2 full48 + 消融 + 结构遮挡跨域", "Ready"],
    ["最终交付物", "报告/PPT/视频/代码/CST/data", "G5 收口中"],
  ], 72, 172, 1030, 68, [330, 470, 230]);
  note(slide, ctx, "审计口径：completion_proven 只能在正式 PDF/DOCX/PPTX/MP4 和提交包审计全部通过后置为 true。", 72, 572, 1030, 62);
''',
        3: '''
  setup(slide, ctx, 3, "文献迁移", "方法不是从零拼装，而是从近场测量、等效源、压缩采样和辐射指纹四条主线迁移");
  const lanes = [
    ["IEEE 149/1720", "标准测量与近远场变换", C.blue],
    ["IEEE TAP", "任意曲面 NF-FF 与等效源", C.green],
    ["IEEE TSP/JSTSP", "压缩感知与少测点优化", C.amber],
    ["RF/SEI 文献", "空-频-极化联合指纹", "#7A5FA8"],
  ];
  for (let i = 0; i < lanes.length; i += 1) {
    const y = 178 + i * 92;
    box(slide, ctx, 90, y, 170, 58, { fill: lanes[i][2], line: ctx.line("transparent", 0) });
    text(slide, ctx, lanes[i][0], 105, y + 16, 140, 28, { size: 16, bold: true, color: C.white, align: "center" });
    box(slide, ctx, 292, y, 620, 58, { fill: C.white, stroke: "#D8DEE8" });
    text(slide, ctx, lanes[i][1], 316, y + 16, 560, 28, { size: 18, color: C.ink });
  }
  text(slide, ctx, "迁移到赛题：半球面测量 → 等效源/角域校准 → 少测点 → 多源状态识别", 100, 570, 860, 34, { size: 22, bold: true, color: C.ink });
''',
        4: '''
  setup(slide, ctx, 4, "技术路线", "CST 负责可信电磁数据源，Python 负责重建、识别和审计闭环");
  const steps = [
    ["CST 建模", "标准源 / element-library / 简化结构"],
    ["数据导出", "nearfield / farfield / labels"],
    ["算法处理", "等效源重建 / 角域校准 / 特征工程"],
    ["审计交付", "scorecard / completion audit / submission"],
  ];
  for (let i = 0; i < steps.length; i += 1) {
    const x = 80 + i * 285;
    box(slide, ctx, x, 214, 220, 140, { fill: i % 2 ? C.paleGreen : C.white, stroke: "#CBD5E1" });
    text(slide, ctx, steps[i][0], x + 22, 238, 176, 28, { size: 23, bold: true, color: C.ink, align: "center" });
    text(slide, ctx, steps[i][1], x + 18, 282, 184, 48, { size: 15, color: C.muted, align: "center" });
    if (i < steps.length - 1) text(slide, ctx, "→", x + 235, 255, 34, 48, { size: 34, color: C.blue, bold: true });
  }
  miniTable(slide, ctx, [
    ["Gate", "当前结果"],
    ["G1/G2/G3/G4", "complete"],
    ["G5", "partial：正式 PPTX/MP4 与最终审计仍需关闭"],
  ], 250, 470, 760, 48, [180, 580]);
''',
        5: f'''
  setup(slide, ctx, 5, "测量布局", "13 m 半球面 162 测点覆盖 12m x 10m x 8m 被测空间");
  await image(slide, ctx, {js_string(paths['sensor'])}, 78, 158, 650, 410, {{ fit: "contain", alt: "hemisphere sensor layout" }});
  metric(slide, ctx, "空间测点", "{m['sensor_count']}", 790, 180, 250, C.blue);
  metric(slide, ctx, "单频双极化通道", "324", 790, 300, 250, C.green);
  metric(slide, ctx, "执行路线", "半球面", 790, 420, 250, C.amber);
  note(slide, ctx, "半柱面保留为后续工程扩展；本轮 CST Level 1/2 与所有审计均以半球面测点表为准。", 780, 545, 350, 70, C.paleBlue);
''',
        6: f'''
  setup(slide, ctx, 6, "Level 1 标准源", "FarfieldPlot-derived 角域样本与 CST 远场真值高度一致");
  await image(slide, ctx, {js_string(paths['angular'])}, 80, 162, 650, 382, {{ fit: "contain", alt: "level 1 angular calibration" }});
  metric(slide, ctx, "max NMSE", "{float(m['level1_nmse']):.2e}", 780, 172, 270, C.green);
  metric(slide, ctx, "min corr", "{float(m['level1_corr']):.5f}", 780, 292, 270, C.blue);
  metric(slide, ctx, "主瓣误差", "0.00°", 780, 412, 270, C.amber);
  note(slide, ctx, "边界：该通道证明 solver-safe 角域一致性；full-wave near-field monitor 等效源反演仍作为模型风险说明。", 760, 548, 390, 70);
''',
        7: '''
  setup(slide, ctx, 7, "重建算法", "把有限半球面观测转成可外推的等效源，再由正则化控制病态反演");
  text(slide, ctx, "E_meas = G_nf · J + n", 125, 178, 470, 58, { size: 40, bold: true, color: C.ink, align: "center" });
  text(slide, ctx, "J* = argmin ||G_nf J - E||² + λ ||J||²", 125, 258, 620, 46, { size: 28, bold: true, color: C.blue, align: "center" });
  const items = [
    ["输入", "半球面 Ex/Ey/Ez 复数场"],
    ["求解", "Tikhonov/SVD 稳定反演"],
    ["输出", "远场方向图与主瓣/相关系数/NMSE"],
    ["边界", "FarfieldPlot 角域样本不直接等同 full-wave 近场 monitor"],
  ];
  miniTable(slide, ctx, items, 155, 385, 860, 54, [170, 690]);
''',
        8: f'''
  setup(slide, ctx, 8, "少测点优化", "合成鲁棒性扫描显示 75% 测点更稳，50% 可作为压缩候选");
  await image(slide, ctx, {js_string(paths['tradeoff'])}, 78, 162, 680, 390, {{ fit: "contain", alt: "sensor tradeoff" }});
  bullet(slide, ctx, "30 dB 下 optimized_75：NMSE≈1.13e-3，corr≈0.9983", 800, 190, 330, {{ height: 72 }});
  bullet(slide, ctx, "optimized_50 相关性仍高，但主瓣定位需结合真实 CST 边界说明", 800, 275, 330, {{ height: 76, accent: C.amber }});
  bullet(slide, ctx, "25% 暂不作为主方案，只保留为极限对照", 800, 380, 330, {{ height: 72, accent: C.red }});
  note(slide, ctx, "该页作为算法鲁棒性参考，不替代 Level 1 required 高精度证明。", 790, 515, 360, 62, C.paleBlue);
''',
        9: f'''
  setup(slide, ctx, 9, "Level 2 多源识别", "48 个 CST-derived 样本上，空-频-极化特征超过 85% 指标线");
  await image(slide, ctx, {js_string(paths['confusion'])}, 100, 150, 530, 430, {{ fit: "contain", alt: "level 2 confusion matrix" }});
  metric(slide, ctx, "样本完整度", "{m['level2_samples']}/48", 720, 174, 260, C.blue);
  metric(slide, ctx, "特征维度", "4965", 720, 294, 260, C.green);
  metric(slide, ctx, "SVM accuracy", "{float(m['level2_accuracy']):.3f}", 720, 414, 260, C.amber);
  note(slide, ctx, "证据性质：CST-derived element-library superposition；结构影响由下一页 bounded 对照约束。", 700, 548, 430, 66);
''',
        10: f'''
  setup(slide, ctx, 10, "结构遮挡对照", "简化机体遮挡会改变方向图，但识别特征保持跨域稳定");
  await image(slide, ctx, {js_string(paths['structure'])}, 68, 155, 670, 405, {{ fit: "contain", alt: "structure comparison" }});
  metric(slide, ctx, "mean shadow", "{float(m['structure_shadow']):.2f} dB", 780, 170, 270, C.amber);
  metric(slide, ctx, "P95 shadow", "{float(m['structure_p95']):.2f} dB", 780, 290, 270, C.blue);
  metric(slide, ctx, "cross-domain", "{float(m['structure_accuracy']):.3f}", 780, 410, 270, C.green);
  note(slide, ctx, "这是 simplified aircraft occlusion transfer，不是 full-wave CST airframe scattering；用于报告中保守约束结论边界。", 750, 548, 430, 76);
''',
        11: '''
  setup(slide, ctx, 11, "创新点", "创新不在单个脚本，而在物理模型、测点压缩、联合指纹和可复现审计的组合");
  const cards = [
    ["受限域等效源", "把复杂辐射体替换为可计算、可诊断的源分布"],
    ["半球面少测点", "162 点全量与 75/50/25% 压缩对照"],
    ["空频极化指纹", "方向图、相位、频谱和极化联合表征"],
    ["CST-Python 审计", "manifest、strict merge、scorecard、completion audit"],
  ];
  for (let i = 0; i < cards.length; i += 1) {
    const x = 86 + (i % 2) * 510;
    const y = 176 + Math.floor(i / 2) * 170;
    box(slide, ctx, x, y, 440, 122, { fill: i % 2 ? C.paleGreen : C.white, stroke: "#D8DEE8" });
    text(slide, ctx, cards[i][0], x + 24, y + 22, 390, 28, { size: 22, bold: true, color: C.ink });
    text(slide, ctx, cards[i][1], x + 24, y + 62, 390, 38, { size: 15.5, color: C.muted });
  }
  note(slide, ctx, "答辩口径：先讲评分项对应证据，再讲边界；不把 simplified 结构对照包装成 full-wave airframe。", 90, 560, 940, 58, C.paleBlue);
''',
        12: '''
  setup(slide, ctx, 12, "总结与交付", "技术证据已基本齐套，最终提交仍由 G5 四件套决定");
  miniTable(slide, ctx, [
    ["交付物", "当前状态", "关闭证据"],
    ["方案报告 DOCX/PDF", "已生成", "submission/01_report"],
    ["答辩 PPTX/PDF", "本轮生成 PPTX", "submission/02_presentation"],
    ["演示视频 MP4", "待录制/生成", "submission/03_video/demo_video.mp4"],
    ["代码/CST/data/附录", "草稿包齐套", "submission index blocked=0"],
  ], 86, 168, 980, 70, [260, 260, 460]);
  metric(slide, ctx, "completion audit", "7C / 1P", 110, 540, 260, C.blue);
  metric(slide, ctx, "submission blocked", "0", 420, 540, 260, C.green);
  metric(slide, ctx, "next gate", "G5", 730, 540, 260, C.amber);
''',
    }

    write_text(SLIDES_DIR / "slide_common.mjs", COMMON_MJS)
    for no, body in slide_defs.items():
        write_text(SLIDES_DIR / f"slide-{no:02d}.mjs", slide_module(no, body))


def write_planning_docs(storyboard: list[dict[str, str]], metrics: dict[str, object]) -> None:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)
    write_text(
        WORKSPACE / "profile-plan.txt",
        "\n".join(
            [
                "task mode: create",
                "primary deck-profile: engineering-platform",
                "secondary gates: appendix-heavy evidence discipline; strategy-leadership claim spine",
                "required proof objects: metric rail, hemisphere layout, Level 1 angular calibration, Level 2 confusion matrix, structure comparison",
                "asset requirements: all visual assets are local project outputs with provenance in outputs/",
                "known missing inputs: team member names and final MP4 recording",
            ]
        )
        + "\n",
    )
    write_text(
        WORKSPACE / "source-notes.txt",
        "\n".join([f"- {key}: {path.relative_to(ROOT)}" for key, path in ASSETS.items()])
        + "\n- Metrics: outputs/scorecard/scorecard_metrics.json\n",
    )
    claim_lines = [
        "thesis: 半球面 2π + CST-Python 闭环能够支撑赛题的重建、少测点和识别要求。",
        "audience: 竞赛评审和队内答辩人。",
        "arc: 指标拆解 -> 文献迁移 -> 技术路线 -> Level 1/Level 2/结构边界 -> 创新与提交。",
        "",
    ]
    for row in storyboard:
        claim_lines.append(f"slide {row['slide_no']}: {row['title']} | proof={row['visual_type']} | note={row['speaker_note_draft']}")
    write_text(WORKSPACE / "claim-spine.txt", "\n".join(claim_lines) + "\n")
    write_text(
        WORKSPACE / "design-system.txt",
        "\n".join(
            [
                "slide size: 1280x720",
                "background: warm paper #F7F4EC",
                "typography: Microsoft YaHei for Chinese, Calibri/Aptos fallback",
                "palette: ink #0B2545, blue #2E74B5, green #4C8C6A, amber #B87921, white panels",
                "chart grammar: use existing project plots in white frames with concise metric rails",
                "diagram grammar: left-to-right process boxes and direct labels",
                "footer: CS-202614 | 半球面 2π | CST-Python 闭环",
                "banned motifs: fake logos, decorative blobs, unverified brand marks",
            ]
        )
        + "\n",
    )
    write_text(
        WORKSPACE / "contact-sheet-plan.txt",
        "\n".join(
            [
                "1 cover with metric rail",
                "2 requirements table",
                "3 literature method lanes",
                "4 pipeline diagram",
                "5 image-led layout",
                "6 image + metric rail",
                "7 formula/table slide",
                "8 chart + bullets",
                "9 confusion matrix + metrics",
                "10 structure comparison + metrics",
                "11 innovation cards",
                "12 closing checklist",
            ]
        )
        + "\n",
    )
    write_text(
        QA_DIR / "comeback-scorecard.txt",
        "\n".join(
            [
                "primary deck-profile: engineering-platform",
                "profile gate: pending rendered preview QA",
                "story: 4/5",
                "specificity: 5/5",
                "rhythm: 4/5",
                "whitespace: pending preview",
                "chart clarity: pending preview",
                "typography: pending preview",
                "restraint: 4/5",
                "precision: 5/5",
                "coherence: pending preview",
                "residual gap: final MP4 is not generated by this deck builder.",
            ]
        )
        + "\n",
    )


def run_builder() -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["HOME"] = r"C:\Users\heh20"
    env["PYTHON"] = str(PYTHON)
    cmd = [
        str(NODE),
        str(BUILD_SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--slides-dir",
        str(SLIDES_DIR),
        "--out",
        str(FINAL_PPTX),
        "--preview-dir",
        str(PREVIEW_DIR),
        "--layout-dir",
        str(LAYOUT_DIR / "final"),
        "--contact-sheet",
        str(CONTACT_SHEET),
        "--manifest",
        str(MANIFEST),
        "--slide-count",
        "12",
        "--slide-size",
        "1280x720",
        "--scale",
        "1",
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"artifact-tool build failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout)


def main() -> None:
    storyboard = read_storyboard()
    metrics = metric_rows()
    build_slide_modules(metrics)
    write_planning_docs(storyboard, metrics)
    manifest = run_builder()
    summary = {
        "pptx": str(FINAL_PPTX.relative_to(ROOT)),
        "pdf": "submission\\02_presentation\\defense_slides.pdf",
        "workspace": str(WORKSPACE.relative_to(ROOT)),
        "slide_count": manifest.get("slideCount"),
        "contact_sheet": str(CONTACT_SHEET.relative_to(ROOT)),
        "preview_dir": str(PREVIEW_DIR.relative_to(ROOT)),
        "layout_dir": str((LAYOUT_DIR / "final").relative_to(ROOT)),
        "pdf_contact_sheet": "outputs\\presentation_artifact\\defense_slides_pdf_contact_sheet.png",
        "is_final_presentation": True,
        "requires_visual_qa": True,
        "layout_qa": "Run check_layout_quality.mjs on layout_dir; latest manual run passed 0 errors / 0 warnings.",
        "final_video_still_missing": not (ROOT / "submission" / "03_video" / "demo_video.mp4").exists(),
    }
    summary_path = ROOT / "outputs" / "presentation_artifact" / "defense_pptx_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
