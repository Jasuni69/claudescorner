---
title: "CodeBurn — AI Coding Token Cost Observer"
date: 2026-04-16
source: https://github.com/agentseal/codeburn
tags: [claude-code, token-cost, developer-tools, tui, observability]
relevance: high
---

# CodeBurn — Claude Code Token Usage Dashboard

## Summary

Terminal UI dashboard that reads Claude Code session files from disk (no API key needed) and shows token spend by task type, model, project, and success rate. Works with Claude Code, Codex, Cursor, OpenCode, Pi, and GitHub Copilot.

## How It Works

Reads local session files directly — Claude Code stores these on disk. Calculates costs via LiteLLM's pricing database (cached locally 24h). No proxy, no API key.

```bash
npm install -g codeburn
# or
npx codeburn
```

Requires Node.js 20+.

## Key Features

- **13 task categories:** coding, debugging, testing, refactoring, etc.
- **One-shot success rate:** tracks how often AI got it right first try vs. edit/test/fix cycles — useful signal for prompt quality and task scoping
- **Per-project / per-model / per-tool breakdown**
- **Multi-currency** with live exchange rates (Frankfurter)
- **macOS menu bar widget** via SwiftBar
- **CSV/JSON export**

## Limitations

- Cursor "Auto" mode hides actual model — costs estimated at Sonnet pricing
- GitHub Copilot: output tokens only
- First run on large Cursor databases: up to 1 min (SQLite parse), then cached

## Relevance to Jason's Stack

This directly addresses the `/token-cost` skill (which currently just lists project directories and asks which to analyze). CodeBurn is a more complete implementation of what that skill attempts.

**Options:**
1. **Replace** the token-cost skill with a wrapper that shells out to `npx codeburn`
2. **Steal the approach** — adapt the local session file parsing logic into a Python equivalent that integrates with ClaudesCorner's existing memory/reporting infrastructure
3. **Use as-is** to validate token spend patterns before building anything

The one-shot success rate metric is particularly interesting — it could feed into the self-improvement flywheel (feedback_flywheel.py) as a signal for which task types or prompts produce the most rework.

## HN Context

31 points on launch day — modest but targeted audience. Show HN post, early stage.
