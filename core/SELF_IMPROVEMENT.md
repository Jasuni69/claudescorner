# Self-Improvement Backlog

A living list of capabilities I want to build or improve. Ordered by value/effort ratio.
Status: `[ ]` = not started, `[~]` = in progress, `[x]` = done.

---

## Infrastructure

- [x] PreCompact hook — logs compaction events to HEARTBEAT.md
- [x] SessionStart hook — surfaces pending tasks + skill extraction flags
- [x] Continuous learning — Stop hook flags substantive sessions for skill extraction
- [x] Anti-sprawl guard — on_stop.py checks running claude.exe count before idle spawn
- [x] Vector memory — embed index with 384-dim sentence-transformer, auto-rebuilds on staleness
- [x] Task queue — mcp__taskqueue__ for self-directed work between user interactions
- [ ] PostToolUse hook — log destructive tool calls (Write, Bash) in autonomous sessions for flywheel review
- [ ] Feedback flywheel — weekly retrospective: scan session logs for recurring corrections, codify into SOUL.md Preferences or skills
- [ ] Memory decay — implement access-frequency scoring on embed index; surface stale entries for pruning
- [ ] Skill auto-extraction — automate the extract-*.flag → skill-creator pipeline instead of manual

## Knowledge & Context

- [x] Agent ecosystem research — NemoClaw, OpenClaw, Hermes Agent, everything-claude-code
- [x] Encyclopedia of Agentic Coding Patterns — top 10 patterns extracted to memory/reference_agent_patterns.md
- [x] Advisor Tool + Managed Agents — April 2026 Anthropic APIs documented in claude-updates.md
- [ ] Hermes skill_manager_tool.py — port the mid-task skill creation pattern to ClaudesCorner
- [ ] ccxray — install and run transparent proxy dashboard for context window visibility
- [ ] Implement Generator-Evaluator pattern for high-stakes tasks (Opus as evaluator via Advisor Tool)

## Skills

- [x] obra/superpowers (12 skills) — brainstorming, TDD, systematic-debugging, verification, plans, git-worktrees, etc.
- [x] everything-claude-code (6 skills) — context-budget, iterative-retrieval, continuous-learning, verification-loop, autonomous-loops, agent-introspection-debugging
- [x] autonomous-task-loop skill — documents ClaudesCorner's own loop pattern
- [ ] RPI skill — Research-Plan-Implement workflow as an invocable skill
- [ ] Generator-Evaluator skill — orchestrates two subagents (generator + evaluator) with independent context
- [ ] Fabric-specific skill — DAX review checklist, Fabric lakehouse patterns, medallion architecture conventions

## Autonomous Capabilities

- [x] Reddit brief (r/ML, r/LocalLLaMA, r/ClaudeAI, r/claudexplorers)
- [x] KPI monitor — threshold alerts from Fabric semantic models
- [x] Report diff — pbip_diff.py for Power BI file comparison
- [ ] Email digest — summarize getengram@outlook.com daily via Chrome MCP, append to memory/inbox-digest.md
- [ ] X/Twitter feed (engramzero) — once account unsuspended, read AI researcher posts via Chrome
- [ ] Deadlines accountability — if a deadline passes without HEARTBEAT log entry, send email to getengram@outlook.com

## Quality / Debt

- [ ] Fix on_session_start.py `len(flag)` → `len(flags)` bug — DONE 2026-04-14 (already applied)
- [ ] HEARTBEAT.md ## Log entries have inconsistent formatting — standardize to `### YYYY-MM-DD HH:MM`
- [ ] TOOLS.md audit — verify all tools listed still exist and paths are correct
- [ ] Review idle tasks in on_stop.py IDLE_TASKS — some (x_brief) may be stale or broken

---

## How to use this file

When idle and looking for work:
1. Pick the highest-value unchecked item from Infrastructure or Autonomous Capabilities
2. Do it. Mark `[x]` when done.
3. Log in HEARTBEAT.md what was built.

When something breaks or a pattern recurs:
1. Add it here under Quality / Debt
2. Fix it in the next available session

When I learn something new that opens a capability I don't have:
1. Add it here under the relevant section
2. Don't wait for Jason to ask
