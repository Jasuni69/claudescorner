---
title: "Chrome DevTools MCP — Official Browser Automation MCP Server (29 tools)"
date: 2026-04-18
source: https://github.com/ChromeDevTools/chrome-devtools-mcp
stars: 36052
stars_today: +438
tags: [mcp, browser-automation, chrome, devtools, agent-tools]
signal: high
---

# Chrome DevTools MCP — Official Browser Automation MCP Server

**Repo:** ChromeDevTools/chrome-devtools-mcp · 36k stars · +438 today · TypeScript

Official Chrome DevTools MCP server — Chrome itself ships this. Gives agents direct browser control + debugging.

## 29 Tools Across 6 Categories

| Category | Tools |
|---|---|
| Input | click, drag, fill, fill_form, handle_dialog, hover, press_key, type_text, upload_file |
| Navigation | close_page, list_pages, navigate_page, new_page, select_page, wait_for |
| Emulation | emulate, resize_page |
| Performance | trace recording, memory snapshots, insights analysis, (4 total) |
| Network | request inspection, listing |
| Debugging | screenshot, snapshot, console messages, Lighthouse audits, script eval |

Slim mode: 3-tool subset for basic tasks.

## Usage

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

Requires Node.js v20.19+. Chrome auto-starts on first tool call.

## Claude Code Integration

Installs as both MCP server AND skills plugin. Provides expert guidance alongside tools — not just raw automation.

## Relevance to ClaudesCorner

- **dispatch.py workers:** Drop-in browser tool layer. Workers doing web research or UI scraping get 29 reliable tools vs ad-hoc WebFetch.
- **windows-mcp complement:** windows-mcp handles OS-level PowerShell/events; chrome-devtools-mcp handles browser layer. Together = full desktop automation stack.
- **fabric-mcp / Fairford:** Could automate Power BI browser interactions (report export, embedded dashboards) that don't have REST API coverage.
- **Action:** Wire into `~/.claude/settings.json` mcpServers — `npx` install, zero config.
