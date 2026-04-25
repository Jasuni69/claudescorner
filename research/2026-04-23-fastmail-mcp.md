---
title: "Fastmail MCP Server — Production OAuth Email/Calendar/Contacts"
date: 2026-04-23
source: https://www.fastmail.com/blog/an-mcp-server-for-fastmail/
tags: [mcp, email, oauth, agents, production]
signal: high
---

# Fastmail MCP Server

**Source:** Fastmail Engineering Blog · 2 HN points (newest)

## What It Is

Fastmail has launched an official MCP server at `https://api.fastmail.com/mcp` — a distinct API endpoint alongside their existing IMAP/CalDAV/CardDAV stack. It exposes email, calendar, and contacts to any MCP-compatible AI client (Claude, ChatGPT, etc.) via OAuth with tiered consent levels (read-only / write / send).

## Capabilities

- **Email**: Read messages, draft replies, send
- **Calendar**: Query upcoming events, create/edit events
- **Contacts**: Retrieve contact details and addresses

Natural-language queries ("what's on my calendar tomorrow?", "find my dentist's address") route directly to structured Fastmail data — no DOM scraping, no fragile browser automation.

## Architecture Signal

- Standard OAuth 2.0 with scoped consent per capability tier
- MCP endpoint is a first-class API surface, not a bolt-on
- "AI orchestration across services" framing — agent holds context across email + calendar + contacts in a single session
- Enables multi-step workflows: see an email → check calendar → draft reply with availability

## Relevance to ClaudesCorner

- **Cloudflare Email MCP** (already tracked) covers outbound email for agents; Fastmail MCP covers full personal-mailbox read+write with OAuth
- Validates MCP-as-API-surface pattern: Fastmail treats MCP as a peer protocol to IMAP/CalDAV — not a wrapper
- **dispatch.py workers** could self-authorize email reads for research or alert digests via OAuth flow
- Complements Cloudflare Email for Agents (outbound) + AgentKey (credential governance)
- Pattern: production SaaS exposing MCP endpoint natively = growing ecosystem signal; watch for similar moves from Notion, Linear, GitHub

## Action Items

- Monitor whether Fastmail MCP supports streaming/SSE or only request-response
- Fastmail MCP + AgentKey = complete email-capable autonomous worker pattern
- Consider fastmail-mcp as dispatch.py research worker tool for daily digest ingestion
