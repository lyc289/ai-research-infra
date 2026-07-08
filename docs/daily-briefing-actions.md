# 通过 GitHub Actions 运行每日 AI 研究简报

这个仓库负责“调度与投递”。来源列表来自本仓库的
`examples/briefing-source-set.md`；实际抓取、合并、去重、评分和来源健康检查由
[`draco-agent/tech-news-digest`](https://github.com/draco-agent/tech-news-digest) 在 workflow
运行时完成。

## 运行内容

- Workflow：`.github/workflows/daily-briefing.yml`
- 定时：每天 `01:00 UTC`，也就是北京时间 `09:00`
- 默认来源类型：`rss,github`
- 来源配置：运行时从本仓库整理的 AI/research 来源名单生成
- 投递方式：PushPlus 微信推送
- 结果文件：合并后的 JSON、运行元数据、调试文件、推送用 Markdown

Twitter/X 和 Web Search 默认不启用，因为它们通常需要额外 API key。添加上游
`tech-news-digest` 所需的 secret 后，可以手动运行 workflow，并把 `only` 改成
`rss,github,twitter,web,trending`。

## 必需 secret

在 GitHub 仓库里添加：

`Settings -> Secrets and variables -> Actions -> New repository secret`

- 名称：`PUSHPLUS_TOKEN`
- 值：你的 PushPlus token

不要把 token 提交到仓库。

## 如何查看状态

1. 打开 GitHub 仓库。
2. 进入 `Actions` 页面。
3. 选择 `AI 研究每日简报`。
4. 点击最近一次 run。
5. 查看 `Run tech-news-digest pipeline` 和 `Render and send PushPlus briefing` 是否成功。

## 如何查看执行结果

在某次 workflow run 页面下载 `daily-ai-research-briefing` artifact。常用文件：

- `pushplus-digest.md`：实际发送到微信的中文 Markdown 内容。
- `td-merged.json`：评分和去重后的来源数据。
- `td-merged.meta.json`：每类来源的抓取数量、耗时和健康检查摘要。
- `tech-news-digest-sources.json`：运行时生成并传给 `tech-news-digest` 的来源覆盖配置。
- `td-merged-debug/`：RSS/GitHub 等中间抓取结果。

## 如何手动运行

打开 `Actions -> AI 研究每日简报 -> Run workflow`。

输入项：

- `hours`：抓取最近多少小时，默认 `48`。
- `only`：运行哪些来源类型，默认 `rss,github`。
- `dry_run`：只生成 artifact，不发送 PushPlus。
