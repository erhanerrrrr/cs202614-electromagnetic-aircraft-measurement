from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "scorecard"


@dataclass
class ScoreItem:
    item: str
    points: int
    status: str
    current_status: str
    evidence: str
    missing_for_final: str
    next_action: str


def exists_text(path: str) -> str:
    return "yes" if (ROOT / path).exists() else "missing"


def read_json(path: str) -> dict[str, Any]:
    full = ROOT / path
    if not full.exists():
        return {}
    return json.loads(full.read_text(encoding="utf-8"))


def read_csv(path: str) -> pd.DataFrame:
    full = ROOT / path
    if not full.exists():
        return pd.DataFrame()
    return pd.read_csv(full, encoding="utf-8-sig")


def count_literature_rows() -> int:
    path = ROOT / "docs" / "literature_matrix.md"
    if not path.exists():
        return 0
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("| L"):
            count += 1
    return count


def metric_value(payload: dict[str, Any], keys: list[str], default: Any = "") -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def collect_metrics() -> dict[str, Any]:
    baseline_recon = read_csv("outputs/baseline/reconstruction_metrics.csv")
    robustness_best = read_csv("outputs/reconstruction_robustness/reconstruction_robustness_best.csv")
    cst_recon_demo = read_json("outputs/cst_reconstruction_demo/cst_reconstruction_metrics.json")
    cst_recognition_demo = read_json("outputs/cst_recognition_demo/cst_recognition_metrics.json")
    cst_recognition_level2 = read_json("outputs/cst_recognition_level2/cst_recognition_metrics.json")
    ablation = read_csv("outputs/cst_recognition_ablation/recognition_ablation_metrics.csv")
    level2_ablation = read_csv("outputs/cst_recognition_level2_ablation/recognition_ablation_metrics.csv")
    level2_summary = read_json("outputs/cst_level2_plan/level2_manifest_summary.json")
    level1_summary = read_json("outputs/cst_level1_plan/level1_manifest_summary.json")
    level1_merge_summary = read_json("outputs/cst_level1_merge_report/level1_merge_summary.json")
    level1_batch_summary = read_json("outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_summary.json")
    level1_angular_summary = read_json("outputs/cst_level1_angular_calibration/angular_calibration_summary.json")
    level1_angular_results = read_csv("outputs/cst_level1_angular_calibration/angular_calibration_batch_results.csv")
    structure_summary = read_json("outputs/cst_structure_comparison/structure_comparison_summary.json")
    compound_summary = read_json("data/recognition_stress_tests/level2_compound_stress/recognition_compound_stress_summary.json")
    compound_core = compound_summary.get("summary", {})
    compound_core = compound_core if isinstance(compound_core, dict) else {}
    compound_best = compound_core.get("best_overall_strategy", {})
    compound_best = compound_best if isinstance(compound_best, dict) else {}
    compound_worst = compound_core.get("worst_row", {})
    compound_worst = compound_worst if isinstance(compound_worst, dict) else {}
    level1_workpack_summary = read_json("outputs/cst_level1_workpack/level1_workpack_summary.json")
    level2_workpack_summary = read_json("outputs/cst_level2_workpack/level2_workpack_summary.json")
    cst_dashboard_summary = read_json("outputs/cst_execution_dashboard/cst_execution_dashboard_summary.json")
    analytic_level1_summary = read_json("outputs/level1_analytic_reference/level1_analytic_reference_summary.json")
    synthetic_level1_results = read_csv("outputs/synthetic_cst_level1_dataset/reconstruction_batch/level1_batch_reconstruction_results.csv")
    level1_real_results = read_csv("outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv")
    merge_summary = read_json("outputs/cst_level2_merge_report/level2_merge_summary.json")

    metrics: dict[str, Any] = {
        "literature_rows": count_literature_rows(),
        "baseline_reconstruction_rows": int(len(baseline_recon)),
        "robustness_rows": int(len(robustness_best)),
        "level1_planned_cases": level1_summary.get("case_count", 0),
        "level1_required_cases": len(level1_summary.get("required_cases", [])),
        "level1_complete_cases": level1_merge_summary.get("complete_cases", 0),
        "level1_complete_required_cases": level1_merge_summary.get("required_complete_cases", 0),
        "level1_required_complete": level1_merge_summary.get("required_complete", False),
        "level1_batch_queued_cases": level1_batch_summary.get("queued_cases", 0),
        "level1_batch_completed_runs": level1_batch_summary.get("completed_runs", 0),
        "level1_angular_case_count": level1_angular_summary.get("case_count", 0),
        "level1_angular_max_nmse": level1_angular_summary.get("max_nmse", ""),
        "level1_angular_min_correlation": level1_angular_summary.get("min_correlation", ""),
        "level1_angular_max_main_lobe_error": level1_angular_summary.get("max_main_lobe_error_deg", ""),
        "structure_sample_count": structure_summary.get("sample_count", 0),
        "structure_sample_frequency_count": structure_summary.get("sample_frequency_count", 0),
        "structure_mean_shadow_db": structure_summary.get("mean_shadow_db", 0.0),
        "structure_p95_shadow_db": structure_summary.get("p95_shadow_db", 0.0),
        "structure_max_shadow_db": structure_summary.get("max_shadow_db", 0.0),
        "structure_mean_pattern_correlation": structure_summary.get("mean_pattern_correlation", 0.0),
        "structure_cross_domain_accuracy": structure_summary.get("cross_domain_accuracy", ""),
        "structure_best_cross_domain_model": structure_summary.get("best_cross_domain_model", ""),
        "structure_is_full_wave_airframe": structure_summary.get("is_full_wave_cst_airframe", False),
        "compound_stress_rows": compound_core.get("row_count", 0),
        "compound_all_rows_pass_085": compound_core.get("all_rows_pass_085", ""),
        "compound_worst_accuracy": compound_worst.get("best_accuracy", ""),
        "compound_worst_candidate": compound_worst.get("candidate", ""),
        "compound_worst_strategy": compound_worst.get("strategy", ""),
        "compound_worst_case": compound_worst.get("stress_case", ""),
        "compound_best_strategy": compound_best.get("strategy", ""),
        "compound_best_mean_accuracy": compound_best.get("mean_accuracy", ""),
        "compound_best_min_accuracy": compound_best.get("min_accuracy", ""),
        "compound_best_delta_vs_zero_fill": compound_best.get("mean_delta_vs_zero_fill", ""),
        "level1_workpack_cases": level1_workpack_summary.get("case_count", 0),
        "level1_workpack_sensor_count": level1_workpack_summary.get("sensor_count", 0),
        "level1_measurement_surface": level1_workpack_summary.get("selected_measurement_surface", "2pi_upper_hemisphere"),
        "level2_planned_samples": level2_summary.get("sample_count", 0),
        "level2_sample_frequency_rows": level2_summary.get("sample_frequency_rows", 0),
        "level2_workpack_samples": level2_workpack_summary.get("sample_count", 0),
        "level2_workpack_frequency_tasks": level2_workpack_summary.get("sample_frequency_tasks", 0),
        "cst_dashboard_level1_required_actions": cst_dashboard_summary.get("level1_required_actions", 0),
        "cst_dashboard_level2_pilot_actions": cst_dashboard_summary.get("level2_pilot_actions", 0),
        "cst_dashboard_missing_required_now_files": cst_dashboard_summary.get("missing_required_now_files", 0),
        "cst_dashboard_missing_level2_pilot_files": cst_dashboard_summary.get("missing_level2_pilot_files", 0),
        "level1_analytic_case_count": analytic_level1_summary.get("case_count", 0),
        "level1_analytic_required_case_count": analytic_level1_summary.get("required_case_count", 0),
        "level1_analytic_rows_per_case": analytic_level1_summary.get("rows_per_case", 0),
        "level1_analytic_real_cst_compared_cases": analytic_level1_summary.get("real_cst_compared_cases", 0),
        "level2_complete_samples": merge_summary.get("complete_samples", 0),
        "level2_all_complete": merge_summary.get("all_complete", False),
        "cst_demo_nmse": metric_value(cst_recon_demo, ["metrics", "nmse"], cst_recon_demo.get("nmse", "")),
        "cst_demo_correlation": metric_value(
            cst_recon_demo,
            ["metrics", "correlation"],
            cst_recon_demo.get("correlation", ""),
        ),
        "cst_recognition_demo_accuracy": metric_value(
            cst_recognition_demo,
            ["recognition", "best_accuracy"],
            "",
        ),
        "level2_recognition_accuracy": metric_value(
            cst_recognition_level2,
            ["recognition", "best_accuracy"],
            "",
        ),
        "level2_recognition_samples": metric_value(
            cst_recognition_level2,
            ["feature_metadata", "sample_count"],
            0,
        ),
        "level2_recognition_features": metric_value(
            cst_recognition_level2,
            ["feature_metadata", "feature_count"],
            0,
        ),
    }

    if not baseline_recon.empty and "experiment" in baseline_recon.columns:
        opt50 = baseline_recon[baseline_recon["experiment"] == "optimized_50"]
        if not opt50.empty:
            row = opt50.iloc[0]
            metrics.update(
                {
                    "baseline_opt50_nmse": float(row.get("nmse", 0.0)),
                    "baseline_opt50_correlation": float(row.get("correlation", 0.0)),
                    "baseline_opt50_sensors": int(row.get("sensor_points", 0)),
                }
            )

    if not robustness_best.empty:
        robust_30 = robustness_best[pd.to_numeric(robustness_best["snr_db"], errors="coerce").eq(30.0)]
        opt75 = robust_30[robust_30["case"] == "optimized_75"]
        opt50 = robust_30[robust_30["case"] == "optimized_50"]
        if not opt75.empty:
            row = opt75.iloc[0]
            metrics.update(
                {
                    "robust_30db_opt75_nmse": float(row["nmse_mean"]),
                    "robust_30db_opt75_correlation": float(row["correlation_mean"]),
                    "robust_30db_opt75_main_lobe_error": float(row["main_lobe_error_deg_mean"]),
                }
            )
        if not opt50.empty:
            row = opt50.iloc[0]
            metrics.update(
                {
                    "robust_30db_opt50_nmse": float(row["nmse_mean"]),
                    "robust_30db_opt50_correlation": float(row["correlation_mean"]),
                    "robust_30db_opt50_main_lobe_error": float(row["main_lobe_error_deg_mean"]),
                }
            )

    if not ablation.empty and "best_accuracy" in ablation.columns:
        metrics["recognition_ablation_min_accuracy"] = float(pd.to_numeric(ablation["best_accuracy"], errors="coerce").min())
        metrics["recognition_ablation_cases"] = int(len(ablation))

    if not level2_ablation.empty and "best_accuracy" in level2_ablation.columns:
        metrics["level2_ablation_min_accuracy"] = float(pd.to_numeric(level2_ablation["best_accuracy"], errors="coerce").min())
        metrics["level2_ablation_cases"] = int(len(level2_ablation))

    if not synthetic_level1_results.empty:
        ok = synthetic_level1_results[synthetic_level1_results["status"].astype(str).eq("ok")].copy()
        if not ok.empty:
            metrics["synthetic_level1_completed_runs"] = int(len(ok))
            metrics["synthetic_level1_max_nmse"] = float(pd.to_numeric(ok["nmse"], errors="coerce").max())
            metrics["synthetic_level1_min_correlation"] = float(pd.to_numeric(ok["correlation"], errors="coerce").min())
            metrics["synthetic_level1_max_main_lobe_error"] = float(pd.to_numeric(ok["main_lobe_error_deg"], errors="coerce").max())

    if not level1_real_results.empty:
        ok = level1_real_results[level1_real_results["status"].astype(str).eq("ok")].copy()
        if not ok.empty:
            metrics["level1_real_reconstruction_runs"] = int(len(ok))
            metrics["level1_real_max_nmse"] = float(pd.to_numeric(ok["nmse"], errors="coerce").max())
            metrics["level1_real_min_correlation"] = float(pd.to_numeric(ok["correlation"], errors="coerce").min())
            metrics["level1_real_max_main_lobe_error"] = float(pd.to_numeric(ok["main_lobe_error_deg"], errors="coerce").max())

    if not level1_angular_results.empty:
        metrics["level1_angular_completed_runs"] = int(len(level1_angular_results))
        metrics["level1_angular_max_nmse"] = float(pd.to_numeric(level1_angular_results["nmse"], errors="coerce").max())
        metrics["level1_angular_min_correlation"] = float(pd.to_numeric(level1_angular_results["correlation"], errors="coerce").min())
        metrics["level1_angular_max_main_lobe_error"] = float(
            pd.to_numeric(level1_angular_results["main_lobe_error_deg"], errors="coerce").max()
        )

    return metrics


