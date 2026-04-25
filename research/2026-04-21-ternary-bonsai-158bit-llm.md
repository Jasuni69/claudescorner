---
title: "Ternary Bonsai: Top Intelligence at 1.58 Bits"
date: 2026-04-21
source: https://prismml.com/news/ternary-bonsai
hn: https://news.ycombinator.com/item?id=47844431
points: 158
tags: [local-inference, quantization, llm, edge-ai, dispatch]
---

## Summary

PrismML released the Ternary Bonsai model family (1.7B / 4B / 8B), using 1.58-bit weight representation where every weight is constrained to {-1, 0, +1} with a shared FP16 scale per 128-weight group. No higher-precision escape hatches — embeddings, attention, MLPs, and LM head all use identical compression. Apache 2.0.

## Key Numbers

| Model | Avg Score | Memory | Speed (M4 Pro) | Speed (iPhone 17 PM) |
|-------|-----------|--------|----------------|----------------------|
| Ternary Bonsai 8B | 75.5 | 1.75 GB | 82 toks/sec | 27 toks/sec |
| 1-bit Bonsai 8B | 70.5 | 1.15 GB | — | — |
| Qwen3 8B (FP16) | ~76 | 16.38 GB | ~15 toks/sec | — |

- ~9x smaller memory footprint vs FP16 equivalent
- ~5x faster inference vs 16-bit 8B on M4 Pro
- 3-4x energy efficiency improvement
- Benchmarks: MMLU Redux, GSM8K, HumanEval+, IFEval

## Availability

- HuggingFace: `prism-ml/Ternary-Bonsai-8B-mlx-2bit`
- Native MLX for Apple (Mac/iPhone/iPad)
- Locally AI app (iOS)
- Whitepaper + web demo available

## Relevance to ClaudesCorner

**dispatch.py Haiku fallback candidate.** When Anthropic rate limits tighten (validated concern per memory — K2VV ToolCall benchmarks recommend testing alternatives before Fairford Phase 2), Ternary Bonsai 8B running locally on Mac via MLX is a viable Haiku-tier leaf-node option for narrow dispatch tasks. At 82 toks/sec on M4 Pro and 1.75 GB RAM it fits comfortably alongside Claude Code without memory pressure.

**Not a Sonnet replacement.** 75.5 avg benchmark score vs Sonnet 4.6 multi-turn reasoning — suitable for summarization, classification, and tool-call formatting workers, not complex DAX generation or architectural planning.

**ENGRAM edge case.** If engram.dev targets on-device deployment, Ternary Bonsai 8B is the first credible open-weight model that runs on iPhone without significant quality degradation. Worth noting as an ENGRAM mobile runtime story.
