# Build Spec 01 — The Research Brain (unified memory)

> **How to use this file.** Don't read it as documentation. Hand it to your own
> coding agent (Claude Code, Codex, Cursor, Hermes, …) and say:
> *"Read this spec and build this system for me, adapting it to my environment."*
> The agent will interview you about your setup, then scaffold the brain and wire
> it into your tools. Everything below is written **for that agent**.

---

## 0. Agent: read this first

You are building a **personal, local-first research memory** for the user. It is the
foundation the other two systems (the nightly *dream loop*, the daily *briefing*) sit on,
so get the shape right. The whole system is plain **Markdown + Git** — no database is
required to read or trust it. Your job is to scaffold the repo, encode the operating
contract, and connect the user's AI tools to it.

Before you build anything, **discover the user's environment** (Section 2). Do **not**
hardcode paths, model names, or endpoints from any example — those are the user's to fill in.

## 1. The problem this solves

The user runs several AI agents (some local, some on remote machines) plus web chats and
doc tools. Each works fine alone, but memory is **siloed**: switch tools and you re-explain
the project; one agent doesn't know what another decided yesterday; there is no single
place that holds the authoritative state of a project. This brain is the fix: **one
authoritative long-term memory every agent reads before working and writes back to after.**

## 2. Discover the environment (do this before scaffolding)

Ask the user (or detect, then confirm). Record the answers — they parameterise everything:

1. **Which AI coding agents / assistants do you use?** (e.g. Claude Code, Codex, Cursor,
   a custom agent.) Where does each store its conversation logs on disk? *(You will need
   these paths for Build Spec 02; for now just note them.)*
2. **One machine or several?** If several, what's the SSH alias / label for each? (The brain
   tags memory by machine so a remote server's logs never get confused with the laptop's.)
3. **Where should the brain repo live?** A path the user backs up / syncs. Default to a
   `research-brain/` directory under their home unless they prefer elsewhere.
4. **What are your active projects, right now?** Get a short slug for each (e.g.
   `widget-detector`, `protein-fold`). Seed one project folder per slug. Don't invent projects.
5. **Do you want a semantic-search layer later?** (Optional L2 — see Section 7.) If yes,
   note whether they already run a local embeddings endpoint or vector store. If they don't
   know, default to **no L2** for v1; the brain is fully usable as grep-able Markdown.

> **Rule:** anything you'd otherwise hardcode (a path, a model id, a host name) is a
> question for the user, not a constant. The reference numbers in this spec are the
> author's; they are almost certainly wrong for this user.

## 3. The non-negotiable design principles

These are the load-bearing decisions. Encode them; do not "improve" them away.

- **Markdown is the single source of truth.** The committed Markdown in this repo is
  authoritative. Vector stores, agent auto-memory, and raw transcripts are *upstream signal
  or rebuildable cache* — when they disagree with the Markdown, **the Markdown wins.**
- **Raw transcripts are evidence, never memory.** Conversation logs are large, noisy, and
  may contain secrets. They are archived (Build Spec 02) and *distilled*, but are **never**
  fed wholesale to an agent and **never** embedded directly into a search index. Extract
  atomic facts first.
- **Resolve the project before doing anything.** Every task starts by mapping itself to a
  project slug in the registry, then reading that project's short working brief. No brief,
  no work.
- **Write back as a diff, never a silent rewrite.** When a task changes understanding, the
  agent *proposes* an update to the relevant file (a decision, a timeline event, an open
  question). It does not quietly overwrite authoritative state.
- **A wrong long-term memory is worse than no memory.** Bias toward *not* promoting a fact
  unless it's durable, sourced, and still useful next month. Stale-in-a-week artifacts
  (PR numbers, commit SHAs, "phase N done", file counts) are **not** durable memory — they
  belong in a timeline, not a memory card.
- **Stay tool-agnostic.** The brain is a *convention*, not a runtime. Any agent that can
  read a file and follow a contract is a valid client. Never couple it to one vendor.

## 4. Repository structure to scaffold

Create this skeleton at the chosen location. Folder names matter (the contract references
them); contents below are starting templates.

