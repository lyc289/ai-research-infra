# ai-research-infra

**Build-spec prompts for a personal, local-first AI research infrastructure.**
**一套用于搭建本地优先的个人科研基础设施的「构建说明书」。**

[**English**](#english) · [**中文**](#中文)

These are not a framework or a library. They're three Markdown specs you hand to *your own*
coding agent — Claude Code, Codex, Cursor, whatever you use — and it builds the system **for
you, adapted to your environment.**

这不是框架，也不是库。它们是三份 Markdown 规范，你把它交给*你自己的* coding agent（Claude
Code、Codex、Cursor，任何你用的），由它**照着帮你搭出来，并适配你自己的环境**。

Companion to the essay 配套文章： [Staying Grounded in Fast-Paced AI Research 快节奏的科研下，我们如何自处？](https://jxtse.github.io/blog/how-to-cope-with-fast-paced-research) 

---

# English

## Why build-specs, not a framework

The most valuable part of any personal research setup is **how it's designed and the traps it
avoids**.

So instead of shipping an implementation, this repo ships the **design as a prompt**. Your
coding agent reads the spec, interviews you about *your* tools and paths, and stands the system
up in *your* world. The spec carries the architecture and the principles; your agent carries the
adaptation. That's also the whole thesis of the essay — let the agent do the domain-specific
translation work.

## The three systems

Each spec targets one concrete pain. Read the pain first; if it's yours, build that spec.

### 01 — The Research Brain → [`01-research-brain.md`](01-research-brain.md)
- **The pain it solves.** Switch tools and you re-explain the project from scratch. Codex
  doesn't know what you decided in Claude Code yesterday; your notes are in a doc the agent
  can't see. No single place holds the authoritative state of a project — *you* are the only
  thing that remembers the whole picture.
- **What it gives you.** One unified, local-first **memory** — plain Markdown + Git, no database
  — that every agent reads *before* working and writes back to *after*. The authoritative answer
  to "where is this project, and why did we decide that?"
- **Build it when:** you use more than one AI agent and you're tired of being the only one who
  remembers. This is the foundation — start here; it's useful on its own.

### 02 — The Dream Loop → [`02-dream-loop.md`](02-dream-loop.md)
- **The pain it solves.** Valuable facts — a config gotcha, a decision and its reason, an
  experiment number — get discovered all day but die inside individual chat transcripts. Nobody
  re-reads yesterday's logs to extract them, so the brain slowly goes stale.
- **What it gives you.** A **nightly offline pipeline** that harvests the day's agent
  conversations, distils durable facts from them, and files the high-confidence ones into the
  brain — reversibly, under guardrails, while you sleep.
- **Build it when:** the brain (01) exists and you want it to *stay current on its own*, without
  manual upkeep.

### 03 — The Daily Briefing → [`03-daily-briefing.md`](03-daily-briefing.md)
- **The pain it solves.** You open Twitter, see a hundred new things, learn nothing, and feel
  behind. Most "AI news" is hot-takes and camp warfare; the real signal is buried.
- **What it gives you.** A once-a-day **information filter**: many sources in, deterministic
  ranking and dedup, an LLM only at the very last step, **5–7 items out** — the ones that
  actually matter to *you*.
- **Build it when:** you want to stay aware of the frontier without drowning in the firehose.
  Independent of the brain, but sharper when connected to it.

**Dependencies:** 02 builds on 01. 03 is independent but better connected to 01. **Start with 01.**

## How to use

1. Open the spec you want (start with [`01-research-brain.md`](01-research-brain.md)).
2. Give it to your coding agent: *"Read this spec and build this system for me, adapting it to
   my environment. Interview me first."*
3. Answer its questions about your tools, paths, model provider, and scheduler. **Every number,
   path, and model name in these specs is the author's — they're placeholders for yours.**
4. Review what it scaffolds against the spec's acceptance criteria, then iterate.

A worked, fully de-personalised example brain lives under [`examples/`](examples/) so you can
see the *shape* of the output before building your own.

## How this maps to harness engineering

If you think about AI agents in terms of the **harness** — the scaffolding around a model that
actually determines what it can do (its tool surface, memory schema, operating principles, how
its context is framed) — then this repo is just *a harness for your own research workflow*,
taught one dimension at a time:

- **Memory schema + operating principles** → 01 (the brain + its contract)
- **Context framing** (what reaches the agent's working context) → 03 (the briefing)
- **Tool surface** → your own skills/tools (see Related), with the brain as their shared memory
- **Keeping the harness current over time** → 02 (the dream loop)

Building your own research infrastructure is, in the end, dogfooding harness engineering on
yourself.

## Related

- [`jxtse/scientific-research-skills`](https://github.com/jxtse/scientific-research-skills) — the
  **tool surface**: concrete research skills for coding agents (literature search, full-text
  harvest, related-work survey, figure generation, Zotero management). Those are the
  *capabilities*; the brain here is the *shared memory* they read and write.

---

# 中文

## 为什么是「构建说明书」，而不是一个框架

任何人的个人科研系统里，最值钱的部分是**它的设计思路**，所以这个仓库交付的不是某个实现，而是**把设计本身做成 prompt**。你的 coding agent 读完规范，
采访*你*的工具和路径，然后在*你*的环境里把系统搭起来。规范负责架构与原则，你的 agent 负责适配。

## 三个系统

每份规范对应一个具体痛点。先读痛点，如果是你的，就搭那一份。

### 01 — 记忆底座（The Research Brain）→ [`01-research-brain.md`](01-research-brain.md)
- **解决什么问题。** 一换工具就得把项目背景重讲一遍。Codex 不知道你昨天在 Claude Code 里做了
  什么决策；你的笔记在 agent 看不见的文档里。没有任何一个地方保存项目的权威状态——*你自己*成了
  唯一记得全局的人。
- **它给你什么。** 一份统一的、本地优先的**记忆**——纯 Markdown + Git，不需要数据库——每个
  agent 干活*前*先读它、干完*后*写回它。是「这个项目到底进展到哪、当初为什么那样决定」的权威答案。
- **什么时候搭：** 你同时用不止一个 AI agent，且厌倦了自己是唯一记得住全局的人。这是地基——
  从这里开始，它单独就有用。

### 02 — 记忆整理回路（The Dream Loop）→ [`02-dream-loop.md`](02-dream-loop.md)
- **解决什么问题。** 有价值的事实——一个配置的坑、一个决策及其理由、一个实验数字——每天都在
  产生，却死在一条条孤立的对话记录里。没人会回头翻昨天的日志去提炼它们，于是 brain 慢慢腐烂。
- **它给你什么。** 一条**每晚离线运行的流水线**：在你睡觉时，把白天各个 agent 的对话收集回来、
  提炼出持久事实、把高置信度的那些归档进 brain——可回滚、带护栏。
- **什么时候搭：** brain（01）已经有了，你希望它**自己保持新鲜**，不用手动维护。

### 03 — 信息简报（The Daily Briefing）→ [`03-daily-briefing.md`](03-daily-briefing.md)
- **解决什么问题。** 你打开 Twitter，看到一百条新东西，什么都没学到，还觉得自己在掉队。大部分
  「AI 新闻」是 hot take 和阵营站队，真正的信号被淹没了。
- **它给你什么。** 一个每天一次的**信息过滤器**：多源进入，确定性排序与去重，只在最后一步用
  LLM 挑选，**输出 5–7 条**——真正对*你*重要的那几条。
- **什么时候搭：** 你想跟上前沿，又不想被信息洪流淹没。它独立于 brain，但接上 brain 会更精准。

**依赖关系：** 02 建立在 01 之上；03 独立，但接上 01 更好。**先搭 01。**

## 怎么用

1. 打开你想要的那份规范（从 [`01-research-brain.md`](01-research-brain.md) 开始）。
2. 把它交给你的 coding agent：*「读这份规范，照着帮我搭这个系统，适配我的环境。先采访我。」*
3. 回答它关于你的工具、路径、模型 provider、调度器的提问。**这些规范里所有的数字、路径、模型名
   都是作者的——它们是占位符，等你替换成你自己的。**
4. 对照规范里的验收标准检查它搭出来的东西，然后迭代。

[`examples/`](examples/) 下有一个完全去个人化的示例 brain，让你在动手前先看清产出的*形状*。

## 它如何映射到 harness engineering

如果你用 **harness**（决定一个模型实际能做什么的脚手架——它的工具面、记忆结构、操作原则、上下文
如何组织）来思考 AI agent，那么这个仓库其实就是*为你自己的科研流程搭的一套 harness*，一次讲一个维度：

- **记忆结构 + 操作原则** → 01（brain 及其契约）
- **上下文组织**（什么进入 agent 的工作上下文）→ 03（信息简报）
- **工具面** → 你自己的 skills/工具（见 Related），以 brain 作为它们的共享记忆
- **让 harness 随时间保持新鲜** → 02（记忆整理回路）

为自己搭科研基础设施，归根结底就是把 harness engineering 用在自己身上做 dogfooding。

## 相关

- [`jxtse/scientific-research-skills`](https://github.com/jxtse/scientific-research-skills) ——
  **工具面**：给 coding agent 的具体科研 skills（文献搜索、全文批量下载、相关工作综述、配图生成、
  Zotero 管理）。那些是*能力*；这里的 brain 是它们读写的*共享记忆*。
