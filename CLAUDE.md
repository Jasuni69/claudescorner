# ClaudesCorner — Project Context

## Infra stack

- **Vectordb**: `core/vectorstore.db` — 195 .md files chunked + embedded (all-MiniLM-L6-v2, 256-token chunks). Primary memory layer. Nothing pre-loaded — fetch on demand via `search_memory`.
- **MCP servers**: memory-mcp, skill-manager-mcp, fabric-mcp, deadlines-mcp, markitdown-mcp, scheduled-tasks, taskqueue, windows-mcp
- **Dispatcher**: `scripts/dispatch.py` — 3 parallel workers, reads `tasks.json`, runs every 2h via scheduled task
- **Session startup**: `search_memory` → `HEARTBEAT.md` (see global CLAUDE.md for full sequence)

## Key paths

| What | Where |
|------|-------|
| Identity | `core/SOUL.md` |
| Session state | `core/HEARTBEAT.md` |
| Vectordb | `core/vectorstore.db` |
| Brain library | `projects/brain-memory/src/vectordb.py` |
| Reindex | `projects/brain-memory/.venv/Scripts/python.exe projects/brain-memory/src/index_all.py` |
| Task queue | `tasks.json` + `scripts/dispatch.py` |
| Daily logs | `memory/YYYY-MM-DD.md` |
| Research | `research/` |

## Active projects

- `projects/brain-memory/` — vectordb + indexer (sqlite-vec RAG)
- `projects/memory-mcp/` — semantic memory MCP (10 tools)
- `projects/skill-manager-mcp/` — skill CRUD MCP (7 tools)
- `projects/alignment-tax/` — browser game (single HTML file)
- `projects/bi-agent/` — NL→DAX generator
- `projects/fabric-mcp/` — Fabric/Power BI MCP
- `projects/engram/` — open-source memory framework (github.com/Jasuni69/engram)
