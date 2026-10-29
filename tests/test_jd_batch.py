"""jd-detector 批量流水线的测试（全部 mock，不调用真实 API）。"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from myaitools.cli import main
from myaitools.tools import jd_detector

FAKE_SALES = {"is_sales": True, "confidence": 0.9, "reason": "销售职责"}
FAKE_OTHER = {"is_sales": False, "confidence": 0.8, "reason": "研发职责"}


def test_split_by_blank_lines() -> None:
    text = "第一条 JD\n继续第一句\n\n第二条 JD\n\n\n第三条"
    assert jd_detector.split_jds(text) == ["第一条 JD\n继续第一句", "第二条 JD", "第三条"]


def test_split_by_separator_lines() -> None:
    text = "第一条\n---\n第二条\n\n第三条"
    assert jd_detector.split_jds(text) == ["第一条", "第二条", "第三条"]


def test_split_handles_crlf_and_windows_line_endings() -> None:
    assert jd_detector.split_jds("a\r\n\r\nb\r\n---\r\nc") == ["a", "b", "c"]


def test_split_ignores_empty_text() -> None:
    assert jd_detector.split_jds("\r\n\r\n  \r\n") == []


def test_load_txt_file(tmp_path: Path) -> None:
    path = tmp_path / "jds.txt"
    path.write_text("第一条\n\n第二条", encoding="utf-8")
    items = jd_detector.load_file(path)
    assert [item.text for item in items] == ["第一条", "第二条"]


def test_load_csv_uses_title_and_description(tmp_path: Path) -> None:
    path = tmp_path / "jds.csv"
    path.write_text(
        "岗位,职位描述\n地推专员,负责商圈拉新\n后端开发,负责服务端开发\n",
        encoding="utf-8",
    )
    items = jd_detector.load_file(path)
    assert [(item.title, item.text) for item in items] == [
        ("地推专员", "负责商圈拉新"),
        ("后端开发", "负责服务端开发"),
    ]


def test_load_csv_falls_back_to_all_columns(tmp_path: Path) -> None:
    path = tmp_path / "jds.csv"
    path.write_text("公司,备注\nA 公司,第一条\nB 公司,第二条\n", encoding="utf-8")
    items = jd_detector.load_file(path)
    assert items[0].text == "A 公司 第一条"


def test_load_csv_rejects_missing_header(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")
    with pytest.raises(jd_detector.JdDetectorError, match="表头"):
        jd_detector.load_file(path)


def test_load_unsupported_suffix(tmp_path: Path) -> None:
    path = tmp_path / "jds.md"
    path.write_text("x", encoding="utf-8")
    with pytest.raises(jd_detector.JdDetectorError, match=r"\.txt"):
        jd_detector.load_file(path)


def test_load_missing_file(tmp_path: Path) -> None:
    with pytest.raises(jd_detector.JdDetectorError, match="不存在"):
        jd_detector.load_file(tmp_path / "missing.txt")


def test_short_title_prefers_explicit_title() -> None:
    assert jd_detector.short_title("正文", "地推专员", 1) == "地推专员"


def test_short_title_derives_from_first_line() -> None:
    assert jd_detector.short_title("# 招聘地推专员\n正文", "", 1) == "招聘地推专员"


def test_short_title_truncates_long_line() -> None:
    title = jd_detector.short_title("招聘地推专员负责商圈拉新扫码注册客户开拓团队", "", 1)
    assert len(title) == 21
    assert title.endswith("…")


def test_analyze_batch_continues_after_error(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        calls.append(text)
        if "坏" in text:
            raise jd_detector.JdDetectorError("HTTP 500")
        return FAKE_SALES if "销售" in text else FAKE_OTHER

    monkeypatch.setattr(jd_detector, "classify", fake_classify)
    items = [
        jd_detector.JdItem("销售岗"),
        jd_detector.JdItem("坏数据"),
        jd_detector.JdItem("研发岗"),
    ]

    results = jd_detector.analyze_batch(items, api_key="k")

    assert [result.nature for result in results] == ["销售/地推", "分析失败", "非销售/地推"]
    assert results[1].error == "HTTP 500"
    assert [result.index for result in results] == [1, 2, 3]
    assert len(calls) == 3


def test_render_markdown_table_escapes_pipes() -> None:
    results = [jd_detector.JdBatchResult(1, "a|b", "分析失败", 42, "boom")]
    table = jd_detector.render_markdown_table(results)
    assert "| 1 | a\\|b | 分析失败 | 42/100 |" in table


def test_write_report_csv(tmp_path: Path) -> None:
    results = [jd_detector.JdBatchResult(1, "地推专员", "销售/地推", 38)]
    path = tmp_path / "report.csv"

    jd_detector.write_report_csv(results, path)

    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[0] == list(jd_detector.REPORT_COLUMNS)
    assert rows[1] == ["1", "地推专员", "销售/地推", "38/100"]


def _set_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")


def test_cli_batch_txt(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    _set_key(monkeypatch)
    monkeypatch.setattr(jd_detector, "classify", lambda *args, **kwargs: FAKE_SALES)
    jd_file = tmp_path / "jds.txt"
    jd_file.write_text("地推专员，负责拉新\n\n研发工程师，负责开发", encoding="utf-8")
    report = tmp_path / "report.csv"

    assert (
        main(
            [
                "jd-detector",
                "--file",
                str(jd_file),
                "--report",
                str(report),
                "--no-cache",
            ]
        )
        == 0
    )

    out = capsys.readouterr().out
    assert "| 序号 | 岗位简称 | 岗位性质 | 水分指数 |" in out
    assert "共 2 条：成功 2 条，失败 0 条" in out
    assert report.exists()


def test_cli_batch_partial_failure(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    _set_key(monkeypatch)

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        if "坏" in text:
            raise jd_detector.JdDetectorError("请求超时")
        return FAKE_SALES

    monkeypatch.setattr(jd_detector, "classify", fake_classify)
    jd_file = tmp_path / "jds.txt"
    jd_file.write_text("地推专员\n\n坏数据\n\n另一个地推专员", encoding="utf-8")
    report = tmp_path / "report.csv"

    assert (
        main(
            [
                "jd-detector",
                "--file",
                str(jd_file),
                "--report",
                str(report),
                "--no-cache",
            ]
        )
        == 0
    )

    out = capsys.readouterr().out
    assert "分析失败" in out
    assert "成功 2 条，失败 1 条" in out
    with report.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[2][2] == "分析失败"
    assert "请求超时" not in ",".join(rows[2])


def test_cli_batch_csv(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    _set_key(monkeypatch)
    monkeypatch.setattr(
        jd_detector,
        "classify",
        lambda text, **kwargs: FAKE_SALES if "销售" in text else FAKE_OTHER,
    )
    csv_file = tmp_path / "jds.csv"
    csv_file.write_text(
        "岗位,职位描述\n销售代表,负责渠道销售\n后端工程师,负责服务端开发\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.csv"

    assert (
        main(
            [
                "jd-detector",
                "--file",
                str(csv_file),
                "--report",
                str(report),
                "--no-cache",
            ]
        )
        == 0
    )

    out = capsys.readouterr().out
    assert "销售代表" in out
    assert "后端工程师" in out
    with report.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    assert rows[1][2] == "销售/地推"
    assert rows[2][2] == "非销售/地推"


def test_cli_batch_empty_file(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    _set_key(monkeypatch)
    jd_file = tmp_path / "empty.txt"
    jd_file.write_text("\n\n", encoding="utf-8")

    assert main(["jd-detector", "--file", str(jd_file)]) == 1
    assert "没有可分析的 JD" in capsys.readouterr().err


def test_cli_batch_unsupported_file(tmp_path: Path, capsys) -> None:
    path = tmp_path / "jds.md"
    path.write_text("x", encoding="utf-8")

    assert main(["jd-detector", "--file", str(path)]) == 1
    assert "仅支持" in capsys.readouterr().err


def test_cli_batch_rejects_text_and_file(tmp_path: Path, capsys) -> None:
    path = tmp_path / "jds.txt"
    path.write_text("x", encoding="utf-8")

    assert main(["jd-detector", "文本", "--file", str(path)]) == 1
    assert "不能同时指定" in capsys.readouterr().err


def test_load_bytes_txt_and_csv() -> None:
    txt_items = jd_detector.load_bytes("a.txt", "一\n\n二".encode())
    assert [item.text for item in txt_items] == ["一", "二"]

    csv_items = jd_detector.load_bytes("a.csv", "岗位,职位描述\n地推,负责拉新\n".encode())
    assert [(item.title, item.text) for item in csv_items] == [("地推", "负责拉新")]


def test_load_bytes_rejects_invalid_utf8() -> None:
    with pytest.raises(jd_detector.JdDetectorError, match="UTF-8"):
        jd_detector.load_bytes("a.txt", b"\xff\xfe\x00")


def test_report_csv_escapes_formula_cells() -> None:
    results = [jd_detector.JdBatchResult(1, "=SUM(A1)", "销售/地推", 10)]
    content = jd_detector.report_csv_bytes(results).decode("utf-8-sig")
    assert "'=SUM(A1)" in content


def test_analyze_batch_retries_retryable_error(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = {"count": 0}

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        calls["count"] += 1
        if calls["count"] < 3:
            raise jd_detector.JdDetectorError("超时", retryable=True)
        return FAKE_SALES

    monkeypatch.setattr(jd_detector, "classify", fake_classify)
    results = jd_detector.analyze_batch(
        [jd_detector.JdItem("销售岗")],
        api_key="k",
        retries=2,
        retry_delay=0,
    )

    assert results[0].nature == "销售/地推"
    assert calls["count"] == 3


def test_analyze_batch_does_not_retry_permanent_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"count": 0}

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        calls["count"] += 1
        raise jd_detector.JdDetectorError("HTTP 401")

    monkeypatch.setattr(jd_detector, "classify", fake_classify)
    results = jd_detector.analyze_batch(
        [jd_detector.JdItem("销售岗")],
        api_key="k",
        retries=2,
        retry_delay=0,
    )

    assert results[0].nature == "分析失败"
    assert calls["count"] == 1


def test_analyze_batch_uses_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = {"count": 0}

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        calls["count"] += 1
        return FAKE_SALES

    monkeypatch.setattr(jd_detector, "classify", fake_classify)
    cache = tmp_path / "cache.json"
    items = [jd_detector.JdItem("销售岗")]

    first = jd_detector.analyze_batch(items, api_key="k", cache_path=cache, use_cache=True)
    second = jd_detector.analyze_batch(items, api_key="k", cache_path=cache, use_cache=True)

    assert first[0].cached is False
    assert second[0].cached is True
    assert calls["count"] == 1


def test_analyze_batch_preserves_order_with_workers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(jd_detector, "classify", lambda *args, **kwargs: FAKE_SALES)
    items = [jd_detector.JdItem(f"销售岗 {number}") for number in range(5)]

    results = jd_detector.analyze_batch(items, api_key="k", workers=4)

    assert [result.index for result in results] == [1, 2, 3, 4, 5]
    assert all(result.nature == "销售/地推" for result in results)


def test_cli_batch_dry_run_skips_api(
    monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        jd_detector,
        "classify",
        lambda *args, **kwargs: pytest.fail("dry-run 不应调用 API"),
    )
    jd_file = tmp_path / "jds.txt"
    jd_file.write_text("地推专员\n\n后端工程师", encoding="utf-8")

    assert main(["jd-detector", "--file", str(jd_file), "--dry-run"]) == 0

    out = capsys.readouterr().out
    assert "将分析 2 条 JD" in out
    assert "--dry-run" in out


def test_cli_batch_limit(monkeypatch: pytest.MonkeyPatch, capsys, tmp_path: Path) -> None:
    _set_key(monkeypatch)
    monkeypatch.setattr(jd_detector, "classify", lambda *args, **kwargs: FAKE_SALES)
    jd_file = tmp_path / "jds.txt"
    jd_file.write_text("地推专员\n\n另一个地推专员", encoding="utf-8")
    report = tmp_path / "report.csv"

    assert (
        main(
            [
                "jd-detector",
                "--file",
                str(jd_file),
                "--limit",
                "1",
                "--no-cache",
                "--report",
                str(report),
            ]
        )
        == 0
    )

    out = capsys.readouterr().out
    assert "共 1 条" in out
    with report.open(encoding="utf-8-sig", newline="") as handle:
        assert len(list(csv.reader(handle))) == 2
