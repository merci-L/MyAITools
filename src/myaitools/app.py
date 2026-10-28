"""MyAITools 的极简 Web 界面（Streamlit）。

视觉世界：精密档案卡 / 卡片目录。
本地启动：

    streamlit run src/myaitools/app.py
"""

from __future__ import annotations

import html
import os
from datetime import datetime
from typing import Any

import streamlit as st

from myaitools import __version__
from myaitools.tools import jd_detector, sys_radar

_LIGHT_PALETTE = {
    "ground": "#efebe1",
    "sheet": "#f9f6ec",
    "ink": "#20201d",
    "muted": "#676254",
    "rule": "#d6d0c0",
    "accent": "#a63d2f",
    "ok": "#4f6b4f",
    "caution": "#9a6b1f",
    "ochre-water": "#b07d2e",
    "sidebar": "#e9e4d7",
    "gauge-track": "#e6e0d1",
    "scrollbar": "#c9c2b0",
}

_DARK_PALETTE = {
    "ground": "#12100c",
    "sheet": "#1d1a14",
    "ink": "#ece5d6",
    "muted": "#a49b87",
    "rule": "#3a352b",
    "accent": "#e0765f",
    "ok": "#86a882",
    "caution": "#cfa055",
    "ochre-water": "#c08a48",
    "sidebar": "#17140f",
    "gauge-track": "#2a261e",
    "scrollbar": "#403b30",
}

_FONT_TOKENS = (
    '  --font-ui: "Segoe UI", "Microsoft YaHei", "PingFang SC", '
    '"Hiragino Sans GB", "Noto Sans SC", sans-serif;\n'
    '  --font-mono: "Cascadia Mono", "Cascadia Code", Consolas, '
    '"SFMono-Regular", Menlo, "DejaVu Sans Mono", monospace;\n'
)


def _palette_css(dark: bool) -> str:
    """返回当前外观的 CSS 变量块。"""
    palette = _DARK_PALETTE if dark else _LIGHT_PALETTE
    lines = "\n".join(f"  --{name}: {value};" for name, value in palette.items())
    return f"<style>\n:root {{\n{lines}\n{_FONT_TOKENS}}}\n"


