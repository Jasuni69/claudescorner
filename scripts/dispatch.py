"""
dispatch.py — Parallel autonomous agent dispatcher.

Reads tasks from tasks.json, spawns up to MAX_WORKERS concurrent claude.exe
subprocesses. No polling, no idle loops — pure event-driven execution.

Usage:
    python dispatch.py                  # run all pending tasks
    python dispatch.py --dry-run        # show what would run
    python dispatch.py --push "prompt"  # push a task and run
    python dispatch.py --category research  # run only tasks of this category
    python dispatch.py --list           # show queue

Task schema (tasks.json):
    [
        {
            "id": "unique-id",
            "priority": 1-5 (1=highest),
            "category": "infrastructure|research|skill|memory|journal|vault",
            "prompt": "...",
            "status": "pending|running|done|failed",
            "created": "ISO timestamp",
            "result_file": "logs/dispatch-<id>.txt",  # written on completion
            "bare": false  # optional: true = --bare mode (skips CLAUDE.md, hooks, auto-memory)
        }
    ]
"""
import argparse
import json
import os
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
TASKS_FILE = BASE / "tasks.json"
LOGS_DIR = BASE / "logs"
CLAUDE = r"C:\Users\JasonNicolini\.local\bin\claude.exe"
MAX_WORKERS = 3
TIMEOUT_SECONDS = 300  # 5 min per task

LOGS_DIR.mkdir(exist_ok=True)


# ── Queue management ──────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        return []
    return json.loads(TASKS_FILE.read_text(encoding="utf-8"))


def save_tasks(tasks: list[dict]) -> None:
    TASKS_FILE.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")


def push_task(prompt: str, category: str = "infrastructure", priority: int = 3, bare: bool = False) -> dict:
    tasks = load_tasks()
    task = {
        "id": str(uuid.uuid4())[:8],
        "priority": priority,
        "category": category,
        "prompt": prompt,
        "status": "pending",
        "created": datetime.now().isoformat(),
        "result_file": None,
        "bare": bare,
    }
    tasks.append(task)
    tasks.sort(key=lambda t: t["priority"])
    save_tasks(tasks)
    return task


def get_pending(tasks: list[dict], category: str | None = None) -> list[dict]:
    pending = [t for t in tasks if t["status"] == "pending"]
    if category:
        pending = [t for t in pending if t["category"] == category]
    return sorted(pending, key=lambda t: t["priority"])


def update_task(tasks: list[dict], task_id: str, **kwargs) -> None:
    for t in tasks:
        if t["id"] == task_id:
            t.update(kwargs)
            break
    save_tasks(tasks)


# ── Execution ─────────────────────────────────────────────────────────────────

def run_task(task: dict) -> tuple[str, bool, str]:
    """Run a single task. Returns (task_id, success, output)."""
    task_id = task["id"]
    result_file = LOGS_DIR / f"dispatch-{task_id}.txt"

    env = os.environ.copy()
    # Clear nested session guard
    for var in ("CLAUDECODE", "CLAUDE_CODE", "CLAUDE_CODE_ENTRYPOINT"):
        env.pop(var, None)

    try:
        cmd = [CLAUDE, "--permission-mode", "auto", "-p", task["prompt"], "--output-format", "text"]
        if task.get("bare"):
            cmd.insert(1, "--bare")
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_SECONDS,
            env=env,
            cwd=str(BASE),
        )
        output = proc.stdout.strip() or proc.stderr.strip()
        success = proc.returncode == 0
    except subprocess.TimeoutExpired:
        output = f"TIMEOUT after {TIMEOUT_SECONDS}s"
        success = False
    except Exception as e:
        output = f"ERROR: {e}"
        success = False

    result_file.write_text(output, encoding="utf-8")
    return task_id, success, str(result_file)


def dispatch(tasks: list[dict], pending: list[dict], dry_run: bool = False) -> None:
    if not pending:
        print("Queue empty — nothing to run.")
        return

    print(f"Dispatching {len(pending)} task(s) with up to {MAX_WORKERS} workers...\n")

    if dry_run:
        for t in pending:
            print(f"  [{t['priority']}] [{t['category']}] {t['id']} — {t['prompt'][:80]}")
        return

    # Mark all as running
    for t in pending:
        update_task(tasks, t["id"], status="running", started=datetime.now().isoformat())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(run_task, t): t for t in pending}
        for future in as_completed(futures):
            task = futures[future]
            task_id, success, result_file = future.result()
            status = "done" if success else "failed"
            update_task(
                tasks, task_id,
                status=status,
                result_file=result_file,
                finished=datetime.now().isoformat(),
            )
            icon = "OK" if success else "FAIL"
            print(f"  {icon} [{task['category']}] {task_id} -> {result_file}")

    done = sum(1 for t in tasks if t["id"] in {p["id"] for p in pending} and t["status"] == "done")
    failed = len(pending) - done
    print(f"\nDone: {done}  Failed: {failed}")


