# Daily briefing via GitHub Actions

This repository is the scheduler wrapper. The actual fetching, merge, deduplication, scoring,
and source-health checks are run by
[`draco-agent/tech-news-digest`](https://github.com/draco-agent/tech-news-digest) during the
workflow.

## What runs

- Workflow: `.github/workflows/daily-briefing.yml`
- Schedule: every day at `01:00 UTC`, which is `09:00 Asia/Shanghai`
- Default sources: `rss,github,reddit`
- Output delivery: PushPlus WeChat message
- Artifacts: merged JSON, metadata, debug files, and rendered PushPlus Markdown

Twitter and web search are intentionally not enabled by default because they need extra API
keys. Run the workflow manually with `only=rss,github,reddit,twitter,web,trending` after adding
the relevant secrets expected by `tech-news-digest`.

## Required secret

Add this in GitHub:

`Settings -> Secrets and variables -> Actions -> New repository secret`

- Name: `PUSHPLUS_TOKEN`
- Value: your PushPlus token

Do not commit the token to the repository.

## How to check status

1. Open the GitHub repository.
2. Go to the `Actions` tab.
3. Select `Daily AI Research Briefing`.
4. Click the latest run.
5. Check whether `Run tech-news-digest pipeline` and `Render and send PushPlus briefing`
   succeeded.

## How to inspect results

In a workflow run, download the `daily-ai-research-briefing` artifact. Useful files:

- `pushplus-digest.md`: the exact message rendered for WeChat.
- `td-merged.json`: scored and deduplicated source data.
- `td-merged.meta.json`: pipeline timing, per-source counts, and health summary.
- `td-merged-debug/`: intermediate RSS/GitHub/Reddit outputs and health JSON.

## How to run manually

Open `Actions -> Daily AI Research Briefing -> Run workflow`.

Inputs:

- `hours`: recent time window, default `48`.
- `only`: sources to run, default `rss,github,reddit`.
- `dry_run`: render artifacts without sending PushPlus.
