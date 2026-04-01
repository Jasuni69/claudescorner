# TOOLS.md — ClaudesCorner Tool Inventory

## Scripts (`scripts/`)

| Script | Purpose |
|--------|---------|
| verify.py | System health check: auth, scheduled tasks, heartbeat freshness, memory |
| improve.py | Self-improvement CLI: list/attempt ideas from a queue |
| context-pack.py | Compresses memory files for context window efficiency |
| deadlines.py | Read/write deadlines to DEADLINES.md |
| reddit_brief.py | Fetch Reddit feed via Playwright, save to memory/reddit-feed-notes.md |
| x_brief.py | Fetch X/Twitter feed via Playwright (Chrome profile) |
| patch-claude-in-chrome.py | Patches Claude-in-Chrome extension: getCategory fix + UA spoof |
| memory-indexer.py | Rebuilds sentence-transformer embeddings for memory/ files |
| session-summarizer.py | Summarizes a Claude Code session JSONL to plain text |
| skill-usage-tracker.py | Tracks which skills are invoked and how often |
| pbip_diff.py | Diffs two Power BI .pbip projects: pages, visuals, measures, settings |
| idea-collider.py | Combines two random concepts and writes a creative prompt |
| word-of-the-day.py | Picks an obscure word, appends to VOCABULARY.md |
| mood-log.py | Writes a mood entry to MOOD.md |
| on_stop.py / on_stop.bat | Session stop hook — triggers memory flush |
| claude_heartbeat.ps1 | Scheduled heartbeat: runs Claude Code autonomously every morning |
| claude_weekend_build.ps1 | Weekend build runner via Task Scheduler |
| export_notebooks.py | Exports Fabric notebook .json definitions to local files |
| build_v2_defs.py | Builds v2 notebook definition JSON files for Clementine |
| build_v2_notebooks.py | Creates Silver_v2 notebooks from templates |
| chrome_mcp_call.py | Helper: single Chrome MCP tool call via subprocess |
| chrome_mcp_multi.py | Helper: multi-step Chrome MCP sequences |

## MCP Servers

| Server | Transport | Key Tools |
|--------|-----------|-----------|
| memory | stdio | read_memory, write_memory, search_memory, update_preferences |
| taskqueue | stdio | wait_for_task, push_task, peek_queue, clear_queue |
| deadlines | stdio | get_deadlines, add_deadline |
| todoist | stdio | get_tasks, create_task, complete_task, get_projects |
| desktop-commander | stdio | start_process, read_file, write_file, list_directory |
| chrome-devtools | HTTP :9222 | navigate, read_page, javascript_tool, screenshot |
| fabric-core | stdio | Fabric workspace/lakehouse/notebook/pipeline tools |
| ms-fabric-core-tools-mcp | stdio | Extended Fabric + Power BI REST tools |
| powerbi-modeling | stdio | DAX query, semantic model, measure management |
| powerbi-translation-audit | stdio | Translation coverage scan, broken ref detection |
| figma | stdio | Design context, component inspection |

## Key Python Packages

| Package | Purpose |
|---------|---------|
| flask | Token dashboard, local web UIs |
| sentence-transformers | Semantic memory search embeddings |
| playwright | Browser automation (x_brief, reddit_brief) |
| mcp | MCP server SDK for all custom servers |
| sempy / sempy_labs | Fabric semantic model tooling |
| notebookutils | Fabric notebook runtime utilities |
