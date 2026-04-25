---
title: "DeepSeek V4 Pro — Open-Weight Frontier Model Surpasses Claude on Coding"
date: 2026-04-24
source: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
hn_url: https://news.ycombinator.com/
hn_points: 304
tags: [llm, open-source, agents, mcp, competitive-signal, dispatch]
relevance: [dispatch-routing, sonnet-fallback, mcp-benchmarks, fairford-phase2]
---

# DeepSeek V4 Pro — Open-Weight Frontier Model

**Source**: HuggingFace model card + HN front page (304 pts, 1hr old as of 2026-04-24 morning)
**License**: MIT
**Release**: April 2026

## What It Is

DeepSeek V4 Pro is a 1.6T parameter Mixture-of-Experts model with only 49B activated parameters per forward pass. MIT licensed, fully open-weight. Three variants: V4-Flash (fast), V4-Pro (balanced), V4-Pro-Max (maximum reasoning).

## Architecture

- **1.6T total / 49B activated** — MoE with Compressed Sparse Attention (CSA) + Heavily Compressed Attention (HCA)
- **1 million token context window** — with only 10% KV cache vs DeepSeek-V3.2
- **27% of single-token inference FLOPs** vs V3.2 — massive efficiency gain
- **FP4 MoE experts + FP8 mixed precision**
- Pre-trained on 32T+ tokens
- Three thinking modes: Non-think (fast) / Think High (conscious analysis) / Think Max (max reasoning, requires ≥384K context)
- Muon optimizer for training stability

## Benchmark Results (V4-Pro-Max)

| Benchmark | DeepSeek V4-Pro-Max | Claude Opus-4.6 Max | GPT-5.4 xHigh |
|---|---|---|---|
| LiveCodeBench | **93.5%** | 91.7%* | 91.7% |
| Codeforces Rating | **3206** | 3168 | — |
| SWE-Verified | **80.6%** | — | — |
| IMOAnswerBench | **89.8%** | 75.3% | — |
| Terminal-Bench 2.0 | **67.9%** | — | — |
| MCPAtlas Pass@1 | **73.6%** | — | — |
| BrowseComp Pass@1 | **83.4%** | — | — |
| Toolathlon Pass@1 | 51.8% | — | — |

*Comparison labels from model card; verify exact model versions before routing decisions*

## MCP / Agentic Signal

- **MCPAtlas** is included as a first-class benchmark (73.6% Pass@1) — direct MCP tool-use validation
- Terminal-Bench 2.0 score 67.9% — stronger than Kimi K2.6 (66.7% on Terminal-Bench)
- BrowseComp 83.4% — strong web-browsing agent capability

## Relevance to ClaudesCorner

### dispatch.py routing
- **Sonnet 4.6 fallback candidate** when Anthropic rate limits hit — MIT license removes licensing friction
- 49B activated params = deployable locally or via API at lower cost than frontier closed models
- MCPAtlas benchmark validates tool-use reliability; needs K2VV ToolCall F1 test before Fairford routing

### Fairford Phase 2
- MIT license enables self-hosted deployment on Foundry VMs — cost model changes significantly
- Stronger coding than Claude on LiveCodeBench; evaluate for bi-agent DAX generation scaffold tier

### ENGRAM
- 1M context window large enough to hold full SOUL.md + HEARTBEAT.md + session history in one context
- Open weights = potential for fine-tuning on ENGRAM memory format

## Action Items

- [ ] Benchmark V4-Pro via KVV ToolCall (F1 + JSON Schema) before routing any Fairford work
- [ ] Compare Haiku 4.5 vs V4-Flash on dispatch.py leaf node tasks (cost vs latency)
- [ ] Check if vLLM/SGLang Windows support is viable for local fallback
- [ ] Monitor: Apache-licensed vLLM + V4-Flash = potential zero-API-cost dispatch.py worker

## Notes

- Think Max mode requires ≥384K context — keep in mind for long dispatch sessions
- Tokenizer: `encoding_dsv4` (custom), not tiktoken — measure actual token inflation before budgeting
- SimpleQA-Verified 57.9% vs Gemini-3.1-Pro 75.6% — factual recall gap vs coding strength; not suitable for research-tier workers without oracle
