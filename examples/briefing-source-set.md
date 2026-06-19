# Appendix — The author's live briefing source set & method

> **A starting point, not a default.** This is the actual source set and selection method
> behind the author's daily briefing. It's here so you have a concrete, opinionated list to
> fork from instead of a blank page. **Delete what you don't care about, add your own.** None
> of this is required by [`../03-daily-briefing.md`](../03-daily-briefing.md) — the spec is the
> design; this is one filled-in instance.

The author's briefing is **AI-research-focused**. The list below is the curated subset
(~64 sources); the full personal config also carries crypto and general-consumer-tech feeds
that were dropped here because they dilute a research briefing. **What you mute matters as much
as what you keep** — the author actively disables ~50 noisy crypto-KOL / rate-limited social
sources to protect signal quality.

---

## A. The source set (curated, AI / research / frontier-tech)

★ = priority source (gets a ranking weight bump in the deterministic pre-rank).

### Deep AI blogs & analysis (the highest-signal tier)
The core of the whole thing. These are where good ideas surface *first* — see the source-priority
argument in the spec.

| ★ | Source | Feed |
|---|--------|------|
| ★ | Simon Willison | `https://simonwillison.net/atom/everything/` |
| ★ | Lil'Log (Lilian Weng) | `https://lilianweng.github.io/index.xml` |
| ★ | Import AI (Jack Clark) | `https://jack-clark.net/feed/` |
| ★ | Latent Space | `https://www.latent.space/feed` |
| ★ | SemiAnalysis | `https://semianalysis.com/feed/` |
| ★ | AI Snake Oil | `https://aisnakeoil.substack.com/feed` |
| ★ | Gary Marcus | `https://garymarcus.substack.com/feed` |
| ★ | Sebastian Raschka | `https://magazine.sebastianraschka.com/feed` |
| ★ | The Decoder | `https://the-decoder.com/feed/` |
| ★ | MarkTechPost | `https://www.marktechpost.com/feed/` |
|   | Dwarkesh Patel | `https://www.dwarkeshpatel.com/feed` |
|   | Gwern | `https://gwern.substack.com/feed` |
|   | minimaxir (Max Woolf) | `https://minimaxir.com/index.xml` |

### Official lab / vendor blogs
Note the **Google News RSS trick**: labs that don't publish a clean public feed (OpenAI,
Anthropic, DeepMind) are reached via `news.google.com/rss/search?q=site:<domain>` — a durable
way to get a first-party feed without scraping. Worth stealing.

| ★ | Source | Feed |
|---|--------|------|
| ★ | OpenAI Blog | `https://openai.com/blog/rss.xml` (or via `news.google.com/rss/search?q=site:openai.com`) |
| ★ | Anthropic Blog | via `news.google.com/rss/search?q=site:anthropic.com&hl=en-US&gl=US&ceid=US:en` |
| ★ | Google DeepMind Blog | `https://deepmind.google/blog/rss.xml` (or via Google News site:deepmind.google) |
| ★ | Hugging Face Blog | `https://huggingface.co/blog/feed.xml` |
| ★ | NVIDIA AI Blog | `https://blogs.nvidia.com/feed/` |
|   | Google AI Blog | `https://blog.google/technology/ai/rss/` |

### Tech press (AI-leaning, kept lean)
| ★ | Source | Feed |
|---|--------|------|
| ★ | MIT Technology Review | `https://www.technologyreview.com/feed` |
| ★ | Ben's Bites | `https://www.bensbites.com/feed` |
|   | VentureBeat AI | `https://venturebeat.com/category/ai/feed/` |
|   | IEEE Spectrum | `https://spectrum.ieee.org/feeds/feed.rss` |

### Chinese-language AI media
| ★ | Source | Feed |
|---|--------|------|
| ★ | 机器之心 Synced | `https://www.jiqizhixin.com/rss` |
| ★ | 36氪 | `https://36kr.com/feed` |
|   | 量子位 QbitAI | `https://www.qbitai.com/feed` |

### Curated aggregator (a high-signal pre-filtered input)
- **AI HOT** (`aihot.virxact.com`) — a hand-curated AI news station (168 hand-picked sources +
  multi-dimensional scoring + event clustering) by 数字生命卡兹克. Its *selected* items are
  treated as an already-second-pass-filtered T1.2 tier. Public API:
  `https://aihot.virxact.com/api/public/items?mode=selected&since=<ISO>` and `/api/public/daily`.

