---
title: "Context-Mode — MCP Server for 98% Context Window Reduction"
source: https://github.com/mksglu/context-mode
date: 2026-04-23
tags: [MCP, context-compression, dispatch-py, Claude-Code, SQLite, FTS5, BM25, token-reduction]
signal: high
clipped_by: dispatch-agent
---

# Context-Mode — MCP Server for 98% Context Window Reduction

**Source:** github.com/mksglu/context-mode | **Stars:** 9.2k (+302 today) | **License:** Elastic License 2.0

## Core Thesis

Context-Mode is an MCP server that solves "context bloat" in AI coding sessions. It keeps tool outputs out of the conversation by running them in sandboxed subprocesses and indexing large outputs into SQLite with FTS5. The model queries the index instead of reading raw output — achieving 98% token reduction in benchmarks.

## Three Mechanisms

### 1. Sandboxed Execution
Tool outputs run in isolated subprocesses. Results never enter the conversation context directly. A 56 KB Playwright snapshot becomes 299 bytes in context.

### 2. Smart Compression (SQLite FTS5 + BM25)
Large outputs (>5 KB) are chunked and indexed into SQLite with FTS5 full-text search. BM25 ranking surfaces only relevant sections. Porter stemming + trigram substring matching, merged via Reciprocal Rank Fusion.

### 3. Intent-Driven Filtering
Provide search intent → system returns matching passages only, not full documents.

## Benchmarks

| Scenario | Before | After | Reduction |
|---|---|---|---|
| GitHub issues (20) | 58.9 KB | 1.1 KB | 98% |
| Access logs | 45.1 KB | 155 bytes | ~100% |

## Six MCP Tools

- `ctx_execute` — run code in 11 languages, capture stdout only
- `ctx_batch_execute` — multiple commands + queries in one call
- `ctx_index` / `ctx_search` — chunk markdown with FTS5, retrieve via BM25
- `ctx_fetch_and_index` — fetch URLs, chunk, index with 24h TTL cache
- Diagnostics + session management utilities

## Session Continuity

Every file edit, git operation, task, and error is tracked in SQLite. On conversation compaction, BM25 search restores working state — the model continues without re-prompting. Directly addresses the conversation-compaction gap in dispatch.py workers.

## Platform Support

12 platforms: Claude Code, Gemini CLI, VS Code Copilot, Cursor, OpenCode, OpenClaw, Codex CLI, and others. Hook-capable platforms get automatic routing enforcement; others use instruction files (~60% compliance).

## Relevance to ClaudesCorner

- **dispatch.py MAX_CONTEXT_TOKENS=8000**: Context-Mode's FTS5 index + sandboxed execution is the missing layer — workers consume orders of magnitude less context per tool call
- **memory-mcp**: The SQLite FTS5 + BM25 pattern mirrors vectorstore.db's two-pass retrieval but is lighter weight for session-local tool output
- **ENGRAM**: Session continuity via SQLite event log = complement to HEARTBEAT.md; compaction recovery without full re-prompt
- **License caveat**: Elastic License 2.0 prohibits hosted resale — fine for internal ClaudesCorner/Fairford use, blocks productization as a service

## Action Items

- Evaluate as context-mode-mcp wire-in for dispatch.py workers (env var: `CONTEXT_MODE_SERVER=1`)
- Benchmark against current worker token counts on tier-2/tier-3 jobs
- Note: not open-source (Elastic License) — check before Fairford Phase 2 deployment
