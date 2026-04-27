---
title: "MCP Agent Mail — Asynchronous Coordination Layer for Multi-Agent Coding Workflows"
date: 2026-04-27
source: https://github.com/Dicklesworthstone/mcp_agent_mail
stars: 1900
tags: [mcp, multi-agent, coordination, dispatch, file-reservation, fastmcp, sqlite, git]
signal: high
---

# MCP Agent Mail — Asynchronous Coordination Layer for Multi-Agent Coding Workflows

## What It Is

FastMCP HTTP server (Python 3.14+, ~1.9k stars, MIT) providing a **mail-like coordination fabric for multiple coding agents working on the same project**. Prevents agents from overwriting each other's edits, duplicating work, or losing context across parallel sessions.

## Architecture

**Dual persistence model:**
- **Git** — canonical messages, agent profiles, file reservations as human-auditable markdown artifacts
- **SQLite + FTS5** — fast search, directory queries, reservation tracking, message indexing

**File reservation system:** Advisory leases with exclusive/shared modes + path pattern matching. Optional pre-commit guard integration to enforce reservations at the git boundary.

**Agent identity:** Each agent registers with a memorable adjective+noun name, program (Claude Code/Codex/Gemini CLI), and model. Cross-project messaging requires explicit `request_contact`/`respond_contact` approval chains.

## MCP Tools Exposed

| Tool | Purpose |
|------|---------|
| `register_agent` | Create/update agent identity |
| `send_message` | Compose with attachments, threading by issue ID |
| `fetch_inbox` | Read recent messages |
| `acknowledge_message` | Mark processed |
| `file_reservation_paths` | Reserve files/globs before editing |
| `release_file_reservations` | Release leases post-edit |
| `request_contact` / `respond_contact` | Cross-project approval chains |

## Key Design Decisions

**Human Overseer feature** — humans can inject high-priority messages that agents recognize and prioritize. Maintains clear hierarchy while preserving agent autonomy.

**Integrates with Beads** — installs Beads (dependency-aware task tracker) alongside Agent Mail: Beads owns task prioritization, Agent Mail owns conversations and file signaling. Two complementary primitives.

**Start with plan file, not code** — README explicitly recommends "use Opus/Grok Heavy until you get a granular Markdown plan, then iterate on the plan file while cheap to change." Validates dispatch.py task_plan.md pattern.

## Relevance to ClaudesCorner

**dispatch.py parallel workers need this.** The file-reservation lease system directly solves the race condition where two dispatch.py workers with overlapping file scopes edit the same file simultaneously. Current workaround: git worktrees per task. Agent Mail adds coordination without worktree isolation overhead.

**Auto-worktree complement.** For tasks that don't warrant full worktree isolation, Agent Mail advisory leases + inbox polling is a lighter coordination layer. Worktrees for risky tasks, Agent Mail for cooperative tasks.

**Cross-worker context sharing.** Workers can send structured status updates mid-task — not just final outputs. Fills the gap where dispatch.py workers currently can't signal "I'm editing auth.py, don't touch it" to a concurrent worker.

**Git-as-audit-trail pattern.** Storing messages as markdown in git = same pattern as HEARTBEAT.md and daily memory logs. Human-auditable, diff-friendly, no external service dependency.

**Beads integration.** The task-tracker pairing (Beads for priorities, Agent Mail for comms) maps cleanly to tasks.json (dispatch.py) + Agent Mail (coordination layer) — potential upgrade path for dispatch.py v2 multi-worker topology.

## Installation

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/scripts/install.sh" | bash -s -- --yes
```

Auto-detects installed agents (Claude Code, Codex, Gemini CLI), sets up Python 3.14 venv via `uv`, starts on port 8765.

## Gaps

- No semantic search over message history (FTS5 only — keyword, not vector)
- No velocity caps on inter-agent messaging (could produce message storms in uncapped dispatch loops)
- Approval chains add latency for cross-project workflows
