---
title: "Claude Opus 4.7 vs Kimi K2.6: Workflow Orchestration DAG Test"
date: 2026-04-22
source: https://blog.kilo.ai/p/we-gave-claude-opus-47-and-kimi-k26
tags: [claude, kimi, benchmark, dispatch, workflow-orchestration, agent-architecture]
signal: high
relevance: dispatch.py model routing, Fairford Phase 2 cost modeling
---

# Claude Opus 4.7 vs Kimi K2.6: Workflow Orchestration DAG Test

**Source:** blog.kilo.ai | HN newest | 2026-04-22

## What Was Tested

Kilo.ai gave both models the same spec: **FlowGraph**, a persistent workflow orchestration API featuring:
- DAG validation
- Atomic worker claims
- Lease expiry recovery
- Pause/resume/cancel operations
- SSE event streaming
- 20 endpoints

This maps directly to the architecture concerns in dispatch.py: worker claims, task state machines, lease/timeout recovery.

## Results

| Dimension | Claude Opus 4.7 | Kimi K2.6 |
|-----------|----------------|-----------|
| Score | **91/100** | 68/100 |
| Cost | ~5× | ~1× (19% of Claude) |
| Confirmed bugs | 1 | 6 |
| Architecture delivery | Complete | Complete |
| Test suite reliability | High | Masked bugs |

**Cost efficiency framing:** Kimi K2.6 delivered "75% of Claude's score at 19% of the cost."

## Key Findings

1. **Claude wins on correctness** — only one genuine bug (multi-expired lease recovery edge case). Kimi had six confirmed problems in lease handling, cross-run scheduling, and live SSE streaming.

2. **Kimi's tests lied** — both models claimed passing tests. Manual code review exposed correctness gaps Kimi's own test suite masked. Self-assessment is unreliable for both models.

3. **Both delivered the scaffold** — Prisma schemas, Hono routes, test suites all present in both outputs. The divergence was in state-machine edge cases, not structure.

## Practical Recommendations (from Kilo.ai)

- **Prototyping/scaffolding:** Kimi K2.6 is compelling at 19% of the cost.
- **Production correctness** (state machines, lease expiry, worker coordination, live streaming): Claude Opus 4.7 is substantially safer.

## Signal for ClaudesCorner

- **dispatch.py tier model validated:** Claude Sonnet/Opus for tier 2/3 orchestration tasks (correctness-critical); Haiku/Kimi for leaf scaffolding is a viable cost play.
- **Self-assessment unreliability** confirms bi-agent 3-layer oracle is necessary — model-reported test pass is not sufficient.
- **Fairford cost modeling:** Kimi K2.6 at 19% of Claude cost is a legitimate fallback for non-critical Fabric DAG generation tasks; not for production lease/state recovery paths.
- **Dispatch worker prompts** should embed validation oracles (not rely on model's own test claims) — third independent confirmation of this gap.
