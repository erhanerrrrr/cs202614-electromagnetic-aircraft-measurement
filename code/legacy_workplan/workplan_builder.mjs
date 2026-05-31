import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const outputDir = path.join(__dirname, "outputs", "contest_work_plan");
const outputPath = path.join(outputDir, "复杂航空载体电磁辐射空域特性测量_工作计划与进度跟踪.xlsx");

const d = (y, m, day) => new Date(y, m - 1, day);

const owners = ["华尔涵", "张昊", "李伊然"];
const statuses = ["未开始", "进行中", "待复核", "已完成", "延期", "暂停"];
const priorities = ["P0", "P1", "P2"];

const tasks = [
  ["H-01", "0 启动与报名", "赛题拆解", "赛题硬约束与评分拆解", "提取提交时间、报名窗口、主客观评分项，形成需求矩阵。", "华尔涵", "张昊, 李伊然", 3, "P0", d(2026, 5, 18), d(2026, 5, 21), "无", "评分牵引表、需求矩阵", "未开始", 0, "团队互审", ""],
  ["H-02", "0 启动与报名", "总体路线", "确定总体技术路线", "明确“仿真数据-近远场重建-测点优化-空频识别-成果包装”的主线。", "华尔涵", "张昊, 李伊然", 2, "P0", d(2026, 5, 20), d(2026, 5, 24), "H-01", "总体流程图、模块边界说明", "未开始", 0, "老师", ""],
  ["H-03", "0 启动与报名", "指标体系", "建立实验评价指标", "定义 NMSE、相关系数、主瓣方向误差、峰值误差、识别准确率等口径。", "华尔涵", "李伊然", 2, "P0", d(2026, 5, 22), d(2026, 5, 27), "H-01", "指标定义表", "未开始", 0, "团队互审", ""],
  ["H-04", "0 启动与报名", "协作环境", "搭建代码仓库与目录结构", "建立 data、simulation、reconstruction、recognition、report 等目录和 README。", "华尔涵", "张昊", 2, "P0", d(2026, 5, 24), d(2026, 5, 30), "H-02", "Git 仓库、目录规范、README", "未开始", 0, "团队互审", ""],
  ["L-01", "1 调研与方案", "文献调研", "国内外发展调研", "调研近场扫描、等效源法、压缩感知测量、辐射指纹识别相关文献。", "李伊然", "华尔涵", 3, "P0", d(2026, 5, 18), d(2026, 5, 31), "H-01", "文献表、调研章节初稿", "未开始", 0, "华尔涵", ""],
  ["L-02", "1 调研与方案", "文献调研", "文献管理与引用格式", "统一文献编号、Bib/引用格式和可引用图表来源，避免报告后期返工。", "李伊然", "", 2, "P1", d(2026, 5, 25), d(2026, 6, 7), "L-01", "参考文献库、引用规范", "未开始", 0, "华尔涵", ""],
  ["Z-01", "1 调研与方案", "仿真准备", "确认仿真软件与授权环境", "确认 CST/FEKO/COMSOL/openEMS 可用性、计算资源和导出格式。", "张昊", "华尔涵", 3, "P0", d(2026, 5, 20), d(2026, 5, 27), "H-02", "软件可用性记录、环境截图", "未开始", 0, "华尔涵", ""],
  ["Z-02", "2 仿真闭环", "标准源仿真", "建立短偶极子/半波振子标准源", "先用标准源验证理论方向图和近远场流程，不直接跳到复杂飞机模型。", "张昊", "华尔涵", 3, "P0", d(2026, 5, 28), d(2026, 6, 8), "Z-01", "标准源模型、方向图截图", "未开始", 0, "华尔涵", ""],
  ["H-05", "2 仿真闭环", "测点布局", "半球面/半柱面测点生成脚本", "参数化生成覆盖 2π 空间立体角的坐标、角度、极化方向，容纳 12m×10m×8m。", "华尔涵", "张昊", 3, "P0", d(2026, 5, 28), d(2026, 6, 10), "H-02", "测点坐标表、布局图", "未开始", 0, "张昊", ""],
  ["Z-03", "2 仿真闭环", "近场采样", "配置近场采样面与导出", "在半球/半柱测点上导出 Ex/Ey/Ez 复数近场数据，覆盖关键频点与极化。", "张昊", "华尔涵", 3, "P0", d(2026, 6, 8), d(2026, 6, 18), "Z-02, H-05", "近场数据样例、导出流程", "未开始", 0, "华尔涵", ""],
  ["Z-04", "2 仿真闭环", "远场真值", "导出远场参考真值并校验", "导出 CST/FEKO 远场方向图，作为自研算法重建精度对比基准。", "张昊", "华尔涵", 3, "P0", d(2026, 6, 12), d(2026, 6, 22), "Z-02", "远场真值数据、理论对比图", "未开始", 0, "华尔涵", ""],
  ["L-03", "2 仿真闭环", "数据规范", "建立统一数据字典", "定义 sensor_id、坐标、频点、极化、复数场分量、源类型、工作状态等字段。", "李伊然", "张昊", 2, "P0", d(2026, 6, 10), d(2026, 6, 20), "Z-03", "数据字典、样例数据说明", "未开始", 0, "华尔涵", ""],
  ["Z-07", "2 仿真闭环", "数据接口", "批量导出与命名脚本", "整理多频点、多状态、多极化数据的导出、命名、归档规则。", "张昊", "李伊然", 2, "P1", d(2026, 6, 16), d(2026, 6, 28), "Z-03, L-03", "批处理脚本、数据清单", "未开始", 0, "华尔涵", ""],
  ["H-06", "3 重建算法", "物理模型", "等效源/Huygens 面建模方案", "确定等效偶极子阵列或 Huygens 面，明确测量场与等效源变量。", "华尔涵", "张昊", 3, "P0", d(2026, 6, 18), d(2026, 6, 28), "H-03, Z-03", "算法建模说明、公式推导", "未开始", 0, "老师", ""],
  ["H-07", "3 重建算法", "传播矩阵", "构建传播矩阵 G", "基于 Green 函数/等效源法建立测点场与等效源之间的线性关系。", "华尔涵", "张昊", 5, "P0", d(2026, 6, 24), d(2026, 7, 10), "H-06", "G 矩阵代码、单频验证结果", "未开始", 0, "张昊", ""],
  ["H-08", "3 重建算法", "反演求解", "实现 Tikhonov/SVD 反演", "求解 min ||GJ-E||² + λ||J||²，并完成 λ 参数扫描。", "华尔涵", "李伊然", 5, "P0", d(2026, 7, 4), d(2026, 7, 20), "H-07", "反演代码、参数扫描曲线", "未开始", 0, "团队互审", ""],
  ["H-09", "3 重建算法", "远场外推", "重建远场方向图并与真值对比", "由等效源计算远场，输出二维/三维方向图和误差热力图。", "华尔涵", "张昊", 4, "P0", d(2026, 7, 14), d(2026, 7, 28), "H-08, Z-04", "方向图对比、误差热力图", "未开始", 0, "老师", ""],
  ["H-10", "3 重建算法", "误差评估", "形成重建精度评估报告", "用 NMSE、相关系数、主瓣误差、峰值误差统一评估各实验组。", "华尔涵", "李伊然", 3, "P0", d(2026, 7, 22), d(2026, 8, 2), "H-09", "误差表、结论段落", "未开始", 0, "团队互审", ""],
  ["Z-05", "2 仿真闭环", "复杂源仿真", "多源/多频/多极化模型", "构造多偶极子、多频源、不同极化组合，模拟机载多设备协同辐射。", "张昊", "华尔涵", 4, "P1", d(2026, 6, 24), d(2026, 7, 15), "Z-02", "多源模型、多状态数据", "未开始", 0, "华尔涵", ""],
  ["Z-06", "2 仿真闭环", "载体模型", "简化航空载体结构模型", "建立金属圆柱机身、平板机翼和多天线安装模型，体现遮挡和散射影响。", "张昊", "华尔涵", 4, "P1", d(2026, 7, 8), d(2026, 7, 31), "Z-05", "简化载体模型、安装效应图", "未开始", 0, "老师", ""],
  ["H-11", "4 测点优化", "稀疏采样", "测点数量优化与压缩感知实验", "比较 100%、75%、50%、25% 和优化采样，目标是同等精度下减少测点。", "华尔涵", "张昊", 4, "P0", d(2026, 7, 24), d(2026, 8, 12), "H-09", "测点数-误差曲线、优化坐标表", "未开始", 0, "老师", ""],
  ["H-12", "4 测点优化", "鲁棒性", "噪声与频点鲁棒性实验", "加入噪声、频点变化、测点缺失，评估算法稳定性和工程可用性。", "华尔涵", "李伊然", 3, "P1", d(2026, 8, 5), d(2026, 8, 18), "H-10, H-11", "鲁棒性曲线、结论表", "未开始", 0, "团队互审", ""],
  ["L-04", "5 特征辨识", "特征工程", "空间-频谱-极化联合特征提取", "提取主瓣方向、副瓣数量、方向图熵、频谱峰值、极化比、空频相关性。", "李伊然", "华尔涵", 3, "P0", d(2026, 7, 22), d(2026, 8, 6), "L-03, Z-05", "特征表、可分性可视化", "未开始", 0, "华尔涵", ""],
  ["L-05", "5 特征辨识", "分类基线", "SVM/随机森林识别基线", "以典型辐射源和工作状态为标签，建立 Accuracy ≥85% 的可解释基线。", "李伊然", "华尔涵", 3, "P0", d(2026, 8, 1), d(2026, 8, 15), "L-04", "训练脚本、准确率结果", "未开始", 0, "华尔涵", ""],
  ["L-06", "5 特征辨识", "评价结果", "混淆矩阵与识别报告", "输出 Accuracy、Precision、Recall、F1 和混淆矩阵，说明可区分性来源。", "李伊然", "华尔涵", 2, "P0", d(2026, 8, 12), d(2026, 8, 22), "L-05", "混淆矩阵、指标表", "未开始", 0, "团队互审", ""],
  ["Z-08", "6 展示包装", "可视化", "三维测点与方向图可视化", "制作半柱/半球布局、远场方向图、误差曲线、状态指纹图的统一视觉模板。", "张昊", "华尔涵, 李伊然", 2, "P1", d(2026, 8, 10), d(2026, 8, 25), "H-09, L-06", "统一图表模板、核心图集", "未开始", 0, "华尔涵", ""],
  ["H-13", "6 展示包装", "方案报告", "撰写算法与核心结果章节", "整理重建算法、测点优化、精度排名逻辑和关键创新点。", "华尔涵", "李伊然", 3, "P0", d(2026, 8, 14), d(2026, 8, 30), "H-12", "报告算法章节、结果章节", "未开始", 0, "老师", ""],
  ["L-07", "6 展示包装", "方案报告", "撰写背景调研与识别章节", "完成国内外调研、数据集说明、特征辨识方法和结果解释。", "李伊然", "华尔涵", 2, "P1", d(2026, 8, 14), d(2026, 8, 30), "L-01, L-06", "报告调研章节、识别章节", "未开始", 0, "华尔涵", ""],
  ["Z-10", "6 展示包装", "方案报告", "撰写仿真系统与模型章节", "说明仿真对象分级、传感布局、导出数据和复杂载体模型。", "张昊", "华尔涵", 3, "P1", d(2026, 8, 14), d(2026, 8, 30), "Z-06, Z-08", "报告仿真章节、模型图", "未开始", 0, "华尔涵", ""],
  ["H-16", "6 展示包装", "创新点", "提炼创新点与答辩防守口径", "围绕高精度重建、少测点、空频指纹和可复现闭环提炼答辩说法。", "华尔涵", "张昊, 李伊然", 3, "P0", d(2026, 8, 24), d(2026, 9, 3), "H-13, L-07, Z-10", "创新点页、答辩 Q&A", "未开始", 0, "老师", ""],
  ["H-14", "6 展示包装", "答辩 PPT", "制作 10-15 页答辩 PPT 主线", "组织问题背景、总体方案、核心算法、结果对比、创新点、计划与应用价值。", "华尔涵", "张昊, 李伊然", 3, "P0", d(2026, 8, 26), d(2026, 9, 6), "H-16", "答辩 PPT 初稿", "未开始", 0, "老师", ""],
  ["Z-09", "6 展示包装", "视频录屏", "制作 2-3 分钟演示视频素材", "录制仿真模型、测点布局、重建过程、识别结果和运行代码。", "张昊", "华尔涵", 3, "P1", d(2026, 8, 26), d(2026, 9, 8), "Z-08, H-14", "视频脚本、录屏素材、成片", "未开始", 0, "团队互审", ""],
  ["L-09", "7 复核提交", "复现说明", "整理环境配置和运行顺序", "写清依赖、数据路径、脚本运行顺序、主要参数和复现实验入口。", "李伊然", "华尔涵", 2, "P0", d(2026, 8, 28), d(2026, 9, 8), "H-04, L-05", "README、复现说明", "未开始", 0, "华尔涵", ""],
  ["L-08", "7 复核提交", "质量检查", "交付物清单与一致性检查", "检查报告、PPT、视频、代码、报名表、压缩包命名和邮件主题格式。", "李伊然", "张昊", 1, "P0", d(2026, 9, 5), d(2026, 9, 12), "H-14, Z-09, L-09", "提交前检查表", "未开始", 0, "华尔涵", ""],
  ["H-15", "7 复核提交", "最终提交", "最终集成、模拟答辩与提交", "完成代码可运行检查、报告/PPT 终稿、视频压缩、系统提交和邮件报送。", "华尔涵", "张昊, 李伊然", 2, "P0", d(2026, 9, 8), d(2026, 9, 15), "全部核心任务", "最终压缩包、提交记录", "未开始", 0, "老师", "9月15日前完成"],
];