def build_score_items(metrics: dict[str, Any]) -> list[ScoreItem]:
    return [
        ScoreItem(
            item="国内外发展调研分析",
            points=10,
            status="Draft evidence",
            current_status=f"已形成文献筛查和矩阵，当前矩阵约 {metrics['literature_rows']} 条。",
            evidence="docs/literature_screening_and_strategy.md; docs/literature_matrix.md; docs/literature_to_algorithm_traceability.md",
            missing_for_final="补充最终引用格式，把文献到算法迁移证据链转成报告正文。",
            next_action="把文献矩阵转为报告第 2 章正式文本和参考文献表。",
        ),
        ScoreItem(
            item="研究思路合理性",
            points=10,
            status="CST evidence ready; write-up pending",
            current_status=(
                "已形成标准源 -> 多源 -> 简化载体 -> 扰动鲁棒性的递进路线；"
                f"Level 1 required_complete={metrics.get('level1_required_complete')}，"
                f"Level 2 all_complete={metrics.get('level2_all_complete')}，"
                f"简化结构对照样本={metrics.get('structure_sample_count', 0)}。"
            ),
            evidence="docs/phase_01_cst_technical_route_and_division.md; docs/solution_report_draft.md; docs/literature_to_algorithm_traceability.md",
            missing_for_final="补充 CST solver-safe、element-library 叠加、简化结构遮挡对照和调参过程说明。",
            next_action="把 Level 1/2/结构对照当前结果写入报告第 3/5/7/9 章，并明确 full-wave 结构对照仍是可选增强项。",
        ),
        ScoreItem(
            item="技术路线可行性",
            points=10,
            status="CST evidence ready; model risk bounded",
            current_status=(
                "CST 模板、校验、重建、识别、合并、鲁棒性扫描脚本均已具备；"
                f"Level 1 真实 required 重建 {metrics.get('level1_real_reconstruction_runs', 0)} 个案例，"
                f"角域校准 {metrics.get('level1_angular_case_count', 0)} 个案例，"
                f"Level 2 完整样本 {metrics.get('level2_complete_samples', 0)}/{metrics.get('level2_planned_samples', 0)}，"
                f"结构遮挡对照 cross-domain accuracy={metrics.get('structure_cross_domain_accuracy', '')}。"
            ),
            evidence="src/*.py; outputs/cst_templates; outputs/cst_level1_merge_report; outputs/cst_level1_reconstruction_batch; outputs/cst_level1_angular_calibration; outputs/cst_level2_merge_report; outputs/cst_recognition_level2; outputs/cst_structure_comparison",
            missing_for_final="角域校准已证明 solver-safe FarfieldPlot-derived 数据自洽；简化结构遮挡对照已给出安装效应敏感性，但 full-wave 近场等效源反演和 full-wave airframe 结构散射仍需边界说明。",
            next_action="把 Level 1 双通道证据和 Level 2 简化结构遮挡对照写入报告，明确哪些是已验证证据、哪些是后续 full-wave 增强。",
        ),
        ScoreItem(
            item="测试方案完整性",
            points=10,
            status="CST evidence ready; screenshots pending",
            current_status=(
                f"已具备 Level 1/2 规程、Level 1 manifest {metrics.get('level1_planned_cases', 0)} 个案例、"
                f"半球面 Level 1 任务包 {metrics.get('level1_workpack_cases', 0)} 个案例、"
                f"Level 1 解析方向图 sanity reference {metrics.get('level1_analytic_case_count', 0)} 个案例、"
                f"Level 2 任务包 {metrics.get('level2_workpack_samples', 0)} 个样本、"
                f"CST dashboard required action {metrics.get('cst_dashboard_level1_required_actions', 0)} 个、"
                f"Level 2 strict all_complete={metrics.get('level2_all_complete')}。"
            ),
            evidence="docs/cst_level1_standard_source_protocol.md; outputs/cst_level1_plan; docs/phase_03_cst_level2_multisource_recognition_protocol.md; outputs/cst_level2_plan",
            missing_for_final="最终报告需要补充 CST 参数截图、简化结构对照图和最终测试日志。",
            next_action="把 batch summary、strict merge、识别结果和结构对照图纳入报告/PPT 素材包。",
        ),
        ScoreItem(
            item="2π 传感布局与 12m x 10m x 8m 包络",
            points=10,
            status="Ready",
            current_status="13 m 半球面 162 测点方案已生成，并已用于 Level 1/2 CST-derived 导出合同。",
            evidence="outputs/cst_templates/sensor_layout_hemisphere_for_cst.csv; outputs/baseline/sensor_layout_hemisphere.png; data/cst_exports/level2/all_nearfield.csv",
            missing_for_final="最终报告/PPT 需补充半球面布局图和 CST 参数截图。",
            next_action="把半球面布局图、行数审计和测点删减结果写入材料。",
        ),
        ScoreItem(
            item="三维场重建高精度与少测点",
            points=30,
            status="CST angular calibration ready; near-field model risk",
            current_status=(
                f"真实 Level 1 required 重建已完成 {metrics.get('level1_real_reconstruction_runs', 0)} 个案例；"
                f"等效源近场反演最大 NMSE={metrics.get('level1_real_max_nmse', 0.0):.3e}、"
                f"最小相关系数={metrics.get('level1_real_min_correlation', 0.0):.5f}；"
                f"FarfieldPlot-derived 角域校准最大 NMSE={metrics.get('level1_angular_max_nmse', 0.0):.3e}、"
                f"最小相关系数={metrics.get('level1_angular_min_correlation', 0.0):.5f}、"
                f"最大主瓣误差={metrics.get('level1_angular_max_main_lobe_error', 0.0):.2f} deg。"
            ),
            evidence="outputs/cst_level1_reconstruction_batch/level1_batch_reconstruction_results.csv; outputs/cst_reconstruction/L1_short_dipole_z_1p2G; outputs/cst_reconstruction/L1_halfwave_dipole_z_1p2G; outputs/cst_level1_angular_calibration",
            missing_for_final="solver-safe nearfield 是 FarfieldPlot-derived 角域样本，不是 full-wave 近场 monitor；正式报告必须区分角域高一致性和近场等效源模型风险。",
            next_action="在报告第 5/8/9 章写清数据来源、角域校准结果和近场等效源反演的适用边界。",
        ),
        ScoreItem(
            item="空间-频谱特征辨识准确率 >= 85%",
            points=20,
            status="Ready with compound-stress mitigation caveat",
            current_status=(
                f"Level 2 48 样本 CST-derived 数据已完成；识别样本 {metrics.get('level2_recognition_samples', 0)} 个、"
                f"特征 {metrics.get('level2_recognition_features', 0)} 维，accuracy={metrics.get('level2_recognition_accuracy', '')}，"
                f"消融最低 accuracy={metrics.get('level2_ablation_min_accuracy', '')}；"
                f"简化结构 cross-domain accuracy={metrics.get('structure_cross_domain_accuracy', '')}，"
                f"平均遮挡={metrics.get('structure_mean_shadow_db', 0.0):.2f} dB；"
                f"复合仪器误差+结构缺测 {metrics.get('compound_stress_rows', 0)} 行，"
                f"原始最差 accuracy={metrics.get('compound_worst_accuracy', '')}，"
                f"最佳缓解策略={metrics.get('compound_best_strategy', '')}，"
                f"min accuracy={metrics.get('compound_best_min_accuracy', '')}。"
            ),
            evidence="outputs/cst_level2_merge_report/level2_merge_summary.json; outputs/cst_recognition_level2; outputs/cst_recognition_level2_ablation; outputs/cst_structure_comparison; data/recognition_stress_tests/level2_compound_stress",
            missing_for_final="当前证据为 element-library 线性叠加 + 简化结构遮挡迁移 + 仿真复合仪器/缺测压力测试；尚不是复杂载体 full-wave airframe 结构散射解或真实仪器校准结论。",
            next_action="将混淆矩阵、消融曲线、简化结构对照和复合误差插补缓解结论写入报告；full-wave airframe 与真实仪器校准作为后续增强项。",
        ),
    ]


