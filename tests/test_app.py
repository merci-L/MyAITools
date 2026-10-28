"""Streamlit 图形界面的冒烟测试（不启动真实服务）。"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from myaitools.tools import jd_detector

APP_PATH = Path(__file__).resolve().parents[1] / "src" / "myaitools" / "app.py"


def _run_app() -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.run()
    return app


def test_app_renders_title_tabs_and_buttons() -> None:
    app = _run_app()
    assert not app.exception
    assert app.title[0].value == "MyAITools"
    assert [tab.label for tab in app.tabs] == ["系统雷达", "JD 脱水器"]
    assert [button.label for button in app.button] == ["开始检测", "开始脱水"]


def test_sys_radar_button_shows_metrics() -> None:
    app = _run_app()
    app.button[0].click().run()
    assert not app.exception
    labels = [metric.label for metric in app.metric]
    assert "CPU 使用率" in labels
    assert "内存使用率" in labels


def test_jd_detector_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    app = _run_app()
    app.text_area[0].set_value("招聘地推专员")
    app.button[1].click().run()
    assert not app.exception
    assert any("DeepSeek API Key" in error.value for error in app.error)


def test_jd_detector_renders_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        return {"is_sales": True, "confidence": 0.98, "reason": "地推岗位"}

    monkeypatch.setattr(jd_detector, "classify", fake_classify)

    app = _run_app()
    app.text_area[0].set_value("招聘地推专员，单休，底薪3000，年薪四十万不是梦")
    app.button[1].click().run()
    assert not app.exception
    values = {metric.label: metric.value for metric in app.metric}
    assert values["结论"] == "是销售/地推岗位"
    assert values["置信度"] == "98%"
    assert "38" in str(values["水分指数"])
    assert "地推岗位" in " ".join(info.value for info in app.info)