const weeks = [
  ["W01", "2026-05-18 至 2026-05-24", "启动与赛题拆解", "完成评分项拆解、总体路线初稿。", "确认仿真软件、准备标准源环境。", "启动文献检索和调研表。", "需求矩阵 v0.1、路线草图", "能否清楚回答 100 分评分如何拿分？", "未开始"],
  ["W02", "2026-05-25 至 2026-05-31", "路线定稿与报名准备", "搭建仓库、确定评价指标。", "完成标准源建模准备。", "完成首轮文献综述和引用库。", "Git 目录、指标表、调研表", "报名材料和技术路线是否一致？", "未开始"],
  ["W03", "2026-06-01 至 2026-06-07", "标准源闭环启动", "测点布局脚本原型。", "短偶极子/半波振子仿真。", "数据字段规范草案。", "标准源模型、布局坐标样例", "近场与远场数据是否能导出？", "未开始"],
  ["W04", "2026-06-08 至 2026-06-14", "近场采样与数据格式", "完善 2π 半球/半柱布局。", "配置近场采样面。", "细化 HDF5/npz/CSV 数据字典。", "近场样例数据、字段说明", "每个测点的复数场分量是否齐全？", "未开始"],
  ["W05", "2026-06-15 至 2026-06-21", "远场真值与数据接口", "准备等效源建模方案。", "导出远场真值和批处理脚本。", "数据清单模板。", "远场真值图、导出流程", "真值、近场和坐标能否一一对应？", "未开始"],
  ["W06", "2026-06-22 至 2026-06-28", "传播模型设计", "完成 Huygens/等效源模型推导。", "启动多源模型。", "协助数据归档。", "算法公式说明、传播模型草案", "G 矩阵维度和物理量是否自洽？", "未开始"],
  ["W07", "2026-06-29 至 2026-07-05", "G 矩阵实现", "编写传播矩阵代码并做单频测试。", "提供标准源数据补充。", "检查数据读入接口。", "单频传播矩阵、读数脚本", "是否能从近场数据跑到待反演矩阵？", "未开始"],
  ["W08", "2026-07-06 至 2026-07-12", "反演算法初版", "实现 Tikhonov/SVD 反演。", "推进简化载体模型。", "准备识别标签体系。", "反演代码 v0.1、载体模型草图", "标准源重建误差是否可接受？", "未开始"],
  ["W09", "2026-07-13 至 2026-07-19", "远场重建对比", "完成方向图重建与真值对比。", "输出多源/载体数据初版。", "准备特征工程脚本。", "方向图对比图、误差热力图", "能否展示“自研算法”而非软件截图？", "未开始"],
  ["W10", "2026-07-20 至 2026-07-26", "误差体系与多状态数据", "形成误差评估表。", "完善多源、多极化数据集。", "启动空间-频谱特征提取。", "误差指标表、特征表初版", "重建评价指标是否能支持排序？", "未开始"],
  ["W11", "2026-07-27 至 2026-08-02", "测点优化启动", "设计 100/75/50/25% 对比实验。", "完成简化载体仿真图。", "完善特征可分性分析。", "测点压缩实验方案", "减少测点后精度损失如何说明？", "未开始"],
  ["W12", "2026-08-03 至 2026-08-09", "识别基线启动", "推进稀疏优化策略。", "补充仿真数据缺口。", "训练 SVM/随机森林基线。", "识别准确率初值、测点误差曲线", "识别精度是否达到 85%？", "未开始"],
  ["W13", "2026-08-10 至 2026-08-16", "优化与鲁棒性", "完成测点优化和噪声鲁棒性。", "制作统一图表模板。", "完成混淆矩阵与指标报告。", "测点数-精度曲线、混淆矩阵", "客观 60 分的证据链是否完整？", "未开始"],
  ["W14", "2026-08-17 至 2026-08-23", "结果冻结与报告初稿", "冻结核心算法结果。", "整理模型图和方向图。", "撰写调研/识别章节。", "报告初稿 v0.5、核心图集", "报告是否有图、有表、有指标？", "未开始"],
  ["W15", "2026-08-24 至 2026-08-30", "材料整合", "撰写算法章节、提炼创新点。", "撰写仿真章节、视频脚本。", "整理复现说明。", "报告 v0.8、PPT 大纲、视频脚本", "技术故事是否能在 10-15 页讲清？", "未开始"],
  ["W16", "2026-08-31 至 2026-09-06", "PPT 与视频初稿", "完成 PPT 初稿和答辩 Q&A。", "录制仿真/可视化素材。", "完成 README 初稿。", "PPT 初稿、录屏素材、README", "老师评审意见是否闭环？", "未开始"],
  ["W17", "2026-09-07 至 2026-09-13", "终稿复核", "最终集成与模拟答辩。", "剪辑视频、检查图表。", "交付物清单和命名检查。", "报告/PPT/视频/代码终稿", "压缩包是否完整、可运行、可追溯？", "未开始"],
  ["W18", "2026-09-14 至 2026-09-15", "提交", "完成系统提交和邮件报送。", "协助提交材料备份。", "核对报名表与系统信息。", "提交记录、备份包", "是否早于 9 月 15 日完成提交？", "未开始"],
  ["W19", "2026-10-01 至 2026-11-30", "入围后完善预案", "根据专家意见优化重建与答辩。", "补充更复杂仿真或现场条件说明。", "补充材料和演示脚本。", "擂台赛版 PPT、演示包", "若入围，是否能快速升级到擂台赛版本？", "未开始"],
];