def status_label(item: ScoreItem) -> str:
    return item.status


def write_markdown(items: list[ScoreItem], metrics: dict[str, Any], out_dir: Path) -> None:
    score_rows = []
    for item in items:
        score_rows.append(
            f"| {item.item} | {item.points} | {status_label(item)} | {item.current_status} | {item.missing_for_final} |"
        )

    metric_rows = [
        ("文献矩阵条目", metrics.get("literature_rows", "")),
        ("Level 1 计划案例", metrics.get("level1_planned_cases", "")),
        ("Level 1 必做案例", metrics.get("level1_required_cases", "")),
        ("Level 1 完整案例", metrics.get("level1_complete_cases", "")),
        ("Level 1 完整必做案例", metrics.get("level1_complete_required_cases", "")),
        ("Level 1 批量重建完成数", metrics.get("level1_batch_completed_runs", "")),
        ("Level 1 角域校准案例数", metrics.get("level1_angular_case_count", "")),
        ("Level 1 角域校准最大 NMSE", metrics.get("level1_angular_max_nmse", "")),
        ("Level 1 角域校准最小相关系数", metrics.get("level1_angular_min_correlation", "")),
        ("Level 1 半球面任务包案例数", metrics.get("level1_workpack_cases", "")),
        ("Level 1 半球面测点数", metrics.get("level1_workpack_sensor_count", "")),
        ("Level 1 同形合成重建完成数", metrics.get("synthetic_level1_completed_runs", "")),
        ("Level 1 同形合成最大 NMSE", metrics.get("synthetic_level1_max_nmse", "")),
        ("Level 1 同形合成最小相关系数", metrics.get("synthetic_level1_min_correlation", "")),
        ("Level 2 计划样本", metrics.get("level2_planned_samples", "")),
        ("Level 2 半球面任务包样本", metrics.get("level2_workpack_samples", "")),
        ("Level 2 半球面频点任务", metrics.get("level2_workpack_frequency_tasks", "")),
        ("CST dashboard Level 1 required action", metrics.get("cst_dashboard_level1_required_actions", "")),
        ("CST dashboard Level 2 pilot action", metrics.get("cst_dashboard_level2_pilot_actions", "")),
        ("CST dashboard required-now missing files", metrics.get("cst_dashboard_missing_required_now_files", "")),
        ("Level 1 解析参考案例数", metrics.get("level1_analytic_case_count", "")),
        ("Level 1 解析参考每案例行数", metrics.get("level1_analytic_rows_per_case", "")),
        ("Level 1 解析参考已比对真实 CST 案例数", metrics.get("level1_analytic_real_cst_compared_cases", "")),
        ("Level 2 完整样本", metrics.get("level2_complete_samples", "")),
        ("Level 2 strict all_complete", metrics.get("level2_all_complete", "")),
        ("Level 2 识别样本", metrics.get("level2_recognition_samples", "")),
        ("Level 2 识别特征数", metrics.get("level2_recognition_features", "")),
        ("Level 2 识别 accuracy", metrics.get("level2_recognition_accuracy", "")),
        ("Level 2 消融最低 accuracy", metrics.get("level2_ablation_min_accuracy", "")),
        ("Level 2 结构对照样本", metrics.get("structure_sample_count", "")),
        ("Level 2 结构对照样本-频点", metrics.get("structure_sample_frequency_count", "")),
        ("Level 2 结构平均遮挡 dB", metrics.get("structure_mean_shadow_db", "")),
        ("Level 2 结构 P95 遮挡 dB", metrics.get("structure_p95_shadow_db", "")),
        ("Level 2 结构最大遮挡 dB", metrics.get("structure_max_shadow_db", "")),
        ("Level 2 结构方向图平均相关系数", metrics.get("structure_mean_pattern_correlation", "")),
        ("Level 2 结构 cross-domain accuracy", metrics.get("structure_cross_domain_accuracy", "")),
        ("Level 2 结构 cross-domain model", metrics.get("structure_best_cross_domain_model", "")),
        ("Level 2 结构对照是否 full-wave airframe", metrics.get("structure_is_full_wave_airframe", "")),
        ("Level 2 复合压力测试行数", metrics.get("compound_stress_rows", "")),
        ("Level 2 复合压力测试全行通过 0.85", metrics.get("compound_all_rows_pass_085", "")),
        ("Level 2 复合压力测试原始最差 accuracy", metrics.get("compound_worst_accuracy", "")),
        ("Level 2 复合压力测试原始最差策略", metrics.get("compound_worst_strategy", "")),
        ("Level 2 复合压力测试原始最差场景", metrics.get("compound_worst_case", "")),
        ("Level 2 复合压力测试最佳缓解策略", metrics.get("compound_best_strategy", "")),
        ("Level 2 复合压力测试最佳策略最小 accuracy", metrics.get("compound_best_min_accuracy", "")),
        ("Level 2 复合压力测试最佳策略平均提升", metrics.get("compound_best_delta_vs_zero_fill", "")),
        ("Level 1 真实重建完成数", metrics.get("level1_real_reconstruction_runs", "")),
        ("Level 1 真实重建最大 NMSE", metrics.get("level1_real_max_nmse", "")),
        ("Level 1 真实重建最小相关系数", metrics.get("level1_real_min_correlation", "")),
        ("Level 1 真实重建最大主瓣误差", metrics.get("level1_real_max_main_lobe_error", "")),
        ("合成 CST 重建 demo NMSE", metrics.get("cst_demo_nmse", "")),
        ("合成 CST 重建 demo 相关系数", metrics.get("cst_demo_correlation", "")),
        ("30 dB optimized_75 NMSE", metrics.get("robust_30db_opt75_nmse", "")),
        ("30 dB optimized_75 相关系数", metrics.get("robust_30db_opt75_correlation", "")),
        ("CST 格式识别 demo accuracy", metrics.get("cst_recognition_demo_accuracy", "")),
        ("识别删减 demo 最低 accuracy", metrics.get("recognition_ablation_min_accuracy", "")),
    ]
    metric_table = "\n".join(f"| {name} | {value} |" for name, value in metric_rows)

    content = f"""# CS-202614 scorecard

Generated from the current workspace. This scorecard is intentionally conservative: synthetic/demo outputs are treated as pipeline evidence, and CST-derived element-library outputs are separated from full-wave airframe evidence.

## Overall Status

- Goal status: in progress.
- Strongest current assets: literature matrix, CST data schema, Level 1 required CST exports/reconstruction, Level 2 48-sample CST-derived exports/recognition, simplified structure comparison, compound instrument/dropout stress test, manifests, merge audits, and robustness scans.
- Critical gap: Level 1 equivalent-source reconstruction quality is weak, simplified structure/occlusion evidence is ready but not full-wave airframe scattering, and severe compound recognition stress needs the median-imputation mitigation caveat in report/PPT wording.
- Submission gap: exported report/PPT/video/archive files exist, but they need review or regeneration after the latest G5 compound-stress wording update; administrative metadata and human playback review remain outside the code pipeline.

## Score Items

| Item | Points | Status | Current evidence | Missing for final | 
|---|---:|---|---|---|
{chr(10).join(score_rows)}

## Key Metrics

| Metric | Value |
|---|---:|
{metric_table}

## Next Actions

1. Improve or explain the weak Level 1 solver-safe reconstruction metrics.
2. Write the simplified airframe/occlusion comparison into the report and keep full-wave airframe scattering as an optional enhancement.
3. Add the compound instrument/dropout stress boundary: raw zero-fill/mask can fall below 0.85, while frequency/sensor median imputation is the current mitigation candidate.
4. Replace demo values in `docs/solution_report_draft.md` with the current Level 1/2 CST-derived evidence.
5. Review or regenerate final report, PPT, video script, and code/package checklist with the compound-stress wording included.
6. Rebuild completion audit and submission package after refreshed artifacts are accepted.
"""
    (out_dir / "scorecard.md").write_text(content, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    metrics = collect_metrics()
    items = build_score_items(metrics)

    score_df = pd.DataFrame([asdict(item) for item in items])
    score_df.to_csv(OUT / "score_items.csv", index=False, encoding="utf-8-sig")
    (OUT / "scorecard_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(items, metrics, OUT)

    print(f"Scorecard written to {OUT}")
    print(score_df[["item", "points", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
