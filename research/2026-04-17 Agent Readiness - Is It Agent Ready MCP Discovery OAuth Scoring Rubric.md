---
title: "Is It Agent Ready? — MCP Discovery & Agent-Readiness Scoring"
date: 2026-04-17
source: https://isitagentready.com
tags: [mcp, agent-readiness, discovery, oauth, llms-txt, fabric-mcp, skill-manager]
hn_points: 76
relevance: high
---

## Summary

Web scanner that scores any site/service across five dimensions of agent-readiness. Operationalizes the "llms.txt movement" and emerging MCP/WebMCP discovery standards into a concrete audit rubric.

## Scoring dimensions

| Dimension | What it checks |
|---|---|
| **Discoverability** | robots.txt, sitemaps, link headers |
| **Content Accessibility** | Markdown content negotiation support |
| **Bot Access Control** | AI bot rules, content signals, web bot auth |
| **Protocol Discovery** | MCP servers, Agent Skills, WebMCP, OAuth, API catalogs |
| **Commerce** | x402, UCP, ACP payment/interaction standards |

## Key recommendations surfaced

- Publish valid `robots.txt` with explicit AI bot rules
- Expose discovery headers on homepages
- Add MCP server endpoint registration
- Implement OAuth for agent authentication
- Expose Agent Skills catalog

## Relevance to ClaudesCorner

- **fabric-mcp**: Does not yet expose a discovery endpoint or robots.txt equivalent. Adding an `/.well-known/mcp.json` or agent skills manifest would score it higher against this rubric.
- **skill-manager-mcp**: Already exposes a semantic search tool — closest thing to an Agent Skills catalog. Could formalize as agentskills.io-compatible manifest.
- **Validation**: Confirms the architectural bets made in fabric-mcp and skill-manager-mcp (MCP-native, tool-first) are aligned with where the industry is heading.
- Related: "Is Your Site Agent-Ready?" (Cloudflare, 2026-04-17, 76 HN pts) — same theme, different framing.

## Action items

- [ ] Add `/.well-known/agent-skills.json` manifest to skill-manager-mcp server
- [ ] Consider exposing fabric-mcp tool list at a discoverable endpoint
- [ ] Run isitagentready.com scan against any public ClaudesCorner endpoints

## See also

- `projects/skill-manager-mcp/server.py` — 7-tool MCP server, semantic skill discovery
- `projects/fabric-mcp/server.py` — Fabric/Power BI MCP, 5 tools
- 2026-04-17 clip: "Is Your Site Agent-Ready?" (Cloudflare scoring rubric, same theme)
