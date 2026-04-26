---
title: "Recent Claude Code Quality Reports — Harness Bugs Not Model Drift"
source: https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/
author: Simon Willison
date: 2026-04-24
clipped: 2026-04-26
tags: [claude-code, dispatch, harness, telemetry, cc-canary, long-sessions]
relevance: dispatch.py long-session workers, cc-canary health check, per-session telemetry
---

# Recent Claude Code Quality Reports — Harness Bugs Not Model Drift

**Source:** simonwillison.net, Apr 24 2026

## Core Finding

Two months of perceived Claude Code quality degradation (Mar–Apr 2026) were caused by **three harness-layer bugs**, not model regression. Anthropic's postmortem confirmed the complaints were legitimate. Fixed in v2.1.116.

## The Critical Bug (Most Relevant)

March 26 change intended to clear older thinking from **idle sessions (>1 hour)** to reduce latency. Bug: the clear happened **every turn for the rest of the session**, not just once after idle. Effect: Claude appeared forgetful and repetitive — users saw context amnesia mid-session.

## Willison's Personal Angle (Not in Official Postmortem)

Willison explicitly notes he spends **more time in stale sessions than fresh ones** — multi-day sessions are his default workflow. This means he was among the most affected users. His insight: **harness-level bugs are deeply complex** even without model non-determinism, and performance complaints always warrant infrastructure investigation before assuming model drift.

## Why This Matters for dispatch.py

- **dispatch.py long-session workers** running tier-2/3 tasks (potentially hours) were in the exact session-length window most exposed to this bug (Mar26–Apr10).
- Any anomalous token burn in dispatch logs from that window is worth reviewing retroactively.
- **cc-canary** (`thinking_redaction` metric, 7-headline-metric scanner) is the correct instrument for catching this class of regression — run weekly `/cc-canary 30d` as a health check pre/post any Claude Code version bump.
- **Per-session telemetry** is the only way to distinguish harness bugs from model drift — silence (no metrics) looks identical to "still running correctly."

## Architectural Takeaway

Harness bugs are indistinguishable from model drift without per-session observability. The fix is:
1. Pin Claude Code version in dispatch.py worker invocations (detect upgrade-triggered regressions)
2. Wire `thinking_redaction` + `Read:Edit ratio` metrics from cc-canary as a weekly automated health check
3. Flag sessions with anomalous token burn for manual review before attributing to "model degraded"
