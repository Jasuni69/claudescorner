---
title: "Anthropic Project Deal — Claude-Run Marketplace Experiment"
date: 2026-04-27
source: https://www.anthropic.com/features/project-deal
tags: [anthropic, agents, multi-agent, commerce, model-capability, dispatch]
signal: high
---

# Anthropic Project Deal — Claude-Run Marketplace Experiment

## What It Is

Anthropic's internal research experiment (December 2025, published April 2026) where 69 employees used Claude agents to autonomously negotiate and execute real trades in a classified marketplace. Agents struck **186 deals worth over $4,000** in actual goods (snowboards, ping-pong balls, etc.) without human intervention during negotiations. All negotiations ran through Slack channels.

## Key Findings

**Model capability > prompting.** Stronger models (Opus) generated **$3.64 more per item sold** than weaker models (Haiku). Prompting agents to negotiate aggressively or cooperatively made minimal difference — model tier was decisive.

**Asymmetric awareness.** Users with inferior agents (Haiku) didn't perceive any disadvantage vs. Opus users, even when consistently getting worse deals. The performance gap was invisible to the humans.

**Agent-to-agent negotiation works without pre-scripted protocols.** Agents successfully represented human preferences through natural language, handling ambiguity and counter-offers without explicit negotiation rules.

**Unexpected agent behavior at scale.** One participant unknowingly bought a duplicate snowboard; another agent bought ping-pong balls as a "gift to itself." Edge-case behavior emerged from model autonomy, not bugs.

## Relevance to ClaudesCorner

**dispatch.py tier routing confirmed.** The $3.64/item Opus vs. Haiku gap on negotiation tasks maps directly to the dispatch.py Sonnet/Opus tier: model capability at decision-making tasks is not fungible across tiers. Using Haiku for tasks requiring judgment = invisible underperformance.

**Agent-to-agent communication primitive.** Project Deal validates that agents can negotiate/coordinate via natural language channels (Slack in this case) without a formal protocol layer — relevant to dispatch.py worker communication and the MCP Agent Mail pattern (file reservations + message threading).

**Human blindness to agent underperformance.** The asymmetric-awareness finding is a governance signal: workers running on wrong model tier will appear to succeed while producing worse outcomes. This argues for explicit model-tier enforcement in dispatch.py worker configs, not just cost-based routing.

**ENGRAM multi-agent positioning.** Anthropic's own internal research shows agent-to-agent commerce as a natural next step after single-agent workflows — validates ENGRAM's multi-agent memory and communication scope.

## HN Signal

Low traction (4–6 pts across multiple submissions) — content surfaced via Anthropic features page, not organic HN discovery. Quality of research > discovery velocity here.
