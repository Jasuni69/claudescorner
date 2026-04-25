---
title: "CC-Canary: Claude Code Session Drift Detection via Local Log Analysis"
date: 2026-04-24
source: https://github.com/delta-hq/cc-canary
hn_url: https://news.ycombinator.com/item?id=43796xxx
hn_pts: 4
tags: [claude-code, agentic, monitoring, quality, dispatch]
relevance: high
---

# CC-Canary — Claude Code Drift Detection

**Repo**: delta-hq/cc-canary | MIT | Python | 0.x pre-alpha

## What It Does

Detects Claude Code quality regressions over time by analyzing `~/.claude/projects/*.jsonl` session logs locally. Zero network, no account, no telemetry, no background daemon. Produces verdict + report (Markdown or dark-theme HTML dashboard).

## How It Works

Six-step pipeline:
1. Scans local JSONL session logs
2. Deduplicates assistant messages by ID
3. Aggregates per-session metrics
4. Computes composite health score per day; finds inflection points via argmax(delta) with 0.75σ floor; falls back to median-timestamp split if no clear break
5. Pre-renders skeleton report with data tables
6. Claude fills narrative gaps during skill invocation (local files only, prompts truncated to 180 chars)

## Metrics Tracked

| Metric | What It Measures |
|---|---|
| Read:Edit ratio | Investigation thoroughness before editing |
| Write share of mutations | Rewrites vs. surgical edits |
| Reasoning loops per 1K tool calls | Self-correction frequency |
| Thinking redaction rate | Visible vs. redacted reasoning |
| Mean thinking length | Reasoning depth proxy |
| API turns per user message | Call volume per prompt |
| Tokens per user message | Token burn per prompt |

Plus appendices: premature stops, self-admitted errors, hour-of-day patterns, word-frequency shifts, per-turn behavior rates.

## Installation

```bash
npx skills add delta-hq/cc-canary
```

Then from Claude Code:
```
/cc-canary 60d          # Markdown report
/cc-canary-html 30d     # HTML dashboard (auto-opens)
```

Window: `7d / 14d / 30d / 60d / 90d / 180d` (default 60d).

## Output

Verdict: `HOLDING / SUSPECTED REGRESSION / CONFIRMED REGRESSION / INCONCLUSIVE`
Includes: headline metrics with color-coded bands, weekly cost/ratio/token trends, cross-version comparisons, detected inflection dates.

## Signal for ClaudesCorner

**dispatch.py blind spot filled**: long autonomous sessions accumulate quality drift invisibly. CC-Canary quantifies it from logs already on disk.

- The Mar26–Apr10 thinking-cache bug (Anthropic postmortem) would show as a spike in "API turns per user message" and token burn — retrospective validation possible by running `/cc-canary 90d` against existing logs.
- Read:Edit ratio is a direct proxy for over-editing (the Levenshtein benchmark issue from 2026-04-22 research).
- Works on Windows via Python; HTML auto-open falls back gracefully on WSL/Windows.
- Backlog: wire `/cc-canary 30d` as a weekly dispatch.py worker health check; compare pre/post v2.1.116 inflection.
