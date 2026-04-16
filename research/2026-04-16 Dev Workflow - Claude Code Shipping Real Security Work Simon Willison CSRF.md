---
title: "Claude Code Shipping Real Security Work — Willison CSRF PR"
date: 2026-04-16
source: https://simonwillison.net/2026/Apr/14/replace-token-based-csrf/
via: simonwillison.net
tags: [claude-code, security, agentic-development, human-in-the-loop, datasette]
relevance: [claude-code-patterns, agent-quality, verification]
---

## Summary

Simon Willison used Claude Code to ship Datasette PR #2689 — replacing token-based CSRF protection with `Sec-Fetch-Site` header-based defense across 10 commits. The post is notable not for the security change itself, but for what it reveals about human-AI collaboration patterns at this level of work.

## What Claude Code Did

- Removed all `<input type="hidden" name="csrftoken">` hidden fields from templates
- Deleted the `skip_csrf(datasette, scope)` plugin hook from `hookspecs.py`
- Updated CSRF protection docs and added an upgrade guide section
- 10 commits total; Willison "closely guided" and cross-reviewed with GPT-5.4

## The Security Change

Replaced token-based CSRF with `Sec-Fetch-Site` header validation — approach from Filippo Valsorda's research, shipped in Go 1.25 (August 2025). Eliminates the maintenance burden of scattering tokens through templates and selectively disabling protection for external APIs.

## Notable Pattern: Human Honesty Loop

Willison decided to write PR descriptions by hand rather than AI-generated summaries — "partly to make them more concise and also as an exercise in keeping myself honest." This is a signal that top practitioners are actively resisting full AI narration of AI work to maintain comprehension.

## Relevance to Jason's Work

- **ENGRAM quality signal**: Claude Code can ship real security-relevant refactors, not just scaffolding
- **Human-in-the-loop framing**: Willison's "closely guided" phrasing is the correct posture — agent does the commits, human owns the decisions
- **Cross-review pattern**: using Claude Code + GPT-5.4 cross-review before merge is worth adopting for ENGRAM PRs
- **PR description discipline**: Willison's manual PR write-up practice is a useful counterweight to the "RIP Pull Requests" trend clipped earlier today
