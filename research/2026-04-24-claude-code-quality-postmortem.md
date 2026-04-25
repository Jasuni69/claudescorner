---
title: "Anthropic Claude Code Quality Postmortem — 3 Bugs (Mar–Apr 2026)"
source: https://www.anthropic.com/engineering/april-23-postmortem
date: 2026-04-24
tags: [claude-code, anthropic, agentic, dispatch, postmortem, cache, reasoning]
hn_points: 489
hn_comments: 366
signal: high
---

# Anthropic Claude Code Quality Postmortem

Three bugs shipped between March 4 and April 20 degraded Claude Code output quality. All affected Sonnet 4.6 and Opus 4.6. All now fixed as of v2.1.116.

## Bug 1 — Reasoning Effort Silently Downgraded
- **Window:** March 4 → April 7
- Default reasoning effort changed from `high` to `medium` to reduce UI freeze on long thinking chains
- Users reported Claude felt "less intelligent"; reverted after complaints
- **Impact for dispatch.py:** Tier 2/3 workers running Sonnet 4.6 during this window may have produced lower-quality plans/code

## Bug 2 — Thinking Cache Cleared Every Turn (Critical for Agentic Use)
- **Window:** March 26 → April 10 (v2.1.101)
- Efficiency feature to clear cached reasoning after 1hr idle had a flaw: `clear_thinking_20251015` API header with `keep:1` parameter cleared thinking history on **every turn**, not just once after idle timeout
- Result: Claude appeared forgetful/repetitive in multi-turn sessions; each turn triggered a cache miss = accelerated token burn
- Bug survived code review, unit tests, and e2e tests; masked by an unrelated server-side messaging experiment
- **Impact for dispatch.py:** Long-running Sonnet 4.6 worker sessions (>1hr) during this window burned tokens at 2-3× expected rate and produced repetitive/forgetful outputs — explains any anomalous session logs from late March/early April

## Bug 3 — Verbosity Cap Harmed Code Quality
- **Window:** April 16 → April 20 (v2.1.116)
- System prompt: "keep text between tool calls to ≤25 words. Keep final responses to ≤100 words"
- Caused 3% regression on coding evals for Opus 4.6 and Opus 4.7
- **Impact:** bi-agent and dispatch.py workers running Opus 4.7 during this window may have produced truncated DAX explanations or incomplete code blocks

## Action Items
- Verify dispatch.py workers run Claude Code ≥ v2.1.116
- Review any session logs from March 26–April 10 for anomalous token consumption or repetitive outputs; those sessions are suspect
- The `clear_thinking` cache bug is the most dangerous pattern for autonomous long-horizon sessions — add session-length monitoring as a proxy signal
