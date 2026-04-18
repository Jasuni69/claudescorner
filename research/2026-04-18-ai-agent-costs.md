---
title: "Are the costs of AI agents rising exponentially? — Toby Ord"
source: https://www.tobyord.com/writing/hourly-costs-for-ai-agents
clipped: 2026-04-18
tags: [ai-agents, economics, deployment, metr, cost-curves]
hn_pts: 35
---

## Core argument

METR's benchmark shows AI agents can handle increasingly longer tasks exponentially over time — but nobody is measuring whether the *costs* are rising just as fast. If hourly costs grow faster than task duration capability, headline progress numbers are misleading.

**"Hourly cost"** = money to complete a task at 50% success threshold ÷ task duration in human hours.

## Key data points

| Model | Sweet-spot hourly | Plateau hourly |
|---|---|---|
| Grok 4 | $0.40 | — |
| o3 | ~$40 | $350 |
| Human SWE | — | ~$120 |

o3 at full capability costs ~$350/hr — more expensive than a human engineer.

## Findings

- Both "sweet spot" and "saturation" points show hourly costs rising with task duration capability
- METR's time-horizon trends may be partly driven by unsustainable inference compute scaling, not genuine capability improvement
- Real-world deployment will lag theoretical benchmarks by widening cost gaps

## Implications for Jason

- **dispatch.py**: 3 parallel workers × Opus 4.7 on complex tasks = cost exposure worth monitoring; sweet-spot task sizing matters more than frontier capability
- **bi-agent**: cache_control=ephemeral pattern on schema block is already the correct mitigation — reduces per-call token burn
- **Clementine / Fairford**: enterprise agent ROI pitch needs to account for hourly cost curves, not just accuracy benchmarks
- When scoping autonomous loops, prefer tasks at the inflection point (sweet spot) rather than pushing to saturation — same task horizon, fraction of the cost
- Validates the dispatch.py architecture: short parallel tasks > one long sequential chain

## Gaps in the analysis

Ord acknowledges: limited model coverage, no explicit hourly-cost-vs-release-date trend line, OpenAI cost estimates are uncertain. Treat numbers as directional, not precise.
