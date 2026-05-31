# -*- coding: utf-8 -*-
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

BLACK = colors.black
WHITE = colors.white

ROOT = Path.cwd()
OUT_DIR = ROOT / "outputs" / "contest_work_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_ASCII = OUT_DIR / "work_plan_teacher.pdf"

FONT_BODY = "DengXian"
FONT_BOLD = "DengXian-Bold"
FONT_HEI = "SimHei"

pdfmetrics.registerFont(TTFont(FONT_BODY, r"C:\Windows\Fonts\Deng.ttf"))
pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\Dengb.ttf"))
pdfmetrics.registerFont(TTFont(FONT_HEI, r"C:\Windows\Fonts\simhei.ttf"))


class WorkPlanDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=22 * mm,
            rightMargin=22 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="复杂航空载体电磁辐射空域特性测量技术比赛工作计划",
            author="华尔涵团队",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BLACK)
        canvas.setLineWidth(0.7)
        canvas.line(22 * mm, A4[1] - 14 * mm, A4[0] - 22 * mm, A4[1] - 14 * mm)
        canvas.setFont(FONT_BODY, 8.5)
        canvas.setFillColor(BLACK)
        canvas.drawString(22 * mm, A4[1] - 11 * mm, "CS-202614 复杂航空载体电磁辐射空域特性测量技术比赛")
        canvas.drawRightString(A4[0] - 22 * mm, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        fontName=FONT_HEI,
        fontSize=23,
        leading=31,
        textColor=BLACK,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSub",
        fontName=FONT_BODY,
        fontSize=12,
        leading=19,
        textColor=BLACK,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="H1",
        fontName=FONT_HEI,
        fontSize=15.5,
        leading=22,
        textColor=BLACK,
        spaceBefore=8,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="H2",
        fontName=FONT_BOLD,
        fontSize=12.3,
        leading=17,
        textColor=BLACK,
        spaceBefore=7,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        fontName=FONT_BODY,
        fontSize=10.4,
        leading=16,
        textColor=BLACK,
        spaceAfter=5.5,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        fontName=FONT_BODY,
        fontSize=9.2,
        leading=14,
        textColor=BLACK,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletCN",
        parent=styles["Body"],
        leftIndent=12,
        firstLineIndent=0,
        bulletIndent=0,
        bulletFontName=FONT_BODY,
        bulletFontSize=9.5,
        spaceAfter=5.5,
    )
)
styles.add(
    ParagraphStyle(
        name="Note",
        fontName=FONT_BODY,
        fontSize=10.2,
        leading=16,
        textColor=BLACK,
        backColor=WHITE,
        borderColor=BLACK,
        borderWidth=0.6,
        borderPadding=7,
        spaceBefore=4,
        spaceAfter=8,
    )
)


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def h1(text):
    return p(text, "H1")


def h2(text):
    return p(text, "H2")


def bullet(text):
    return Paragraph(text, styles["BulletCN"], bulletText="•")


def note(title, body):
    return p(f"<b>{title}</b><br/>{body}", "Note")


def table(rows, col_widths):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), WHITE),
                ("TEXTCOLOR", (0, 0), (-1, 0), BLACK),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_BODY),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 13.5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, BLACK),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, WHITE]),
            ]
        )
    )
    return t


def person_section(name, title, position, tasks, outputs, links):
    parts = [h1(f"{name}：{title}"), p(position), h2("负责的具体工作")]
    parts.extend(bullet(x) for x in tasks)
    parts.append(h2("需要形成的成果"))
    parts.extend(bullet(x) for x in outputs)
    parts.append(h2("协作关系"))
    parts.extend(bullet(x) for x in links)
    return KeepTogether(parts)


story = []

story.append(Spacer(1, 20 * mm))
story.append(p("复杂航空载体电磁辐射空域特性测量技术比赛", "CoverTitle"))
story.append(p("工作计划与成员分工", "CoverTitle"))
story.append(Spacer(1, 7 * mm))
story.append(p("团队成员：华尔涵、张昊、李伊然", "CoverSub"))
story.append(p("参考材料：赛题方案、前期 Workflow 总结文档、老师介绍 PPT", "CoverSub"))
story.append(p("计划节点：2026年9月15日前完成作品提交", "CoverSub"))
story.append(Spacer(1, 18 * mm))
story.append(note("工作目标", "围绕赛题要求，完成“测量布局设计—仿真数据生成—近远场重建—测点优化—特征辨识—成果展示”的完整方案，最终提交方案报告、PPT、演示视频、测试代码和复现说明。"))
story.append(PageBreak())

