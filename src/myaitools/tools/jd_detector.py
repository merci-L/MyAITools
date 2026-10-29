"""职位检测器：调用 DeepSeek API 判断一段文字是否为销售/地推岗位。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from myaitools import __version__

__all__ = [
    "API_KEY_ENV",
    "DEFAULT_BASE_URL",
    "DEFAULT_CACHE_PATH",
    "DEFAULT_MODEL",
    "DEFAULT_RETRIES",
    "DEFAULT_TIMEOUT",
    "DEFAULT_WORKERS",
    "REPORT_COLUMNS",
    "REPORT_FILENAME",
    "JdBatchResult",
    "JdDetectorError",
    "JdDetectorTool",
    "JdItem",
    "analyze_batch",
    "build_messages",
    "classify",
    "estimate_water_index",
    "load_bytes",
    "load_file",
    "parse_classification",
    "read_input",
    "render_dry_run",
    "render_json",
    "render_markdown_table",
    "render_text",
    "report_csv_bytes",
    "request_completion",
    "short_title",
    "split_jds",
    "write_report_csv",
]

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TIMEOUT = 30.0
DEFAULT_WORKERS = 4
DEFAULT_RETRIES = 2
DEFAULT_CACHE_PATH = Path(".cache/jd-detector.json")
API_KEY_ENV = "DEEPSEEK_API_KEY"
REPORT_FILENAME = "report.csv"
REPORT_COLUMNS = ("序号", "岗位简称", "岗位性质", "水分指数")
_RETRYABLE_HTTP_STATUS = frozenset({408, 409, 425, 429, 500, 502, 503, 504})
_EXCEL_FORMULA_PREFIXES = ("=", "+", "-", "@")

_TEXT_COLUMNS = ("jd", "jd_text", "description", "职位描述", "岗位描述", "内容")
_TITLE_COLUMNS = ("title", "position", "岗位", "岗位名称", "职位", "职位名称")
_SEPARATOR_LINE = re.compile(r"(?m)^\s*(?:-{3,}|—{3,}|={3,})\s*$")


@dataclass(frozen=True)
class JdItem:
    """一条待分析的 JD。"""

    text: str
    title: str = ""


@dataclass(frozen=True)
class JdBatchResult:
    """批量分析中的一条结果；``error`` 非空表示该条分析失败。"""

    index: int
    title: str
    nature: str
    water: int
    error: str | None = None
    cached: bool = False


# 「画饼」关键词及权重，用于本地估算 JD 的水分指数
WATER_KEYWORDS: dict[str, int] = {
    "躺赚": 25,
    "暴富": 25,
    "年薪百万": 20,
    "年薪四十万": 18,
    "月入过万": 15,
    "月薪过万": 15,
    "画饼": 15,
    "上不封顶": 12,
    "不是梦": 10,
    "不看出身": 10,
    "狼性": 10,
    "轻松": 8,
    "大量招人": 8,
    "不限学历": 8,
    "无经验": 8,
    "996": 8,
    "大小周": 8,
    "包吃住": 6,
    "单休": 6,
    "提成": 6,
    "急招": 5,
    "老板nice": 5,
    "底薪": 4,
    "抗压": 4,
    "氛围好": 4,
    "团队年轻": 3,
}

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
    """调用 DeepSeek API 或解析结果时发生的错误。

    ``retryable`` 为 True 时，批量流水线会对该条 JD 做指数退避重试。
    """

    def __init__(self, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


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
        raise JdDetectorError(
            f"DeepSeek API 返回 HTTP {exc.code}{suffix}",
            retryable=exc.code in _RETRYABLE_HTTP_STATUS,
        ) from exc
    except urllib.error.URLError as exc:
        raise JdDetectorError(f"无法连接 DeepSeek API：{exc.reason}", retryable=True) from exc
    except TimeoutError as exc:
        raise JdDetectorError(
            f"请求 DeepSeek API 超时（{timeout:g} 秒）",
            retryable=True,
        ) from exc
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


def estimate_water_index(text: str) -> int:
    """用关键词规则估算 JD 的水分指数（0-100，越高越像在画饼）。"""
    normalized = text.lower()
    score = sum(weight for keyword, weight in WATER_KEYWORDS.items() if keyword in normalized)
    return max(0, min(100, score))


def split_jds(text: str) -> list[str]:
    """把长文本按连续空行或 ``---`` 分隔符切割成 JD 列表。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
    chunks: list[str] = []
    for block in _SEPARATOR_LINE.split(normalized):
        for part in re.split(r"\n[ \t]*\n", block):
            cleaned = part.strip()
            if cleaned:
                chunks.append(cleaned)
    return chunks


