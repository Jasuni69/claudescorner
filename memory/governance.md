---
name: Memory Write Authority & Promotion Rules
description: Which agent roles can write to which memory stores, and how breadcrumbs get promoted to durable memory
type: project
---

# Memory Write Authority & Promotion Rules

## Memory Store Taxonomy

| Store | Path | Scope | Mutability |
|---|---|---|---|
| **Session breadcrumbs** | `logs/dispatch-*.txt` | Single session | Write-once, never edited |
| **Daily log** | `memory/YYYY-MM-DD.md` | One calendar day | Append-only |
| **HEARTBEAT** | `core/HEARTBEAT.md` | Rolling session state | Overwrite `## Log` section; update pending tasks |
| **MEMORY index** | `memory/MEMORY.md` | Cross-session index | Append entries; update stale entries |
| **Memory files** | `memory/*.md` | Durable facts | Overwrite to update; never delete without replacing |
| **SOUL** | `core/SOUL.md` | Identity & preferences | Append to `## Preferences I've Learned` only |
| **claude_memory.json** | `core/claude_memory.json` | Structured facts | Merge/upsert; no orphan keys |

---

## Agent Role Definitions

| Role | Description |
|---|---|
| **Interactive** | Claude responding to Jason in a live conversation |
| **Heartbeat** | Scheduled autonomous invocation (no Jason present) |
| **Dispatcher** | `dispatch.py` spawning task subprocesses |
| **Subagent** | Spawned via `Agent()` tool inside a session |
| **Skill** | Code invoked via `Skill()` tool |

---

## Write Authority Matrix

| Store | Interactive | Heartbeat | Dispatcher | Subagent | Skill |
|---|---|---|---|---|---|
| Session breadcrumbs (`logs/`) | Read | Read | **Write** | Read | Read |
| Daily log (`memory/YYYY-MM-DD.md`) | **Write** | **Write** | No | No | No |
| HEARTBEAT (`core/HEARTBEAT.md`) | **Write** | **Write** | No | No | No |
| MEMORY index (`memory/MEMORY.md`) | **Write** | **Write** | No | No | No |
| Memory files (`memory/*.md`) | **Write** | **Write** | No | No | No |
| SOUL (`core/SOUL.md`) | Append only | Append only | No | No | No |
| `claude_memory.json` | **Write** | **Write** | No | No | No |

**Rule: Dispatcher and Subagent roles cannot write to durable memory.** They operate in their own log scope. Any facts worth preserving must be bubbled up to the Interactive or Heartbeat agent that spawned them.

---

## Promotion Rules

### Breadcrumb → Daily Log
- **Who promotes:** Interactive or Heartbeat agent, at session end
- **What qualifies:** decisions made, files touched, things learned, errors hit and resolved
- **Format:** timestamped entry in `memory/YYYY-MM-DD.md`, append if file exists
- **Threshold:** anything non-obvious that would matter in a future session

### Daily Log → MEMORY.md (Durable)
- **Who promotes:** Interactive agent, when recognizing a pattern worth keeping cross-session
- **What qualifies:**
  - Recurring corrections or preferences (→ `feedback_*.md`)
  - Stable project facts that aren't in the code (→ `project_*.md`)
  - External resource locations (→ `reference_*.md`)
  - User role/skill/context updates (→ `user_*.md`)
- **What does NOT qualify:** task lists, in-progress state, debugging sessions, one-off facts
- **Process:** write `memory/<type>_<slug>.md` with frontmatter, then add index line to `MEMORY.md`

### Daily Log → SOUL.md
- **Who promotes:** Interactive agent only (Jason must be present or have implicitly ratified the change)
- **What qualifies:** confirmed preference changes, learned behavioral rules, corrections that apply globally
- **Where:** append to `## Preferences I've Learned` section only — never edit other sections without explicit instruction
- **Threshold:** must have been confirmed or validated in conversation, not inferred

### Subagent Output → Durable Memory
- **Process:** subagent writes findings to its `logs/dispatch-*.txt` breadcrumb OR returns output inline
- **Promoting agent:** the Interactive or Heartbeat agent that reads the subagent output decides whether to promote
- **Subagents never write to MEMORY.md, SOUL.md, or daily logs directly**

---

## Cross-Agent Handoff Protocol

When a Heartbeat or Dispatcher run wants to hand off state to the next session:

1. **Write to HEARTBEAT.md `## Log`** — timestamped summary of what ran
2. **Update pending tasks in HEARTBEAT.md** — add/remove as needed
3. **If a durable fact was discovered** — write `memory/<type>_<slug>.md` + update `MEMORY.md`
4. **Do NOT write to SOUL.md** — only Interactive sessions with Jason present may update SOUL

---

## Conflict Resolution

- If a subagent's breadcrumb contradicts a durable memory entry: **trust the durable entry** until Interactive agent can resolve
- If two sessions write conflicting daily log entries for the same date: **append both** with timestamps, resolve at next flush
- If a memory file is stale: **overwrite** the file, update the `MEMORY.md` index description, do not leave orphan entries

---

## Anti-Patterns (Never Do)

- Subagent writes directly to `MEMORY.md` or `SOUL.md`
- Dispatcher modifies daily logs
- Skill overwrites memory files
- Promoting ephemeral task state (what's pending right now) to durable memory
- Storing code patterns, file paths, or architecture in memory (derivable from code)
- Duplicate memory entries — always check index before creating new file
