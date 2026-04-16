---
source: https://old.reddit.com/r/openclaw/comments/1sm7igb/reduced_my_openclaw_costs_from_20_to_2_a_day/
clipped: 2026-04-16
tags: [cost-optimization, caching, observability, openclaw, api]
---

# Reduced OpenClaw costs from $20 to $2/day — still using Sonnet

**r/openclaw** | Practical cost reduction via API proxy + cache fix, no model downgrade.

## Problem
After Anthropic pricing change, costs spiked to $20/day on a financial bot (transaction sync, Telegram briefings, spend tracking). Root causes invisible without instrumentation.

## Fix
Built a proxy between OpenClaw and the API that logs every call. Discovered:
1. Most LLM calls were missing cache due to bad setup
2. Forgotten background tasks still running
3. Opportunities to route cheap tasks to cheaper models

**Result: 13¢ → 2¢ per call. No prompt changes, no model changes — just fixed cache setup.**

## Key insight
Cache misconfiguration is the silent cost killer. You can't see it without a proxy/logger in front of the API.

## Takeaway for ClaudesCorner
Worth auditing prompt_cache settings on any long-running agent loops. A logging proxy or even Claude Code's token cost tracking (`/token-cost`) can surface this.
