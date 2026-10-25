# 贡献指南

感谢你愿意为 MyAITools 出力！下面是参与开发的约定，保持简单：

## 开发环境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"

ruff check .            # 静态检查
ruff format .           # 格式化
pytest                  # 跑测试
pre-commit install      # 安装提交前钩子（只需一次）
```

## 分支约定

| 分支 | 用途 |
| --- | --- |
| `main` | 稳定分支，始终可运行、可通过测试 |
| `feat/<主题>` | 新功能或新工具，例如 `feat/json-format` |
| `fix/<主题>` | 修复问题，例如 `fix/word-count-crlf` |
| `docs/<主题>` | 只改文档，例如 `docs/git-guide` |

从最新的 `main` 切出分支，完成后通过 Pull Request 合回 `main`。

## 提交信息规范

采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```text
<type>(<scope>): <简短描述>
```

常用 `type`：

| type | 含义 |
| --- | --- |
| `feat` | 新功能、新工具 |
| `fix` | 修复 bug |
| `docs` | 仅文档变更 |
| `refactor` | 重构，不改变行为 |
| `test` | 测试相关 |
| `build` | 构建、依赖变更 |
| `ci` | CI 配置变更 |
| `chore` | 杂项（初始化、版本号等） |

示例：

```text
feat(word-count): 支持指定编码读取文件
fix(cli): 修复无子命令时退出码错误
docs(readme): 补充安装步骤
```

## 新增工具

见 [docs/adding-a-tool.md](docs/adding-a-tool.md)。要点：

1. 一个工具一个模块，文件放在 `src/myaitools/tools/`，命令名用 kebab-case
2. 在 `src/myaitools/tools/__init__.py` 的 `TOOL_REGISTRY` 中注册
3. 正常路径与异常路径都要有测试
4. 同步更新 README、CHANGELOG

## 代码风格

- 遵循 ruff 的默认规则（配置在 `pyproject.toml`），提交前请跑 `ruff check .` 和 `ruff format .`
- 面向用户的错误信息用中文，写到 `stderr`，并返回非 0 退出码
- 读取文件统一用 `pathlib.Path` 和显式 `encoding="utf-8"`

## Pull Request 检查清单

- [ ] 分支从最新 `main` 切出
- [ ] `ruff check .` 与 `ruff format --check .` 通过
- [ ] `pytest` 全部通过
- [ ] 新功能包含测试，文档已更新
- [ ] 单个 PR 只做一件事，描述写清楚“改了什么、为什么”

## 行为准则

参与本项目即表示同意遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。

## 许可证

提交的代码默认以 [MIT](LICENSE) 许可证发布。
