"""职位检测器：调用 DeepSeek API 判断一段文字是否为销售/地推岗位。"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from myaitools import __version__

__all__ = [
    "API_KEY_ENV",
    "DEFAULT_BASE_URL",
    "DEFAULT_MODEL",
    "DEFAULT_TIMEOUT",
    "JdDetectorError",
    "JdDetectorTool",
    "build_messages",
    "classify",
    "parse_classification",
    "read_input",
    "render_json",
    "render_text",
    "request_completion",
]

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 30.0
API_KEY_ENV = "DEEPSEEK_API_KEY"

SYSTEM_PROMPT = (
    "你是一个招聘信息分类助手。请判断用户提供的职位描述是否属于销售或地推（地面推广）岗位。\n"
    "判断标准：岗位职责以直接销售产品或服务、开拓客户、地推推广、拉新获客、电话销售、"
    "门店导购等为主，视为销售/地推岗位；研发、技术支持、行政、运营策划等非直接销售岗位视为否。\n"
    "只输出一个 JSON 对象（json），不要输出其他内容，格式为："
    '{"is_sales": true 或 false, "confidence": 0 到 1 之间的小数, '
    '"reason": "不超过 50 字的中文理由"}'
)

_TRUE_VALUES = {"true", "yes", "是", "1"}
_FALSE_VALUES = {"false", "no", "否", "0"}


class JdDetectorError(Exception):
    """调用 DeepSeek API 或解析结果时发生的错误。"""


def build_messages(text: str) -> list[dict[str, str]]:
    """构造发送给 DeepSeek 的消息列表。"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"职位描述：\n{text}"},
    ]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE_VALUES:
            return True
        if normalized in _FALSE_VALUES:
            return False
    raise JdDetectorError("模型输出的 is_sales 字段不是布尔值")


def _as_confidence(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(min(max(number, 0.0), 1.0), 2)


def parse_classification(content: str) -> dict[str, Any]:
    """从模型输出中解析出分类结果。"""
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match is None:
        raise JdDetectorError("无法从模型输出中解析出 JSON 结果")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise JdDetectorError("模型输出中的 JSON 格式不合法") from exc
    if not isinstance(data, dict):
        raise JdDetectorError("模型输出中的 JSON 不是对象")
    return {
        "is_sales": _as_bool(data.get("is_sales")),
        "confidence": _as_confidence(data.get("confidence")),
        "reason": str(data.get("reason") or "").strip(),
    }


def _post_json(
    url: str,
    payload: dict[str, Any],
    api_key: str,
    timeout: float,
) -> dict[str, Any]:
    """发送 JSON POST 请求，返回解析后的响应体。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"myaitools/{__version__}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def request_completion(
    text: str,
    *,
    api_key: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """调用 DeepSeek 对话接口，返回模型输出的文本内容。"""
    payload = {
        "model": model,
        "messages": build_messages(text),
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    url = f"{base_url.rstrip('/')}/chat/completions"
    try:
        data = _post_json(url, payload, api_key, timeout)
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            error_body = json.loads(exc.read().decode("utf-8", errors="replace"))
        except (json.JSONDecodeError, OSError):
            error_body = None
        if isinstance(error_body, dict):
            error = error_body.get("error")
            if isinstance(error, dict):
                detail = str(error.get("message") or "")
        suffix = f"：{detail}" if detail else ""
        raise JdDetectorError(f"DeepSeek API 返回 HTTP {exc.code}{suffix}") from exc
    except urllib.error.URLError as exc:
        raise JdDetectorError(f"无法连接 DeepSeek API：{exc.reason}") from exc
    except TimeoutError as exc:
        raise JdDetectorError(f"请求 DeepSeek API 超时（{timeout:g} 秒）") from exc
    except json.JSONDecodeError as exc:
        raise JdDetectorError("DeepSeek API 返回内容不是合法 JSON") from exc

    try:
        return str(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise JdDetectorError("DeepSeek API 返回结构异常") from exc


def classify(
    text: str,
    *,
    api_key: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """把职位描述交给 DeepSeek 判断，返回结构化结果。"""
    content = request_completion(
        text,
        api_key=api_key,
        model=model,
        base_url=base_url,
        timeout=timeout,
    )
    return parse_classification(content)


def render_text(result: dict[str, Any]) -> str:
    """把判断结果渲染为便于阅读的文本。"""
    verdict = "是销售/地推岗位" if result["is_sales"] else "不是销售/地推岗位"
    lines = [f"结论: {verdict}"]
    confidence = result.get("confidence")
    if confidence is not None:
        lines.append(f"置信度: {confidence:.0%}")
    reason = result.get("reason")
    if reason:
        lines.append(f"理由: {reason}")
    return "\n".join(lines)


def render_json(result: dict[str, Any]) -> str:
    """把判断结果渲染为 JSON 字符串。"""
    return json.dumps(result, ensure_ascii=False, indent=2)


def read_input(text: str | None, file: Path | None) -> str:
    """按优先级读取职位描述：文本参数 > --file > 标准输入。"""
    if text is not None and file is not None:
        raise JdDetectorError("不能同时指定文本参数和 --file")
    if file is not None:
        try:
            content = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise JdDetectorError(f"读取文件失败：{exc}") from exc
    elif text is not None:
        content = text
    elif not sys.stdin.isatty():
        content = sys.stdin.read()
    else:
        raise JdDetectorError("请提供职位描述：文本参数、--file 或通过标准输入传入")

    content = content.strip()
    if not content:
        raise JdDetectorError("职位描述内容为空")
    return content


class JdDetectorTool:
    """``jd-detector`` 子命令：用 DeepSeek 判断职位是否为销售/地推。"""

    name = "jd-detector"
    help = "调用 DeepSeek API 判断一段职位描述是否为销售/地推岗位"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "text",
            nargs="?",
            default=None,
            help="职位描述文本；省略时从 --file 或标准输入读取",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=Path,
            default=None,
            help="从 UTF-8 文本文件读取职位描述",
        )
        parser.add_argument("--json", action="store_true", help="以 JSON 格式输出判断结果")
        parser.add_argument(
            "--model",
            default=DEFAULT_MODEL,
            help=f"DeepSeek 模型名，默认 {DEFAULT_MODEL}",
        )
        parser.add_argument(
            "--base-url",
            default=DEFAULT_BASE_URL,
            help=f"API 地址，默认 {DEFAULT_BASE_URL}",
        )
        parser.add_argument(
            "--timeout",
            type=float,
            default=DEFAULT_TIMEOUT,
            metavar="SECONDS",
            help=f"请求超时秒数，默认 {DEFAULT_TIMEOUT:g}",
        )

    def run(self, args: argparse.Namespace) -> int:
        if args.timeout <= 0:
            print("错误：--timeout 必须大于 0", file=sys.stderr)
            return 2
        try:
            text = read_input(args.text, args.file)
        except JdDetectorError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1

        api_key = os.environ.get(API_KEY_ENV, "").strip()
        if not api_key:
            print(f"错误：未设置环境变量 {API_KEY_ENV}", file=sys.stderr)
            return 1

        try:
            result = classify(
                text,
                api_key=api_key,
                model=args.model,
                base_url=args.base_url,
                timeout=args.timeout,
            )
        except JdDetectorError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1

        print(render_json(result) if args.json else render_text(result))
        return 0
