# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增

- 新增 `sys-radar` 工具：查看本机 CPU、内存使用率与磁盘空间，支持 `--json` 输出与 `--path` 指定磁盘

### 变更

- 新增运行依赖 `psutil>=5.9`

## [0.1.0] - 2026-10-25

### 新增

- 初始化项目脚手架：`src` 布局、`myaitools` 命令行入口、pytest 测试、ruff 检查、GitHub Actions CI
- 第一个示例工具 `word-count`：统计文本文件的字符数、单词数与行数
- 开源配套文档：README（中英双版）、贡献指南、行为准则、Git 工作流教程

[Unreleased]: https://github.com/merci-L/MyAITools/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/merci-L/MyAITools/releases/tag/v0.1.0
