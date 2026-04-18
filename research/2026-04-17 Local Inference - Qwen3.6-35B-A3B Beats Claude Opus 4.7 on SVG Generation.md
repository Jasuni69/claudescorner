---
title: "Qwen3.6-35B-A3B on my laptop drew a better pelican than Claude Opus 4.7"
date: 2026-04-17
source: https://simonwillison.net/2026/Apr/16/qwen-beats-opus/
author: Simon Willison
tags: [local-inference, qwen, open-source, claude, benchmarking, agents]
signal: medium
clipped: 2026-04-17
---

## Summary

Alibaba's Qwen3.6-35B-A3B (20.9 GB quantized, runs on MacBook Pro via LM Studio) outperformed Claude Opus 4.7 on two SVG generation tasks:

- **Pelican test**: Qwen produced geometrically correct bicycle; Opus "messed up the bicycle frame"
- **Flamingo test**: Qwen added humorous details (sunglasses, bowtie); Opus delivered "competent if slightly dull" output

Willison's "pelican benchmark" is a longstanding joke — SVG of a pelican riding a bicycle — that historically correlated with general model usefulness. He notes that correlation has now broken down.

## Key Facts

- Model: `Qwen3.6-35B-A3B` — 35B total params, 3.6B active (MoE)
- Runtime: LM Studio on local MacBook Pro
- HN score: 755 points at time of clip
- Open weights — downloadable and self-hostable

## Relevance for Jason

This is an **agentic coding** model per Qwen's own positioning — not just creative SVG. The 3.6B active parameters (MoE) means low inference cost relative to a 35B dense model. Relevant to:

1. **Cost optimization**: If Qwen3.6 handles coding subtasks adequately, it's a cheaper fallback than Opus 4.7 for non-critical agent steps
2. **Darkbloom synergy**: Combined with Darkbloom (private inference on idle Macs, clipped 2026-04-16), local agent inference is becoming viable for non-sensitive intermediate steps
3. **Benchmark skepticism**: Willison's point that task-specific wins don't imply broad superiority — don't over-index on single benchmark wins

## Counterpoint

Willison explicitly says this doesn't indicate Qwen is broadly superior. Claude Opus 4.7 leads on extended reasoning (`xhigh` effort), agentic tool use, and instruction following for complex multi-step tasks.
