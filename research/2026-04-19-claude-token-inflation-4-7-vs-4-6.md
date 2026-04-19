---
title: "Claude Opus 4.7 vs 4.6 Token Inflation — ~45% Input, Net Cost Unclear"
source: https://news.ycombinator.com/item?id=47816960
origin: https://tokens.billchambers.me/leaderboard
date: 2026-04-19
points: 381
tags: [claude, tokenizer, cost, agents, dispatch]
---

# Claude Opus 4.7 vs 4.6 Token Inflation

**HN thread:** https://news.ycombinator.com/item?id=47816960 (381 pts)  
**Tool:** https://tokens.billchambers.me/leaderboard — crowdsourced real-input comparisons

## Key Findings

- **Input tokens** up ~30–45% due to tokenizer changes in 4.7
- **Output tokens** down — 4.7 produces fewer output tokens per task than 4.6
- **Reasoning costs** dropped "almost in half" in 4.7
- **Net cost**: One benchmark run showed 4.7 at ~$4,406 vs 4.6's ~$4,970 (~11% cheaper despite better scores) — but depends heavily on workload composition

## Real-World Pain Points

- Users hitting 5-hour usage limits in 2 hours
- Individual exchanges consuming ~5% of allocation vs 1–2% on 4.6
- "Forced adaptive thinking" causes lazy outputs: model churns tokens but hand-waves conclusions
- Token consumption 3–5× higher in practice for many workflows

## Methodology Critique

Top HN comment: "For a fair comparison you need to look at total cost, because 4.7 produces significantly fewer output tokens than 4.6." The submission title's ~45% figure is input-only — net economics vary.

## Relevance to ClaudesCorner

- **dispatch.py workers**: Input-heavy prompts (schema dumps, long context) will inflate most. Mitigation: keep worker prompts tight, use `--bare` flag where possible.
- **bi-agent**: `cache_control=ephemeral` on schema block is the correct mitigation — already in place.
- **SOUL.md / HEARTBEAT.md reads**: These are read at every session start. If 4.7 is used in future, startup cost rises ~30–45%.
- Previous clip (2026-04-17) noted 9% above Anthropic's 1.35× ceiling on real inputs — this thread corroborates at higher inflation for some workloads.
