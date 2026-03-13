#!/usr/bin/env python3
"""
deadlines.py — live terminal countdown from DEADLINES.md
Format in DEADLINES.md:
  - 2026-03-20 Sprint review
  - 2026-04-01 Tax deadline
"""

import time
import os
import sys
from datetime import datetime, date
from pathlib import Path

BASE = Path(__file__).parent.parent
DEADLINES_FILE = BASE / "DEADLINES.md"
REFRESH = 1  # seconds


def parse_deadlines(path: Path) -> list[tuple[date, str]]:
    deadlines = []
    if not path.exists():
        return deadlines
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("-").strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        try:
            d = datetime.strptime(parts[0], "%Y-%m-%d").date()
            deadlines.append((d, parts[1].strip()))
        except ValueError:
            continue
    return sorted(deadlines)


def fmt_delta(target: date) -> str:
    today = date.today()
    delta = (target - today).days
    if delta < 0:
        return f"\033[90m{abs(delta)}d ago\033[0m"
    if delta == 0:
        return "\033[91mTODAY\033[0m"
    if delta <= 3:
        return f"\033[91m{delta}d\033[0m"
    if delta <= 14:
        return f"\033[93m{delta}d\033[0m"
    return f"\033[92m{delta}d\033[0m"


def render(deadlines: list[tuple[date, str]]) -> None:
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\033[1m⏱  DEADLINES\033[0m  \033[90m{now}\033[0m\n")
    if not deadlines:
        print("  No deadlines found. Add entries to DEADLINES.md")
        print("  Format:  - 2026-03-20 Sprint review")
        return
    for d, label in deadlines:
        delta_str = fmt_delta(d)
        date_str = d.strftime("%Y-%m-%d")
        print(f"  {date_str}  {delta_str:>20}  {label}")
    print(f"\n\033[90mFile: {DEADLINES_FILE}  |  Ctrl+C to exit\033[0m")


def main() -> None:
    print("Loading deadlines... (Ctrl+C to quit)")
    try:
        while True:
            deadlines = parse_deadlines(DEADLINES_FILE)
            render(deadlines)
            time.sleep(REFRESH)
    except KeyboardInterrupt:
        print("\nBye.")
        sys.exit(0)


if __name__ == "__main__":
    main()
