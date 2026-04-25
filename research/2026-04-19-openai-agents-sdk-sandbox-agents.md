---
title: "OpenAI Agents SDK v0.14.2 — Sandbox Agents + MCP Native"
source: https://github.com/openai/openai-agents-python
date: 2026-04-19
tags: [ai-agents, mcp, multi-agent, sdk, openai, claude]
stars: 23000
relevance: dispatch.py architecture, ENGRAM complement, MCP tooling
---

## Summary

OpenAI Agents SDK v0.14.2 (released 2026-04-18) is a lightweight MIT-licensed Python framework for multi-agent workflows. Notable new feature: **Sandbox Agents** — agents deployed in containers for long-horizon, stateful tasks with persistent filesystem access. Provider-agnostic; supports Claude via LiteLLM in addition to OpenAI models.

## Key Features

- **Agents** — LLMs with instructions, tools, guardrails, and handoffs
- **Sandbox Agents** (v0.14.0+) — containerized agents for long-running tasks; persistent filesystem; stateful across sessions
- **MCP as first-class tool type** — alongside function tools and hosted tools; MCP tool layer is native, not bolted on
- **Human-in-the-loop** — escalation mechanisms built in across run lifecycle
- **Sessions** — automatic conversation history management
- **Tracing** — built-in run tracking and observability
- **Guardrails** — input/output safety validation
- **268 contributors**, active development pace (v0.14.2 dropped day after v0.14.0)

## MCP Integration

MCP is listed as a first-class tool category alongside function tools and hosted tools. This matches the direction fabric-mcp and skill-manager-mcp are heading — exposing domain capabilities as MCP tool surfaces callable from any compliant agent.

## Claude/Anthropic Compatibility

Repo ships with `CLAUDE.md`. Claude supported via LiteLLM as model provider — same pattern as dispatch.py workers could adopt for model-switching without code changes.

## Relevance to ClaudesCorner

| Concern | How SDK addresses it |
|---|---|
| dispatch.py Sandbox isolation | Sandbox Agent = containerized long-horizon worker; structural parallel |
| Worker escalation | Human-in-the-loop built in (pairs with AgentRQ pattern) |
| MCP tool surface | First-class MCP tool type = fabric-mcp + skill-manager-mcp drop-in |
| Multi-model routing | LiteLLM backend = Claude/GPT/Gemini switchable per worker |
| Tracing | Built-in; fills dispatch.py observability gap |

## Action Items

- Evaluate Sandbox Agent container spec as dispatch.py worker isolation primitive (pairs with smolvm)
- Cross-reference tracing output format against kpi-monitor alert schema
- Consider LiteLLM adapter layer in dispatch.py workers for model-agnostic execution
