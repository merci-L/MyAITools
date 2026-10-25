"""word-count 工具的单元测试。"""

from __future__ import annotations

from myaitools.tools.word_count import count_text


def test_counts_mixed_text() -> None:
    counts = count_text("hello world\n你好，世界\n")
    assert counts["lines"] == 2
    assert counts["words"] == 3
    assert counts["chars"] == len("hello world\n你好，世界\n")


def test_counts_without_trailing_newline() -> None:
    counts = count_text("a b c")
    assert counts == {"chars": 5, "words": 3, "lines": 1}


def test_counts_empty_text() -> None:
    counts = count_text("")
    assert counts == {"chars": 0, "words": 0, "lines": 0}
