---
title: "Cognee — Knowledge Graph Memory Engine with MCP and Claude Code Plugin"
date: 2026-04-17
source: https://github.com/topoteretes/cognee
tags: [agent-memory, knowledge-graph, MCP, claude-code, RAG-alternative, open-source]
relevance: high
---

# Cognee — Knowledge Graph Memory Engine with MCP and Claude Code Plugin

**Repo:** github.com/topoteretes/cognee | 15,862 stars (+170 today)
**Install:** `uv pip install cognee`

## What It Does

Open-source knowledge engine that gives AI agents persistent, learning memory. Combines vector search + graph databases + cognitive science to transform documents into interconnected knowledge queryable by agents.

## Four Core Operations

```python
import cognee
await cognee.remember("Your text here")   # store permanently or in session
results = await cognee.recall("query")    # auto-routes to vector or graph search
await cognee.forget("topic")              # delete when done
await cognee.improve(feedback)            # refine future responses from outcomes
```

## Graph vs RAG

Traditional RAG retrieves semantic chunks. Cognee additionally:
- Maps **relationships between concepts** across documents
- Tracks how information **evolves and interconnects** over time
- **Auto-routing recall** selects optimal search strategy per query
- Updates memory from agent outcomes → prevents repeated mistakes

## Agent Integrations

- **Claude Code plugin**: Captures tool calls into session memory via lifecycle hooks; syncs to permanent graph at session end
- **Hermes Agent**: Configure as memory provider for session-aware knowledge graph recall
- **Custom agents**: `await cognee.serve()` routes any Python agent to managed cloud instance
- **MCP**: `cognee-mcp` package for tool-standardized LLM connections

## Relevance to Jason's Work

Highly relevant to **ENGRAM**. Cognee is a production-scale version of the same problem ENGRAM solves — agent memory that persists across sessions and learns from experience. Key differentiators to consider adopting:

1. **Graph-based recall routing** (auto-selects vector vs graph per query) — more sophisticated than ENGRAM's current flat memory-mcp search
2. **Claude Code lifecycle hook integration** — same pattern Jason uses in `projects/memory-mcp/`; worth comparing implementation
3. **`cognee.improve()`** — explicit feedback loop to update memory from outcomes; aligns with `feedback_flywheel.py` concept

Could serve as a drop-in memory backend for ENGRAM or as a reference architecture for upgrading memory-mcp beyond all-MiniLM-L6-v2 embeddings.
