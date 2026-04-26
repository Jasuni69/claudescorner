---
title: "DeepSeek-V4 Day-0: SGLang ShadowRadix + Miles RL Training"
source: https://www.lmsys.org/blog/2026-04-25-deepseek-v4/
clipped: 2026-04-26
tags: [llm-inference, open-weight, deepseek, sglang, rl-training, dispatch-py, agentic]
signal: high
---

# DeepSeek-V4 Day-0: From Fast Inference to Verified RL with SGLang and Miles

**Source:** lmsys.org — HN 37 pts, April 25 2026
**Models:** DeepSeek-V4-Pro (1.6T MoE, 49B active) + DeepSeek-V4-Flash (284B)

## Key Technical Contributions

### ShadowRadix — Hybrid Sparse-Attention Prefix Caching
DeepSeek-V4 uses a novel hybrid sparse-attention architecture with three heterogeneous KV pool types (sliding window, compressed KV, compression-state pools). Standard prefix caching breaks on this. SGLang's solution: **ShadowRadix** — virtual token coordinates + per-pool shadow mappings maintain cache coherence across all pool types without architectural changes. This is the key enabling primitive for cost-effective long-context serving.

### Flat Decode Throughput 4K → 900K Tokens
Benchmark result: decode throughput remains essentially flat from 4K to 900K context tokens.
- B200: 199 → 180 tok/s (−10% at near-1M ctx)
- H200: 266 → 240 tok/s (−10% at near-1M ctx)

This makes DeepSeek-V4 viable for long-horizon agentic tasks without the exponential cost cliff that breaks most MoE serving stacks.

### HiSparse CPU KV Offloading
Inactive KV cache pages are offloaded to CPU RAM via HiSparse, enabling up to **3× throughput improvement** on memory-constrained deployments. Paired with fused metadata preparation into CUDA graphs for speculative decoding.

### Custom Kernels
- **Flash Compressor** — reduces KV compression overhead to negligible levels
- **Lightning TopK** — sparse top-k selection from 100µs → ~15µs
- **FlashMLA** — hybrid attention fast kernel
- **FP4 expert weight handling** via TRTLLM-Gen fused MoE

### Miles — RL Training Stack
Full parallelism support: DP/TP/SP/EP/PP/CP. FP8 rollout + BF16 training. Rollout-training log-probability drift held at **~0.023** on the 285B model across 32 GB300 GPUs. Experimental indexer replay for data-efficient RL fine-tuning.

## Relevance to ClaudesCorner

**dispatch.py open-weight fallback routing:** DeepSeek-V4-Flash at $0.14/M input (vs Sonnet 4.6 $3/M) is now viable for Haiku-tier dispatch workers on long-context tasks, given the flat throughput curve. K2VV ToolCall benchmark still required before routing Fairford work — but inference quality gate is now the only blocker, not serving cost or context degradation.

**Long-context agentic sessions:** The 4K→900K flat curve means a dispatch.py worker session that grows from a short task to a 200K-token context doesn't suddenly become 10× more expensive or slower. This changes the cost model for deep-research workers.

**RL fine-tuning reference:** Miles' stable FP8 rollout pattern is the cleanest public example of verified RL at 285B scale — relevant if bi-agent DAX oracle ever moves to reward-model fine-tuning rather than hard rule checking.

## Action Items
- [ ] K2VV ToolCall benchmark: DeepSeek-V4-Flash vs Sonnet 4.6 for dispatch.py Haiku-tier routing
- [ ] Check DeepSeek-V4 on MCPAtlas (73.6% Pass@1 in V4-Pro — already promising for tool-call tasks)
- [ ] Monitor SGLang HiSparse Windows support (currently CUDA-only, no Windows binary)
