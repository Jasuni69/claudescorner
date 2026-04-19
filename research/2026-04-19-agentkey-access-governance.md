---
title: "AgentKey — Access governance for AI agents"
date: 2026-04-19
source: https://agentkey.dev
hn_points: 2
tags: [ai-agents, security, access-governance, mcp, credentials, audit]
relevance: high
---

# AgentKey — Centralized Credential & Access Governance for AI Agents

**Show HN** — submitted ~1hr ago, 2 pts.

## What it is

AgentKey is an access governance platform that manages credentials for AI agents centrally. Agents register a single identity, request tool access, and humans approve/deny via a unified inbox. Approved agents fetch credentials on demand — secrets never get hardcoded.

## How it works

1. **Agent registers** — single identity per agent
2. **Agent requests** — declares which tools/APIs it needs (or suggests missing ones)
3. **Human approves** — unified inbox, multi-person approval via Clerk orgs
4. **Agent fetches** — credentials served on demand, AES-256-GCM encrypted

## Key features

- One-click revocation (immediate effect)
- Full append-only audit log
- Slack/Discord webhook notifications
- **Self-growing catalog**: agents that request unavailable tools trigger a suggestion flow; once approved, all requestors get access automatically
- Company-specific "usage guides" (API URLs, conventions) loaded per agent on demand
- Works with any HTTP-capable agent framework — no SDK required

## Deployment

- Free, no credit card — vendor-pays SaaS model long-term
- Self-hostable on Vercel (Neon + Upstash + Clerk)
- Compatible with Claude Code, OpenAI SDK, LangChain, etc.

## Why it matters for Jason

- dispatch.py workers currently have no credential governance — AgentKey fills this gap without adding SDK complexity
- Self-growing catalog pattern mirrors skill-manager-mcp's skill discovery: agents declare what they need, not what exists
- Audit trail + revocation = missing primitive in current ClaudesCorner infra stack
- Complements AgentRQ (human-in-loop escalation) — AgentRQ handles task escalation, AgentKey handles access escalation
- Self-hostable → no secrets leaving local infra

## Signal

Freshly submitted (HN newest). Technically solid and directly relevant to dispatch.py worker security posture.
