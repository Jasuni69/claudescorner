---
title: "Willison: Is Claude Code Going to Cost $100/Month? The Transparency Problem"
source: https://simonwillison.net/2026/Apr/22/claude-code-confusion/
date: 2026-04-22
tags: [anthropic, claude-code, pricing, transparency, max-plan, dispatch]
signal: medium
---

# Willison: Is Claude Code Going to Cost $100/Month? The Transparency Problem

**Source:** Simon Willison | 2026-04-22

## What Happened

On April 22, Anthropic's pricing page was quietly updated to restrict Claude Code exclusively to **Max plans** ($100–200/month), removing it from the $20 Pro tier. Discovery came via screenshots and Internet Archive comparisons — no announcement.

- **Scale of test**: Affected ~2% of new signups ("small A/B test on prosumer signups").
- **Reversal**: Anthropic reverted the public pricing page within hours of Willison's post going live.
- **Explanation**: Head of Growth said the experiment continued but pages were corrected because the change was "understandably confusing."

## Willison's Critique

The transparency failure is the real story:

> "The opaque handling and lack of clear communication damaged confidence in Anthropic's pricing transparency."

Removing the $20 entry point would harm adoption and education. The Pro plan is how most developers first encounter Claude Code; pricing it out kills the funnel.

## Relationship to The Register Story (Already Clipped)

The Register (clipped earlier today) covered the test itself and immediate impact. Willison adds:

- Reversal timing: happened *during the day*, same day as discovery
- Trust dimension: silent changes caught via Archive.org, not changelog
- Experiment continues in background despite page revert

## Implications for ClaudesCorner

- **Fairford cost model**: Max plan ($100–200/mo) is the realistic pricing floor for heavy Claude Code usage — budget accordingly even if Pro access currently works.
- **dispatch.py workers**: API-key based, unaffected by plan tier changes. The risk is interactive sessions, not headless workers.
- **Pattern**: Anthropic is running silent pricing experiments. Watch pricing pages with Archive.org or changedetection.io.
- **Max plan trajectory**: Two signals in one day (this + Copilot) confirm flat-rate pricing is breaking for agentic use. Subscription prices will rise; token pricing is the destination.
