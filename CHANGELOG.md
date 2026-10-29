# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 规范，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.3.0] - 2026-10-29

### 新增

- `jd-detector` 支持 `--file` 批量流水线：读取 `.txt` / `.csv`，自动按空行或 `---` 切割 JD 并逐条分析
- 批量分析支持 `--workers` 并发、`--retries` 指数退避重试（超时 / 429 / 5xx）、`--no-cache` 缓存开关、`--dry-run` 预览与 `--limit` 条数限制
- 批量分析在终端输出 Markdown 汇总表（序号 / 岗位简称 / 岗位性质 / 水分指数），并生成 `report.csv`（UTF-8 BOM，Excel 可直接打开；已做 CSV 公式注入防护）
- 单条 JD 分析失败不会中断整批，结果标记为「分析失败」；可用 `--report` 指定报告路径
- 新增 Streamlit「批量分析」标签页：上传 `.txt` / `.csv`、预览切割结果、进度条、结果表格与 `report.csv` 下载
- 新增 Streamlit 图形界面 `app.py`：包含「系统雷达」和「JD 脱水器」两个标签页，JD 脱水器展示结论、置信度与水分指数
- 新增 Release 自动发布工作流：推送 `v*` 标签后自动提取 `CHANGELOG.md` 内容创建 GitHub Release

### 变更

- `jd-detector --file` 从单条读取升级为批量入口；不带 `--file` 时仍支持文本参数 / 标准输入单条分析
- 新增运行依赖 `streamlit>=1.36`
- GUI 重做为「精密档案卡」视觉世界：Streamlit 主题 + 自定义 CSS、校准刻度条、印章判定与纸面读数排版
- GUI 支持浅色 / 深色双外观：深色为同一档案世界的「夜班」版本，侧边栏开关即时切换
- 设计终审（taste + impeccable）：统一 2 种系统字体、去掉静态阴影与微缩大写标签、全站字号 ≥11px、补上 h1，并把浅色底改为中性石色

### 文档

- README、`docs/jd-detector.md` 增加批量分析用法、并发/重试/缓存参数与 `report.csv` 说明
- CI 扩展为 Ubuntu / Windows / macOS 跨平台矩阵，并启用 Dependabot 依赖更新
- README 增加 Release / CI / License 徽章，并补充从 GitHub 直接安装的说明
- README 增加图形界面启动说明
- 新增 `PRODUCT.md` 与 `DESIGN.md`，记录产品定义与设计 token

## [0.2.0] - 2026-10-28

### 新增

- 新增 `sys-radar` 工具：查看本机 CPU、内存使用率与磁盘空间，支持 `--json` 输出与 `--path` 指定磁盘
- 新增 `jd-detector` 工具：调用 DeepSeek API 判断职位描述是否为销售/地推岗位，支持文本参数、`--file`、标准输入三种输入方式与 `--json` 输出
- README 补充 `jd-detector` 的实际运行示例

### 变更

- 新增运行依赖 `psutil>=5.9`

## [0.1.0] - 2026-10-25

### 新增

- 初始化项目脚手架：`src` 布局、`myaitools` 命令行入口、pytest 测试、ruff 检查、GitHub Actions CI
- 第一个示例工具 `word-count`：统计文本文件的字符数、单词数与行数
- 开源配套文档：README（中英双版）、贡献指南、行为准则、Git 工作流教程

[Unreleased]: https://github.com/merci-L/MyAITools/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/merci-L/MyAITools/releases/tag/v0.3.0
[0.2.0]: https://github.com/merci-L/MyAITools/releases/tag/v0.2.0
[0.1.0]: https://github.com/merci-L/MyAITools/releases/tag/v0.1.0