story.append(h1("一、赛题要求与工作重点"))
story.append(
    p(
        "赛题要求面向复杂航空载体的电磁辐射空域特性测量，重点不在单点测试，而在全空间、多频点、多极化条件下获取辐射信息，并进一步完成近远场关联建模、三维场域重建和空间—频谱特征辨识。"
    )
)
story.append(
    p(
        "从评分要求看，客观分主要集中在三个方面：传感器布局需覆盖 2π 空间立体角，并能容纳 12m×10m×8m 的被测对象；三维场域重建需要在保证精度的同时尽量减少测点数量；典型辐射源的空间频率特征辨识精度不低于 85%。主观分则要求调研、研究思路、技术路线和测试方案完整。"
    )
)
story.append(note("工作重点", "本组方案以“仿真数据支撑、自研算法验证、量化指标评价”为主线。仿真软件用于生成近场数据和远场参考真值，自研代码负责重建、优化和识别，最终用图表和指标说明方案有效性。"))
story.append(h2("需要特别注意的地方"))
for item in [
    "先用标准辐射源跑通完整流程，再逐步加入多源、多极化、安装位置和简化航空载体结构。",
    "仿真软件的远场结果只作为参考真值，不能替代自研近远场重建算法。",
    "传感器布局要给出坐标、极化方向、采样密度和覆盖示意，不能只停留在文字描述。",
    "识别部分需要给出数据集划分、特征提取、分类器、准确率和混淆矩阵。",
]:
    story.append(bullet(item))

story.append(h1("二、总体技术路线"))
story.append(
    p(
        "整体工作按“标准源验证—传感布局设计—近远场重建—测点优化—特征辨识—成果整理”推进。标准源用于校验物理模型和代码正确性，多源及简化载体模型用于体现航空平台的结构影响和多设备协同辐射特征。"
    )
)
route_rows = [
    [p("环节", "Small"), p("主要工作", "Small"), p("评价方式", "Small")],
    [p("标准源验证", "Small"), p("建立短偶极子、半波振子或小环天线模型，导出近场采样数据和远场真值。", "Small"), p("检查坐标、极化、复数场数据和方向图是否一致。", "Small")],
    [p("传感布局", "Small"), p("设计半柱面或半球面测点，考虑多角度、多极化、宽频段采样。", "Small"), p("验证 2π 空间覆盖和 12m×10m×8m 被测空间要求。", "Small")],
    [p("场域重建", "Small"), p("建立 E_meas = GJ 模型，采用 Tikhonov、SVD 截断或 L1 稀疏约束反演等效源并外推远场。", "Small"), p("用 NMSE、相关系数、主瓣方向误差和峰值误差评价。", "Small")],
    [p("测点优化", "Small"), p("比较全测点、75%、50%、25% 测点和优化采样方案。", "Small"), p("形成测点数量—重建精度曲线，说明工程折中点。", "Small")],
    [p("特征辨识", "Small"), p("提取空间—频谱—极化联合特征，建立 SVM、随机森林等识别模型。", "Small"), p("输出准确率、F1 和混淆矩阵，目标准确率不低于 85%。", "Small")],
]
story.append(table(route_rows, [33 * mm, 78 * mm, 63 * mm]))
story.append(PageBreak())

story.append(
    person_section(
        "华尔涵",
        "总体方案与近远场重建",
        "主要负责赛题拆解、总体方案把关和核心算法实现。重点放在近远场关联建模、等效源反演、远场重建、测点优化以及最终报告和答辩主线。",
        [
            "梳理赛题硬性指标，包括 2π 空间覆盖、12m×10m×8m 被测空间、重建精度、测点数量和识别准确率。",
            "确定总体技术路线，安排标准源、多源、简化载体和识别数据集的递进关系。",
            "建立近远场重建模型，构建测点场与等效源之间的传播矩阵 G。",
            "实现最小二乘、Tikhonov 正则、SVD 截断等反演方法；时间允许时加入 L1 稀疏约束。",
            "组织测点优化实验，比较规则采样、随机抽样和优化采样对重建精度的影响。",
            "负责报告核心章节、PPT 主线、创新点整理和答辩问题准备。",
        ],
        [
            "赛题需求拆解和总体技术路线图。",
            "近远场重建公式推导、核心代码和参数说明。",
            "方向图重建结果、误差热力图和重建精度指标表。",
            "测点数量—重建精度曲线及推荐测点布局结论。",
            "报告算法章节、结果章节和答辩主线。",
        ],
        [
            "需要张昊提供近场复数数据、测点坐标、远场真值和仿真模型参数。",
            "需要李伊然提供数据字典、识别标签体系和文献调研材料。",
            "算法结果更新后，同步给张昊用于图表展示，给李伊然用于指标整理和报告汇总。",
        ],
    )
)
story.append(PageBreak())

story.append(
    person_section(
        "张昊",
        "电磁仿真、测量布局与可视化",
        "主要负责把赛题中的复杂载体、全景测试和传感布局落到可计算的数据和可展示的模型上。其工作直接决定算法输入是否可信，也决定报告中工程场景是否充分。",
        [
            "确认 CST、FEKO、COMSOL 或其他可用仿真工具，明确频点、边界条件、材料设置和导出格式。",
            "建立短偶极子、半波振子或小环天线等标准源模型，输出可用于算法验证的近场数据和远场方向图。",
            "设计半柱面或半球面测点布局，给出传感器坐标、极化方向、采样密度和被测空间尺寸示意。",
            "构造多源、多频点、多极化组合，模拟机载设备的多状态辐射特征。",
            "建立简化航空载体模型，如金属圆柱机身、平板机翼和天线安装位置，用于体现遮挡、散射和安装效应。",
            "制作测点布局图、三维方向图、仿真模型截图和演示视频素材。",
        ],
        [
            "标准源、多源和简化载体仿真模型。",
            "半柱面或半球面测点坐标表及 2π 覆盖示意图。",
            "近场采样数据、远场参考真值和数据导出说明。",
            "多状态数据集和载体安装效应展示图。",
            "报告和 PPT 所需的模型图、方向图和录屏素材。",
        ],
        [
            "向华尔涵提供统一坐标系下的测点坐标、复数场数据和远场真值。",
            "向李伊然提供源类型、工作状态、频点和极化标签，保证识别数据集可追溯。",
            "根据重建和识别结果统一图表风格，支撑最终 PPT 和视频展示。",
        ],
    )
)
story.append(PageBreak())

