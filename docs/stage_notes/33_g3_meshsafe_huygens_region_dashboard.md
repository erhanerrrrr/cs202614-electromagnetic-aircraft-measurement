# S33 G3 mesh-safe Huygens region-lobe gate and dashboard integration

## 做了什么

- 在 `code/run_cst_meshsafe_huygens_extrapolation.py` 中新增 top-power 主瓣区域指标，补充原有单点 `argmax` 主瓣误差。
- 将两例真实 CST mesh-safe Huygens batch 重新生成，输出区域主瓣误差、区域 Jaccard 和区域 capture。
- 将 `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` 接入 `code/build_g3_model_dashboard.py`。
- 刷新 `outputs/g3_model_dashboard/`，新增 `meshsafe_huygens_real_cst_batch` 证据行，并把下一步优先级改为 H-field/阻抗定标。

## 为什么这样做

S32 中短偶极子已经有很高的全方向相关性和很低的尺度拟合 NMSE，但因为方向图是宽环状高功率区域，单个最大值点会跳到对称/近简并位置，导致 `main_lobe_error_deg = 139.52`。这个数值不代表整体方向图错了，而是指标本身不适合评价环状主瓣。

本阶段新增的区域主瓣指标把参考方向图和预测方向图中归一化功率高于 `0.75` 的区域作为主瓣区域，计算区域误差、区域 Jaccard 和区域 capture。这样保留了单点主瓣误差作为严格指标，同时新增更适合宽主瓣/环状主瓣的稳定判断。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/run_cst_meshsafe_huygens_extrapolation.py` | 新增 `main_lobe_region_*` 指标和 `region_shape_pass` 状态 | `python code\run_cst_meshsafe_huygens_extrapolation.py --batch` |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.csv` | 两例 batch 汇总，包含 point-lobe 与 region-lobe 对照 | 查看跨源例区域主瓣门控 |
| `data/sampling_layouts/cst_meshsafe_huygens_extrapolation_batch/meshsafe_huygens_batch_summary.json` | 机器可读 batch 汇总，新增 `case_count_strict_proxy_or_region` | G3 dashboard 输入 |
| `code/build_g3_model_dashboard.py` | 新增真实 CST mesh-safe batch 证据行和下一步 H-field/阻抗动作 | `python code\build_g3_model_dashboard.py` |
| `outputs/g3_model_dashboard/g3_model_status.csv` | 新增 `meshsafe_huygens_real_cst_batch` 行 | G3 当前状态总览 |
| `outputs/g3_model_dashboard/g3_next_actions.csv` | 第一优先级变为 mesh-safe Huygens H-field/阻抗定标 | 后续执行清单 |

## 验证方式

```powershell
python -m py_compile code\run_cst_meshsafe_huygens_extrapolation.py code\build_g3_model_dashboard.py
python code\run_cst_meshsafe_huygens_extrapolation.py --batch
python code\build_g3_model_dashboard.py
```

当前验证结果：

- batch gate 完成 `2/2`，缺失或失败 `0`。
- 旧的 strict/physics-proxy count 为 `1`，新增 strict/physics-proxy/region count 为 `2`。
- `L1_halfwave_dipole_z_1p2G` 保持 `physics_proxy_pass`，相关性约 `0.9868`，scaled NMSE 约 `1.41e-2`，point-lobe 和 region-lobe 误差均为 `0.00 deg`。
- `L1_short_dipole_z_1p2G` 从 `shape_pass_lobe_ambiguous` 提升为 `region_shape_pass`：point-lobe 误差仍为 `139.52 deg`，但 region-lobe 误差为 `0.00 deg`，区域 Jaccard 约 `0.919`，区域 min capture 约 `0.930`。
- G3 dashboard 新增 `meshsafe_huygens_real_cst_batch`，状态为 `region_proxy_batch_pass`。

## 当前解释

本阶段没有声称最终 Huygens 物理证明完成。它解决的是评价门控问题：短偶极子的环状主瓣不能只用单点最大值位置判断。区域主瓣指标显示，真实 CST 局部场经当前 proxy 外推后，其高功率主瓣区域与参考方向图高度重合。

这使当前结论更精确：mesh-safe 路线已经在两个 Level 1 源例上通过真实 CST 数据链和区域主瓣门控；后续真正要攻克的是 H-field/阻抗支撑的等效面流定标，而不是 CST 是否能跑、ResultTree 是否能导出、或短偶极子方向图是否完全错位。

## 下一步

1. 准备 H-field 或阻抗定标工作包，让局部 Huygens 面从 E-field proxy 走向等效面电流/面磁流。
2. 若 CST 可稳定导出 H-field probe 曲线，则为两例重复 `E/H -> J/M -> farfield` 批处理。
3. 若 H-field probe 暂不可得，则先用现有 E-field 与 farfield reference 拟合局部等效阻抗，给出显式误差边界，再进入下一轮 dashboard。
