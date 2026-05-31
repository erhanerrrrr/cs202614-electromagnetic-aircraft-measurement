# -*- coding: utf-8 -*-
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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


ROOT = Path.cwd()
OUT_DIR = ROOT / "outputs" / "contest_work_plan"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_PATH = OUT_DIR / "复杂航空载体电磁辐射空域特性测量_正文版工作计划.pdf"


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
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="normal",
        )
        self.addPageTemplates(
            PageTemplate(id="main", frames=[frame], onPage=self.draw_page)
        )

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#1F5A66"))
        canvas.setLineWidth(0.7)
        canvas.line(22 * mm, A4[1] - 14 * mm, A4[0] - 22 * mm, A4[1] - 14 * mm)
        canvas.setFont(FONT_BODY, 8.5)
        canvas.setFillColor(colors.HexColor("#53666D"))
        canvas.drawString(22 * mm, A4[1] - 11 * mm, "CS-202614 复杂航空载体电磁辐射空域特性测量技术比赛")
        canvas.drawRightString(A4[0] - 22 * mm, 10 * mm, f"第 {doc.page} 页")
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        fontName=FONT_HEI,
        fontSize=24,
        leading=31,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#12343B"),
        spaceAfter=13,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSub",
        fontName=FONT_BODY,
        fontSize=12,
        leading=19,
        textColor=colors.HexColor("#2D4F57"),
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="H1CN",
        fontName=FONT_HEI,
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#12343B"),
        spaceBefore=8,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="H2CN",
        fontName=FONT_BOLD,
        fontSize=12.5,
        leading=17,
        textColor=colors.HexColor("#1F5A66"),
        spaceBefore=7,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCN",
        fontName=FONT_BODY,
        fontSize=10.4,
        leading=16,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#1F2933"),
        spaceAfter=5.5,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallCN",
        fontName=FONT_BODY,
        fontSize=9.2,
        leading=14,
        textColor=colors.HexColor("#3F4D55"),
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletCN",
        parent=styles["BodyCN"],
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
        name="CalloutCN",
        fontName=FONT_BODY,
        fontSize=10.3,
        leading=16,
        textColor=colors.HexColor("#17323A"),
        backColor=colors.HexColor("#EAF3F5"),
        borderColor=colors.HexColor("#9CBCC4"),
        borderWidth=0.6,
        borderPadding=7,
        spaceBefore=5,
        spaceAfter=8,
    )
)


def p(text, style="BodyCN"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(text, styles["BulletCN"], bulletText="•")


def h1(text):
    return p(text, "H1CN")


def h2(text):
    return p(text, "H2CN")


def callout(title, body):
    return p(f"<b>{title}</b><br/>{body}", "CalloutCN")


def compact_table(rows, col_widths):
    table = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F5A66")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("FONTNAME", (0, 1), (-1, -1), FONT_BODY),
                ("FONTSIZE", (0, 0), (-1, -1), 9.2),
                ("LEADING", (0, 0), (-1, -1), 13),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C9CE")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F9FA")]),
            ]
        )
    )
    return table


def person_section(name, role, positioning, responsibilities, deliverables, interface):
    story = [
        h1(f"{name}：{role}"),
        callout("职责定位", positioning),
        h2("主要任务"),
    ]
    for item in responsibilities:
        story.append(bullet(item))
    story.extend([h2("阶段性成果"), *[bullet(item) for item in deliverables]])
    story.extend([h2("与其他成员的接口"), *[bullet(item) for item in interface]])
    return KeepTogether(story)


story = []

story.append(Spacer(1, 18 * mm))
story.append(p("复杂航空载体电磁辐射空域特性测量技术比赛", "CoverTitle"))
story.append(p("正文版工作计划与三人职责分工", "CoverTitle"))
story.append(Spacer(1, 6 * mm))
story.append(p("团队成员：华尔涵、张昊、李伊然", "CoverSub"))
story.append(p("依据文件：CS-202614 赛题方案、Workflow 总结文档、老师介绍 PPT", "CoverSub"))
story.append(p("目标：形成能体现赛题理解、技术可行性和团队执行路径的工作计划。", "CoverSub"))
story.append(Spacer(1, 10 * mm))
story.append(
    callout(
        "本版调整",
        "不再把 Excel 表格截图插入 PDF，也不把工作量百分比作为表达重点。本文以“赛题理解—技术路线—人员职责—阶段成果”的方式组织，便于老师快速判断团队是否抓住了比赛的关键矛盾。",
    )
)
story.append(PageBreak())

