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


def _markdown_text(app: AppTest) -> str:
    return " ".join(element.value for element in app.markdown)


def test_app_renders_masthead_tabs_and_buttons() -> None:
    app = _run_app()
    assert not app.exception
    text = _markdown_text(app)
    assert "MYAITOOLS" in text
    assert "<h1" in text
    assert "Catalogue 002" in text
    assert [tab.label for tab in app.tabs] == ["系统雷达", "JD 脱水器"]
    assert [button.label for button in app.button] == ["采集读数", "开始脱水"]


def test_sys_radar_empty_state() -> None:
    app = _run_app()
    assert "尚无读数" in _markdown_text(app)


def test_dark_mode_toggle_switches_palette() -> None:
    app = _run_app()
    assert "--ground: #e8e8e6" in _markdown_text(app)
    app.toggle[0].set_value(True).run()
    assert not app.exception
    assert "--ground: #12100c" in _markdown_text(app)


def test_sys_radar_button_shows_readout() -> None:
    app = _run_app()
    app.button[0].click().run()
    assert not app.exception
    text = _markdown_text(app)
    assert "CPU 使用率" in text
    assert "内存使用率" in text
    assert "磁盘" in text
    assert "读数记录" in text


def test_jd_detector_empty_state() -> None:
    app = _run_app()
    assert "尚无判定" in _markdown_text(app)


def test_jd_detector_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    app = _run_app()
    app.text_area[0].set_value("招聘地推专员")
    app.button[1].click().run()
    assert not app.exception
    assert "DeepSeek API Key" in _markdown_text(app)


def test_jd_detector_renders_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def fake_classify(text: str, **kwargs: object) -> dict[str, object]:
        return {"is_sales": True, "confidence": 0.98, "reason": "地推岗位"}

    monkeypatch.setattr(jd_detector, "classify", fake_classify)

    app = _run_app()
    app.text_area[0].set_value("招聘地推专员，单休，底薪3000，年薪四十万不是梦")
    app.button[1].click().run()
    assert not app.exception
    text = _markdown_text(app)
    assert "销售 / 地推" in text
    assert "98%" in text
    assert "水分指数" in text
    assert ">38<" in text
    assert "地推岗位" in text
    assert "略有水分" in text
