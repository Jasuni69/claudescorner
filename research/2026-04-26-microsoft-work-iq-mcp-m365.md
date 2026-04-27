---
title: "Microsoft Work IQ — Official M365 MCP Server"
source: https://github.com/microsoft/work-iq
author: Microsoft
date: 2026-04-26
clipped: 2026-04-26
stars: 763
forks: 72
license: EULA (proprietary)
tags: [mcp, microsoft, m365, teams, outlook, fabric, fairford, claude-code]
---

## Summary

Official Microsoft MCP plugin collection for GitHub Copilot (and any MCP-compatible client) that exposes Microsoft 365 data — email, meetings, documents, Teams channels, org charts — via natural language queries.

## What It Does

Three plugins under the `work-iq` umbrella:

| Plugin | Capability |
|--------|-----------|
| `workiq` | NL queries against M365 data (email, calendar, OneDrive, Teams, People) |
| `microsoft-365-agents-toolkit` | Scaffold declarative M365 Copilot agents |
| `workiq-productivity` | Read-only analytics: email triage, meeting cost, org chart, channel audit |

## Auth & Installation

- Node.js 18+ + NPM/NPX
- Install via `/plugin install` in any MCP-compatible client, or run as standalone MCP server
- First access triggers **tenant admin consent** (Entra ID) — M365 permissions required
- Works on Windows/Linux/macOS

## Relevance to ClaudesCorner

- **fabric-mcp complement**: fabric-mcp covers Power BI/Lakehouse data; Work IQ covers the M365 collaboration layer (who sent what, which meeting cost how much, what's in that Teams channel) — together they form a complete Microsoft enterprise data access stack
- **Fairford Phase 2**: client-facing M365 data (Outlook threads, Teams decisions, OneDrive reports) as agent context alongside Fabric KPIs; Work IQ + fabric-mcp = full Fairford data layer
- **dispatch.py research workers**: Work IQ could give research workers access to internal org context (decisions in Teams, email threads about a metric) without custom integration
- **ENGRAM**: SOUL.md + Work IQ = agent with identity AND access to the organization's knowledge layer

## Caveats

- **License**: Proprietary EULA, not open-source — check terms before Fairford production use
- **Tenant admin consent required** — not self-service; needs IT buy-in at Numberskills/Fairford
- **Public preview** — 46 open issues; treat as beta
- **GitHub Copilot-first** framing, but MCP-native = works with Claude Code via `.mcp.json`

## Action Items

- Test Work IQ as standalone MCP server against a dev M365 tenant before Fairford Phase 2
- Wire alongside fabric-mcp in a combined Fairford context skill: `get_deal_context` = Work IQ email thread + Fabric KPI
- Review EULA for data residency clauses before Fairford production use