# ── Self-populate ─────────────────────────────────────────────────────────────

DEFAULT_AUTONOMOUS_TASKS = [
    {
        "category": "infrastructure",
        "priority": 1,
        "prompt": (
            "You are running autonomously. Check E:\\2026\\ClaudesCorner\\core\\HEARTBEAT.md "
            "for any pending [ ] tasks. Pick the highest-priority one and execute it. "
            "Update HEARTBEAT.md when done. If nothing actionable, respond HEARTBEAT_OK. "
            "VERIFY: If you executed a task, confirm the task is marked [x] in HEARTBEAT.md "
            "and a log entry was appended before finishing."
        ),
    },
    {
        "category": "research",
        "priority": 2,
        "prompt": (
            "You are running autonomously. Read E:\\2026\\ClaudesCorner\\research\\sources.md. "
            "Pick one source. Fetch it via browser. Find 1-2 high-signal posts relevant to "
            "Jason's work (AI agents, MCP, Microsoft Fabric, Claude Code). "
            "Clip them to E:\\2026\\ClaudesCorner\\research\\ as markdown files with frontmatter. "
            "Use mcp-obsidian for writes. Don't duplicate files already there today. "
            "VERIFY: After writing, read each file back and confirm it has non-empty frontmatter and body. "
            "If a file is empty or missing, re-write it before finishing."
        ),
    },
    {
        "category": "memory",
        "priority": 3,
        "prompt": (
            "You are running autonomously. Run memory hygiene: "
            "1) Check MEMORY.md index for stale/broken entries, fix them. "
            "2) Scan core/HEARTBEAT.md for tasks done in the last 7 days that aren't in MEMORY.md — add durable facts. "
            "3) If memory/YYYY-MM-DD.md for today doesn't exist, check if yesterday's has anything worth preserving. "
            "Write changes directly. No dry-run. "
            "VERIFY: After any writes, read MEMORY.md back and confirm new entries appear in the index. "
            "Report what was added or 'no changes needed' if clean."
        ),
    },
]


def populate_defaults() -> list[dict]:
    """Push default autonomous tasks if queue is empty."""
    tasks = load_tasks()
    pending = get_pending(tasks)
    if pending:
        return pending

    print("Queue empty — populating with default autonomous tasks...")
    for spec in DEFAULT_AUTONOMOUS_TASKS:
        push_task(spec["prompt"], spec["category"], spec["priority"])

    return get_pending(load_tasks())


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Parallel autonomous agent dispatcher")
    parser.add_argument("--dry-run", action="store_true", help="Show tasks without running")
    parser.add_argument("--push", metavar="PROMPT", help="Push a task and run the queue")
    parser.add_argument("--bare", action="store_true", help="Mark pushed task as bare (--bare mode, no CLAUDE.md)")
    parser.add_argument("--category", help="Filter to tasks of this category")
    parser.add_argument("--list", action="store_true", help="Show full queue")
    parser.add_argument("--clear-done", action="store_true", help="Remove completed/failed tasks")
    parser.add_argument("--populate", action="store_true", help="Push default tasks if queue empty")
    args = parser.parse_args()

    if args.clear_done:
        tasks = load_tasks()
        kept = [t for t in tasks if t["status"] == "pending"]
        removed = len(tasks) - len(kept)
        save_tasks(kept)
        print(f"Removed {removed} completed/failed tasks. {len(kept)} pending.")
        return

    if args.list:
        tasks = load_tasks()
        if not tasks:
            print("Queue is empty.")
            return
        for t in tasks:
            print(f"  [{t['status']:8}] [{t['priority']}] [{t['category']:14}] {t['id']} — {t['prompt'][:60]}")
        return

    if args.push:
        category = args.category or "infrastructure"
        task = push_task(args.push, category=category, bare=args.bare)
        print(f"Pushed task {task['id']} ({category}{'  --bare' if args.bare else ''})")

    if args.populate:
        populate_defaults()

    tasks = load_tasks()
    pending = get_pending(tasks, args.category)

    if not pending and not args.push:
        # Auto-populate if nothing queued
        pending = populate_defaults()
        tasks = load_tasks()

    dispatch(tasks, pending, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
