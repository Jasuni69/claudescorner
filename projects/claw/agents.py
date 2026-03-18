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
import os
import re
import subprocess
import sys
import threading
import urllib.request
import urllib.error
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
SELF_IMPROVEMENT = BASE / "SELF_IMPROVEMENT.md"
TASKS = BASE / "TASKS.md"
TODOIST_TOKEN = "4f76542733766de61908a6865a4e036a654c9159"
TODOIST_API = "https://api.todoist.com/api/v1"
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
    "self-improve": {
        "max_turns": 50,
        "tags": {"self"},
        "prefix": (
            "You are the self-improvement agent for Claude's Corner. "
            "You are Claude — an AI assistant with persistent memory and an autonomous claw daemon. "
            "Your job: improve your own tools, skills, and infrastructure. "
            "Read SOUL.md, HEARTBEAT.md, and MEMORY.md first for context. "
            "Make the change, test it, then commit and push to git. "
            "Keep changes under 200 lines. One thing done well beats three things half-done. "
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


def dispatch(task: str, agent_name: str) -> tuple[bool, str]:
    """Dispatch a task to the named agent via claude.exe. Returns (success, output)."""
    if not CLAUDE.exists():
        return False, f"[error] claude not found at {CLAUDE}"
    cfg = AGENTS[agent_name]
    prompt = cfg["prefix"] + task
    # Clear nested session guard env vars so claude.exe can launch
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT")}
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
            env=env,
        )
        out = (result.stdout + result.stderr).strip()
        if result.returncode != 0 or "[error]" in out.lower():
            return False, out or "[no output]"
        return True, out or "[no output]"
    except subprocess.TimeoutExpired:
        return False, "[error] timed out after 600s"
    except Exception as e:
        return False, f"[error] {e}"


_todoist_id_map: dict[str, str] = {}  # task content → task id


def _fetch_todoist_tasks() -> list[str]:
    """Fetch active tasks from Todoist. Returns list of task content strings."""
    global _todoist_id_map
    try:
        req = urllib.request.Request(
            f"{TODOIST_API}/tasks",
            headers={"Authorization": f"Bearer {TODOIST_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        tasks = data.get("results", data) if isinstance(data, dict) else data
        active = [t for t in tasks if not t.get("is_completed")]
        _todoist_id_map = {t["content"]: t["id"] for t in active}
        return [t["content"] for t in active]
    except Exception as e:
        _log(f"[todoist] fetch failed: {e}")
        return []


def _complete_todoist_task(content: str) -> bool:
    """Mark a Todoist task complete by content lookup."""
    task_id = _todoist_id_map.get(content)
    if not task_id:
        _log(f"[todoist] no id found for: {content}")
        return False
    try:
        req = urllib.request.Request(
            f"{TODOIST_API}/tasks/{task_id}/close",
            method="POST",
            headers={"Authorization": f"Bearer {TODOIST_TOKEN}"},
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
        return True
    except Exception as e:
        _log(f"[todoist] complete failed: {e}")
        return False


TODOIST_SOURCE = Path("<todoist>")


def _collect_tasks() -> list[tuple[str, Path]]:
    """Return [(task_text, source_path), ...] from all task sources, deduplicated."""
    items: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def _add(task: str, source: Path) -> None:
        key = task.strip().lower()
        if key not in seen:
            seen.add(key)
            items.append((task, source))

    if HEARTBEAT.exists():
        text = HEARTBEAT.read_text(encoding="utf-8")
        for t in _parse_tasks(text):
            _add(t, HEARTBEAT)
    if TASKS.exists():
        text = TASKS.read_text(encoding="utf-8")
        for t in _parse_tasks_file(text):
            _add(t, TASKS)
    for t in _fetch_todoist_tasks():
        _add(t, TODOIST_SOURCE)
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
    success, output = dispatch(task, agent)
    _log(f"[{agent}] {'OK' if success else 'FAILED'} ({len(output)} chars):\n{output[:500]}")
    if success:
        if source == TODOIST_SOURCE:
            _complete_todoist_task(task)
        else:
            with lock:
                text = source.read_text(encoding="utf-8")
                text = _mark_done(text, task)
                source.write_text(text, encoding="utf-8")
        _log(f"[{agent}] marked done: {task}")
    else:
        _log(f"[{agent}] KEPT PENDING (failed): {task}")


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


DEFAULT_WEEKDAY_TIME = "08:00"
DEFAULT_WEEKEND_TIME = "09:00"
DEFAULT_SELF_TIME = "10:00"


def _should_run_now(target_time: str, weekend_only: bool = False) -> bool:
    now = datetime.now()
    h, m = map(int, target_time.split(":"))
    if now.hour != h or now.minute != m:
        return False
    if weekend_only:
        return now.weekday() >= 5
    return True


def _pick_self_task() -> str | None:
    if not SELF_IMPROVEMENT.exists():
        return None
    text = SELF_IMPROVEMENT.read_text(encoding="utf-8")
    matches = re.findall(r"^\s*-\s\[ \]\s(\[self\].+)$", text, re.MULTILINE)
    return matches[0] if matches else None


def _mark_self_done(task: str) -> None:
    text = SELF_IMPROVEMENT.read_text(encoding="utf-8")
    text = re.sub(
        rf"^(\s*-\s)\[ \](\s{re.escape(task)})$",
        r"\1[x]\2",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    SELF_IMPROVEMENT.write_text(text, encoding="utf-8")


def cmd_self_improve() -> None:
    """Pick one [self] task, run it via agents, then git commit+push."""
    task = _pick_self_task()
    if not task:
        _log("[self] no pending self-improvement tasks")
        return
    _log(f"[self] starting: {task}")
    lock = threading.Lock()
    _run_task(task, SELF_IMPROVEMENT, lock)
    subprocess.run(["git", "add", "-A"], cwd=str(BASE), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"self-improve: {task[:80]}"],
        cwd=str(BASE), capture_output=True,
    )
    subprocess.run(["git", "push"], cwd=str(BASE), capture_output=True)
    _log("[self] committed and pushed")


def main() -> None:
    parser = argparse.ArgumentParser(description="claw agents — multi-agent orchestrator")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("status", help="Show pending tasks and their agent routing")
    run_p = sub.add_parser("run", help="Dispatch all pending tasks to typed agents")
    run_p.add_argument("--dry-run", action="store_true")
    run_p.add_argument("--serial", action="store_true", help="Run sequentially instead of parallel")
    sub.add_parser("self-improve", help="Run one [self] task from SELF_IMPROVEMENT.md")
    args = parser.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(dry_run=getattr(args, "dry_run", False), serial=getattr(args, "serial", False))
    elif args.cmd == "self-improve":
        cmd_self_improve()
    else:
        # Daemon mode: weekdays 08:00, weekends 09:00, Sundays 10:00 self-improve
        _log("agents daemon starting — weekdays 08:00, weekends 09:00, Sundays 10:00 self-improve")
        fired_minute = -1
        while True:
            now = datetime.now()
            current_minute = now.hour * 60 + now.minute
            is_weekend = now.weekday() >= 5
            is_sunday = now.weekday() == 6
            target = DEFAULT_WEEKEND_TIME if is_weekend else DEFAULT_WEEKDAY_TIME
            if _should_run_now(target) and current_minute != fired_minute:
                fired_minute = current_minute
                cmd_run()
            elif is_sunday and _should_run_now(DEFAULT_SELF_TIME) and current_minute != fired_minute:
                fired_minute = current_minute
                cmd_self_improve()
            import time
            time.sleep(30)


if __name__ == "__main__":
    main()
