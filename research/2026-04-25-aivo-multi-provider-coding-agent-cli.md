---
title: "Aivo — Unified Multi-Provider Coding Agent CLI with Cross-Agent MCP Sessions"
date: 2026-04-25
source: https://getaivo.dev/
hn_points: 2
tags: [agents, MCP, dispatch, multi-provider, claude-code]
relevance: high
---

# Aivo — Unified Multi-Provider Coding Agent CLI with Cross-Agent MCP Sessions

**Source:** https://getaivo.dev/ (GitHub: yuanchuan/aivo)
**HN:** 2pts (newest, 2026-04-25 — pre-viral)
**License:** Open source

## What It Is

Aivo is a unified CLI that "translates between provider protocols, so any model works in your coding agent." It abstracts provider differences and lets you run Claude Code, Codex, Gemini CLI, OpenCode, and Pi interchangeably — or switch mid-session.

## Key Capabilities

- **Cross-agent shared sessions via MCP**: agents can read each other's mid-conversation work by name (e.g., `--as reviewer`). One agent writes, another reads and critiques — zero API overhead.
- **Multi-provider failover**: OpenAI, Anthropic, Google, OpenRouter, DeepSeek, MiniMax, Kimi, Groq, and local (Ollama/LM Studio). Free tier via built-in provider with no keys required.
- **Local SQLite logging**: all sessions stored locally with queryable stats and token counts. No telemetry, no prompt proxying.
- **OpenAI-compatible API server**: serves all providers through one endpoint with automatic failover.
- **Encrypted local key storage**: AES credentials, zero exfiltration.

## Architecture

```
aivo CLI → provider translation layer → Claude Code / Codex / Gemini CLI / OpenCode
                                     ↓
                              MCP interface (shared sessions)
                                     ↓
                              SQLite log (token stats)
```

## Signal for ClaudesCorner

**dispatch.py multi-provider fallback**: Aivo's provider translation layer is the cleanest public implementation of the pattern dispatch.py approximates manually. The `--as reviewer` cross-agent session sharing via MCP is the missing cross-worker context handoff primitive — workers currently pass artifacts via files, not live session state.

**Cost reduction path**: Built-in free provider + OpenRouter routing means Haiku-tier workers could route through Aivo for zero-cost reads when Anthropic rate limits hit, with automatic fallback.

**Token audit**: SQLite-per-session log matches the cc-canary pattern for drift detection — queryable token burn per agent run.

## Gaps / Caveats

- 2 HN points = very early signal, production maturity unknown
- Cross-agent session sharing security model unclear (shared session = shared context = potential injection surface)
- No benchmark data comparing provider routing quality
- K2VV ToolCall verification required before routing Fairford work through any non-Anthropic provider

## Action Items

- Benchmark Aivo's provider translation vs direct API calls for latency overhead
- Evaluate `--as reviewer` pattern as dispatch.py cross-worker review loop primitive
- Wire SQLite log output as alternative token burn source for token-dashboard
