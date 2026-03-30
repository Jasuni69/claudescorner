# memory-mcp

MCP server exposing SOUL.md, MEMORY.md, HEARTBEAT.md, and memory search as tools.

## Install

```bash
pip install mcp
```

## Tools

| Tool | Description |
|------|-------------|
| `read_soul` | Read SOUL.md |
| `read_heartbeat` | Read HEARTBEAT.md |
| `read_memory` | Read MEMORY.md |
| `read_daily_log` | Read memory/{date}.md (defaults to today) |
| `search_memory` | Keyword/TF-IDF search across all .md files |
| `append_heartbeat_log` | Append timestamped entry to HEARTBEAT.md |
| `run_context_pack` | Regenerate MEMORY.md via context-pack.py |
| `list_memory_files` | List all daily log files |

## Claude Desktop Config

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "memory": {
      "command": "C:\\Python314\\python.exe",
      "args": ["E:\\2026\\ClaudesCorner\\projects\\memory-mcp\\server.py"]
    }
  }
}
```

Restart Claude Desktop after editing.

## Test

```bash
python server.py
# Then send MCP initialize + tools/list via stdin (or use mcp dev tools)
```
