#!/usr/bin/env python3
"""Render tech-news-digest output and send it through PushPlus."""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUSHPLUS_URL = "https://www.pushplus.plus/send"

TOPIC_LABELS = {
    "llm": "大语言模型",
    "ai-agent": "智能体",
    "frontier-tech": "前沿技术",
    "crypto": "加密与区块链",
}

SOURCE_TYPE_LABELS = {
    "rss": "订阅源",
    "github": "代码仓库发布",
    "github-trending": "代码仓库趋势",
    "github_trending": "代码仓库趋势",
    "trending": "代码仓库趋势",
    "reddit": "社区讨论",
    "twitter": "社交媒体",
    "web": "网页搜索",
}

STEP_LABELS = {
    "RSS": "订阅源",
    "GitHub": "代码仓库发布",
    "GitHub Trending": "代码仓库趋势",
    "Reddit": "社区讨论",
    "Twitter": "社交媒体",
    "Web": "网页搜索",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def article_url(article: dict[str, Any]) -> str:
    return (
        article.get("link")
        or article.get("url")
        or article.get("external_url")
        or article.get("reddit_url")
        or ""
    )


def article_source(article: dict[str, Any]) -> str:
    raw_type = str(
        article.get("source_type")
        or article.get("source")
        or article.get("source_name")
        or article.get("display_name")
        or ""
    ).strip().lower()
    return SOURCE_TYPE_LABELS.get(raw_type, "来源")


def topic_label(topic_id: str, topic_data: dict[str, Any]) -> str:
    label = TOPIC_LABELS.get(topic_id) or topic_data.get("label") or topic_data.get("name") or topic_id
    emoji = topic_data.get("emoji") or ""
    return f"{emoji} {label}".strip()


def chinese_reason(article: dict[str, Any]) -> str:
    raw_type = str(
        article.get("source_type")
        or article.get("source")
        or article.get("source_name")
        or article.get("display_name")
        or ""
    ).strip().lower()
    if raw_type in {"github", "github-trending", "github_trending", "trending"}:
        return "代码仓库出现更新或热度信号，适合快速判断是否与你的工具链和研究工作相关。"
    if raw_type == "rss":
        return "来自精选研究博客或机构来源，适合纳入今日研究动态快速浏览。"
    if raw_type == "reddit":
        return "来自社区讨论，适合观察研究者和开发者正在关注的问题。"
    if raw_type in {"twitter", "web"}:
        return "来自外部动态来源，适合作为今日趋势的补充线索。"
    return "该条目在本次筛选中得分较高，适合快速浏览并判断是否需要深入阅读。"


def top_articles(data: dict[str, Any], per_topic: int, total_limit: int) -> list[tuple[str, dict[str, Any]]]:
    picked: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    topics = data.get("topics", {})
    if not isinstance(topics, dict):
        return picked

    for topic_id, topic_data in topics.items():
        if not isinstance(topic_data, dict):
            continue
        articles = topic_data.get("articles", [])
        if not isinstance(articles, list):
            continue
        ranked = sorted(
            [a for a in articles if isinstance(a, dict)],
            key=lambda a: a.get("quality_score", 0),
            reverse=True,
        )
        label = topic_label(topic_id, topic_data)
        for article in ranked[:per_topic]:
            title = str(article.get("title") or "").strip().lower()
            dedup_key = article_url(article).strip().lower() or title
            if dedup_key and dedup_key in seen:
                continue
            if dedup_key:
                seen.add(dedup_key)
            picked.append((label, article))

    picked.sort(key=lambda item: item[1].get("quality_score", 0), reverse=True)
    return picked[:total_limit]


def render_markdown(data: dict[str, Any], meta: dict[str, Any] | None, per_topic: int, total_limit: int) -> str:
    now = datetime.now(timezone.utc).astimezone()
    stats = data.get("output_stats", {})
    generated = data.get("generated") or now.isoformat(timespec="seconds")
    items = top_articles(data, per_topic=per_topic, total_limit=total_limit)

    lines = [
        f"# AI 研究每日简报",
        "",
        f"- 生成时间：`{generated}`",
        f"- 合并去重后条目数：`{stats.get('total_articles', '?')}`",
    ]

    if meta:
        steps = meta.get("steps", [])
        if isinstance(steps, list):
            source_bits = []
            for step in steps:
                if isinstance(step, dict):
                    step_name = str(step.get("name") or "")
                    source_bits.append(f"{STEP_LABELS.get(step_name, step_name)}：{step.get('count', 0)}")
            if source_bits:
                lines.append(f"- 来源计数：{' ｜ '.join(source_bits)}")

        health = meta.get("health_summary")
        if isinstance(health, dict):
            stale = health.get("stale_sources") or health.get("dead_sources") or []
            if stale:
                lines.append(f"- 来源健康：{len(stale)} 个来源可能失效或长期无更新")

    lines.extend(["", "## 今日精选"])

    if not items:
        lines.append("")
        lines.append("本次没有筛选出条目。可以查看本次运行的结果文件。")
    else:
        for idx, (label, article) in enumerate(items, start=1):
            title = str(article.get("title") or "Untitled").strip()
            url = article_url(article)
            source = article_source(article)
            score = article.get("quality_score", 0)

            lines.append("")
            if url:
                lines.append(f"{idx}. **[{title}]({url})**")
            else:
                lines.append(f"{idx}. **{title}**")
            lines.append(f"   - 主题：{label}")
            lines.append(f"   - 来源类型：{source} ｜ 分数：{score}")
            lines.append(f"   - 为什么值得看：{chinese_reason(article)}")

    lines.extend(
        [
            "",
            "---",
            "原始数据、运行元数据和调试文件已保存为本次运行的结果文件。",
        ]
    )
    return "\n".join(lines)


def send_pushplus(token: str, title: str, content: str) -> dict[str, Any]:
    payload = {
        "token": token,
        "title": title,
        "content": content,
        "template": "markdown",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        PUSHPLUS_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"PushPlus HTTP {exc.code}: {raw}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"PushPlus request failed: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Send a tech-news-digest JSON as a PushPlus message.")
    parser.add_argument("--input", required=True, type=Path, help="Merged JSON from tech-news-digest.")
    parser.add_argument("--meta", type=Path, help="Optional .meta.json from tech-news-digest.")
    parser.add_argument("--output", required=True, type=Path, help="Markdown digest written for artifacts.")
    parser.add_argument("--title", default="AI 研究每日简报", help="PushPlus message title.")
    parser.add_argument("--per-topic", type=int, default=3, help="Maximum items considered per topic.")
    parser.add_argument("--limit", type=int, default=7, help="Maximum items sent in the digest.")
    parser.add_argument("--dry-run", action="store_true", help="Render only; do not send PushPlus.")
    args = parser.parse_args()

    data = load_json(args.input)
    meta = load_json(args.meta) if args.meta and args.meta.exists() else None
    content = render_markdown(data, meta, per_topic=args.per_topic, total_limit=args.limit)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")

    if args.dry_run:
        print(content)
        return 0

    token = os.environ.get("PUSHPLUS_TOKEN")
    if not token:
        print("PUSHPLUS_TOKEN is not set; rendered digest but did not send.", file=sys.stderr)
        return 2

    result = send_pushplus(token=token, title=args.title, content=content)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    code = result.get("code")
    if code not in (None, 200, "200"):
        print(f"PushPlus returned non-success response: {html.escape(str(result))}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
