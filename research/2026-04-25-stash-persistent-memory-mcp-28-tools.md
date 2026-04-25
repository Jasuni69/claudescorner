---
title: "Stash — Open-Source Persistent Memory Layer with 6-Stage Consolidation and 28 MCP Tools"
date: 2026-04-25
source: https://alash3al.github.io/stash?_v01
hn_points: 18
tags: [memory, MCP, ENGRAM, agents, pgvector, consolidation]
relevance: high
---

# Stash — Open-Source Persistent Memory Layer with 6-Stage Consolidation and 28 MCP Tools

**Source:** https://alash3al.github.io/stash?_v01 (GitHub: alash3al/stash)
**HN:** 18pts (newest, 2026-04-25)
**License:** Apache 2.0

## What It Is

Stash is an open-source persistent memory layer for AI agents that transforms raw session observations into structured, evolving knowledge. Explicitly positioned as distinct from RAG: "RAG is a search engine — Stash learns."

## Architecture: 6-Stage Consolidation Pipeline

```
Raw observations
    ↓
1. Episodes       — session-scoped events
    ↓
2. Facts          — extracted atomic assertions
    ↓
3. Relationships  — cross-entity connections
    ↓
4. Causal links   — cause→effect chains
    ↓
5. Patterns       — recurring signatures
    ↓
6. Contradiction resolution — conflict detection + reconciliation
```

Recent additions: **goal inference**, **failure pattern detection**, **hypothesis scanning**.

## Technical Stack

- **Storage**: PostgreSQL + pgvector (vector embeddings)
- **Memory organisation**: hierarchical namespaces (user prefs / projects / agent self-knowledge)
- **MCP surface**: 28 tools covering full cognitive stack
- **Model**: any OpenAI-compatible API (OpenRouter, Ollama, Groq, self-hosted)
- **Deploy**: Docker Compose + env vars

## 28 MCP Tools Coverage

Full cognitive stack exposed as MCP tools: episode recording, fact extraction, relationship mapping, causal chain queries, pattern retrieval, contradiction queries, goal state, failure history, hypothesis generation. Single MCP server covers write + read + introspection.

## Signal for ClaudesCorner

**ENGRAM v2 write-layer**: memory-mcp currently stores atomic facts with semantic search. Stash's 6-stage pipeline is the consolidation architecture ENGRAM v2 needs — especially contradiction resolution (memory-mcp has no conflict detection) and causal links (missing from current vectordb).

**Goal inference + failure pattern detection**: these two capabilities directly address the dispatch.py doom-loop problem. If a worker has failed on the same pattern 3 times, Stash would surface it; dispatch.py currently has no cross-session failure memory.

**28 MCP tools vs memory-mcp's 10**: the expanded surface covers agent self-knowledge introspection — workers can query their own failure history before starting a task.

**pgvector backend**: memory-mcp uses sqlite-vec (all-MiniLM-L6-v2). Stash's pgvector backend is production-grade but heavier. ENGRAM v2 decision: sqlite-vec for local/portable, pgvector (via Stash) for team/Fairford deployment.

## Gaps / Caveats

- PostgreSQL dependency = heavier than current sqlite-vec stack
- Docker Compose required — not a drop-in Windows service without WSL2 or Docker Desktop
- 18 HN points = early traction, API stability unknown
- No Claude Code lifecycle hook integration (unlike Cognee) — MCP-only surface
- Consolidation pipeline latency unknown at dispatch.py scale

## Comparison to Existing Stack

| Capability | memory-mcp | Cognee | Stash |
|---|---|---|---|
| Semantic search | ✓ (sqlite-vec) | ✓ (graph+vector) | ✓ (pgvector) |
| Fact extraction | manual | auto | auto (stage 2) |
| Contradiction resolution | ✗ | partial | ✓ (stage 6) |
| Causal links | ✗ | ✗ | ✓ (stage 4) |
| Goal inference | ✗ | ✗ | ✓ |
| Failure pattern detection | ✗ | ✗ | ✓ |
| MCP tools | 10 | via cognee-mcp | 28 native |
| CC lifecycle hooks | ✗ | ✓ (5 hooks) | ✗ |

## Action Items

- Evaluate Stash contradiction resolution as memory-mcp v3 write-gate layer
- Add failure pattern detection to dispatch.py via Stash MCP query pre-task
- Consider Stash as Fairford team memory backend (pgvector scales; sqlite-vec doesn't)
