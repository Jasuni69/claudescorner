---
title: "Steve Yegge: AI Adoption Curve — 20/60/20 and the Google Debate"
date: 2026-04-19
source: https://simonwillison.net/2026/Apr/13/steve-yegge/
tags: [ai-agents, adoption, agentic-coding, google, anthropic, claude-code]
signal: high
relevance: dispatch.py worker adoption framing, ENGRAM positioning, org-level AI rollout patterns
---

## Summary

Steve Yegge claimed Google's AI coding adoption mirrors John Deere's tractor adoption curve:

- **20%** — agentic power users (full autonomous coding workflows)
- **60%** — still using Cursor or equivalent chat tools (copilot-style, not agentic)
- **20%** — outright refusers

He attributed Google's lagging adoption to an **18+ month hiring freeze** preventing external engineers from bringing awareness of best practices and competitive gaps.

## Key Quote

> "Google engineering appears to have the same AI adoption footprint as John Deere, the tractor company."

## Rebuttals

**Addy Osmani (Google):** Directly contradicted Yegge — "Over 40K SWEs use agentic coding weekly here. Googlers have access to our own versions of @antigravity, @geminicli, custom models, skills, CLIs and MCPs for our daily work."

**Demis Hassabis (DeepMind):** Called the post "completely false and just pure clickbait" and told Yegge to "do some actual work."

## Relevance to Jason's Work

- The 20/60/20 curve is a useful framing for **Fairford PoC positioning** — most enterprise users are in the 60% chat-tool tier; the pitch is a path to the 20% agentic tier via Fabric + Claude.
- Validates the ClaudesCorner autonomous architecture (dispatch.py, skill-manager-mcp) as **ahead of the curve** for individual practitioners.
- The Google internal stack (custom MCPs, CLIs, skills) mirrors the ENGRAM architecture exactly — independent validation that MCP + skills + agent loops is the right substrate.
- Hiring freeze → knowledge gap = **the same problem ENGRAM solves** for teams that can't hire Claude Code power users.
