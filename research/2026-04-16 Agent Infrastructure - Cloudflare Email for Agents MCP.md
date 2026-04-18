---
title: "Cloudflare Email Service for Agents — Public Beta"
date: 2026-04-16
source: https://blog.cloudflare.com/email-for-agents/
tags: [cloudflare, agents, mcp, infrastructure, email]
type: research-clip
---

# Cloudflare Email Service for Agents

**HN:** 256 pts / 110 comments — entered public beta 2026-04-16

## What It Is

Purpose-built email infrastructure for AI agents. Bidirectional: agents can send and receive email natively via Cloudflare Workers. Bundles sending, routing, and an `onEmail` hook into the Agents SDK.

## How It Works

- **Sending**: Workers binding (no API key management) or REST API — SDKs in TypeScript, Python, Go
- **Receiving**: `onEmail` hook — agents process inbound mail and reply asynchronously
- **Address routing**: sub-addressing routes `support@domain.com` to specific agent instances
- **Auth**: HMAC-SHA256 signing prevents forged routing headers
- **State**: Durable Objects for persistent state across email sessions
- **Auto-configured**: SPF, DKIM, DMARC handled automatically

## MCP Integration

Ships with an **MCP server** for agent integration + open-source skills for coding agents. Also includes an "Agentic Inbox" reference app template.

## Use Cases Mentioned

- Customer support agents
- Invoice processing agents
- Multi-agent workflows with email handoffs

## Pricing

Email Routing: free (existing). Email Sending: public beta — pricing TBD.

## Relevance

Directly extends Claude Code agent capabilities to email I/O without custom infrastructure. MCP server means this could be wired into ClaudesCorner dispatch workflows or Clementine (Fairford) reporting agents. Durable Objects + persistent state = good fit for long-running agentic tasks that need async human-in-the-loop via email.
