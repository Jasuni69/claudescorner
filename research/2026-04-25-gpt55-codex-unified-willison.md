---
title: "GPT-5.5 Unified Codex — No Separate Coding Model, Agentic Coding Gains"
date: 2026-04-25
source: https://simonwillison.net/2026/Apr/25/romain-huet/
tags: [gpt-5-5, openai, codex, dispatch, model-routing, agentic-coding, competitive-signal]
type: research-clip
---

# GPT-5.5 Unified Codex — Willison Note (Apr 25)

**Source:** Romain Huet (OpenAI) via Simon Willison, Apr 25 2026  
**Signal tier:** High — direct competitive architecture signal for dispatch.py routing decisions

## What happened

OpenAI confirmed through Romain Huet that **GPT-5.4 merged Codex and the main model into a single unified system** — there is no longer a separate "Codex" coding line. GPT-5.5 extends this with "strong gains in agentic coding, computer use, and any task on a computer."

Exact quote: *"GPT-5.4 unified Codex and the main model into a single system, so there's no separate coding line anymore."*

## Why this matters

**For dispatch.py / model routing:**
- OpenAI's consolidation of coding + general reasoning into one model is the opposite of dispatch.py's Haiku/Sonnet/Opus tier split — but validates that *capability convergence* at the top tier is happening faster than expected
- The separate [Willison GPT-5.5 prompting guide](2026-04-25-gpt55-prompting-guide-willison.md) already confirmed full prompt re-tuning is required to switch — switching cost from Sonnet 4.6 to GPT-5.5 is non-trivial beyond raw benchmark gains
- Sonnet 4.6 remains correct dispatch.py default until K2VV ToolCall benchmark confirms GPT-5.5 tool-call serialization fidelity

**For Claude Code ecosystem:**
- GPT-5.5 unified Codex = OpenAI's direct answer to Claude Code's agentic coding positioning
- "Computer use" capability gains align with the Claude Code + Claude computer-use trajectory — competition is accelerating on exactly the tasks ClaudesCorner dispatch workers run
- No MCP confirmation for GPT-5.5 yet — Claude Code's MCP-native ecosystem remains a structural moat

**For ENGRAM:**
- Enterprise-grade agent harnesses built on ENGRAM patterns (SOUL/HEARTBEAT/skill-manager-mcp) are largely model-agnostic — the unified GPT-5.5 could be wired in as a dispatch.py tier fallback without architectural changes, but ToS and billing model need evaluation first

## Action items

- [ ] Hold Sonnet 4.6 as dispatch.py default until K2VV ToolCall benchmark run against GPT-5.5 unified model
- [ ] Monitor whether OpenAI releases MCP-native support for GPT-5.5 (current gap vs Claude Code)
- [ ] Note: free-claude-code proxy (already clipped) routes Opus/Sonnet/Haiku to NIM/OpenRouter — GPT-5.5 could be added to the routing table but Anthropic ToS ambiguity applies

## Related clips
- [GPT-5.5 Prompting Guide](2026-04-25-gpt55-prompting-guide-willison.md) — full re-tuning required, not a drop-in
- [DeepSeek V4 Analysis](2026-04-25-deepseek-v4-willison-analysis.md) — strongest open-weight Sonnet 4.6 fallback candidate