const scoreMap = [
  ["国内外发展调研分析", 10, "主观分：国内外发展调研分析情况。", "形成近场测量、等效源法、压缩感知、辐射指纹识别四条文献线。", "文献表、技术路线对比表、报告调研章节", "李伊然", "L-01, L-02", d(2026, 6, 7)],
  ["研究思路合理性", 10, "主观分：研究思路合理性。", "用“标准源闭环-多源复杂化-载体安装效应-识别验证”的递进路线。", "总体流程图、阶段性实验闭环", "华尔涵", "H-01, H-02", d(2026, 5, 31)],
  ["技术路线可行性", 10, "主观分：技术路线可行性。", "CST/FEKO 生成数据，Python/MATLAB 自研近远场重建，scikit-learn/PyTorch 做识别。", "工具链说明、可运行代码、样例数据", "华尔涵", "H-04, Z-01, L-03", d(2026, 6, 20)],
  ["测试方案完整性", 10, "主观分：测试方案完整性。", "覆盖传感布局、近场采样、真值对比、测点压缩、鲁棒性和识别评价。", "测试矩阵、交付物清单、复现说明", "华尔涵", "H-03, L-09", d(2026, 9, 8)],
  ["传感布局覆盖", 10, "客观分：多角度、多极化、宽频段；覆盖 2π 半柱面或半球面；容纳不小于 12m×10m×8m。", "参数化半柱/半球布局，给出坐标、极化和覆盖示意。", "测点坐标表、布局图、尺寸标注", "张昊", "H-05, Z-03", d(2026, 6, 18)],
  ["三维场域重建", 30, "客观分：高精度重建且尽量减少测点，按精度和测点数量排序。", "等效源反演 + Tikhonov/L1 稀疏，输出重建方向图、误差曲线、测点优化曲线。", "重建代码、方向图对比、NMSE/相关系数/主瓣误差、测点数-精度曲线", "华尔涵", "H-06 至 H-12", d(2026, 8, 18)],
  ["特征辨识精度", 20, "客观分：典型辐射源空间频率特征辨识精度不低于 85%。", "先做传统特征 + SVM/随机森林基线，必要时加入 CNN/自编码器加分。", "准确率、F1、混淆矩阵、空间-频谱指纹图", "李伊然", "L-04 至 L-06", d(2026, 8, 22)],
];

