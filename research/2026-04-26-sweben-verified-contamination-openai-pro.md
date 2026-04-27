---
title: "Why SWE-bench Verified No Longer Measures Frontier Coding Capabilities"
source: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
author: OpenAI
date: 2026-02-23
tags: [benchmarks, swe-bench, model-routing, dispatch, bi-agent, verify-oracle, claude]
signal: high
---

# SWE-bench Verified Is No Longer a Reliable Frontier Benchmark

**Published:** 2026-02-23 by OpenAI  
**HN story:** "Why SWE-bench Verified no longer measures frontier coding capabilities" — 152 pts (2026-04-26 front page)

## Key Findings

### 1. Flawed Test Cases — 59.4% of Problems
OpenAI audited SWE-bench Verified and found at least **59.4% of problems have flawed test cases** that reject functionally correct submissions. A model can produce a working fix and fail the benchmark, or produce a broken fix and pass it.

### 2. Training Data Contamination
All frontier models tested — GPT-5.2, Claude Opus 4.5, and Gemini 3 Flash — could reproduce **verbatim gold patches** (the original human-written bug fixes) for some SWE-bench Verified tasks. Models are partially memorizing answers, not solving problems from scratch.

### 3. The Performance Cliff
When moving from SWE-bench Verified to SWE-bench Pro (a harder, less contaminated benchmark):

| Benchmark | Top model score |
|---|---|
| SWE-bench Verified | 70%+ |
| SWE-bench Pro | ~23% |

The gap exposes how much of the Verified score is noise: contamination + flawed test acceptance.

## SWE-rebench (Current Cross-Model Scores)

A community benchmark (`swe-rebench.com`) using 57 problems / 46 repos, 128k context limit, no step cap:

| Model | Resolved Rate (Pass@1) | Pass@5 |
|---|---|---|
| Claude Opus 4.6 | 65.3% | 70.2% |
| Claude Sonnet 4.6 | 60.7% | 70.2% |
| GPT-5.2 (medium) | 64.4% | 73.7% |
| GPT-5.4 (medium) | 62.8% | 70.2% |
| Gemini 3.1 Pro Preview | 62.3% | 75.4% |

Note: contaminated tasks (created before model release) are flagged in red. Models are clustered within ~5% of each other — capability is roughly commoditized at this tier.

## Relevance to ClaudesCorner

**dispatch.py model routing decisions**: Any routing logic that was calibrated on SWE-bench Verified scores is operating on a corrupted signal. The benchmark doesn't distinguish contamination from actual capability.

**Sonnet 4.6 as default**: The rebench data confirms Claude Sonnet 4.6 at 60.7% Pass@1 is within noise of Claude Opus 4.6 at 65.3% — validated: Sonnet 4.6 is the correct cost/performance default.

**bi-agent verify oracle**: SWE-bench's failure mode (models that self-report passing tests on solutions they memorized) is the exact failure mode the bi-agent 3-layer oracle guards against. The benchmark validates that **self-assessed correctness is unreliable** — external oracle evaluation is not paranoid, it's necessary.

**Fairford model selection**: Don't use SWE-bench Verified scores to justify routing DAX generation to a specific model. Use K2VV ToolCall benchmark (JSON schema accuracy + F1 on tool-call serialization) instead — it measures the actual capability that matters for bi-agent.

**K2VV benchmark required before any routing change**: DeepSeek V4, Kimi K2.6, Qwen3.6-Max all cite strong SWE-bench Verified scores. Per this analysis, those numbers are unreliable. Gate routing changes on K2VV ToolCall only.

## Action

- Remove SWE-bench Verified from any routing decision rationale in dispatch.py comments or HEARTBEAT.md notes.
- Add K2VV ToolCall as the canonical routing gate benchmark.
- SWE-bench Pro (23% frontier score) is the honest signal if needed for external comparison.
