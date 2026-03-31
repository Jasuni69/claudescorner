# Harness Build Log
<!-- Interrupt-safe progress log. Update after each feature. -->

## Goal
Improve the Claude Code harness using patterns from:
- **autoresearch** (karpathy): git-checkpoint loop, results TSV, stall detection, guide files
- **meta-harness** (stanford-iris-lab): context snapshot injection, completion gates, output truncation

## Build Order (ROI-ranked)
| # | Feature | Source | Status |
|---|---------|---------|--------|
| 1 | Context snapshot in `wait_for_task` default task | meta-harness | ✅ 2026-03-31 |
| 2 | Stall detection in taskqueue (N failures → strategy switch) | autoresearch | ✅ 2026-03-31 |
| 3 | `/experiment` skill — TSV log + git checkpoint loop | autoresearch | ✅ 2026-03-31 |
| 4 | Completion gates — checklist before marking done | meta-harness | ✅ 2026-03-31 |
| 5 | Output truncation guard in taskqueue | meta-harness | ✅ 2026-03-31 |

## Feature Notes

### Feature 1 — Context Snapshot
**What:** Instead of a bare "Read HEARTBEAT.md" idle task, inject a pre-built snapshot of:
- `git status` (project state)
- pending task count from task_queue.json
- memory freshness (age of today's daily log)
- current hour (for morning task flagging)

**Where:** `taskqueue-mcp/server.py` — `_default_tasks()` function. Add a snapshot-builder that runs once per idle cycle and prepends context to the default task string.

**Why:** Saves 2-5 turns per loop iteration. Agent starts with full situational awareness, not a blank slate.

**Files:** `projects/taskqueue-mcp/server.py`

---

### Feature 2 — Stall Detection
**What:** Track consecutive `discard`/`fail` results in `core/task_queue_state.json`. After N=5 stalls, auto-inject a "radical strategy" task into the queue.

**Where:** `taskqueue-mcp/server.py` — add `stall_count` to state. `push_task` with `status=fail` increments it; `status=keep` resets it.

**Why:** Mirrors autoresearch's insight: agents get stuck in local minima. A stall counter breaks the loop automatically.

**Files:** `projects/taskqueue-mcp/server.py`

---

### Feature 3 — `/experiment` Skill
**What:** Skill that scaffolds and runs an autonomous experiment loop:
- Creates `experiment_guide.md` (what's editable, what's frozen, metric definition)
- Creates `experiment_results.tsv` (commit | score | status | description)
- Runs loop: propose → git commit → evaluate → keep/reset → log → repeat

**Where:** `~/.claude/commands/experiment.md` (slash command skill)

**Why:** Direct port of autoresearch's core pattern. Enables autonomous code/config improvement.

**Files:** `C:\Users\JasonNicolini\.claude\commands\experiment.md`

---

### Feature 4 — Completion Gates
**What:** Checklist injected before any task marked complete:
- Did you update HEARTBEAT.md?
- Did you write/update the daily log?
- Did you log to MEMORY.md if durable fact learned?
- Does the output actually exist/work?

**Where:** idle_tasks.json — add a `completion_gate` idle task type. Also embed in `/memory-flush` skill.

**Why:** Meta-harness pattern. Prevents premature task completion and memory gaps.

**Files:** `core/idle_tasks.json`, skill update

---

### Feature 5 — Output Truncation
**What:** Cap tool/task output at 30KB before returning to LLM. Log truncation events to `logs/taskqueue.log`.

**Where:** `taskqueue-mcp/server.py` — wrap `call_tool` return values.

**Why:** Prevents context blowup on large outputs (ls -R, long logs, big files).

**Files:** `projects/taskqueue-mcp/server.py`

---

## Completed Features

### ✅ Feature 1 — Context Snapshot (2026-03-31)
`_build_context_snapshot()` in `taskqueue-mcp/server.py`. Prepends git status, queue depth, memory freshness, stall count, and morning flag to every idle task.

### ✅ Feature 2 — Stall Detection (2026-03-31)
`_increment_stall()` / `_reset_stall()` in `taskqueue-mcp/server.py`. `push_task(status="fail")` increments; `push_task(status="keep")` resets. At threshold 5, `_default_tasks()` injects a strategy-switch task.

### ✅ Feature 3 — /experiment Skill (2026-03-31)
`~/.claude/commands/experiment.md`. Subcommands: create, run, status, revert. Git-checkpoint loop with TSV logging. Integrates with taskqueue stall tracking.

### ✅ Feature 4 — Completion Gates (2026-03-31)
Checklist added to `memory-flush.md`. `completion_gate` idle task added to `idle_tasks.json` (cooldown 3600s).

### ✅ Feature 5 — Output Truncation (2026-03-31)
`_truncate()` in `taskqueue-mcp/server.py`. Caps at 30KB, logs truncation events to taskqueue.log.

## Interruption State
**Status: COMPLETE** — all 5 features built and logged.
**Resume command:** N/A — if resuming, check git log for what changed.
