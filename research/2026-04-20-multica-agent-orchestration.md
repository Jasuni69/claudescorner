---
title: "Multica — Issue-Assignment Agent Orchestration Platform"
date: 2026-04-20
source: https://github.com/multica-ai/multica
tags: [agent-orchestration, dispatch, mcp, claude-code, skill-accumulation, pgvector]
signal: high
---

# Multica — Turn Coding Agents into Real Teammates

**Repo**: multica-ai/multica | 17,532 stars (+7,831 this week, #5 trending all languages) | Apache-2.0 | v0.2.9 April 2026

## What It Is

Open-source agent orchestration platform. Teams assign issues (like GitHub issues) to coding agents; agents autonomously execute, stream progress via WebSocket, post status comments, and accumulate reusable skills across sessions.

## Architecture

| Layer | Tech |
|-------|------|
| Frontend | Next.js 16 (App Router) |
| Backend | Go + Chi router + sqlc |
| Database | PostgreSQL 17 + pgvector |
| Runtime | Local daemon executing agent CLIs |
| Comms | WebSocket (real-time progress streaming) |

## Workflow

1. Create issue → assign to agent (identical UX to assigning to a human teammate)
2. Daemon picks up task, executes via agent CLI
3. Agent streams progress; posts blockers as comments
4. Completed solution promoted to team skill store (pgvector embeddings)

## Supported Agent Frameworks

Claude Code, Codex, OpenClaw, OpenCode, Hermes, Gemini, Pi, Cursor Agent — auto-detected via PATH.

## Notable Features

- **Multi-workspace** with role-based permissions
- **Unified runtime dashboard** — local + cloud compute in one view
- **Vendor-neutral** — swap any LLM provider
- **Self-hosted** via Docker
- **pgvector skill store** — completed solutions become searchable embeddings for the whole team

## Gaps vs ClaudesCorner

| Multica capability | dispatch.py current state | Gap |
|--------------------|--------------------------|-----|
| WebSocket progress streaming | stdout-only, no live feed | No real-time visibility |
| Issue-assignment UX | Raw tasks.json JSON | No human-friendly task creation |
| Cross-session pgvector skill accumulation | skill-manager-mcp (FTS5+vector) | Already covered — multica's is team-scoped |
| Blocker escalation via comments | Not implemented | AgentRQ covers this gap |
| Multi-workspace RBAC | Single-user | N/A for ClaudesCorner solo use |

## Relevance to ClaudesCorner

The pgvector skill store accumulation pattern is the same bet as skill-manager-mcp but team-scoped. The WebSocket progress streaming is a real gap — dispatch.py workers are fire-and-forget with no live visibility. The issue-assignment UX is irrelevant for solo use but validates AgentRQ as the right escalation primitive.

**One-line signal**: Multica's issue→agent→WebSocket-stream→pgvector-skill pipeline is the team-scale version of dispatch.py + skill-manager-mcp, and its WebSocket progress layer is the one capability ClaudesCorner's dispatcher currently lacks.
