---
title: "Hermes Agent v0.11.0 — Interface Release"
date: 2026-04-25
source: https://github.com/NousResearch/hermes-agent/releases
tags: [hermes, agent, mcp, engram, dispatch, multi-provider, bedrock]
signal: high
---

# Hermes Agent v0.11.0 — "The Interface Release" (April 23, 2026)

**Repo:** github.com/NousResearch/hermes-agent — 117k stars (+15k since last clip), MIT

## What Changed

### Complete TUI Rewrite
React/Ink frontend with Python JSON-RPC backend. Sticky composer, live streaming output. The previous terminal interface is replaced wholesale.

### Pluggable Transport Architecture
Five new inference paths added in v0.11.0:
- **NVIDIA NIM** — local/hosted GPU inference
- **Arcee AI** — specialized fine-tuned models
- **Step Plan** — multi-step reasoning backend
- **Google Gemini CLI OAuth** — no API key required
- **Vercel ai-gateway** — unified provider proxy

Plus existing: Anthropic, ChatCompletions, Responses API, **AWS Bedrock** (confirmed production transport).

### `/steer` Mid-Run Course Correction
New command lets you interrupt a running agent and redirect it without killing the session. This is the missing primitive for dispatch.py — currently workers run to completion or timeout; `/steer` equivalent would allow operator intervention on long-horizon tasks without restarting.

### Orchestrator Roles + File Coordination
"Smarter delegation with orchestrator roles and file coordination" — agents can be designated as orchestrators that assign work to sub-agents and coordinate shared file access. Structural parallel to dispatch.py's coordinator/worker split.

### Expanded Plugin Surface
- Slash commands
- Tool dispatch hooks
- Execution blocking (deny: equivalent)
- Result transformation middleware
- Dashboard plugin with live theme switching + i18n

### QQBot (17th messaging platform)
QR scan setup. Joins Telegram, Discord, Slack, WhatsApp, Signal, and 11 others.

### GPT-5.5 via Codex OAuth
Live model discovery via Codex backdoor API — no OpenAI API key required for GPT-5.5 access through Hermes.

## Scale
~1,556 commits and 761 merged PRs between v0.9.0 and v0.11.0. Essentially a different product from what was clipped in April 2026.

## Relevance to ClaudesCorner

| Hermes Feature | ClaudesCorner Parallel | Action |
|---|---|---|
| Pluggable transport (Bedrock/NIM/Gemini) | dispatch.py single-provider | Multi-provider fallback routing |
| `/steer` mid-run correction | No equivalent | Operator interrupt hook for tier 2/3 workers |
| Orchestrator roles | dispatch.py coordinator concept | Formalize coordinator SOUL.md for dispatch workers |
| Execution blocking | `deny:` frontmatter | Already implemented |
| FTS5 session search | memory-mcp semantic search | Already differentiated |

**ENGRAM positioning holds:** Hermes is now richer as a standalone agent but still no persistent markdown-as-codebase artifact pattern (SOUL.md/HEARTBEAT.md). The semantic memory-mcp search is differentiated vs Hermes FTS5 file-based store.

**Immediate backlog:** `/steer`-equivalent interrupt hook for dispatch.py workers running tier 2+ tasks — currently the only intervention is `tasks.json` queue manipulation.
