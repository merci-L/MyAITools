"""sys-radar 工具的测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from myaitools.cli import main
from myaitools.tools.sys_radar import (
    collect_disks,
    format_bytes,
    format_percent,
    render_json,
    render_text,
)

GIB = 1024**3

FAKE_DATA = {
    "cpu": {"percent": 12.5, "logical_cores": 8, "physical_cores": 4},
    "memory": {
        "total": 16 * GIB,
        "used": 8 * GIB,
        "available": 8 * GIB,
        "percent": 50.0,
    },
    "disks": [
        {
            "mountpoint": "C:\\",
            "fstype": "NTFS",
            "total": 512 * GIB,
            "used": 256 * GIB,
            "free": 256 * GIB,
            "percent": 50.0,
        }
    ],
}


def test_format_bytes() -> None:
    assert format_bytes(0) == "0 B"
    assert format_bytes(512) == "512 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1536) == "1.5 KB"
    assert format_bytes(GIB) == "1.0 GB"
    assert format_bytes(1024 * GIB) == "1.0 TB"


def test_format_percent() -> None:
    assert format_percent(0) == "0.0%"
    assert format_percent(12.34) == "12.3%"


def test_render_text_contains_all_sections() -> None:
    text = render_text(FAKE_DATA)
    assert "CPU" in text
    assert "12.5%" in text
    assert "8 逻辑核心（4 物理核心）" in text
    assert "8.0 GB" in text
    assert "NTFS" in text
    assert "50.0%" in text


def test_render_text_without_disks() -> None:
    data = {**FAKE_DATA, "disks": []}
    assert "未检测到可用磁盘" in render_text(data)


def test_render_json_round_trip() -> None:
    assert json.loads(render_json(FAKE_DATA)) == FAKE_DATA


def test_collect_disks_with_explicit_path(tmp_path: Path) -> None:
    disks = collect_disks([tmp_path])
    assert len(disks) == 1
    assert disks[0]["mountpoint"] == str(tmp_path.resolve())
    assert disks[0]["total"] > 0
    assert disks[0]["percent"] >= 0


def test_cli_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sys-radar", "--json", "--interval", "0"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert set(data) == {"cpu", "memory", "disks"}
    assert isinstance(data["cpu"]["percent"], int | float)
    assert data["memory"]["total"] > 0


def test_cli_missing_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sys-radar", "--path", str(tmp_path / "missing")]) == 1
    assert "错误" in capsys.readouterr().err


def test_cli_rejects_negative_interval(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sys-radar", "--interval", "-1"]) == 2
    assert "不能为负数" in capsys.readouterr().err
