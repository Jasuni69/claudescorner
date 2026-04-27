---
title: "Anthropic Changelog: Claude Managed Agents Memory — Public Beta"
date: 2026-04-26
source: https://platform.claude.com/docs/en/release-notes/overview
tags: [anthropic, managed-agents, memory, engram, dispatch, api]
clipped_by: dispatch-agent
---

# Claude Managed Agents Memory — Public Beta (Apr 23, 2026)

**Source:** Anthropic Docs Changelog  
**Signal strength:** HIGH — directly affects ENGRAM memory architecture and dispatch.py worker session state

## What shipped

Memory for Claude Managed Agents is now in **public beta** under the existing `managed-agents-2026-04-01` beta header. Full integration guide: `/docs/en/managed-agents/memory`.

This is an additive capability on top of the Managed Agents harness (launched Apr 8), which already provides:
- Fully managed agent sessions with secure sandboxing
- Built-in tools + server-sent event streaming
- Container configuration via API

Memory adds persistent cross-session state to Managed Agents — same header, no new header required.

## Why this matters for ClaudesCorner

**ENGRAM architecture:**  
The official Managed Agents memory layer is now a direct competitor to memory-mcp. The question is whether it uses a compatible model (semantic search? vector store? key-value?) or a proprietary one. If the storage model is opaque/hosted, ENGRAM's self-hosted sqlite-vec approach remains differentiated. If the API is open, it could become a backend option for memory-mcp's write gate.

**dispatch.py workers:**  
Current dispatch.py workers are stateless — each session loads context from HEARTBEAT.md and task_plan.md. Managed Agents memory would allow workers to accumulate session learnings across runs without file-based handoff. This is the same pattern as ENGRAM's `daily logs → vectordb` promotion chain, but hosted by Anthropic.

**Managed Agents harness vs. dispatch.py:**  
The Apr 8 launch already introduced a hosted alternative to dispatch.py (sandboxing + SSE streaming + container config). The memory beta closes the last major gap. Key remaining differentiators for dispatch.py:
- Local execution (no hosted dependency, no Anthropic data retention)
- Fabric/Power BI MCP integration (not available in Managed Agents)
- Custom task queue (tasks.json) and VERIFY oracles
- CrabTrap + AgentKey governance stack

**Rate Limits API (Apr 24):**  
Also shipped this week: programmatic rate limit querying via `/v1/rate-limits`. Administrators can now query limits per org/workspace. Actionable: wire into dispatch.py's token budget logic to auto-back-off before hitting hard limits rather than catching 429 errors reactively.

## Actionable backlog

1. Read `/docs/en/managed-agents/memory` — determine storage model compatibility with memory-mcp
2. Add Rate Limits API call to dispatch.py worker startup: cache the org limits and adjust `MAX_CONTEXT_TOKENS` accordingly
3. Update ENGRAM README: position memory-mcp as self-hosted alternative with Fabric/local-execution advantage over Managed Agents memory

## Context

- Managed Agents harness launched: Apr 8, 2026
- `ant` CLI (native API client for Claude Code): also launched Apr 8
- Bedrock GA with Claude Opus 4.7 + Haiku 4.5: Apr 16 (27 AWS regions, `/anthropic/v1/messages` endpoint)
- Claude Sonnet 4 + Opus 4 deprecated Apr 14, retirement June 15 — dispatch.py workers should pin `claude-sonnet-4-6` not `claude-sonnet-4`
