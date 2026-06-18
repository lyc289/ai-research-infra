# Project: widget-detector

> Authoritative state for this project. Agents read `agent_brief.md` first; this is the full
> picture. Update via reviewed diffs (see AGENTS.md writeback contract).
>
> ⚠️ EXAMPLE / FICTIONAL. Everything here is invented to demonstrate the structure.

## One-line goal
Show that a lightweight detector can stay accurate on small, partially-occluded widgets
without a heavy backbone.

## Current status
- **Stage:** experiment
- **Last meaningful update:** 2026-01-15
- **Current bottleneck:** recall drops sharply above 60% occlusion.
- **Next concrete action:** ablate the occlusion-aug schedule (see decisions.md 2026-01-15).

## Core claim
A targeted occlusion-augmentation curriculum recovers most of the recall lost under heavy
occlusion, at a fraction of the cost of scaling the backbone.

## Evidence map
- Claim "aug curriculum > backbone scaling" → supported by exp `occ-curriculum-v2` (mAP +4.1).
- Claim "holds under >60% occlusion" → still missing evidence (current bottleneck).
- Negative result: naive heavy backbone gave +0.6 mAP for 3x compute — not worth it.

## Important decisions
See `decisions.md` for the full log. Highlights:
- 2026-01-15: drop backbone-scaling line, commit to augmentation curriculum — see decisions.md.

## Active ideas
- occlusion-curriculum — novelty: medium — risk: low — validate via the v2 ablation.

## Experiments
- occ-curriculum-v2 — done — dataset: synth-widgets-1k — result: mAP 71.3 (+4.1) — artifact: experiments/occ-curriculum-v2.md
  (full records would live in `experiments/<slug>.md`)

## Storytelling
See `storytelling.md`. Summary: target a vision workshop; reader pain = detectors brittle under
occlusion; arc = cheap curriculum beats expensive scaling; key figure = recall-vs-occlusion curve.

## Open questions
See `open_questions.md`. Top one: does the curriculum transfer to real (non-synthetic) widgets?

## Pointers
- Code: <your repo path>
- Data: <your dataset path>
- Raw logs: raw/agent_logs/<agent>/<machine>/widget-detector/
- Manuscript: <your draft path>
- Relevant wiki pages: wiki/methods/occlusion-augmentation
