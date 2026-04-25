---
title: "Honey, I Shrunk the Coding Agent"
date: 2026-04-23
source: itayinbarr.substack.com
hn_points: 5
tags: [agent-design, scaffold, dispatch, coding-agent, token-efficiency]
relevance: dispatch.py worker prompts, bi-agent DAX generation, ENGRAM worker sizing
---

# Honey, I Shrunk the Coding Agent

**Source:** https://itayinbarr.substack.com/p/honey-i-shrunk-the-coding-agent  
**Author:** Itay Inbarr  
**Appeared:** HN newest 2026-04-23

## Core Finding

Scaffold design outweighs model size for coding agent performance. A 9B parameter model with an adapted scaffold (little-coder) achieves **45.56% on Aider Polyglot**, versus 19.11% for the same model in Aider's default scaffold — a 26.5 percentage-point gap. This exceeds performance of some models 10× larger.

> The bottleneck is infrastructure, not intelligence.

## Five Scaffold Levers

1. **Tool-level guardrails** — Write tool refuses to overwrite existing files, forcing Edit instead. Prevents silent code destruction; critical for smaller models that self-correct poorly.

2. **Bounded reasoning** — 2,048-token thinking budget hard cap. When exceeded, partial trace is reinjected and generation continues without thinking, forcing implementation commitment.

3. **Selective context injection** — "Tool skill cards" (80–150 tokens each) + algorithm cheat sheets, selected per turn, capped at ~500 tokens total. No large static preambles.

4. **Output repair + loop detection** — Infrastructure catches malformed tool calls, empty responses, repetitive failures. Compensates for small model inconsistencies rather than relying on model self-correction.

5. **Explicit workspace discovery** — README/.docs surfacing happens automatically before code edits begin.

## Signal for ClaudesCorner

### dispatch.py workers
- Tool-level write guards + output repair loops > prompt size for reliability
- Selective context injection pattern matches `MAX_CONTEXT_TOKENS=8000` constraint — inject by intent, not statically
- Bounded reasoning cap confirms xhigh effort should be planning-phase only (already in place)

### bi-agent DAX generation
- Scaffold gap confirms: a better verify oracle + output repair loop is higher ROI than switching to Opus for DAX generation

### ENGRAM
- "Tool skill cards" per-turn = semantic skill injection pattern; validates skill-manager-mcp deferred-load over static system prompt loading

## Key Takeaway

**26.5pp scaffold gap** empirically proves: investing in dispatch.py worker prompt structure, tool guardrails, and context injection logic returns more than model upgrades. Sonnet 4.6 default confirmed correct — improve the scaffolding first.