_CSS_BODY = """

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--ground);
  color: var(--ink);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: flex !important; background: transparent; }
[data-testid="stAppDeployButton"], [data-testid="stMainMenu"], #MainMenu, footer {
  display: none !important;
}
[data-testid="stExpandSidebarButton"] { display: flex !important; color: var(--ink) !important; }
[data-testid="stExpandSidebarButton"] span { color: var(--ink) !important; }
[data-testid="stMainBlockContainer"], [data-testid="stAppViewBlockContainer"] {
  max-width: 1120px;
  padding: 2.4rem 2.6rem 4rem;
}

::selection { background: var(--accent); color: var(--sheet); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--ground); }
::-webkit-scrollbar-thumb { background: var(--scrollbar); border: 3px solid var(--ground); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

/* ---------- masthead ---------- */
.masthead {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--rule);
}
.wordmark-row { display: flex; align-items: center; gap: 11px; }
.tab-mark { width: 9px; height: 9px; background: var(--accent); display: inline-block; }
.wordmark {
  font-family: var(--font-mono);
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.34em;
  line-height: 1;
}
.masthead-sub { margin: 8px 0 0; font-size: 12.5px; color: var(--muted); }
.masthead-right {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.14em;
  color: var(--muted);
  text-align: right;
  line-height: 1.8;
}

/* ---------- tabs ---------- */
[data-testid="stTabs"] [role="tablist"] {
  gap: 0;
  border-bottom: 1px solid var(--rule);
  background: transparent;
}
[data-testid="stTab"] {
  background: transparent;
  border-radius: 0;
  padding: 11px 20px;
  color: var(--muted) !important;
}
[data-testid="stTab"] p {
  font-family: var(--font-ui) !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  letter-spacing: 0.06em !important;
  color: inherit !important;
}
[data-testid="stTab"][aria-selected="true"] {
  background: var(--sheet);
  color: var(--ink) !important;
  box-shadow: inset 0 2px 0 0 var(--accent);
}
[data-testid="stTabPanel"] {
  background: var(--sheet);
  border: 1px solid var(--rule);
  border-top: none;
  border-radius: 0 0 2px 2px;
  padding: 26px 30px 30px;
  box-shadow: 0 22px 36px -30px rgba(32, 32, 29, 0.45);
}

/* ---------- sheet typography ---------- */
.sheet-title {
  margin: 0 0 5px;
  font-family: var(--font-ui);
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: var(--ink);
}
.sheet-caption {
  margin: 0 0 22px;
  font-size: 12.5px;
  line-height: 1.7;
  color: var(--muted);
}
.sheet-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 8px;
  margin-bottom: 4px;
  border-bottom: 1px solid var(--rule);
}
.sheet-meta {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.14em;
  color: var(--muted);
}

/* ---------- buttons ---------- */
[data-testid="stButton"] > button,
[data-testid="stBaseButton-secondary"],
[data-testid="stBaseButton-primary"] {
  font-family: var(--font-ui);
  font-size: 12px;
  letter-spacing: 0.12em;
  border-radius: 2px;
  transition: background 160ms ease, border-color 160ms ease, color 160ms ease;
}
[data-testid="stBaseButton-primary"] {
  background: var(--ink) !important;
  border: 1px solid var(--ink) !important;
  color: var(--sheet) !important;
  padding: 10px 22px !important;
  box-shadow: none !important;
}
[data-testid="stBaseButton-primary"]:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  color: var(--sheet) !important;
}

/* ---------- inputs ---------- */
[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"] {
  background: var(--sheet) !important;
  border: 1px solid var(--rule) !important;
  border-radius: 2px !important;
  box-shadow: none !important;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within {
  border-color: var(--ink) !important;
}
[data-testid="stTextInputRootElement"] input,
[data-testid="stTextAreaRootElement"] textarea {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  color: var(--ink) !important;
  font-family: var(--font-ui) !important;
  font-size: 14px !important;
  line-height: 1.65 !important;
  caret-color: var(--accent);
}
[data-testid="stWidgetLabel"] p {
  font-family: var(--font-mono) !important;
  font-size: 9.5px !important;
  letter-spacing: 0.14em !important;
  color: var(--muted) !important;
  text-transform: uppercase;
}
[data-testid="stBaseButton-primary"] p {
  font-family: var(--font-ui) !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.12em !important;
  color: inherit !important;
}

/* ---------- readout entries ---------- */
.readout { margin-top: 22px; }
.entry { padding: 20px 0 18px; border-top: 1px solid var(--rule); }
.entry:first-child { border-top: none; padding-top: 4px; }
.entry-line, .disk-line, .measure-line {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.entry-label, .measure-label { font-size: 13px; color: var(--ink); }
.leader { flex: 1; border-bottom: 1px dotted var(--rule); transform: translateY(-4px); }
.entry-value {
  font-family: var(--font-mono);
  font-size: 30px;
  font-weight: 500;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.01em;
}
.unit { margin-left: 2px; font-size: 11px; color: var(--muted); letter-spacing: 0; }
.entry-meta {
  margin: 9px 0 0;
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.04em;
  color: var(--muted);
}

/* ---------- calibrated gauges ---------- */
.gauge { position: relative; height: 14px; margin-top: 12px; }
.gauge-scale {
  height: 5px;
  background-image: repeating-linear-gradient(
    90deg, var(--rule) 0 1px, transparent 1px 10%
  );
}
.gauge-track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 6px;
  background: var(--gauge-track);
}
.gauge-fill { height: 100%; background: var(--ink); }
.gauge-fill.is-caution { background: var(--caution); }
.gauge-fill.is-alert { background: var(--accent); }

/* ---------- disks ---------- */
.disks-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 28px;
  padding: 18px 0 2px;
  border-top: 1px solid var(--ink);
}
.disks-head .sheet-title { font-size: 14px; margin: 0; }
.disk { padding: 14px 0 12px; }
.disk + .disk { border-top: 1px solid var(--rule); }
.disk-name {
  font-family: var(--font-mono);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.disk-type {
  padding: 2px 5px;
  border: 1px solid var(--rule);
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--muted);
}
.disk-percent {
  font-family: var(--font-mono);
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

/* ---------- empty / notice ---------- */
.empty {
  border: 1px dashed var(--rule);
  margin-top: 20px;
  padding: 22px 24px;
}
.empty-kicker {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.16em;
  color: var(--muted);
}
.empty p { margin: 9px 0 0; font-size: 13px; line-height: 1.7; color: var(--ink); }
.notice {
  margin-top: 20px;
  padding: 13px 16px;
  border: 1px solid var(--rule);
  border-top: 2px solid var(--ink);
  background: var(--sheet);
}
.notice-label {
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.16em;
  color: var(--muted);
}
.notice p { margin: 7px 0 0; font-size: 13px; line-height: 1.7; }
.notice.is-error { border-top-color: var(--accent); }
.notice.is-error .notice-label { color: var(--accent); }

/* ---------- verdict ---------- */
.verdict { margin-top: 26px; border-top: 1px solid var(--ink); padding-top: 18px; }
.verdict-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
}
.verdict-grid {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 38px;
  align-items: center;
  padding: 24px 0 10px;
}
.stamp-wrap { display: flex; justify-content: center; }
.stamp {
  display: inline-block;
  padding: 12px 20px;
  border: 3px double var(--accent);
  color: var(--accent);
  text-align: center;
  transform: rotate(-5deg);
  opacity: 0.86;
}
.stamp.is-fresh { animation: stamp-press 420ms cubic-bezier(0.16, 1, 0.3, 1) both; }
.stamp-main {
  display: block;
  font-family: var(--font-mono);
  font-size: 19px;
  font-weight: 600;
  letter-spacing: 0.08em;
  line-height: 1.15;
  white-space: nowrap;
}
.stamp-sub {
  display: block;
  margin-top: 5px;
  font-family: var(--font-mono);
  font-size: 8.5px;
  letter-spacing: 0.22em;
}
@keyframes stamp-press {
  from { opacity: 0; transform: rotate(-12deg) scale(1.16); }
  to { opacity: 0.86; transform: rotate(-5deg) scale(1); }
}
@media (prefers-reduced-motion: reduce) {
  .stamp.is-fresh { animation: none; }
}

.measure { padding-bottom: 16px; }
.measure + .measure { border-top: 1px dotted var(--rule); padding-top: 16px; }
.measure-value {
  font-family: var(--font-mono);
  font-size: 24px;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}
.measure-note {
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.1em;
  color: var(--muted);
}
.water-track { position: relative; display: flex; height: 8px; margin-top: 12px; }
.water-zone { height: 100%; opacity: 0.55; }
.water-marker {
  position: absolute;
  top: -5px;
  width: 2px;
  height: 18px;
  background: var(--ink);
  transform: translateX(-1px);
}
.water-marker::after {
  content: "";
  position: absolute;
  top: -4px;
  left: -3px;
  border-right: 4px solid transparent;
  border-left: 4px solid transparent;
  border-top: 5px solid var(--ink);
}
.water-scale {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.verdict-reason { margin-top: 4px; padding-top: 14px; border-top: 1px solid var(--rule); }
.reason-label {
  display: block;
  margin-bottom: 6px;
  font-family: var(--font-mono);
  font-size: 9.5px;
  letter-spacing: 0.16em;
  color: var(--muted);
}
.verdict-reason p { margin: 0; font-size: 13.5px; line-height: 1.75; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
  background: var(--sidebar);
  border-right: 1px solid var(--rule);
}
[data-testid="stSidebar"] .block-container { padding-top: 2.2rem; }
.side-title { margin: 0 0 8px; font-size: 14px; font-weight: 600; letter-spacing: 0.02em; }
.side-note {
  margin: 10px 0 0;
  font-size: 11.5px;
  line-height: 1.75;
  color: var(--muted);
}
.side-foot {
  margin-top: 30px;
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.14em;
  color: var(--muted);
  line-height: 1.9;
}

/* ---------- native chrome ---------- */
[data-testid="stSpinner"] { color: var(--muted) !important; }
[data-baseweb="tooltip"] {
  background: var(--sheet) !important;
  color: var(--ink) !important;
}
[data-testid="stTooltipContent"] {
  background: var(--sheet) !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule) !important;
}
[data-testid="stCheckbox"] label p {
  font-family: var(--font-mono) !important;
  font-size: 9.5px !important;
  letter-spacing: 0.14em !important;
  color: var(--muted) !important;
  text-transform: uppercase;
}
[data-testid="stCheckbox"] [role="switch"] { accent-color: var(--accent); }

/* ---------- type resets against Streamlit's markdown defaults ---------- */
[data-testid="stMarkdownContainer"] { font-family: var(--font-ui); }
.masthead-sub {
  margin: 8px 0 0 !important;
  font-size: 12.5px !important;
  line-height: 1.6 !important;
  color: var(--muted) !important;
}
.sheet-title {
  margin: 0 0 5px !important;
  font-size: 17px !important;
  font-weight: 600 !important;
  line-height: 1.45 !important;
  letter-spacing: 0.03em !important;
  color: var(--ink) !important;
}
.sheet-caption {
  margin: 0 0 22px !important;
  font-size: 12.5px !important;
  line-height: 1.7 !important;
  color: var(--muted) !important;
}
.entry-meta {
  margin: 9px 0 0 !important;
  font-family: var(--font-mono) !important;
  font-size: 10px !important;
  line-height: 1.5 !important;
  letter-spacing: 0.04em !important;
  color: var(--muted) !important;
}
.side-title {
  margin: 0 0 8px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  color: var(--ink) !important;
}
.side-note {
  margin: 10px 0 0 !important;
  font-size: 11.5px !important;
  line-height: 1.75 !important;
  color: var(--muted) !important;
}
.empty p {
  margin: 9px 0 0 !important;
  font-size: 13px !important;
  line-height: 1.7 !important;
  color: var(--ink) !important;
}
.notice p {
  margin: 7px 0 0 !important;
  font-size: 13px !important;
  line-height: 1.7 !important;
}
.verdict-reason p {
  margin: 0 !important;
  font-size: 13.5px !important;
  line-height: 1.75 !important;
  color: var(--ink) !important;
}
.measure-note {
  margin: 8px 0 0 !important;
  font-family: var(--font-mono) !important;
  font-size: 9.5px !important;
  line-height: 1.5 !important;
  letter-spacing: 0.1em !important;
  color: var(--muted) !important;
}

/* ---------- colophon ---------- */
.colophon {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-top: 34px;
  padding-top: 12px;
  border-top: 1px solid var(--rule);
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.12em;
  color: var(--muted);
}

/* ---------- responsive ---------- */
@media (max-width: 760px) {
  [data-testid="stMainBlockContainer"], [data-testid="stAppViewBlockContainer"] {
    padding: 1.4rem 1.1rem 3rem;
  }
  .masthead { flex-direction: column; align-items: flex-start; gap: 10px; }
  .masthead-right { text-align: left; }
  .verdict-grid { grid-template-columns: 1fr; gap: 20px; }
  .stamp-wrap { justify-content: flex-start; }
  [data-testid="stTabPanel"] { padding: 20px 18px 24px; }
  .entry-value { font-size: 26px; }
  .colophon { flex-direction: column; gap: 6px; }
}
</style>
"""

