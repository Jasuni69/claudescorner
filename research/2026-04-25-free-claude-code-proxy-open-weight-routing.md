---
title: "free-claude-code — FastAPI Proxy Routes Claude Code to Open-Weight Models"
date: 2026-04-25
source: https://github.com/Alishahryar1/free-claude-code
stars: 8724
weekly_gain: 4397
license: MIT
tags: [claude-code, dispatch, cost, proxy, open-weight, mcp]
relevance: high
---

# free-claude-code — FastAPI Proxy Routes Claude Code to Open-Weight Models

**GitHub:** Alishahryar1/free-claude-code | 8.7k stars | +4.4k this week | MIT | 2026-04-25

## What It Is

A transparent FastAPI proxy that intercepts Claude Code's Anthropic API calls and forwards them to alternative providers (NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp). Claude Code connects as normal; no code changes required — just two env vars.

```bash
ANTHROPIC_AUTH_TOKEN="freecc" ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

## Technical Architecture

1. **Proxy intercepts** all Claude Code requests at `localhost:8082`
2. **Format translation**: Anthropic API format → OpenAI-compatible format
3. **Provider routing**: forwards to chosen backend (NIM / OpenRouter / DeepSeek / local)
4. **Response conversion**: translates response back to Anthropic format + streams to Claude Code
5. **Local optimization**: 5 categories of trivial requests (quota probes, title generation) answered locally without consuming API quota

## Per-Model Routing

Opus, Sonnet, Haiku can each route to different providers/models:

| Provider | Cost | Rate Limit |
|---|---|---|
| NVIDIA NIM | Free (complimentary tier) | 40 req/min |
| OpenRouter | Free/Paid (many free models) | Varies |
| DeepSeek | Usage-based | — |
| LM Studio / llama.cpp | Free (local inference) | Unlimited |

## Notable Features

- **Smart rate limiting**: rolling-window throttle + reactive 429 backoff
- **Thinking token support**: converts `<think>` tags into native Claude thinking blocks
- **Discord/Telegram bot mode**: remote autonomous coding with session persistence
- **Extensible**: abstract base classes for adding providers

## Dispatch.py Relevance

**Cost mitigation path when Anthropic rate limits hit:**
- Route Haiku-tier dispatch workers to NVIDIA NIM free tier (40 req/min) or local llama.cpp
- Route Sonnet-tier workers to DeepSeek or OpenRouter free models
- Proxy is stateless and transparent — dispatch.py workers need only the two env vars changed

**Concerns:**
- Output quality delta vs real Claude is unknown — needs K2VV ToolCall benchmark before routing any Fairford work
- NVIDIA NIM 40 req/min cap = ceiling on parallel worker throughput (3 workers × burst = hits cap quickly)
- Anthropic ToS position unclear — this is a workaround, not a sanctioned integration
- Governance: CrabTrap + AgentKey still apply at the worker layer; proxy doesn't change the outbound filtering requirement

## Comparison to Existing Pattern

The existing dispatch.py already uses Haiku/Sonnet/Opus tier routing. This proxy adds a fourth option: **local or free open-weight fallback** when Anthropic API rate limits are saturated. Most relevant for overnight batch jobs where latency is acceptable and cost is the constraint.

## Key Takeaway

MIT FastAPI proxy gives Claude Code a zero-code-change path to open-weight model backends. Viable as a dispatch.py cost fallback for non-critical Haiku-tier workers, but requires quality benchmarking before production Fairford use. Anthropic ToS ambiguity is the main blocker for any serious deployment.