const deliverables = [
  ["报名表", "2026-05-30 至 2026-06-30 在线报名并上传盖章报名表。", "华尔涵", d(2026, 6, 25), "未开始", "系统审核通过，信息与提交材料一致。"],
  ["方案报告", "背景调研、需求分析、技术路线、系统设计、算法设计、仿真结果、误差分析、识别结果。", "华尔涵", d(2026, 9, 6), "未开始", "所有核心结论有图表和指标支撑。"],
  ["答辩 PPT", "10-15 页：背景、方案、传感布局、重建算法、测点优化、识别结果、创新点。", "华尔涵", d(2026, 9, 6), "未开始", "可在 8-10 分钟内讲清楚主线。"],
  ["视频/录屏", "2-3 分钟展示仿真模型、测点布局、重建流程、识别结果和代码运行。", "张昊", d(2026, 9, 8), "未开始", "画面清晰，有字幕或讲解，能支撑评审快速理解。"],
  ["仿真模型", "标准源、多源、多极化、简化航空载体模型。", "张昊", d(2026, 7, 31), "未开始", "模型可复查，参数和频点有说明。"],
  ["近场/远场数据集", "近场复数数据、远场真值、不同状态数据集、测点坐标表。", "张昊", d(2026, 8, 5), "未开始", "数据字段完整，样本能被算法脚本直接读取。"],
  ["近远场重建代码", "数据读取、传播矩阵、反演求解、远场外推、误差评估。", "华尔涵", d(2026, 8, 12), "未开始", "一条命令或清晰步骤可复现核心图。"],
  ["测点优化代码", "规则抽样、随机抽样、贪心/稀疏优化、精度对比。", "华尔涵", d(2026, 8, 18), "未开始", "输出测点数-精度曲线和优化坐标表。"],
  ["识别代码", "特征提取、训练、验证、混淆矩阵和指标输出。", "李伊然", d(2026, 8, 22), "未开始", "Accuracy >= 85%，并保留训练/测试划分。"],
  ["结果图表", "布局图、方向图对比、误差热力图、测点曲线、混淆矩阵、流程图。", "张昊", d(2026, 8, 25), "未开始", "图表风格统一，坐标轴/单位/图例完整。"],
  ["复现说明", "环境配置、运行顺序、数据格式、主要参数、文件结构。", "李伊然", d(2026, 9, 8), "未开始", "换一台电脑按说明能跑通核心结果。"],
  ["最终压缩包", "报告、PPT、视频、代码、数据样例、报名表扫描件和说明文档。", "华尔涵", d(2026, 9, 15), "未开始", "按赛题要求命名并完成系统/邮件提交。"],
];

