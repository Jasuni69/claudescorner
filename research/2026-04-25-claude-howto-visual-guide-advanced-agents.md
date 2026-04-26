---
title: "claude-howto — Visual guide to Claude Code advanced agents, 28.8k stars"
date: 2026-04-25
source: https://github.com/luongnv89/claude-howto
tags: [claude-code, hooks, subagents, mcp, multi-agent, templates, reference]
stars: 28795
today_gain: +242
license: MIT
relevance: dispatch.py, ENGRAM, hooks, subagents
---

# claude-howto — Visual Claude Code Guide

**GitHub:** https://github.com/luongnv89/claude-howto
**Stars:** 28.8k (+242 today) | **License:** MIT | **Updated:** April 24, 2026
**Compatible with:** Claude Code v2.1.119, Claude Sonnet 4.6+

## What It Is

Visual, example-driven guide to Claude Code spanning basics to advanced multi-agent patterns, with 15+ copy-paste templates. Updated yesterday — current with v2.1.116+ fixes.

## 10 Modules Covered

1. Slash Commands — user-invoked shortcuts
2. Memory — persistent cross-session CLAUDE.md hierarchy (project/directory/personal)
3. Skills — reusable auto-invoked capabilities
4. **Subagents** — specialized AI assistants with isolated contexts
5. **MCP Protocol** — external tool and API access
6. **Hooks** — event-driven automation (**28 events across 5 hook types**)
7. Plugins — bundled feature collections
8. Checkpoints — session snapshots and rewind
9. Advanced Features — planning mode, extended thinking, background tasks
10. CLI Reference

## High-Signal Details

### Hooks — 28 events, 5 types
Documented comprehensively here; the 28-event count is the most complete public reference for Claude Code hook surface area. Current `on_stop.py` in dispatch.py only covers Stop + PostToolUse. Cross-reference this to find missed hook opportunities (PreToolUse, UserPromptSubmit, PreCompact).

### Subagents
Templates for specialized subagents: code review, testing, documentation, security analysis — each with isolated context. Pattern matches dispatch.py worker roles but implemented as Claude Code subagents rather than API workers. Useful for hybrid dispatch: local subagents + API workers.

### Multi-Agent Workflow Templates
15+ copy-paste templates including:
- Code-review skill
- Subagent definitions
- Hook scripts
- MCP configurations
- PR review, DevOps, documentation pipeline plugins

### CLAUDE.md Hierarchy
Documents 3-level memory architecture (personal → project → directory) with merge semantics — validates HEARTBEAT.md placement + per-project SOUL.md boundary.

## Relevance to ClaudesCorner

1. **28 hook events** — audit `on_stop.py` and dispatch.py worker hooks against this list; likely missing PreToolUse + UserPromptSubmit hooks for token-burn telemetry
2. **Subagent templates** — copy-paste starting points for ENGRAM worker role definitions; isolated context pattern = SOUL.md boundary per agent
3. **MCP config templates** — ready-made `.mcp.json` patterns for common integrations (GitHub, databases); compare against current `settings.json` for gaps
4. **Checkpoint module** — session rewind capability not yet used in dispatch.py; relevant for long-horizon worker recovery on context exhaustion
5. **Reference resource for ENGRAM docs** — 28.8k stars + MIT + current = citable community reference for ENGRAM README agent patterns
