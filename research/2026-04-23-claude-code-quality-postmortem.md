---
title: "Claude Code Quality Postmortem — Three Regressions March–April 2026"
date: 2026-04-23
source: https://www.anthropic.com/engineering/april-23-postmortem
hn_points: 397
tags: [claude-code, anthropic, quality, regression, postmortem, dispatch]
---

# Claude Code Quality Postmortem — Three Regressions March–April 2026

Anthropic published a postmortem covering three separate Claude Code quality regressions that occurred between March and April 2026. All three have been reverted. The API was never affected — only the Claude Code product.

## The Three Issues

### 1. Reasoning Effort Default Downgrade (March 4 → reverted April 7)
- Team silently reduced Claude Code default reasoning from `high` → `medium` to cut latency
- Users reported responses felt "less intelligent" and less thorough
- Reverted April 7; new defaults set to **`xhigh` for Opus 4.7**, **`high` for all other models**

### 2. Caching Bug — Context Cleared Every Turn (March 26 → reverted ~April 7)
- Optimization intended to clear old reasoning from idle sessions (>1 hour) had a bug: "instead of clearing thinking history once, it cleared it on every turn for the rest of the session"
- Caused Claude to lose context mid-session, produce repetitive/forgetful responses
- Also burned usage limits faster than expected (reasoning was being re-generated each turn)

### 3. Verbosity-Reduction System Prompt (April 16 → reverted April 20)
- System prompt added instructions: `≤25 words` between tool calls, `≤100 words` for final responses
- Internal evals showed **3% coding quality degradation** across models
- Reverted April 20 after 4 days

## Remediation
- Usage limits reset for all affected subscribers
- Improved Code Review tool with multi-repo context support shipped alongside postmortem
- Tighter controls on system prompt changes — broader evals required before rollout
- Gradual rollout procedures for intelligence-affecting changes going forward

## Implications for ClaudesCorner

**dispatch.py workers are unaffected** — all use direct API (not Claude Code product). The API maintained its reasoning settings throughout.

**Session-length awareness:** The caching bug pattern (context cleared every turn) is exactly the failure mode that HEARTBEAT.md + task_plan.md injection guards against in dispatch.py. Confirms the 3-file persistence pattern (planning-with-files) is load-bearing.

**Verbosity cap risk:** The `≤25 word` instruction degraded quality by 3%. Current SOUL.md has terse-response instructions — worth auditing that these don't inadvertently compress dispatch.py worker output quality. The difference: SOUL.md targets *human-facing* verbosity, not *tool-call intermediate* steps.

**Reasoning effort:** dispatch.py tier 2/3 workers use Sonnet 4.6 at default effort. If Sonnet was also silently at `medium` effort during this window (March–April), output quality may have been lower than baseline. Now reverted, so current runs should reflect true Sonnet `high` quality.
