# agent_brief: widget-detector

> READ THIS FIRST. The <=150-line working brief. If you need the full picture, open PROJECT.md.
> ⚠️ EXAMPLE / FICTIONAL — invented to show what a brief looks like.

**Goal (one sentence):** prove a lightweight detector stays accurate on small, occluded
widgets without a heavy backbone.

**Where we are:** the augmentation-curriculum line is winning (+4.1 mAP over baseline). The
open problem is recall collapsing above 60% occlusion.

**Next concrete action:** run the occlusion-aug schedule ablation (3 schedules × 2 seeds) and
update `experiments/occ-curriculum-v2.md` with the recall-vs-occlusion curve.

**Decisions you must NOT relitigate:**
- Backbone scaling is OFF the table (gave +0.6 mAP for 3× compute — see decisions.md 2026-01-12).
- We use synthetic widgets for development; real-widget transfer is a separate open question,
  not a blocker for the current ablation.
- Augmentation curriculum is the committed direction (decisions.md 2026-01-15).

**Pointers:** code `<repo>`, data `synth-widgets-1k`, method note
`wiki/methods/occlusion-augmentation`.

**If you discover something durable** (a config truth, a result, a gotcha), propose a memory
card — don't bury it in a transcript. If you make or change a decision, append it to
`decisions.md` with a date and a reason.
