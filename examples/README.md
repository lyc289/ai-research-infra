# `examples/` — a worked, de-personalised Research Brain

This is what Build Spec 01 produces, shrunk to one fictional project so you can see the
**shape** before your agent builds your own. Nothing here is real — `widget-detector` is a
made-up project, and every path/model/host is a placeholder.

```
brain/
├── AGENTS.md                       # the operating contract (the important file)
├── registry/
│   └── projects.yaml               # slug -> project catalog
└── projects/
    └── widget-detector/
        ├── PROJECT.md              # full authoritative state
        ├── agent_brief.md          # <=150-line working brief, read FIRST
        ├── decisions.md            # dated decisions: what + why + source
        └── memory_cards/
            └── mem-2026-01-15-001.md   # one curated durable fact
```

A real brain also has `timeline.md`, `open_questions.md`, `storytelling.md`,
`experiments/`, a fuller `wiki/`, and the `scripts/` tooling — omitted here to keep the
example readable. See [`../01-research-brain.md`](../01-research-brain.md) §4 for the full
structure.
