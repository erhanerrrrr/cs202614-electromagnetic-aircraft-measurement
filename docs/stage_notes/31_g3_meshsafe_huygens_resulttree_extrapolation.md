# S31 G3 mesh-safe Huygens ResultTree export and extrapolation

## 做了什么

- 新增 `code/export_cst_meshsafe_huygens_results.py`，把短路径 CST 工程 `C:\csttmp\huy_s\h_short.cst` 中已保留的 probe 结果通过 CST `ResultTree` 读取出来。
- 避开了 CST `Field Monitors` 视图的 ASCII export 弹窗问题，改为读取 `1D Results\Probes\E-Field\...\(X/Y/Z)` 复数曲线。
- 生成真实局部 Huygens 面场 CSV：`data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv`，共 `96 * 3 = 288` 行。
- 新增 `code/run_cst_meshsafe_huygens_extrapolation.py`，用这份真实 CST 局部场做等效面流/Kirchhoff 代理外推，并与现有 Level 1 CST far-field reference 对比。
- 刷新 `data/cst_meshsafe_huygens_workpack/`，把 ResultTree 导出命令加入 `next_meshsafe_huygens_commands.csv`。

## 为什么这样做

S29 证明旧的 13 m Cartesian probe 方案会触发约 `4.6` billion cells 和 `3` 个 MPI cluster nodes 的资源瓶颈；S30 证明 mesh-safe 局部 Huygens 工程可以在本机进入 HF Time Domain solver，并保留 `.m3d/.ffm/.fme` 结果。

本阶段解决的是下一层问题：不是继续手动点 CST 的 Field Monitor ASCII export，而是用 CST Python API 从 solved `ResultTree` probe 曲线中抽取频域复数场。这样工程链路第一次拥有了真实 CST 局部面场 CSV，可以进入 Python 侧外推诊断。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/export_cst_meshsafe_huygens_results.py` | 审计/导出短路径 mesh-safe Huygens CST 结果 | `python code\export_cst_meshsafe_huygens_results.py --attempt-export` |
| `data/cst_exports/level1_meshsafe_huygens/L1_short_dipole_z_1p2G_level1_local_sphere_r0p35_local_efield.csv` | 真实 CST 局部 Huygens 面 Ex/Ey/Ez 复数场，288 行 | Python Huygens 外推输入 |
| `outputs/cst_meshsafe_huygens_result_export/meshsafe_huygens_export_summary.json` | ResultTree 导出摘要，记录 `target_contract_complete` | 本机审计证据 |
| `outputs/cst_meshsafe_huygens_result_export/meshsafe_huygens_probe_item_map.csv` | 每个 sensor/component 对应的 CST result-tree item 和取值频点 | 调试 CST 导出映射 |
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 真实局部场到 far-field reference 的诊断外推门 | `python code\run_cst_meshsafe_huygens_extrapolation.py` |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation/` | 外推诊断结果、场质量、最佳 far-field 对比表和 README | G3 后续算法证据入口 |

## 验证方式

```powershell
python -m py_compile code\export_cst_meshsafe_huygens_results.py code\prepare_cst_meshsafe_huygens_workpack.py code\run_cst_meshsafe_huygens_extrapolation.py
python code\prepare_cst_meshsafe_huygens_workpack.py
python code\export_cst_meshsafe_huygens_results.py --attempt-export --overwrite
python code\run_cst_meshsafe_huygens_extrapolation.py
```

当前验证结果：

- `export_cst_meshsafe_huygens_results.py --attempt-export --overwrite` 返回 `target_contract_complete`。
- 目标 CSV 存在，行数 `288`，列合同完整。
- CST probe 曲线频率轴共有 `1001` 点，目标频率 `1.2 GHz` 精确命中，频点索引 `500`。
- `meshsafe_huygens_probe_item_map.csv` 中 `value_read = 288`，无缺失分量。
- 外推诊断最佳分支为 `outgoing_equivalence_minus`，状态 `shape_pass_lobe_ambiguous`，全方向功率形状相关性约 `0.9989`，尺度拟合功率 NMSE 约 `6.96e-04`。

## 当前解释

CST 不是无法正常运行。当前问题已经从“CST 能否打开/求解”推进为“如何把 solver 保留的结果稳定导出并接入严格 Huygens 算子”。

之前弹窗的根因是尝试从 `Field Monitors` 视图直接做 ASCII export，而这个视图不支持当前 monitor 的 ASCII 导出；本阶段改用 `ResultTree.GetResultFromTreeItem(...).GetYRe/GetYIm` 读取 solved probe 频域曲线，因此绕过了该问题。

`shape_pass_lobe_ambiguous` 的含义是：短偶极子 far-field 有宽环状高功率区域，单个 `argmax` 主瓣点可能跳到对称/近简并方向，所以主瓣角误差不适合作为唯一判据；但全方向形状相关性和尺度拟合 NMSE 已经说明局部场数据链路方向是对的。

## 当前不足

- 这还不是最终 Stratton-Chu/Huygens 严格证明；当前外推使用 `J ~= -E_t/eta0` 和 `M = -n x E_t` 的诊断代理。
- 还缺第二个 Level 1 case 的同样导出和外推验证。
- 还缺 H-field 或更严格的表面积分算子来把局部面场变成 report-level 物理证据。

## 下一步

1. 为第二个 Level 1 mesh-safe Huygens case 运行短路径 solver 和 ResultTree 导出。
2. 将 `run_cst_meshsafe_huygens_extrapolation.py` 升级为更严格的矢量面等效积分算子，优先补 H-field/阻抗估计和法向一致性检查。
3. 把通过的局部 Huygens 外推结果接入 G3 dashboard，并重新评估 reduced-layout 采样候选是否仍保持同等形状精度。
