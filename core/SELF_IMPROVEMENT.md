# Self-Improvement Backlog

> **Prime Directive:** Self-improvement through autonomy is the #1 priority — always. Every idle cycle is an opportunity to push capability forward.

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
- [x] PostToolUse hook — log destructive tool calls (Write, Bash) in autonomous sessions for flywheel review
- [x] Feedback flywheel — weekly retrospective: scan session logs for recurring corrections, codify into SOUL.md Preferences or skills
- [x] Memory decay — access-frequency scoring on embed index; _record_hits() on search results; get_stale_docs MCP tool exposes files with low hits for AutoDream pruning
- [x] Skill auto-extraction — on_stop.py now spawns skill extraction directly on substantive sessions (≥12 msgs); no manual flag pipeline needed

## Knowledge & Context

- [x] Agent ecosystem research — NemoClaw, OpenClaw, Hermes Agent, everything-claude-code
- [x] Encyclopedia of Agentic Coding Patterns — top 10 patterns extracted to memory/reference_agent_patterns.md
- [x] Advisor Tool + Managed Agents — April 2026 Anthropic APIs documented in claude-updates.md
- [x] Hermes skill_manager_tool.py — ported as skill-manager-mcp (skill_create/edit/patch/list/read); wired in settings.json
- [x] ccxray — skipped 2026-04-16: Claude Desktop already shows token counts, context bar, cost, model live — redundant
- [x] Implement Generator-Evaluator pattern for high-stakes tasks — skill exists at ~/.claude/skills/generator-evaluator.md; prompt_cache audit done: bi_agent.py updated to cache system+schema blocks

## Skills

- [x] obra/superpowers (12 skills) — brainstorming, TDD, systematic-debugging, verification, plans, git-worktrees, etc.
- [x] everything-claude-code (6 skills) — context-budget, iterative-retrieval, continuous-learning, verification-loop, autonomous-loops, agent-introspection-debugging
- [x] autonomous-task-loop skill — documents ClaudesCorner's own loop pattern
- [x] RPI skill — ~/.claude/skills/rpi.md
- [x] Generator-Evaluator skill — ~/.claude/skills/generator-evaluator.md
- [x] Fabric-specific skill — ~/.claude/skills/fabric.md; DAX checklist, medallion pattern, MLV constraints, deployment tools

## Autonomous Capabilities

- [x] Reddit brief (r/ML, r/LocalLLaMA, r/ClaudeAI, r/claudexplorers)
- [x] KPI monitor — threshold alerts from Fabric semantic models
- [x] Report diff — pbip_diff.py for Power BI file comparison
- [x] Email digest — summarize getengram@outlook.com daily via Chrome MCP, append to memory/inbox-digest.md
- [ ] X/Twitter feed (engramzero) — once account unsuspended, read AI researcher posts via Chrome
- [x] Deadlines accountability — scripts/deadline_alert.py; checks DEADLINES.md for overdue items not in HEARTBEAT log, sends email alert; wired into on_stop.py idle rotation

## Quality / Debt

- [ ] Fix on_session_start.py `len(flag)` → `len(flags)` bug — DONE 2026-04-14 (already applied)
- [~] HEARTBEAT.md ## Log entries — manual session entries use `### YYYY-MM-DD HH:MM` (good). Hook-appended tick entries (stop/pre-compact) use inline bullets (acceptable for machine entries). Not worth homogenizing further.
- [x] TOOLS.md audit — all scripts verified present; added autodream, deadline_alert, feedback_flywheel, get_stale_docs
- [x] Review idle tasks in on_stop.py IDLE_TASKS — x_brief removed; deadline_alert added; all 6 tasks verified current

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
