# Build Spec 02 — The Dream Loop (offline memory distillation)

> **How to use this file.** Hand it to your own coding agent and say *"build this for me,
> adapting it to my environment."* It assumes Build Spec 01 (the Research Brain) is already
> in place. Everything below is written **for that agent**.

---

## 0. Agent: read this first

You are building a **nightly offline pipeline** that keeps the Research Brain (Build Spec 01)
fed and current *without the user lifting a finger*. The metaphor is "dreaming": while the
user sleeps, the system collects the day's agent conversations, distils durable facts from
them, and files high-confidence facts into the brain's memory cards — all reversibly and
under guardrails.

This is an **upgrade**, not a foundation. The brain works without it (the user can write
cards by hand). Build it only after Build Spec 01 exists and the user wants maintenance
automated. **Discover the environment first (Section 2).**

## 1. The problem this solves

Durable facts get discovered all day — a config gotcha, a decision and its reason, an
experiment number — but they live and die inside individual agent transcripts. Nobody
re-reads yesterday's logs to extract them, so the brain slowly goes stale. The dream loop
closes that gap: **harvest → digest → promote → (optionally) index**, every night.

```
agents' log dirs  --harvest-->  raw/agent_logs/  --digest-->  bounded skeleton
   (+ remote hosts)                                              |
                                              (LLM extracts atomic durable facts)
                                                                 v
                                  high-confidence  -> projects/<slug>/memory_cards/auto_*.md  (L1)
                                  med/low          -> inbox/auto_promoted_review/  (human glance)
                                                                 |
                                                          --index--> optional L2 cache
```

**Invariant (inherited from Build Spec 01): raw transcripts are NEVER embedded and NEVER
fed wholesale to the LLM.** Only a bounded, summarised slice is sent; only reviewed-shape
cards land in L1.

## 2. Discover the environment (before writing any script)

1. **Agent log locations.** For each agent the user uses, where are the raw conversation
   logs on disk, and what format? (Common shapes: a per-project tree of JSONL rollouts; a
   flat sessions dir; one file per chat.) You need a reader per format. Confirm the actual
   paths — do not assume.
2. **Remote machines.** Does the user run agents on other hosts (a GPU server, a lab box)?
   If yes, get the SSH alias per host and confirm key-based login works non-interactively.
   Those logs get pulled into the same brain, tagged by machine.
3. **An LLM provider for the distiller.** The nightly job needs *some* LLM to turn skeletons
   into facts. The only universal requirement is this: **the user configures their own
   provider.** Treat it as a provider-agnostic abstraction — `base_url`, `api_key`, `model`
   in one config block — so the pipeline code never cares whether that points at a cloud API
   (OpenAI, Anthropic, a router) or a local server (Ollama, vLLM, llama.cpp, LM Studio). Ask:
   - Which provider will you use, and what are its `base_url` / `api_key` / `model`? Put them
     in config or env, never hardcoded.
   - It runs **unattended at night**, so the credential/endpoint must work non-interactively.
   - Whatever you pick, **verify its actual behaviour before trusting it** — providers differ
     in ways that matter for batch structured extraction (see Section 4).
4. **A scheduler.** What runs jobs on a schedule on the user's machine? (cron, launchd,
   systemd timers, Task Scheduler, or the user's agent platform's own cron.) You'll register
   the nightly job with whatever they have.
5. **Compliance limits.** Does any project forbid sending its data to a cloud provider (e.g.
   governed datasets under a data-use agreement)? If so, the distiller for those projects must
   point at a provider that satisfies the restriction (often a self-hosted/local one), or skip
   them entirely. Ask explicitly — this is a legal line, not a preference.

> Every reference number, model id, path, and host in this spec is the author's. Replace
> all of them with the user's answers.

## 3. The non-negotiable design principles

- **Gated full-auto, additive only.** The pipeline may write durable cards unsupervised, but
  **only additively**: a new card never edits, deletes, or overwrites an existing one.
  Collisions are skipped or linked via `supersedes`, never destructive.
- **Everything auto-written is tagged and reversible.** Every auto card carries
  `created_by: <dream pipeline>` + `auto_promoted: true` in front-matter, so a single
  command finds and removes them all. Always surface that rollback command to the user.
- **Confidence gating.** Only *high-confidence* facts go straight into the authoritative
  memory-card layer. Medium/low go to an `inbox/auto_promoted_review/` folder for a human
  glance — never into the authoritative layer.
- **Idempotent + de-duplicated.** Re-running must not duplicate work: harvest by hardlink and
  skip existing destinations; keep a content-hash ledger so the same fact isn't re-carded on
  a later night.
- **Fail safe, never hang.** A missing brain, an unreachable host, or a dead LLM endpoint
  must degrade gracefully (skip that step, log it) — never block the night or corrupt state.
- **Quiet by default.** The nightly job speaks to the user **only** when it actually did
  something worth reporting (wrote cards) or something broke. Silent nights stay silent.

## 4. Verify your provider; handle the pipeline-level pitfalls

Two different classes of caveat live here. Don't confuse them.

**(A) Provider behaviour varies — verify yours, don't assume.** The author hit specific bugs
on one specific endpoint; *you* may hit none, or different ones, depending on the provider you
configured in §2.3. So the rule is **test your provider on a real batch before trusting it**,
and watch for these *categories* of difference (examples, not predictions):

- **Some models return empty/garbage on batch structured-extraction.** Certain "reasoning"
  models can spend their token budget on internal reasoning and hand back empty message
  content for a JSON-extraction prompt; some small local models ignore the format instruction.
  If your test batch comes back empty or unparseable, switch to a standard chat model, disable
  reasoning, or raise the token budget — whatever your provider needs.
