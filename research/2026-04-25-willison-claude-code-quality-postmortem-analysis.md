---
title: "Willison on Claude Code Quality Postmortem — Harness Bugs Hit Long Sessions Hardest"
date: 2026-04-25
source: https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/
tags: [claude-code, dispatch, reliability, session-management, postmortem]
relevance: high
---

# Willison on Claude Code Quality Postmortem

**Source:** simonwillison.net, April 24 2026
**Signal:** Thinking-cache bug (Mar26–Apr10) cleared context every turn for the rest of the session — dispatch.py long-session workers were the most affected class. Fixed in v2.1.116.

## Summary

Simon Willison's analysis of Anthropic's postmortem on two months of Claude Code quality complaints. The root cause was three separate infrastructure bugs, not model degradation:

1. **Reasoning downgraded** (Mar 4 – Apr 7): Claude's reasoning was silently set to `medium` effort instead of intended level.
2. **Thinking cache cleared every turn** (Mar 26 – Apr 10, most dangerous): A fix meant to clear stale thinking once after >1hr idle instead ran on every turn for the rest of the session — making Claude appear forgetful and repetitive throughout any extended session.
3. **Verbosity cap regression** (Apr 16 – Apr 20): Caused a 3% coding regression.

## Willison's Key Observation

> "On March 26, we shipped a change to clear Claude's older thinking from sessions that had been idle for over an hour, to reduce latency when users resumed those sessions. A bug caused this to keep happening every turn for the rest of the session instead of just once, which made Claude seem forgetful and repetitive."

Willison notes this bug hit his workflow hardest because he frequently maintains extended sessions over hours or days. He currently runs 11 such long-lived sessions and spends more time in "stale" sessions than new ones.

## Implications for dispatch.py

- **Dispatch long-session workers were the most exposed** during Mar26–Apr10. Any worker that ran a multi-turn session (tier 2/3 tasks) would have had thinking wiped every turn.
- **Retrospective audit possible**: Review dispatch logs from that window for anomalous token burn, unexpected repetition, or re-asking already-answered questions.
- **Fix is in v2.1.116** — verify Claude Code version before scheduling long-horizon dispatch runs.
- **Harness-level bugs are invisible without per-session telemetry** — cc-canary's `thinking_redaction` metric directly surfaces this class of failure.

## Broader Lesson

Willison emphasizes that developers building agentic harnesses should study this postmortem carefully. Infrastructure bugs that interact with LLM behavior are uniquely hard to diagnose because they look identical to model quality drift. The combination of LLM unpredictability + harness bugs creates a compounding diagnostic challenge.

**Action:** Add `thinking_redaction` spike detection to dispatch.py session health check. Wire cc-canary as a weekly pre-dispatch validation step.