```
research-brain/
├── AGENTS.md            # the operating contract (Section 5). The most important file.
├── README.md            # 60-second orientation + the layer model.
├── .gitignore           # ignore raw/ evidence and rebuildable caches (Section 6).
├── registry/
│   ├── projects.yaml    # slug -> {title, status, dir}. Resolve a task to a slug HERE first.
│   ├── machines.yaml    # label -> {ssh alias, role}. Optional if single-machine.
│   └── sources.yaml     # optional: canonical data/code/manuscript locations per project.
├── projects/
│   └── <slug>/
│       ├── PROJECT.md         # full authoritative state (template in Section 8).
│       ├── agent_brief.md     # <=150-line working brief — READ THIS FIRST each session.
│       ├── timeline.md        # append-only dated events.
│       ├── decisions.md       # dated decisions: what + why + source.
│       ├── open_questions.md  # open / resolved questions.
│       ├── storytelling.md    # paper narrative: venue, reader pain, arc, key figures.
│       ├── experiments/       # one file per experiment: command, data, result, artifact path.
│       └── memory_cards/      # curated durable facts (template in Section 8). The only L1 that gets indexed.
├── wiki/                # cross-project knowledge
│   ├── concepts/        ├── methods/    ├── datasets/
│   ├── papers/          ├── failure_modes/  └── people/
├── inbox/               # untriaged notes/clips. Staging — NOT authoritative until promoted.
└── scripts/             # tooling lives here; Build Spec 02 fills most of it in.
    └── templates/       # PROJECT / agent_brief / memory_card / session_digest templates.
```

The **4-layer memory model** the structure encodes (put this in README.md):

```
L0  Raw evidence     raw/, the agents' own log dirs, experiment logs   (append-only; never embedded)
L1  Compiled brain   THIS repo: projects/ wiki/ registry/              (the ONLY source of truth)
L2  Retrieval        optional semantic index over L1 memory cards      (rebuildable cache; see §7)
L3  Agent runtime    the user's agents                                 (read L1/L2, write back to L1)
```

## 5. The operating contract (`AGENTS.md`)

This file is the heart of the system: it's what makes any agent "understand" the brain.
Keep it short (rules + index, not an encyclopedia — aim for < 200 lines). It must state:

**The one rule that matters**
> The Markdown in this repo is the ONLY authoritative long-term memory. Raw transcripts,
> agent auto-memory, and vector stores are not authoritative. When they disagree, the
> Markdown wins.

**Before working**
1. Identify the project slug from `registry/projects.yaml`.
2. Read `projects/<slug>/agent_brief.md` (the working brief).
3. If you need more, read `PROJECT.md`, then the `wiki/` pages it links.
4. Do not treat raw transcripts or your own auto-memory as authoritative.

**After working (writeback as a proposed diff)**
- Decisions (date + reason + source) → `decisions.md`
- Timeline events → `timeline.md`
- Experiment outcomes → `experiments/<exp>.md`
- Paper-narrative changes → `storytelling.md`
- New / resolved open question → `open_questions.md`
- A durable cross-task fact → a reviewed **memory card** (rules below)
- Half-baked scratch → `inbox/`, never `PROJECT.md`

**Memory-card rules** — a fact becomes a `memory_cards/*.md` file only if ALL of:
still useful next month, AND has a `source:` (path to raw evidence or an experiment), AND
has a project (or `scope: global`), AND isn't already captured elsewhere. Every card carries
front-matter (`id, type, scope, project, status, confidence, source, evidence, created_by,
created_at, supersedes, expires`). Only cards — never raw chat — get indexed into L2.

**Hard prohibitions**
- Never write secrets / tokens / keys / private data into any tracked file.
- Never bulk-embed raw transcripts or working docs (plans, drafts, scratch TODOs). Extract
  atomic facts first, or leave them in L0.
- Never record stale-in-a-week artifacts as durable memory.
- Keep `AGENTS.md` and any per-tool import file short. They are rules + index.

## 6. `.gitignore` (version L1, ignore L0 and caches)

L1 (the brain) is versioned. L0 raw evidence is **not** — it's large, machine-local, may
contain secrets, and is reconstructable by re-harvesting. Ignore:

```
raw/agent_logs/**
raw/papers/**
raw/experiment_logs/**
!raw/**/.gitkeep
inbox/imported_sessions/digest_*.md   # regenerated from raw
*.jsonl.meta.yaml                     # harvester sidecars
.DS_Store
__pycache__/
*.pyc
```
Tracked: `projects/`, `wiki/`, `registry/`, `scripts/`, `AGENTS.md`, `README.md`, and
`memory_cards/` (curated L1). Ignored: only raw evidence and rebuildable caches.

## 7. Optional L2 — semantic retrieval (skip for v1 unless asked)

The brain is fully usable with grep + reading `agent_brief.md`. If the user wants semantic
recall **over their memory cards** (not over raw transcripts), add a thin, **swappable**
index built only from `memory_cards/` with `status: active`:

