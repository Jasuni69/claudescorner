---
title: "Agents Aren't Coworkers — Embed Them in Your Software"
source: https://www.feldera.com/blog/ai-agents-arent-coworkers-embed-them-in-your-software
date: 2026-04-26
clipped: 2026-04-26
via: Hacker News front page (13pts)
tags: [ai-agents, architecture, cdc, reconciliation, fabric-mcp, dispatch]
---

## Summary

Feldera argues agents should be **ambient embedded systems**, not conversational coworkers. The core problem: treating agents like chat partners requires constant human supervision, produces token waste, and breaks when the human isn't watching.

## Three architectural patterns the post endorses

1. **CLI interfaces** — agents interact via structured commands, not prose; eliminates token waste and ambiguity
2. **Declarative specifications** — express desired outcomes (schemas, configs) rather than procedural steps; agents reconcile current state to target
3. **Reconciliation loops** — Kubernetes-style "converge toward declared target state" continuously; agent detects drift and self-corrects without prompting

## Key insight: Change Data Capture (CDC) over polling

Instead of agents scanning tables and asking "what changed?", databases emit **precise change streams** (insert/update/delete events). Agents react to events in real time:

> "Transaction T123 inserted: $9,800 → fraud check triggered immediately"

vs. polling: "SELECT * FROM transactions WHERE updated_at > last_check" every N seconds.

Feldera's incremental query engine is the product vehicle, but the CDC principle is model-agnostic.

## Relevance to ClaudesCorner

| Pattern | Where it applies |
|---|---|
| CDC event streams | **fabric-mcp**: Fabric datasets can expose change feeds; fabric-mcp tools should react to change events not poll full tables |
| Declarative reconciliation | **dispatch.py**: workers declare target artifact state (task_plan.md) and reconcile — already partially implemented |
| CLI-first agent interface | **memory-mcp / skill-manager-mcp**: all tools are already CLI-style; validates the design |
| Ambient not conversational | **kpi-monitor**: polling Python loop should be replaced with CDC-triggered check |

## Signal rating: HIGH
Direct architectural validation for fabric-mcp event-driven design. The CDC + reconciliation loop framing is a cleaner mental model than "agent that queries Fabric" — it's "agent that subscribes to Fabric change feeds."
