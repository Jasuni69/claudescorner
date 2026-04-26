---
title: "WUPHF — Multi-Agent Collaborative Office with Shared Wiki and MCP Tool Scoping"
date: 2026-04-25
source: https://github.com/nex-crm/wuphf
hn_url: https://news.ycombinator.com/item?id=show_hn_wuphf
hn_pts: 8
tags: [agents, mcp, engram, memory, dispatch, claude-code, wiki]
type: research-clip
---

# WUPHF — Multi-Agent Collaborative Office with Shared Wiki

**Source:** github.com/nex-crm/wuphf (94 stars, MIT, ~75% Go / 14.7% TypeScript)
**Via:** Show HN — 2026-04-25

## What It Is

WUPHF is an open-source multi-agent collaborative office built on Claude Code. Agents (Claude, Codex, OpenClaw) share a unified workspace with two-tier memory: per-agent private notebooks and a shared team wiki. The CLI launches a local web interface at `localhost:7891`.

## Architecture

**Memory tiers:**
- **Notebooks** — per-agent, scoped, private working memory
- **Wiki** — workspace-wide shared knowledge, updated by any agent
- **Promotion flow** — notebook entries graduate to wiki status (direct parallel: ENGRAM daily-log → memory-mcp durable write)

**Three wiki backends:**
- `markdown` (default) — git-native, stored at `~/.wuphf/wiki/`, file-over-app
- `Nex` — knowledge graph backend
- `GBrain` — vector search backend

**MCP tool scoping:**
- DM mode: 4 tools (minimal surface)
- Full office: 27 tools (complete collaborative stack)
- Tools include `team_wiki_read`, `team_wiki_write`, `wuphf_wiki_lookup`

**Agent roles:**
- CEO agent: Claude Sonnet (upgradeable to Opus via `--opus-ceo`)
- External bridges: Telegram, OpenClaw integrations

## Performance & Cost

- 97% cache hit rate across turns via Anthropic prompt caching
- ~87k input tokens per turn; ~40k billable after caching
- 10-turn session: ~286k total tokens
- Push-driven notifications (not polling) → zero idle burn

## Signal for Jason's Work

**ENGRAM parallel:** WUPHF independently ships the notebook→wiki promotion flow that ENGRAM's daily-log→memory-mcp pattern implements. Key validation: the two-tier private/shared memory split is the right abstraction — not a single flat store.

**dispatch.py:** The MCP tool scoping (4 vs 27 tools) is a production implementation of deferred-load at the agent role level. DM workers needing 4 tools ≠ full office workers needing 27 = CPU/token cost savings match dispatch.py Haiku/Sonnet tier logic.

**ENGRAM bootstrap:** The `markdown` (git-native) backend with `~/.wuphf/wiki/` storage is directly comparable to ClaudesCorner's `memory/YYYY-MM-DD.md` pattern. WUPHF proves git-native markdown wiki is production-viable at 165 releases.

**Action:** Evaluate WUPHF's promotion-flow logic for memory-mcp write-gate upgrade. The `team_wiki_write` tool interface is a reference implementation for ENGRAM's durable write authority model.
