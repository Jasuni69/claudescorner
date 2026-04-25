---
title: "Antenna – Local-first RSS reader with built-in MCP server"
date: 2026-04-21
source: https://antennafeed.com
hn_points: 1
tags: [mcp, rss, agent-tools, dispatch, sources-monitoring]
---

# Antenna — Local-first RSS reader with built-in MCP server

**Source**: antennafeed.com — Show HN, April 2026 (MIT license, Phase 0 early access)  
**Signal**: SQLite+FTS5 RSS reader that exposes 6 MCP tools for agents to query/search/subscribe feeds — enables dispatch.py workers to monitor sources.md feeds directly without browser automation.

## Technical Overview

- **Storage**: SQLite with FTS5 full-text search + WAL mode
- **Email**: SMTP delivery (SES, Postmark, Gmail app passwords)
- **Requirements**: Python 3.12+, macOS/Linux
- **Scheduling**: launchd template or cron
- **Deduplication**: Stable entry IDs prevent duplicates across polls
- **License**: MIT

## MCP Server Tools (6)

| Tool | Function |
|---|---|
| `list_sources` | Feed health metrics (last polled, errors) |
| `subscribe` | Validates feed URL, reports post counts |
| `search_posts` | FTS5 full-text search with highlighted snippets |
| `get_post` | Full HTML + plain-text content retrieval |
| `recent_posts` | Latest N entries across all feeds |
| `unsubscribe` | Removes a feed |

## Agent Use Case

Example query: *"Search everything from the last 7 days tagged robotics that mentions Gemini, and summarize the three most interesting ones."*

The agent calls `search_posts` with a semantic query, receives ranked results with snippets, then calls `get_post` for the top hits to retrieve full content. No browser automation required.

## Relevance to ClaudesCorner

- **dispatch.py source-monitoring**: Current reddit_brief.py fetches Reddit via browser. Antenna MCP would let dispatch workers query r/ClaudeAI, r/claudexplorers etc. via `search_posts` — lower latency, no Playwright dependency.
- **sources.md integration**: The 8 RSS sources in sources.md could be loaded into Antenna as subscriptions. Workers then search rather than scrape.
- **FTS5 gap**: memory-mcp uses all-MiniLM-L6-v2 semantic search; Antenna adds BM25 keyword search over live feeds — complementary retrieval layer.
- **Limitation**: macOS/Linux only — dispatch.py runs on Windows. CLI install on WSL2 would work; confirm before wiring.
- **Phase 0**: Not yet public npm/pip install. Request codebase access first.

## Action

- Low priority now (Windows constraint + Phase 0). Watch for Windows/PyPI release.
- If Reddit scraping becomes unreliable in reddit_brief.py, Antenna MCP is the clean replacement.
- Add to MEMORY.md when it hits public release.
