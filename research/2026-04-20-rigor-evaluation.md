---
title: Rigor AI Agent Proxy — Evaluation for dispatch.py
date: 2026-04-20
tags: [evaluation, dispatch, security, proxy]
source: internal-eval
---

# Rigor Proxy — dispatch.py Integration Evaluation

## Verdict: NO-GO (product unverifiable, better alternatives exist)

## Findings

"Rigor" as described in the 2026-04-19 synthesis clip (MIT MITM proxy, Rego policy enforcement,
wire-level hallucination filtering via HTTPS_PROXY) cannot be located in public repositories,
GitHub search, or vendor documentation. The clip may reference an early-access or private beta
product that hasn't shipped publicly yet.

## Closest public alternatives

| Tool | Approach | Rego | HTTPS_PROXY | Latency | Verdict |
|------|----------|------|-------------|---------|---------|
| Microsoft Agent Governance Toolkit | In-process Python SDK | Yes | No | <0.1ms p99 | Viable for in-process use |
| ProxyClawd | HTTPS_PROXY subprocess intercept | No | Yes | Unknown | Low relevance (Claude-specific, no policy engine) |
| ClawShield | Reverse proxy + iptables + eBPF | No | No | Unknown | Over-engineered for 3-worker dispatch |

## dispatch.py-specific blockers

1. **Subprocess isolation**: dispatch.py workers are independent `claude.exe` subprocesses.
   HTTPS_PROXY wiring requires injecting the proxy env var into each worker's env copy — doable
   (`env["HTTPS_PROXY"] = "http://localhost:PORT"` in `run_task()`), but the proxy server must
   be running before dispatch starts and must handle 3 concurrent worker streams.

2. **TLS termination friction**: MITM proxy needs self-signed CA trusted by the OS cert store or
   injected via `NODE_EXTRA_CA_CERTS`. Non-trivial on Windows without admin rights.

3. **5-minute timeout sensitivity**: Any proxy startup overhead or per-request latency eats into
   the 300s TIMEOUT_SECONDS. Not quantifiable without a real product to benchmark.

4. **Hallucination filtering scope**: dispatch.py workers write to log files — output is inspected
   post-hoc via result_file, not streamed. A MITM proxy intercepts the API call layer, not the
   output layer. The verify oracle pattern already in dispatch.py workers covers the output layer
   at lower cost.

## Recommendation

Keep the **verify oracle** approach already in place (HEARTBEAT oracle, file-size oracle, MEMORY.md
entry count oracle). This covers the output correctness concern at zero infrastructure cost.

Revisit Rigor if/when a public repo surfaces with:
- Confirmed HTTPS_PROXY compatibility
- Benchmarked latency on subprocess workloads
- Free self-hosted tier

Until then, close this backlog item as "researched — deferred pending public release."
