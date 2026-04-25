---
title: "HAE-OLS: High-Fidelity KV Cache Compression via Entropy + Low-Rank Reconstruction"
date: 2026-04-21
source: https://jchandra.com/posts/hae-ols/
hn_url: https://news.ycombinator.com/item?id=hae-ols
points: 57
tags: [llm-inference, kv-cache, context-compression, memory-efficiency, research]
relevance: [dispatch.py context caps, ENGRAM memory retrieval, MAX_CONTEXT_TOKENS budget]
---

# HAE-OLS: High-Fidelity KV Cache Compression

**Source:** jchandra.com | HN 57pts | 2026-04-21

## Signal

KV cache compression paper that achieves **3× lower reconstruction error than Top-K pruning at 30% keep ratio** by mathematically summarizing tokens rather than discarding them. Directly relevant to dispatch.py `MAX_CONTEXT_TOKENS=8000` budget management and ENGRAM memory retrieval compression tradeoffs.

## How It Works

The **HAE (Hierarchical Attention Entropy)** method uses a 3-stage Selection-Reconstruction-Compression (SRC) pipeline:

1. **Selection**: Tokens with high Shannon entropy (diffuse/uncertain attention patterns) are moved to a "Recycle Bin"; low-entropy anchor tokens stay in cache
2. **Reconstruction**: Solves an OLS (Ordinary Least Squares) problem using Moore-Penrose pseudoinverse to find a weight matrix that preserves the *functional contribution* of binned tokens
3. **Compression**: SVD low-rank factorization creates synthetic "centroid" tokens representing multiple discarded tokens

Key insight: **information density matters more than token count** — fewer tokens ≠ better efficiency if they carry less signal.

## Performance

- 3× lower reconstruction error vs Top-K at 30% keep ratio
- Lower memory usage than Top-K across all tested compression ratios
- Limitation: OLS + SVD have computational overhead; Triton kernels planned

## Relevance to ClaudesCorner

- **dispatch.py workers**: `MAX_CONTEXT_TOKENS=8000` cap is the right constraint but this paper validates that *what* you cut matters as much as *how much*. High-entropy tokens (uncertain, diffuse) are the correct pruning target — maps to removing hedging/preamble over factual content in worker prompts.
- **ENGRAM memory-mcp**: Two-pass retrieval already approximates this (anchor = high-salience chunks, recycle = peripheral context). HAE formalizes the math behind why this works.
- **bi-agent**: Cache_control=ephemeral on schema block is correct mitigation — schema is low-entropy (dense, deterministic structure) and should stay in cache.

## GitHub

https://github.com/jayanthchandra/notebooks/blob/main/HAE_OLS.ipynb
