---
title: "GitHub Copilot Individual Plans: Agentic Workflows Force Pricing Restructure"
source: https://github.blog/changelog/2026-04-22-changes-to-github-copilot-individual-plans/
secondary_source: https://simonwillison.net/2026/Apr/22/changes-to-github-copilot/
date: 2026-04-22
tags: [github-copilot, agentic-workflows, pricing, token-limits, dispatch, infrastructure]
signal: high
---

# GitHub Copilot Individual Plans: Agentic Workflows Force Pricing Restructure

**Source:** GitHub Blog + Simon Willison | 2026-04-22

## What Changed

GitHub implemented three immediate changes to Copilot individual plans:

1. **Sign-up pause**: New registrations for Pro, Pro+, and Student plans suspended to protect existing customers.
2. **Tighter token limits**: Usage caps reduced; Pro+ now offers "5× the limits of Pro." Users who hit unexpected limits can cancel before May 20 for pro-rated refunds.
3. **Model restrictions**: Claude Opus 4.7 removed from Pro tier entirely — restricted to Pro+ ($39/month). Older Opus models (4.5, 4.6) being phased out of Pro+ as well.

## Root Cause

GitHub's own statement: **"Agentic workflows have fundamentally changed Copilot's compute demands."** Long-running parallelized sessions now "regularly consume far more resources than the original plan structure was built to support." A single agentic request can burn tokens that previously took dozens of sessions.

## Willison Analysis

- GitHub's per-request pricing model (not per-token) made it structurally vulnerable to agentic inflation.
- Token-based weekly caps are the emergency fix — not sustainable long-term.
- Announcement was unclear about which of 15+ Copilot-branded products are affected (CLI, cloud agents, code review, IDE).
- VS Code and CLI now show usage % warnings at 75% of weekly limit.

## Implications for ClaudesCorner

- **Validates direct API + dispatch.py architecture**: GitHub-mediated access to Claude is now a worse deal than direct Anthropic API — usage caps bite before billing does.
- **Sonnet 4.6 default confirmed correct**: Opus restricted to highest tier; Sonnet remains the right cost/performance sweet spot for dispatch.py workers.
- **Fairford cost model**: If Fairford ever uses GitHub Copilot as a Claude access layer, assume Pro+ minimum ($39/mo) and weekly token caps; direct API is safer.
- **Parallel to Anthropic Pro test**: Same economic pressure as the Claude Code Pro removal A/B test — agentic token consumption is breaking flat-rate pricing across the industry.

## Action Items

- Keep dispatch.py workers on direct Anthropic API (not GitHub or IDE-mediated).
- No change needed to current architecture — this confirms existing bets.
- Monitor: if GitHub introduces per-token pricing for agentic plans, that may become a routing alternative for Fairford Phase 2.