def short_title(text: str, title: str = "", index: int = 1) -> str:
    """取岗位简称：优先显式标题，否则取 JD 第一行；超长截断。"""
    candidate = (title or "").strip()
    if not candidate:
        for line in text.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                candidate = stripped
                break
    candidate = re.sub(r"^(?:岗位|职位|标题)[：:]\s*", "", candidate).strip()
    if not candidate:
        return f"JD {index}"
    if len(candidate) > 20:
        candidate = candidate[:20] + "…"
    return candidate


def load_file(path: Path) -> list[JdItem]:
    """读取 .txt 或 .csv 文件，返回待分析的 JD 列表。"""
    if not path.exists():
        raise JdDetectorError(f"文件不存在：{path}")
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise JdDetectorError(f"读取文件失败：{exc}") from exc
    return load_bytes(path.name, data)


def load_bytes(filename: str, data: bytes) -> list[JdItem]:
    """从内存字节解析 .txt 或 .csv（GUI 上传文件也复用这里）。"""
    suffix = Path(filename).suffix.lower()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise JdDetectorError(f"文件不是合法的 UTF-8 文本：{exc}") from exc
    if suffix == ".csv":
        return _parse_csv(text)
    if suffix != ".txt":
        shown = suffix or "无扩展名"
        raise JdDetectorError(f"仅支持 .txt 或 .csv 文件，收到 {shown}")
    return [JdItem(text=chunk) for chunk in split_jds(text)]


def _parse_csv(text: str) -> list[JdItem]:
    try:
        reader = csv.DictReader(io.StringIO(text))
        if not reader.fieldnames:
            raise JdDetectorError("CSV 文件缺少表头")
        columns = {name.strip().lower(): name for name in reader.fieldnames}
        text_column = next((columns[key] for key in _TEXT_COLUMNS if key in columns), None)
        title_column = next(
            (columns[key] for key in _TITLE_COLUMNS if key in columns),
            None,
        )
        items: list[JdItem] = []
        for row in reader:
            if text_column is not None:
                row_text = str(row.get(text_column) or "").strip()
            else:
                row_text = " ".join(
                    str(value).strip() for value in row.values() if value and str(value).strip()
                )
            if not row_text:
                continue
            title = str(row.get(title_column) or "").strip() if title_column else ""
            items.append(JdItem(text=row_text, title=title))
        return items
    except csv.Error as exc:
        raise JdDetectorError(f"CSV 解析失败：{exc}") from exc


def _cache_key(text: str, model: str) -> str:
    return hashlib.sha256(f"{model}\0{text}".encode()).hexdigest()


def _load_cache(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        key: value
        for key, value in data.items()
        if isinstance(key, str) and isinstance(value, dict) and "is_sales" in value
    }


def _save_cache(path: Path | None, cache: dict[str, dict[str, Any]]) -> None:
    if path is None:
        return
    try:
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        return  # 缓存写入失败不影响主流程


def _cached_result(
    cache: dict[str, dict[str, Any]],
    item: JdItem,
    index: int,
    model: str,
) -> JdBatchResult | None:
    value = cache.get(_cache_key(item.text, model))
    if not isinstance(value, dict) or not isinstance(value.get("is_sales"), bool):
        return None
    nature = "销售/地推" if value["is_sales"] else "非销售/地推"
    return JdBatchResult(
        index,
        short_title(item.text, item.title, index),
        nature,
        estimate_water_index(item.text),
        None,
        True,
    )


