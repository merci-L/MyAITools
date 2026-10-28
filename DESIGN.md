---
name: MyAITools
description: Precision archive cards for a quiet local toolkit.
colors:
  ground: "#EFEBE1"
  sheet: "#F9F6EC"
  ink: "#20201D"
  muted: "#676254"
  rule: "#D6D0C0"
  vermilion-tab: "#A63D2F"
  sage-ok: "#4F6B4F"
  amber-caution: "#9A6B1F"
  sidebar-ground: "#E9E4D7"
  gauge-track: "#E6E0D1"
  scrollbar-thumb: "#C9C2B0"
  ochre-water: "#B07D2E"
typography:
  wordmark:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.34em"
  headline:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.45
    letterSpacing: "0.03em"
  body:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "9.5px"
    fontWeight: 500
    letterSpacing: "0.14em"
  measure:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "30px"
    fontWeight: 500
    lineHeight: 1
    letterSpacing: "-0.01em"
  measure-sm:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "24px"
    fontWeight: 500
    lineHeight: 1
  measure-mobile:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "26px"
    fontWeight: 500
    lineHeight: 1
  numeric-sm:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.2
  title-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    lineHeight: 1.4
  input:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.65
  ui:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  ui-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    lineHeight: 1.2
  body-strong:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
    lineHeight: 1.75
  caption-sm:
    fontFamily: "Segoe UI, Microsoft YaHei, PingFang SC, Noto Sans SC, sans-serif"
    fontSize: "11.5px"
    fontWeight: 400
    lineHeight: 1.75
  meta:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "10px"
    fontWeight: 400
    lineHeight: 1.5
  unit:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "11px"
    fontWeight: 400
    lineHeight: 1.2
  stamp-main:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "19px"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0.08em"
  stamp-sub:
    fontFamily: "Cascadia Mono, Cascadia Code, Consolas, monospace"
    fontSize: "8.5px"
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: "0.22em"
rounded:
  none: "0px"
  sm: "2px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "28px"
  xl: "38px"
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

- 石色卡纸底 + 墨色字，唯一的朱红只做标签页强调、印章与告警
- 数字用等宽字体、表格数字对齐；标签用 9.5px 等宽大写、0.14em 字距
- 虚线引导线连接标签与数值；校准刻度条承担测量感的表达
- 一个作者时刻：判定印章按下时的 420ms 落印动画；其余元素不动
- 反参考：发光仪表盘卡片矩阵、大数字英雄面板、渐变文字、玻璃拟态、彩色左边框

## Colors

一张温暖的档案纸：石色底、奶油纸面、近黑墨色，一个朱红记号笔色。

### Primary