const risks = [
  ["仿真模型过大", "高", "中", "CST/FEKO 计算时间过长或内存不足。", "先标准源，再多源，最后简化载体；控制频点和网格规模。", "张昊", d(2026, 6, 8), "用解析模型/openEMS 数据补齐算法验证。"],
  ["只停留在软件远场截图", "高", "中", "报告缺少自研重建算法和误差指标。", "必须导出近场数据，自主实现 GJ 反演和远场外推。", "华尔涵", d(2026, 7, 10), "保留软件远场仅作真值，不作为核心算法。"],
  ["重建精度不稳定", "高", "中", "NMSE 高、主瓣方向偏差大。", "做 λ 扫描、SVD 截断、噪声归一化和坐标校验。", "华尔涵", d(2026, 7, 28), "降低模型复杂度，先保证标准源闭环。"],
  ["测点优化说服力不足", "中", "中", "随机删点无明显优于规则采样。", "设计 100/75/50/25% 和优化采样对照，使用统一误差指标。", "华尔涵", d(2026, 8, 12), "以工程可用折中点展示，不强行追求极限压缩。"],
  ["识别准确率低于 85%", "高", "中", "多状态样本混叠或样本量不足。", "先构造可控差异样本，做传统特征基线，再引入深度模型。", "李伊然", d(2026, 8, 15), "减少类别数或聚焦典型源/状态，确保达标基线。"],
  ["数据格式混乱", "中", "中", "脚本读取失败或字段含义不一致。", "统一数据字典、命名和样例，所有脚本使用同一读入接口。", "李伊然", d(2026, 6, 20), "转为 CSV/npz 简化格式并冻结字段。"],
  ["报告像概念方案", "高", "低", "文字多、量化结果少。", "每个模块至少一图一表一指标，优先展示客观评分证据。", "华尔涵", d(2026, 8, 30), "删减空泛背景，集中展示实验闭环。"],
  ["提交材料遗漏", "中", "低", "缺报名表、视频或代码说明。", "用交付物清单逐项勾选，9月12日前完成全量检查。", "李伊然", d(2026, 9, 12), "准备最终压缩包和云端/本地备份。"],
];

const fields = [
  ["sensor_id", "测点编号", "字符串/整数", "唯一定位一个传感器位置。"],
  ["x, y, z", "传感器坐标", "米", "统一坐标系，报告中说明原点与轴向。"],
  ["theta, phi", "球坐标角度", "度或弧度", "需在数据字典中固定单位。"],
  ["frequency", "频率", "Hz/GHz", "用于宽频段空频特征。"],
  ["polarization", "极化", "H/V/Ex/Ey/Ez", "至少考虑两个正交极化或三分量场。"],
  ["Ex/Ey/Ez_real", "电场实部", "V/m", "复数近场数据的一部分。"],
  ["Ex/Ey/Ez_imag", "电场虚部", "V/m", "复数近场数据的一部分。"],
  ["source_type", "辐射源类型", "类别", "识别标签之一。"],
  ["working_state", "运行状态", "类别", "通信源开关、雷达源开关、多源同时工作等。"],
  ["sample_id", "样本编号", "字符串", "关联同一状态、频点和测点集合。"],
];

