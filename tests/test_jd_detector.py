"""jd-detector 工具的测试（全部使用 mock，不调用真实 API）。"""

from __future__ import annotations

import io
import json
import urllib.error
from pathlib import Path

import pytest

from myaitools.cli import main
from myaitools.tools import jd_detector

FAKE_RESULT = {"is_sales": True, "confidence": 0.92, "reason": "职责以地推拉新为主"}
FAKE_CONTENT = json.dumps(FAKE_RESULT, ensure_ascii=False)


class _FakeTty:
    """模拟交互式终端：isatty() 为 True。"""

    def isatty(self) -> bool:
        return True


def _patch_completion(monkeypatch: pytest.MonkeyPatch, content: str = FAKE_CONTENT) -> None:
    def fake_request_completion(text: str, **kwargs: object) -> str:
        assert "地推" in text
        return content

    monkeypatch.setattr(jd_detector, "request_completion", fake_request_completion)


def test_build_messages_includes_text_and_schema() -> None:
    messages = jd_detector.build_messages("负责商圈地推")
    assert messages[0]["role"] == "system"
    assert "JSON" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "职位描述：\n负责商圈地推"}


def test_parse_classification_plain_json() -> None:
    assert jd_detector.parse_classification(FAKE_CONTENT) == FAKE_RESULT


def test_parse_classification_strips_code_fence() -> None:
    content = f"```json\n{FAKE_CONTENT}\n```"
    assert jd_detector.parse_classification(content) == FAKE_RESULT


def test_parse_classification_normalizes_string_values() -> None:
    content = '{"is_sales": "是", "confidence": "0.7", "reason": "地推"}'
    assert jd_detector.parse_classification(content) == {
        "is_sales": True,
        "confidence": 0.7,
        "reason": "地推",
    }


def test_parse_classification_clamps_confidence() -> None:
    content = '{"is_sales": false, "confidence": 1.5, "reason": ""}'
    result = jd_detector.parse_classification(content)
    assert result["confidence"] == 1.0
    assert result["reason"] == ""


def test_parse_classification_without_json_raises() -> None:
    with pytest.raises(jd_detector.JdDetectorError, match="JSON"):
        jd_detector.parse_classification("我觉得这是销售岗位")


def test_parse_classification_missing_is_sales_raises() -> None:
    with pytest.raises(jd_detector.JdDetectorError, match="is_sales"):
        jd_detector.parse_classification('{"confidence": 0.5, "reason": "x"}')


def test_render_text_sales() -> None:
    text = jd_detector.render_text(FAKE_RESULT)
    assert "是销售/地推岗位" in text
    assert "92%" in text
    assert "地推拉新" in text


def test_render_text_non_sales_without_confidence() -> None:
    text = jd_detector.render_text({"is_sales": False, "confidence": None, "reason": ""})
    assert "不是销售/地推岗位" in text
    assert "置信度" not in text


def test_render_json_round_trip() -> None:
    assert json.loads(jd_detector.render_json(FAKE_RESULT)) == FAKE_RESULT


def test_request_completion_builds_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(
        url: str,
        payload: dict[str, object],
        api_key: str,
        timeout: float,
    ) -> dict[str, object]:
        captured.update(url=url, payload=payload, api_key=api_key, timeout=timeout)
        return {"choices": [{"message": {"content": FAKE_CONTENT}}]}

    monkeypatch.setattr(jd_detector, "_post_json", fake_post)
    content = jd_detector.request_completion("负责地推", api_key="secret")

    assert captured["url"] == "https://api.deepseek.com/chat/completions"
    assert captured["api_key"] == "secret"
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "deepseek-chat"
    assert payload["response_format"] == {"type": "json_object"}
    assert content == FAKE_CONTENT


def test_request_completion_wraps_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args: object, **kwargs: object) -> dict[str, object]:
        raise urllib.error.URLError("network down")

    monkeypatch.setattr(jd_detector, "_post_json", fake_post)
    with pytest.raises(jd_detector.JdDetectorError, match="无法连接"):
        jd_detector.request_completion("负责地推", api_key="secret")


def test_cli_classify_from_argument(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    _patch_completion(monkeypatch)

    assert main(["jd-detector", "招聘地推专员，负责商圈拉新"]) == 0
    out = capsys.readouterr().out
    assert "是销售/地推岗位" in out
    assert "92%" in out
    assert "地推拉新" in out


def test_cli_json_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    _patch_completion(monkeypatch)

    assert main(["jd-detector", "招聘地推专员", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == FAKE_RESULT


def test_cli_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("sys.stdin", io.StringIO("负责商圈地推"))
    _patch_completion(monkeypatch)

    assert main(["jd-detector"]) == 0
    assert "是销售/地推岗位" in capsys.readouterr().out


def test_cli_reads_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    _patch_completion(monkeypatch)
    jd_file = tmp_path / "jd.txt"
    jd_file.write_text("招聘地推专员，负责拉新", encoding="utf-8")

    assert main(["jd-detector", "--file", str(jd_file)]) == 0
    assert "是销售/地推岗位" in capsys.readouterr().out


def test_cli_missing_api_key(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(
        jd_detector,
        "request_completion",
        lambda *args, **kwargs: pytest.fail("缺少 Key 时不应调用 API"),
    )

    assert main(["jd-detector", "招聘地推专员"]) == 1
    assert "DEEPSEEK_API_KEY" in capsys.readouterr().err


def test_cli_reports_api_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def boom(*args: object, **kwargs: object) -> str:
        raise jd_detector.JdDetectorError("HTTP 401")

    monkeypatch.setattr(jd_detector, "request_completion", boom)

    assert main(["jd-detector", "招聘地推专员"]) == 1
    err = capsys.readouterr().err
    assert "错误" in err
    assert "HTTP 401" in err


def test_cli_requires_input(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr("sys.stdin", _FakeTty())

    assert main(["jd-detector"]) == 1
    assert "请提供职位描述" in capsys.readouterr().err


def test_cli_rejects_text_and_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    assert main(["jd-detector", "招聘地推专员", "--file", str(tmp_path / "jd.txt")]) == 1
    assert "不能同时指定" in capsys.readouterr().err


def test_cli_rejects_empty_text(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    assert main(["jd-detector", "   "]) == 1
    assert "内容为空" in capsys.readouterr().err


def test_cli_rejects_negative_timeout(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    assert main(["jd-detector", "招聘地推专员", "--timeout", "-1"]) == 2
    assert "必须大于 0" in capsys.readouterr().err


def test_estimate_water_index_flags_buzzwords() -> None:
    text = "招聘地推专员，要求吃苦耐劳，单休，底薪3000，年薪四十万不是梦"
    assert jd_detector.estimate_water_index(text) >= 30


def test_estimate_water_index_clean_jd() -> None:
    text = "负责后端服务开发，要求三年以上 Python 经验，熟悉分布式系统"
    assert jd_detector.estimate_water_index(text) < 10


def test_estimate_water_index_caps_at_100() -> None:
    text = "躺赚 暴富 年薪百万 月入过万 上不封顶 不是梦 画饼"
    assert jd_detector.estimate_water_index(text) == 100
