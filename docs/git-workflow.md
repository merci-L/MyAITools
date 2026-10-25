# Git 初始化与开源发布实操（Windows / PowerShell）

本仓库已经执行完第 2 节的初始化与首次提交。下面把完整流程和日常用法讲清楚，在别的项目里可以直接照做。

## 0. 先理解四个位置

```text
工作区（你正在改的文件）
   │  git add
   ▼
暂存区（本次提交要包含的改动）
   │  git commit
   ▼
本地仓库（.git 目录，完整的提交历史）
   │  git push
   ▼
远程仓库（GitHub / Gitee）
```

`git add` 和 `git commit` 是两个独立动作，这也是 Git 能做“选择性提交”的原因。

## 1. 一次性配置（每台电脑只做一次）

```powershell
git config --global user.name "merci_L"
git config --global user.email "1916249178@qq.com"
git config --global init.defaultBranch main
git config --global core.quotepath false   # git status 正常显示中文文件名
git config --global core.autocrlf false    # 换行符交给 .gitattributes 统一管理
git config --global pull.ff only           # 拉取只允许快进，避免多出 merge 提交
```

检查当前配置：

```powershell
git config --global --list
git config --list --show-origin   # 显示每一项来自哪个配置文件
```

> 提交记录里的邮箱是公开的。如果不想暴露私人邮箱，去 GitHub「Settings → Emails」开启
> “Keep my email addresses private”，然后用它给出的 `xxx@users.noreply.github.com` 作为 `user.email`。

## 2. 在项目目录初始化仓库（本仓库已执行）

```powershell
cd F:\项目\MyAITools
git init -b main        # 初始化，并把默认分支命名为 main
git status              # 看哪些文件未被跟踪（.gitignore 里的不会出现）
git add .               # 把全部改动放入暂存区
git status              # 再确认一次：绿色是新文件、待提交
git diff --cached       # 逐行检查即将提交的内容（重要）
git commit -m "chore: 初始化项目脚手架"
git log --oneline --graph
```

老版本 Git 不支持 `-b` 时：先 `git init`，再 `git branch -M main`。

几个要点：

- `.gitignore` 只对**尚未被跟踪**的文件生效。已经提交过的文件，之后加入 `.gitignore` 不会自动移出
- `git add .` 会把当前目录所有未忽略改动加入暂存区；想精确控制就用 `git add <文件>` 或 `git add -p`
- 第一次提交前确认没有 `.venv/`、`__pycache__/`、密钥、大文件

## 3. 提交前自检与撤销

```powershell
git status                          # 有哪些改动
git diff                            # 工作区 vs 暂存区
git diff --cached                   # 暂存区 vs 上次提交
git diff --cached | Select-String -Pattern "key|secret|token|password"   # 粗暴的密钥自查
```

撤销操作（越往下越危险）：

| 目的 | 命令 | 说明 |
| --- | --- | --- |
| 取消暂存，保留改动 | `git restore --staged <文件>` | 最安全，常用 |
| 丢弃工作区修改，回到上次提交 | `git restore <文件>` | 改动会丢失 |
| 撤销最近一次提交，改动回到暂存区 | `git reset --soft HEAD~1` | 提交历史重写，未推送时可用 |
| 撤销最近一次提交，改动回到工作区 | `git reset --mixed HEAD~1` | 同上 |
| 硬回退到某次提交 | `git reset --hard <commit>` | 危险，未保存的改动全丢 |

如果误把虚拟环境提交了（文件会一直留在历史里，先止血）：

```powershell
git rm -r --cached .venv
git commit -m "chore: 从版本库移除 .venv"
```

## 4. 推送到 GitHub

1. 在 GitHub 网页新建仓库：名字建议 `MyAITools`，**不要**勾选 README、.gitignore、License（本地已有，避免冲突）
2. 关联远程仓库并首次推送：

```powershell
git remote add origin https://github.com/<你的用户名>/MyAITools.git
git remote -v
git push -u origin main     # -u 记住上游分支，之后直接 git push
```

3. 身份认证二选一：

- **HTTPS + 凭据管理器**（Windows 上默认）：首次推送会弹窗登录，或在 GitHub 生成 Personal Access Token（Settings → Developer settings → Tokens），推送时用 token 当密码。token 只输入一次，不要写进代码或 URL
- **SSH**（推荐长期使用）：

```powershell
ssh-keygen -t ed25519 -C "1916249178@qq.com"
Get-Content $env:USERPROFILE\.ssh\id_ed25519.pub   # 复制内容
# 粘贴到 GitHub → Settings → SSH and GPG keys → New SSH key
ssh -T git@github.com                              # 看到 successfully authenticated 即可
git remote set-url origin git@github.com:<你的用户名>/MyAITools.git
```