story.append(h1("一、对赛题的理解"))
story.append(
    p(
        "本赛题不是简单做一次电磁场测试，也不是把仿真软件的方向图截图汇总成报告。它要求建立一条完整技术链：先通过分布式宽带电磁传感获取复杂载体周围的空域辐射信息，再基于电磁传播与等效原理完成近远场关联建模和三维场域重建，最后利用空间—频谱特征实现不同载体或工作状态的辨识。"
    )
)
story.append(
    p(
        "因此，作品的核心竞争力应落在三件事上：第一，测量布局是否真的覆盖 2π 空间并能容纳 12m×10m×8m 级别被测对象；第二，是否有自研的近远场重建算法，而不是只依赖软件内置 Far-field 功能；第三，是否能用量化实验说明重建精度、测点数量和识别准确率。"
    )
)
story.append(
    callout(
        "评分牵引",
        "主观分关注调研、思路、技术路线和测试方案完整性；客观分的拉分点在三维场域重建 30 分、特征辨识 20 分、传感布局 10 分。团队计划围绕客观 60 分构造可验证结果，同时用清晰调研和方案叙述支撑主观 40 分。",
    )
)
story.append(h2("我们应避免的偏差"))
for item in [
    "避免把项目做成“CST 仿真截图集合”。仿真软件应提供近场数据和远场真值，自研代码应完成重建与误差评估。",
    "避免一开始建过于复杂的飞机模型。先用标准源建立闭环，再逐步加入多源、极化、安装位置和简化载体结构。",
    "避免只说“覆盖范围大”。必须给出半柱面或半球面传感器坐标、极化方向、频点设置和空间覆盖示意。",
    "避免识别部分只做概念描述。需要给出数据集、特征、分类器、准确率和混淆矩阵，且准确率不低于 85%。",
]:
    story.append(bullet(item))

story.append(h1("二、总体技术路线"))
story.append(
    p(
        "总体路线采用“仿真生成数据、算法重建场域、优化减少测点、识别区分状态、材料呈现证据”的闭环。标准源用于校验物理模型，多源和简化航空载体用于体现工程复杂性，远场真值用于评价自研重建算法。"
    )
)
route_rows = [
    [p("阶段", "SmallCN"), p("技术动作", "SmallCN"), p("关键判断", "SmallCN")],
    [
        p("1. 标准源闭环", "SmallCN"),
        p("短偶极子、半波振子或小环天线；导出近场采样与远场真值。", "SmallCN"),
        p("先证明坐标、极化、复数场数据和方向图评价是正确的。", "SmallCN"),
    ],
    [
        p("2. 传感布局", "SmallCN"),
        p("以半柱面为主方案，半球面为展示备选；考虑多角度、多极化、宽频段采样。", "SmallCN"),
        p("必须响应 2π 空间覆盖和 12m×10m×8m 被测空间要求。", "SmallCN"),
    ],
    [
        p("3. 近远场重建", "SmallCN"),
        p("建立 E_meas = GJ 传播模型，采用 Tikhonov/SVD/L1 稀疏约束求解等效源并外推远场。", "SmallCN"),
        p("以 NMSE、相关系数、主瓣方向误差、峰值误差评价重建质量。", "SmallCN"),
    ],
    [
        p("4. 测点优化", "SmallCN"),
        p("比较 100%、75%、50%、25% 测点及优化采样方案。", "SmallCN"),
        p("在精度可接受的前提下减少测点，回应客观评分中的排序项。", "SmallCN"),
    ],
    [
        p("5. 特征辨识", "SmallCN"),
        p("提取空间—频谱—极化联合特征，先做 SVM/随机森林基线，再考虑深度模型增强。", "SmallCN"),
        p("形成准确率、F1 和混淆矩阵，确保典型源识别准确率超过 85%。", "SmallCN"),
    ],
]
story.append(compact_table(route_rows, [32 * mm, 76 * mm, 66 * mm]))
story.append(PageBreak())

