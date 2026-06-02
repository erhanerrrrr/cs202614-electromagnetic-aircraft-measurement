---
name: CST 数据/建模任务
about: 提交或跟踪 CST 建模、求解、导出、真近场 monitor 和数据校验任务
title: "[CST] "
labels: cst, data
---

## 任务类型

- [ ] Level 1 标准源
- [ ] Level 2 多源/多状态
- [ ] 简化结构/安装效应
- [ ] True near-field monitor 导出
- [ ] Full-wave airframe 增强

## 样本与频点

- sample_id：
- frequency_hz：
- candidate/layout：
- polarization/field components：

## 目标文件

- nearfield CSV：
- farfield CSV：
- true-monitor CSV：
- CST 工程/截图/日志位置：

当前 required true-monitor 优先文件：

- `data/cst_exports/level1_true_nearfield/L1_short_dipole_z_1p2G_true_nearfield.csv`
- `data/cst_exports/level1_true_nearfield/L1_halfwave_dipole_z_1p2G_true_nearfield.csv`

每个 required full-grid 文件应有 486 行，并包含 `Ex/Ey/Ez` 三个复场分量。

## 校验命令

```powershell
python code\check_true_nearfield_dropzone.py --required-only --full-grid-only
python code\run_true_nearfield_gate.py --required-only
python code\run_true_nearfield_workflow_decision.py
```

## 完成标准

- [ ] 目标 CSV 路径存在
- [ ] 行数、频点、sample_id、sensor subset 正确
- [ ] `check_true_nearfield_dropzone.py` 不再报告 `missing_file`
- [ ] README、issue 或 handoff 状态已同步
