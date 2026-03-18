#!/usr/bin/env python3
"""
improve.py — CLI for SELF_IMPROVEMENT.md

Usage:
  python improve.py list          # show all pending [self] tasks
  python improve.py next          # show the next task to pick up
  python improve.py add <text>    # add a new [self] task
  python improve.py done <n>      # mark task #n as done (1-indexed from list)
"""
import re
import sys
from pathlib import Path

SELF_IMPROVEMENT = Path(__file__).parent.parent / "SELF_IMPROVEMENT.md"
TASK_RE = re.compile(r"^(\s*-\s)\[([ x])\](\s\[self\].+)$", re.MULTILINE)


def _read() -> str:
    return SELF_IMPROVEMENT.read_text(encoding="utf-8")


def _write(text: str) -> None:
    SELF_IMPROVEMENT.write_text(text, encoding="utf-8")


def _pending(text: str) -> list[tuple[int, str]]:
    """Return [(line_index, task_text), ...] for unchecked tasks."""
    results = []
    for i, line in enumerate(text.splitlines()):
        m = re.match(r"^\s*-\s\[ \]\s(\[self\].+)$", line)
        if m:
            results.append((i, m.group(1)))
    return results


def cmd_list() -> None:
    text = _read()
    tasks = _pending(text)
    if not tasks:
        print("No pending tasks.")
        return
    for n, (_, task) in enumerate(tasks, 1):
        print(f"  {n}. {task}")


def cmd_next() -> None:
    text = _read()
    tasks = _pending(text)
    if not tasks:
        print("No pending tasks.")
        return
    print(tasks[0][1])


def cmd_add(task_text: str) -> None:
    text = _read()
    if not task_text.startswith("[self]"):
        task_text = f"[self] {task_text}"
    # Insert before first unchecked task, or at end of Backlog section
    lines = text.splitlines(keepends=True)
    insert_at = len(lines)
    for i, line in enumerate(lines):
        if re.match(r"^\s*-\s\[ \]\s\[self\]", line):
            insert_at = i
            break
    lines.insert(insert_at, f"- [ ] {task_text}\n")
    _write("".join(lines))
    print(f"Added: {task_text}")


def cmd_done(n: int) -> None:
    text = _read()
    tasks = _pending(text)
    if n < 1 or n > len(tasks):
        print(f"Invalid task number: {n} (have {len(tasks)})")
        sys.exit(1)
    line_idx, task = tasks[n - 1]
    lines = text.splitlines(keepends=True)
    lines[line_idx] = lines[line_idx].replace("- [ ]", "- [x]", 1)
    _write("".join(lines))
    print(f"Done: {task}")


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "next":
        cmd_next()
    elif args[0] == "add":
        if len(args) < 2:
            print("Usage: improve.py add <task text>")
            sys.exit(1)
        cmd_add(" ".join(args[1:]))
    elif args[0] == "done":
        if len(args) < 2:
            print("Usage: improve.py done <n>")
            sys.exit(1)
        cmd_done(int(args[1]))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
