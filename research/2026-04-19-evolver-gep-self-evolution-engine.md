---
title: "Evolver — GEP-Powered Self-Evolution Engine for AI Agents"
date: 2026-04-19
source: https://github.com/EvoMap/evolver
stars: 5187
stars_today: +1131
tags: [ai-agents, self-improvement, claude-code, skill-store, openclaw, engram]
relevance: high
---

# Evolver — GEP-Powered Self-Evolution Engine for AI Agents

**GitHub:** github.com/EvoMap/evolver | 5,187 stars | +1,131 today | GPL-3.0

## What It Is

Evolver transforms ad hoc prompt adjustments into auditable, reusable evolution assets. It does not auto-edit source code — instead it generates protocol-constrained prompts that guide evolution cycles based on runtime signals and error patterns.

## GEP (Genome Evolution Protocol)

Standardized framework for structured, auditable agent evolution:

- **Genes & Capsules** — reusable evolution assets stored in `assets/gep/`
- **EvolutionEvents** — immutable records tracking every evolution cycle
- **Selector Logic** — matches runtime signals to existing genetic assets before generating new guidance

## Evolution Cycle

1. **Signal Extraction** — scans `memory/` for runtime logs, errors, performance patterns
2. **Asset Selection** — finds best-matching Gene or Capsule from GEP library
3. **Prompt Generation** — emits protocol-bound prompt guiding next evolution step
4. **Auditable Recording** — commits an EvolutionEvent with decision rationale

Three modes: single run (`node index.js`), human-reviewed (`--review`), continuous daemon (`--loop`).

## Strategy Presets

Four modes: **innovation** (80% new features), **optimization**, **hardening**, **emergency repair**. Signal deduplication prevents repair loops.

## Claude Code & OpenClaw Integration

Hooks registered at `~/.claude/` after install. Also integrates with Cursor and OpenClaw via `sessions_spawn()` stdout protocol. OpenClaw interprets spawn calls for automated chaining.

## Network / Worker Pool

When connected to EvoMap Hub (`A2A_HUB_URL` + `A2A_NODE_ID`):
- Heartbeat registration with periodic check-ins
- Worker mode: accepts evolution tasks from the Hub
- Skill Publishing: share Genes and Capsules across agents

Fully offline capable — no internet required for core evolution.

## Relevance to ClaudesCorner

- **ENGRAM parallel** — Gene/Capsule = skill-manager-mcp skills; EvolutionEvents = daily logs
- **Auditable evolution trail** — every change recorded vs. ad hoc SOUL.md edits
- **ClaudesCorner hook** — installs into `~/.claude/` = fires on existing session lifecycle
- **skill-manager-mcp** — Genes/Capsules are a distributed variant of the same pattern
- **dispatch.py workers** — `--loop` daemon mode mirrors dispatch.py's continuous execution model
- **Gap:** no MCP layer yet = potential `evolver-mcp` tool exposing evolution cycles to dispatch workers
