[![Release](https://img.shields.io/github/v/release/merci-L/MyAITools?label=release)](https://github.com/merci-L/MyAITools/releases)
[![CI](https://img.shields.io/github/actions/workflow/status/merci-L/MyAITools/ci.yml?branch=main&label=CI)](https://github.com/merci-L/MyAITools/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

# MyAITools

[简体中文](README.md) | [English](README.en.md)

一组轻量、可组合的 Python 命令行小工具，持续更新中。

## 特性

- **一个工具一个模块**：互不依赖，看得懂、改得动、删得掉
- **统一的命令行入口**：所有工具都挂在 `myaitools <command>` 下
- **标准的 `src` 布局 + `pyproject.toml`**：可 `pip install -e .` 本地开发，也可直接发布到 PyPI
- **自带质量保障**：pytest 测试、ruff 检查、GitHub Actions CI、pre-commit 钩子
- **面向开源**：LICENSE、贡献指南、行为准则、Issue/PR 模板、更新日志一应俱全

## 目录结构

```text
MyAITools/
├── .github/                  # Issue / PR 模板与 CI 工作流
│   ├── ISSUE_TEMPLATE/
│   ├── pull_request_template.md
│   └── workflows/
│       ├── ci.yml
│       └── release.yml       # 打 v* 标签后自动发布 GitHub Release
├── docs/                     # 文档
│   ├── adding-a-tool.md      # 如何新增一个小工具
│   ├── git-workflow.md       # Git 初始化与开源发布流程
│   └── jd-detector.md        # jd-detector 使用说明
├── src/myaitools/            # 唯一的源码包
│   ├── __init__.py           # 版本号（pyproject 从此处读取）
│   ├── __main__.py           # 支持 python -m myaitools
│   ├── cli.py                # CLI 入口与子命令注册
│   └── tools/                # 每个小工具一个模块
│       ├── __init__.py       # TOOL_REGISTRY 注册表
│       ├── base.py           # 工具接口约定
│       └── word_count.py     # 示例工具：文本统计
├── tests/                    # pytest 测试
├── pyproject.toml            # 项目元数据、依赖、工具配置
├── README.md / README.en.md  # 中英文说明
├── CHANGELOG.md              # 更新日志
├── CONTRIBUTING.md           # 贡献指南
├── CODE_OF_CONDUCT.md        # 行为准则
├── LICENSE                   # MIT 许可证
├── .gitignore / .gitattributes / .editorconfig
└── .pre-commit-config.yaml
```

## 快速开始

要求 Python 3.10 及以上。

```powershell
# 1. 创建并激活虚拟环境（Windows PowerShell）
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# 如果提示脚本被禁止运行，先执行：
# Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 2. 安装项目（-e 表示可编辑安装，改代码立即生效）
python -m pip install -U pip
python -m pip install -e ".[dev]"

# 3. 运行
myaitools --help
myaitools word-count README.md
```

> 国内网络下载依赖慢或超时，可以在安装命令后加清华镜像：
> `python -m pip install -e ".[dev]" -i https://pypi.tuna.tsinghua.edu.cn/simple`

也可以直接从 GitHub 安装（无需克隆仓库）：

```powershell
pip install git+https://github.com/merci-L/MyAITools.git
```

也可以用模块方式运行（无需安装入口脚本）：

```powershell
python -m myaitools word-count README.md
```

输出示例：

```text
lines: 120
words: 356
chars: 4821
```

## 现有工具

| 命令 | 说明 | 示例 |
| --- | --- | --- |
| `word-count` | 统计文本文件的字符数、单词数、行数 | `myaitools word-count README.md` |
| `sys-radar` | 查看本机 CPU、内存使用率与磁盘空间 | `myaitools sys-radar` |
| `jd-detector` | 调用 DeepSeek API 判断职位描述是否为销售/地推岗位 | `myaitools jd-detector --file jd.txt` |

`jd-detector` 需要先设置环境变量 `DEEPSEEK_API_KEY`，详细用法（输入方式、JSON 输出、退出码、隐私说明）见 [docs/jd-detector.md](docs/jd-detector.md)。

### 实际运行示例

`jd-detector` 实际调用 DeepSeek（`deepseek-chat`）的效果：

```powershell
python -m myaitools jd-detector "招聘地推专员，要求吃苦耐劳，单休，底薪3000，年薪四十万不是梦"
```

```text
结论: 是销售/地推岗位
置信度: 98%
理由: 职位为地推专员，职责为地面推广拉新获客，属销售/地推岗位。
```

## 图形界面（Streamlit）

除了命令行，项目还自带一个极简 Web 界面，包含「系统雷达」和「JD 脱水器」两个标签页：

```powershell
# 在仓库根目录安装依赖（streamlit 已包含在依赖中）
pip install -e .

# 启动界面
streamlit run src/myaitools/app.py
```

浏览器会自动打开 <http://localhost:8501>。系统雷达点击「采集读数」即可查看 CPU / 内存 / 磁盘；JD 脱水器需要先在左侧边栏填写 `DEEPSEEK_API_KEY`（或启动前设置环境变量），粘贴 JD 后点击「开始脱水」，会显示结论、置信度和水分指数。侧边栏的「深色模式」开关可在浅色与深色（夜班档案室）外观之间切换。

界面采用「精密档案卡」视觉世界（纸面读数、校准刻度、印章判定），设计 token 见 [DESIGN.md](DESIGN.md)，产品定义见 [PRODUCT.md](PRODUCT.md)。

## 新增一个小工具

三步即可，详细模板见 [docs/adding-a-tool.md](docs/adding-a-tool.md)：

1. 在 `src/myaitools/tools/` 下新建模块（如 `json_format.py`），实现 `name`、`help`、`add_arguments()`、`run()`
2. 在 `src/myaitools/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册
3. 在 `tests/` 补测试，并同步更新本文件与 `CHANGELOG.md`

## 开发

```powershell
ruff check .            # 代码检查
ruff format .           # 格式化
pytest                  # 运行测试
pytest --cov=myaitools  # 带覆盖率
pre-commit install      # 安装提交前钩子（只需一次）
```

## 开源与发布

- 仓库已推送到 GitHub，`main` 分支由 CI 保护，历史版本见 [Releases](https://github.com/merci-L/MyAITools/releases)
- 打上 `v*` 标签后，`.github/workflows/release.yml` 会自动提取 `CHANGELOG.md` 内容发布 GitHub Release
- 推送到 GitHub 的完整步骤、分支模型、提交信息规范、打标签与发布流程：见 [docs/git-workflow.md](docs/git-workflow.md)
- 发布到 PyPI（可选）：`python -m build` 后 `twine upload dist/*`

> 仓库主页：<https://github.com/merci-L/MyAITools>

## 许可证

[MIT](LICENSE) © 2026 merci_L
