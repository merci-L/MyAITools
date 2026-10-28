---
name: MyAITools
description: Precision archive cards for a quiet local toolkit.
colors:
  ground: "#E8E8E6"
  sheet: "#F5F5F3"
  ink: "#20201D"
  muted: "#676254"
  rule: "#D8D8D5"
  vermilion-tab: "#A63D2F"
  sage-ok: "#4F6B4F"
  amber-caution: "#9A6B1F"
  sidebar-ground: "#E4E4E1"
  gauge-track: "#E3E3E0"
  scrollbar-thumb: "#C6C6C2"
  ochre-water: "#B07D2E"
  dark-ground: "#12100C"
  dark-sheet: "#1D1A14"
  dark-ink: "#ECE5D6"
  dark-muted: "#A49B87"
  dark-rule: "#3A352B"
  dark-accent: "#E0765F"
  dark-ok: "#86A882"
  dark-caution: "#CFA055"
  dark-ochre-water: "#C08A48"
  dark-sidebar: "#17140F"
  dark-gauge-track: "#2A261E"
  dark-scrollbar: "#403B30"
typography:
  wordmark:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.18em"
  headline:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "0.01em"
  body:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
  meta:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0em"
  measure:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "30px"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.01em"
  measure-sm:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "24px"
    fontWeight: 500
    lineHeight: 1
  measure-mobile:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "26px"
    fontWeight: 500
    lineHeight: 1
  numeric-sm:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.2
  unit:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.2
  stamp:
    fontFamily: "Consolas, Cascadia Mono, DejaVu Sans Mono, monospace"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0.06em"
  input:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
  title-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.4
  ui:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  ui-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    lineHeight: 1.2
  body-strong:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.75
  caption-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.75
rounded:
  none: "0px"
  sm: "2px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "28px"
  xl: "40px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.sm}"
    padding: "10px 22px"
  button-primary-hover:
    backgroundColor: "{colors.vermilion-tab}"
    textColor: "{colors.sheet}"
  tab-active:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
  input:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.sm}"
  sheet:
    backgroundColor: "{colors.sheet}"
    rounded: "{rounded.sm}"
  stamp:
    textColor: "{colors.vermilion-tab}"
    rounded: "{rounded.none}"
---

# Design System: MyAITools

## Overview

**Creative North Star: "The Precision Archive"**

MyAITools 的操作界面是一张精密档案卡：读数像登记在卡片上的条目，判定像盖在卡片上的橡皮章。它安静、克制、可核对，所有装饰都必须为“精确”服务。视觉世界只借用四个东西——字体、配色、密度、一个签名动作（印章）——布局、导航与控件仍然是标准的工具控件。

**Key Characteristics:**

- 中性石色卡纸底 + 墨色字；唯一的朱红只做页签强调、印章与告警
- 数字用等宽字体、表格数字对齐；文字标签用 11–13px 无衬线、句子大小写、零字距
- 虚线引导线连接标签与数值；校准刻度条承担测量感的表达
- 纸面平铺在石色地面上，只用 1px 发丝线与色阶分面，不用阴影
- 一个作者时刻：判定印章按下时的 420ms 落印动画；其余元素不动
- 反参考：发光仪表盘卡片矩阵、大数字英雄面板、渐变文字、玻璃拟态、彩色左边框、微缩大写标签

## Colors

一张中性的档案纸：石色地面、近白纸面、近黑墨色，一个朱红记号笔色。

### Primary