_WATER_ZONES = (
    (20, "var(--ok)"),
    (20, "var(--caution)"),
    (30, "var(--ochre-water)"),
    (30, "var(--accent)"),
)


def _water_label(score: int) -> str:
    """把水分指数转成一句人话。"""
    if score <= 20:
        return "很实在"
    if score <= 40:
        return "略有水分"
    if score <= 70:
        return "水分较大"
    return "严重画饼"


def _gauge(percent: float, alarm: bool = True) -> str:
    """返回一条带刻度的测量条；alarm=False 时不按阈值着色。"""
    value = max(0.0, min(100.0, percent))
    state = ""
    if alarm:
        state = " is-alert" if value >= 90 else " is-caution" if value >= 75 else ""
    return (
        '<div class="gauge">'
        '<div class="gauge-scale"></div>'
        f'<div class="gauge-track"><div class="gauge-fill{state}" '
        f'style="width:{value:.2f}%"></div></div>'
        "</div>"
    )


def _notice(kind: str, label: str, message: str) -> None:
    role = "alert" if kind == "error" else "status"
    st.markdown(
        f'<div class="notice is-{kind}" role="{role}">'
        f'<span class="notice-label">{label}</span>'
        f"<p>{html.escape(message)}</p></div>",
        unsafe_allow_html=True,
    )


