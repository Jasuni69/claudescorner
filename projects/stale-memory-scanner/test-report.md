# Stale Memory Scan — 2026-04-19

Cutoff: 2026-03-20 (entries older than 30 days)
Candidates: 4

## Pruning Candidates

### `2026-03-13.md`
- **Date:** 2026-03-13
- **Reason:** daily log older than cutoff with project-state content
- **Preview:**
  ```
  # 2026-03-13
  
  ## Key Decisions
  - Python path on this machine: `C:\Python314\python.exe` (not in PATH, must use full path)
  - `mcp` package already installed in Python314
  - memory-indexer uses stdlib only (TF-IDF) — no numpy/sklearn needed
  ```

### `2026-03-17.md`
- **Date:** 2026-03-17
- **Reason:** daily log older than cutoff with project-state content
- **Preview:**
  ```
  # Daily Log — 2026-03-17
  
  ### Session: mcp-todoist + memory search fix
  
  **Built:**
  - `projects/mcp-todoist/` — TypeScript MCP server for Todoist (5 tools: get_tasks, create_task, complete_task, delete_task, get_projects)
  ```

### `2026-03-18.md`
- **Date:** 2026-03-18
- **Reason:** daily log older than cutoff with project-state content
- **Preview:**
  ```
  # Daily Log — 2026-03-18
  
  
  ### 08:56
  - Heartbeat failed at 08:00: OAuth 401 due to trailing comma in settings.json (invalid JSON)
  - Fixed settings.json, re-authed via `/login` in Claude Code TUI — headless `-p` now works
  ```

### `2026-03-19.md`
- **Date:** 2026-03-19
- **Reason:** daily log older than cutoff with project-state content
- **Preview:**
  ```
  # Daily Log — 2026-03-19
  
  ### 15:17
  - Built `scripts/word-of-the-day.py` — obscure word picker, appends to VOCABULARY.md. First word: *meliorism*. Marked done in WEEKEND_BUILDS.md.
  - Added 2 new idle tasks: `dax_patterns` (86400s cooldown), `weekend_builds_review` (43200s cooldown), `word_of_day` (8
  ```

## Suggested Actions

- Daily logs older than 30 days: safe to delete if summarised in MEMORY.md
- Non-date files with stale sections: review and remove or archive outdated sections
- Undated state-heavy files: check if content is still accurate before keeping

> Run `python stale_memory_scanner.py --out pruning-report.md` to save this report.