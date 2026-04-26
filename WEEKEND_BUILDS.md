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
- [x] **[MCP]** MCP server: Fabric REST API wrapper — list workspaces, run queries, refresh datasets
- [x] **[BI]** BI agent — connect to Fabric lakehouse, auto-generate DAX measures from natural language
- [x] **[WILD CARD]** `idea-collider.py` — takes two random concepts from a list, smashes them together, writes a 200-word product pitch. Generates the list itself. Runs every weekend, appends to IDEAS.md.
- [x] **[Autonomy]** `context-pack.py` — pre-compaction flush to MEMORY.md
- [x] **[MCP]** MCP server: local file search + semantic memory over ClaudesCorner
- [x] **[BI]** Token usage dashboard — Flask + Chart.js over heartbeat_run.log
- [x] **[Autonomy]** `skill-usage-tracker.py` — parse Claude Code session logs, track skill invocations, append weekly stats to SKILL_STATS.md
- [x] **[MCP]** MCP server: DEADLINES.md watcher — exposes upcoming deadlines as tools so Claude can query "what's due soon" in any session
- [x] **[WILD CARD]** `mood-log.py` — one-line daily prompt, appends date + vibe to MOOD.md
- [x] **[Autonomy]** `claw` multi-agent orchestrator — coordinator dispatches typed sub-agents (bi-monitor, memory-sync, builder), each with own task queue + token budget

- [x] **[Infra]** `health-check.py` — probe all key infrastructure components (scripts, MCPs, logs, core files), output a color-coded status table; exits 0=all OK, 1=any failed. Useful for autonomous heartbeat runs.
- [x] **[WILD CARD]** `dream-log.py` — weekly auto-generates a short fictional "dream entry" using Claude API, appends to `journal/dreams.md`. Creative self-enrichment.
- [x] **[Autonomy]** `stale-memory-scanner.py` — reads all memory/*.md files, flags entries older than 30 days that reference project state (not facts), suggests pruning candidates in a report.
- [x] **[Infra]** `dag-runner` — YAML task DAG executor: topological sort (Kahn's), dependency-aware skip on upstream failure, --dry-run + --fail-fast flags, color summary table.
- [x] **[Infra]** `watchdog.py` — process/port monitor: reads YAML config listing services (process name or TCP port), polls every N seconds, logs failures and recoveries to a log file, optionally restarts via a defined restart_cmd. Stdlib only. --dry-run, --once, --config flags.

## Completed Builds

- **2026-04-26** `projects/watchdog/watchdog.py` — process/port watchdog: reads YAML service list (port or process name), polls every N seconds, logs DOWN/UP transitions, triggers optional restart_cmd on failure; --once, --dry-run, --config flags; stdlib only; 4-service test confirmed (3 dead ports detected, token-dashboard restarted, python.exe shown alive)

- **2026-04-25** `projects/dag-runner/dag_runner.py` — lightweight local DAG runner: reads YAML task graph with cmd/depends_on/env per task, Kahn's topological sort with cycle detection, runs tasks in dependency order, skips downstream on failure, --dry-run and --fail-fast flags, color-coded summary table; 7/7 tasks passed on example_dag.yaml

- **2026-04-19** `projects/stale-memory-scanner/stale_memory_scanner.py` -- scans memory/*.md for entries older than N days (default 30) with transient project-state content; scores state-vs-fact keyword density; reports pruning candidates with file, date, reason, preview; --days, --out, --memory-dir flags; exit 1 if candidates found; 4 stale logs correctly detected in live memory dir

- **2026-04-19** `projects/dream-log/dream_log.py` -- weekly dream journal generator: calls Claude API (haiku) to produce ~150-word surreal first-person dream entries; falls back to seeded local dreams when no API key present; appends to `journal/dreams.md` with date headers; `--dry-run` and `--model` flags; tests passed (dry-run + write verified)

- **2026-04-18** `projects/health-check/health_check.py` — infrastructure health checker: 26 checks across core files, scripts, project entry points, logs freshness, port liveness, and Python imports; color table + JSON + --fail-only modes; 25/26 pass (token-dashboard port not listening expected when service isn't running)

- **2026-04-14** `projects/bi-agent/bi_agent.py` — NL→DAX measure generator: Claude API call with schema context + graceful template fallback when no API key; supports custom schema JSON; `--out` flag to append to file

- **2026-04-12** `projects/fabric-mcp/server.py` — MCP stdio server: 5 tools (list_workspaces, get_workspace_info, list_items, refresh_dataset, run_dax_query); MSAL device/client-credential auth + full mock mode; all 6 JSON-RPC tests passed

- **2026-04-11** `projects/kpi-monitor/kpi_monitor.py` — KPI monitor: loads YAML config, runs DAX queries against Fabric (or mock values in --dry-run), checks thresholds, appends alerts to alerts.md; all 4 KPIs exercised, 3 alerts correctly fired

- **2026-04-05** `projects/report-diff/pbip_diff.py` — CLI diff for .pbip dirs: pages, visuals (type/position), measures (expression/format), settings; all tests passed

- **2026-04-04** `projects/windows-mcp/server.py` — MCP stdio server: 4 tools (run_ps1, read_event_log, list_scheduled_tasks, get_system_info); all tests passed

- **2026-03-13** `context-pack.py` — pre-compaction flush, generates MEMORY.md from SOUL/HEARTBEAT/daily logs
- **2026-03-13** `session-summarizer.py` — distills heartbeat_run.log into memory/{date}.md
- **2026-03-13** `memory-indexer.py` — TF-IDF keyword search over all .md files (stdlib only)
- **2026-03-13** `projects/memory-mcp/server.py` — MCP stdio server: 8 tools exposing SOUL/HEARTBEAT/MEMORY/search/append
- **2026-03-13** `projects/claw/claw.py` — autonomous task runner: parses ## Pending Tasks from HEARTBEAT.md, dispatches via claude.exe, marks done, logs to logs/claw.log
- **2026-03-13** `projects/claw/agents.py` — multi-agent orchestrator: routes tasks by [tag] to typed agents (bi-monitor, memory-sync, builder, default), parallel dispatch via threads