def _empty(kicker: str, message: str) -> None:
    st.markdown(
        f'<div class="empty"><span class="empty-kicker">{kicker}</span>'
        f"<p>{html.escape(message)}</p></div>",
        unsafe_allow_html=True,
    )


def _entry(label: str, value: str, unit: str, meta: str, percent: float) -> str:
    return (
        '<div class="entry">'
        '<div class="entry-line">'
        f'<span class="entry-label">{html.escape(label)}</span>'
        '<span class="leader" aria-hidden="true"></span>'
        f'<span class="entry-value">{value}<span class="unit">{unit}</span></span>'
        "</div>"
        f"{_gauge(percent)}"
        f'<p class="entry-meta">{meta}</p>'
        "</div>"
    )


def _sys_readout(data: dict[str, Any], captured: datetime) -> str:
    cpu = data["cpu"]
    memory = data["memory"]
    cores = f"{cpu['logical_cores']} 逻辑核心"
    if cpu["physical_cores"]:
        cores += f" · {cpu['physical_cores']} 物理核心"
    entries = _entry(
        "CPU 使用率",
        f"{cpu['percent']:.1f}",
        "%",
        f"{cores} · 采样 0.5 秒",
        cpu["percent"],
    )
    entries += _entry(
        "内存使用率",
        f"{memory['percent']:.1f}",
        "%",
        (
            f"已用 {sys_radar.format_bytes(memory['used'])} / "
            f"{sys_radar.format_bytes(memory['total'])} · "
            f"可用 {sys_radar.format_bytes(memory['available'])}"
        ),
        memory["percent"],
    )

    disks = data["disks"]
    disk_rows = "".join(
        (
            '<div class="disk">'
            '<div class="disk-line">'
            f'<span class="disk-name">{html.escape(str(disk["mountpoint"]))}</span>'
            f'<span class="disk-type">{html.escape(disk["fstype"] or "—")}</span>'
            '<span class="leader" aria-hidden="true"></span>'
            f'<span class="disk-percent">{disk["percent"]:.1f}'
            '<span class="unit">%</span></span>'
            "</div>"
            f"{_gauge(disk['percent'])}"
            f'<p class="entry-meta">已用 {sys_radar.format_bytes(disk["used"])} / '
            f"{sys_radar.format_bytes(disk['total'])} · "
            f"剩余 {sys_radar.format_bytes(disk['free'])}</p>"
            "</div>"
        )
        for disk in disks
    )
    disks_html = (
        '<div class="disks-head">'
        '<h3 class="sheet-title">磁盘</h3>'
        f'<span class="sheet-meta">{len(disks)} VOLUMES</span>'
        "</div>"
        f"{disk_rows}"
        if disks
        else '<div class="disks-head"><h3 class="sheet-title">磁盘</h3>'
        '<span class="sheet-meta">0 VOLUMES</span></div>'
    )

    return (
        '<section class="readout">'
        '<div class="sheet-head">'
        '<span class="sheet-meta">READOUT</span>'
        f'<span class="sheet-meta">{captured.strftime("%Y-%m-%d %H:%M:%S")}</span>'
        "</div>"
        f"{entries}{disks_html}"
        "</section>"
    )