story.append(
    person_section(
        "李伊然",
        "文献调研、数据规范与特征辨识",
        "主要负责调研依据、数据规范和特征辨识部分。该部分既支撑主观评分中的国内外调研，也支撑客观评分中不低于 85% 的特征辨识要求。",
        [
            "调研近场测量、等效源重建、压缩感知测量、辐射指纹识别等方向的国内外研究。",
            "建立数据字典，统一 sensor_id、坐标、频率、极化、复数场分量、source_type、working_state 等字段。",
            "整理识别数据集，按源类型、安装位置、频点、极化和运行状态建立标签。",
            "提取主瓣方向、副瓣数量、方向图熵、频谱峰值、极化比、空频相关性等特征。",
            "建立 SVM、随机森林等识别基线，目标是稳定达到或超过 85% 准确率。",
            "整理 README、运行顺序、数据格式说明、图表清单和提交前检查清单。",
        ],
        [
            "文献调研表、国内外技术路线对比和报告调研章节。",
            "统一数据字典、样例数据说明和标签规范。",
            "特征提取脚本、可分性可视化图和识别训练脚本。",
            "识别准确率、Precision、Recall、F1 和混淆矩阵。",
            "复现说明和提交材料检查清单。",
        ],
        [
            "需要张昊提供稳定的数据字段、样本标签和仿真数据说明。",
            "需要华尔涵提供重建后的方向图、误差指标和测点优化结论。",
            "最终材料中负责把调研、数据、识别和复现说明整理成可查证的证据链。",
        ],
    )
)
story.append(PageBreak())

story.append(h1("六、阶段安排与成果节点"))
story.append(p("阶段安排以最终提交为目标，重点保证每一阶段都有可检查的结果。建议按以下五个阶段推进。"))
milestone_rows = [
    [p("时间", "Small"), p("主要目标", "Small"), p("阶段成果", "Small")],
    [p("5月下旬—6月上旬", "Small"), p("完成赛题拆解、调研启动、仿真环境确认和标准源模型。", "Small"), p("需求拆解、文献框架、标准源模型、初版测点布局。", "Small")],
    [p("6月中旬—7月上旬", "Small"), p("跑通近场数据导出、远场真值导出和传播矩阵建模。", "Small"), p("近场/远场样例数据、G 矩阵代码、数据字典。", "Small")],
    [p("7月中旬—8月上旬", "Small"), p("完成近远场重建、误差评估和多源/载体数据扩展。", "Small"), p("方向图对比、误差表、简化载体模型、多状态样本。", "Small")],
    [p("8月中旬—8月下旬", "Small"), p("完成测点优化和空间—频谱特征识别。", "Small"), p("测点数量—精度曲线、混淆矩阵、识别准确率报告。", "Small")],
    [p("9月上旬—9月15日前", "Small"), p("完成报告、PPT、视频、代码复现和提交材料检查。", "Small"), p("最终报告、答辩 PPT、演示视频、测试代码、复现说明和压缩包。", "Small")],
]
story.append(table(milestone_rows, [36 * mm, 72 * mm, 66 * mm]))

story.append(h1("七、协同要求"))
for item in [
    "统一坐标系。仿真数据、测点布局和重建算法必须使用同一坐标定义，避免后期误差来源不清。",
    "统一数据格式。近场、远场、频点、极化和标签信息要按数据字典保存，保证后续脚本可直接读取。",
    "统一评价指标。重建部分使用 NMSE、相关系数、主瓣方向误差等指标；识别部分使用准确率、F1 和混淆矩阵。",
    "统一材料逻辑。报告和 PPT 按“测量覆盖—场域重建—测点优化—特征辨识—工程价值”组织，不按个人流水账组织。",
]:
    story.append(bullet(item))

story.append(h1("八、预期提交成果"))
for item in [
    "分布式宽带电磁传感布设方案及 2π 空间覆盖示意。",
    "标准源、多源和简化航空载体的近场数据与远场真值数据。",
    "近远场重建算法代码、误差评估结果和测点优化结果。",
    "空间—频谱—极化联合特征识别模型，准确率不低于 85%。",
    "方案报告、答辩 PPT、演示视频、测试代码和复现说明。",
]:
    story.append(bullet(item))

doc = WorkPlanDoc(str(PDF_ASCII))
doc.build(story)
print(PDF_ASCII)
