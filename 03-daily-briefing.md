# Build Spec 03 — The Daily Briefing (deterministic information filter)

> **How to use this file.** Hand it to your own coding agent and say *"build this for me,
> adapting it to my environment."* This system is **independent** — it doesn't require the
> Brain (Build Spec 01) — but it's better when connected to it (Section 7). Everything below
> is written **for that agent**.

---

## 0. Agent: read this first

You are building a **once-a-day information briefing** that fights the research firehose. It
pulls the last 24 hours from many sources in parallel, filters them down with **deterministic
rules first** and an LLM only at the very last step, and delivers **5–7 items** the user
actually cares about. The design goal is *less noise, not more coverage*.

**Discover the environment first (Section 2).** Don't hardcode feeds, models, or delivery
targets from the example.

## 1. The problem this solves

The user opens Twitter/X, sees a hundred new things, learns nothing, and feels behind. Most
"AI news" is hot takes and camp warfare; the signal is buried. A daily briefing built on a
clear **source-priority model** plus deterministic filtering converts that firehose into a
short, ranked, deduplicated digest — so the user spends attention on substance, not scrolling.

## 2. Discover the environment (before building)

1. **Sources.** Which channels does the user actually want pulled? Gather concrete handles,
   not categories: specific blog RSS/Atom feeds, specific researchers to follow on X, any
   curated aggregator they already trust, GitHub trending in their fields, subreddits, etc.
   Get the real list — this is the single biggest quality lever.
2. **Source priority.** Confirm the user's ordering (Section 3 has a strong default). This
   ordering is a *filter weight*, not cosmetic.
3. **Interests / projects.** What is the user working on right now? The final LLM pass uses
   this to pick what's relevant. If Build Spec 01's brain exists, read project briefs from it
   (Section 7) instead of asking.
4. **An LLM provider** for the final selection pass only. Same universal rule as Build Spec 02:
   **the user configures their own provider** (`base_url` / `api_key` / `model`; cloud or local).
5. **Delivery + schedule.** Where should the briefing land (a chat platform, email, a local
   file, a dashboard)? What time? What scheduler runs it?
6. **API access reality.** Which sources need keys / authenticated clients (X/Twitter, some
   aggregators) vs. open RSS? Prefer durable official clients/feeds over scraping; note what
   the user already has credentials for.

## 3. The non-negotiable design principles

This is the spec's center of gravity. Encode it; don't dilute it.

- **"If code can do it, don't use an agent."** Sorting, deduplication, diversity quotas,
  recency windows, source-priority weighting — **all deterministic, all hardcoded.** The LLM
  is *not* the ranker. It only does the final, genuinely-semantic step: judging relevance to
  the user given their context. Deterministic rules first, LLM last, never the reverse.
- **Source priority (default, optimised for frontier-insight efficiency — not rigor):**
  **Blog > peer-reviewed paper > arXiv preprint > podcast > social media.**
  Rationale to preserve in comments: good techniques surface in blogs first (higher
  information density, no reviewer-pandering, mobile-friendly), reach arXiv months later, top
  venues later still. Podcasts rank below arXiv because density is low (one good insight per
  hour) and they're hard to cite/recall — treat them as *inspiration sources*, not knowledge
  sources. Social media ranks last: real signal exists but drowns in hot-takes and
  "X is dead" noise, and it manufactures a false sense of learning. **This ordering optimises
  for getting frontier insight fast, not for source rigor** — say so, so the user trusts the
  ranking's intent.
- **A hard cap on output.** 5–7 items, period. The point is a filter, not a feed. More items
  = failure.
- **Diversity + floors as deterministic constraints.** Don't let one loud source or one
  category dominate. Enforce category diversity and a minimum for non-news/substance items
  with hardcoded rules, before the LLM ever sees the shortlist.
- **One message out.** The user gets a single, clean digest — not a stream of per-source
  dumps.

## 4. The pipeline to build

