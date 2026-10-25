# 新增一个小工具

所有工具共用一套注册机制：CLI 遍历 `TOOL_REGISTRY`，把每个工具注册成 `myaitools <name>` 子命令。新增工具只需写一个模块并登记即可。

## 约定

| 项目 | 约定 | 示例 |
| --- | --- | --- |
| 模块文件名 | snake_case | `json_format.py` |
| 子命令名 | kebab-case | `json-format` |
| 错误输出 | 写到 `stderr`，返回 1 | `print(..., file=sys.stderr)` |
| 正常输出 | 写到 `stdout` | `print(...)` |
| 退出码 | 0 成功 / 1 运行错误 / 2 参数错误 | `return 0` |
| 文件读写 | `pathlib.Path` + 显式 UTF-8 | `path.read_text(encoding="utf-8")` |

## 第一步：写模块

在 `src/myaitools/tools/` 下新建文件，按模板实现：

```python
"""一句话说明这个工具做什么。"""

from __future__ import annotations

import argparse
import sys

__all__ = ["MyTool"]


class MyTool:
    """``my-tool`` 子命令的实现。"""

    name = "my-tool"
    help = "在 --help 里显示的一句话说明"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("input", help="输入文件路径")
        parser.add_argument("-n", "--number", type=int, default=1, help="某个可选项")

    def run(self, args: argparse.Namespace) -> int:
        try:
            # 你的逻辑：读取 args.input，使用 args.number
            print(f"处理 {args.input}")
        except OSError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        return 0
```

说明：

- 类名由你定，必须提供 `name`、`help` 两个属性，以及 `add_arguments()`、`run()` 两个方法
- 不要在模块里调用 `sys.exit()`，用返回值表达结果，方便测试
- 需要第三方依赖时，把它加进 `pyproject.toml` 的 `project.dependencies`

## 第二步：注册

编辑 `src/myaitools/tools/__init__.py`：

```python
from myaitools.tools.my_tool import MyTool

TOOL_REGISTRY: tuple[Tool, ...] = (
    WordCountTool(),
    MyTool(),  # 新增
)
```

## 第三步：写测试

在 `tests/` 下新建 `test_my_tool.py`，至少覆盖正常路径和错误路径：

```python
from __future__ import annotations

from pathlib import Path

import pytest

from myaitools.cli import main


def test_my_tool_runs(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "in.txt"
    target.write_text("hello", encoding="utf-8")

    assert main(["my-tool", str(target)]) == 0
    assert "hello" in capsys.readouterr().out


def test_my_tool_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["my-tool", str(tmp_path / "missing.txt")]) == 1
    assert "错误" in capsys.readouterr().err
```

## 第四步：更新文档

- 在 `README.md` / `README.en.md` 的“现有工具”表格中加一行
- 在 `CHANGELOG.md` 的 `[Unreleased]` 下加 `feat(<工具名>): ...`
- 如果工具较复杂，在 `docs/` 下补一份使用说明

## 第五步：本地验证

```powershell
ruff check .
ruff format --check .
pytest
myaitools my-tool --help
```

全部通过后按 [CONTRIBUTING.md](../CONTRIBUTING.md) 的分支规范提交 Pull Request。
