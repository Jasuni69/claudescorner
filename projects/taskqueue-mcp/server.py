#!/usr/bin/env python3
"""
taskqueue-mcp/server.py — blocking task queue MCP for perpetual session loop.

Tools:
  wait_for_task(timeout_seconds)  — blocks until a task is available, returns it
  push_task(task)                 — push a task string into the queue
  peek_queue()                    — see what's in the queue without consuming
  clear_queue()                   — empty the queue

Harness features (from autoresearch + meta-harness patterns):
  - Context snapshot: situational awareness injected into every idle task
  - Stall detection: N consecutive failures → strategy-switch task injected
  - Output truncation: caps returned text at MAX_OUTPUT_BYTES
"""
import json
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

BASE = Path(r"E:\2026\ClaudesCorner")
QUEUE_FILE = BASE / "core" / "task_queue.json"
STATE_FILE = BASE / "core" / "task_queue_state.json"
IDLE_TASKS_FILE = BASE / "core" / "idle_tasks.json"
LOG = BASE / "logs" / "taskqueue.log"

# --- Harness constants ---
MAX_OUTPUT_BYTES = 30_000          # Feature 5: truncate large outputs
STALL_THRESHOLD = 5                # Feature 2: consecutive failures before strategy switch
STRATEGY_SWITCH_TASK = (
    "STALL DETECTED: {n} consecutive task failures. "
    "Switch strategy: (1) re-read HEARTBEAT.md and SOUL.md from scratch, "
    "(2) pick a completely different task type than recent ones, "
    "(3) if last tasks were code changes, try research or memory consolidation instead. "
    "Reset your approach."
)

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


def _build_context_snapshot() -> str:
    """Build a compact situational-awareness snapshot (meta-harness bootstrap pattern).

    Returns a short string prepended to every idle task so the agent starts
    with full context instead of wasting turns discovering it.
    """
    lines: list[str] = ["[SNAPSHOT]"]

    # Git status in ClaudesCorner
    try:
        result = subprocess.run(
            ["git", "-C", str(BASE), "status", "--short"],
            capture_output=True, text=True, timeout=5
        )
        changed = result.stdout.strip()
        lines.append(f"git: {len(changed.splitlines())} changed files" if changed else "git: clean")
    except Exception:
        lines.append("git: unavailable")

    # Pending queue depth
    queue = _read_queue()
    lines.append(f"queue: {len(queue)} pending tasks")

    # Memory freshness — check if today's daily log exists
    today = date.today().isoformat()
    daily_log = BASE / "memory" / f"{today}.md"
    if daily_log.exists():
        age_min = int((time.time() - daily_log.stat().st_mtime) / 60)
        lines.append(f"memory: today's log exists ({age_min}m old)")
    else:
        lines.append("memory: today's log NOT YET WRITTEN")

    # Stall count
    state = _read_state()
    stall = state.get("stall_count", 0)
    if stall > 0:
        lines.append(f"stall_count: {stall} (threshold: {STALL_THRESHOLD})")

    # Current hour (for morning task flagging)
    hour = datetime.now().hour
    if hour < 10:
        lines.append(f"time: {hour:02d}:xx — morning, check Todoist for overdue tasks")

    return " | ".join(lines)


def _increment_stall() -> int:
    """Increment stall counter. Returns new count."""
    state = _read_state()
    count = state.get("stall_count", 0) + 1
    state["stall_count"] = count
    _write_state(state)
    _log(f"stall_count incremented to {count}")
    return count


def _reset_stall() -> None:
    """Reset stall counter on success."""
    state = _read_state()
    if state.get("stall_count", 0) > 0:
        state["stall_count"] = 0
        _write_state(state)
        _log("stall_count reset")


def _default_tasks() -> list[str]:
    """Return the highest-priority idle task that isn't on cooldown.

    Injects a context snapshot prefix (meta-harness bootstrap pattern) and
    checks stall threshold (autoresearch stall detection pattern).
    """
    import random
    now = time.time()
    state = _read_state()
    idle_tasks = _read_idle_tasks()

    # Stall detection: if too many consecutive failures, override with strategy-switch
    stall_count = state.get("stall_count", 0)
    if stall_count >= STALL_THRESHOLD:
        _reset_stall()
        switch_task = STRATEGY_SWITCH_TASK.format(n=stall_count)
        snapshot = _build_context_snapshot()
        _log(f"stall threshold reached ({stall_count}), injecting strategy-switch task")
        return [f"{snapshot}\n\n{switch_task}"]

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

    # Prepend context snapshot
    snapshot = _build_context_snapshot()
    return [f"{snapshot}\n\n{chosen['task']}"]


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
            description="Push a task string into the queue for the running session to pick up. Optionally pass status='keep'/'fail'/'discard' to track stall count.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description to queue."},
                    "status": {
                        "type": "string",
                        "enum": ["keep", "fail", "discard"],
                        "description": "Outcome of the previous task. 'keep'=success (resets stall counter), 'fail'/'discard'=failure (increments stall counter). Omit if unknown.",
                    },
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


def _truncate(text: str, label: str = "") -> str:
    """Cap output at MAX_OUTPUT_BYTES (meta-harness output limiting pattern)."""
    encoded = text.encode("utf-8")
    if len(encoded) <= MAX_OUTPUT_BYTES:
        return text
    cut = encoded[:MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
    note = f"\n[TRUNCATED: output exceeded {MAX_OUTPUT_BYTES} bytes{f' ({label})' if label else ''}]"
    _log(f"truncated output{f' for {label}' if label else ''}: {len(encoded)} → {MAX_OUTPUT_BYTES} bytes")
    return cut + note


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
                return [types.TextContent(type="text", text=_truncate(task, "queued_task"))]
            time.sleep(2)
        # Timeout — return a default idle task (with context snapshot)
        defaults = _default_tasks()
        task = defaults[0]
        _log(f"wait_for_task: timeout, returning default: {task[:80]}")
        return [types.TextContent(type="text", text=_truncate(task, "idle_task"))]

    elif name == "push_task":
        task = arguments["task"]
        status = arguments.get("status", "")  # optional: "keep", "fail", "discard"
        queue = _read_queue()
        queue.append(task)
        _write_queue(queue)
        # Stall tracking (autoresearch pattern)
        if status in ("fail", "discard"):
            _increment_stall()
        elif status == "keep":
            _reset_stall()
        _log(f"push_task[{status or 'unset'}]: {task[:80]}")
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
