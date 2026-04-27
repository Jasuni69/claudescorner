---
title: "Claude Opus 4.6 vs. Opus 4.7 Effort Levels and Prompt Steering Benchmarks"
source: https://ai.georgeliu.com/p/claude-opus-46-vs-opus-47-effort
author: George Liu
date: 2026-04-26
hn_points: 1
tags: [claude, opus-46, opus-47, prompt-steering, dispatch, cost-optimization, benchmarks]
clipped_by: dispatch-plan-agent
---

# Claude Opus 4.6 vs. 4.7 Prompt Steering Benchmarks

**Source**: ai.georgeliu.com | HN newest 2026-04-26

## Setup

200 headless Claude Code sessions comparing Opus 4.6 (high effort) vs Opus 4.7 (xhigh effort) across 5 prompt steering variants and 10 diverse tasks. Measured: cost, latency, instruction-following accuracy, token usage.

## Key Findings

### Cost Impact by Steering Variant

| Steering | Opus 4.6 high | Opus 4.7 xhigh | Note |
|---|---|---|---|
| `no-tools` prefix | significant reduction | **-63% cost** | but -2 instruction-following passes |
| `concise` prefix | **-56.3% cost, 0 accuracy loss** | moderate reduction | best overall signal |
| `think-step-by-step` | cost reduction | **+22% cost increase** | zero improvement in instruction-following |

### Model Divergence (Critical)

**Identical steering text produced opposite effects between models.** What reduces cost on Opus 4.6 may increase cost on Opus 4.7. Prompt steering is not model-portable — any steering change needs per-model verification.

### Instruction-Following Consistency

- **Opus 4.6**: 9/9 instruction-following across all variants at high effort — consistent and predictable
- **Opus 4.7**: variant-dependent degradation; `no-tools` = -2 passes; `concise` at medium effort = -1 pass; xhigh effort required to approach 4.6 parity

## Routing Recommendations

- **Direct-answer / prose / inline code tasks**: test `no-tools` first, verify file-access not required
- **Tool-dependent tasks (codebase inspection, debugging)**: use `concise` prefix — 56.3% cost reduction on 4.6 with zero accuracy penalty
- **Avoid `think-step-by-step` / `ultrathink` on Opus 4.7** without per-prompt cost verification; they increase expense without improving compliance

## Relevance for ClaudesCorner

- **dispatch.py worker prompts**: apply `concise` prefix to Sonnet 4.6 tier-1 workers first (direct analog to 4.6 high effort result); expect ~50% cost reduction with no oracle regression
- **Sonnet 4.6 default confirmed**: Opus 4.7 instruction-following degradation at medium effort + token inflation = Sonnet 4.6 as dispatch.py default is correct; xhigh effort required on 4.7 to be reliable = expensive
- **Steering is not portable**: any future model routing change (Sonnet→Opus, 4.6→4.7 tier) requires re-benchmarking all worker steering prefixes independently — cannot copy prompts across model versions
- **bi-agent DAX prompts**: `concise` prefix on the Haiku executor layer is the first experiment; `think-step-by-step` should not be used on Haiku (likely same anti-pattern as 4.7 xhigh)
