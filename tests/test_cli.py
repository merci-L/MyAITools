"""CLI 入口与子命令注册的测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from myaitools import __version__
from myaitools.cli import main


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage:" in capsys.readouterr().out


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_unknown_command_exits_with_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["no-such-command"])
    assert excinfo.value.code == 2


def test_word_count_reports_all_counts(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("hello world\n你好，世界\n", encoding="utf-8")

    assert main(["word-count", str(path)]) == 0
    out = capsys.readouterr().out
    assert "lines: 2" in out
    assert "words: 3" in out
    assert "chars: 18" in out


def test_word_count_single_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "sample.txt"
    path.write_text("a b c", encoding="utf-8")

    assert main(["word-count", "-w", str(path)]) == 0
    assert capsys.readouterr().out.strip() == "words: 3"


def test_word_count_missing_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["word-count", str(tmp_path / "missing.txt")]) == 1
    assert "找不到文件" in capsys.readouterr().err
