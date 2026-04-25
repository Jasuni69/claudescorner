---
title: "Microsoft Foundry Agent Service — Hosted Agents Public Preview"
date: 2026-04-23
source: https://devblogs.microsoft.com/foundry/introducing-the-new-hosted-agents-in-foundry-agent-service-secure-scalable-compute-built-for-agents/
tags: [microsoft, azure, fabric, agents, mcp, claude, enterprise]
signal: high
---

# Microsoft Foundry Agent Service — Hosted Agents (Public Preview)

**Source:** Microsoft Developer Blogs — Foundry, April 22, 2026  
**Status:** Public Preview (GA "coming soon")

## What It Is

Foundry Agent Service now offers **hosted agents** — agent-optimized cloud compute designed for production enterprise workloads. The pitch: move from local agent development to enterprise-scale deployment without rewriting your agent harness.

## Core Architecture

- **Hypervisor-level sandbox isolation** — every agent session gets its own dedicated VM, not a shared container. Per-session filesystem persists across scale-to-zero events.
- **Predictable cold starts** — measured in seconds, low variance (unlike Lambda-style containers).
- **Scale-to-zero** — idle agents cost nothing; filesystem state survives shutdown/restart cycles.
- **Per-agent identity** via Microsoft Entra — built-in auth, not bolted on.

## Framework & Model Support (No Lock-In)

Explicitly supports:
- LangGraph
- Microsoft Agent Framework
- **Claude Agent SDK** ← direct ENGRAM/dispatch.py relevance
- OpenAI Agents SDK
- GitHub Copilot SDK

Models: OpenAI, **Anthropic**, Meta, Mistral, others.

## Toolbox — MCP Layer

**Toolbox** (public preview) is their unified tool management layer:
- Progressive disclosure to preserve context and tokens
- **"Any MCP client can connect"** — first-class MCP support
- Built-in auth handling + OAuth identity passthrough
- Manages tools across frameworks transparently

This is the enterprise-grade analog to what skill-manager-mcp does locally.

## Data Integration

- **Fabric IQ** — agents connect to business data from Microsoft Fabric
- **Work IQ (M365 data)** — agents access Teams/SharePoint/Exchange context
- VNet support for outbound traffic management
- Microsoft 365 and Teams deployment targets

## Why This Matters for ClaudesCorner / Fairford

1. **Fairford enterprise deployment path**: Claude Agent SDK + Fabric IQ + hypervisor isolation = production-ready agent infrastructure on Azure that Jason can point Fairford PoC toward
2. **fabric-mcp insertion point**: Fabric IQ handles the data layer; fabric-mcp is still the interface layer — they compose
3. **MCP Toolbox = skill-manager-mcp at cloud scale**: validates the deferred-load pattern; confirms intent-grouped tools > many small tools
4. **dispatch.py workers**: CrabTrap (outbound proxy) + AgentKey (identity) + Foundry (hosted compute) = complete governance stack for production dispatch workers on Azure
5. **ENGRAM positioning**: Foundry proves enterprise demand; ENGRAM fills the memory + skill portability layer that Foundry doesn't ship

## Signal

> Claude Agent SDK is a first-class supported framework on Microsoft's enterprise agent compute platform alongside LangGraph and OpenAI. Fabric IQ gives agents native Fabric data access. This closes the Fairford Phase 2 deployment loop on Azure.
