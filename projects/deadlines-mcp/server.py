#!/usr/bin/env python3
"""MCP server: DEADLINES.md watcher — exposes upcoming deadlines as tools."""

import re
from datetime import date
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

DEADLINES_FILE = Path(__file__).parent.parent.parent / "DEADLINES.md"
ENTRY_RE = re.compile(r"^-\s+(\d{4}-\d{2}-\d{2})\s+(.+)$")

server = Server("deadlines-mcp")


def _load() -> list[dict]:
    if not DEADLINES_FILE.exists():
        return []
    today = date.today()
    items = []
    for line in DEADLINES_FILE.read_text(encoding="utf-8").splitlines():
        m = ENTRY_RE.match(line.strip())
        if m:
            d = date.fromisoformat(m.group(1))
            days = (d - today).days
            items.append({
                "date": str(d),
                "label": m.group(2).strip(),
                "days_remaining": days,
                "status": "overdue" if days < 0 else "today" if days == 0 else "upcoming",
            })
    return sorted(items, key=lambda x: x["date"])


def _format_list(items: list[dict]) -> str:
    if not items:
        return "No deadlines found."
    lines = []
    for it in items:
        days = it["days_remaining"]
        if days < 0:
            delta = f"OVERDUE by {abs(days)}d"
        elif days == 0:
            delta = "TODAY"
        else:
            delta = f"{days}d remaining"
        lines.append(f"- {it['date']}  [{delta}]  {it['label']}")
    return "\n".join(lines)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_deadlines",
            description="List all upcoming deadlines from DEADLINES.md with days remaining.",
            inputSchema={"type": "object", "properties": {
                "filter": {
                    "type": "string",
                    "enum": ["all", "overdue", "upcoming", "today"],
                    "description": "Filter by status. Default: all.",
                }
            }},
        ),
        Tool(
            name="add_deadline",
            description="Add a new deadline entry to DEADLINES.md.",
            inputSchema={"type": "object", "properties": {
                "date": {"type": "string", "description": "ISO date YYYY-MM-DD"},
                "label": {"type": "string", "description": "Short description"},
            }, "required": ["date", "label"]},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "get_deadlines":
        items = _load()
        f = arguments.get("filter", "all")
        if f != "all":
            items = [i for i in items if i["status"] == f]
        return [TextContent(type="text", text=_format_list(items))]

    if name == "add_deadline":
        d = arguments["date"]
        label = arguments["label"]
        # Validate date
        date.fromisoformat(d)
        entry = f"- {d} {label}\n"
        with DEADLINES_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)
        return [TextContent(type="text", text=f"Added: {d} {label}")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
