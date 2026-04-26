---
title: "Surf-CLI — Zero-Config CLI Browser Automation for AI Agents via Unix Socket + CDP"
date: 2026-04-25
source: https://github.com/nicobailon/surf-cli
stars: 453
license: MIT
tags: [browser-automation, claude-code, dispatch-py, MCP, CDP, agents, windows]
relevance: dispatch.py browser worker, chrome-devtools-mcp complement
---

# Surf-CLI — Browser Automation for AI Agents

**GitHub:** https://github.com/nicobailon/surf-cli  
**Stars:** 453 | **License:** MIT | **Version:** v2.7.2 (April 2026)  
**Language:** JavaScript/TypeScript (55.6% / 43.7%)

## What Is It

Surf is a CLI + socket-based browser automation tool designed specifically for AI agents. No API keys, no configuration required. Agents issue commands via CLI or Unix socket; Surf translates them to Chrome DevTools Protocol (CDP) operations or falls back to `chrome.scripting` API when CDP is unavailable.

**Pipeline:** `CLI (surf) → Unix Socket → Native Host → Chrome Extension → CDP/Scripting API`

## Key Capabilities

- **Navigation & reading:** page nav, accessibility tree extraction, semantic DOM queries
- **Interaction:** click, type, form select, scroll
- **Screenshots:** auto-capture with token-efficient resizing (default 1200px) — reduces token cost vs raw screenshots
- **Network monitoring:** automatic request logging with filtering and replay
- **Multi-browser:** Chrome, Brave, Edge, Arc, Helium, Chromium
- **Device emulation:** mobile profiles + custom viewports
- **Workflows:** multi-step deterministic automation sequences
- **AI query bridge:** access ChatGPT, Gemini, Perplexity, Grok, Google AI Studio using existing browser login credentials (no new auth)
- **Window isolation:** parallel agent operation without cross-contamination

## Agent Compatibility

Explicitly supports: Claude Code, GPT, Gemini, Cursor, custom agents, shell scripts — anything that can run commands. Both CLI and Socket API interfaces available.

## Platform Support

macOS (primary), Linux (experimental), Windows (experimental).

## Relevance to ClaudesCorner

**dispatch.py browser worker:** Lighter alternative to chrome-devtools-mcp (36k stars, 29 tools). Surf is CLI-first — dispatch.py workers can invoke `surf` as a shell command without MCP wiring. Zero config = lower bootstrap cost per worker.

**chrome-devtools-mcp vs Surf-CLI:** chrome-devtools-mcp is richer (29 tools, slim mode, npx install) and MCP-native. Surf is simpler for headless shell-based workers — better fit for dispatch.py BUILD/RESEARCH leaf nodes that need occasional page scraping without full MCP overhead.

**AI Subroutines complement:** Surf's workflow mode (multi-step deterministic sequences) maps directly to the AI Subroutines record-once/replay-N pattern (clipped 2026-04-18). Surf handles the execution layer; AI Subroutines handle the recording layer.

**Token cost management:** 1200px auto-resize on screenshots is a real token saver — relevant given Opus 4.7 3.01× image token inflation (Willison, clipped 2026-04-20).

## Action Items

- Backlog: evaluate Surf-CLI as dispatch.py RESEARCH worker browser primitive on Windows (experimental support — test before committing)
- Compare against chrome-devtools-mcp slim mode (3 tools) for dispatch.py use case: lower overhead vs richer protocol
- Window isolation feature = one Surf instance per dispatch.py worker without interference