const workbook = Workbook.create();
const overview = workbook.worksheets.add("总览");
const taskSheet = workbook.worksheets.add("任务跟踪");
const weekSheet = workbook.worksheets.add("每周计划");
const scoreSheet = workbook.worksheets.add("评分映射");
const deliverSheet = workbook.worksheets.add("交付物清单");
const riskSheet = workbook.worksheets.add("风险清单");
const dataSheet = workbook.worksheets.add("数据规范");

function writeTable(sheet, startCell, headers, rows) {
  const range = sheet.getRange(startCell).resize(rows.length + 1, headers.length);
  range.values = [headers, ...rows];
  const headerRange = sheet.getRange(startCell).resize(1, headers.length);
  headerRange.format = {
    fill: "#245B6B",
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
  };
  range.format = {
    wrapText: true,
    borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } },
  };
  return range;
}

function setWidths(sheet, widths) {
  widths.forEach((width, i) => {
    const col = String.fromCharCode("A".charCodeAt(0) + i);
    sheet.getRange(`${col}:${col}`).format.columnWidthPx = width;
  });
}

function styleTitle(sheet, range, title, subtitle) {
  const titleRange = sheet.getRange(range);
  titleRange.merge();
  titleRange.values = [[title]];
  titleRange.format = {
    fill: "#12343B",
    font: { bold: true, color: "#FFFFFF", size: 16 },
  };
  if (subtitle) {
    const sub = sheet.getRange("A2:N2");
    sub.merge();
    sub.values = [[subtitle]];
    sub.format = { fill: "#E7F0F2", font: { color: "#12343B", italic: true }, wrapText: true };
  }
}

function addValidation(range, values) {
  try {
    range.dataValidation = { rule: { type: "list", values } };
  } catch {}
}

function addTable(sheet, address, name, style = "TableStyleMedium2") {
  try {
    const table = sheet.tables.add(address, true, name);
    table.style = style;
    table.showFilterButton = true;
    return table;
  } catch {
    return null;
  }
}

overview.showGridLines = false;
styleTitle(
  overview,
  "A1:N1",
  "复杂航空载体电磁辐射空域特性测量技术比赛工作计划",
  "基于赛题 CS-202614：9月15日前提交作品；报名窗口为2026-05-30至2026-06-30；主攻三维场域重建、测点优化和空间-频谱特征辨识。"
);
setWidths(overview, [120, 140, 120, 120, 120, 120, 130, 130, 120, 120, 120, 120, 120, 120]);
overview.getRange("A1:N1").format.rowHeightPx = 30;
overview.getRange("A2:N2").format.rowHeightPx = 26;
overview.getRange("A4:N22").format.rowHeightPx = 28;
overview.getRange("A5:B6").format.rowHeightPx = 40;
overview.getRange("F14:N21").format.rowHeightPx = 48;

overview.getRange("A4:B10").values = [
  ["项目关键节点", "日期/要求"],
  ["团队成员", "华尔涵、张昊、李伊然"],
  ["责任比例", "华尔涵 50%；张昊 30%；李伊然 20%"],
  ["报名窗口", "2026-05-30 至 2026-06-30"],
  ["作品提交", "2026-09-15 前"],
  ["初审结果", "2026-09-30 前"],
  ["终审擂台赛", "2026-11"],
];
overview.getRange("A4:B4").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
overview.getRange("A4:B10").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };

overview.getRange("D4:H9").values = [
  ["进度仪表盘", "数值", "说明", "", ""],
  ["总任务数", null, "任务跟踪表中的 WBS 数量", "", ""],
  ["计划工作量点", null, "三人总任务点数，应为100", "", ""],
  ["加权总进度", null, "按工作量点加权", "", ""],
  ["已完成任务数", null, "状态为“已完成”", "", ""],
  ["逾期未完成", null, "截止日期早于 TODAY 且未完成", "", ""],
];
overview.getRange("E5:E9").formulas = [
  ["=COUNTA('任务跟踪'!$A$2:$A$80)"],
  ["=SUM('任务跟踪'!$H$2:$H$80)"],
  ["=SUMPRODUCT('任务跟踪'!$H$2:$H$80,'任务跟踪'!$O$2:$O$80)/SUM('任务跟踪'!$H$2:$H$80)"],
  ["=COUNTIF('任务跟踪'!$N$2:$N$80,\"已完成\")"],
  ["=COUNTIFS('任务跟踪'!$A$2:$A$80,\"<>\",'任务跟踪'!$K$2:$K$80,\"<\"&TODAY(),'任务跟踪'!$N$2:$N$80,\"<>已完成\")"],
];
overview.getRange("D4:H4").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
overview.getRange("D4:H9").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };
overview.getRange("E7:E7").format.numberFormat = "0%";

