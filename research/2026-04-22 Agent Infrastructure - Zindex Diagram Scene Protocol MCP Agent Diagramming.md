---
title: "Zindex: Diagram Scene Protocol — MCP-Native Agent Diagramming Infrastructure"
date: 2026-04-22
source: https://zindex.ai
github: https://github.com/zindexai/zindex
hn_points: 16
tags: [mcp, agent-infrastructure, diagrams, protocol, visualization]
relevance: medium
---

# Zindex — Diagram Scene Protocol for Agents

**Zindex.ai | HN 16pts | MCP integration | PostgreSQL-backed**

## What It Is

Zindex is infrastructure for making diagrams a first-class durable artifact in agent workflows. Instead of agents generating disposable SVG/PNG blobs, Zindex manages diagrams as versioned, patchable state with semantic structure.

Core abstraction: the **Diagram Scene Protocol (DSP)** — a machine-readable format where agents declare *semantic elements* (nodes, edges, relationships) rather than specifying geometric positions. The layout engine computes positions and edge routing automatically.

## How It Works

Deterministic pipeline: **validate → normalize → layout → render**

- **17 operation types** for building/modifying scene graphs
- **40+ validation rules** — agents get structured errors, not layout corruption
- **Incremental patch-based updates** with stable element IDs (agents can modify without full regeneration)
- **Multiple output formats**: SVG and PNG, 4 themes
- **PostgreSQL-backed storage** with auth and rate limiting
- **MCP integration** — configurable as an MCP server for Claude Code / agent access

## Why This Matters vs. Raw LLM SVG Generation

LLMs generating raw SVG/Mermaid/Graphviz fail on complex layouts (overlapping nodes, inconsistent routing). DSP separates semantic intent from geometric computation — agents describe *what*, layout engine decides *where*.

This is the same separation of concerns as MCP (agents describe intent, tools execute) applied to visualization.

## Relevance to ClaudesCorner

| Scenario | Fit |
|----------|-----|
| dispatch.py pipeline visualization | ✅ DSP declares worker topology as semantic graph |
| fabric-mcp data flow diagrams | ✅ Nodes = Fabric artifacts, edges = data dependencies |
| ENGRAM memory graph visualization | Medium — Cognee already provides graph layer |
| BI-agent DAX query plan visualization | Low priority now |

**Primary value:** if any dispatch.py or fabric-mcp workflow needs diagram output as a durable, versioned artifact (e.g., pipeline audit trail, architecture docs), Zindex is the MCP-native layer to reach for rather than prompting raw SVG.

## Gaps / Watch Items

- Pricing and licensing not yet public — check GitHub before production use
- No agent runtime (just the diagram state layer) — needs a driver agent on top
- 16 HN pts suggests early stage; verify active maintenance before adopting

## Action

Low priority. Add to backlog: if fabric-mcp or dispatch.py ever needs diagram output, evaluate Zindex as DSP backend before rolling raw Mermaid generation. Check GitHub for license and maintenance cadence.
