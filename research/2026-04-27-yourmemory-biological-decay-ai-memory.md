---
title: "YourMemory — Ebbinghaus Forgetting Curve for AI Agent Memory"
source: https://github.com/sachitrafa/YourMemory
author: sachitrafa
date: 2026-04-27
hn_points: 50
hn_comments: 25
stars: 79
license: CC-BY-NC-4.0
tags: [memory, engram, memory-mcp, ebbinghaus, forgetting-curve, vector-graph-hybrid, locomo]
clipped_by: dispatch-plan-agent
---

# YourMemory — Ebbinghaus Forgetting Curve for AI Agent Memory

**Source**: github.com/sachitrafa/YourMemory | Show HN 2026-04-27 | 79 stars | CC-BY-NC-4.0

## Core Concept

YourMemory applies the **Ebbinghaus forgetting curve** to AI agent memory: memories decay exponentially over time, but decay is slowed by importance weight (0–1 scale) and recall frequency. Memories below strength 0.05 are auto-pruned on a 24-hour APScheduler cycle. Survival times vary by category (strategy ~38 days, failure ~11 days). This is a persistent memory MCP server targeting Claude, Cline, and Cursor.

## Technical Architecture

**Storage layer:**
- DuckDB (default, local) or PostgreSQL + pgvector (production)
- NetworkX (default) or Neo4j for graph operations

**Retrieval (two rounds):**
1. Vector search — cosine similarity across all memories
2. Graph expansion — BFS from top-N results to surface vocabulary-different but semantically related memories

**Decay model formula:**
```
strength(t) = initial_strength × exp(-λ × t / (importance × category_weight))
```
Where λ is the forgetting rate constant and category_weight controls domain-specific survival times.

## Benchmark

On **LoCoMo** (1,534 QA pairs across long conversational histories):
- YourMemory **Recall@5: 59%** (95% CI: 56–61%)
- Zep Cloud: **28%**
- ~2× improvement vs the leading commercial competitor

## Relevance for ENGRAM / memory-mcp

### Auto-pruning = write-gate complement
Current memory-mcp uses `MEMORY_WRITE_GATE=1` to control writes at ingestion time. YourMemory's decay pruner addresses the opposite end: **expiry of stale entries** without requiring manual curation. The stale-memory-scanner (`projects/stale-memory-scanner/`) currently scores state-vs-fact density — integrating a decay coefficient would make scoring continuous rather than batch.

### Failure category survival time
YourMemory gives failure memories an 11-day survival window vs 38 days for strategy. This maps directly to memory governance: feedback memories (corrections) should have shorter half-lives than project decisions. Worth encoding in memory-mcp as a `decay_category` field on write.

### Two-pass retrieval validation
YourMemory's vector→graph BFS two-round retrieval independently validates brain-memory's two-pass approach (`projects/brain-memory/src/vectordb.py`). The graph expansion step surfaces memories that share entities/relationships but not vocabulary — a gap that pure cosine similarity misses.

### LoCoMo benchmark
LoCoMo is the correct benchmark for memory-mcp quality evaluation (long conversational history QA). Currently memory-mcp has no eval harness — LoCoMo is the backlog target.

## Limitations

- **CC-BY-NC-4.0**: Non-commercial license blocks direct Fairford production use. Observe architecture; don't fork into commercial product.
- **79 stars**: Early project, API may change
- **No write-gate**: No MEMORY_WRITE_GATE equivalent — all memories written unconditionally; validates memory-mcp's write-gate design as differentiated
- **DuckDB default**: Not compatible with brain-memory's sqlite-vec vectorstore without migration

## Action Items

- **Backlog**: Add `decay_category` field to memory-mcp write schema (feedback=short, project=medium, reference=long)
- **Backlog**: Implement auto-prune pass in memory-mcp (APScheduler or cron) for entries below configurable strength threshold
- **Evaluate**: LoCoMo benchmark as memory-mcp quality eval harness — 1,534 QA pairs, open dataset
- **Watch**: License change; if Apache/MIT, consider BFS graph-expansion layer for brain-memory retrieval
