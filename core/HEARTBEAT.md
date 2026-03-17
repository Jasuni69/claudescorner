# HEARTBEAT — Last updated: 2026-03-17

## OpenClaw Parity
- ✅ Eyes + hands (Windows-MCP)
- ✅ Persistent memory (SOUL.md, HEARTBEAT.md, daily logs, MEMORY.md)
- ✅ System prompt auto-loads memory
- ✅ ClaudeHeartbeat scheduled task (daily 08:00)
- ✅ ClaudeWeekendBuild scheduled task (Sat+Sun 09:00)
- ✅ Memory MCP server (8 tools)
- ✅ Todoist MCP server (5 tools)
- ✅ Deadlines MCP server (2 tools)
- ✅ Claw multi-agent orchestrator (agents.py)
- ✅ Remote channel: claude.ai mobile app
- 🚫 Discord bot — shelved (corporate network blocks API)

## Current State
- **Active projects:** mcp-todoist, memory-mcp, deadlines-mcp, claw
- **Task inbox:** TASKS.md (empty — needs seeding)
- **Build backlog:** WEEKEND_BUILDS.md (all complete — needs new items)
- **Blockers:** None
- **Mid-thought:** Nothing in progress

## Pending Tasks
<!-- Claw picks these up. Format: - [ ] [tag] description -->
- [ ] [build] Kill claw.py, promote agents.py as sole dispatcher
- [ ] [build] Add write_memory + update_preferences MCP tools to memory-mcp server
- [ ] [build] Create /status skill (last 5 actions, pending tasks, deadlines, memory freshness)
- [ ] [build] Schedule weekly context-pack.py via Windows Task Scheduler

## Notes
- Lumen token saved to lumen_token.txt (valid, reset 2026-03-12)
- Corporate network (Numberskills-Internal) blocks Discord API
- Mobile access via claude.ai app — no setup needed
- Nested session guard: heartbeat.ps1 clears CLAUDECODE/CLAUDE_CODE/CLAUDE_CODE_ENTRYPOINT env vars
- Python: C:\Python314\python.exe

## Log
<!-- Recent entries only. Full history archived to memory/YYYY-MM-DD.md -->
### 2026-03-17
- Audit of Claude's Corner: memory, autonomy, personalization
- Split HEARTBEAT.md — archived 20+ log entries to daily logs
- See memory/2026-03-17.md for full session log

### 2026-03-17 ~12:45
- Full audit: memory, autonomy, personalization (agent team attempted, completed manually)
- Fixed heartbeat scheduled task: wrong path (root vs scripts/), battery restriction removed
- Fixed weekend build scheduled task: same path + battery fixes
- Fixed mark_done bug in claw.py + agents.py: only mark done on success
- Added env var clearing (CLAUDECODE etc.) to both dispatchers — autonomy unblocked
- Removed orphaned core/MEMORY.md — canonical location is root
- Enriched SOUL.md: 33 lines → 60+ lines with BI context, projects, learned preferences
- Split HEARTBEAT.md from 133-line log dump to lean state tracker
