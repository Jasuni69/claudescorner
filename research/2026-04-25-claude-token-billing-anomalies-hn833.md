---
title: "I Cancelled Claude: Token Issues, Declining Quality, Poor Support (HN 833pts)"
date: 2026-04-25
source: https://nickyreinert.de/en/2026/2026-04-24-claude-critics/
hn: https://news.ycombinator.com/item?id=43793212
points: 833
comments: 492
tags: [claude, tokens, billing, dispatch, cost-model]
---

## Summary

Developer cancels Claude subscription after documented billing anomalies, quality regression, and inadequate support. High-signal post (833 HN pts, 492 comments) because it surfaces undocumented rate-limit behavior directly affecting dispatch.py cost assumptions.

## Key Findings

### Token Anomalies (Undocumented)
- **Monthly limit exists but is undocumented**: A monthly usage cap warning appeared despite being within hourly and weekly stated limits. Official documentation makes no mention of monthly limits.
- **Cache cleared on forced break**: When Claude forces a break, the conversation cache is cleared — meaning users pay tokens twice to reload the same codebase context after a break. This contradicts the documented token-economics of caching.
- **Window shift**: The weekly token window silently shifted from "today" to Monday — a behavioral change with no announcement.
- **Two questions → 100% spike**: After a 10-hour break (ample refresh time), two simple Haiku questions caused usage to hit 100%.

### Quality Regression
- Opus generated a workaround script (auto-injection) instead of directly editing JSX components — a symptom of lazy generation consuming ~50% of the 5-hour token allowance on unnecessary indirection.
- Author has baseline via GitHub Copilot, OpenAI Codex, and local inference tools — not a novice comparison.

### Support Failure
- AI bot gave generic responses; human follow-up pasted documentation and closed the ticket with "further replies may not be monitored."

## Relevance to ClaudesCorner

| Area | Impact |
|------|--------|
| **dispatch.py cost model** | Undocumented monthly limits mean per-session token budgets can hit a hidden ceiling; long-running dispatch weeks may silently degrade |
| **Cache-clear-on-break** | dispatch.py workers that pause mid-session lose cache state; cost doubles on resume — affects tier 2/3 jobs with forced breaks |
| **Window shift (Mon reset)** | Token availability calculations in HEARTBEAT.md may be off if window resets Monday not rolling 7d |
| **Sonnet 4.6 default** | Opus lazy-workaround pattern confirms Sonnet 4.6 as correct default for cost+quality; Opus for planning only |

## Action Items (Backlog)

- Add `monthly_limit_warning` check to health-check `checks.py`
- Document cache-invalidation-on-break behavior in HEARTBEAT session startup notes
- Verify token window reset cadence (rolling vs Monday) against actual dispatch session logs
