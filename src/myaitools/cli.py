"""命令行入口：把所有小工具注册成 ``myaitools <command>`` 子命令。"""

from __future__ import annotations

import argparse

from myaitools import __version__
from myaitools.tools import TOOL_REGISTRY


def build_parser() -> argparse.ArgumentParser:
    """构建顶层解析器，并把每个工具注册为子命令。"""
    parser = argparse.ArgumentParser(
        prog="myaitools",
        description="一组轻量、可组合的 Python 命令行小工具。",
        epilog="用 `myaitools <command> --help` 查看某个工具的具体用法。",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    for tool in TOOL_REGISTRY:
        subparser = subparsers.add_parser(tool.name, help=tool.help, description=tool.help)
        tool.add_arguments(subparser)
        subparser.set_defaults(func=tool.run)
    return parser


def main(argv: list[str] | None = None) -> int:
    """程序入口，返回进程退出码（0 表示成功）。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 0
    return int(func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
