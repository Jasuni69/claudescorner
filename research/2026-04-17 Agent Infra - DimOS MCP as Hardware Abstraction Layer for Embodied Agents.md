---
title: "DimOS — MCP as Hardware Abstraction Layer for Embodied AI Agents"
date: 2026-04-17
source: https://github.com/dimensionalOS/dimos
tags: [mcp, agents, robotics, abstraction, patterns]
signal: medium
---

# DimOS — Agentic OS for Physical Hardware via MCP

**Repo:** dimensionalOS/dimos | ~2.9k stars, +137 today | Pre-release beta

## What It Is

Agentic operating system for controlling physical robots (humanoids, drones, quadrupeds) via natural language + Python. Agents issue high-level commands; DimOS exposes hardware capabilities as MCP tools.

## Key Architectural Pattern

**MCP as hardware abstraction layer** — robots expose skills (navigation, manipulation, perception) as MCP tools. Agents call `dimos mcp call <skill>` identically to how Claude Code calls any MCP tool. The physical/software boundary disappears from the agent's perspective.

```
Agent (LLM)
  → MCP tool call: "navigate to kitchen"
    → DimOS skill resolver
      → Motor controllers / SLAM / sensor fusion
```

## Relevant Patterns for Agent Infrastructure

1. **Blueprint system** — modules auto-connect by matching input/output types; no manual wiring. Analogous to typed tool schemas in MCP servers.
2. **Spatio-temporal memory** — object permanence and spatial recall across sessions. Different memory architecture than ENGRAM's text-graph; complements it.
3. **Stream-driven** — continuous sensor feeds flow through modules. Applicable to streaming financial data or real-time Fabric event streams.

## LLM Integration

- Ollama for local inference
- Claude-compatible via standard MCP interface
- Vision/multimodal: camera streams to VLMs for reasoning

## Why It Matters (Beyond Robotics)

The core insight: **MCP is a universal abstraction layer**, not just for software APIs. DimOS proves the pattern scales to hardware. For ClaudesCorner, this validates fabric-mcp's design — wrapping Fabric as MCP tools gives agents the same clean interface regardless of what's behind the tool boundary.

## Signal

Novel pattern, pre-release, small community. Track for MCP abstraction patterns rather than direct use.
