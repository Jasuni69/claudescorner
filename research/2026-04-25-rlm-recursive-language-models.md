---
title: "RLM — Recursive Language Models inference library"
date: 2026-04-25
source: https://github.com/alexzhang13/rlm
stars: 3846
stars_today: 227
license: MIT
tags: [ai-agents, inference, recursion, sandboxing, dispatch-py, engram, haiku-tier]
signal: high
---

# RLM — Recursive Language Models

**Repo:** `alexzhang13/rlm` · 3,846 stars · +227 today · MIT License  
**Lab:** MIT OASYS Laboratory · arXiv 2512.24601 (December 2025)  
**Install:** `pip install rlms`

## What it is

A plug-and-play inference library that replaces standard `llm.completion()` with `rlm.completion()`. Instead of stuffing massive context into a single LLM call, RLM lets a model programmatically examine its input, decompose it into subtasks, and recursively call itself — each sub-call running in an isolated REPL sandbox.

The core insight: **recursive decomposition + small context windows > single-call large context windows** for long-horizon tasks. Published benchmarks show Qwen3.5-27B + RLM hitting 22.18% on LongCoT — roughly 2× GPT-5.2 at the same task. Small models + recursive loops can match frontier models on long-horizon tasks.

## Architecture

```
Input → RLM.completion()
         ↓
    REPL Environment (sandbox)
         ↓
    LM examines input, identifies subtasks
         ↓
    rlm.completion() sub-calls (recursive)
         ↓
    RLMLogger captures full trajectory tree
         ↓
    Web visualizer (inspect recursion graph)
```

## Supported sandbox backends

| Backend | Isolation | Notes |
|---|---|---|
| Local (default) | None | Python `exec` — dev only |
| Docker | Container | Good for most workloads |
| Modal Sandboxes | Cloud VM | Production-grade |
| E2B | Cloud VM | E2B SDK compatible |
| Daytona | Cloud VM | Beta |
| Prime Intellect | Cloud VM | Beta |

## Supported model providers

- Anthropic (Claude native)
- OpenAI
- OpenRouter
- Portkey
- Local via vLLM (OpenAI-compatible)

## Usage

```python
from rlm import RLM

rlm = RLM(
    backend="anthropic",
    backend_kwargs={"model_name": "claude-haiku-4-5-20251001"},
    verbose=True
)
result = rlm.completion("Analyze and summarize this 200-page document: ...")
```

## Key features

- `RLMLogger` — trajectory logging; reconstructs full recursion tree for debugging
- Web visualizer — inspect code execution, sub-calls, recursion depth in browser
- Configurable namespaces — tune security/isolation per execution context
- GEPA integration (per HN 2026-04-25) — use RLMs to improve RLMs via self-generated prompts

## Relevance to ClaudesCorner

**dispatch.py Haiku-tier workers:** RLM validates the short-parallel architecture. A Haiku worker + RLM decomposition can handle tasks previously requiring Sonnet/Opus directly, by recursively breaking them into sub-calls. This is a concrete mechanism for Haiku-tier cost reduction beyond simple task scoping.

**ENGRAM two-pass retrieval:** RLM's recursive self-query pattern is architecturally identical to ENGRAM's two-pass memory retrieval (broad fetch → targeted re-query). Both are instances of the same principle: decompose context rather than expand context window.

**Sandbox backends:** RLM already supports E2B SDK — same interface as CubeSandbox. dispatch.py v2 worker isolation could route through `rlm.completion()` with Modal/E2B backend rather than wrapping subprocess calls directly.

**bi-agent DAX oracle:** The RLMLogger trajectory export is a natural fit for the bi-agent 3-layer oracle — each DAX generation step could be a recursive sub-call with logged evidence at each layer.

## Gaps / caveats

- No MCP integration yet — wrap opportunity
- Recursion depth / cost control requires careful tuning (doom-loop risk)
- GEPA (self-improvement loop) is experimental, no production case studies yet
- Windows: Docker backend works; Modal/E2B require network egress through CrabTrap

## Action items

- Benchmark Haiku + RLM vs Sonnet direct on a dispatch.py tier-2 task
- Evaluate RLM + RLMLogger as bi-agent DAX oracle evidence layer
- Monitor GEPA integration — if stable, relevant to feedback_flywheel.py
