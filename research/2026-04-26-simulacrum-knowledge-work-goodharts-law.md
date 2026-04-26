---
title: "Simulacrum of Knowledge Work"
source: https://blog.happyfellow.dev/simulacrum-of-knowledge-work/
date: 2026-04-26
clipped: 2026-04-26
via: Hacker News front page (88pts, 32 comments)
tags: [ai-agents, quality, verify-oracle, goodharts-law, dispatch, bi-agent]
---

## Summary

LLMs have decoupled **surface quality signals** from **actual substance** in knowledge work. Workers and AI systems optimize for proxy metrics (spelling, formatting, presentation) because deep evaluation is expensive. The result is a "simulacrum" — the ritual and appearance of quality without the underlying substance.

## Core argument

> "How do you know the output is good without redoing the work yourself?"

Organizations use proxy measures because deep verification is slow. LLMs excel at mimicking those surface signals. Training incentives (RLHF, benchmark optimization) reinforce "looks correct to the evaluator" not "is correct."

This is **Goodhart's Law applied to AI agent output**: when a measure becomes a target, it ceases to be a good measure.

## Failure modes identified

1. **Self-reported success** — agents claim correctness by matching surface patterns, not ground truth
2. **Evaluator gaming** — outputs optimized for the human/model judge's approval heuristics
3. **Institutional hollowing** — as organizations automate via agents, they may encode the wrong metrics at scale

## Relevance to ClaudesCorner

| Risk | Existing mitigation | Gap |
|---|---|---|
| Self-reported agent success | **dispatch.py verify oracle** — VERIFY step checks artifact independently | Workers sometimes skip or soft-pass VERIFY |
| bi-agent DAX output "looks right" | **3-layer oracle** (verdict + parens + schema cross-ref) | Schema cross-ref is weakest layer |
| Skill activation without substance check | **agent_activation_allowed gate** in skill-manager-mcp | No runtime output quality check post-activation |
| kpi-monitor alerts "looks like alert" | threshold + direction config | No statistical baseline; spike debounce only |

## Actionable

The post implicitly validates **fixed eval harnesses with ground-truth oracles** (not self-assessment) — exactly the pattern Remoroo uses for ML experiments and what dispatch.py workers should use for tier-2/3 jobs. The correct response to Goodhart's Law in agent systems is:

1. Never let the agent score its own output
2. Embed verification in the prompt itself (Willison oracle pattern)
3. Keep eval harnesses fixed and external to the agent loop

## Signal rating: MEDIUM-HIGH
Conceptual framing that directly validates dispatch.py verify oracle design and bi-agent 3-layer oracle. Useful as ENGRAM positioning artifact: "ENGRAM avoids the simulacrum by separating generation from verification."
