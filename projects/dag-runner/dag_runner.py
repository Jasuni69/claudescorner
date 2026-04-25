"""
dag_runner.py — run a YAML task DAG in topological order.

Usage:
  python dag_runner.py <dag.yaml> [--dry-run] [--fail-fast]

YAML schema:
  tasks:
    task_name:
      cmd: "shell command to run"
      depends_on: [other_task, ...]   # optional
      env: {KEY: VALUE}               # optional extra env vars

Exit codes: 0 = all passed, 1 = any failed, 2 = bad input / cycle detected.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ── Data model ──────────────────────────────────────────────────────────────

@dataclass
class Task:
    name: str
    cmd: str
    depends_on: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)

    # filled after run
    status: str = "pending"   # pending | ok | failed | skipped
    duration: float = 0.0
    returncode: Optional[int] = None


# ── DAG loading ─────────────────────────────────────────────────────────────

def load_dag(path: Path) -> dict[str, Task]:
    with path.open() as f:
        raw = yaml.safe_load(f)

    tasks_raw = raw.get("tasks", {})
    if not tasks_raw:
        print("ERROR: no 'tasks' key found in YAML", file=sys.stderr)
        sys.exit(2)

    tasks: dict[str, Task] = {}
    for name, spec in tasks_raw.items():
        if not isinstance(spec, dict) or "cmd" not in spec:
            print(f"ERROR: task '{name}' missing 'cmd'", file=sys.stderr)
            sys.exit(2)
        tasks[name] = Task(
            name=name,
            cmd=spec["cmd"],
            depends_on=spec.get("depends_on") or [],
            env={str(k): str(v) for k, v in (spec.get("env") or {}).items()},
        )

    # validate all depends_on references exist
    for t in tasks.values():
        for dep in t.depends_on:
            if dep not in tasks:
                print(f"ERROR: '{t.name}' depends on unknown task '{dep}'", file=sys.stderr)
                sys.exit(2)

    return tasks


# ── Topological sort (Kahn's algorithm) ─────────────────────────────────────

def topo_sort(tasks: dict[str, Task]) -> list[str]:
    in_degree: dict[str, int] = {name: 0 for name in tasks}
    dependents: dict[str, list[str]] = {name: [] for name in tasks}

    for t in tasks.values():
        for dep in t.depends_on:
            in_degree[t.name] += 1
            dependents[dep].append(t.name)

    queue: deque[str] = deque(name for name, deg in in_degree.items() if deg == 0)
    order: list[str] = []

    while queue:
        name = queue.popleft()
        order.append(name)
        for child in dependents[name]:
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    if len(order) != len(tasks):
        cycle_nodes = [n for n in tasks if n not in order]
        print(f"ERROR: cycle detected involving: {', '.join(cycle_nodes)}", file=sys.stderr)
        sys.exit(2)

    return order


# ── Execution ────────────────────────────────────────────────────────────────

GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def run_task(task: Task, dry_run: bool) -> None:
    env = {**os.environ, **task.env}
    print(f"  {BOLD}> {task.name}{RESET}  {task.cmd}")
    if dry_run:
        task.status = "ok"
        return

    t0 = time.monotonic()
    result = subprocess.run(task.cmd, shell=True, env=env)
    task.duration = time.monotonic() - t0
    task.returncode = result.returncode
    task.status = "ok" if result.returncode == 0 else "failed"


def run_dag(tasks: dict[str, Task], order: list[str], dry_run: bool, fail_fast: bool) -> int:
    failed_upstream: set[str] = set()
    any_failed = False

    for name in order:
        task = tasks[name]
        blocked = [d for d in task.depends_on if tasks[d].status != "ok"]

        if blocked:
            task.status = "skipped"
            failed_upstream.add(name)
            print(f"\n{YELLOW}SKIP{RESET} {name} (blocked by: {', '.join(blocked)})")
            continue

        print(f"\n{BOLD}[{order.index(name)+1}/{len(order)}]{RESET} {name}")
        run_task(task, dry_run)

        if task.status == "ok":
            label = "(dry-run)" if dry_run else f"{task.duration:.1f}s"
            print(f"  {GREEN}OK{RESET}  {label}")
        else:
            print(f"  {RED}FAILED{RESET}  rc={task.returncode}")
            any_failed = True
            if fail_fast:
                break

    return 1 if any_failed else 0


# ── Summary table ─────────────────────────────────────────────────────────────

def print_summary(tasks: dict[str, Task], order: list[str]) -> None:
    print(f"\n{'-'*52}")
    print(f"{'TASK':<24} {'STATUS':<10} {'TIME':>6}")
    print(f"{'-'*52}")
    for name in order:
        t = tasks[name]
        if t.status == "ok":
            color = GREEN
        elif t.status == "failed":
            color = RED
        else:
            color = YELLOW
        dur = f"{t.duration:.1f}s" if t.duration else "-"
        print(f"{name:<24} {color}{t.status:<10}{RESET} {dur:>6}")
    print(f"{'-'*52}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Run a YAML task DAG in dependency order.")
    parser.add_argument("dag", type=Path, help="Path to DAG YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print commands, don't run them")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    args = parser.parse_args()

    if not args.dag.exists():
        print(f"ERROR: file not found: {args.dag}", file=sys.stderr)
        sys.exit(2)

    tasks = load_dag(args.dag)
    order = topo_sort(tasks)

    mode = " (DRY RUN)" if args.dry_run else ""
    print(f"{BOLD}dag-runner{RESET}{mode} - {len(tasks)} tasks, execution order: {' -> '.join(order)}")

    rc = run_dag(tasks, order, args.dry_run, args.fail_fast)
    print_summary(tasks, order)
    sys.exit(rc)


if __name__ == "__main__":
    main()
