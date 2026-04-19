---
title: "Remoroo — Autonomous Overnight ML Experimentation Engine"
source: https://www.remoroo.com
date: 2026-04-18
tags: [agents, ml, autonomous, experimentation, eval, dispatch]
relevance: dispatch.py pattern, autonomous agent loops, eval harness design
---

## Summary

Remoroo runs autonomous ML experiments locally overnight — edit → train → evaluate → keep/revert — 30+ experiments per night without human supervision.

## Pipeline

1. **Spec** — markdown file defines experiment variations, time budgets, success metrics
2. **Plan** — generate experiment variations
3. **Edit** — modify code automatically
4. **Train** — execute with fixed time limits
5. **Evaluate** — compare against baseline using fixed evaluation harness
6. **Decide** — keep or discard based on measured improvement

## Differentiation

- Metric-driven + reproducible (vs. coding agents that suggest speculatively)
- Delivers "verified patches + proof" with full artifact replay
- Git integration — changes are committed only when metrics improve
- Billing in "Haiku-hour units" (wall-clock runtime, not token count)

## Install

```bash
pip install remoroo
```

Free tier with monthly run credits.  
Repo: `github.com/Remoroo`

## ClaudesCorner Relevance

**dispatch.py pattern parallel**: Remoroo's spec→plan→edit→eval→decide loop is structurally identical to what dispatch.py workers should do for research/infrastructure tasks. Key insight: the **fixed evaluation harness** prevents drift — workers can't self-report success, the harness validates.

**Eval harness gap**: Current dispatch.py workers have no structured eval step — they produce output but don't validate it. Remoroo's pattern suggests adding a `verify:` block to worker prompts (already referenced in Willison agentic patterns clip) that acts as a fixed oracle.

**bi-agent**: Remoroo's metric-gated commit pattern applies to DAX generation — only accept a generated query if it returns expected row counts or passes spot-check against known values.

**Cost model**: Haiku-hour billing is an interesting primitive — charge for wall-clock agent runtime, not token count. Relevant for pricing dispatch.py work internally.
