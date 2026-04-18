---
title: "llm-anthropic 0.25 — Claude Opus 4.7 and Extended Thinking Support"
date: 2026-04-17
source: https://simonwillison.net/2026/Apr/16/llm-anthropic/
author: Simon Willison
tags: [claude, anthropic, llm-cli, extended-thinking, tooling]
signal: high
clipped: 2026-04-17
---

## Summary

Simon Willison released `llm-anthropic 0.25`, the LLM CLI plugin for Anthropic models. Key additions:

- **New model**: `claude-opus-4.7` now available via `llm -m claude-opus-4.7`
- **Extended thinking**: `thinking_effort: xhigh` parameter unlocks Opus 4.7's deep reasoning mode
- **New boolean flags**: `thinking_display` and `thinking_adaptive` — control whether extended reasoning is shown or adapted per prompt
- **Token defaults**: `max_tokens` now defaults to the model's maximum (previously undercut)
- **API cleanup**: removed obsolete `structured-outputs-2025-11-13` beta header for older models

## Relevance

`thinking_display` is currently only available in JSON output/logs — not plain text output — limiting accessibility. The `xhigh` effort level maps directly to what Claude Code's `/ultrareview` uses under the hood.

For agent workflows: extended thinking at `xhigh` increases latency but materially improves multi-step reasoning quality. Useful for planning phases, not per-tool-call steps.

## Usage

```bash
pip install -U llm-anthropic
llm -m claude-opus-4.7 "your prompt" --option thinking_effort xhigh
```

## Why It Matters

Jason uses Claude API directly in `bi-agent` and other tools. This plugin wraps the same API — useful for CLI-level testing of Opus 4.7 behaviors before wiring into code. The `max_tokens` fix means previous calls were silently truncated.
