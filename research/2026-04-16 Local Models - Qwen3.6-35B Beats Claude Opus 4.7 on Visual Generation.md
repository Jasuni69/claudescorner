---
title: "Qwen3.6-35B-A3B: Local Model Beats Claude Opus 4.7 on Visual Generation"
date: 2026-04-16
source: https://simonwillison.net/2026/Apr/16/qwen-beats-opus/
author: Simon Willison
tags: [local-models, open-source, claude, benchmarks, svg-generation]
relevance: model-selection, local-vs-cloud, cost-architecture
hn_points: 148
---

## Summary

Alibaba's Qwen3.6-35B-A3B (20.9GB quantized) running locally on a MacBook Pro M5 via LM Studio outperformed Claude Opus 4.7 on Simon Willison's SVG generation benchmarks ("pelican riding a bicycle", "flamingo on unicycle").

## Results

- **Qwen**: Correct bicycle frame, anatomically plausible bird, contextual elements (clouds), creative flair
- **Opus 4.7**: Wrong bicycle frame shape despite extended thinking enabled; less creative output on backup test
- Qwen won both rounds of Willison's visual generation tests

## Key Caveats

Willison explicitly notes: *"I very much doubt that a 21GB quantized version of their latest model is more powerful or useful than Anthropic's latest proprietary release"* for general tasks. This is a narrow benchmark win, not overall superiority.

## Implications for Jason's Work

- **Model selection**: Don't default to Claude for every subtask — open-weight models now competitive on specific tasks (creative generation, SVG, visual output)
- **Cost architecture**: Qwen3.6 at zero marginal cost on local hardware vs Opus 4.7 pricing; for high-volume creative tasks in agents, consider routing
- **ENGRAM/agent routing**: Could justify a lightweight model-routing layer in the dispatch pipeline — cheap local model for generation tasks, Claude for reasoning/code
- **Fabric relevance**: For report visual generation or diagram creation in BI pipelines, local model routing is now viable without API cost
