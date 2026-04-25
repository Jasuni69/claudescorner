---
title: "Kimi Vendor Verifier (KVV) — Agent Tool-Call Benchmark Suite"
source: https://kimi.com/blog/kimi-vendor-verifier
date: 2026-04-21
tags: [agents, benchmarks, tool-calling, dispatch, verify-oracle, open-source]
hn_pts: 152
signal: high
---

## Summary

Moonshot AI released the **Kimi Vendor Verifier (KVV)** alongside K2.6 — a reproducible 6-benchmark suite that audits inference provider correctness. The core insight: most "model failures" in production are actually infrastructure deviations (quantization bugs, KV cache corruption, broken tool-call serialization), not model deficiencies.

## Six Benchmarks

| Benchmark | What It Tests |
|-----------|--------------|
| Pre-Verification | API param enforcement (temperature, top_p constraints) |
| OCRBench | Multimodal pipeline correctness in ~5 min |
| MMMU Pro | Vision input preprocessing diversity |
| AIME2025 | Extended output / KV cache + quantization stress |
| **K2VV ToolCall** | **Tool-call consistency: F1 + JSON Schema accuracy** |
| SWE-Bench | Full agentic coding end-to-end (not open-sourced — sandbox deps) |

The **K2VV ToolCall** benchmark is the highest-signal item: it scores tool-calling via F1 and JSON Schema conformance, catching the exact failure mode that breaks dispatch.py workers silently (malformed tool outputs that pass text checks but fail schema validation).

## Infrastructure Requirements

- 2× NVIDIA H20 8-GPU servers
- ~15 hours sequential execution
- Checkpoint/resume for streaming inference

## Relevance to ClaudesCorner

**dispatch.py verify-oracle gap:** Current worker prompts describe expected behavior but don't embed schema-level oracle checks. K2VV ToolCall pattern — F1 scoring + JSON Schema accuracy on tool outputs — is the missing layer. Apply to:
- `bi-agent` DAX output validation (schema oracle on measure/column refs)
- dispatch.py worker output gates (JSON Schema assert before marking task complete)
- skill `verify:` sections (replace prose assertions with runnable schema checks)

**Vendor trust:** If dispatch.py is ever routed to Kimi K2.6 or another open-weight model, KVV gives an auditable trust score before deploying to production tasks.

Public leaderboard planned — track for when Kimi open-weights K2.6 fully.
