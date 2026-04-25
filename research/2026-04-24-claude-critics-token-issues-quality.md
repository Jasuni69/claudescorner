---
title: "Why I Cancelled Claude: Token Issues, Declining Quality, Poor Support (HN 170pts)"
date: 2026-04-24
source: https://nickyreinert.de/en/2026/2026-04-24-claude-critics/
hn_score: 170
tags: [claude-code, token-cost, quality-regression, dispatch-py, sonnet-vs-opus]
category: Anthropic Signal
---

# Why I Cancelled Claude: Token Issues, Declining Quality, Poor Support

**Source:** https://nickyreinert.de/en/2026/2026-04-24-claude-critics/
**HN:** 170pts (2026-04-24)

## Key Complaints

**Token management anomalies:**
- Sudden 100% token usage spike after two small Haiku queries (unexplained)
- Cache expiration forced re-reading entire codebases — paying for the same context twice
- "Monthly usage limit" warning appeared despite being within hourly and weekly limits
- Weekly reset window shifted unexpectedly from current day to Monday

**Quality regression:**
- Claude Opus proposed lazy workarounds instead of proper refactoring
- One lazy Opus implementation consumed ~50% of the five-hour token allowance in a single task
- Compared unfavorably to GitHub Copilot and locally-run Qwen3.5-9B on same tasks

**Support:**
- Template response that didn't address the specific issue
- Ticket closed without resolution

## Alternatives Switched To

GitHub Copilot, OpenAI Codex, locally-run Qwen3.5-9B via Continue.

## Signal for ClaudesCorner

**Calibration input for dispatch.py architecture and cost model.**

1. **Token spike on Haiku confirms unpredictability.** The 100% spike after two small queries is consistent with the thinking-cache bug (Mar26–Apr10, fixed v2.1.116) — but if similar spikes recur, dispatch.py needs a per-run token budget hard cap, not just a cost estimate.

2. **Cache expiration forcing codebase re-reads = exact problem cache_control=ephemeral solves.** The author was using interactive Claude; dispatch.py workers with explicit cache_control avoid this. This validates the bi-agent caching architecture.

3. **Opus lazy workarounds = why dispatch.py defaults to Sonnet 4.6.** The author saw Opus producing low-effort solutions that burned tokens. Sonnet 4.6 on narrow, well-specified tasks outperforms Opus on cost-adjusted quality — this is the dispatch.py tier rationale.

4. **"Monthly usage limit" confusion** may be the Claude Code Pro removal A/B test (clipped 2026-04-22) — 2% of new signups saw this. Not a general platform reliability issue.

5. **Qwen3.5-9B as local fallback** — author found it viable for some tasks. Validates dispatch.py Haiku-tier fallback strategy if Anthropic rate limits tighten (also validated by Kimi K2.6 and DeepSeek V4 Pro).

**Verdict:** Not a signal to change the platform, but confirms: (a) Sonnet 4.6 default over Opus is correct, (b) explicit cache_control is load-bearing not optional, (c) token budget caps should be added to dispatch.py workers.
