---
title: "Stash — Open-Source Persistent Memory MCP Server (pgvector + 5-layer pipeline)"
date: 2026-04-26
source: https://github.com/alash3al/stash
hn: https://news.ycombinator.com/item?id=47897790
hn_points: 173
hn_comments: 73
tags: [mcp, memory, agents, engram, pgvector, go]
relevance: [memory-mcp, ENGRAM, brain-memory, dispatch.py]
---

# Stash — Persistent Memory MCP Server

**Repo:** `alash3al/stash` | 267 stars | Go (81%) | Apache 2.0  
**HN:** 173pts / 73 comments | 2026-04-25

## What it is

Open-source MCP server that gives any AI agent persistent cognitive memory across sessions. Backed by **PostgreSQL + pgvector**. Ships with **28 MCP tools**. Works with Claude Desktop, Cursor, Windsurf, Cline, Continue, OpenAI Agents, Ollama, OpenRouter — anything MCP-compatible.

## Architecture: 5-layer consolidation pipeline

Raw observations flow through an auto-running background consolidation process:

1. **Episodes** — append-only raw observations (what happened)
2. **Facts** — synthesized beliefs with confidence scores
3. **Relationships** — entity knowledge graph edges
4. **Patterns** — higher-order abstractions from repeated facts
5. **Goals & Failures** — intent tracking + failure pattern prevention

The consolidation loop runs continuously, promoting Episodes → Facts → Relationships → Patterns automatically without agent intervention.

**Namespace model:** hierarchical folders (`/users/alice`, `/projects/restaurant-saas`, `/self`). Agents can maintain a `/self` namespace tracking their own capabilities and preferences.

## Deployment

```bash
git clone https://github.com/alash3al/stash
cp .env.example .env   # add API key + model
docker compose up      # starts postgres+pgvector + MCP server
```

## HN discussion signal

Top criticism: **misleading parity claim with Claude.ai** — Claude uses automated background summarization; Stash requires explicit `store`/`remember` calls. Multiple commenters called it "pg_vector + mcp with two functions." Key concern: no benchmarks proving retrieval quality over baseline vector search. Context pollution across unrelated projects flagged as unsolved.

## Relevance to ClaudesCorner

| Dimension | Stash | memory-mcp (ClaudesCorner) |
|---|---|---|
| Backend | PostgreSQL + pgvector | SQLite + all-MiniLM-L6-v2 |
| Write model | Explicit tool calls | Haiku write-gate (MEMORY_WRITE_GATE=1) |
| Consolidation | Auto background loop | Manual (feedback_flywheel.py) |
| MCP tools | 28 | 10 |
| Language | Go | Python |
| License | Apache 2.0 | — |

**Key architectural difference:** Stash auto-consolidates (no human gate); memory-mcp uses Haiku as a write-gate to prevent garbage accumulation. HN critics confirm the auto-consolidation approach has quality risks — validates the MEMORY_WRITE_GATE=1 design choice.

**ENGRAM relevance:** Stash is the closest public analog to memory-mcp by feature count (28 tools vs 10). The 5-layer pipeline (Episodes→Facts→Relationships→Patterns→Goals) is a more structured version of the breadcrumb→daily→durable promotion rules in memory governance. The `/self` namespace pattern is an independent reinvention of SOUL.md.

**Backlog signal:** Stash's failure pattern layer (`/failures` namespace) is a feature gap in memory-mcp — storing what went wrong to prevent repetition. Worth adding a `record_failure` tool to memory-mcp alongside `record_learnings`.
