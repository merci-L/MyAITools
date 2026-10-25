# jd-detector 使用说明

`jd-detector` 把一段职位描述（JD）发送给 DeepSeek API，判断它是否属于销售/地推岗位，并给出置信度和一句话理由。

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

> 不要把 Key 写进代码或提交到仓库。项目的 `.gitignore` 已忽略 `.env` 等文件。

## 2. 输入职位描述

三种方式任选其一：

```powershell
# a) 直接把文字作为参数
myaitools jd-detector "招聘地推专员，负责商圈拉新、扫码注册、客户开拓"

# b) 从 UTF-8 文件读取
myaitools jd-detector --file jd.txt

# c) 通过管道输入
Get-Content jd.txt -Raw | myaitools jd-detector
```

> 本机 `.venv\Scripts\myaitools.exe` 被应用控制策略拦截时，用 `python -m myaitools jd-detector ...`。

## 3. 输出

默认文本输出：

```text
结论: 是销售/地推岗位
置信度: 92%
理由: 职责以地推拉新和客户开拓为主
```

加 `--json` 输出结构化结果，方便脚本处理：

```json
{
  "is_sales": true,
  "confidence": 0.92,
  "reason": "职责以地推拉新和客户开拓为主"
}
```

## 4. 参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `text` | 职位描述文本（位置参数，可省略） | 从 `--file` 或标准输入读取 |
| `-f, --file PATH` | 从 UTF-8 文本文件读取职位描述 | 无 |
| `--json` | 输出 JSON | 关闭 |
| `--model NAME` | DeepSeek 模型名 | `deepseek-chat` |
| `--base-url URL` | API 地址，可替换为兼容网关 | `https://api.deepseek.com` |
| `--timeout SECONDS` | 请求超时秒数 | `30` |

## 5. 退出码

| 退出码 | 含义 |
| --- | --- |
| 0 | 判断成功 |
| 1 | 缺少 API Key、输入为空、网络/API 错误、结果解析失败 |
| 2 | 参数错误（如 `--timeout` 不是正数） |

## 6. 工作原理

- 调用 DeepSeek 的 OpenAI 兼容接口：`POST {base-url}/chat/completions`
- 使用 `response_format={"type": "json_object"}` 约束模型返回 JSON
- 提示词要求模型返回 `is_sales`、`confidence`、`reason` 三个字段
- 解析时会去掉 Markdown 代码围栏，并兼容 `"true"` / `"是"` 这类字符串布尔值
- 只使用 Python 标准库 `urllib`，不额外安装 HTTP 客户端依赖

## 7. 隐私与费用

- 职位描述文本会发送到 DeepSeek 服务器，请勿输入个人隐私或公司机密内容
- 调用按 DeepSeek 的 token 计费，价格见其官网
- 单元测试全部使用 mock，不会调用真实 API，也不会产生费用

## 8. 参与开发

- 实现：`src/myaitools/tools/jd_detector.py`
- 测试：`tests/test_jd_detector.py`
- 新增工具的统一流程见 [adding-a-tool.md](adding-a-tool.md)
