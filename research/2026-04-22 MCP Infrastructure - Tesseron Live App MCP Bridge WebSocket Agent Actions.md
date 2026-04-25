---
title: "Tesseron — Live App MCP Bridge via WebSocket"
date: 2026-04-22
source: https://github.com/BrainBlend-AI/tesseron
tags: [mcp, agents, websocket, claude-code, infrastructure]
signal: high
---

# Tesseron — Live App MCP Bridge via WebSocket

**Stars:** 4 (v1.0.1, April 2026) | **License:** BSL 1.1 → Apache-2.0 after 4 years | **Protocol spec:** CC BY 4.0

## What It Does

Tesseron lets live applications (browser tabs, Node.js processes, desktop apps) expose typed actions that AI agents invoke as real MCP tools over WebSocket — no UI scraping, no DOM automation. Agents call validated functions against actual application state.

## Architecture

| Layer | Package | Role |
|---|---|---|
| Client SDKs | `@tesseron/web`, `@tesseron/server`, `@tesseron/react` | Browser / Node / React hooks |
| Protocol core | `@tesseron/core` | JSON-RPC 2.0 types + Zod-style action builder |
| MCP gateway | `@tesseron/mcp` | Bridges WebSocket connections → MCP clients |

**Handshake:** six-character claim code (no API keys) — "click-to-connect" pairing.

## Key Capabilities

- `ctx.confirm()` — agent prompts user for confirmation before acting
- `ctx.elicit()` — schema-validated prompts to gather structured input
- `ctx.sample()` — agent makes LLM sub-calls mid-action
- `ctx.progress()` — streaming progress updates to MCP client
- Subscribable resources for live data reads
- Bundled Claude Code plugin: one-command install

## Supported MCP Clients

Claude Code, Claude Desktop, Cursor, VS Code Copilot, and any MCP-compatible client.

## Relevance to ClaudesCorner

- **dispatch.py browser workers**: Tesseron replaces fragile DOM automation with typed, validated app-level MCP calls. If any web app in the Fairford PoC or ClaudesCorner stack exposes a Tesseron SDK, dispatch.py workers get real function access instead of scraping.
- **Complement to chrome-devtools-mcp**: DevTools MCP handles network/DOM inspection; Tesseron handles intentional app-level action exposure — different layers, not competing.
- **ENGRAM distribution**: Tesseron's `@tesseron/mcp` gateway pattern is a clean model for how memory-mcp could expose write actions to browser-side agents without requiring API keys.
- **fabric-mcp parallel**: Same pattern — wrap an existing API surface as typed MCP tools. Tesseron does it for live apps; fabric-mcp does it for Power BI/Fabric.

## Gaps / Watch Items

- BSL 1.1 license is not fully open; check before Fairford production use (Apache-2.0 conversion happens ~2030)
- 4 stars = very early; no community validation yet
- Windows WebSocket behavior should be tested before dispatch.py integration
- No persistent session resumption described — agents lose context on WebSocket drop

## Action

Low-priority backlog: evaluate `@tesseron/mcp` gateway as model for exposing skill-manager-mcp actions to browser-based agents. Revisit when stars > 500.
