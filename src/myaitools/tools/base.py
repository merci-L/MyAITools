"""小工具需要实现的接口约定。"""

from __future__ import annotations

import argparse
from typing import Protocol


class Tool(Protocol):
    """一个可以注册到 CLI 的小工具。

    实现约定：

    - ``name``：子命令名，小写加连字符，例如 ``word-count``
    - ``help``：出现在 ``--help`` 中的一句话说明
    - ``add_arguments()``：只声明该工具自己的参数
    - ``run()``：执行逻辑，返回退出码（0 表示成功，非 0 表示失败）
    """

    name: str
    help: str

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """向子命令解析器添加参数。"""
        ...

    def run(self, args: argparse.Namespace) -> int:
        """执行工具逻辑，返回退出码。"""
        ...
