---
title: "The Beginning of Scarcity in AI — Compute Crisis 2026"
date: 2026-04-17
source: https://tomtunguz.com/ai-compute-crisis-2026/
hn: https://news.ycombinator.com/item?id=47799322
hn_pts: 114
hn_comments: 146
tags: [infrastructure, compute, scarcity, frontier-models, open-source]
clipped: 2026-04-17
---

## Summary

Tunguz argues the era of abundant cheap AI compute is ending. For the first time since the 2000s, technology companies face genuine supply constraints — GPU rental prices for Nvidia Blackwell surged 48% in two months ($2.75 → $4.08/hr). CoreWeave raised prices 20% and extended minimum contracts from 1 to 3 years.

## Five Characteristics of the Scarcity Era

1. **Relationship-based access** — top frontier models reserved for strategic partners (~40 orgs for Anthropic's newest)
2. **Capital determines winners** — only well-funded organizations can afford premium models
3. **Speed unavailable** — high cost without performance guarantees
4. **Inflationary pressures** — compute procurement becomes a critical business discipline
5. **Forced diversification** — developers shift to smaller models and on-premise solutions

## HN Signal

- **Open weights as equalizer:** open-weight models ~6-12 months behind SOTA — practical local inference viable now
- **Innovation through constraint:** scarcity drives harness design + small model optimization — "tremendous low-hanging fruit remains"
- **Energy is the real bottleneck:** ASML EUV lithography limits + power supply (turbines) — energy infrastructure more fundamental than chip supply
- **Skeptic position:** labs burning cash while selling at losses — genuine scarcity vs. strategic underselling unclear

## Relevance to Jason

- Anthropic limiting access to ~40 orgs validates the engram/ENGRAM design: frameworks that work on any model tier, not just frontier
- bi-agent's prompt caching (`cache_control=ephemeral`) is a direct hedge against inference cost inflation
- For Numberskills/Fairford: enterprise AI procurement strategy now matters — lock in capacity before price floors rise further
- Open-weight diversification (Qwen3.6 already beating Opus 4.7 on SVG) supports multi-model routing in ClaudesCorner dispatcher
