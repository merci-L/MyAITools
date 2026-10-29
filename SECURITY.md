# 安全政策

## 支持范围

本项目是本地运行的小工具集，没有托管服务端。安全更新会应用到 `main` 分支的最新版本。

## 报告漏洞

如果你发现安全问题，请**不要**公开提交 Issue，而是通过 GitHub 仓库的
**Security → Report a vulnerability** 私下报告：

<https://github.com/merci-L/MyAITools/security/advisories/new>

请在报告中说明影响范围、复现步骤和受影响版本；维护者会尽快确认并修复。

## 敏感信息

- `DEEPSEEK_API_KEY` 只从环境变量或界面输入读取，不会写入磁盘或提交到仓库
- `.env`、`report.csv`、`.cache/`、`.impeccable/`、`.taste-skill/` 已加入 `.gitignore`
- 如果误把密钥提交进仓库，请立刻到 DeepSeek 控制台吊销并更换该 Key，再清理 git 历史
