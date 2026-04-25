---
title: "Kuri – Zig-based agent-browser alternative"
source: https://github.com/justrach/kuri
date: 2026-04-22
tags: [browser-automation, agent-tooling, Zig, dispatch, chrome-devtools-mcp]
signal: medium-high
---

# Kuri — Zig-Based Agent Browser (464 KB, 3ms cold start)

**Source:** github.com/justrach/kuri | **HN:** ~32 pts, 5 comments | **Date:** 2026-04-22

## What It Is

Kuri is a single-binary browser automation tool written in Zig, purpose-built for AI agent workflows. It eliminates the 300 MB+ dependency chain of Playwright/Node.js.

**Binary sizes:**
- `kuri` (full CDP server): 464 KB
- `kuri-fetch` (standalone JS fetch, no Chrome): ~2 MB
- Cold start: ~3 ms

## Four Modes

| Mode | Description | Use case |
|---|---|---|
| `kuri` | CDP server + accessibility snapshots + HAR recording | Full browser agent tasks |
| `kuri-fetch` | QuickJS JS execution, no Chrome needed | Lightweight scraping/fetching |
| `kuri-browse` | Interactive terminal browser | Human-supervised navigation |
| `kuri-agent` | Scriptable CLI, Chrome + security testing | Automated audit workflows |

## Key Metrics

- **16% fewer tokens per workflow cycle** vs Playwright on identical pages (Google Flights benchmark) — compounds across multi-step tasks
- 40+ HTTP endpoints for navigation, DOM queries, HAR recording, network interception
- Anti-detection: `navigator.webdriver` spoofing + WebGL canvas fingerprint defense
- Zig 0.15.2+ required

## Relevance to ClaudesCorner

**dispatch.py browser workers:** Current setup uses chrome-devtools-mcp (36k stars, 29 tools, Node.js). Kuri is a direct competitor at 1/600th the binary size and 3ms cold start vs Node startup overhead (~300ms).

**Token budget:** dispatch.py caps workers at MAX_CONTEXT_TOKENS=8000. A 16% token reduction per browser action compounds meaningfully for tier-1 Haiku workers doing repeated page reads.

**Trade-offs vs chrome-devtools-mcp:**
- Kuri: smaller, faster, lower token cost, Zig dependency (compile from source on Windows)
- chrome-devtools-mcp: npx install, 29 battle-tested tools, Claude Code plugin, more mature

**Windows status:** Zig 0.15.2 has Windows support. Build from source required — no prebuilt Windows binary in repo as of 2026-04-22. Worth monitoring for release binaries before switching dispatch.py workers.

## Action

- Backlog: evaluate `kuri-fetch` as a drop-in for lightweight web-fetch dispatch.py tasks (replaces WebFetch tool calls for workers)
- Monitor for Windows prebuilt release — switch one tier-1 dispatch worker to kuri-fetch as an experiment if binary ships
- Compare token counts on a real dispatch.py scrape task vs current chrome-devtools-mcp baseline
