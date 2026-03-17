# PATTERNS.md — Code Patterns & Decisions

Stable conventions confirmed across sessions. Update when decisions change.

## Python
- `Path(__file__).parent.parent.parent` to anchor BASE — don't hardcode absolute paths
- `LOG.parent.mkdir(exist_ok=True)` before first write — never assume dirs exist
- `read_text(encoding="utf-8")` / `write_text(encoding="utf-8")` everywhere — explicit encoding
- Type hints on all function signatures
- `dataclasses` for structured data, avoid raw dicts when shape is known
- Specific exceptions only — never bare `except:`
- f-strings, not `.format()` or `%`

## Anti-patterns
- No hardcoded absolute paths except `CLAUDE` exe path (unavoidable)
- No `time.sleep()` in non-scheduler code
- No `subprocess.run()` with `shell=True`
- No `os.path` — use `pathlib.Path` throughout
- No magic numbers — name constants at module level

## Architecture decisions
- Task sources: HEARTBEAT.md `## Pending Tasks` section + TASKS.md full scan
- Mark-done writes back to source file using regex — preserves formatting
- Agent routing by `[tag]` prefix in task text — untagged → default agent
- Parallel dispatch via `threading.Thread` — use `--serial` flag to override
- `--dangerously-skip-permissions --max-turns N` on all claude.exe calls
- MCP servers: stdio transport, Python, `mcp` package from PyPI
- Scripts: `E:\2026\Claude's Corner\scripts\`
- Projects: `E:\2026\Claude's Corner\projects\<name>\`

## File size rule
- Keep files under 300 lines. Split if growing past that.

## Logging
- Always: `[YYYY-MM-DD HH:MM:SS] message` format
- Log to `logs/claw.log` for automation, stdout for interactive
- Truncate long output at 500 chars in logs

## Known gotchas
- `CLAUDECODE` env var set inside claude.exe sessions — nested calls blocked by session guard
- Corporate network (Numberskills-Internal) blocks Discord API
- Microsoft Graph API token lacks Tasks.Read/Tasks.ReadWrite scopes (401 on To Do)
- Python is `C:\Python314\python.exe` — `mcp` package installed there
- Bun + Windows has issues running MCP servers (non-blocking, workaround: node or python)
