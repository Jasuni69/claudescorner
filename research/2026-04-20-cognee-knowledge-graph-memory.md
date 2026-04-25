---
title: "Cognee — Knowledge Graph Memory Engine for AI Agents"
date: 2026-04-20
source: https://github.com/topoteretes/cognee
stars: 16528
weekly_gain: +1347
tags: [memory, knowledge-graph, vector, mcp, engram, claude-code, lifecycle-hooks]
signal: high
clipped: 2026-04-20
---

# Cognee — Knowledge Graph Memory Engine for AI Agents

## Overview
**16.5k stars, +1.3k this week.** Open-source knowledge engine that unifies graph databases, vector search, and cognitive science principles for persistent AI agent memory. Apache-2.0 / self-hostable.

GitHub: https://github.com/topoteretes/cognee  
Install: `uv pip install cognee` (Python 3.10–3.13)

## Architecture

Three-layer hybrid store:
- **Vector search** — semantic similarity recall
- **Graph database** — relationship mapping, entity linking
- **Auto-routing** — selects recall strategy based on query type

Four primary operations:
```python
await cognee.remember(data)   # permanent storage + graph processing
await cognee.recall(query)    # auto-routed retrieval
await cognee.forget(data)     # deletion
await cognee.improve(feedback) # feedback integration loop
```

## Claude Code Integration — 5 Lifecycle Hooks

Cognee ships a Claude Code plugin that hooks into:
- `SessionStart` — load prior session context
- `PostToolUse` — auto-capture tool results
- `UserPromptSubmit` — log incoming intent
- `PreCompact` — flush before context compression
- `SessionEnd` — consolidate session into persistent graph

This is the most complete Claude Code memory capture pattern observed to date. Covers the same lifecycle events as the PostCompact hook in ClaudesCorner's settings.json but adds graph structure on top of flat vector storage.

## Key Differentiators vs. Standard RAG

| Feature | Standard RAG | Cognee |
|---|---|---|
| Storage | Flat chunks | Knowledge graph + vectors |
| Recall routing | Always vector | Auto-selects graph vs. vector |
| Feedback | None | `cognee.improve()` loop |
| Session sync | Manual | Background auto-sync |
| Cross-session | Requires manual indexing | Persistent by default |

## Integrations
- **Hermes Agent** — session-aware knowledge graph memory layer
- **MCP** — available as `cognee-openclaw` plugin
- **Research paper** — arXiv:2505.24478 (optimizing KG-LLM interfaces)
- **Managed cloud** — Cognee Cloud + Railway/Modal/Fly.io self-host options

## Relevance to ClaudesCorner / ENGRAM

**Strongest ENGRAM implementation reference found.** The 5-hook Claude Code plugin pattern is more complete than the current `on_stop.py` + PostCompact setup. Specific gaps it closes:

1. **`PostToolUse` auto-capture** — currently missing; would eliminate manual `write_memory` calls
2. **`UserPromptSubmit` intent logging** — not in current hooks; enables intent→outcome tracking
3. **Graph structure** — memory-mcp uses flat vector search; graph layer adds relationship traversal

**`cognee.improve()` feedback loop** — directly maps to `feedback_flywheel.py` concept in SOUL.md self-improvement infrastructure. This is the missing runtime feedback mechanism.

**MCP wrapper opportunity** — `cognee-openclaw` exists but there is no `cognee-mcp` standalone. A thin MCP wrapper exposing `remember/recall/forget/improve` as 4 tools would make cognee accessible to any dispatch.py worker.

## Action Items
- Study `cognee-openclaw` plugin source for hook implementation patterns
- Evaluate `cognee.improve()` as runtime feedback layer for feedback_flywheel.py
- Consider adding `PostToolUse` hook to ClaudesCorner settings.json (see cognee pattern)
- Flag as ENGRAM v2 memory backend candidate (graph+vector > flat vector)