story.append(
    person_section(
        "华尔涵",
        "总体技术负责人、近远场重建与测点优化负责人",
        "华尔涵负责把赛题拆成可验证的技术闭环，并承担最核心的算法难点：近远场关联建模、等效源反演、远场重建、测点优化和最终答辩主线。这个角色的重点不是做最多杂务，而是保证作品有物理依据、有自研算法、有可量化指标。",
        [
            "完成赛题需求拆解：明确 2π 覆盖、12m×10m×8m 被测空间、重建精度、测点数量和识别准确率等硬指标。",
            "设计总体技术路线：确定“标准源验证—多源扩展—简化载体—重建优化—识别验证”的递进路线。",
            "建立近远场重建模型：以 Green 函数、等效源或 Huygens 面为基础，构建测点场与等效源之间的传播矩阵 G。",
            "实现反演求解与远场外推：完成最小二乘、Tikhonov 正则、SVD 截断，条件允许时加入 L1 稀疏约束。",
            "组织测点优化实验：对规则采样、随机抽样、贪心选择或稀疏优化进行对比，形成测点数量—重建精度曲线。",
            "把控最终材料逻辑：提炼创新点、撰写算法与结果章节，统筹 PPT 答辩主线和技术问答。",
        ],
        [
            "评分牵引表与总体流程图。",
            "近远场重建公式推导、核心代码和参数说明。",
            "方向图重建结果、误差热力图、NMSE/相关系数/主瓣误差表。",
            "测点优化曲线和推荐测点布局结论。",
            "报告核心章节、答辩 PPT 主线和答辩问答。",
        ],
        [
            "需要张昊提供近场复数数据、测点坐标、远场真值和仿真模型参数。",
            "需要李伊然提供统一数据字典、识别标签体系和报告调研材料。",
            "每次算法结果更新后，应同步给张昊用于可视化，给李伊然用于报告指标整理。",
        ],
    )
)
story.append(PageBreak())

story.append(
    person_section(
        "张昊",
        "电磁仿真、测量布局与可视化负责人",
        "张昊负责把赛题中的“复杂航空载体”和“全景测试方法”落到可计算、可展示的数据和模型上。这个角色的核心价值是让算法有可信输入，让报告有工程场景，让评委看到传感布局和载体结构不是空泛概念。",
        [
            "确认仿真工具链：优先 CST，若具备条件可用 FEKO 或 COMSOL 作为补充验证；明确频点、边界条件、材料和导出格式。",
            "建立标准源模型：从短偶极子、半波振子或小环天线开始，输出理论可校验的近场数据和远场方向图。",
            "设计测量布局：按照半柱面或半球面布设测点，给出传感器坐标、极化方向、采样密度和被测空间尺寸示意。",
            "构造多源与简化载体模型：用多偶极子、多频点、多极化组合模拟机载设备协同辐射；进一步加入金属圆柱机身、平板机翼和天线安装位置。",
            "建立数据导出流程：保证近场 Ex/Ey/Ez 复数分量、频率、极化、源类型和工作状态能够被算法脚本直接读取。",
            "负责可视化和视频素材：制作测点布局图、三维方向图、仿真模型截图、重建过程录屏和最终演示视频。",
        ],
        [
            "标准源、多源和简化载体仿真模型。",
            "半柱面/半球面测点坐标表与 2π 覆盖示意图。",
            "近场采样数据、远场参考真值和导出说明。",
            "复杂载体安装效应图、多状态数据集。",
            "报告中的模型图、方向图、视频录屏素材。",
        ],
        [
            "向华尔涵提供同一坐标系下的测点坐标、复数场数据和远场真值，避免算法阶段因坐标口径返工。",
            "向李伊然提供源类型、工作状态、频点和极化标签，保证识别数据集可追溯。",
            "根据华尔涵的重建结果，统一图表风格并制作答辩中最直观的空间展示图。",
        ],
    )
)
story.append(PageBreak())