def _classify_with_retry(
    item: JdItem,
    *,
    api_key: str,
    model: str,
    base_url: str,
    timeout: float,
    retries: int,
    retry_delay: float,
) -> tuple[dict[str, Any] | None, str | None]:
    attempts = max(1, retries + 1)
    for attempt in range(attempts):
        try:
            result = classify(
                item.text,
                api_key=api_key,
                model=model,
                base_url=base_url,
                timeout=timeout,
            )
        except JdDetectorError as exc:
            if not exc.retryable or attempt >= attempts - 1:
                return None, str(exc)
            if retry_delay > 0:
                time.sleep(retry_delay * (2**attempt))
        else:
            return result, None
    return None, "未知错误"  # pragma: no cover


def analyze_batch(
    items: list[JdItem],
    *,
    api_key: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    workers: int = 1,
    retries: int = 0,
    retry_delay: float = 1.0,
    cache_path: Path | None = None,
    use_cache: bool = False,
    on_progress: Callable[[int, int], None] | None = None,
) -> list[JdBatchResult]:
    """逐条分析 JD；单条失败只记录“分析失败”，不中断整批。"""
    workers = max(1, min(workers, 16))
    results: list[JdBatchResult | None] = [None] * len(items)
    cache = _load_cache(cache_path) if use_cache else {}
    pending: list[tuple[int, JdItem]] = []
    for offset, item in enumerate(items):
        cached = _cached_result(cache, item, offset + 1, model) if cache else None
        if cached is None:
            pending.append((offset, item))
        else:
            results[offset] = cached

    done = len(items) - len(pending)
    if on_progress is not None:
        on_progress(done, len(items))

    if pending:

        def work(
            offset: int, item: JdItem
        ) -> tuple[int, JdItem, dict[str, Any] | None, str | None]:
            result, error = _classify_with_retry(
                item,
                api_key=api_key,
                model=model,
                base_url=base_url,
                timeout=timeout,
                retries=retries,
                retry_delay=retry_delay,
            )
            return offset, item, result, error

        with ThreadPoolExecutor(max_workers=min(workers, len(pending))) as executor:
            futures = [executor.submit(work, offset, item) for offset, item in pending]
            for future in as_completed(futures):
                offset, item, result, error = future.result()
                index = offset + 1
                title = short_title(item.text, item.title, index)
                water = estimate_water_index(item.text)
                if error is not None or result is None:
                    results[offset] = JdBatchResult(index, title, "分析失败", water, error)
                else:
                    nature = "销售/地推" if result["is_sales"] else "非销售/地推"
                    results[offset] = JdBatchResult(index, title, nature, water)
                    if use_cache and cache_path is not None:
                        cache[_cache_key(item.text, model)] = result
                done += 1
                if on_progress is not None:
                    on_progress(done, len(items))

    if use_cache:
        _save_cache(cache_path, cache)
    return [result for result in results if result is not None]


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def render_markdown_table(results: list[JdBatchResult]) -> str:
    """把批量结果渲染为 Markdown 表格。"""
    lines = [
        "| 序号 | 岗位简称 | 岗位性质 | 水分指数 |",
        "| --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result.index} | {_escape_cell(result.title)} | "
            f"{_escape_cell(result.nature)} | {result.water}/100 |"
        )
    return "\n".join(lines)


def render_dry_run(items: list[JdItem]) -> str:
    """渲染 --dry-run 预览：只展示切割结果和本地水分指数。"""
    lines = [
        f"将分析 {len(items)} 条 JD（--dry-run，未调用 API）：",
        "",
        "| 序号 | 岗位简称 | 水分指数 |",
        "| --- | --- | --- |",
    ]
    for index, item in enumerate(items, start=1):
        title = _escape_cell(short_title(item.text, item.title, index))
        lines.append(f"| {index} | {title} | {estimate_water_index(item.text)}/100 |")
    return "\n".join(lines)


def _excel_safe(value: str) -> str:
    """防止 CSV 注入：Excel 会把 = + - @ 开头的单元格当公式执行。"""
    if value.lstrip().startswith(_EXCEL_FORMULA_PREFIXES):
        return "'" + value
    return value


def report_csv_bytes(results: list[JdBatchResult]) -> bytes:
    """返回可直接下载/写入的 report.csv 内容（UTF-8 BOM）。"""
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(REPORT_COLUMNS)
    writer.writerows(
        (result.index, _excel_safe(result.title), result.nature, f"{result.water}/100")
        for result in results
    )
    return buffer.getvalue().encode("utf-8-sig")


