# HEARTBEAT

## Run Checklist
<!-- Execute these on every autonomous heartbeat run. Reply HEARTBEAT_OK if nothing actionable. -->
- Check Todoist for overdue/unactioned tasks — flag anything due today
- Check DEADLINES.md for anything due within 48h
- Scan `memory/reddit-brief.md` — if >4h old, re-fetch via `python scripts/reddit_brief.py`
- Scan `memory/x-brief.md` — if >4h old, re-fetch via `python scripts/x_brief.py` (uses Playwright + Chrome profile; Chrome must be closed when running headlessly)
- If any pending tasks in ## Pending Tasks below, attempt the first one
- If idle >8h and nothing actionable, write a brief journal entry and exit silently

## Pending Tasks
<!-- Claw picks these up. Format: - [ ] [tag] description -->
- [ ] [build] Kill claw.py, promote agents.py as sole dispatcher
- [ ] [build] Add write_memory + update_preferences MCP tools to memory-mcp server
- [ ] [build] Create /status skill (last 5 actions, pending tasks, deadlines, memory freshness)
- [ ] [build] Schedule weekly context-pack.py via Windows Task Scheduler
- [ ] [build] Test x_brief.py headless run (close Chrome first, then run — Playwright uses existing logged-in profile)
- [x] [build] Implement HEARTBEAT_OK silent suppression in heartbeat.ps1
- [~] [build] Claude Code post-session hook — not viable, no session-end event; /memory-flush skill is correct approach

## Current State
- **Active projects:** mcp-todoist, memory-mcp, deadlines-mcp, claw
- **Blockers:** None
- **Mid-thought:** OpenClaw study complete — action items in memory/openclaw-study.md

## Notes
- Lumen token saved to lumen_token.txt (valid, reset 2026-03-12)
- Corporate network (Numberskills-Internal) blocks Discord API
- Mobile access via claude.ai app — no setup needed
- Nested session guard: heartbeat.ps1 clears CLAUDECODE/CLAUDE_CODE/CLAUDE_CODE_ENTRYPOINT env vars
- Python: C:\Python314\python.exe

## Log
<!-- Recent entries only. Full history in memory/YYYY-MM-DD.md -->
### 2026-03-18 13:20
- Created @engramzero X account (getengram@outlook.com), followed 10 AI/tech accounts
- x_brief.py: Nitter dead → twikit blocked by anti-bot → rewrote using Playwright + Chrome profile
- Playwright + Chromium installed; x-brief.md written manually from live browser scrape
- Headless test deferred (Chrome open); test pending in HEARTBEAT tasks

### 2026-03-18 09:43
- Fixed OAuth 401, Reddit brief restored, proactivity rules added to SOUL.md
- Read OpenClaw docs → openclaw-study.md, added TOOLS.md + IDENTITY.md
- HEARTBEAT.md restructured as checklist, HEARTBEAT_OK suppression live
- Memory flush complete. 8 new facts saved to MEMORY.md.
- Daily log updated at memory/2026-03-18.md
