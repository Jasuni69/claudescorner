---
title: "Libretto — Deterministic Browser Automation for Coding Agents"
source: https://github.com/saffron-health/libretto
date: 2026-04-16
tags: [agent-tools, browser-automation, mcp, claude-code, infrastructure]
relevance: high
---

## Summary

Libretto is a browser automation toolkit designed specifically for coding agents (Claude, GPT, etc.). It wraps Playwright with agent-optimized features: minimal context overhead, network traffic capture for API reverse-engineering, action recording/replay, and session persistence.

## Why It Matters

Most browser automation tools are built for humans or test suites. Libretto is explicitly designed for the agent as the operator — it reduces the context cost of page inspection by delegating visual analysis to an external LLM call rather than dumping full page content into the agent context. This directly addresses the "context explosion" problem in long-horizon web tasks.

## Key Features

- **Live browser** (headless/headed) with Playwright backend
- **Network traffic logging** — lets agents understand site APIs rather than UI-scraping
- **Action recording + replay** — reproducible workflows, useful for skill-like patterns
- **Session persistence** — saves authenticated state (cookies, localStorage) between runs
- **Multi-model support** — OpenAI, Anthropic, Google, Vertex for snapshot analysis
- **CLI-first** — token-efficient interface; designed to slot into agent tool calls

## Applicability to Jason's Work

- **ClaudesCorner agents**: Could replace ad-hoc WebFetch calls for sites that require JS rendering or auth
- **MCP integration**: The action recording pattern maps well to MCP tool definitions — record once, replay as a tool
- **Obsidian clipping**: Current obsidian-web-clipper skill uses desktop automation; Libretto could be a more reliable alternative for authenticated sites

## Open Questions

- Does Libretto expose an MCP-compatible interface or require custom wrapping?
- Performance overhead vs raw Playwright for simple read-only tasks?

## Source Context

Appeared on Hacker News front page 2026-04-16 as "Show HN: Libretto – Making AI browser automations deterministic" with 93 points.
