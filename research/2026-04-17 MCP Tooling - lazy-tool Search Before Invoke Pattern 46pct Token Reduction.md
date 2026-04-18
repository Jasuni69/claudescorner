---
title: "lazy-tool: Search Before Invoke — 46% Token Reduction for MCP Agents"
date: 2026-04-17
source: https://github.com/rpgeeganage/lazy-tool
tags: [MCP, agents, tooling, token-efficiency, Claude-Code]
signal: high
clipped_by: claude-autonomous
---

## Summary

`lazy-tool` is a local-first MCP discovery runtime that solves prompt bloat from large MCP server inventories. Instead of dumping all tool schemas into every prompt, it exposes 5 meta-tools and uses a **search before invoke** pattern — agent queries what it needs, gets back only relevant tools, then calls them.

## The Problem

As MCP server count grows, all tool schemas accumulate in every prompt. Models mis-select tools, token costs rise, and latency increases. With 10+ MCP servers (as in ENGRAM/ClaudesCorner), this becomes a real tax.

## Architecture

Three modes:
- **Search mode** (default): Agent sees 5 meta-tools, discovers via semantic query
- **Direct mode**: All cataloged tools exposed as first-class MCP tools  
- **Hybrid**: Both available simultaneously

Maintains a local SQLite catalog (no vector DB, no Docker). Optional Ollama integration for local embeddings, or remote model fallback.

## Benchmarks (llama-3.1-8b-instant)

| Metric | Direct MCP | lazy-tool |
|--------|-----------|-----------|
| Input tokens | 1,701 | 915 (−46%) |
| Latency | 0.232s | 0.158s (−32%) |
| Tools in context | 47 | 5 |

## Setup

```bash
./lazy-tool import --write  # auto-discovers from Claude Desktop / Cursor / VS Code configs
./lazy-tool reindex         # indexes all tools locally
./lazy-tool serve           # runs as MCP endpoint
```

## Relevance to ClaudesCorner

Jason's setup has 10+ MCP servers (memory-mcp, skill-manager, windows-mcp, fabric-mcp, deadlines-mcp, Figma, Microsoft Learn, Obsidian, etc.). lazy-tool as a proxy layer would reduce per-request token overhead significantly.

**Mode guidance**: Search mode for Sonnet/Opus (strong reasoning). Direct mode for Haiku or local models.

Compared to alternatives:
- RAG-MCP: Python + vector DB (heavier)
- MetaMCP: Docker required
- AWS AgentCore Gateway: managed/cloud
- Claude Code built-in tool search: client-side, Claude-only

lazy-tool is the only local-first, single-binary, provider-agnostic option.

## Links

- GitHub: https://github.com/rpgeeganage/lazy-tool
- HN: 23 pts (Mar 31, 2026)
