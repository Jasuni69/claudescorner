---
title: "exe.dev — Agent-Native Cloud Infrastructure (crawshaw.io)"
date: 2026-04-23
source: https://crawshaw.io/blog/building-a-cloud
hn_url: https://news.ycombinator.com/item?id=building-a-cloud
hn_points: 803
tags: [infrastructure, agents, cloud, compute, dispatch]
---

# exe.dev — Agent-Native Cloud Infrastructure

**Author:** David Crawshaw (founder, exe.dev) · HN 803pts · April 22, 2026

## What It Is

`exe.dev` is a new cloud platform explicitly designed around the observation that AI agents are the primary future consumers of compute. Crawshaw argues that existing clouds (AWS/GCP/Azure) were designed for human-operated VMs, and that their abstractions waste agent "context window" on API complexity rather than problem-solving.

## Technical Differentiators

| Feature | Traditional Cloud | exe.dev |
|---|---|---|
| Resource model | One VM = one CPU+memory bundle | CPU and memory provisioned independently; multiple VMs per instance |
| Storage | Remote block device (10× IOPS overhead) | Local NVMe with async off-machine replication |
| Networking | Egress pricing "10× datacenter rack cost" | Built-in TLS + auth proxies; anycast global network |
| Regional routing | Manual multi-region config | Automatic machine placement optimization |

## Agent-Specific Motivation

Direct quote from the post: agents struggle with "fundamental limits of the abstractions" in current clouds, wasting "context window" on cloud API contortions. The platform targets the explosion in *volume* of software that agents will generate — more deployable units, shorter lifetimes, tighter resource utilization requirements.

No explicit MCP integration or agent-specific APIs mentioned. This is infrastructure-layer, not agent-framework-layer.

## Status

Live at exe.dev as of April 22, 2026. No pricing disclosed. Early-access stage.

## Signal for ClaudesCorner

**Validates dispatch.py short-parallel architecture**: Crawshaw's framing — "agents need better traditional abstractions, not agent-specific ones" — directly supports ClaudesCorner's approach of composing short parallel Claude API calls rather than a monolithic long-running agent.

**Future dispatch.py isolation**: If CubeSandbox (TencentCloud KVM microVMs) or smolvm (Linux VMs) require Linux hosts, exe.dev's flexible VM model + local NVMe could become a deployment target for dispatch.py worker isolation in a production setting.

**Compute cost trajectory**: Crawshaw explicitly calls out egress pricing as "10× what you pay racking a server in a normal data center" — reinforces the case for self-hosted inference (LM Studio/Llama.cpp via free-claude-code proxy) for high-volume Haiku-tier dispatch work.

**Comparison to Microsoft Foundry Hosted Agents**: Foundry gives hypervisor-isolated per-session VMs within Azure ecosystem (enterprise, managed). exe.dev is indie/startup-tier with more flexible resource model but no enterprise SLA. For Fairford Phase 2, Foundry remains primary; exe.dev is a cost-optimization alternative worth monitoring.
