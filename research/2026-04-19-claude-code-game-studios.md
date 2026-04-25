---
title: "Claude Code Game Studios — 49-agent studio template"
date: 2026-04-19
source: https://github.com/Donchitos/Claude-Code-Game-Studios
stars: 13200
stars_today: 698
tags: [claude-code, multi-agent, skills, hooks, architecture]
relevance: high
---

# Claude Code Game Studios

**Repo:** github.com/Donchitos/Claude-Code-Game-Studios  
**Stars:** 13.2k (+698 today) | **License:** MIT

## What It Is

Open-source Claude Code template that turns a single session into a structured 3-tier agent studio: 49 agents, 72 slash-command skills, 12 automated hooks, 11 path-scoped coding rules. Built for game dev but the architecture is pure multi-agent coordination pattern.

## Architecture

- **Tier 1 — Directors** (Claude Opus): Creative, Technical, Producer. Set direction, don't write code.
- **Tier 2 — Department Leads** (Claude Sonnet): Game Design, Programming, Art, Audio, Narrative, QA, Production. Own domain decisions.
- **Tier 3 — Specialists** (30+ agents): Gameplay, engine, UI, world-building, testing, analytics. Execute within scoped paths.

Vertical delegation flows director→lead→specialist. Horizontal consultation allowed same-tier; no cross-domain binding decisions.

## 72 Skills by Phase

Brainstorm → Design Docs → Architecture → Sprint Planning → Code Review → QA → Release Management. Each is a slash command that routes to the right tier automatically.

## 12 Safety Hooks

POSIX bash hooks validate every commit: gap detection, agent action audit, path-scoped standards enforcement. Rules are per-domain:
- Gameplay code: data-driven values only
- Core engine: zero allocations in hot paths
- Test code: fixture patterns enforced

## Relevance to ClaudesCorner

**Direct pattern match** for dispatch.py architecture:
- Tier model mirrors research/infrastructure/skill/memory worker categories
- Path-scoped rules = dispatch.py `--category` flag logic
- Hooks-as-safety-layer pattern applicable to every dispatch worker
- 72 skills = validation that skill proliferation at scale is manageable with slash-command routing
- "Collaborative not autonomous" framing: agents present options with pros/cons, user approves finals — matches human-in-loop gap identified in dispatch workers

**ENGRAM bootstrap opportunity**: the 3-tier + hooks + scoped-rules structure is a portable agent harness. Could be stripped of game-dev specifics and repackaged as generic multi-agent CLAUDE.md template.

## Gaps / Watch Points

- Collaborative (not autonomous) by design — doesn't run headless; not a dispatch.py replacement
- No MCP integration yet — skills are slash commands, not MCP tools
- Windows 10 + Git Bash tested; ClaudesCorner stack compatible
