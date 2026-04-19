---
title: "AI Subroutines — Zero-Token Deterministic Browser Automation"
source: https://www.rtrvr.ai/blog/ai-subroutines-zero-token-deterministic-automation
date: 2026-04-18
tags: [agents, browser-automation, mcp, tools, deterministic]
relevance: dispatch.py browser layer, windows-mcp complement, chrome-devtools-mcp pairing
---

## Summary

AI Subroutines (rtrvr.ai) are reusable browser automation scripts that record once and replay deterministically — callable as agent tools with zero per-invocation token cost.

## How It Works

- Chrome extension captures network requests via two mechanisms: MAIN-world `fetch`/`XHR` patch (runs before page scripts) + Chrome `webRequest` API for CORS/service-worker paths
- Replay executes **inside the webpage** — cookies, CSRF tokens, signing, and fingerprinting propagate for free
- Request ranking trims dozens of captured requests to top 5 using weighted signals:
  - First-party origin (+20), telemetry hosts (-80)
  - Temporal correlation to DOM events (+28 within 800ms)
  - Mutating operations (+35), volatile IDs (-18, triggers DOM-only fallback)

## `rtrvr.*` Helper Namespace

Semantic DOM/network ops: `find()`, `click()`, `type()`, `waitFor()`, `request()`, `getCsrfToken()`  
Parameters bind as function arguments — no string concatenation, no template injection risk.  
`rtrvr.find()` walks open shadow roots.

## Key Properties

- **Zero token cost** at execution time — inference happens only at parameter-selection
- **Deterministic** — same input, same output
- **LLM-callable** — agent picks parameters per row; Subroutine runs at script speed
- Pre-built library: Instagram DMs, LinkedIn connections, X posts, etc.

## Shipping Alongside

- BYO ChatGPT/Claude OAuth
- WhatsApp `/run` and `/schedule` commands
- Knowledge Base + MCP upgrades
- **Rover** — agent-readable website structure with analytics

## ClaudesCorner Relevance

**Pattern signal**: Subroutines invert the standard agent loop — LLM stays in the parameter-selection layer, deterministic scripts handle execution. This is a cleaner architecture than keeping LLM in the action loop for repetitive browser tasks.

**dispatch.py**: Subroutines could serve as pre-built worker primitives for browser-based tasks — record once, dispatch N times with different params at zero inference cost.

**chrome-devtools-mcp** complement: chrome-devtools-mcp handles debugging/inspection; Subroutines handle recorded task replay. Complementary, not overlapping.

**windows-mcp**: Current windows-mcp uses PowerShell for automation. Subroutines cover the browser surface that windows-mcp can't reach natively.

## Repo

`github.com/rtrvr-ai`
