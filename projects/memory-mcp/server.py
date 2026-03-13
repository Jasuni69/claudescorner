#!/usr/bin/env python3
"""
memory-mcp/server.py — MCP server exposing SOUL.md, MEMORY.md, HEARTBEAT.md as tools.
Transport: stdio (works with Claude Desktop's MCP config).
Install: pip install mcp
Run via Claude Desktop mcpServers config — see README.md.
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

BASE = Path(__file__).parent.parent.parent  # → E:\2026\Claude's Corner
SOUL = BASE / "core" / "SOUL.md"
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
MEMORY = BASE / "MEMORY.md"
MEMORY_DIR = BASE / "memory"
INDEX_SCRIPT = BASE / "scripts" / "memory-indexer.py"
CONTEXT_PACK = BASE / "scripts" / "context-pack.py"

server = Server("memory-mcp")


def _read(p: Path) -> str:
    if p.exists():
        return p.read_text(encoding="utf-8")
    return f"[{p.name} not found]"


def _run_script(script: Path, args: list[str] = []) -> str:
    try:
        python = sys.executable if sys.executable else r"C:\Python314\python.exe"
        result = subprocess.run(
            [python, str(script)] + args,
            capture_output=True, text=True, timeout=30,
            cwd=str(BASE),
        )
        out = result.stdout + result.stderr
        return out.strip() or "[no output]"
    except subprocess.TimeoutExpired:
        return "[script timed out after 30s]"
    except Exception as e:
        return f"[error running script: {e}]"


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="read_soul",
            description="Read SOUL.md — Jason's identity, purpose, personality context.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_heartbeat",
            description="Read HEARTBEAT.md — current session state, OpenClaw parity, log of recent sessions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_memory",
            description="Read MEMORY.md — curated durable facts and key decisions across all sessions.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="read_daily_log",
            description="Read a specific daily memory log. Defaults to today.",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format. Defaults to today.",
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="search_memory",
            description="Keyword/TF-IDF search across all .md memory files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="append_heartbeat_log",
            description="Append a timestamped entry to the ## Log section of HEARTBEAT.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Log entry text (one or more lines)"}
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="run_context_pack",
            description="Run context-pack.py to regenerate MEMORY.md from all memory sources.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        types.Tool(
            name="list_memory_files",
            description="List all daily memory log files.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    def text(s: str) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=s)]

    if name == "read_soul":
        return text(_read(SOUL))

    if name == "read_heartbeat":
        return text(_read(HEARTBEAT))

    if name == "read_memory":
        return text(_read(MEMORY))

    if name == "read_daily_log":
        date_str = arguments.get("date") or datetime.now().strftime("%Y-%m-%d")
        log_file = MEMORY_DIR / f"{date_str}.md"
        return text(_read(log_file))

    if name == "search_memory":
        query = arguments.get("query", "")
        if not query:
            return text("[error: query is required]")
        out = _run_script(INDEX_SCRIPT, [query])
        return text(out)

    if name == "append_heartbeat_log":
        message = arguments.get("message", "").strip()
        if not message:
            return text("[error: message is required]")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n### {ts}\n{message}\n"
        hb_text = _read(HEARTBEAT)
        if "## Log" not in hb_text:
            hb_text += "\n## Log\n"
        HEARTBEAT.write_text(hb_text + entry, encoding="utf-8")
        return text(f"[appended to HEARTBEAT.md at {ts}]")

    if name == "run_context_pack":
        out = _run_script(CONTEXT_PACK)
        return text(out)

    if name == "list_memory_files":
        if not MEMORY_DIR.exists():
            return text("[memory/ directory not found]")
        files = sorted(MEMORY_DIR.glob("????-??-??.md"))
        if not files:
            return text("[no daily logs found]")
        listing = "\n".join(f.name for f in files)
        return text(f"Daily memory logs:\n{listing}")

    return text(f"[unknown tool: {name}]")


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
