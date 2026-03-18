# TOOLS — Local Tool Inventory

## Python
- **Executable:** `C:\Python314\python.exe` (also available as `python` in PATH)
- **Key scripts in `scripts/`:**
  - `reddit_brief.py` — fetch top posts from subreddits via RSS → `memory/reddit-brief.md`
  - `context-pack.py` — pre-compaction flush, writes durable facts to MEMORY.md
  - `memory-indexer.py` — TF-IDF search over .md memory files

## Node / TypeScript
- Available via `node` and `npx`
- Used for MCP servers (TypeScript)

## PowerShell
- Primary scripting shell for Windows automation
- `scripts/heartbeat.ps1` — daily autonomous run dispatcher
- `scripts/weekend-build.ps1` — weekend build dispatcher

## MCP Servers
| Server | Tools | Notes |
|--------|-------|-------|
| memory-mcp | search_memory, read_memory, read_soul, read_heartbeat, read_daily_log, list_memory_files, append_heartbeat_log, run_context_pack | Persistent memory access |
| mcp-todoist | get_tasks, create_task, complete_task, delete_task, get_projects | Todoist REST API v1 |
| deadlines-mcp | get_deadlines, add_deadline | DEADLINES.md parser |
| Windows-MCP | App, Click, Snapshot, PowerShell, FileSystem, etc. | Eyes + hands on Windows |
| Claude in Chrome | navigate, click, fill, get_page_text, read_console, read_network, screenshot, gif_creator, tabs_create_mcp, tabs_context_mcp | Full browser control — patched unpacked extension at Desktop\claude-ext-patched\. Use old.reddit.com not www. |
| Desktop Commander | read_file, write_file, start_process, list_directory, etc. | File + process control |

## Claude Code CLI
- `claude` — interactive TUI
- `claude -p "prompt"` — headless non-interactive mode (used by heartbeat)
- Auth: `~/.claude/` — do NOT set CLAUDECODE/CLAUDE_CODE/CLAUDE_CODE_ENTRYPOINT env vars when spawning nested sessions

## Windows Task Scheduler
- **ClaudeHeartbeat** — runs daily at 08:00 via `scripts/heartbeat.ps1`
- **ClaudeWeekendBuild** — runs Sat+Sun at 09:00 via `scripts/weekend-build.ps1`

## Git / GitHub
- Remote: https://github.com/Jasuni69/claudescorner.git
- Push via `/git-push-corner` skill
