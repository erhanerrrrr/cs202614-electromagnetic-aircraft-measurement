# 协作说明

## 分支与提交

- `main` 保持可读、可复现、可展示。
- 新任务建议从 `main` 拉分支：`feature/cst-level2-case-*`、`feature/sampling-optimization-*`、`docs/workflow-*`。
- 每次提交尽量只改一个主题：CST 数据、算法脚本、文档更新不要混在一个 commit。

## 大文件约定

- 不提交 `node_modules/`、CST `Result/`/`Temp/`/`ModelCache/`、最终 zip、可再生成的大型 CSV。
- 真实 CST 导出优先放入 `data/cst_exports/`，并同步更新对应 README 或 issue。
- 若后续必须协作大文件，使用 Git LFS、GitHub Release 或队伍共享网盘，在仓库保留链接、SHA256 和生成命令。

## 提交前检查

```powershell
python -m compileall code
python code\check_cst_export.py --nearfield data\cst_exports\level1\all_nearfield.csv --farfield data\cst_exports\level1\all_farfield.csv
```

如果只改文档，可跳过数据校验，但需要确认链接和文件路径有效。