- Treat L2 as a **rebuildable cache**, never a source of truth — it can be deleted and
  regenerated from L1 at any time.
- Use whatever vector store + embeddings endpoint the user already runs (ask in §2). If they
  have none, leave a clearly-marked `scripts/index.py` stub and a note: *"wire your embeddings
  endpoint here; the brain works without it."*
- Index **cards only**, verbatim, with `infer=False`-style direct insertion (no LLM
  re-summarisation at index time) so the indexed text equals the reviewed card text.

## 8. Templates to drop into `scripts/templates/`

**PROJECT.template.md** — authoritative per-project state:
```
# Project: <slug>
## One-line goal           — what does this ultimately try to prove?
## Current status          — stage | last meaningful update | current bottleneck | next action
## Core claim              — what does the paper/project assert?
## Evidence map            — claim A → supported by exp X; claim B → still missing
## Important decisions      — highlights; full log in decisions.md
## Active ideas            — slug — novelty — risk — validation plan
## Experiments             — slug — status — dataset — command — result — artifact path
## Storytelling            — see storytelling.md (venue / reader pain / arc / figures)
## Open questions          — see open_questions.md
## Pointers                — code / data / raw logs / manuscript / wiki pages / docs
```

**agent_brief.md** — the <=150-line file every session reads first. Distil PROJECT.md to:
goal in one sentence, current bottleneck, next concrete action, the 3–5 decisions an agent
must not relitigate, and pointers to code/data. If it grows past ~150 lines, it's doing
PROJECT.md's job — trim it.

**memory_card.template.md** — one durable fact:
```
---
id: mem-YYYY-MM-DD-NNN
type: decision | experiment_result | idea | pitfall | story | preference
scope: global | project | paper | personal
project: <slug>
status: active | superseded | rejected | archived
confidence: low | medium | high
source: <path to L0 evidence — where this came from>
evidence: <path to the L1 artifact that backs it>
created_by: <agent or human>
created_at: YYYY-MM-DD
supersedes:            # id of a card this replaces, if any
expires:              # YYYY-MM-DD or null
---
# <one-line claim — the fact itself>
## Claim       — the durable, falsifiable statement
## Evidence    — run path / commit / table / figure / key metric
## Implication — what an agent should DO or NOT DO because of this
## Links       — [[projects/<slug>/...]]  [[wiki/<area>/<page>]]
```

## 9. Wire the user's agents into the brain

For **each** agent the user named in §2, make the contract load automatically every session:

- If the agent has a project- or home-level instruction file (e.g. a `CLAUDE.md`,
  `AGENTS.md`, a Cursor rules file, a custom system prompt), add a few lines that **import /
  point at** `research-brain/AGENTS.md` and state the before/after contract. Guaranteed-load
  beats a tool the model might forget to call.
- Prefer the always-loaded instruction file over an optional MCP/tool when the goal is
  *"never forget the contract."* (An optional tool can supplement, not replace, it.)
- Verify: open each agent fresh, give it a trivial task in a project dir, and confirm it
  reads `agent_brief.md` before acting and proposes a writeback diff after.

## 10. Acceptance criteria (how the user knows it's built)

- [ ] `research-brain/` exists with the structure in §4 and is a git repo.
- [ ] `AGENTS.md` encodes the one rule, before/after contract, card rules, and prohibitions.
- [ ] `registry/projects.yaml` lists the user's real project slugs; each has a folder with
      at least `PROJECT.md` + `agent_brief.md`.
- [ ] `.gitignore` keeps `raw/` and caches out of version control; `projects/ wiki/ registry/`
      are tracked.
- [ ] At least one agent loads the contract automatically and demonstrably reads the brief
      before working.
- [ ] (If L2 chosen) memory cards — and only cards — can be indexed and recalled.

## 11. Don't

- **Don't** invent the user's projects, paths, model names, or machine labels — ask.
- **Don't** embed or dump raw transcripts anywhere an agent reads them in bulk.
- **Don't** make the brain depend on a specific vendor, model, or running service to be
  *readable*. Markdown + git must stand alone.
- **Don't** let `agent_brief.md` bloat into a second PROJECT.md.
- **Don't** commit secrets, tokens, or private/participant-level data — ever.
- **Don't** over-engineer v1. Ship the Markdown brain + contract first; add L2 and the
  dream loop (Build Spec 02) only once the foundation is real.

## 12. Report back

When done, print: the brain's path; the project slugs seeded; which agents were wired in
and how (which instruction file you edited); whether L2 was set up or deferred; and the exact
commands the user runs to (a) add a new project and (b) verify an agent obeys the contract.
