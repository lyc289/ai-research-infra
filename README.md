# research-infra

**Build-spec prompts for a personal, local-first AI research infrastructure.**

Not a framework. Not a library. Three Markdown specs you hand to *your own* coding agent —
Claude Code, Codex, Cursor, Hermes, whatever you use — and it builds the system **for you,
adapted to your environment.** You bring the agent and the judgment; these specs bring the
design and the hard-won pitfalls.

This is the open-source companion to the essay
[*Staying Grounded in Fast-Paced AI Research*](https://jxtse.github.io). The essay argues
*why* you need a research infrastructure; this repo is the *executable form* of that argument.

---

## Why build-specs, not a framework

The most valuable part of any personal research setup is **how it's designed and the traps it
avoids** — not one person's exact wiring to their local model server, their vector store, their
scheduler. That wiring is the least portable thing there is; ship it as a framework and most
people bounce off the install before they ever get the idea.

So instead of shipping my implementation, I'm shipping the **design as a prompt**. Your coding
agent reads the spec, interviews you about *your* tools and paths, and stands the system up in
*your* world. The spec carries the architecture and the principles; your agent carries the
adaptation. That's also just… the whole thesis of the essay — let the agent do the
domain-specific translation work.

## The three systems

| # | Spec | What your agent builds | The principle it encodes |
|---|------|------------------------|--------------------------|
| **01** | [The Research Brain](01-research-brain.md) | A unified, local-first **memory** every agent reads before working and writes back to after — plain Markdown + Git, no database required. | *Markdown is the single source of truth; raw transcripts are evidence, never memory.* |
| **02** | [The Dream Loop](02-dream-loop.md) | A **nightly offline pipeline** that harvests the day's agent conversations and distils durable facts into the brain — reversibly, under guardrails. | *Gated full-auto: additive only, every auto-write tagged and one-command reversible.* |
| **03** | [The Daily Briefing](03-daily-briefing.md) | A once-a-day **information filter**: many sources in, deterministic ranking, LLM only at the last step, 5–7 items out. | *If code can do it, don't use an agent. Deterministic rules first, LLM last.* |

**Dependencies:** 02 builds on 01. 03 is independent but sharper when connected to 01.
Start with 01 — it's the foundation and it's useful on its own.

## How to use

1. Open the spec you want (start with [`01-research-brain.md`](01-research-brain.md)).
2. Give it to your coding agent: *"Read this spec and build this system for me, adapting it
   to my environment. Interview me first."*
3. Answer its questions about your tools, paths, models, and scheduler. **Every number, path,
   and model name in these specs is mine — they're placeholders for yours.**
4. Review what it scaffolds, then iterate. The specs include acceptance criteria so you can
   check the result.

There's a worked, fully de-personalised example brain under [`examples/`](examples/) so you
can see the *shape* of the output before you build your own.

## How this maps to harness engineering

If you think about AI agents in terms of the **harness** — the scaffolding around a model that
actually determines what it can do (its tool surface, its memory schema, its operating
principles, how its context is framed) — then this repo is just *a harness for your own
research workflow*, taught one dimension at a time:

- **Memory schema + operating principles** → Build Spec 01 (the brain + its contract)
- **Context framing** (what gets into the agent's working context) → Build Spec 03 (the briefing)
- **Tool surface** → your own skills/tools (see below), with the brain as their shared memory
- **Keeping the harness current over time** → Build Spec 02 (the dream loop)

Building your own research infrastructure is, in the end, dogfooding harness engineering on
yourself.

## Related

- [`jxtse/scientific-research-skills`](https://github.com/jxtse/scientific-research-skills) —
  the **tool surface**: concrete research skills for coding agents (literature search,
  full-text harvest, related-work survey, figure generation, Zotero management, …). These are
  the *capabilities*; the brain in this repo is the *shared memory* they read and write.

## A few honest caveats

- **These are reference designs, not turnkey software.** Expect to adapt. Your agent does most
  of the adapting, but you own the result.
- **I won't be supporting your specific stack.** Fork it, change it, make it yours. Issues that
  improve the *specs* (clearer steps, missing pitfalls) are very welcome; "it doesn't run on my
  machine" mostly won't be, because there's nothing here that "runs" — your agent builds that part.
- **Never let an agent commit secrets or governed data.** The specs say this repeatedly; it
  matters. Keep tokens, keys, and participant-level data out of any tracked file.

## License

MIT. Use it, fork it, build your own.
