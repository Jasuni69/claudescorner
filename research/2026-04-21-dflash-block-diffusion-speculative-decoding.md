---
title: "dflash — Block Diffusion Speculative Decoding"
date: 2026-04-21
source: https://github.com/z-lab/dflash
tags: [llm-inference, speculative-decoding, qwen3, kimi-k2, dispatch, self-hosted]
stars: 2001
weekly_gain: 868
license: MIT
---

# dflash — Block Diffusion Speculative Decoding

**Repo:** z-lab/dflash (~2k stars, +868 this week) · MIT

## What it does

Block diffusion model for speculative decoding: generates multiple tokens in parallel (via a lightweight draft model) rather than sequentially, then verifies with the target model. Net effect: significant latency reduction without quality loss.

## Key features

- **Multi-backend:** vLLM, SGLang, Transformers, MLX (Apple Silicon)
- **Draft models available for:** Qwen3/3.5 series, Kimi-K2.5, LLaMA-3.1, GPT-OSS variants
- **Sliding window KV caching** for long-context scenarios
- Pure Python, 100% open, MIT license

## Relevance to ClaudesCorner

| Angle | Detail |
|---|---|
| dispatch.py latency | If dispatch.py workers ever route to self-hosted inference (Qwen3.6-35B-A3B or Kimi-K2.6 as Haiku fallback), dflash draft models cut per-token latency substantially |
| Qwen3 + Kimi-K2.5 support | Both flagged as Sonnet 4.6 fallback candidates (see MEMORY.md); dflash makes them more production-viable |
| Apple Silicon / local dev | MLX backend means zero cloud cost for prototyping dispatch worker prompts offline |
| No MCP yet | Wrap opportunity: `dflash-mcp` as inference-acceleration tool for local model workers |

## Signal

> Block diffusion + vLLM/SGLang backends + Qwen3/Kimi-K2.5 draft models = the missing latency layer if Anthropic rate limits push dispatch.py toward open-weight fallbacks.

## Action items

- Benchmark Qwen3.6-35B-A3B + dflash vs Sonnet 4.6 on bi-agent DAX generation quality/cost
- Revisit if Anthropic rate limits tighten (see reference_anthropic_compute_2026.md scarcity window)
