"""MyAITools 的极简 Web 界面（Streamlit）。

本地启动：

    streamlit run src/myaitools/app.py
"""

from __future__ import annotations

import os

import streamlit as st

from myaitools import __version__
from myaitools.tools import jd_detector, sys_radar


def _water_label(score: int) -> str:
    """把水分指数转成一句人话。"""
    if score <= 20:
        return "很实在"
    if score <= 40:
        return "略有水分"
    if score <= 70:
        return "水分较大"
    return "严重画饼"


def _show_sys_radar() -> None:
    """系统雷达标签页。"""
    st.caption("一次性采集本机 CPU、内存与磁盘使用情况。")
    if st.button("开始检测", type="primary", key="sys-radar-run"):
        with st.spinner("正在采集系统信息…"):
            try:
                st.session_state["sys_radar_data"] = sys_radar.collect(interval=0.5)
            except OSError as exc:
                st.error(f"采集失败：{exc}")

    data = st.session_state.get("sys_radar_data")
    if data is None:
        st.info("点击上方「开始检测」按钮查看本机状态。")
        return

    cpu = data["cpu"]
    memory = data["memory"]
    with st.container(border=True):
        left, middle, right = st.columns(3)
        left.metric("CPU 使用率", f"{cpu['percent']:.1f}%")
        middle.metric("逻辑核心", cpu["logical_cores"])
        right.metric("物理核心", cpu["physical_cores"] or "—")
        st.progress(min(cpu["percent"] / 100, 1.0), text=f"CPU {cpu['percent']:.1f}%")

    with st.container(border=True):
        left, middle, right = st.columns(3)
        left.metric("内存使用率", f"{memory['percent']:.1f}%")
        middle.metric("已用", sys_radar.format_bytes(memory["used"]))
        right.metric("总量", sys_radar.format_bytes(memory["total"]))
        st.progress(
            min(memory["percent"] / 100, 1.0),
            text=f"可用 {sys_radar.format_bytes(memory['available'])}",
        )

    st.markdown("#### 磁盘")
    disks = data["disks"]
    if not disks:
        st.warning("未检测到可用磁盘。")
        return
    for disk in disks:
        label = disk["mountpoint"]
        if disk["fstype"]:
            label += f"（{disk['fstype']}）"
        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.progress(
                min(disk["percent"] / 100, 1.0),
                text=(
                    f"已用 {sys_radar.format_bytes(disk['used'])} / "
                    f"{sys_radar.format_bytes(disk['total'])} · "
                    f"剩余 {sys_radar.format_bytes(disk['free'])} · {disk['percent']:.1f}%"
                ),
            )


def _show_jd_detector(api_key: str) -> None:
    """JD 脱水器标签页。"""
    st.caption("粘贴一段职位描述，用 DeepSeek 判断是否销售/地推岗位，并估算「水分指数」。")
    text = st.text_area(
        "职位描述",
        height=260,
        placeholder="例如：招聘地推专员，要求吃苦耐劳，单休，底薪3000，年薪四十万不是梦",
        key="jd-text",
    )
    if st.button("开始脱水", type="primary", key="jd-run"):
        content = text.strip()
        if not content:
            st.warning("请先粘贴职位描述。")
        elif not api_key.strip():
            st.error("请先在左侧填写 DeepSeek API Key。")
        else:
            with st.spinner("正在调用 DeepSeek 分析…"):
                try:
                    result = jd_detector.classify(content, api_key=api_key.strip())
                except jd_detector.JdDetectorError as exc:
                    st.error(f"分析失败：{exc}")
                else:
                    st.session_state["jd_result"] = {"text": content, "result": result}

    saved = st.session_state.get("jd_result")
    if saved is None:
        st.info("粘贴 JD 后点击「开始脱水」，结果会显示在这里。")
        return

    result = saved["result"]
    water = jd_detector.estimate_water_index(saved["text"])
    verdict = "是销售/地推岗位" if result["is_sales"] else "不是销售/地推岗位"
    confidence = result.get("confidence")

    with st.container(border=True):
        left, middle, right = st.columns(3)
        left.metric("结论", verdict)
        middle.metric("置信度", f"{confidence:.0%}" if confidence is not None else "—")
        right.metric("水分指数", f"{water}/100")
        st.progress(water / 100, text=f"{water}/100 · {_water_label(water)}")
        if result.get("reason"):
            st.info(f"理由：{result['reason']}")
        st.caption("水分指数基于「画饼」关键词规则估算（0 很实在 → 100 严重画饼），仅供参考。")


def main() -> None:
    """页面入口。"""
    st.set_page_config(
        page_title="MyAITools",
        page_icon="🧰",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("MyAITools")
    st.caption(f"轻量 Python 小工具集 · v{__version__}")

    with st.sidebar:
        st.header("设置")
        api_key = st.text_input(
            "DeepSeek API Key",
            value=os.environ.get("DEEPSEEK_API_KEY", ""),
            type="password",
            help="只在本地使用，不会写入磁盘；也可以启动前设置环境变量 DEEPSEEK_API_KEY。",
        )
        st.divider()
        st.caption("系统雷达无需 API Key；JD 脱水器需要 DeepSeek API Key。")

    sys_tab, jd_tab = st.tabs(["系统雷达", "JD 脱水器"])
    with sys_tab:
        _show_sys_radar()
    with jd_tab:
        _show_jd_detector(api_key)


if __name__ == "__main__":  # pragma: no cover
    main()
