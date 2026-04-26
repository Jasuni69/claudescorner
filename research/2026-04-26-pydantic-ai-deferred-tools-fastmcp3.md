---
title: "pydantic-ai v1.87 — HandleDeferredToolCalls + FastMCP 3.2 + DynamicToolset"
date: 2026-04-26
source: https://github.com/pydantic/pydantic-ai/releases
tags: [mcp, agents, tool-loading, orchestration, claude, python]
stars: 16632
signal: high
relevance: [skill-manager-mcp, dispatch.py, memory-mcp]
---

# pydantic-ai v1.87 — Deferred Tool Loading + FastMCP 3.2

**Source:** github.com/pydantic/pydantic-ai — 16,632 stars | Released 2026-04-24

## What shipped

### v1.87.0 — HandleDeferredToolCalls
- New `HandleDeferredToolCalls` capability + `handle_deferred_tool_calls` hook: agents can register tool schemas lazily and resolve them only when the model actually requests that tool. Tools not called in a given turn carry zero token cost.
- `ProcessEventStream` capability: structured event stream from agent runs, enabling per-step observability without full transcript serialization.
- GPT-5.5 thinking setting support added.

### v1.86.x — DynamicToolset + MCP lifecycle
- `DynamicToolset`: runtime-composable toolset that mounts/unmounts MCP servers per-agent-run rather than at framework init. MCPServer lifecycle (connect/disconnect) is managed within the toolset, not globally.
- Bug fix: MCPServer lifecycle management in DynamicToolset — previously MCP server connections leaked across agent runs in multi-agent setups.
- Per-tool-call metadata injection via `FastMCPToolset` (v1.83.0): arbitrary context (caller ID, auth token, session tag) injected per call without modifying tool signatures.

### v1.82-1.85 — FastMCP 3.2 upgrade + online eval
- FastMCP upgraded from 2.x → 3.2.0: streamable HTTP, OAuth 2.1 elicitation, resource subscriptions, and improved session multiplexing.
- Online evaluation via OpenTelemetry events (v1.85.0): each tool call emits OTEL spans — direct integration with Grafana/Datadog without a separate eval harness.

## Why it matters to ClaudesCorner

**Direct parallel to skill-manager-mcp deferred-load:**
`HandleDeferredToolCalls` is the production Python implementation of exactly the pattern Anthropic's MCP Production Guide describes (85% token reduction via tool search before invocation). The hook fires when the model requests a tool whose schema hasn't been loaded yet — the framework fetches and injects it at that moment. skill-manager-mcp's `skill_search` → `skill_load` two-step does the same thing manually today; this formalizes it as a capability.

**DynamicToolset → dispatch.py worker isolation:**
Each dispatch.py worker currently shares a global MCP config. `DynamicToolset` is the correct primitive for giving each worker its own MCP server lifecycle — mount only the tools that worker's task requires, unmount on completion. Eliminates cross-worker tool scope bleed.

**FastMCP 3.2 OAuth 2.1 elicitation:**
memory-mcp and fabric-mcp both lack OAuth. FastMCP 3.2's built-in elicitation flow is the lowest-effort path to adding OAuth-scoped tool access without writing a separate auth layer.

**Per-tool metadata injection:**
`FastMCPToolset` metadata injection = the missing link for passing dispatch.py worker identity (task_id, tier, worker_index) into MCP tool calls for audit trail. Currently CrabTrap sees the call but the tool itself doesn't know which worker called it.

## Backlog actions
- [ ] Study `HandleDeferredToolCalls` implementation as reference for skill-manager-mcp lazy schema load
- [ ] Prototype `DynamicToolset` wrapper for dispatch.py workers (one toolset per task)
- [ ] Evaluate FastMCP 3.2 OAuth elicitation for fabric-mcp caller scoping
- [ ] Wire per-tool metadata injection (worker_id, task_id) into memory-mcp + fabric-mcp calls

## Related prior clips
- Anthropic MCP Production Guide (2026-04-23) — 85% token reduction via tool search
- skill-manager-mcp v2.6.0 (MEMORY.md) — `skill_search` = primary entry point, deferred load
- dispatch.py parallel dispatcher — 3 workers, shared MCP config (gap identified here)
---
*Clipped by PLAN agent 2026-04-26*
