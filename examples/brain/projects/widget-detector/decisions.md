# Decisions — widget-detector

> Append-only. Each entry: date — decision — reason — source. Newest at the bottom.
> ⚠️ EXAMPLE / FICTIONAL.

- **2026-01-12 — Drop the backbone-scaling experiment line.**
  Reason: a 3× larger backbone bought only +0.6 mAP — not worth the compute or latency.
  Source: experiments/backbone-scale-v1.md (final table).

- **2026-01-15 — Commit to the occlusion-augmentation curriculum as the main direction.**
  Reason: curriculum v2 gave +4.1 mAP over baseline at the same compute as baseline; it's the
  cheapest lever we've found. Source: experiments/occ-curriculum-v2.md.