story.append(
    person_section(
        "李伊然",
        "文献调研、数据规范与特征辨识负责人",
        "李伊然负责把作品的研究依据、数据规范和识别评价补齐。这个角色的重点是让主观评分有文献支撑，让数据流不混乱，让特征辨识部分真正达到赛题要求的 85% 准确率门槛。",
        [
            "完成国内外发展调研：围绕近场测量、等效源重建、压缩感知测量、辐射指纹识别四条线整理文献。",
            "建立数据字典：统一 sensor_id、坐标、频率、极化、复数场分量、source_type、working_state 等字段含义。",
            "整理识别数据集：按源类型、安装位置、频点、极化和运行状态建立标签，保证训练集和测试集划分清楚。",
            "进行特征工程：提取主瓣方向、副瓣数量、方向图熵、频谱峰值、极化比、空频相关性等特征。",
            "建立识别基线：优先采用 SVM、随机森林等传统机器学习方法，目标是稳定达到或超过 85% 准确率；若时间允许，再加入 CNN 或自编码器增强展示。",
            "负责复现说明和提交检查：整理 README、运行顺序、数据格式说明、图表清单和提交材料一致性。",
        ],
        [
            "文献调研表、国内外技术路线对比和报告调研章节。",
            "统一数据字典、样例数据说明和标签规范。",
            "特征提取脚本、PCA/t-SNE 可分性图。",
            "识别准确率、Precision、Recall、F1 和混淆矩阵。",
            "复现说明、提交前检查清单和材料格式检查。",
        ],
        [
            "需要张昊提供稳定的数据导出字段和样本标签，避免识别阶段重新清洗数据。",
            "需要华尔涵提供重建后的方向图、误差指标和测点优化结论，作为识别特征和报告结果的一部分。",
            "在最终材料中负责把调研、数据、识别和复现说明整理成评委能快速查证的证据链。",
        ],
    )
)
story.append(PageBreak())

story.append(h1("六、阶段安排与成果落点"))
story.append(
    p(
        "阶段安排不以“填满表格”为目的，而是保证每一阶段都有能支撑评分的成果。建议把最终提交前的工作压缩成五个清晰里程碑。"
    )
)
milestone_rows = [
    [p("时间", "SmallCN"), p("主要目标", "SmallCN"), p("应形成的成果", "SmallCN")],
    [
        p("5月下旬—6月上旬", "SmallCN"),
        p("完成赛题拆解、调研启动、仿真环境确认和标准源模型。", "SmallCN"),
        p("需求拆解、文献框架、标准源模型、初版测点布局。", "SmallCN"),
    ],
    [
        p("6月中旬—7月上旬", "SmallCN"),
        p("跑通近场数据导出、远场真值导出和传播矩阵建模。", "SmallCN"),
        p("近场/远场样例数据、G 矩阵代码、数据字典。", "SmallCN"),
    ],
    [
        p("7月中旬—8月上旬", "SmallCN"),
        p("完成自研近远场重建、误差评估和多源/载体数据扩展。", "SmallCN"),
        p("方向图对比、误差表、简化载体模型、多状态样本。", "SmallCN"),
    ],
    [
        p("8月中旬—8月下旬", "SmallCN"),
        p("完成测点优化和空间—频谱特征识别。", "SmallCN"),
        p("测点数—精度曲线、混淆矩阵、识别准确率报告。", "SmallCN"),
    ],
    [
        p("9月上旬—9月15日前", "SmallCN"),
        p("集中完成报告、PPT、视频、代码复现和提交材料检查。", "SmallCN"),
        p("最终报告、答辩 PPT、演示视频、测试代码、复现说明和压缩包。", "SmallCN"),
    ],
]
story.append(compact_table(milestone_rows, [36 * mm, 72 * mm, 66 * mm]))

story.append(h1("七、团队协同原则"))
for item in [
    "统一坐标系优先。所有仿真数据、测点布局和重建算法必须使用同一坐标定义，否则后期误差会被坐标问题掩盖。",
    "先标准源、后复杂载体。标准源闭环没有跑通前，不把主要精力投入大模型堆复杂度。",
    "每个模块必须有量化输出。传感布局要有坐标和覆盖图，重建要有误差指标，识别要有准确率和混淆矩阵。",
    "最终材料围绕评分项组织。报告和 PPT 不按成员流水账写，而按“测量覆盖—场域重建—测点优化—特征辨识—工程价值”组织。",
]:
    story.append(bullet(item))

story.append(h1("八、预期最终成果"))
for item in [
    "一套覆盖 2π 空间的半柱面/半球面分布式宽带电磁传感布设方案。",
    "标准源、多源和简化航空载体的近场采样数据与远场真值数据。",
    "自研近远场重建算法，包括传播矩阵构建、正则化反演、远场外推和误差评估。",
    "测点数量优化实验，展示在减少测点条件下的重建精度变化。",
    "空间—频谱—极化联合特征识别模型，准确率不低于 85%，并给出混淆矩阵。",
    "方案报告、答辩 PPT、演示视频、测试代码和复现说明。",
]:
    story.append(bullet(item))

doc = WorkPlanDoc(str(PDF_PATH))
doc.build(story)
print(PDF_PATH)
