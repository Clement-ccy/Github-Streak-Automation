# GitHub Streak Automation

一个用 GitHub Actions 每天自动创建一次提交并推送到当前仓库的项目。默认每天北京时间 08:10 运行，更新 `activity/streak.md`，如果当天已经更新过则不会重复提交；也可以手动触发并选择强制更新。

## 项目结构

```text
.
├── .github/workflows/daily-commit.yml  # GitHub Actions 定时任务
├── activity/streak.md                  # 每日自动更新的日志文件
├── scripts/update_streak.py            # 生成每日日志条目的脚本
└── tests/test_update_streak.py         # 脚本单元测试
```

## 使用步骤

1. 在 GitHub 创建一个名为 `Github-Streak-Automation` 的仓库。
2. 如果你当前是在一个普通文件夹里创建项目，先初始化并推送到 GitHub：

   ```bash
   git init
   git add .
   git commit -m "chore: initialize GitHub streak automation"
   git branch -M main
   git remote add origin https://github.com/<your-username>/Github-Streak-Automation.git
   git push -u origin main
   ```

   如果你是先 clone 了 GitHub 仓库再复制这些文件，只需要执行 `git add .`、`git commit` 和 `git push`。

3. 确认这些文件已经在 GitHub 仓库的默认分支上；GitHub Actions 的定时任务只会从默认分支读取 workflow。
4. 打开仓库的 **Settings → Actions → General → Workflow permissions**，选择 **Read and write permissions**，这样 workflow 才能推送提交。
5. 如果默认分支有保护规则，需要允许这个 workflow 或 `GITHUB_TOKEN` 推送；否则定时任务会运行到 `git push` 时失败。
6. 可选但推荐：在 **Settings → Secrets and variables → Actions → Variables** 中添加：
   - `GIT_AUTHOR_NAME`：你的 GitHub 用户名或希望展示的提交作者名。
   - `GIT_AUTHOR_EMAIL`：你的 GitHub 已验证邮箱，或 GitHub 提供的 noreply 邮箱。

> 如果提交作者邮箱没有关联到你的 GitHub 账号，提交可能不会计入你的个人贡献图。
> 如果不想公开个人邮箱，建议使用 GitHub 提供的 noreply 邮箱。

## 手动运行

在 GitHub 仓库页面进入 **Actions → Daily GitHub Streak Commit → Run workflow**，可以手动触发一次。选择 `force=true` 时，即使当天已经有日志条目，也会再次写入并提交。

本地也可以运行：

```bash
python scripts/update_streak.py --force
```

## 本地验证

```bash
python -m compileall scripts tests
python -m unittest discover -s tests
```

## 自定义时间和文件

默认配置在 `.github/workflows/daily-commit.yml` 中：

- `STREAK_TIMEZONE: Asia/Shanghai`
- `STREAK_FILE: activity/streak.md`
- `cron: "10 0 * * *"`，表示每天 UTC 00:10，也就是北京时间 08:10。

如果要改运行时间，只需要修改 workflow 里的 cron 表达式。GitHub Actions 的 `schedule` 使用 UTC 时间。

## 说明

这个项目会对仓库中的日志文件产生真实变更并提交。请合理使用自动化，不要将它用于垃圾提交或违反平台规则的行为。
