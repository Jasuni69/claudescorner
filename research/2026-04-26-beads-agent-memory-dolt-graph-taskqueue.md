---
title: "gastownhall/beads — Dolt-Backed Graph Task Queue as Persistent Agent Memory"
date: 2026-04-26
source: https://github.com/gastownhall/beads
tags: [ai-agents, memory, task-queue, multi-agent, claude-code, dispatch, dolt]
stars: 21433
stars_today: 133
license: MIT
relevance: high
---

# gastownhall/beads — Persistent Graph Memory for Coding Agents

**21,433 stars | +133 today | MIT | Go**

## What It Is

Distributed graph issue tracker designed as persistent structured memory for coding agents. Replaces markdown task lists with a dependency-aware graph stored in [Dolt](https://github.com/dolthub/dolt) — a version-controlled SQL database with cell-level merge, native branching, and remote sync.

## Architecture

**Storage backends:**
- **Embedded mode (default)**: Dolt in-process, data in `.beads/embeddeddolt/`, file-locked single-writer
- **Server mode**: External `dolt sql-server` for multi-concurrent-writer (multi-agent) scenarios

**Memory model:**
- Hash-based IDs (`bd-a1b2`) prevent merge collisions across concurrent agents
- Hierarchical: epics → tasks (`.1`) → sub-tasks (`.1.1`)
- Dependency graph: `relates_to`, `duplicates`, `supersedes`, `replies_to` link types
- **Semantic compaction ("memory decay")**: summarizes closed tasks to conserve context window
- Ephemeral messaging: threaded message-type issues with delegation

**Agent-optimized CLI:**
```bash
bd ready      # list unblocked tasks (dependency-aware)
bd claim      # atomically claim a task (multi-agent safe)
bd dep add    # link task dependencies
bd show       # display task with full audit trail
```

**Claude integration**: `.claude-plugin` and `.claude/` directories present; Claude Code workflow guides included.

**Install:**
```bash
brew install beads
npm install -g @beads/bd
```

Works on macOS, Linux, Windows, FreeBSD. Git-free via `BEADS_DIR` env var + `--stealth` flag.

## Signal for Jason's Stack

**dispatch.py task queue upgrade**: `tasks.json` is a flat JSON file with no dependency tracking, no atomic claiming, and no multi-agent collision safety. Beads' Dolt backend gives exactly what dispatch.py workers need for coordination: `bd claim` is atomic (no two workers grab the same task), `bd ready` filters to unblocked tasks only (respects dependency graph), and `dolt diff` gives full audit of what changed per task. This is a structural upgrade to the tasks.json polling loop.

**Memory decay = HEARTBEAT.md compaction**: Beads automatically summarizes closed tasks to shrink context. This is the "memory compression on completion" pattern that HEARTBEAT.md does manually — semantic compaction is the automated version. Relevant for long dispatch.py runs where completed task context bloats worker prompts.

**Multi-writer server mode**: With 3 parallel dispatch.py workers, the embedded single-writer mode would serialize on file locks. Server mode (`dolt sql-server`) removes that bottleneck — each worker connects independently without a coordinator.

**ENGRAM parallel**: Beads is specifically scoped to task/issue graph memory (what HEARTBEAT.md does), not semantic/episodic memory (what memory-mcp does). The two are complementary: beads = structured task state, memory-mcp = semantic knowledge. Stack them: beads manages what needs doing, memory-mcp stores what was learned.

**Dolt branching**: Git-style branching for task state means dispatch.py can branch the task graph before a risky operation and merge back on success — same pattern as auto-worktree for code, applied to task state.

## Caution

- Dolt adds a dependency not currently in the stack; evaluate binary size and Windows install friction
- Embedded mode single-writer lock may serialize workers unless server mode is configured
- Go binary: no Python SDK — dispatch.py would shell out to `bd` CLI or use Dolt SQL directly
- Stars (21k) may be inflated vs actual production usage — verify issue tracker activity

## Action Items

- [ ] Test `bd claim` atomicity with 3 concurrent processes on Windows 11
- [ ] Benchmark Dolt server mode overhead vs tasks.json polling loop latency
- [ ] Prototype replacing tasks.json with beads for dispatch.py tier-1 research tasks
- [ ] Evaluate `memory decay` compaction output quality as HEARTBEAT.md summary replacement