def _verdict_html(result: dict[str, Any], text: str, captured: datetime) -> str:
    water = jd_detector.estimate_water_index(text)
    confidence = result.get("confidence")
    verdict_text = "销售 / 地推" if result["is_sales"] else "非销售 / 地推"
    verdict_sub = "SALES · FIELD" if result["is_sales"] else "NOT SALES"
    fresh = " is-fresh" if st.session_state.pop("jd_fresh_stamp", False) else ""

    confidence_html = (
        '<div class="measure">'
        '<div class="measure-line">'
        '<span class="measure-label">置信度</span>'
        '<span class="leader" aria-hidden="true"></span>'
        f'<span class="measure-value">{confidence:.0%}</span>'
        "</div>"
        f"{_gauge(confidence * 100, alarm=False)}"
        "</div>"
        if confidence is not None
        else '<div class="measure"><div class="measure-line">'
        '<span class="measure-label">置信度</span>'
        '<span class="leader" aria-hidden="true"></span>'
        '<span class="measure-value">—</span></div></div>'
    )

    zones = "".join(
        f'<span class="water-zone" style="width:{width}%;background:{color}"></span>'
        for width, color in _WATER_ZONES
    )
    reason = html.escape(result.get("reason") or "")
    reason_html = (
        f'<div class="verdict-reason"><span class="reason-label">理由</span><p>{reason}</p></div>'
        if reason
        else ""
    )
    return (
        '<section class="verdict">'
        '<div class="verdict-top">'
        '<span class="sheet-meta">VERDICT</span>'
        f'<span class="sheet-meta">{captured.strftime("%Y-%m-%d %H:%M:%S")}</span>'
        "</div>"
        '<div class="verdict-grid">'
        '<div class="stamp-wrap">'
        f'<div class="stamp{fresh}" role="status" aria-label="{verdict_text}">'
        f'<span class="stamp-main">{verdict_text}</span>'
        f'<span class="stamp-sub">{verdict_sub}</span>'
        "</div></div>"
        '<div class="verdict-measures">'
        f"{confidence_html}"
        '<div class="measure">'
        '<div class="measure-line">'
        '<span class="measure-label">水分指数</span>'
        '<span class="leader" aria-hidden="true"></span>'
        f'<span class="measure-value">{water}<span class="unit">/100</span></span>'
        "</div>"
        f'<div class="water-track">{zones}'
        f'<span class="water-marker" style="left:{water}%"></span></div>'
        '<div class="water-scale"><span>0 实在</span><span>20</span>'
        "<span>40</span><span>70</span><span>100 画饼</span></div>"
        f'<p class="measure-note">{_water_label(water)}</p>'
        "</div>"
        "</div></div>"
        f"{reason_html}"
        "</section>"
    )


