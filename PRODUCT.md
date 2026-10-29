# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

主要用户是开发者本人及少数同事，在 Windows 本机上通过 PowerShell 启动 Streamlit 界面，完成两类短任务：查看本机资源占用、判断一段 JD 是否属于销售/地推岗位。开源项目访问者会浏览仓库与界面截图，但截图不是产品本身。

## Product Purpose

MyAITools 是一组轻量、可组合的 Python 小工具：统一的 CLI 入口 `myaitools <command>` 加一个极简 Web 界面。成功的使用是——用户在几次点击内拿到可信结果，不需要先读文档；失败的使用是——用户不确定结果从哪来、或者要在一堆控件里找下一步。

## Positioning

一个工具一个模块，CLI 与 Web 界面共用同一套工具逻辑，用户可以把任意一个工具单独拆出来用。它不是一个平台，而是一把放在桌上的多用工具。

## Operating Context

- 本机 Windows 10/11 + PowerShell，从仓库根目录运行 `streamlit run src/myaitools/app.py`
- 单页两个标签，一次使用通常在几十秒到几分钟之间，属于高频、短停留场景
- 系统雷达完全本地运行，不需要网络
- JD 脱水器需要 DeepSeek API Key（侧边栏输入或环境变量），有网络与费用成本，结果需要可解释
- 界面语言为简体中文；没有账号系统，没有数据持久化，API Key 不落盘

## Capabilities and Constraints

- 系统雷达：CPU 使用率/核心数、内存使用率/已用/可用、各磁盘容量与使用率（psutil）
- JD 脱水器：调用 DeepSeek 判断是否销售/地推岗位，展示结论、置信度、理由与本地规则计算的水分指数
- JD 脱水器支持单条（文本/管道）与批量（`--file` 读取 `.txt` / `.csv`）；批量输出 Markdown 汇总表与 `report.csv`，单条失败不中断整批
- Streamlit 自定义 CSS 可用，保留 Streamlit 的数据与交互能力，不引入新的前端框架
- 现有 CLI 行为、工具命名（`sys-radar`、`jd-detector`）与测试结构保持不变

## Brand Commitments

- 产品名 MyAITools，界面中文；项目已发布 v0.2.0
- 性格：精密、冷静、可信；不做营销式的夸张表达
- 开源仓库 https://github.com/merci-L/MyAITools 已存在，README 与 Release 是真实的对外资产

## Evidence on Hand

- 真实运行数据：系统雷达的本机采集结果；JD 脱水器实测输出（结论「是销售/地推岗位」、置信度 98%、理由文本）
- 现有 pytest / Streamlit AppTest 测试，真实界面可本地启动验证
- 无用户研究、无品牌视觉资产、无客户证言；不得编造这些内容

## Product Principles

1. 结果可信：数字与判断都要附带来源、理由和边界，不制造确定性幻觉。
2. 一眼可读：最重要的结论在首屏，用层级与颜色表达状态，而不是堆文字。
3. 工具感：界面服务于重复使用，动效与装饰克制，按钮一次到位。
4. 单一真相：GUI 与 CLI 共用同一套逻辑与文案，不复制规则。

## Accessibility & Inclusion

简体中文阅读场景；正文对比度满足 WCAG AA；状态不依赖颜色单独传达（同时给出文字）；交互使用 Streamlit 原生控件以保留键盘可达性。