- **Vermilion Tab** (#A63D2F)：只出现在四个位置——激活标签页的顶边、主按钮 hover、判定印章、以及越过警戒阈值的测量条。它是记号，不是主题色。

### Neutral

- **Stone Ground** (#EFEBE1)：页面地面，也是浏览器滚动条与侧边栏的底色。
- **Card Sheet** (#F9F6EC)：所有读数、判定与输入控件所在的纸面。
- **Archive Ink** (#20201D)：正文、标题与数值；对比度对纸面约 15:1。
- **Muted Annotation** (#676254)：说明文字、时间戳、元数据；对纸面约 6.5:1。
- **Hairline Rule** (#D6D0C0)：1px 分隔线、虚线引导线、输入框描边。

### Secondary (state)

- **Sage OK** (#4F6B4F)：水分指数 0–20 区间。
- **Amber Caution** (#9A6B1F)：测量条 75–90% 的告警态、水分指数 21–40 区间。

### Named Rules

**The One Red Rule.** 朱红在任意一屏的覆盖面积不超过 5%，且只做“记号”用途；大面积铺红即失去档案感。

**The Paper Rule.** 所有数据必须落在 Card Sheet 上，不直接贴在 Stone Ground 上；地面只负责承载纸面。

**The Calibration Rule.** 颜色只表达真实状态：测量条的琥珀/朱红仅在越过阈值时出现，置信度条永远用墨色，不用红色暗示“警告”。

## Typography

**Display / Label Font:** Cascadia Mono（Consolas / DejaVu Sans Mono 兜底）
**Body Font:** Segoe UI（微软雅黑 / PingFang SC / Noto Sans SC 兜底）

**Character:** 中文用系统无衬线保证清晰；数字、微标签、时间戳用等宽字体，让读数看起来像被登记进表格，而不是被排版成广告。

### Hierarchy

- **Wordmark** (600, 17px, 1, 0.34em)：`MYAITOOLS`，等宽大写，小宽屏也不换行。
- **Headline** (600, 17px, 1.45)：纸面标题（系统读数 / JD 判定）。
- **Body** (400, 12.5px, 1.7)：说明文字，单行宽度受纸面限制。
- **Label** (500, 9.5px, 0.14em, uppercase)：条目名、小标题、时间戳、字段名。
- **Measure** (500, 30px, 1, tabular-nums)：核心读数；移动端降到 26px。

### Named Rules

**The Tabular Rule.** 所有测量值使用 `font-variant-numeric: tabular-nums` 并右对齐；数值变化时不允许列宽跳动。

**The Label Rule.** 微标签永远等宽、大写、带字距；中文标签不加字距，避免松散。

## Layout

单列纸面，最大内容宽度 1120px；桌面容器内边距 38.4px / 41.6px，移动端 22.4px / 17.6px。页头是一条 1px 发丝线，右侧放目录编号；标签页紧贴纸面，激活页签与纸面连成一体（纸面顶部无边框）。

纸面内部：标题 → 12.5px 说明（下留 22px）→ 主操作按钮 → 内容。读数条目 20px / 18px 内边距，条目间 1px 发丝线；磁盘区以一条 1px 墨线开始，盘符行与说明行成组。判定卡为 250px 印章列 + 自适应测量列的两栏网格，760px 以下堆叠为单列。页脚 colophon 用 34px 上外边距与发丝线收束页面。

## Elevation & Depth

平铺为主：纸面与地面之间只有一层环境阴影 `0 22px 36px -30px rgba(32,32,29,0.45)`，用来把纸从地面上“托起” 1–2mm。没有内嵌卡片、没有发光、没有多层阴影堆叠；深度来自纸面叠放关系，而不是阴影强度。

**The Flat-By-Default Rule.** 纸面之外不加阴影；悬停与激活只改变颜色与 1px 线条，不抬升元素。

## Shapes

最大圆角 2px；纸面只在下沿收 2px 圆角。边框统一 1px 实线（#D6D0C0），空状态用 1px 虚线；印章用 3px 双线框并旋转 -5°；测量条为 6px 高的实心条 + 5px 刻度带；页签标记是一枚 9px 朱红方块。不使用胶囊、卡片矩阵与装饰性多边形。

## Components

### Buttons

- **Shape:** 2px 圆角（`2px`），高 40px 左右。
- **Primary:** 墨色底 + 纸色字，`10px 22px` 内边距，12px 中文、0.12em 字距。
- **Hover / Focus:** hover 切到朱红底；focus 用 2px 朱红外描边、2px 偏移；无位移、无阴影。
- **Disabled:** 墨色 40% 透明度，保持文字可读。

### Tabs

- 抽屉页签：未激活为地面色、muted 文字；激活页签为纸面色 + 内侧 2px 朱红顶边，与下方纸面无缝相接。页签区与纸面之间只有一条 1px 发丝线。

### Inputs

- **Shape:** 2px 圆角；1px 发丝描边；纸色底。
- **Label:** 9.5px 等宽大写、0.14em 字距、muted 色。
- **Focus:** 描边变墨色，无外发光；caret 为朱红。

### Sheet (readout / verdict)

- 所有内容的唯一容器；纸色底、1px 发丝描边、下沿 2px 圆角与一层环境阴影。
- 读数条目：左标签 + 虚线引导 + 右对齐等宽数值；下方刻度条与 10px 元数据。
- 判定卡：旋转印章 + 置信度条（墨色）+ 水分指数分区条（sage/amber/ochre/朱红，55% 不透明度）+ 理由行。

### Stamp

- 3px 双线框、-5° 旋转、朱红字；主行 19px 等宽，副行 8.5px / 0.22em。
- 首次出现时执行一次 `stamp-press` 落印动画（420ms，cubic-bezier(0.16, 1, 0.3, 1)）；尊重 `prefers-reduced-motion`。

### Empty & Notice

- 空状态：1px 虚线框 + 9.5px 等宽小标签 + 一句行动说明，不用插图。
- 提示条：纸色底、1px 发丝框；错误只把顶边换成 2px 朱红，并把小标签染红；不使用彩色左边框。

## Do's and Don'ts

- **Do** 让数字承担视觉重量：等宽、tabular、右对齐，字号远大于标签。
- **Do** 用虚线引导线构成“登记表”阅读路径。
- **Do** 把颜色留给状态：同一屏最多一个朱红记号 + 测量条状态色。
- **Do** 保持纸面与地面两层关系；新增区块优先用发丝线与间距分组。
- **Don't** 添加卡片矩阵、发光阴影、渐变文字、玻璃拟态或彩色左边框。
- **Don't** 用红色表达“置信度高”；置信度条固定墨色。
- **Don't** 给每个元素加入场动画；全站只保留印章落印这一个作者时刻。
- **Don't** 引入外部字体或图标字体；等宽与中文系统字体即可满足，离线也能保持一致。