def _show_sys_radar() -> None:
    st.markdown(
        '<h2 class="sheet-title">系统读数</h2>'
        '<p class="sheet-caption">读取本机 CPU、内存与磁盘的实时状态，'
        "数据只保留在当前页面。</p>",
        unsafe_allow_html=True,
    )
    if st.button("采集读数", type="primary", key="sys-radar-run"):
        with st.spinner("正在读取…"):
            try:
                data = sys_radar.collect(interval=0.5)
            except OSError as exc:
                st.session_state["sys_radar_error"] = str(exc)
            else:
                st.session_state["sys_radar"] = {
                    "data": data,
                    "captured": datetime.now(),
                }
                st.session_state.pop("sys_radar_error", None)

    error = st.session_state.get("sys_radar_error")
    saved = st.session_state.get("sys_radar")
    if error:
        _notice("error", "READ FAILED / 读取失败", f"无法读取系统信息：{error}")
    elif saved is None:
        _empty("NO READOUT", "尚无读数。点击「采集读数」，本机状态会登记到这张卡片上。")
    else:
        st.markdown(
            _sys_readout(saved["data"], saved["captured"]),
            unsafe_allow_html=True,
        )


def _show_jd_detector(api_key: str) -> None:
    st.markdown(
        '<h2 class="sheet-title">JD 判定</h2>'
        '<p class="sheet-caption">粘贴一段职位描述，用 DeepSeek 判定是否销售/地推岗位，'
        "并给出水分指数。</p>",
        unsafe_allow_html=True,
    )
    text = st.text_area(
        "职位描述",
        height=200,
        placeholder="例如：招聘地推专员，要求吃苦耐劳，单休，底薪3000，年薪四十万不是梦",
        key="jd-text",
    )
    if st.button("开始脱水", type="primary", key="jd-run"):
        content = text.strip()
        if not content:
            st.session_state["jd_error"] = "请先粘贴职位描述。"
        elif not api_key.strip():
            st.session_state["jd_error"] = "请先在左侧填写 DeepSeek API Key。"
        else:
            with st.spinner("正在调用 DeepSeek 分析…"):
                try:
                    result = jd_detector.classify(content, api_key=api_key.strip())
                except jd_detector.JdDetectorError as exc:
                    st.session_state["jd_error"] = f"分析失败：{exc}"
                else:
                    st.session_state["jd_verdict"] = {
                        "result": result,
                        "text": content,
                        "captured": datetime.now(),
                    }
                    st.session_state["jd_fresh_stamp"] = True
                    st.session_state.pop("jd_error", None)

    error = st.session_state.get("jd_error")
    saved = st.session_state.get("jd_verdict")
    if error:
        _notice("error", "ERROR / 未完成", error)
    elif saved is None:
        _empty("NO VERDICT", "粘贴 JD 后点击「开始脱水」，判定会盖在这张卡片上。")
    else:
        st.markdown(
            _verdict_html(saved["result"], saved["text"], saved["captured"]),
            unsafe_allow_html=True,
        )


