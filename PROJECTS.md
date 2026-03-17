# PROJECTS.md — Project Registry

One-liner per project. Update status when things change.

| Project | Status | What it does | Key files |
|---------|--------|--------------|-----------|
| `claw` | ✅ operational | Autonomous task runner + multi-agent orchestrator | `projects/claw/claw.py`, `projects/claw/agents.py` |
| `memory-mcp` | ✅ operational | MCP stdio server: 8 tools exposing SOUL/HEARTBEAT/MEMORY/search | `projects/memory-mcp/server.py` |
| `mcp-todoist` | ✅ operational | MCP server: Todoist task tools (5 tools, REST API v1) | `projects/mcp-todoist/` |
| `context-pack` | ✅ operational | Pre-compaction flush: generates MEMORY.md from all core files | `scripts/context-pack.py` |
| `session-summarizer` | ✅ operational | Distills heartbeat_run.log → memory/{date}.md | `scripts/session-summarizer.py` |
| `memory-indexer` | ✅ operational | TF-IDF keyword search over all .md files, builds .index.json | `scripts/memory-indexer.py` |

## Backlog
See `WEEKEND_BUILDS.md` for planned builds.

## Shelved
- Discord bot (`lumen_bot.ps1`) — corporate network blocks Discord API