- **Vermilion Tab** (#A63D2F)：只出现在四个位置——激活标签页的顶边、主按钮 hover、判定印章、以及越过警戒阈值的测量条。它是记号，不是主题色。

### Neutral

- **Stone Ground** (#E8E8E6)：页面地面，也是浏览器滚动条的底色。
- **Card Sheet** (#F5F5F3)：所有读数、判定与输入控件所在的纸面。
- **Archive Ink** (#20201D)：正文、标题与数值；对纸面约 15:1。
- **Muted Annotation** (#676254)：说明文字、时间戳、元数据；对纸面约 6.5:1。
- **Hairline Rule** (#D8D8D5)：1px 分隔线、虚线引导线、输入框描边。
- **Sidebar Ground** (#E4E4E1)：设置侧栏，比地面深一阶。
- **Gauge Track** (#E3E3E0)：测量条轨道。
- **Scrollbar Thumb** (#C6C6C2)：浏览器滚动条。

### Secondary (state)

- **Sage OK** (#4F6B4F)：水分指数 0–20 区间。
- **Amber Caution** (#9A6B1F)：测量条 75–90% 的告警态、水分指数 21–40 区间。
- **Ochre Water** (#B07D2E)：水分指数 41–70 区间。

### Dark Variant — The Night Archive

深色外观是同一间档案室的夜班，不是另一套产品：地面换成暖炭黑（#12100C），纸面变成深色卡纸（#1D1A14），墨色反转成暖白（#ECE5D6），朱红提亮到 #E0765F 以保证深底上的小字对比度。它保留全部版式、刻度、虚线引导与印章，只是把「纸张在灯下」换成「纸张在台灯下」：暖、暗、安静，不做霓虹、不做发光。

- **Night Ground** (#12100C)：页面地面。
- **Night Sheet** (#1D1A14)：纸面、输入框、页签激活态。
- **Lamp Ink** (#ECE5D6)：正文与数值，对纸面约 12:1。
- **Night Muted** (#A49B87)：说明文字，对纸面约 6.5:1。
- **Night Rule** (#3A352B)：发丝线与虚线引导。
- **Night Accent** (#E0765F)：夜班里的朱红记号（印章、激活页签顶边、告警）。

### Named Rules

**The One Red Rule.** 朱红在任意一屏的覆盖面积不超过 5%，且只做“记号”用途；大面积铺红即失去档案感。

**The Paper Rule.** 所有数据必须落在 Card Sheet 上，不直接贴在 Stone Ground 上；地面只负责承载纸面。

**The Calibration Rule.** 颜色只表达真实状态：测量条的琥珀/朱红仅在越过阈值时出现，置信度条永远用墨色，不用红色暗示“警告”。

**The Night Shift Rule.** 深色外观只换纸与灯，不换世界：布局、字体层级、刻度与印章规则完全一致；禁止霓虹、发光与高饱和大面积色。

## Typography

**Display / Data Font:** Consolas（Cascadia Mono / DejaVu Sans Mono 兜底）
**Body Font:** Segoe UI（微软雅黑 / PingFang SC / Noto Sans SC 兜底）

**Character:** 中文用系统无衬线保证清晰；数字与测量值用等宽字体，让读数看起来像被登记进表格。全站只有两种字体，且都是本机系统字体——离线也能保持一致。标签一律句子大小写、零字距，不靠微缩大写制造“技术感”。

### Hierarchy

- **Wordmark** (600, 20px, 1, 0.18em)：`MYAITOOLS`，等宽大写，小宽屏也不换行。
- **Headline** (600, 18px, 1.4)：纸面标题（系统读数 / JD 判定）。
- **Body** (400, 13px, 1.7)：说明文字，单行宽度受纸面限制。
- **Label** (400, 11–12px, 0)：字段名、时间戳、状态说明；句子大小写，零字距。
- **Measure** (500, 30px, 1, tabular-nums)：核心读数；移动端降到 26px。

### Named Rules

**The Tabular Rule.** 所有测量值使用 `font-variant-numeric: tabular-nums` 并右对齐；数值变化时不允许列宽跳动。

**The Two Faces Rule.** 只用一种 UI 字体与一种数据字体；不加载外部字体、不使用图标字体；系统字体缺失时退到平台等宽字体，不额外请求网络。

**The No Tiny Caps Rule.** 没有 11px 以下文字；不使用大写 + 大字距的微标签；字号最小 11px，辅助文字 12px。

## Layout

单列纸面，最大内容宽度 1120px；桌面容器内边距 38.4px / 41.6px，移动端 22.4px / 17.6px。页头是一条 1px 发丝线，右侧放目录编号；标签页紧贴纸面，激活页签与纸面连成一体（纸面顶部无边框）。纸面内边距 30px / 34px。

纸面内部：标题 → 13px 说明（下留 24px）→ 主操作按钮 → 内容。读数条目 20px / 18px 内边距，条目间 1px 发丝线；磁盘区以一条 1px 墨线开始，盘符行与说明行成组。判定卡为 250px 印章列 + 自适应测量列的两栏网格，760px 以下堆叠为单列。页脚 colophon 用 40px 上外边距与发丝线收束页面。

## Elevation & Depth

平铺，无阴影：纸面与地面之间只用一阶色差与 1px 发丝线分开。没有内嵌卡片、没有环境阴影、没有发光；深度来自纸面叠放关系，而不是阴影强度。只有真正的浮层（菜单、对话框、tooltip）才允许浮动。

**The Flat-At-Rest Rule.** 静止的纸面、按钮、输入框一律无阴影；悬停与激活只改变颜色与 1px 线条，不抬升元素。

## Shapes

最大圆角 2px；纸面只在下沿收 2px 圆角。边框统一 1px 实线（#D8D8D5），空状态用 1px 虚线；印章用 3px 双线框并旋转 -5°；测量条为 6px 高的实心条 + 5px 刻度带；页签标记是一枚 10px 朱红方块。不使用胶囊、卡片矩阵与装饰性多边形。

## Components

### Buttons

- **Shape:** 2px 圆角（`2px`），高 40px 左右。
- **Primary:** 墨色底 + 纸色字，`10px 22px` 内边距，13px 中文、0.02em 字距。
- **Hover / Focus:** hover 切到朱红底；focus 用 2px 朱红外描边、2px 偏移；无位移、无阴影。
- **Disabled:** 墨色 40% 透明度，保持文字可读。

### Tabs

- 抽屉页签：未激活为地面色、muted 文字；激活页签为纸面色 + 内侧 2px 朱红顶边，与下方纸面无缝相接。页签区与纸面之间只有一条 1px 发丝线；标签 14px、零字距。

### Inputs

- **Shape:** 2px 圆角；1px 发丝描边；纸色底。
- **Label:** 12px 无衬线、句子大小写、零字距、muted 色。
- **Focus:** 描边变墨色，无外发光；caret 为朱红。

### Sheet (readout / verdict)

- 所有内容的唯一容器；纸色底、1px 发丝描边、下沿 2px 圆角，无阴影。
- 读数条目：左标签 + 虚线引导 + 右对齐等宽数值；下方刻度条与 12px 元数据。
- 判定卡：旋转印章 + 置信度条（墨色）+ 水分指数分区条（sage/amber/ochre/朱红，55% 不透明度）+ 理由行。

### Stamp

- 3px 双线框、-5° 旋转、朱红字；单行 20px 等宽。
- 首次出现时执行一次 `stamp-press` 落印动画（420ms，cubic-bezier(0.16, 1, 0.3, 1)）；尊重 `prefers-reduced-motion`。

### Empty & Notice

- 空状态：1px 虚线框 + 12px 句子大小写小标签 + 一句行动说明，不用插图。
- 提示条：纸色底、1px 发丝框；错误只把顶边换成 2px 朱红，并把小标签染红；不使用彩色左边框。

## Do's and Don'ts

- **Do** 让数字承担视觉重量：等宽、tabular、右对齐，字号远大于标签。
- **Do** 用虚线引导线构成“登记表”阅读路径。
- **Do** 把颜色留给状态：同一屏最多一个朱红记号 + 测量条状态色。
- **Do** 保持纸面与地面两层关系；新增区块优先用发丝线与间距分组。
- **Do** 用 11px 以上的句子大小写标签；辅助文字用 muted 色而不是淡灰。
- **Don't** 添加卡片矩阵、阴影、发光、渐变文字、玻璃拟态或彩色左边框。
- **Don't** 使用微缩大写 + 大字距标签，或用图标字体代替文字。
- **Don't** 用红色表达“置信度高”；置信度条固定墨色。
- **Don't** 给每个元素加入场动画；全站只保留印章落印这一个作者时刻。
- **Don't** 引入外部字体或图标字体；系统等宽与中文字体即可满足，离线也能保持一致。
