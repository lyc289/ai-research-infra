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
    return (
        article.get("source_name")
        or article.get("source")
        or article.get("display_name")
        or article.get("source_type")
        or "unknown"
    )


def topic_label(topic_id: str, topic_data: dict[str, Any]) -> str:
    label = topic_data.get("label") or topic_data.get("name") or topic_id
    emoji = topic_data.get("emoji") or ""
    return f"{emoji} {label}".strip()


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
        f"# AI Research Daily Briefing",
        "",
        f"- Generated: `{generated}`",
        f"- Total after merge: `{stats.get('total_articles', '?')}`",
    ]

    if meta:
        steps = meta.get("steps", [])
        if isinstance(steps, list):
            source_bits = []
            for step in steps:
                if isinstance(step, dict):
                    source_bits.append(f"{step.get('name')}: {step.get('count', 0)}")
            if source_bits:
                lines.append(f"- Sources: {' | '.join(source_bits)}")

        health = meta.get("health_summary")
        if isinstance(health, dict):
            stale = health.get("stale_sources") or health.get("dead_sources") or []
            if stale:
                lines.append(f"- Source health: {len(stale)} stale/dead sources")

    lines.extend(["", "## Top items"])

    if not items:
        lines.append("")
        lines.append("No items were selected from this run. Check the Actions artifact for raw output.")
    else:
        for idx, (label, article) in enumerate(items, start=1):
            title = str(article.get("title") or "Untitled").strip()
            url = article_url(article)
            source = article_source(article)
            score = article.get("quality_score", 0)
            snippet = str(article.get("snippet") or article.get("summary") or "").strip()
            snippet = " ".join(snippet.split())
            if len(snippet) > 180:
                snippet = snippet[:177].rstrip() + "..."

            lines.append("")
            if url:
                lines.append(f"{idx}. **[{title}]({url})**")
            else:
                lines.append(f"{idx}. **{title}**")
            lines.append(f"   - Topic: {label}")
            lines.append(f"   - Source: {source} | Score: {score}")
            if snippet:
                lines.append(f"   - Why scan it: {snippet}")

    lines.extend(
        [
            "",
            "---",
            "Raw JSON, metadata, and debug files are saved as GitHub Actions artifacts.",
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
    parser = argparse.ArgumentParser(description="Send a tech-news-digest JSON as a PushPlus message.")
    parser.add_argument("--input", required=True, type=Path, help="Merged JSON from tech-news-digest.")
    parser.add_argument("--meta", type=Path, help="Optional .meta.json from tech-news-digest.")
    parser.add_argument("--output", required=True, type=Path, help="Markdown digest written for artifacts.")
    parser.add_argument("--title", default="AI Research Daily Briefing", help="PushPlus message title.")
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
