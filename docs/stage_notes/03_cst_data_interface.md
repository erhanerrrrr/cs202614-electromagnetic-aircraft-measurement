# S03 CST 数据接口说明

## 做了什么

建立了 CST 导出数据的标准格式、校验脚本、幅相转换脚本和 demo 模板。当前支持 nearfield、farfield、labels、manifest、metrics 等表格字段。

## 为什么这样做

CST 导出格式一旦混乱，后续重建和识别会很难排错。因此先固定字段：

- nearfield 必须包含 `sample_id`、`sensor_id`、坐标、`frequency_hz`、极化、复数场。
- farfield 必须包含 `sample_id`、角度、频点和远场复数或功率/增益。
- 如果 CST 只能导出幅值/相位，先转换成实部/虚部再进入算法。

## 主要产物

| 文件/目录 | 意义 | 使用方式 |
|---|---|---|
| `code/cst_io.py` | CST 表格读取、校验、极化转换、测量向量生成 | 重建、识别、合并脚本共用 |
| `code/check_cst_export.py` | 校验 nearfield/farfield 是否合格 | CST 导出后第一步运行 |
| `code/prepare_cst_templates.py` | 生成 CST 测点和导出模板 | 给 CST 主责对齐字段 |
| `code/normalize_cst_complex_columns.py` | 幅相到实虚部转换 | 兼容 CST 幅相导出 |
| `outputs/cst_templates` | 测点表、模板、demo 数据 | CST 建模和接口测试 |
| `outputs/cst_phase_demo` | 幅相转换闭环验证 | 证明转换流程可用 |
| `docs/data_dictionary.md` | 数据字段字典 | 所有人统一字段口径 |

## 验证方式

```powershell
python code\prepare_cst_templates.py
python code\check_cst_export.py --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv
python code\normalize_cst_complex_columns.py --make-phase-demo --nearfield outputs\cst_templates\nearfield_demo_valid.csv --farfield outputs\cst_templates\farfield_demo_valid.csv --out-dir outputs\cst_phase_demo
```

## 当前不足

- 当前验证使用 demo 数据，不是 CST 全波仿真结果。
- 真实导出后仍需检查相位单位、坐标单位和极化定义。

## 下一步

1. CST 主责按数据字典导出 Level 1 required 文件。
2. 算法主责用 `check_cst_export.py` 和 `merge_cst_level1_exports.py` 审计。
