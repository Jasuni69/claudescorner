---
title: "Microsoft Teams SDK — Bring Your Own Agent"
source: https://microsoft.github.io/teams-sdk/blog/bring-your-agent-to-teams/
date: 2026-04-23
tags: [microsoft, teams, agents, azure, mcp, fairford]
signal: high
---

# Microsoft Teams SDK — Bring Your Own Agent

**Source:** https://microsoft.github.io/teams-sdk/blog/bring-your-agent-to-teams/
**HN:** 4 pts (newest, 2026-04-23)

## What It Is

The Microsoft Teams SDK introduces an HTTP adapter pattern that integrates any existing agent into Microsoft Teams without rewriting code. The SDK wraps an existing Express/FastAPI server and injects a standard `POST /api/messages` endpoint — Teams' messaging interface — while leaving the original server untouched.

## Technical Approach

- **Protocol:** HTTPS + standard HTTP POST to `/api/messages`
- **Integration scenarios:** Slack Bolt apps sharing an Express server, LangChain chains forwarded through message handlers, Azure AI Foundry agents via `AIProjectClient` SDK
- **Security:** SDK verifies every incoming request is legitimately from Teams before invoking handler
- **Deployment:** Requires public HTTPS URL (Dev Tunnels or ngrok), CLI-based bot registration generating client credentials, app manifest sideload into Teams

## Key Capabilities

- Zero code rewrite of existing agent — adapter pattern only
- Multi-platform agents (Slack, LangChain, Azure Foundry) → Teams in one registration
- Typing indicators, message handling out of the box
- Lightweight SDK; existing infrastructure handles the logic

## Limitations / Gaps

- **No MCP support** mentioned — purely HTTP/REST
- No native OAuth integration described
- No mention of Fabric, Claude, or Anthropic
- Requires public HTTPS URL for bot registration (ngrok friction in local dev)

## Signal for ClaudesCorner

**fabric-mcp → Teams integration path:** The adapter pattern means any HTTP-speaking agent (including fabric-mcp endpoints) can be surfaced inside Teams with a thin wrapper. This is the Fairford enterprise deployment story — Fabric data agent reachable from Teams without a custom Teams app build.

**Azure AI Foundry first-class:** `AIProjectClient` is the exact SDK used in Fairford's Azure backbone. The Teams SDK already knows how to speak to it, closing the Teams↔Fabric loop without MCP.

**MCP gap = opportunity:** The SDK supports LangChain and Azure Foundry but not MCP. A `teams-sdk-mcp` adapter that bridges MCP tool calls to the `POST /api/messages` pattern would make any MCP server Teams-native — backlog candidate.
