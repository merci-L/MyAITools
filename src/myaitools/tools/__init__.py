"""内置小工具注册表：新增工具后在这里登记。"""

from __future__ import annotations

from myaitools.tools.base import Tool
from myaitools.tools.word_count import WordCountTool

TOOL_REGISTRY: tuple[Tool, ...] = (WordCountTool(),)

__all__ = ["TOOL_REGISTRY", "Tool"]
