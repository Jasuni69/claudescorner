---
title: "Claude Code Rust — Native Rust TUI Replacing Node.js/React Ink"
date: 2026-04-19
source: github.com/srothgan/claude-code-rust
hn_score: 2
stars: 94
tags: [claude-code, rust, tui, performance, terminal, agent-sdk]
relevance: medium
---

## Summary

Drop-in Rust replacement for Claude Code's stock Node.js/React Ink TUI. Built on Ratatui + Tokio, communicates with Anthropic's official Agent SDK via a TypeScript bridge over stdio JSON. Full feature parity: tool calls, file editing, terminal commands, permission flows.

## Problem It Solves

The stock Node.js TUI suffers from:
- **Memory**: 200–400 MB baseline vs ~20–50 MB native binary
- **Startup**: 2–5 s vs <100 ms
- **Scrollback**: virtual scrolling drops history
- **Input lag**: event queue delays on keystroke handling
- **Copy/paste**: custom implementation breaks native terminal behaviour

## Architecture

```
Rust/Ratatui (presentation) → TypeScript Agent SDK bridge (stdio JSON) → Anthropic Agent SDK
```

Async event loop (Tokio) handles concurrent keyboard input and bridge events. Syntax-highlighted, virtual-scrolled chat history.

## Adoption

94 stars, 34 forks, 170 commits, 21 releases. Early but actively maintained.

## Relevance to ClaudesCorner

- dispatch.py sessions run Claude Code headlessly — the V8 OOM problem surfaces on long autonomous runs
- `--bare` flag sessions could benefit from reduced memory footprint in parallel workers
- Pattern: Agent SDK bridge via stdio JSON = same interface dispatch.py workers use; worth monitoring for headless mode support
- Not worth switching immediately (94 stars, bridge adds a layer), but flag if V8 OOM becomes a dispatch.py issue
