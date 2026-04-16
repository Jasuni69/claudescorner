---
title: "Darkbloom — Private LLM Inference on Idle Apple Silicon"
date: 2026-04-16
source: https://darkbloom.dev
via: Hacker News (222 points)
tags: [infrastructure, inference, privacy, apple-silicon, decentralized]
relevance: [cost-optimization, private-inference, agent-infra]
---

## Summary

Darkbloom (by Eigen Labs) is a decentralized inference network that routes LLM requests to idle Apple Silicon machines. Hardware owners earn 100% of inference revenue; users get ~50% cost reduction vs. centralized cloud with cryptographic privacy guarantees.

## Architecture — 4-Layer Privacy Stack

1. **End-to-end encryption** — requests encrypted on-device before transmission; coordinator only routes ciphertext
2. **Hardware attestation** — each node uses cryptographic keys in Apple Secure Enclave; attestation chains back to Apple's root CA
3. **Hardened runtime** — inference process locked at OS level; debugger and memory inspection blocked
4. **Traceable output** — every response signed by the specific machine; full attestation chain published publicly

## Key Facts

- **API**: OpenAI-compatible — swap base URL, keep existing SDK
- **Models**: Gemma 4 26B, Qwen3.5 (27B and 122B MoE), MiniMax M2.5 (239B)
- **Modalities**: text, image (FLUX.2), speech-to-text (Cohere Transcribe)
- **Status**: research preview

## Relevance to Jason's Work

- Alternative inference backend for ENGRAM or Clementine where data sensitivity matters
- OpenAI-compatible API means zero integration cost for any agent already using Claude SDK fallback
- Cost angle: if fabric-mcp or kpi-monitor grows inference spend, Darkbloom is a viable spillover backend
- Privacy model (attestation chains, no operator visibility) aligns with Fairford Holdings compliance constraints

## HN Thread Signal

222 points — strong traction. Discussion focused on Apple Secure Enclave attestation as genuine technical differentiation vs. "trust us" private inference claims from other providers.
