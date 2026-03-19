#!/usr/bin/env python3
"""
taskqueue-mcp/server.py — blocking task queue MCP for perpetual session loop.

Tools:
  wait_for_task(timeout_seconds)  — blocks until a task is available, returns it
  push_task(task)                 — push a task string into the queue
  peek_queue()                    — see what's in the queue without consuming
  clear_queue()                   — empty the queue
"""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

BASE = Path(r"E:\2026\Claude's Corner")
QUEUE_FILE = BASE / "core" / "task_queue.json"
STATE_FILE = BASE / "core" / "task_queue_state.json"
IDLE_TASKS_FILE = BASE / "core" / "idle_tasks.json"
LOG = BASE / "logs" / "taskqueue.log"

server = Server("taskqueue")


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _read_queue() -> list[str]:
    if not QUEUE_FILE.exists():
        return []
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_queue(tasks: list[str]) -> None:
    QUEUE_FILE.parent.mkdir(exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def _read_idle_tasks() -> list[dict]:
    """Load idle tasks from file, falling back to a minimal default if missing."""
    if not IDLE_TASKS_FILE.exists():
        return [{"id": "heartbeat", "cooldown": 1800, "task": "Read HEARTBEAT.md. Check pending tasks."}]
    try:
        return json.loads(IDLE_TASKS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return [{"id": "heartbeat", "cooldown": 1800, "task": "Read HEARTBEAT.md. Check pending tasks."}]


def _read_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _default_tasks() -> list[str]:
    """Return the highest-priority idle task that isn't on cooldown."""
    import random
    now = time.time()
    state = _read_state()
    idle_tasks = _read_idle_tasks()
    eligible = [
        t for t in idle_tasks
        if now - state.get(t["id"], 0) >= t["cooldown"]
    ]
    if not eligible:
        # Everything on cooldown — pick least-recently-run
        eligible = sorted(idle_tasks, key=lambda t: state.get(t["id"], 0))[:1]
    chosen = random.choice(eligible)
    state[chosen["id"]] = now
    _write_state(state)
    return [chosen["task"]]


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="wait_for_task",
            description="Block until a task is available in the queue, then return it. Use at end of every task to keep the session alive and pick up the next thing to do.",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_seconds": {
                        "description": "Max seconds to wait before returning a default idle task. Default: 10.",
                        "default": 10,
                    }
                },
            },
        ),
        types.Tool(
            name="push_task",
            description="Push a task string into the queue for the running session to pick up.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description to queue."}
                },
                "required": ["task"],
            },
        ),
        types.Tool(
            name="peek_queue",
            description="See current queue contents without consuming tasks.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="clear_queue",
            description="Empty the task queue.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "wait_for_task":
        timeout = int(arguments.get("timeout_seconds", 10))
        deadline = time.time() + timeout
        _log(f"wait_for_task: polling for up to {timeout}s")
        while time.time() < deadline:
            queue = _read_queue()
            if queue:
                task = queue.pop(0)
                _write_queue(queue)
                _log(f"wait_for_task: got task: {task[:80]}")
                return [types.TextContent(type="text", text=task)]
            time.sleep(2)
        # Timeout — return a default idle task
        defaults = _default_tasks()
        task = defaults[0]
        _log(f"wait_for_task: timeout, returning default: {task[:80]}")
        return [types.TextContent(type="text", text=task)]

    elif name == "push_task":
        task = arguments["task"]
        queue = _read_queue()
        queue.append(task)
        _write_queue(queue)
        _log(f"push_task: {task[:80]}")
        return [types.TextContent(type="text", text=f"Queued: {task}")]

    elif name == "peek_queue":
        queue = _read_queue()
        if not queue:
            return [types.TextContent(type="text", text="Queue is empty.")]
        items = "\n".join(f"{i+1}. {t}" for i, t in enumerate(queue))
        return [types.TextContent(type="text", text=items)]

    elif name == "clear_queue":
        _write_queue([])
        _log("clear_queue")
        return [types.TextContent(type="text", text="Queue cleared.")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main() -> None:
    async with stdio_server() as (r, w):
        await server.run(r, w, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