- **Structured-output knobs aren't portable.** `response_format: json_object`, JSON-schema
  mode, and tool/function-calling are supported unevenly across providers. Don't depend on any
  one of them. Prompt for strict JSON and **parse the first `{...}` block defensively**, so the
  pipeline works regardless of which knobs your provider honors.
- **Local endpoints can get trapped by a shell proxy.** If the user's shell exports
  `http_proxy/https_proxy/all_proxy` (common with VPN/Clash-style setups), an HTTP client may
  route even `127.0.0.1` calls through the proxy and hang. *If* your provider is local, unset
  those vars (or set `no_proxy`) before the call. (Irrelevant if you use a cloud provider.)

**(B) Pipeline-level pitfalls — these are general, handle them regardless of provider:**

- **Durable facts cluster at the END of a session.** A session opens with "let me look
  around" and *ends* with the decision/result. When you bound the transcript slice you send
  to the LLM, take **head + tail** (e.g. first 3 and last 5 turns), not just the opening.
- **Transcripts have minor user/assistant misalignment.** Tell the distiller to read for
  *content*, not turn order.
- **Hardlink across filesystems fails.** Harvest by hardlink for zero extra bytes on the same
  filesystem, but fall back to a copy automatically when crossing filesystems.

## 5. Components to build (under the brain's `scripts/`)

Adapt names/paths to the user's setup. Keep each script single-purpose and stdlib-only where
possible (the distiller needs only an HTTP client).

1. **Harvesters** — one per agent log format. Copy/hardlink new log files from the agent's
   dir into `raw/agent_logs/<agent>/<machine>/<slug>/`, with a sidecar of metadata. Infer the
   project slug from the session's working directory; unmatched → an `_unsorted/` bucket the
   user can later route by adding a pattern. Support `--since DATE` and `--dry-run`.
2. **Remote harvester** (only if §2.2 applies) — `rsync` a remote host's agent log dirs into a
   local mirror, then run the harvesters against that mirror with the host's machine label.
   Gate on a short SSH reachability probe; skip cleanly if the host/tunnel is down.
3. **Session digester** — turn one raw log file into a **bounded** skeleton: the task, turn
   counts, tools used, and a head+tail transcript slice (truncate each turn, e.g. 400 chars).
   This is the only thing the LLM ever sees. Never emit the full raw log.
4. **Distiller + promoter** (the core) — for each project, batch its recent skeletons, ask the
   LLM for 0..N atomic durable facts as strict JSON (each tagged `type` + `confidence`), then:
   - high-confidence → write an auto memory card (additive; skip if the hash-named file
     already exists), using the card template from Build Spec 01 plus
     `created_by: <pipeline>` + `auto_promoted: true` + an `expires:` date.
   - medium/low → write a short note into `inbox/auto_promoted_review/`.
   - de-dup via a content-hash ledger; degrade to a no-op if the provider is unreachable
     (and, if your provider is local, strip proxy env first — see §4A).
5. **Nightly orchestrator** — a small wrapper that runs harvest (local + remote) → distiller,
   captures each step's output to a log, and emits **one** summary line to the user **only**
   if cards were written or something broke. Include the rollback command in any
   cards-written message. Register it with the user's scheduler at an off-peak hour.

### The distiller prompt (adapt, keep the guardrails)

The extraction prompt is where quality lives. It must instruct the model to:
- **Extract** when the transcript reveals a confirmed environment/config truth, a decision
  *with a reason*, an experiment result/number, or a reusable pitfall discovered the hard way.
- **Reject** task progress ("I will next…"), PR/commit numbers, "phase N done", file counts,
  sandbox/permission noise, anything stale in a week, anything unverifiable from the text.
- Emit **strict JSON** `{"facts":[{"type","confidence","text","source"}]}`, each `text` a
  single self-contained declarative sentence. `high` = explicitly stated as established;
  `medium` = strongly implied / discovered but not re-confirmed; `low` = inferred.
- Return `{"facts":[]}` when nothing qualifies. Be selective but not timid.

## 6. Acceptance criteria

- [ ] Harvesters pull new sessions into `raw/agent_logs/<agent>/<machine>/<slug>/`,
      idempotently, with `--dry-run` and `--since` working.
- [ ] (If applicable) the remote harvester pulls a server's logs and skips cleanly when the
      host is unreachable.
- [ ] The distiller, run on a day's sessions, produces real auto cards with `auto_promoted:
      true` for high-confidence facts and inbox notes for the rest — verified by reading them.
- [ ] Re-running the same night writes **zero** duplicate cards (ledger works).
- [ ] The rollback command removes exactly the auto cards and nothing else.
- [ ] The nightly job is registered with the scheduler and is silent on a no-op night.
- [ ] No raw transcript is ever embedded or sent wholesale; only bounded skeletons are.

## 7. Don't

- **Don't** send raw transcripts to the LLM or any index — only bounded, summarised slices.
- **Don't** let auto-promotion edit or delete existing cards. Additive only.
- **Don't** put medium/low-confidence facts into the authoritative layer.
- **Don't** auto-promote facts from a compliance-restricted project to a cloud LLM. Ask first.
- **Don't** let one dead host or endpoint hang or crash the whole night.
- **Don't** nag: no card written and nothing broken ⇒ no message.
- **Don't** skip the de-dup ledger or the `auto_promoted` tag — they are what make full-auto safe.

## 8. Report back

When done, print: which agents/machines are harvested and to where; which LLM provider the
distiller uses (and the result of your verification test from §4A); where auto cards vs. inbox
notes land; the
exact rollback command; the scheduler entry created; and how to run the whole pipeline once
by hand in `--dry-run` to inspect it before trusting it.
