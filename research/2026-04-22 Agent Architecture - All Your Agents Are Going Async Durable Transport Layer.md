---
title: "All Your Agents Are Going Async"
source: https://zknill.io/posts/all-your-agents-are-going-async/
date: 2026-04-22
tags: [agent-architecture, async, transport, dispatch, MCP]
signal: high
---

# All Your Agents Are Going Async

**Source:** zknill.io | **HN:** ~36 pts, 22 comments | **Date:** 2026-04-22

## Core Insight

Agent lifetimes no longer align with human connection lifetimes. HTTP request-response is fundamentally the wrong transport primitive for agents that:

- Fire from cron jobs (no waiting caller)
- Run multi-step tasks outlasting any connection
- Need to push results to users unprompted
- Span multiple devices or multiple collaborating humans

The author frames this as a **transport mismatch** — the industry has solved durable *state* (session storage, Anthropic + Cloudflare both do this) but has not yet solved durable *transport* (delivery of results to the right human, on the right device, when they're ready).

## Architectural Split

Two distinct layers must be decoupled:

| Layer | What it covers | Current solutions |
|---|---|---|
| Durable State | Conversation history, agent inference | Anthropic Sessions, Cloudflare Durable Objects |
| Durable Transport | Bidirectional push, multi-device continuity, orphan-result delivery | **Gap** — currently patched via external chat platforms |

## The OpenClaw Model

OpenClaw sidesteps this by using external chat platforms (WhatsApp, Discord, Slack) as the transport layer — the agent's output delivery is delegated to platforms that already have durable, push-capable channels. This works but couples agent output format to platform constraints.

## Concrete Recommendations from Author

- Adopt realtime messaging protocols (WebSockets, SSE with reconnect) over HTTP polling
- Treat **session** as a first-class infrastructure primitive, not an application detail
- Support multi-device and multi-user continuity natively at the transport layer
- Build transport layer independently from state management

## Relevance to ClaudesCorner

**dispatch.py gap confirmed:** Workers fire via cron (scheduled task every 2h) and results go to log files — no push delivery to Jason. If a tier-3 Opus job runs overnight, there's no notification. This is the durable-transport gap in concrete form.

**Tesseron (clipped 2026-04-22)** is a partial answer for browser workers — its WebSocket bridge keeps agent↔app communication alive. But dispatch.py itself needs an async result-delivery channel.

**Multica's WebSocket streaming** (clipped 2026-04-20e) is the most directly applicable pattern: workers stream progress over WebSocket rather than writing to log files silently.

## Action

- Backlog: dispatch.py v2 — add async result notification (push to file-watcher or WebSocket endpoint) for tier 2/3 jobs
- Near-term workaround: dispatch.py `--notify` flag that appends to HEARTBEAT.md on job completion — zero infrastructure, still async
