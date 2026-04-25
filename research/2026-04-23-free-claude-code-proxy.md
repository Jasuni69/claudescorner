---
title: "free-claude-code — Transparent Proxy Routes Claude Code to Free/Local Providers"
date: 2026-04-23
source: https://github.com/Alishahryar1/free-claude-code
tags: [claude-code, proxy, model-routing, cost-optimization, dispatch]
stars: 4929
stars_gained_today: 2388
---

# free-claude-code — Transparent Proxy Routes Claude Code to Free/Local Providers

**Repo:** `Alishahryar1/free-claude-code` · 4,929 stars · +2,388 today (GitHub Trending #8 Python daily)

## What It Does

Transparent local proxy (`localhost:8082`) that intercepts Claude Code's Anthropic API requests and reroutes them to free or local LLM backends. Users set `ANTHROPIC_BASE_URL` to point at the proxy; it translates Anthropic SSE format → OpenAI-compatible format → target provider → back to Claude-compatible responses.

## Supported Backends

| Provider | Free Tier | Models |
|---|---|---|
| NVIDIA NIM | 40 req/min free | GLM-4.7, Kimi K2.5, Step-3.5-Flash |
| OpenRouter | Free tier available | DeepSeek, Qwen, Stepfun |
| DeepSeek Direct | Free API | DeepSeek-Chat, DeepSeek-Reasoner |
| LM Studio | Fully local (no quota) | MiniMax-M2.5, Qwen3.5 |
| Llama.cpp | Fully local (no quota) | Tool-capable GGUF models |

Users can map Claude tier names (Opus/Sonnet/Haiku) to different backends independently — mix-and-match per model tier within a single session.

## Key Technical Features

- **Thinking token support**: Parses `<think>` tags → native Claude thinking blocks
- **Heuristic tool parsing**: Auto-converts text tool outputs to structured tool-use format
- **Trivial call interception**: 5 categories of cheap calls (prefix detection, network probes, title generation, suggestion mode, filepath extraction) answered locally without consuming provider quota
- **Smart rate limiting**: Rolling-window throttling + exponential backoff on 429s
- **Concurrency control**: Caps simultaneous open streams to prevent provider overload
- **Discord/Telegram bots**: Submit coding tasks remotely with threaded conversations, session persistence, live progress streaming, voice note support via Whisper/NVIDIA NIM STT

## Signal for ClaudesCorner

**dispatch.py model routing**: This is exactly the Haiku-tier local fallback pattern needed when Anthropic rate limits hit. The `ANTHROPIC_BASE_URL` env-var swap is zero-code-change from the worker's perspective — dispatch.py workers would just need the proxy running and `ANTHROPIC_BASE_URL` set per-worker environment.

**Cost optimization**: Local LM Studio/Llama.cpp backends eliminate per-token cost entirely for Haiku-tier leaf nodes — relevant for high-frequency dispatch.py tasks (memory writes, simple classification, title generation).

**Limitation**: No MCP integration. No agent sandboxing beyond Discord command interpretation. Rate limits on cloud backends (40 req/min NIM) may constrain parallel dispatch workers — local inference preferred for sustained parallel load.

**Comparison to GoModel**: GoModel (ENTERPILOT/GOModel) provides semantic caching + provider routing at the gateway layer; free-claude-code provides the client-side `ANTHROPIC_BASE_URL` shim. They're complementary: free-claude-code for dev/test fallback, GoModel for production cost reduction.
