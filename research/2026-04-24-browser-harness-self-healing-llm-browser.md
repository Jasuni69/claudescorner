---
title: "Browser Harness — Self-Healing LLM Browser Automation (browser-use)"
date: 2026-04-24
source: https://github.com/browser-use/browser-harness
hn_score: 11
stars: 6200
license: MIT
tags: [browser-automation, llm-agents, dispatch-py, chrome-devtools, mcp]
category: Agent Tooling
---

# Browser Harness — Self-Healing LLM Browser Automation

**Source:** https://github.com/browser-use/browser-harness
**HN:** Show HN, 11pts (2026-04-24, fresh)
**Stars:** 6.2k | **Forks:** 553 | **License:** MIT

## What It Is

Browser Harness is a minimal (~592 lines of Python) self-healing LLM browser automation framework from the browser-use team. Core premise: "The agent writes what's missing, mid-task."

Architecture:
- **run.py** (~36 lines): Executes plain Python with helpers preloaded
- **helpers.py** (~195 lines): Starting tool calls that agents can edit mid-execution
- **admin.py + daemon.py** (~361 lines): CDP WebSocket bridge and daemon bootstrap

Connects directly to Chrome via Chrome DevTools Protocol (CDP) — "one websocket to Chrome, nothing between." No framework overhead, no DOM scraping abstraction layer.

## Key Differentiator

Unlike browser-use (which provides a framework with predefined recipes), browser-harness lets the agent *write the missing helper code itself during the task* when it encounters something unexpected. This is genuine self-healing rather than fallback retry logic.

## Integrations

- **Claude Code / Codex:** Primary setup target; setup prompt directs to Claude Code
- **Remote browsers:** cloud.browser-use.com free tier (3 concurrent browsers, proxy support, captcha solving)
- **CDP-direct:** No Playwright/Selenium abstraction — raw Chrome DevTools Protocol

## Signal for ClaudesCorner

**dispatch.py browser worker primitive.** Browser Harness is the thinnest viable browser automation layer for a dispatch.py worker:
- 592 lines total — auditable, no hidden state
- Self-healing means the worker can recover from dynamic pages without re-prompting the coordinator
- CDP-direct avoids the Playwright dependency chain that breaks on Windows path issues
- Same team as browser-use = maintained and MCP-integration likely upcoming

Compare with:
- **AI Subroutines** (clipped 2026-04-18): record-once/replay-N, zero tokens, but requires pre-recording
- **Chrome DevTools MCP** (clipped 2026-04-18): 29 tools, heavier, requires npx
- Browser Harness sits between: live execution, minimal footprint, agent-written recovery

**Action:** Evaluate as dispatch.py browser worker; pair with CrabTrap (outbound proxy) for safe external browsing.