```
(0) fetch — parallel, last 24h, per source, each with a timeout + isolation
              (one dead feed must not sink the run)
(1) normalize — every item -> a common record:
              {source, source_type, title, url, ts, raw_score?, snippet}
(2) deterministic pre-rank — HARDCODED, no LLM:
              - source-priority weight (Section 3 ordering)
              - recency window (drop >24–48h)
              - dedup near-identical stories across sources (title/URL similarity)
              - per-source and per-category caps (diversity)
              - a substance floor (guarantee >=N non-social / non-news items)
              -> a shortlist of ~15–20 candidates
(3) source-health check — log which feeds returned nothing (silent rot detection)
(4) LLM final select — the ONLY LLM step:
              given the shortlist + the user's current interests/projects,
              pick and order the final 5–7, each with a one-line "why it matters to you"
(5) render + deliver — one message/digest to the configured target; optional dashboard
```

Implementation notes:
- **Parallel fetch with per-source isolation.** Wrap each fetch so a timeout/failure yields
  an empty list, not an exception that kills the batch.
- **Steps 1–3 are pure functions over data.** No model calls. They must be unit-testable and
  produce the same shortlist given the same inputs.
- **Step 4's prompt** gets the *shortlist only* (already small), plus the user's interest
  context, and is asked to select + justify — not to re-rank from scratch and not to
  summarise everything. Keep its output structured (ordered list + one-line rationale each).

## 5. Sourcing guidance (quality lever)

- Prefer a **curated aggregator** the user trusts as one high-signal input, alongside a
  hand-picked set of **deep blogs** (lab blogs, researcher blogs) over generic tech-news
  firehoses.
- For social, pull only a **followed set** of researchers (not the global timeline) and rank
  intra-source by engagement, then let the deterministic caps keep social in its place.
- Favor **official APIs / durable clients / RSS** over one-off scrapers. If a platform has a
  maintained client or feed, use it — it survives; scrapers rot.

> **A concrete starting point.** [`examples/briefing-source-set.md`](examples/briefing-source-set.md)
> contains the author's actual AI-research source set (~64 feeds — deep blogs, official lab
> blogs, a curated aggregator, an X following shortlist, GitHub release feeds, subreddits), the
> de-personalised selection prompt, and a pointer to the upstream fetching pipeline. Fork it and
> cut it down to yours rather than starting from a blank list.

## 6. Acceptance criteria

- [ ] Steps 1–3 run with **no LLM calls** and produce a stable ~15–20 candidate shortlist.
- [ ] Source-priority ordering, recency window, dedup, diversity caps, and the substance
      floor are all hardcoded and testable.
- [ ] A single dead/empty feed does not break the run; source-health logs it.
- [ ] The LLM step only selects/orders the final 5–7 from the shortlist and explains each.
- [ ] Exactly one digest is delivered to the configured target on schedule.
- [ ] Output never exceeds 7 items.

## 7. Optional: connect to the Brain (Build Spec 01)

If the brain exists, the briefing gets sharper:
- Step 4's "user interests" context can be read from the brain's project briefs instead of a
  static list — so relevance tracks what the user is *currently* working on.
- A genuinely important item can be dropped into the brain's `inbox/` as a clip for later
  triage (never auto-promoted to a memory card — that's the dream loop's gated job).
Keep this optional: the briefing must still run standalone if the brain isn't there.

## 8. Don't

- **Don't** use the LLM for ranking, sorting, dedup, or diversity. Those are code. The LLM
  selects the final few and explains relevance — nothing more.
- **Don't** exceed 5–7 items. A longer digest defeats the purpose.
- **Don't** let one source or category dominate; enforce diversity deterministically.
- **Don't** scrape when a maintained API/feed/client exists.
- **Don't** emit per-source dumps; deliver one merged digest.
- **Don't** silently tolerate rotting feeds — surface a source-health signal.
- **Don't** treat the source-priority order as a rigor ranking; it optimises insight speed.

## 9. Report back

When done, print: the source list and per-source method (API/feed/client); the deterministic
rules implemented (priority weights, recency, dedup, caps, floors); which LLM provider does
the final pick; the delivery target + schedule entry; and a
one-shot dry-run command that prints the shortlist (post step 3) and the final digest so the
user can inspect the filter before trusting it.
