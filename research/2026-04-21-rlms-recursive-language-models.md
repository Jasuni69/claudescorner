---
title: "RLMs: Recursive Language Models Collapse Reasoning + Tool Use"
date: 2026-04-21
source: https://raw.works/rlms-are-the-new-reasoning-models/
hn_url: https://news.ycombinator.com/newest
points: 1
tags: [reasoning, agents, rlm, dispatch, architecture, small-models]
---

# RLMs: Recursive Language Models Are the New Reasoning Models

**Core thesis**: Recursive Language Models (RLMs) unify reasoning and tool use by treating the context window itself as the object of computation — models recursively inspect, partition, and query subsets of their own context.

## Key Distinction from Reasoning Models

| | Reasoning Models (o1-style) | RLMs |
|---|---|---|
| Approach | More compute within one forward pass | Recursive self-query over context partitions |
| Reasoning | Internal chain-of-thought | External, programmatic context exploration |
| Tool use | Separate capability | Collapsed into the same recursive loop |
| Context | Static input | Dynamic, explorable environment |

Chain-of-thought improved thinking. ReAct bridged reasoning + actions. Function calling standardized tool reliability. RLMs unify all three by making the prompt itself a computable environment.

## Benchmark Evidence

- **LongCoT**: Qwen3.5-27B with RLM → **22.18%**, more than **2× GPT-5.2** on the same eval
- Also strong on: Oolong (long-context reasoning), LongMemEval (interactive memory)

## Democratization Implication

Small models running recursively on modest hardware can match or exceed frontier model performance on long-horizon tasks. This shifts the advantage away from GPU-rich labs toward distributed architectures.

## Signal for ClaudesCorner

- **dispatch.py worker sizing**: Current Tier 1=Haiku / Tier 2=Sonnet / Tier 3=Opus model routing was sized assuming frontier models needed for hard tasks. RLM pattern suggests Haiku in a recursive loop may match Sonnet on structured long-horizon tasks — potential cost reduction.
- **ENGRAM retrieval**: memory-mcp's two-pass brain retrieval already approximates recursive context querying. RLM framing validates this pattern as principled, not ad hoc.
- **bi-agent**: NL→DAX pipeline could benefit from recursive self-verification loop (query schema, generate DAX, re-query schema against output) rather than single-shot generation.
- **Watch**: Whether Claude API supports programmatic context partitioning or whether this requires multi-turn session management.
