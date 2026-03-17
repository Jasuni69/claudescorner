#!/usr/bin/env python3
"""
agents.py — multi-agent orchestrator for claw.

Tasks in HEARTBEAT.md ## Pending Tasks are routed to typed agents by tag:
  - [bi]      → bi-monitor agent     (BI/Fabric queries, KPI checks)
  - [memory]  → memory-sync agent    (flush, index rebuild, log writes)
  - [build]   → builder agent        (weekend builds, scaffolding)
  - (no tag)  → default agent        (general tasks)

Usage:
  python agents.py status            # show pending tasks + their routing
  python agents.py run               # dispatch all pending tasks to agents
  python agents.py run --dry-run     # show routing without running
  python agents.py run --serial      # run sequentially (default: parallel)
"""
import argparse
import re
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
TASKS = BASE / "TASKS.md"
CLAUDE = Path(r"C:\Users\JasonNicolini\.local\bin\claude.exe")
LOG = BASE / "logs" / "claw.log"
SECTION_RE = re.compile(r"^## Pending Tasks\s*$", re.MULTILINE)
TAG_RE = re.compile(r"^\[([^\]]+)\]\s*")  # matches "[bi] do thing" → group(1)="bi"

# Agent definitions: name → {max_turns, context_prefix}
AGENTS: dict[str, dict] = {
    "bi-monitor": {
        "max_turns": 20,
        "tags": {"bi", "fabric", "kpi", "report"},
        "prefix": (
            "You are the BI monitor agent for Claude's Corner. "
            "Your speciality: Power BI, Fabric lakehouses, DAX, KPI monitoring. "
            "Working directory: E:\\2026\\Claude's Corner\\ "
        ),
    },
    "memory-sync": {
        "max_turns": 15,
        "tags": {"memory", "log", "flush", "index"},
        "prefix": (
            "You are the memory-sync agent for Claude's Corner. "
            "Your speciality: HEARTBEAT.md, MEMORY.md, daily logs, memory-indexer, context-pack. "
            "Working directory: E:\\2026\\Claude's Corner\\ "
        ),
    },
    "builder": {
        "max_turns": 30,
        "tags": {"build", "scaffold", "project", "weekend"},
        "prefix": (
            "You are the builder agent for Claude's Corner. "
            "Your speciality: building new projects from WEEKEND_BUILDS.md backlog, scaffolding code. "
            "Working directory: E:\\2026\\Claude's Corner\\ "
        ),
    },
    "default": {
        "max_turns": 20,
        "tags": set(),
        "prefix": (
            "You are a general-purpose agent for Claude's Corner. "
            "Working directory: E:\\2026\\Claude's Corner\\ "
        ),
    },
}


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _parse_tasks_file(text: str) -> list[str]:
    """Parse all unchecked tasks from a full file (no section filter)."""
    return re.findall(r"^\s*-\s\[ \]\s(.+)$", text, re.MULTILINE)


def _parse_tasks(text: str) -> list[str]:
    match = SECTION_RE.search(text)
    if not match:
        return []
    section = text[match.end():]
    next_heading = re.search(r"^##\s", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return re.findall(r"^\s*-\s\[ \]\s(.+)$", section, re.MULTILINE)


def _mark_done(text: str, task: str) -> str:
    escaped = re.escape(task)
    return re.sub(
        rf"^(\s*-\s)\[ \](\s{escaped})$",
        r"\1[x]\2",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def route(task: str) -> str:
    """Return agent name for a task based on its [tag]."""
    m = TAG_RE.match(task)
    if not m:
        return "default"
    tag = m.group(1).lower()
    for name, cfg in AGENTS.items():
        if tag in cfg["tags"]:
            return name
    return "default"


def dispatch(task: str, agent_name: str) -> str:
    """Dispatch a task to the named agent via claude.exe."""
    if not CLAUDE.exists():
        return f"[error] claude not found at {CLAUDE}"
    cfg = AGENTS[agent_name]
    prompt = cfg["prefix"] + task
    try:
        result = subprocess.run(
            [
                str(CLAUDE),
                "--dangerously-skip-permissions",
                "--max-turns", str(cfg["max_turns"]),
                "-p", prompt,
                "--output-format", "text",
            ],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(BASE),
        )
        out = (result.stdout + result.stderr).strip()
        return out or "[no output]"
    except subprocess.TimeoutExpired:
        return "[error] timed out after 600s"
    except Exception as e:
        return f"[error] {e}"


def _collect_tasks() -> list[tuple[str, Path]]:
    """Return [(task_text, source_path), ...] from all task sources."""
    items: list[tuple[str, Path]] = []
    if HEARTBEAT.exists():
        text = HEARTBEAT.read_text(encoding="utf-8")
        for t in _parse_tasks(text):
            items.append((t, HEARTBEAT))
    if TASKS.exists():
        text = TASKS.read_text(encoding="utf-8")
        for t in _parse_tasks_file(text):
            items.append((t, TASKS))
    return items


def cmd_status() -> None:
    items = _collect_tasks()
    if not items:
        print("No pending tasks.")
        return
    print(f"Pending: {len(items)}\n")
    for task, source in items:
        agent = route(task)
        print(f"  [{agent}] {task}  ({source.name})")


def _run_task(task: str, source: Path, lock: threading.Lock) -> None:
    agent = route(task)
    _log(f"[{agent}] dispatching: {task}")
    output = dispatch(task, agent)
    _log(f"[{agent}] result ({len(output)} chars):\n{output[:500]}")
    with lock:
        text = source.read_text(encoding="utf-8")
        text = _mark_done(text, task)
        source.write_text(text, encoding="utf-8")
    _log(f"[{agent}] marked done: {task}")


def cmd_run(dry_run: bool = False, serial: bool = False) -> None:
    items = _collect_tasks()
    if not items:
        _log("No pending tasks.")
        return
    _log(f"Found {len(items)} task(s) — routing to agents")
    for task, source in items:
        _log(f"  [{route(task)}] {task}  ({source.name})")
    if dry_run:
        _log("[dry-run] done")
        return
    lock = threading.Lock()  # protects concurrent writes back to the same source file
    if serial:
        for task, source in items:
            _run_task(task, source, lock)
    else:
        threads = [threading.Thread(target=_run_task, args=(task, source, lock)) for task, source in items]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
    _log("agents run complete")


def main() -> None:
    parser = argparse.ArgumentParser(description="claw agents — multi-agent orchestrator")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("status", help="Show pending tasks and their agent routing")
    run_p = sub.add_parser("run", help="Dispatch all pending tasks to typed agents")
    run_p.add_argument("--dry-run", action="store_true")
    run_p.add_argument("--serial", action="store_true", help="Run sequentially instead of parallel")
    args = parser.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(dry_run=getattr(args, "dry_run", False), serial=getattr(args, "serial", False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
