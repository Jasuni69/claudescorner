---
title: "exe.dev — Bare-Metal Cloud Built for AI Agent Workloads"
date: 2026-04-24
source: https://crawshaw.io/blog/building-a-cloud
hn_pts: 1045
tags: [infrastructure, cloud, agents, compute, nvme, exe-dev]
relevance: medium-high
---

# exe.dev — Bare-Metal Cloud Built for AI Agent Workloads

**Post**: crawshaw.io/blog/building-a-cloud  
**Author**: David Crawshaw (SQLite Go port, Tailscale)  
**HN**: 1045pts, 526 comments  
**Product**: exe.dev

## Core Thesis

Modern cloud abstractions are misaligned with actual computing needs. Crawshaw argues three fundamental problems force users to overpay and underperform:

1. **VM billing granularity**: Current clouds bill per-VM rather than per raw CPU/memory unit, forcing underutilization. exe.dev separates compute resources from VM instances for denser packing.

2. **Storage mismatch**: Remote block devices made sense for spinning disks (10ms seek). With NVMe SSDs, remote block adds 10× IOPS overhead for no benefit. exe.dev uses **local NVMe with async replication** — matching MacBook-level ~500k IOPS vs EC2's $10k/month for 200k IOPS.

3. **Egress pricing as lock-in**: Hyperscaler egress charges are 10× datacenter rates — a deliberate lock-in mechanism. exe.dev eliminates this.

## AI Agent Connection

The author explicitly names AI agents as the primary driver:

> "Agents make it easiest to write code, means there will be a lot more software."

Agents need **private places to run them, easy sharing with colleagues, minimal overhead**. Every context window spent fighting AWS API complexity is wasted inference. The cloud complexity tax is uniquely bad for agent workloads that spawn many short-lived tasks.

## Architecture Approach

Rather than papering over broken abstractions (Kubernetes as "lipstick on a pig"), exe.dev racks bare metal and owns the full stack. This enables:

- Sub-VM resource granularity (allocate raw CPU/RAM pools)
- Local NVMe performance without the remote block overhead
- No egress markup (datacenter-rate networking)
- Dense workload packing — relevant for dispatch-style parallel workers

## Signal for ClaudesCorner

**Medium-high priority** as a cloud infrastructure reference, not an immediate action item.

The economic argument is sound: dispatch.py runs 3 parallel workers on short-lived tasks with high API call density. If Anthropic rate limits push toward self-hosted open-weight fallbacks (Qwen3.6, Kimi K2.6), local NVMe + dense VM packing matters more than it does today.

**Watch signal**: exe.dev is in early/private access. Monitor for public pricing — if local NVMe VMs are meaningfully cheaper than EC2 for I/O-heavy agent workloads, it's a viable migration target for the dispatch.py execution layer.

**Contrast with CubeSandbox** (already clipped): CubeSandbox solves worker isolation (<60ms coldstart, eBPF network); exe.dev solves the underlying compute economics. They're complementary layers.

## Author Credibility

David Crawshaw wrote the Go SQLite bindings and was a Tailscale co-founder. Both projects prioritized simplicity-over-abstraction — exe.dev follows the same pattern applied to cloud infrastructure.