也可以装 [GitHub CLI](https://cli.github.com/)，用 `gh auth login` 一次搞定认证，再用 `gh repo create` 直接建仓库。

## 5. 日常开发流程

```powershell
# 1) 从最新 main 切分支
git switch main
git pull
git switch -c feat/json-format

# 2) 改代码、提交（可以多次）
git add -A
git commit -m "feat(json-format): 新增 JSON 格式化工具"

# 3) 推送分支，在 GitHub 发起 Pull Request
git push -u origin feat/json-format

# 4) PR 合并后，回到 main 同步并清理分支
git switch main
git pull
git branch -d feat/json-format
git push origin --delete feat/json-format
```

建议在 GitHub 上给 `main` 开启分支保护：要求 CI 通过、至少 1 个 review、禁止直接 push。

## 6. 提交信息规范

采用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

```text
<type>(<scope>): <描述>
```

| type | 用途 | 示例 |
| --- | --- | --- |
| `feat` | 新功能/新工具 | `feat(word-count): 支持统计中文字数` |
| `fix` | 修复问题 | `fix(cli): 修正无参数时的退出码` |
| `docs` | 文档 | `docs(readme): 补充 SSH 配置说明` |
| `refactor` | 重构（不改行为） | `refactor(tools): 抽取公共读取函数` |
| `test` | 测试 | `test(word-count): 补充空文件用例` |
| `ci` | CI 配置 | `ci: 增加 Python 3.14 矩阵` |
| `chore` | 杂项/发版 | `chore: 发布 v0.2.0` |

好处：历史可读、可用工具自动生成 CHANGELOG、可按提交类型推导版本号（feat → MINOR，fix → PATCH，不兼容改动 → MAJOR）。

## 7. 打标签与发布

```powershell
# 发版前确认 main 已同步、CI 全绿
git switch main
git pull
git tag -a v0.1.0 -m "MyAITools v0.1.0"
git push origin v0.1.0
```

然后在 GitHub 仓库的「Releases」页面基于该 tag 发布说明（可直接引用 `CHANGELOG.md` 对应段落，GitHub 也能自动生成）。

发版检查清单：

1. 更新 `src/myaitools/__init__.py` 的 `__version__`
2. 更新 `CHANGELOG.md`（把 `[Unreleased]` 改成具体版本号并加日期）
3. 打 tag 并推送
4. （可选）发布到 PyPI：

```powershell
python -m pip install build twine
python -m build
python -m twine upload dist/*
```

更安全的做法是用 PyPI 的 Trusted Publishing，在 CI 里用 OIDC 发布，避免保存 token。

## 8. 常用命令速查

| 操作 | 命令 |
| --- | --- |
| 看状态 | `git status` |
| 看历史 | `git log --oneline --graph --decorate` |
| 看某文件历史 | `git log -p -- src/myaitools/cli.py` |
| 看远程 | `git remote -v` |
| 拉取并合并 | `git pull`（本仓库配置为只快进） |
| 暂存全部 | `git add -A` |
| 提交 | `git commit -m "type(scope): 描述"` |
| 推送 | `git push` |
| 切分支/新建 | `git switch main` / `git switch -c feat/xxx` |
| 查看当前分支 | `git branch --show-current` |
| 临时存改动 | `git stash` / `git stash pop` |
| 查看谁改的 | `git blame <文件>` |
| 误操作恢复参考 | `git reflog` |

## 9. 新手最常见的问题

**Q：`git status` 里中文文件名变成 `\346\226\207...`？**  
运行 `git config --global core.quotepath false`。

**Q：每次提交都提示 CRLF/LF 警告？**  
本仓库的 `.gitattributes` 已统一为仓库内 LF。再确认 `git config --global core.autocrlf false`。

**Q：`.venv` 或 `__pycache__` 被提交了？**  
先修 `.gitignore`，再 `git rm -r --cached .venv __pycache__` 并提交。

**Q：改完最后一次提交的说明怎么办？**  
`git commit --amend -m "新说明"`。已推送过则需要 `git push --force-with-lease`，并只在自己的分支上做。

**Q：合并发生冲突怎么处理？**  
打开 `git status` 列出的冲突文件，搜索 `<<<<<<<`、`=======`、`>>>>>>>`，改完删掉标记，`git add <文件>` 后 `git commit`。

**Q：不小心提交了大文件/密钥？**  
密钥先立刻吊销并更换，再处理历史（`git filter-repo` 或 BFG）。GitHub 单文件超过 100 MB 会被拒绝，大文件应使用 Git LFS。

**Q：想撤销已经 push 的提交？**  
用 `git revert <commit>` 生成一次反向提交，安全且不重写历史。

## 10. 开源仓库协作建议

- `main` 保护 + CI 必过 + PR 流程
- 用 Issue 模板收集 bug / 需求，用 PR 模板提醒自检
- 用 `CHANGELOG.md` 记录每个版本的变化
- 用 Conventional Commits 让历史与 CHANGELOG 自动对应
- 定期检查依赖更新（GitHub Dependabot 可自动开 PR）
- 发布时同步更新 README、版本号、CHANGELOG 三处，避免文档与代码不一致
