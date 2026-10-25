"""示例工具：统计文本文件的字符数、单词数与行数。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ENCODING = "utf-8"


def count_text(text: str) -> dict[str, int]:
    """返回文本的字符数、单词数与行数。"""
    return {
        "chars": len(text),
        "words": len(text.split()),
        "lines": len(text.splitlines()),
    }


class WordCountTool:
    """``word-count`` 子命令：类似 ``wc`` 的文本统计。"""

    name = "word-count"
    help = "统计文本文件的字符数、单词数与行数"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("path", type=Path, help="要统计的文本文件路径")
        parser.add_argument("-c", "--chars", action="store_true", help="只输出字符数")
        parser.add_argument("-w", "--words", action="store_true", help="只输出单词数")
        parser.add_argument("-l", "--lines", action="store_true", help="只输出行数")

    def run(self, args: argparse.Namespace) -> int:
        try:
            text = args.path.read_text(encoding=ENCODING)
        except FileNotFoundError:
            print(f"错误：找不到文件 {args.path}", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"错误：读取 {args.path} 失败：{exc}", file=sys.stderr)
            return 1

        counts = count_text(text)
        selected = {"lines": args.lines, "words": args.words, "chars": args.chars}
        if not any(selected.values()):
            selected = dict.fromkeys(selected, True)

        for key, enabled in selected.items():
            if enabled:
                print(f"{key}: {counts[key]}")
        return 0
