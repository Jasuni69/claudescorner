---
title: "Is Your Site Agent-Ready? — Cloudflare's Agent Accessibility Checker"
date: 2026-04-17
source: https://isitagentready.com
hn_score: 27
tags: [mcp, agents, infrastructure, cloudflare, web-standards, discovery]
relevance: high
---

# Is Your Site Agent-Ready? — Cloudflare

Cloudflare launched a diagnostic tool that scans any website and scores it across five "agent-readiness" dimensions. The framing is significant: as AI agents become primary web consumers, sites need to be discoverable, parseable, and transactable by machines — not just humans.

## What It Checks

**Discoverability & Content**
- Valid `robots.txt` with AI bot rules
- Sitemap presence
- Markdown content negotiation (agents prefer structured text over HTML)

**Bot Access Control**
- Explicit AI bot allow/deny rules
- Web bot authentication mechanisms

**Protocol Support**
- MCP server presence at well-known paths
- **Agent Skills** (standardized capability exposure — same concept as `agentskills.io`)
- **WebMCP** — browser-accessible MCP for web contexts
- OAuth discovery + OAuth Protected Resources (RFC 9728)
- API catalogs

**Commerce Protocols**
- x402, UCP, ACP — payment/transaction standards for autonomous agents

## Why This Matters

This is the `llms.txt` movement operationalized into a scoring rubric. The implicit claim: within 12–18 months, "is your service agent-accessible?" will be a standard infra question alongside "do you have an API?" and "do you have mobile support?"

The MCP layer is treated as table-stakes discovery — not optional tooling but the expected interface contract between a service and any agent ecosystem.

## Connections to ClaudesCorner

- **fabric-mcp** already exposes Fabric datasets as MCP tools — this validates the architectural bet
- **skill-manager-mcp** maps to "Agent Skills" standard (standardized capability exposure)
- **memory-mcp** + **markitdown-mcp** handle Markdown content negotiation for RAG pipelines
- ENGRAM's design (MCP-native memory layer) positions it well as agent-ready infrastructure

## Practical Takeaway

If Jason builds any public-facing services from ClaudesCorner work (Fabric dashboards, BI agent endpoints, ENGRAM as a service), checking agent-readiness at launch is now a one-URL test. OAuth discovery + MCP exposure are the two highest-leverage additions.
