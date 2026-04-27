---
title: "Databases Were Not Designed for This"
source: https://arpitbhayani.me/blogs/defensive-databases/
author: Arpit Bhayani
date: 2026-04-26
clipped: 2026-04-26
hn_points: 26
hn_comments: 10
tags: [ai-agents, database, safety, dispatch, bi-agent, fairford, governance]
---

## Summary

AI agents break five foundational assumptions databases were built around. The fix is making optional best-practices mandatory when agents are callers.

## The 5 Broken Assumptions

1. **Deterministic callers** — agents generate queries dynamically; no pre-review possible
2. **Intentional writes** — agents write on flawed reasoning or retry loops, not deliberate intent
3. **Brief connections** — multi-step reasoning holds connections open across LLM inference time
4. **Loud failures** — semantically wrong queries return rows silently; no exception raised
5. **Schema as developer contract** — legacy naming and structure confuses language models

## Defensive Mitigations

- **Soft deletes** — never hard-delete from agent-accessible tables; `deleted_at` + filtered views
- **Append-only logs** — agent writes land in audit tables; reconciliation step promotes to live
- **Idempotency keys** — agent retries can't double-write; required on all agent-initiated mutations
- **Role-per-agent-type RBAC** — each agent class gets minimum required table permissions; blast radius bounded
- **Query tagging** — `/* agent=dispatch-worker-1 task=xyz */` prepended to all agent SQL for observability

> "The database was not designed for this caller. But the tools to make it safe are already there."

## Relevance to ClaudesCorner

- **dispatch.py workers**: any DB-adjacent workers need per-role credentials, not shared admin; append-only output artifacts already correct pattern
- **bi-agent DAX generation**: DAX queries are read-only but schema confusion is real — schema_spec.md cross-ref oracle is correct mitigation; add table/column alias comments for LLM clarity
- **Fairford Phase 2**: Fabric Lakehouse tables accessed via fabric-mcp need soft-delete pattern + FABRIC_CALLER_TOKEN scoping already in backlog; per-agent Entra ID service principal = correct implementation
- **memory-mcp write-gate**: MEMORY_WRITE_GATE=1 Haiku guard is the append-only pattern applied to the memory layer — same reasoning

## Action Items

- Add `/* agent=... */` query tagging to bi-agent DAX output format (zero-cost observability)
- Fairford Phase 2 checklist: per-agent Entra service principal + soft-delete on all agent-writable Fabric tables
- Evaluate append-only log pattern for dispatch.py task output artifacts (tasks.json mutation log)
