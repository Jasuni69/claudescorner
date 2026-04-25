---
title: "Preflight – Test your MCP server before submitting to Claude/OpenAI"
source: https://m8ven.ai/preflight
date: 2026-04-23
tags: [MCP, testing, skill-manager-mcp, memory-mcp, compliance]
hn_points: 4
---

## Summary

Preflight (M8ven) is a 15-second MCP server validator that runs 6 checks before official directory submission to Claude or OpenAI — cutting the 30-day review cycle down to immediate feedback.

**Six checks:**
1. **OAuth 2.1 + PKCE** — dynamic client registration, auto-approval flows, token exchange, refresh
2. **CORS Headers** — cross-origin requests from Claude and OpenAI connectors
3. **MCP Protocol** — initialize, tools/list, tools/call via Streamable HTTP
4. **Domain Verification** — OpenAI `.well-known/openai-apps-challenge` file
5. **Token Refresh** — access tokens renew without re-authentication
6. **Anonymous Fallback** — server works without auth (required for direct connection; OAuth required for directory listing)

**Submission workflow:** Submit HTTPS endpoint → run checks → fix failures → submit for official review (2–4 weeks for OpenAI, shorter for Claude).

## Relevance to ClaudesCorner

**skill-manager-mcp / memory-mcp:** Both servers are locally wired in settings.json but have never been validated for public listing compliance. Before any external ENGRAM distribution, Preflight is the correct first gate — especially the OAuth 2.1 + PKCE and Anonymous Fallback checks, since neither server currently implements OAuth.

**ENGRAM distribution:** The `/.well-known/agent-skills.json` endpoint identified in the AI Traffic research (2026-04-20) should be validated by Preflight before any ENGRAM bootstrap README points to it.

**Action:** Run Preflight against memory-mcp and skill-manager-mcp before ENGRAM v1 public release. Add OAuth 2.1 scaffolding to both servers as a pre-release milestone. Anonymous fallback mode should remain functional for local ClaudesCorner use regardless.
