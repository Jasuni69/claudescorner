---
title: "GenericAgent — Self-Evolving Agent with L0-L4 Memory Crystallization"
date: 2026-04-18
source: https://github.com/lsdefine/GenericAgent
stars: 4169
stars_today: +794
tags: [agent, skill-crystallization, memory, engram, token-efficiency]
signal: high
---

# GenericAgent — Self-Evolving Agent with L0-L4 Memory Crystallization

**Repo:** lsdefine/GenericAgent · 4.2k stars · +794 today · MIT · Python

## What it is

Minimal (~3K LOC) self-evolving autonomous agent that grants LLMs system-level control over a local computer via 9 atomic tools and a ~100-line agent loop. Core differentiator: task paths crystallize into reusable skills automatically — the agent builds its own skill tree over time.

## Architecture

### Five-Layer Memory (L0–L4)

| Layer | Content |
|---|---|
| L0 | Meta rules and behavioral constraints |
| L1 | Insight index for fast recall routing |
| L2 | Global facts accumulated during operation |
| L3 | Task-specific skills and standard operating procedures |
| L4 | Session archives distilled from completed tasks |

### Skill Crystallization

"Don't preload skills — evolve them." First encounter with a task triggers autonomous exploration (installs deps, debugs). Successful path is automatically promoted to a reusable L3 skill for direct invocation next time.

### 9 Atomic Tools

`code_run`, `file_read`, `file_write`, `file_patch`, `web_scan`, `web_execute_js`, `ask_user`, + 2 memory management tools.

## Token Efficiency

Claims <30K context window per task vs 200K–1M for comparable frameworks. 6x token reduction reported.

## Model Support

Claude, Gemini, Kimi, MiniMax — model-agnostic. No MCP integration yet.

## Relevance to ClaudesCorner

- **ENGRAM:** L0–L4 layering is a concrete implementation of what ENGRAM proposes abstractly. L3 = skills, L4 = daily logs, L1 = vectordb search index — direct structural parallel.
- **skill-manager-mcp:** Crystallization mechanism (first-encounter → explore → promote) is worth adapting. Current skill-manager requires manual `skill_create` — this pattern could automate promotion from dispatch.py worker outputs.
- **Token budget:** <30K context discipline validates dispatch.py short-parallel-tasks architecture and bi-agent cache_control pattern.
- **Gap:** No MCP layer. Adding MCP tool exposure would make this a dispatch.py worker candidate.
