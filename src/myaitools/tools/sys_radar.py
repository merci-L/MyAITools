"""系统雷达：查看本机 CPU、内存与磁盘使用情况。"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import psutil

__all__ = [
    "SysRadarTool",
    "collect",
    "collect_cpu",
    "collect_disks",
    "collect_memory",
    "format_bytes",
    "format_percent",
    "render_json",
    "render_text",
]


def format_bytes(size: float) -> str:
    """把字节数格式化成易读的字符串。"""
    value = float(size)
    if abs(value) < 1024:
        return f"{int(value)} B"
    for unit in ("KB", "MB", "GB", "TB"):
        value /= 1024
        if abs(value) < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
    return f"{value:.1f} TB"  # pragma: no cover


def format_percent(percent: float) -> str:
    """把百分比格式化为一位小数。"""
    return f"{percent:.1f}%"


def collect_cpu(interval: float = 0.3) -> dict[str, Any]:
    """采集 CPU 使用率与核心数。"""
    return {
        "percent": psutil.cpu_percent(interval=interval),
        "logical_cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
    }


def collect_memory() -> dict[str, Any]:
    """采集内存使用情况。"""
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent,
    }


def _disk_entry(mountpoint: str, fstype: str, total: int, used: int, free: int) -> dict[str, Any]:
    percent = (used / total * 100) if total else 0.0
    return {
        "mountpoint": mountpoint,
        "fstype": fstype,
        "total": total,
        "used": used,
        "free": free,
        "percent": round(percent, 1),
    }


def collect_disks(targets: list[Path] | None = None) -> list[dict[str, Any]]:
    """采集磁盘空间。

    默认列出所有本地物理磁盘；传入 ``targets`` 时只统计这些路径所在的磁盘。
    """
    if targets:
        disks: list[dict[str, Any]] = []
        for target in targets:
            path = target.expanduser().resolve()
            usage = shutil.disk_usage(path)
            disks.append(_disk_entry(str(path), "", usage.total, usage.used, usage.free))
        return disks

    disks = []
    seen: set[str] = set()
    for partition in psutil.disk_partitions(all=False):
        if not partition.fstype or "cdrom" in partition.opts:
            continue
        if partition.device in seen:
            continue
        try:
            usage = shutil.disk_usage(partition.mountpoint)
        except OSError:
            continue
        seen.add(partition.device)
        disks.append(
            _disk_entry(
                partition.mountpoint,
                partition.fstype,
                usage.total,
                usage.used,
                usage.free,
            )
        )
    return disks


def collect(interval: float = 0.3, targets: list[Path] | None = None) -> dict[str, Any]:
    """采集 CPU、内存、磁盘三部分数据。"""
    return {
        "cpu": collect_cpu(interval=interval),
        "memory": collect_memory(),
        "disks": collect_disks(targets),
    }


def render_text(data: dict[str, Any]) -> str:
    """把采集结果渲染为带分组标题的纯文本。"""
    cpu = data["cpu"]
    memory = data["memory"]
    lines = ["CPU"]

    cores = f"{cpu['logical_cores']} 逻辑核心"
    if cpu["physical_cores"]:
        cores += f"（{cpu['physical_cores']} 物理核心）"
    lines.append(f"  使用率: {format_percent(cpu['percent'])}")
    lines.append(f"  核心数: {cores}")

    lines.append("内存")
    lines.append(
        f"  已用: {format_bytes(memory['used'])} / {format_bytes(memory['total'])}"
        f"（{format_percent(memory['percent'])}，可用 {format_bytes(memory['available'])}）"
    )

    lines.append("磁盘")
    if not data["disks"]:
        lines.append("  未检测到可用磁盘")
    for disk in data["disks"]:
        label = disk["mountpoint"]
        if disk["fstype"]:
            label += f" [{disk['fstype']}]"
        lines.append(
            f"  {label} 已用 {format_bytes(disk['used'])} / {format_bytes(disk['total'])}"
            f"（剩余 {format_bytes(disk['free'])}，{format_percent(disk['percent'])}）"
        )
    return "\n".join(lines)


def render_json(data: dict[str, Any]) -> str:
    """把采集结果渲染为 JSON 字符串。"""
    return json.dumps(data, ensure_ascii=False, indent=2)


class SysRadarTool:
    """``sys-radar`` 子命令：一眼看清本机资源占用。"""

    name = "sys-radar"
    help = "查看本机 CPU、内存使用率和磁盘空间"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--json",
            action="store_true",
            help="以 JSON 格式输出，便于脚本处理",
        )
        parser.add_argument(
            "--interval",
            type=float,
            default=0.3,
            metavar="SECONDS",
            help="CPU 采样时长（秒），默认 0.3",
        )
        parser.add_argument(
            "--path",
            action="append",
            type=Path,
            default=None,
            metavar="PATH",
            help="只统计指定路径所在的磁盘，可重复指定",
        )

    def run(self, args: argparse.Namespace) -> int:
        if args.interval < 0:
            print("错误：--interval 不能为负数", file=sys.stderr)
            return 2
        try:
            data = collect(interval=args.interval, targets=args.path)
        except OSError as exc:
            print(f"错误：读取系统信息失败：{exc}", file=sys.stderr)
            return 1
        print(render_json(data) if args.json else render_text(data))
        return 0