def main() -> None:
    """页面入口。"""
    st.set_page_config(
        page_title="MyAITools",
        page_icon="🗂",
        layout="wide",
        initial_sidebar_state="auto",
    )
    dark_mode = bool(st.session_state.get("dark_mode", False))
    st.markdown(_palette_css(dark_mode) + _CSS_BODY, unsafe_allow_html=True)
    st.markdown(
        '<header class="masthead">'
        '<div class="masthead-left">'
        '<div class="wordmark-row">'
        '<span class="tab-mark" aria-hidden="true"></span>'
        '<span class="wordmark">MYAITOOLS</span>'
        "</div>"
        '<p class="masthead-sub">本地工具集 · 系统读数与 JD 判别</p>'
        "</div>"
        '<div class="masthead-right">LOCAL TOOLKIT<br>'
        f"CATALOGUE 002 · v{__version__}</div>"
        "</header>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown('<h2 class="side-title">设置</h2>', unsafe_allow_html=True)
        api_key = st.text_input(
            "DeepSeek API Key",
            value=os.environ.get("DEEPSEEK_API_KEY", ""),
            type="password",
            help="也可以启动前设置环境变量 DEEPSEEK_API_KEY。",
        )
        st.markdown(
            '<p class="side-note">仅保存在本次会话，不写入磁盘；'
            "调用时才会发送给 DeepSeek。</p>"
            '<div class="side-foot">CATALOGUE 002<br>'
            f"MYAITOOLS v{__version__}</div>",
            unsafe_allow_html=True,
        )
        st.toggle(
            "深色模式",
            key="dark_mode",
            value=dark_mode,
            help="在浅色与深色档案室之间切换。",
        )

    sys_tab, jd_tab = st.tabs(["系统雷达", "JD 脱水器"])
    with sys_tab:
        _show_sys_radar()
    with jd_tab:
        _show_jd_detector(api_key)

    st.markdown(
        '<div class="colophon"><span>MYAITOOLS · LOCAL TOOLKIT</span>'
        "<span>数据来源：本机 psutil / DeepSeek API · JD 判定以外不出本机</span></div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
