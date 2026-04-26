---
title: "GPT-5.5 Prompting Guide — OpenAI's Warning: Treat as New Model Family, Not Drop-In"
date: 2026-04-25
source: https://simonwillison.net/2026/Apr/25/gpt-5-5-prompting-guide/
tags: [gpt-5-5, openai, dispatch, model-routing, prompt-engineering, multi-model]
type: research-clip
---

# GPT-5.5 Prompting Guide — Willison Analysis

**Source:** simonwillison.net — 2026-04-25
**Original:** OpenAI GPT-5.5 prompting guidance page

## Key Finding

OpenAI's official guidance: **treat GPT-5.5 as a new model family, not a drop-in replacement** for gpt-5.2 or gpt-5.4. Existing prompts should not be migrated — start from minimal prompts and rebuild against fresh test cases.

## What Changes

- **Paradigm shift:** Don't carry forward legacy instruction sets. Start minimal, preserve only core functionality.
- **Fresh tuning required for:** reasoning effort, verbosity, tool descriptions, output formats
- **User-visible progress updates:** For long-running tasks, send a short acknowledgment before tool calls to prevent perceived freezing (agentic UX pattern)
- **Rebuild, don't migrate:** Legacy optimized prompts for gpt-5.2/5.4 will not transfer cleanly

## Implications for Multi-Model Agent Routing

Prompt incompatibility between model generations means:
1. Any multi-model routing system (like dispatch.py) must maintain **model-specific prompt variants** rather than a single unified prompt per worker role
2. Switching cost from Claude Sonnet 4.6 to GPT-5.5 is higher than apparent — not just API endpoint swap, but full prompt re-tuning per worker
3. Validates **holding Sonnet 4.6 as dispatch.py default** until K2VV ToolCall benchmark confirms GPT-5.5 routing is worthwhile and prompts are re-tuned

## Signal for Jason's Work

**dispatch.py:** Model routing to GPT-5.5 is not a 1-line change. Sonnet 4.6 worker prompts cannot be used as-is with GPT-5.5. Switching cost is meaningful even if raw capability benchmarks favor GPT-5.5.

**ENGRAM:** SOUL.md as the canonical instruction layer must be model-aware if multi-model support is added. A `model:` frontmatter key in SOUL.md enabling per-model instruction variants would be the correct abstraction.

**Competitive signal:** GPT-5.5 joining DeepSeek V4 and Kimi K2.6 as Sonnet 4.6 challengers. All three require fresh benchmarking via K2VV ToolCall before dispatch.py routing changes. The prompting guide's "new model family" warning is the strongest signal yet to gate on benchmarks not just capability claims.
