#!/usr/bin/env python3
"""Build a tech-news-digest source overlay from this repo's curated briefing appendix."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TOPICS = ["llm", "ai-agent", "frontier-tech"]


MANUAL_FEEDS = [
    ("Anthropic Blog", "https://news.google.com/rss/search?q=site:anthropic.com&hl=en-US&gl=US&ceid=US:en", True),
    ("Google DeepMind Blog", "https://deepmind.google/blog/rss.xml", True),
]

GITHUB_REPOS = [
    "vllm-project/vllm",
    "ollama/ollama",
    "huggingface/transformers",
    "pytorch/pytorch",
    "meta-llama/llama",
    "deepseek-ai/DeepSeek-V3",
    "langchain-ai/langchain",
    "run-llama/llama_index",
    "microsoft/autogen",
    "crewAIInc/crewAI",
    "langgenius/dify",
    "mem0ai/mem0",
    "modelcontextprotocol/servers",
    "openai/openai-python",
    "anthropics/anthropic-sdk-python",
    "agno-agi/agno",
]


def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "source"


def load_default_sources(defaults_path: Path) -> list[dict[str, Any]]:
    if not defaults_path.exists():
        return []
    data = json.loads(defaults_path.read_text(encoding="utf-8"))
    return [s for s in data.get("sources", []) if isinstance(s, dict)]


def parse_curated_rss(markdown_path: Path) -> list[dict[str, Any]]:
    text = markdown_path.read_text(encoding="utf-8")
    sources: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "http" not in line or "`" not in line:
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[1].lower() == "source":
            continue

        priority = "★" in cells[0]
        name = re.sub(r"`", "", cells[1]).strip()
        match = re.search(r"`(https?://[^`]+)`", cells[2])
        if not match:
            continue
        url = match.group(1).strip()
        if url in seen_urls:
            continue
        seen_urls.add(url)

        sources.append(
            {
                "id": f"jxtse-{slugify(name)}-rss",
                "type": "rss",
                "name": name,
                "url": url,
                "enabled": True,
                "priority": priority,
                "topics": TOPICS,
                "note": "From jxtse/ai-research-infra examples/briefing-source-set.md",
            }
        )

    for name, url, priority in MANUAL_FEEDS:
        if url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append(
            {
                "id": f"jxtse-{slugify(name)}-rss",
                "type": "rss",
                "name": name,
                "url": url,
                "enabled": True,
                "priority": priority,
                "topics": TOPICS,
                "note": "From jxtse/ai-research-infra examples/briefing-source-set.md",
            }
        )

    return sources


def github_sources() -> list[dict[str, Any]]:
    result = []
    for repo in GITHUB_REPOS:
        result.append(
            {
                "id": f"jxtse-{slugify(repo)}-github",
                "type": "github",
                "name": repo,
                "repo": repo,
                "enabled": True,
                "priority": True,
                "topics": ["ai-agent", "frontier-tech"],
                "note": "GitHub release feed listed in jxtse/ai-research-infra examples/briefing-source-set.md",
            }
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate tech-news-digest overlay config from the curated jxtse source list.")
    parser.add_argument("--source-md", type=Path, default=Path("examples/briefing-source-set.md"))
    parser.add_argument("--defaults", type=Path, required=True, help="tech-news-digest default sources.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    default_sources = load_default_sources(args.defaults)
    disabled_defaults = [
        {
            "id": source["id"],
            "type": source.get("type", "rss"),
            "name": source.get("name", source["id"]),
            "enabled": False,
            "priority": bool(source.get("priority", False)),
            "topics": source.get("topics", TOPICS),
        }
        for source in default_sources
        if source.get("id")
    ]

    curated_sources = parse_curated_rss(args.source_md) + github_sources()
    output = {
        "_description": "由 jxtse/ai-research-infra 的精选 AI 研究简报来源生成。默认来源已禁用，因此 workflow 会按本仓库的来源名单运行。",
        "sources": disabled_defaults + curated_sources,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / "tech-news-digest-sources.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote={out_path}")
    print(f"curated_sources={len(curated_sources)} disabled_defaults={len(disabled_defaults)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
