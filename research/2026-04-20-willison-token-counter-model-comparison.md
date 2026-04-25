---
title: "Claude Token Counter — Now with Model Comparisons"
source: https://simonwillison.net/2026/Apr/20/claude-token-counts/
date: 2026-04-20
tags: [claude, tokens, opus47, dispatch, cost, bi-agent]
hn_points: 5
author: Simon Willison
---

# Claude Token Counter — Now with Model Comparisons

**Source:** simonwillison.net | **Date:** 2026-04-20

## Summary

Willison updated his Claude Token Counter tool to support side-by-side token comparison across four models: Opus 4.7, Opus 4.6, Sonnet 4.6, Haiku 4.5. Measurements confirm token inflation on Opus 4.7 significantly exceeds Anthropic's stated ceiling.

## Key Findings

| Content Type | Opus 4.6 | Opus 4.7 | Inflation |
|---|---|---|---|
| Text (system prompt) | baseline | 1.46× | +46% |
| Image (3.7MB PNG) | baseline | 3.01× | +201% |

- Anthropic's stated ceiling: "roughly 1.0–1.35×"
- Real-world text measurement: **1.46×** (8% above ceiling)
- Real-world image measurement: **3.01×** (driven by higher resolution support — up to 2,576px on long edge)
- Pricing unchanged ($5/$25 per million input/output tokens) — cost increase is purely volumetric

## Practical Impact

At identical pricing, expect ~**40% higher costs** on text-heavy Opus 4.7 workloads vs 4.6. Image-heavy workflows: up to **3× cost increase**.

## Relevance to ClaudesCorner

- **dispatch.py:** Worker prompts are the primary cost surface. Token inflation on Opus 4.7 means the existing prompt-hygiene discipline is correct — don't loosen it.
- **bi-agent:** `cache_control=ephemeral` on schema block already identified as correct mitigation. This measurement confirms schema caching pays for itself even faster on 4.7.
- **Model selection:** For dispatch workers doing routine classification/synthesis, Haiku 4.5 or Sonnet 4.6 is the right tier — Opus 4.7 token inflation makes it a poor default unless reasoning depth is required.
- **Image workflows:** markitdown-mcp + Chandra OCR pipeline should route image-heavy documents through 4.6 or Haiku until image token inflation on 4.7 is better characterized.
- **Budget tracking:** token-dashboard at `projects/token-dashboard/app.py` should add a 1.46× inflation adjustment factor when displaying Opus 4.7 costs vs prior baseline.

## Action Items

- Add 1.46× inflation multiplier flag to token-dashboard for Opus 4.7 cost display
- Keep dispatch.py worker model at Sonnet 4.6 as default; gate Opus 4.7 to planning/synthesis only
- Re-test bi-agent DAX generation token cost under Opus 4.7 to quantify actual vs projected inflation
