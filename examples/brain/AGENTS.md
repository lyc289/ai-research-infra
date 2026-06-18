# AGENTS.md — Research Brain contract (example)

This file is the shared operating contract for **every** agent that works in this research
brain. It is deliberately short. Real knowledge lives in `projects/<slug>/` and `wiki/`,
not here.

## The one rule that matters

> **The Markdown in this repo is the ONLY authoritative long-term memory.** Raw conversation
> transcripts, agent auto-memory, and vector stores are NOT authoritative — they are upstream
> signal or rebuildable cache. When they disagree with the Markdown, the Markdown wins.

## Memory layers (know which one you're touching)

- **L0 Raw evidence** — `raw/`, the agents' own log dirs, experiment logs. Append-only.
  NEVER fed wholesale to an agent, NEVER embedded directly. Evidence, not memory.
- **L1 Compiled brain** — THIS repo's `projects/`, `wiki/`, `registry/`. The source of truth.
- **L2 Retrieval** — optional semantic index over L1 memory cards. Rebuildable cache.
- **L3 Runtime** — the agents themselves. Read L1/L2 before work; write back to L1 after.

## Before working

1. Identify the project slug from `registry/projects.yaml`.
2. Read `projects/<slug>/agent_brief.md` (the working brief).
3. If you need more, read `projects/<slug>/PROJECT.md`, then the `wiki/` pages it links.
4. Do NOT treat raw transcripts or your own auto-memory as authoritative.

## After working (writeback as a proposed diff)

- **Decisions** (date + reason + source) → `projects/<slug>/decisions.md`
- **Timeline** events → `projects/<slug>/timeline.md`
- **Experiment outcomes** → `projects/<slug>/experiments/<exp>.md`
- **Paper-narrative changes** → `projects/<slug>/storytelling.md`
- **New / resolved open question** → `projects/<slug>/open_questions.md`
- **Durable cross-task fact** → a reviewed memory card in `projects/<slug>/memory_cards/`
- **Half-baked scratch** → `inbox/`, NOT PROJECT.md.

## Memory card rules

A durable fact becomes a `memory_cards/*.md` file ONLY if ALL of: still useful next month,
AND has a `source:`, AND has a project (or `scope: global`), AND isn't already captured
elsewhere. Every card carries front-matter (`id, type, scope, project, status, confidence,
source, evidence, created_by, created_at, supersedes, expires`). Only cards get indexed into L2.

## Hard prohibitions

- **Never** write secrets / tokens / keys / private data into any tracked file.
- **Never** bulk-embed raw transcripts or working docs. Extract atomic facts first.
- **Never** record stale-in-a-week artifacts (PR numbers, commit SHAs, "phase N done",
  file counts) as durable memory. Those belong in `timeline.md`.
- Keep this file short. It is rules + index, not an encyclopedia.
