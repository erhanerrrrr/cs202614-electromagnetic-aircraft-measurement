# S32 G3 mesh-safe Huygens two-case batch gate

## 做了什么

- 为第二个 Level 1 mesh-safe Huygens 源例 `L1_halfwave_dipole_z_1p2G` 运行短路径 CST solver gate。
- 通过 `ResultTree` 导出半波偶极子局部 Huygens 面复数 E-field CSV，目标契约完整：`96 * 3 = 288` 行。
- 将 `run_cst_meshsafe_huygens_extrapolation.py` 扩展为批处理入口，可自动遍历 `data/cst_meshsafe_huygens_workpack/level1_required_meshsafe_huygens_cases.csv` 中已有真实 CST 局部场导出。
- 生成两例批处理诊断目录 `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/`，把短偶极子和半波偶极子的外推结果放到同一张 pass/fail 表中。

## 为什么这样做

S31 已经证明短偶极子可以完成“CST 求解结果 -> ResultTree probe 曲线 -> 局部场 CSV -> Python 外推诊断”的真实数据闭环。但单个源例只能证明链路可用，不能证明它对不同方向图形态稳定。

本阶段用半波偶极子重复同一条链路。半波偶极子的方向图主瓣判据更清晰，能够补上短偶极子宽环状主瓣导致的 `shape_pass_lobe_ambiguous` 边界，从而把当前 G3 证据从“一例链路成功”推进到“两例批量门控可复现”。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `data/cst_exports/level1_meshsafe_huygens/L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` | 半波偶极子真实 CST 局部 Huygens 面 Ex/Ey/Ez 复数场，288 行 | Python Huygens 外推输入 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_halfwave/` | 半波偶极子单例外推诊断、场质量、最佳 far-field 对比和 README | 查看单例物理代理结果 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/` | 两个 Level 1 mesh-safe Huygens 源例的批处理汇总和子目录 | 查看跨源例 pass/fail 门控 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 新增 `--batch`、`--case-csv`、`--batch-out-dir`、`--sample-ids` 参数 | `python code\run_cst_meshsafe_huygens_extrapolation.py --batch` |
| `outputs/cst_solver_trials/meshsafe_huygens_halfwave_shortpath/` | 半波偶极子本机 CST solver gate 摘要和 stdout 缓存 | 本机审计证据，默认不纳入 Git |
| `outputs/cst_meshsafe_huygens_result_export_halfwave/` | 半波偶极子 ResultTree 导出审计缓存 | 本机审计证据，默认不纳入 Git |

## 验证方式

```powershell
python code\run_cst_solver_project.py --project C:\csttmp\huy_p\projects\CST_L1_halfwave_dipole_z_1p2G_meshsafe_huygens_r0p35.cst --out-dir C:\csttmp\huy_h --trial-name h_half.cst --summary-out outputs\cst_solver_trials\meshsafe_huygens_halfwave_shortpath\h_half_solver_summary.json --stdout-log outputs\cst_solver_trials\meshsafe_huygens_halfwave_shortpath\h_half_stdout.log --timeout-seconds 900 --poll-seconds 20
python code\export_cst_meshsafe_huygens_results.py --project C:\csttmp\huy_h\h_half.cst --sample-id L1_halfwave_dipole_z_1p2G --out-dir outputs\cst_meshsafe_huygens_result_export_halfwave --attempt-export --overwrite
python code\run_cst_meshsafe_huygens_extrapolation.py --local-nearfield data\cst_exports\level1_meshsafe_huygens\L1_halfwave_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv --sample-id L1_halfwave_dipole_z_1p2G --out-dir data\sampling_layouts\cst_meshsafe_huygens_extrapolation_halfwave
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py code\export_cst_meshsafe_huygens_results.py code\run_cst_solver_project.py
```

当前验证结果：

- 半波偶极子 solver gate 为 clean finish：`status = finished`，`mesh_limit_detected = false`，`path_length_limit_detected = false`，未出现 `aborted_keeping_results_detected`。
- CST solver 日志显示 steady-state energy criterion met，solver finished successfully。
- 半波偶极子 ResultTree 导出为 `target_contract_complete`，目标 CSV `target_rows = 288`，`value_read = 288`，目标频率 `1.2 GHz` 精确命中。
- 半波偶极子最佳诊断分支为 `electric_only_outgoing`，状态 `physics_proxy_pass`，全方向功率形状相关性约 `0.9868`，尺度拟合功率 NMSE 约 `1.41e-2`，主瓣误差 `0.00 deg`。
- 两例批处理完成 `2/2`，缺失或失败 `0`；其中 `L1_halfwave_dipole_z_1p2G` 通过 `physics_proxy_pass`，`L1_short_dipole_z_1p2G` 保持 `shape_pass_lobe_ambiguous`。

## 当前解释

CST 不是无法正常运行。本阶段比 S30/S31 更进一步：第二个 mesh-safe 源例已经 clean finish，并且真实 CST probe 曲线也成功导入 Python 批处理链路。

当前没有把大体积 `.cst/.m3d/.ffm/.fme` 求解缓存纳入 Git。仓库只保留可复验的小体积 CSV、诊断摘要和脚本；本机 CST 缓存在 `C:\csttmp\huy_h`、`outputs/cst_solver_trials/meshsafe_huygens_halfwave_shortpath/` 和 `outputs/cst_meshsafe_huygens_result_export_halfwave/` 中。

## 当前不足

- 批处理门控仍是 data-chain/physics-proxy 证据，不是最终严格 Stratton-Chu/Huygens 证明。
- 现有外推仍以 E-field 诊断代理为主，缺 H-field 或经校准的等效阻抗来支撑面电流/面磁流的严格约定。
- 短偶极子仍因宽环状方向图出现主瓣点 ambiguity，需要用积分窗、环状主瓣评价或更强物理算子替代单点 `argmax`。

## 下一步

1. 把批处理门控接入 G3 dashboard，让后续 CST 导出可以自动显示缺失、失败、proxy pass 和 strict pass。
2. 升级 Huygens 外推算子：优先补 H-field probe、阻抗拟合或 Stratton-Chu 面积分版本。
3. 将局部 Huygens 外推结果与 reduced-layout 半球采样候选相连，重新评估 32/120/162 点布局在真实 CST 局部场链路下的误差门限。
