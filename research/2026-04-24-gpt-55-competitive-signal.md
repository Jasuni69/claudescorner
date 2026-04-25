---
title: "GPT-5.5 — Competitive Signal vs Claude Sonnet 4.6"
source: https://openai.com/index/introducing-gpt-5-5/
date: 2026-04-24
tags: [gpt, openai, competitive, dispatch, routing, agents]
hn_points: 932
hn_comments: 576
signal: medium
---

# GPT-5.5 — Competitive Signal

OpenAI released GPT-5.5 on or around 2026-04-23. HN front page #1 with 932 points.

## What's Known (from HN thread, Willison, Codex backdoor API)
- Available through OpenAI Codex preview access; described as "fast, effective and highly capable" (Willison)
- Gradual rollout starting with Pro/Enterprise accounts
- OpenAI article URL: openai.com/index/introducing-gpt-5-5/ (403 on direct fetch — likely geo/auth gated)
- No confirmed MCP-native support in launch announcement

## HN Discussion Signals
- Engineers expressing dependency concern: "losing access feels like I've had a limb amputated"
- Commenters prefer Claude's refusal behavior over GPT's; Claude cited as better coding partner
- Vendor lock-in and non-determinism discussed as shared GPT/Claude risks
- Kimi K2.6, Qwen, DeepSeek mentioned as open-weight alternatives

## Routing Implications for dispatch.py
- **Hold Sonnet 4.6 as default** — no benchmark data yet confirming GPT-5.5 > Sonnet 4.6 on tool-call accuracy or DAX generation
- If OpenAI releases MCP-native GPT-5.5, re-evaluate as Haiku-tier fallback for research workers
- K2VV ToolCall benchmark should gate any routing change before Fairford use
- Claude's edge: postmortem transparency (3 bugs disclosed openly) vs OpenAI's opaque degradations

## Watch
- Willison benchmark post (expected within days — he already has Codex access)
- Pricing announcement (not yet public)
- MCP support declaration
