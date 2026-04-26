---
title: "Memori — Agent-Native Memory Infrastructure"
date: 2026-04-25
source: https://github.com/MemoriLabs/Memori
stars: 13807
stars_weekly_gain: 115
license: Apache-2.0
tags: [agent-memory, mcp, engram, memory-mcp, production]
relevance: high
---

# Memori — Agent-Native Memory Infrastructure

**13.8k stars · Apache-2.0 · Python 71% / TypeScript 16% / Rust 8%**

## What it is

LLM-agnostic memory layer that converts agent interactions into structured, persistent state for production systems. Agents retain and recall context across sessions without embedding full conversation history in prompts.

## Key architecture

Three-tier entity model:
- **Entity** — users, places, objects
- **Process** — agents, programs
- **Session** — current interaction window

Augmentation layers: attributes, events, facts, people, preferences, relationships, rules, skills — all tracked without latency.

**Intelligent Recall** automatically injects relevant context into future prompts.

## Performance (LoCoMo benchmark)
- **81.95% accuracy** at only **1,294 tokens per query**
- **5% of full-context token cost** — 20× cheaper than full-history prompting
- **67% smaller prompts** vs Zep

## MCP & integrations

- HTTP-based MCP server — zero-SDK integration with Claude Code, Cursor, Codex, Warp
- **OpenClaw Plugin** — captures durable facts/preferences post-conversation, auto-injects on next prompt
- Frameworks: LangChain, Pydantic AI, Agno
- LLMs: OpenAI, Anthropic, Bedrock, Gemini, DeepSeek, Grok

```python
mem = memori.client(api_key="...")
mem.attribution(entity_id="jason", process_id="dispatch-worker")
mem.resetSession()
```

## Deployment
- **Memori Cloud** — managed, free tier with rate limits
- **BYODB** — self-hosted, bring-your-own database

## Signal for ClaudesCorner

**Direct ENGRAM parallel**: same entity/session/process layering that memory-mcp implements, but benchmarked at production scale (81.95% LoCoMo vs unverified). The 5% token cost target is the same design constraint memory-mcp's Haiku write-gate enforces. Key differentiator Memori has that memory-mcp lacks: **transparent SDK interception** (registers existing Anthropic client, captures calls without code changes). OpenClaw Plugin pattern = ENGRAM's PostToolUse hook pattern in production.

**Actionable**: benchmark memory-mcp retrieval accuracy against LoCoMo; adopt Memori's entity/process/session attribution schema in memory-mcp write payloads; evaluate BYODB mode as memory-mcp backend upgrade path.