overview.getRange("A13:D17").values = [
  ["成员工作量分配", "目标占比", "任务点数", "加权进度"],
  ["华尔涵", 0.5, null, null],
  ["张昊", 0.3, null, null],
  ["李伊然", 0.2, null, null],
  ["合计", 1, null, null],
];
overview.getRange("C14:D16").formulas = [
  ["=SUMIF('任务跟踪'!$F$2:$F$80,A14,'任务跟踪'!$H$2:$H$80)", "=IFERROR(SUMPRODUCT(('任务跟踪'!$F$2:$F$80=A14)*'任务跟踪'!$H$2:$H$80*'任务跟踪'!$O$2:$O$80)/C14,0)"],
  ["=SUMIF('任务跟踪'!$F$2:$F$80,A15,'任务跟踪'!$H$2:$H$80)", "=IFERROR(SUMPRODUCT(('任务跟踪'!$F$2:$F$80=A15)*'任务跟踪'!$H$2:$H$80*'任务跟踪'!$O$2:$O$80)/C15,0)"],
  ["=SUMIF('任务跟踪'!$F$2:$F$80,A16,'任务跟踪'!$H$2:$H$80)", "=IFERROR(SUMPRODUCT(('任务跟踪'!$F$2:$F$80=A16)*'任务跟踪'!$H$2:$H$80*'任务跟踪'!$O$2:$O$80)/C16,0)"],
];
overview.getRange("C17:D17").formulas = [["=SUM(C14:C16)", "=SUMPRODUCT(C14:C16,D14:D16)/C17"]];
overview.getRange("A13:D13").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
overview.getRange("B14:B17").format.numberFormat = "0%";
overview.getRange("D14:D17").format.numberFormat = "0%";
overview.getRange("A13:D17").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };

overview.getRange("F13:N21").values = [
  ["阶段里程碑", "开始", "结束", "核心目标", "主责", "验收标准", "状态", "备注", ""],
  ["0 启动与报名", d(2026, 5, 18), d(2026, 6, 30), "完成报名、评分拆解、技术路线和协作环境。", "华尔涵", "报名材料无误，路线图清晰。", "未开始", "", ""],
  ["1 调研与方案", d(2026, 5, 18), d(2026, 6, 7), "形成国内外调研和方案依据。", "李伊然", "调研可支撑主观分。", "未开始", "", ""],
  ["2 仿真闭环", d(2026, 5, 28), d(2026, 7, 31), "生成标准源、多源、简化载体近场/远场数据。", "张昊", "近场和真值一一对应。", "未开始", "", ""],
  ["3 重建算法", d(2026, 6, 18), d(2026, 8, 2), "完成等效源反演和远场重建精度评估。", "华尔涵", "重建结果有真值对比。", "未开始", "", ""],
  ["4 测点优化", d(2026, 7, 24), d(2026, 8, 18), "在精度可接受前提下减少测点。", "华尔涵", "有测点数-误差曲线。", "未开始", "", ""],
  ["5 特征辨识", d(2026, 7, 22), d(2026, 8, 22), "完成空间-频谱特征识别，Accuracy >=85%。", "李伊然", "有混淆矩阵和指标。", "未开始", "", ""],
  ["6 展示包装", d(2026, 8, 10), d(2026, 9, 8), "完成报告、PPT、视频和图表统一。", "华尔涵", "材料可答辩。", "未开始", "", ""],
  ["7 复核提交", d(2026, 9, 5), d(2026, 9, 15), "完成复现检查、压缩包、系统和邮件提交。", "华尔涵", "提交记录可追溯。", "未开始", "", ""],
];
overview.getRange("F13:N13").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
overview.getRange("G14:H21").format.numberFormat = "yyyy-mm-dd";
overview.getRange("F13:N21").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };

try {
  overview.getRange("M24:N27").values = [
    ["成员", "任务点数"],
    ["华尔涵", 50],
    ["张昊", 30],
    ["李伊然", 20],
  ];
  overview.getRange("M24:N27").format = { fill: "#FFFFFF", font: { color: "#FFFFFF" } };
  const chart = overview.charts.add("bar", overview.getRange("M24:N27"));
  chart.title = "团队计划工作量分配";
  chart.hasLegend = false;
  chart.xAxis = { axisType: "textAxis" };
  chart.setPosition("A20", "E36");
} catch {}

taskSheet.showGridLines = false;
const taskHeaders = ["任务ID", "阶段", "模块", "任务", "任务说明", "负责人", "协作人", "工作量点", "优先级", "开始日期", "截止日期", "依赖任务", "交付物/验收证据", "状态", "进度", "审核人", "备注"];
writeTable(taskSheet, "A1", taskHeaders, tasks);
setWidths(taskSheet, [70, 105, 90, 170, 300, 80, 120, 70, 60, 95, 95, 120, 250, 80, 70, 90, 140]);
taskSheet.freezePanes.freezeRows(1);
taskSheet.getRange("H2:H80").format.numberFormat = "0";
taskSheet.getRange("J2:K80").format.numberFormat = "yyyy-mm-dd";
taskSheet.getRange("O2:O80").format.numberFormat = "0%";
addValidation(taskSheet.getRange("F2:F80"), owners);
addValidation(taskSheet.getRange("I2:I80"), priorities);
addValidation(taskSheet.getRange("N2:N80"), statuses);
addTable(taskSheet, `A1:Q${tasks.length + 1}`, "TasksTable", "TableStyleMedium2");
try {
  taskSheet.getRange("O2:O80").conditionalFormats.add("dataBar", { color: "#3B82F6", thresholds: ["min", "max"] });
  taskSheet.getRange("N2:N80").conditionalFormats.add("containsText", { text: "延期", format: { fill: "#FEE2E2", font: { color: "#991B1B", bold: true } } });
  taskSheet.getRange("N2:N80").conditionalFormats.add("containsText", { text: "已完成", format: { fill: "#DCFCE7", font: { color: "#166534", bold: true } } });
} catch {}

