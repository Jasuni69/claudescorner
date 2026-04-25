---
title: "Planning With Files — Persistent Markdown 3-File Pattern for AI Agents"
source: https://github.com/OthmanAdi/planning-with-files
date: 2026-04-22
tags: [claude-code, skills, agent-memory, dispatch, heartbeat, engram]
relevance: high
---

# Planning With Files — Persistent Markdown 3-File Pattern

**Repo**: OthmanAdi/planning-with-files · 19,279 stars · +119 today · GitHub Trending Python #4

## Core Problem

AI agents fail on complex tasks due to:
- Volatile memory — task tracking lost on context reset
- Goal drift — original objectives fade after many tool calls
- Hidden errors — failures not logged, causing repetition
- Context waste — everything crammed into limited context window

## The Solution: 3-File Persistent Memory

Every task gets three markdown files:

| File | Purpose |
|---|---|
| `task_plan.md` | Phases, goals, progress checkboxes |
| `findings.md` | Research, discoveries, insights |
| `progress.md` | Session log, test results, error tracking |

This externalizes agent working memory to disk — markdown as scratch pad + checkpoint store.

## Mechanism: IDE Hooks

The skill uses PreToolUse / PostToolUse / Stop hooks to:
- Re-read the plan before major decisions (prevents goal drift)
- Remind agent to update progress after file writes
- Log all errors for future reference
- Verify completion before stopping

## Session Recovery

When context fills and `/clear` runs, the skill extracts lost conversation data and generates a **catchup report** — prevents knowledge loss across context boundaries.

## Platform Support

17+ platforms: Claude Code (enhanced), Cursor, GitHub Copilot, Mastra Code, Gemini CLI, OpenClaw, Continue, Kilocode, AdaL CLI, BoxLite sandbox.

Entry points: `/plan`, `/planning` commands.

## Performance

- **96.7% pass rate** with skill vs **6.7% without**
- 3/3 blind A/B wins (100% preference)

## Relevance to ClaudesCorner

| ClaudesCorner pattern | Upgrade path |
|---|---|
| `core/HEARTBEAT.md` | Direct analog — HEARTBEAT is the `progress.md` file for the whole system |
| dispatch.py workers | Each worker could create task_plan/findings/progress triplet per job instead of relying on context alone |
| skill-manager-mcp | This is an installable Claude Code skill — validate against skill format and add to local registry |
| ENGRAM | 3-file pattern is a concrete, measurable implementation of the "working memory on disk" principle ENGRAM advocates |

**Key insight**: The 96.7% vs 6.7% delta quantifies exactly why HEARTBEAT.md / persistent planning state matters — it's not organizational preference, it's a 14× task completion multiplier.

## Action Items

- Add `task_plan.md` template to dispatch.py worker output — workers should write their plan before executing, not just execute
- Validate skill YAML frontmatter against skill-manager-mcp format; potentially install via `/plugin marketplace add OthmanAdi/planning-with-files`
- Consider adopting 3-file pattern for longer dispatch.py jobs (tier 2/3 tasks)
