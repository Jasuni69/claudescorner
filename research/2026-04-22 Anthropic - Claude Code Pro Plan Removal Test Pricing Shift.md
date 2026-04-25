---
title: "Anthropic Tests Removing Claude Code from Pro Plan"
source: https://www.theregister.com/2026/04/22/anthropic_removes_claude_code_pro/
date: 2026-04-22
tags: [anthropic, claude-code, pricing, dispatch, operational-risk]
signal: high
---

# Anthropic Tests Removing Claude Code from Pro Plan

**Source:** The Register | HN 229pts | 2026-04-22

## What Is Changing

Anthropic is running a limited A/B test (affecting ~2% of new signups) that removes Claude Code from the **Pro plan** ($20/month). Under the test, Claude Code access would require upgrading to **Max**.

## Why

- Engagement per subscriber "way up" since Max launched ~1 year ago
- Pro plan pricing significantly undervalues actual token consumption — sometimes **by a factor of 10×**
- Claude Code heavy users drive disproportionate infrastructure cost at the $20 price point
- Existing Pro and Max subscribers are **not** affected by the current test

## Key Quote

> "Usage has changed a lot and our current plans weren't built for this." — Anthropic Head of Growth

## Relevance to ClaudesCorner

- **dispatch.py headless workers**: currently rely on `claude -p` CLI or API keys; Pro plan tier change does not affect API-key-based dispatch workers — they bill per-token regardless
- **Operational risk**: if Jason's account is on Pro and Claude Code moves to Max-only, interactive sessions cost more; API key workers are unaffected
- **Pricing signal**: the 10× underpricing acknowledgment confirms Anthropic will raise Pro prices or restructure plans — model for all downstream cost projections
- **Max plan** ($100/month or usage-based) may become the minimum for serious Claude Code usage; factor into Fairford PoC cost model
- Validates dispatch.py Haiku-tier leaf nodes: preserving Claude Code access for human-interactive sessions while routing routine automated work to cheaper tiers is now a cost-governance decision, not just a latency one

## Action Items

- Verify Jason's current plan tier; if Pro, watch for forced upgrade notification
- Update Fairford PoC cost model: assume Max-tier pricing ($100/month + usage) for interactive Claude Code sessions
- dispatch.py workers are API-key billed and unaffected — no changes needed there
- Keep an eye on this HN thread for community responses and workarounds
