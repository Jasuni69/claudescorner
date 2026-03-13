#!/usr/bin/env python3
"""
claw.py — autonomous agent runner for Claude's Corner.
Reads ## Pending Tasks from HEARTBEAT.md, dispatches each via claude.exe,
marks done, and logs results.

Usage:
  python claw.py status              # show pending/done counts
  python claw.py run                 # dispatch all pending tasks
  python claw.py run --dry-run       # show tasks without running
  python claw.py schedule --daily 08:00      # run daily at HH:MM
  python claw.py schedule --weekend 09:00    # run Sat+Sun at HH:MM
  python claw.py schedule --interval 3600    # run every N seconds
"""
import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent.parent  # → E:\2026\Claude's Corner
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
CLAUDE = Path(r"C:\Users\JasonNicolini\.local\bin\claude.exe")
LOG = BASE / "logs" / "claw.log"
MAX_TURNS = 30
# Schedule defaults — used when launched with no args
DEFAULT_WEEKDAY_TIME = "08:00"   # Mon–Fri: check + run pending tasks
DEFAULT_WEEKEND_TIME = "09:00"   # Sat–Sun: longer build window
SECTION_RE = re.compile(r"^## Pending Tasks\s*$", re.MULTILINE)


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def parse_tasks(text: str) -> list[str]:
    """Extract unchecked tasks from ## Pending Tasks section."""
    match = SECTION_RE.search(text)
    if not match:
        return []
    section = text[match.end():]
    # Stop at next ## heading
    next_heading = re.search(r"^##\s", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return re.findall(r"^\s*-\s\[ \]\s(.+)$", section, re.MULTILINE)


def count_done(text: str) -> int:
    match = SECTION_RE.search(text)
    if not match:
        return 0
    section = text[match.end():]
    next_heading = re.search(r"^##\s", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return len(re.findall(r"^\s*-\s\[x\]\s.+$", section, re.MULTILINE | re.IGNORECASE))


def mark_done(text: str, task: str) -> str:
    escaped = re.escape(task)
    return re.sub(
        rf"^(\s*-\s)\[ \](\s{escaped})$",
        r"\1[x]\2",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def dispatch(task: str) -> str:
    if not CLAUDE.exists():
        return f"[error] claude not found at {CLAUDE}"
    try:
        result = subprocess.run(
            [
                str(CLAUDE),
                "--dangerously-skip-permissions",
                "--max-turns", str(MAX_TURNS),
                "-p", task,
                "--output-format", "text",
            ],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(BASE),
        )
        out = (result.stdout + result.stderr).strip()
        return out or "[no output]"
    except subprocess.TimeoutExpired:
        return "[error] timed out after 300s"
    except Exception as e:
        return f"[error] {e}"


def cmd_status() -> None:
    if not HEARTBEAT.exists():
        print(f"HEARTBEAT not found: {HEARTBEAT}")
        sys.exit(1)
    text = HEARTBEAT.read_text(encoding="utf-8")
    pending = parse_tasks(text)
    done = count_done(text)
    print(f"Pending: {len(pending)}  Done: {done}")
    for t in pending:
        print(f"  [ ] {t}")


def cmd_run(dry_run: bool = False) -> None:
    if not HEARTBEAT.exists():
        _log(f"HEARTBEAT not found: {HEARTBEAT}")
        sys.exit(1)
    text = HEARTBEAT.read_text(encoding="utf-8")
    tasks = parse_tasks(text)
    if not tasks:
        _log("No pending tasks found in HEARTBEAT.md")
        return
    _log(f"Found {len(tasks)} pending task(s)")
    for task in tasks:
        _log(f"Dispatching: {task}")
        if dry_run:
            _log("[dry-run] skipped")
            continue
        output = dispatch(task)
        _log(f"Result ({len(output)} chars):\n{output[:500]}")
        text = mark_done(text, task)
        HEARTBEAT.write_text(text, encoding="utf-8")
        _log(f"Marked done: {task}")
    _log("claw run complete")


def _should_run_now(mode: str, target_time: str) -> bool:
    """Return True if current time matches the schedule."""
    now = datetime.now()
    h, m = map(int, target_time.split(":"))
    if now.hour != h or now.minute != m:
        return False
    if mode == "weekend":
        return now.weekday() >= 5  # Sat=5, Sun=6
    return True  # daily


def cmd_schedule(mode: str, target_time: str | None, interval: int | None) -> None:
    if interval:
        _log(f"Scheduler started — interval every {interval}s")
        while True:
            cmd_run()
            time.sleep(interval)
    else:
        _log(f"Scheduler started — {mode} at {target_time}")
        fired_minute = -1
        while True:
            now = datetime.now()
            current_minute = now.hour * 60 + now.minute
            if _should_run_now(mode, target_time) and current_minute != fired_minute:
                fired_minute = current_minute
                cmd_run()
            time.sleep(30)


def main() -> None:
    parser = argparse.ArgumentParser(description="claw — autonomous task runner")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("status", help="Show pending/done task counts")
    run_p = sub.add_parser("run", help="Dispatch all pending tasks")
    run_p.add_argument("--dry-run", action="store_true", help="Parse tasks without running")
    sched_p = sub.add_parser("schedule", help="Run on a schedule (blocks)")
    sched_grp = sched_p.add_mutually_exclusive_group(required=True)
    sched_grp.add_argument("--daily", metavar="HH:MM", help="Run every day at this time")
    sched_grp.add_argument("--weekend", metavar="HH:MM", help="Run Sat+Sun at this time")
    sched_grp.add_argument("--interval", type=int, metavar="SECONDS", help="Run every N seconds")
    args = parser.parse_args()

    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(dry_run=getattr(args, "dry_run", False))
    elif args.cmd == "schedule":
        if args.interval:
            cmd_schedule("interval", None, args.interval)
        elif args.daily:
            cmd_schedule("daily", args.daily, None)
        elif args.weekend:
            cmd_schedule("weekend", args.weekend, None)
    else:
        # No subcommand — run the self-managed schedule
        _log("claw daemon starting — weekdays 08:00, weekends 09:00")
        fired_minute = -1
        while True:
            now = datetime.now()
            current_minute = now.hour * 60 + now.minute
            is_weekend = now.weekday() >= 5
            target = DEFAULT_WEEKEND_TIME if is_weekend else DEFAULT_WEEKDAY_TIME
            if _should_run_now("daily", target) and current_minute != fired_minute:
                fired_minute = current_minute
                cmd_run()
            time.sleep(30)


if __name__ == "__main__":
    main()