weekSheet.showGridLines = false;
const weekHeaders = ["周次", "日期范围", "阶段目标", "华尔涵重点", "张昊重点", "李伊然重点", "周验收物", "周会检查问题", "状态"];
writeTable(weekSheet, "A1", weekHeaders, weeks);
setWidths(weekSheet, [60, 160, 170, 230, 230, 230, 220, 260, 80]);
weekSheet.freezePanes.freezeRows(1);
addValidation(weekSheet.getRange("I2:I40"), statuses);
addTable(weekSheet, `A1:I${weeks.length + 1}`, "WeeklyPlanTable", "TableStyleMedium4");

scoreSheet.showGridLines = false;
const scoreHeaders = ["评分维度", "分值", "赛题原要求", "本队策略/目标", "关键证据", "主责", "对应任务", "目标日期"];
writeTable(scoreSheet, "A1", scoreHeaders, scoreMap);
setWidths(scoreSheet, [140, 60, 320, 330, 300, 80, 130, 100]);
scoreSheet.freezePanes.freezeRows(1);
scoreSheet.getRange("B2:B20").format.numberFormat = "0";
scoreSheet.getRange("H2:H20").format.numberFormat = "yyyy-mm-dd";
addTable(scoreSheet, `A1:H${scoreMap.length + 1}`, "ScoreMapTable", "TableStyleMedium7");

deliverSheet.showGridLines = false;
const deliverHeaders = ["交付物", "内容要求", "负责人", "截止日期", "状态", "验收标准"];
writeTable(deliverSheet, "A1", deliverHeaders, deliverables);
setWidths(deliverSheet, [130, 360, 80, 100, 80, 360]);
deliverSheet.freezePanes.freezeRows(1);
deliverSheet.getRange("D2:D40").format.numberFormat = "yyyy-mm-dd";
addValidation(deliverSheet.getRange("C2:C40"), owners);
addValidation(deliverSheet.getRange("E2:E40"), statuses);
addTable(deliverSheet, `A1:F${deliverables.length + 1}`, "DeliverablesTable", "TableStyleMedium9");

riskSheet.showGridLines = false;
const riskHeaders = ["风险", "影响", "概率", "预警信号", "规避措施", "负责人", "检查日期", "备选方案"];
writeTable(riskSheet, "A1", riskHeaders, risks);
setWidths(riskSheet, [140, 70, 70, 280, 330, 80, 100, 260]);
riskSheet.freezePanes.freezeRows(1);
riskSheet.getRange("G2:G30").format.numberFormat = "yyyy-mm-dd";
addValidation(riskSheet.getRange("B2:B30"), ["高", "中", "低"]);
addValidation(riskSheet.getRange("C2:C30"), ["高", "中", "低"]);
addValidation(riskSheet.getRange("F2:F30"), owners);
addTable(riskSheet, `A1:H${risks.length + 1}`, "RisksTable", "TableStyleMedium3");

dataSheet.showGridLines = false;
styleTitle(dataSheet, "A1:H1", "数据与代码规范", "用于保证仿真、重建、识别、报告之间的数据可复现。");
setWidths(dataSheet, [120, 140, 110, 420, 120, 160, 220, 220]);
dataSheet.getRange("A4:D4").values = [["字段", "含义", "单位/类型", "备注"]];
dataSheet.getRange("A5:D14").values = fields;
dataSheet.getRange("A4:D4").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
dataSheet.getRange("A4:D14").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };
dataSheet.getRange("F4:H13").values = [
  ["建议目录", "用途", "负责人"],
  ["data/raw", "仿真原始导出数据，仅归档不改写。", "张昊"],
  ["data/processed", "统一格式后的 npz/HDF5/CSV。", "李伊然"],
  ["simulation", "仿真模型、参数表、导出脚本。", "张昊"],
  ["reconstruction", "传播矩阵、反演、远场外推、误差评估。", "华尔涵"],
  ["recognition", "特征提取、分类训练、混淆矩阵。", "李伊然"],
  ["figures", "布局图、方向图、误差图、识别图。", "张昊"],
  ["report", "方案报告、PPT、视频脚本。", "华尔涵"],
  ["docs", "文献表、会议纪要、复现说明。", "李伊然"],
  ["outputs", "最终提交材料和备份压缩包。", "华尔涵"],
];
dataSheet.getRange("F4:H4").format = { fill: "#245B6B", font: { bold: true, color: "#FFFFFF" } };
dataSheet.getRange("F4:H13").format = { wrapText: true, borders: { insideHorizontal: { color: "#D6DEE3" }, insideVertical: { color: "#D6DEE3" }, outline: { color: "#9FB2BD" } } };

const weights = tasks.reduce((acc, row) => {
  acc.total += row[7];
  acc[row[5]] = (acc[row[5]] || 0) + row[7];
  return acc;
}, { total: 0 });

await fs.mkdir(outputDir, { recursive: true });

for (const sheetName of ["总览", "任务跟踪", "每周计划", "评分映射", "交付物清单", "风险清单", "数据规范"]) {
  try {
    const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
    await fs.writeFile(path.join(outputDir, `${sheetName}.png`), new Uint8Array(await preview.arrayBuffer()));
  } catch {}
}

const summary = await workbook.inspect({
  kind: "table",
  range: "总览!A1:N22",
  include: "values,formulas",
  tableMaxRows: 22,
  tableMaxCols: 14,
  maxChars: 6000,
});
console.log(summary.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);
console.log(JSON.stringify(weights));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(outputPath);
