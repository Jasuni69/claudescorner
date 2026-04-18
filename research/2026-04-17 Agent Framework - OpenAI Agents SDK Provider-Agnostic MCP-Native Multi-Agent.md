---
title: "OpenAI Agents SDK — Provider-Agnostic, MCP-Native Multi-Agent Framework"
date: 2026-04-17
source: https://github.com/openai/openai-agents-python
tags: [agent-framework, MCP, multi-agent, tool-calling, openai]
relevance: high
---

# OpenAI Agents SDK — Provider-Agnostic, MCP-Native Multi-Agent Framework

**Source:** github.com/openai/openai-agents-python
**Stars today:** ~172 (GitHub trending #5 Python, daily)

## What It Is

Lightweight Python SDK for multi-agent workflows. Despite the name, explicitly provider-agnostic — supports OpenAI Responses/Chat APIs and 100+ other LLMs via LiteLLM.

## Core Primitives

| Primitive | Description |
|---|---|
| Agents | LLM instances with instructions, tools, guardrails, handoff capability |
| Sandbox Agents | Container-aware agents with persistent filesystem state across runs |
| Handoffs | Agent-to-agent delegation for specialization |
| Tools | Functions, **MCP integrations**, hosted tools |
| Sessions | Automatic conversation history management |
| Tracing | Built-in observability dashboard |
| Guardrails | Input/output validation layer |
| Realtime Agents | Voice agent support via gpt-realtime-1.5 |

## MCP Support

Native — MCP listed as a first-class tool type alongside function tools and hosted tools. Any MCP server plugs directly into the agent's tool layer.

## Sandbox Agent Pattern

Notable: agents in containers can inspect files, execute commands, apply patches, maintain workspace state across extended horizons. Mirrors Claude Code's agentic loop but as an explicit primitive rather than emergent behavior.

## Relevance to Jason's Work

- **ENGRAM contrast**: OpenAI SDK externalizes session/memory management; ENGRAM internalizes it via SOUL/HEARTBEAT. Different philosophies — worth watching if ENGRAM goes open-source and needs to speak to OpenAI users.
- **MCP compatibility**: Any MCP server Jason builds (memory-mcp, fabric-mcp, deadlines-mcp) works here too — provider-agnostic validation path.
- **bi-agent pattern**: The handoff + specialization model matches the NL→DAX→validation pipeline Jason has in bi_agent.py.
- **Tracing built-in**: Their observability story is ahead of current ClaudesCorner setup — worth borrowing patterns for tool_audit.jsonl improvement.
