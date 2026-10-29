# jd-detector 使用说明

`jd-detector` 把一段或多段职位描述（JD）发送给 DeepSeek API，判断是否属于销售/地推岗位，并给出置信度与一句话理由；批量模式还会生成 Excel 可直接打开的 `report.csv`。

## 1. 配置 API Key

1. 到 [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) 创建 API Key
2. 设置环境变量 `DEEPSEEK_API_KEY`

PowerShell（仅当前窗口有效）：

```powershell
$env:DEEPSEEK_API_KEY = "sk-你的key"
```

PowerShell（写入当前用户，永久有效，重新打开窗口生效）：

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-你的key", "User")
```

bash / zsh：

```bash
export DEEPSEEK_API_KEY="sk-你的key"
```

> 不要把 Key 写进代码或提交到仓库。项目的 `.gitignore` 已忽略 `.env` 与 `report.csv` 等文件。

## 2. 单条输入

三种方式任选其一：

```powershell
# a) 直接把文字作为参数
myaitools jd-detector "招聘地推专员，负责商圈拉新、扫码注册、客户开拓"

# b) 通过管道输入
Get-Content jd.txt -Raw | myaitools jd-detector

# c) 交互式粘贴（Windows 下按 Ctrl+Z 回车结束）
myaitools jd-detector
```

> 本机 `.venv\Scripts\myaitools.exe` 被应用控制策略拦截时，用 `python -m myaitools jd-detector ...`。

## 3. 批量分析

`--file` 用于批量流水线：读取 `.txt` 或 `.csv`，自动切割成多条 JD 后逐条调用 API。

- **TXT**：按连续空行或单独一行 `---` 切割
- **CSV**：每行一条；`岗位` / `title` / `position` 列作为岗位简称，`职位描述` / `jd` / `description` 列作为正文；没有内容列时把整行拼成一条

```powershell
myaitools jd-detector --file jds.txt
myaitools jd-detector --file jds.csv --report my-report.csv
```

终端输出（Markdown 表格）：

```text
| 序号 | 岗位简称 | 岗位性质 | 水分指数 |
| --- | --- | --- | --- |
| 1 | 地推专员 | 销售/地推 | 38/100 |
| 2 | 后端开发 | 非销售/地推 | 12/100 |
| 3 | 电话销售 | 分析失败 | 55/100 |

共 3 条：成功 2 条，失败 1 条
报告已写入：F:\项目\MyAITools\report.csv
```

- 某一条超时或报错**不会中断整批**，该行岗位性质记为「分析失败」，水分指数仍由本地关键词规则计算
- `report.csv` 使用 UTF-8 BOM 编码，Excel 可直接打开；列与终端表格一致
- 默认报告路径为当前目录的 `report.csv`，可用 `--report` 指定其他路径

## 4. 单条输出

默认文本输出：

```text
结论: 是销售/地推岗位
置信度: 92%
理由: 职责以地推拉新和客户开拓为主
```

单条模式加 `--json` 输出结构化结果，方便脚本处理：

```json
{
  "is_sales": true,
  "confidence": 0.92,
  "reason": "职责以地推拉新和客户开拓为主"
}
```

## 5. 参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `text` | 单条职位描述（位置参数，可省略） | 从标准输入读取 |
| `-f, --file PATH` | 读取 `.txt` / `.csv` 并进入批量分析 | 无（单条模式） |
| `--report PATH` | 批量分析的 CSV 报告路径 | `report.csv` |
| `--json` | 单条模式下输出 JSON | 关闭 |
| `--model NAME` | DeepSeek 模型名 | `deepseek-chat` |
| `--base-url URL` | API 地址，可替换为兼容网关 | `https://api.deepseek.com` |
| `--timeout SECONDS` | 单条请求超时秒数 | `30` |

## 6. 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 执行完成；批量模式下个别条目失败也返回 0（失败项已在表格/报告中标记） |
| 1 | 缺少 API Key、输入为空、文件不可读/格式不支持、单条 API 错误、报告写入失败 |
| 2 | 参数错误（如 `--timeout` 不是正数） |

## 7. 工作原理

- 单条模式：调用 DeepSeek 的 OpenAI 兼容接口 `POST {base-url}/chat/completions`
- 批量模式：本地切割文件 → 逐条调用同一套 `classify()` → 汇总结果 → 写 CSV
- 使用 `response_format={"type": "json_object"}` 约束模型返回 JSON
- 提示词要求模型返回 `is_sales`、`confidence`、`reason` 三个字段
- 解析时会去掉 Markdown 代码围栏，并兼容 `"true"` / `"是"` 这类字符串布尔值
- 水分指数完全在本地按关键词规则计算，不额外消耗 API
- 只使用 Python 标准库 `urllib` / `csv`，不额外安装 HTTP 客户端依赖

## 8. 隐私与费用

- 职位描述文本会发送到 DeepSeek 服务器，请勿输入个人隐私或公司机密内容
- 批量模式会为每条 JD 调用一次 API，按 DeepSeek 的 token 计费
- 单元测试全部使用 mock，不会调用真实 API，也不会产生费用

## 9. 参与开发

- 实现：`src/myaitools/tools/jd_detector.py`
- 测试：`tests/test_jd_detector.py`（单条）、`tests/test_jd_batch.py`（批量切割/遍历/报告）
- 新增工具的统一流程见 [adding-a-tool.md](adding-a-tool.md)
