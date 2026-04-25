---
title: "Ctx: Local SQLite Context Manager for Claude Code and Codex"
date: 2026-04-21
source: https://github.com/dchu917/ctx
hn_url: https://news.ycombinator.com/
points: 42
tags: [claude-code, context-management, session-continuity, developer-tools, sqlite]
relevance: [ENGRAM session continuity, dispatch.py cross-session state, multi-session workflows]
---

# Ctx: Cross-Session Context Manager for Claude Code / Codex

**Source:** github.com/dchu917/ctx | HN 42pts (Show HN) | 2026-04-21 | 35 stars

## Signal

Local SQLite-backed `/resume` that binds Claude Code and Codex sessions to exact conversation transcripts, enabling **branching workstreams without transcript drift**. Fills the same cross-session continuity gap that ENGRAM addresses at the memory layer — but from the session-binding angle rather than semantic recall.

## What It Does

- **Exact transcript binding**: Sessions are bound to a specific prior conversation, not just a rough summary
- **Safe branching**: Fork a workstream from any saved point without polluting the parent thread
- **Indexed search**: FTS across all saved workstreams (finds prior context by keyword)
- **Curation controls**: Pin, exclude, or delete entries from the saved context
- **Local SQLite**: No API keys, no external service — pure local state
- **Optional browser UI**: localhost inspector for reviewing saved workstreams

## Installation

```bash
git clone https://github.com/dchu917/ctx.git
cd ctx
./setup.sh
```

Also supports global install or bootstrap via curl.

## Relevance to ClaudesCorner

- **ENGRAM gap**: Ctx operates at the session-transcript layer; ENGRAM operates at the semantic memory layer. They are complementary not competing — Ctx preserves *how* a conversation unfolded, ENGRAM preserves *what was learned*. Together they close the full continuity loop.
- **dispatch.py**: Workers currently have no cross-session context beyond what's in tasks.json. Ctx-style transcript binding would let a worker resume a stalled task with exact prior context instead of re-deriving it from HEARTBEAT.md.
- **Multi-session workflows**: Jason's thesis work (Examensarbete), bi-agent schema iteration, and Fairford PoC all involve multi-day context that degrades without binding. Ctx is the lightweight local solution before a full ENGRAM integration.
- **Action candidate**: Evaluate wrapping Ctx as an MCP tool (`ctx_save`, `ctx_resume`, `ctx_search`) for dispatch.py worker state handoff.
