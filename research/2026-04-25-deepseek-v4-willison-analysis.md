---
title: "DeepSeek V4 — Willison Analysis: Cheaper Than Sonnet 4.6, MIT, 1M Context"
date: 2026-04-25
source: https://simonwillison.net/2026/Apr/24/deepseek-v4/
tags: [models, cost, dispatch, routing, open-weights, deepseek]
relevance: high
---

# DeepSeek V4 — Willison Analysis

**Source:** simonwillison.net, April 24 2026
**Signal:** V4-Pro at $1.74/M input tokens undercuts Sonnet 4.6 ($3/M) on price with MIT license and 1M context window — strongest open-weight Sonnet-tier routing candidate yet for dispatch.py.

## Models Released

DeepSeek released two preview models:

| Model | Params (total / active) | Context | Input $/M | Output $/M |
|---|---|---|---|---|
| V4-Flash | 284B / 13B MoE | 1M | $0.14 | $0.28 |
| V4-Pro | 1.6T / 49B MoE | 1M | $1.74 | $3.48 |

Both are MIT licensed and available on HuggingFace (865GB for Pro, 160GB for Flash).

## Price Comparison vs Current Stack

- **V4-Flash ($0.14/M)** — cheaper than GPT-5.4 Nano ($0.20/M). Potential Haiku-tier replacement.
- **V4-Pro ($1.74/M)** — cheaper than Claude Sonnet 4.6 ($3/M input). Largest open-weight model yet (1.6T, exceeds Kimi K2.6 at 1.1T).
- V4-Pro is 2× the size of DeepSeek V3.2 (685B), with dramatic efficiency gains: at 1M context, V4-Pro uses only 27% of single-token FLOPs and 10% of KV cache vs V3.2.

## Performance

- Benchmarks position V4-Pro as competitive with frontier models but trailing ~3–6 months behind GPT-5.4 and Gemini-3.1-Pro on reasoning tasks.
- SWE-Verified 80.6%, MCPAtlas 73.6% Pass@1, LiveCodeBench 93.5% (surpasses Claude on this benchmark per separate HN report).
- Willison's pelican SVG test: generally solid but V4-Pro had anatomical issues.

## Dispatch.py Routing Implications

- **V4-Pro as Sonnet-tier fallback**: price advantage is real ($1.74 vs $3/M input). Requires K2VV ToolCall benchmark before Fairford routing — silent tool-call serialization failures are the risk.
- **V4-Flash as Haiku-tier fallback**: $0.14/M is compelling but 13B active params — verify task quality on dispatch leaf-node workloads.
- **1M context window** removes the context-budget pressure on long research tasks; dispatch.py MAX_CONTEXT_TOKENS=8000 cap becomes less of a constraint if routing to V4.
- Available via OpenRouter today (Willison tested there). No local run yet — quantized versions expected soon; Flash may be viable on local hardware.

## License

MIT — no commercial restriction. Clean for Fairford and internal use.

## Action

Run K2VV ToolCall benchmark on V4-Pro before adding as dispatch.py routing option. If F1 + JSON Schema accuracy matches Sonnet 4.6, the cost reduction (~42% cheaper on input) justifies a Sonnet-tier routing lane.
