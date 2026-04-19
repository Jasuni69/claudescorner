---
title: "claude-mem — Automatic Session Memory via Lifecycle Hooks + Agent SDK Compression"
date: 2026-04-18
source: https://github.com/thedotmack/claude-mem
stars: 62207
stars_today: +1024
tags: [memory, claude-code, agent-sdk, engram, hooks, session-continuity]
signal: high
---

# claude-mem — Automatic Session Memory via Lifecycle Hooks + Agent SDK Compression

**Repo:** thedotmack/claude-mem · 62k stars · +1024 today · TypeScript · AGPL-3.0

Claude Code plugin that auto-captures, compresses, and reinjects session context across coding sessions. No manual intervention.

## How It Works

### Capture (5 lifecycle hooks)
- `SessionStart`, `UserPromptSubmit`, `PostToolUse`, `Stop`, `SessionEnd`
- Records "tool usage observations" — what Claude did and learned each turn

### Compression (Agent SDK)
- Uses Anthropic Agent SDK to generate semantic summaries
- Raw observations → condensed summaries that preserve essential context
- Token-efficient: progressive disclosure (compact index → timeline → full details)

### Injection (next session)
- `mem-search` skill queries memory DB from current context
- 3-layer retrieval: compact index → timeline → full details
- Summaries injected into system prompt automatically

### Install
```bash
npx claude-mem install
```
Web viewer at `http://localhost:37777`. `<private>` tags exclude sensitive content.

## Relevance to ClaudesCorner

- **ENGRAM direct competitor/complement:** claude-mem is a working implementation of ENGRAM's core premise (automatic cross-session memory). ENGRAM is more opinionated about identity/soul layers; claude-mem is pure behavioral capture. Worth studying the hook + compression pattern.
- **memory-mcp:** Current memory-mcp requires manual `write_memory` calls. claude-mem's `PostToolUse` hook → auto-compress → store pattern is the upgrade path. Could wire `PostToolUse` in settings.json to call `write_memory` with AI-compressed summaries.
- **project_infra_hooks.md:** Already have PostToolUse writing to tool_audit.jsonl. claude-mem shows how to go one step further: compress + store semantically, not just log.
- **PostCompact hook:** claude-mem's `SessionEnd` compression maps to existing PostCompact hook. Opportunity to merge logic.
- **Gap vs ENGRAM:** AGPL-3.0 + PolyForm Noncommercial on ragtime/ directory means can't ship commercially without OSS compliance. ENGRAM stays MIT.