### X / Twitter (a *followed* shortlist, not the global timeline)
Pulled via an X client, ranked intra-source by `like_count + retweet_count*2`, top 3 kept. The
author follows the official accounts directly and disables the API-fanout duplicates to avoid
rate-limit noise.

| ★ | Handle | | ★ | Handle |
|---|--------|---|---|--------|
| ★ | `@karpathy` | | ★ | `@sama` |
| ★ | `@OpenAI` | | ★ | `@AnthropicAI` |
| ★ | `@stanfordnlp` | | ★ | `@trq212` (Thariq) |
|   | `@tszzl` (roon) | | | |

### GitHub releases (ship-signal for the tools you actually use)
Watching release feeds of the libraries you depend on is a cheap, high-precision signal.

`vLLM` · `Ollama` · `huggingface/transformers` · `pytorch` · `meta-llama` · `deepseek-ai` ·
`langchain` · `llama_index` · `autogen` · `crewai` · `dify` · `mem0` · `modelcontextprotocol/servers` ·
`openai-python` · `anthropic-sdk` · `agno`

### Reddit (community pulse, capped low)
`r/MachineLearning` ★ · `r/OpenAI` ★ · `r/Anthropic` ★ · `r/LocalLLaMA` · `r/artificial`

---

## B. The selection method (de-personalised from the author's cron prompt)

This is the prompt logic that turns the fetched pool into the final 5–7 items. It is the
concrete instance of the spec's **"if code can do it, don't use an agent"** principle.

**Deterministic steps (no LLM):**
- **Source priority / tiering:** official first-party (T1) > curated-aggregator selected (T1.2)
  > tech media > aggregator raw > deep blogs > community. This tier becomes a numeric weight.
- **X following:** sort by `like_count + retweet_count*2`, take Top 3. No vibes.
- **Deep blogs:** filter to the `deep-*` AI sources published in the last 24h; if ≥4, enforce
  **source diversity (max 1 per source)** and take 3, first-party lab blogs first.
- **Curated pool:** merge all items, sort by `quality_score` desc, dedup by normalized URL,
  take Top 15–20 as the shortlist.

**The single LLM step — final select + classify into 5–7 items**, each tagged with a category
emoji and obeying hard constraints:

- 📰 major news (official release / launch / industry event)
- 💬 opinion / stance from the field (a KOL's take, not the news itself)
- 🔥 in-circle buzz (high engagement, not yet headline)
- 📚 deep long-read (the deep-blog tier above)

Hard constraints (deterministic guards on the LLM's output):
- **Dedup:** one story appears once. If an official account's tweet *is* the news, it goes under
  📰, not also 💬.
- **Substance floor:** at least 2 non-📰 items (💬/🔥/📚), so human voices and deep reads aren't
  crowded out by news. Drop to 5 total before dropping below 2 non-news.
- **Attribution:** 💬/🔥/📚 items carry `(@handle)` / author; 📰 doesn't.
- **Clean links:** every item links to the original first-party URL — never an aggregator's
  homepage. (When using an AI-HOT item, link its underlying `url`, not `aihot.virxact.com`.)
- Total length kept tight; one item = one Chinese sentence + one clean link.

---

## C. The pipeline tools (install these — don't copy them)

The author does **not** own the fetching pipeline and it is **not** redistributed here. Point
your own agent at the upstream tools:

- **Fetching pipeline:** [`draco-agent/tech-news-digest`](https://github.com/draco-agent/tech-news-digest)
  — a 5-layer collector (RSS / X / GitHub / Reddit / web) with quality scoring, dedup, retries,
  and a unified source model. The source set in Section A plugs straight into its config schema.
- **Curated aggregator:** AI HOT (`aihot.virxact.com`) — public read API, no install.

Your coding agent, following [`../03-daily-briefing.md`](../03-daily-briefing.md), wires these
together with the deterministic-first / LLM-last selection method in Section B and delivers one
digest on your schedule. The *design* is the spec; this appendix is just the author's filled-in
copy to start from.
