---
title: "Marmelab — Claude Code Tips I Wish I'd Had from Day One (Apr 2026)"
date: 2026-04-25
source: https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html
hn_points: ~5 (fresh)
tags: [claude-code, workflows, hooks, dispatch-py, doom-loop, ENGRAM, cost, oversight]
relevance: dispatch.py worker oversight, CLAUDE.md hygiene, session retrospectives
---

# Marmelab — Claude Code Tips Day One

**Source:** https://marmelab.com/blog/2026/04/24/claude-code-tips-i-wish-id-had-from-day-one.html  
**Posted:** 2026-04-24 | **Author:** Marmelab engineering team

## Key Signal

> *"The human bottleneck was a feature, not a bug. At human pace, errors compound slowly and pain forces early correction. With an army of agents, small mistakes compound at a rate that outruns your ability to catch them."*

This is the clearest articulation of why dispatch.py needs doom-loop detection + verify oracles, not just quality agents. Error compounding at agent speed is the core risk — confirmed from production experience.

## Actionable Patterns

### Workflow Patterns

**Plan-before-code (confirmed):** Use plan mode for complex tasks to catch wrong assumptions before implementation starts. Maps directly to dispatch.py PLAN → BUILD → VERIFY tier sequence.

**Incremental steps:** One feature at a time, review before proceeding. Prevents bad context pollution. dispatch.py one-task-one-session-one-PR model = this pattern at scale (Affirm, clipped 2026-04-24c).

**Bug documentation pattern (new):** When Claude introduces a bug, don't just patch it — have Claude investigate, update CLAUDE.md/ADRs explaining what went wrong, *then* fix. Persistent institutional knowledge > one-shot fix. Maps to `feedback_flywheel.py` pattern + SELF_IMPROVEMENT.md.

**Session retrospectives:** Ask Claude at end of session to reflect on learnings → systematically organize into CLAUDE.md, skill files, ADRs. Automation target: wire this into `on_stop.py` PostStop hook.

**Pre-review cleanup:** Run `/simplify` + `/review` before human code review. Reduces noise in PRs. Both skills already in ClaudesCorner skill library.

### Context Management

- `/rewind` (ESC ESC) to last good state; `/clear` for full reset — prevents bad output polluting subsequent attempts
- `@` syntax for direct file reference in prompts (faster than describing paths)
- `!` to execute shell commands without asking Claude to run them
- Keep CLAUDE.md under **200 lines** — business context + domain knowledge only
- Create **AGENTS.md** alongside CLAUDE.md for cross-agent portability

### Tool Ecosystem (mentioned)

- **Context7 Plugin** — indexes library docs at specific versions; prevents hallucination of stale API signatures. Relevant for dispatch.py workers using third-party MCP tools.
- **RTK Tool** — filters and compresses command output to reduce token usage. dispatch.py worker prompt compression candidate.
- **Snyk MCP Server** — security scanning + dependency vuln checks. Fairford pre-deploy checklist.
- **Superpowers Skills** — TDD + subagent-driven development patterns (already in ClaudesCorner).

### Anti-Patterns (confirmed from practice)

- **Tool overload:** Too many tools = complexity without proportional benefit. Validates deferred-tool-load pattern (Anthropic MCP Production Guide, −85% tokens).
- **Context limits:** Beyond ~400k tokens, agent relevance degrades. dispatch.py MAX_CONTEXT_TOKENS=8000 ceiling is correct defensive floor.
- **Batch command risks:** `/batch` sacrifices debugging granularity when failures occur — hard to diagnose which step failed.
- **Worktree overhead:** Multiple parallel Claude sessions = context-switching + decision fatigue at human level. At agent level this compounds. Confirms dispatch.py 3-worker ceiling (pgrust/Conductor empirical cap, clipped 2026-04-23).

## Relevance to ClaudesCorner

**dispatch.py doom-loop detector:** "errors compound at agent speed" = quantitative argument for ml-intern's doom-loop pattern (injects corrective prompts on repeated tool patterns, clipped 2026-04-23). Add iteration cap + repeated-tool detection to dispatch.py worker loop.

**on_stop.py session retrospective hook:** Auto-trigger session retrospective at Stop event → append distilled insights to SELF_IMPROVEMENT.md. Currently `on_stop.py` does skill extraction + AutoDream gate — add retrospective step.

**CLAUDE.md 200-line limit:** Currently not enforced. Add line-count check to health-check/checks.py.

**AGENTS.md:** Not yet present in ClaudesCorner. Consider adding alongside CLAUDE.md for cross-agent portability (OpenClaw, Hermes, Codex compatibility).
