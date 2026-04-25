---
title: "CubeSandbox — Tencent KVM microVM Agent Sandbox, E2B-Compatible"
date: 2026-04-23
source: https://github.com/tencentcloud/CubeSandbox
tags: [sandbox, agents, microvm, dispatch, infrastructure, isolation]
signal: high
---

# CubeSandbox — TencentCloud KVM Agent Sandbox

**Source:** github.com/tencentcloud/CubeSandbox · HN newest

## What It Is

CubeSandbox is TencentCloud's open agent execution sandbox built on RustVMM + KVM microVMs. Each agent gets a dedicated guest OS kernel (not shared-kernel Docker). Designed for untrusted code from AI agents with sub-100ms coldstart and minimal memory overhead.

## Key Technical Specs

| Metric | Value |
|--------|-------|
| Cold start | <60ms |
| Cold start (50 concurrent) | <150ms |
| Memory overhead per instance | <5MB |
| Isolation | Dedicated kernel + eBPF network filtering |
| Instances per node | Thousands |

## Architecture

- **RustVMM + KVM**: Hardware-level virtualization, not container namespaces
- **CoW snapshot cloning**: Rapid provisioning via copy-on-write from a base image
- **CubeVS (eBPF)**: Per-sandbox network isolation and inter-sandbox traffic filtering
- **Multi-component**: CubeAPI / CubeMaster / CubeProxy / Cubelet / CubeVS / CubeHypervisor
- **E2B SDK compatible**: Drop-in URL swap — `SANDBOX_URL=https://cubesandbox.tencent.com`, no code changes

## Comparison vs Alternatives

| Approach | Isolation | Cold Start | Memory |
|----------|-----------|------------|--------|
| Docker | Shared kernel (low) | ~1s | High |
| Traditional VM | Dedicated kernel | ~10s | High |
| **CubeSandbox** | Dedicated kernel + eBPF | <60ms | <5MB |
| smolvm | libkrun VMM | <200ms | Low |

CubeSandbox is faster and denser than smolvm, with the added advantage of E2B SDK compatibility and a REST gateway — no need for native VMM installation.

## Relevance to ClaudesCorner

- **dispatch.py worker isolation**: Current workers run in the same process. CubeSandbox is the missing sandboxing layer — REST API = zero-dependency integration via `HTTP` from dispatch.py
- **Windows-friendly**: REST gateway means no native Linux VMM requirement; dispatch.py workers on Windows can call the REST API to spin ephemeral sandboxes
- **smolvm comparison**: smolvm (tracked) is Mac/Linux only; CubeSandbox REST API is cross-platform — higher priority for ClaudesCorner on Windows 11
- **E2B drop-in**: If any dispatch worker already uses E2B SDK, migration is one env var change
- **Security posture**: KVM + eBPF network isolation prevents lateral movement between workers — addresses the AgentKey/CrabTrap threat model at execution layer

## Action Items

- Evaluate CubeSandbox REST API as dispatch.py worker execution wrapper (Phase 2 isolation)
- Compare latency overhead of REST-wrapped sandbox calls vs current in-process execution
- CubeSandbox + AgentKey (identity) + CrabTrap (outbound) + AgentRQ (escalation) = complete worker governance stack
- Check license before Fairford use (TencentCloud OSS — verify Apache/MIT vs proprietary)