def write_report_csv(results: list[JdBatchResult], path: Path) -> Path:
    """把批量结果写成 Excel 友好的 UTF-8 BOM CSV。"""
    try:
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(report_csv_bytes(results))
    except OSError as exc:
        raise JdDetectorError(f"写入报告失败：{exc}") from exc
    return path


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
    help = "调用 DeepSeek API 判断职位描述是否为销售/地推岗位（支持批量）"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "text",
            nargs="?",
            default=None,
            help="职位描述文本；省略时从标准输入读取（也可用 --file 批量分析）",
        )
        parser.add_argument(
            "-f",
            "--file",
            type=Path,
            default=None,
            help="读取 .txt 或 .csv 文件并批量分析（txt 按空行或 --- 切割）",
        )
        parser.add_argument(
            "--report",
            type=Path,
            default=Path(REPORT_FILENAME),
            help=f"批量分析的 CSV 报告路径，默认 {REPORT_FILENAME}",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=DEFAULT_WORKERS,
            metavar="N",
            help=f"批量分析并发数（1-16），默认 {DEFAULT_WORKERS}",
        )
        parser.add_argument(
            "--retries",
            type=int,
            default=DEFAULT_RETRIES,
            metavar="N",
            help=f"可重试错误（超时/429/5xx）的重试次数，默认 {DEFAULT_RETRIES}",
        )
        parser.add_argument(
            "--retry-delay",
            type=float,
            default=1.0,
            metavar="SECONDS",
            help="指数退避的基准等待秒数，默认 1.0",
        )
        parser.add_argument(
            "--cache",
            type=Path,
            default=DEFAULT_CACHE_PATH,
            help=f"批量结果缓存路径，默认 {DEFAULT_CACHE_PATH}",
        )
        parser.add_argument("--no-cache", action="store_true", help="禁用批量结果缓存")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="只切割文件并预览将分析的 JD，不调用 API",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            metavar="N",
            help="只分析前 N 条 JD",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="单条模式下以 JSON 格式输出判断结果",
        )
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
        if args.file is not None:
            return self._run_batch(args)
        try:
            text = read_input(args.text, None)
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

    def _run_batch(self, args: argparse.Namespace) -> int:
        """批量模式：读取文件、逐条分析、打印表格并写出 report.csv。"""
        if args.text is not None:
            print("错误：不能同时指定文本参数和 --file", file=sys.stderr)
            return 1
        if not 1 <= args.workers <= 16:
            print("错误：--workers 必须在 1-16 之间", file=sys.stderr)
            return 2
        if args.retries < 0:
            print("错误：--retries 不能为负数", file=sys.stderr)
            return 2
        if args.retry_delay < 0:
            print("错误：--retry-delay 不能为负数", file=sys.stderr)
            return 2
        if args.limit is not None and args.limit <= 0:
            print("错误：--limit 必须大于 0", file=sys.stderr)
            return 2
        try:
            items = load_file(args.file)
        except JdDetectorError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        if args.limit is not None:
            items = items[: args.limit]
        if not items:
            print("错误：文件中没有可分析的 JD", file=sys.stderr)
            return 1
        if args.dry_run:
            print(render_dry_run(items))
            return 0

        api_key = os.environ.get(API_KEY_ENV, "").strip()
        if not api_key:
            print(f"错误：未设置环境变量 {API_KEY_ENV}", file=sys.stderr)
            return 1

        results = analyze_batch(
            items,
            api_key=api_key,
            model=args.model,
            base_url=args.base_url,
            timeout=args.timeout,
            workers=args.workers,
            retries=args.retries,
            retry_delay=args.retry_delay,
            cache_path=None if args.no_cache else args.cache,
            use_cache=not args.no_cache,
        )
        print(render_markdown_table(results))
        succeeded = sum(1 for result in results if result.error is None)
        failed = len(results) - succeeded
        summary = f"共 {len(results)} 条：成功 {succeeded} 条，失败 {failed} 条"
        cached = sum(1 for result in results if result.cached)
        if cached:
            summary += f"（缓存命中 {cached} 条）"
        print(f"\n{summary}")
        try:
            report = write_report_csv(results, args.report)
        except JdDetectorError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        print(f"报告已写入：{report.resolve()}")
        return 0
