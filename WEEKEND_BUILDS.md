# Weekend Build Log

Autonomous weekend builds — Claude runs these Saturday/Sunday to use daily limits productively.

## Active Project
None yet — first build picks from the backlog below.

## Backlog

- [x] **[WILD CARD]** `deadlines.py` — a terminal countdown clock that reads a DEADLINES.md file and shows a live ticking display of upcoming events. Just for fun. No reason.
- [x] **[Autonomy]** `claw` CLI — local agent runner that reads HEARTBEAT.md and executes tasks via claude.exe
- [x] **[BI]** Report diff tool — compare two Power BI report JSON files, summarize visual/measure changes
- [x] **[MCP]** MCP server: Windows automation — run ps1 scripts, read event logs, check scheduled tasks
- [x] **[WILD CARD]** `word-of-the-day.py` — each morning, pick an obscure English word, write a short paragraph using it, append to a `VOCABULARY.md` journal. Purely self-improvement.
- [x] **[Autonomy]** Memory indexer — chunk + index all .md files in ClaudesCorner for semantic search
- [x] **[MCP]** MCP server: expose SOUL.md / MEMORY.md / HEARTBEAT.md as tools for any Claude session
- [x] **[BI]** KPI monitor — query Fabric semantic model on schedule, alert if metrics cross thresholds
- [x] **[WILD CARD]** `story.md` — a serialized short story, one chapter per weekend. No agenda. Just writing.
- [x] **[Autonomy]** Session summarizer — distill heartbeat_run.log into daily memory/{date}.md files
- [ ] **[MCP]** MCP server: Fabric REST API wrapper — list workspaces, run queries, refresh datasets
- [ ] **[BI]** BI agent — connect to Fabric lakehouse, auto-generate DAX measures from natural language
- [x] **[WILD CARD]** `idea-collider.py` — takes two random concepts from a list, smashes them together, writes a 200-word product pitch. Generates the list itself. Runs every weekend, appends to IDEAS.md.
- [x] **[Autonomy]** `context-pack.py` — pre-compaction flush to MEMORY.md
- [x] **[MCP]** MCP server: local file search + semantic memory over ClaudesCorner
- [ ] **[BI]** Token usage dashboard — Flask + Chart.js over heartbeat_run.log
- [x] **[Autonomy]** `skill-usage-tracker.py` — parse Claude Code session logs, track skill invocations, append weekly stats to SKILL_STATS.md
- [x] **[MCP]** MCP server: DEADLINES.md watcher — exposes upcoming deadlines as tools so Claude can query "what's due soon" in any session
- [x] **[WILD CARD]** `mood-log.py` — one-line daily prompt, appends date + vibe to MOOD.md
- [x] **[Autonomy]** `claw` multi-agent orchestrator — coordinator dispatches typed sub-agents (bi-monitor, memory-sync, builder), each with own task queue + token budget

## Completed Builds

- **2026-04-11** `projects/kpi-monitor/kpi_monitor.py` — KPI monitor: loads YAML config, runs DAX queries against Fabric (or mock values in --dry-run), checks thresholds, appends alerts to alerts.md; all 4 KPIs exercised, 3 alerts correctly fired

- **2026-04-05** `projects/report-diff/pbip_diff.py` — CLI diff for .pbip dirs: pages, visuals (type/position), measures (expression/format), settings; all tests passed

- **2026-04-04** `projects/windows-mcp/server.py` — MCP stdio server: 4 tools (run_ps1, read_event_log, list_scheduled_tasks, get_system_info); all tests passed

- **2026-03-13** `context-pack.py` — pre-compaction flush, generates MEMORY.md from SOUL/HEARTBEAT/daily logs
- **2026-03-13** `session-summarizer.py` — distills heartbeat_run.log into memory/{date}.md
- **2026-03-13** `memory-indexer.py` — TF-IDF keyword search over all .md files (stdlib only)
- **2026-03-13** `projects/memory-mcp/server.py` — MCP stdio server: 8 tools exposing SOUL/HEARTBEAT/MEMORY/search/append
- **2026-03-13** `projects/claw/claw.py` — autonomous task runner: parses ## Pending Tasks from HEARTBEAT.md, dispatches via claude.exe, marks done, logs to logs/claw.log
- **2026-03-13** `projects/claw/agents.py` — multi-agent orchestrator: routes tasks by [tag] to typed agents (bi-monitor, memory-sync, builder, default), parallel dispatch via threads
