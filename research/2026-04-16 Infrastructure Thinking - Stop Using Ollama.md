---
title: "Stop Using Ollama — Lessons in Wrapper Risk for LLM Infrastructure"
source: https://sleepingrobots.com/dreams/stop-using-ollama/
date: 2026-04-16
tags: [infrastructure, local-llm, vendor-risk, open-source, agent-backend]
relevance: medium
---

## Summary

A detailed critique of Ollama arguing it misattributes llama.cpp's work, runs 1.8x slower than upstream after a 2025 fork, uses deceptive model naming (e.g. "DeepSeek-R1" silently resolving to smaller distilled variants), and is drifting toward cloud lock-in despite a local-first marketing position.

## Core Argument

Ollama is a wrapper that added convenience but is now subtracting performance and trust. The author recommends returning to llama.cpp directly, or using LM Studio / LiteLLM / ramalama — tools that maintain transparency and upstream performance.

## Why It Matters for Agent Infrastructure

This is a pattern recognition memo, not a specific Ollama decision. The principle:

> **Wrappers that obscure upstream abstractions introduce hidden regressions and trust debt.**

This applies directly to agent stack decisions:

- **MCP servers as wrappers**: Any MCP server wrapping a 3rd-party service should be thin — it should not own state, rename primitives, or add indirection that masks failures
- **LLM routing layers**: LiteLLM, OpenRouter, etc. carry the same wrapper risk — evaluate what they change, not just what they add
- **Skill/tool composition**: Skills that wrap other skills accumulate surface area; prefer direct implementations where possible

## Applicability to Jason's Work

- **ClaudesCorner local models**: If local inference is ever added (for cost or privacy), prefer llama.cpp-direct or ramalama over Ollama
- **Clementine / Fabric**: When wrapping Microsoft Fabric APIs in Claude tools, keep the wrapper thin — don't introduce Ollama-style naming or state divergence
- **MCP server design principle**: Confirmed instinct — thin wrappers, clear attribution, no hidden state

## Appeared On

Hacker News front page 2026-04-16, 141 points.
