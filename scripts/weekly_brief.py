#!/usr/bin/env python3
"""
weekly_brief.py — Synthesize a short weekly brief from memory files.
Reads the most recent sections of fabric-news.md, claude-updates.md,
reddit-feed-notes.md, and HEARTBEAT.md, then writes memory/weekly-brief.md.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent.parent
MEMORY = BASE / "memory"
CORE = BASE / "core"
OUT = MEMORY / "weekly-brief.md"


def last_section(text: str, n: int = 1) -> str:
    """Return the last n ## sections from a markdown file."""
    sections = re.split(r"\n(?=## )", text.strip())
    return "\n\n".join(sections[-n:]) if sections else text[-2000:]


def extract_pending_tasks(heartbeat: str) -> list[str]:
    tasks = []
    in_block = False
    for line in heartbeat.splitlines():
        if line.strip() == "## Pending Tasks":
            in_block = True
            continue
        if in_block and line.startswith("## "):
            break
        if in_block and line.startswith("- [ ]"):
            tasks.append(line.strip())
    return tasks


def build_brief() -> str:
    fabric_news = (MEMORY / "fabric-news.md").read_text(encoding="utf-8")
    cc_updates = (MEMORY / "claude-updates.md").read_text(encoding="utf-8")
    reddit = (MEMORY / "reddit-feed-notes.md").read_text(encoding="utf-8")
    heartbeat = (CORE / "HEARTBEAT.md").read_text(encoding="utf-8")

    fabric_recent = last_section(fabric_news, 2)
    cc_recent = last_section(cc_updates, 2)
    reddit_recent = last_section(reddit, 1)
    pending = extract_pending_tasks(heartbeat)

    date = datetime.now().strftime("%Y-%m-%d")
    pending_md = "\n".join(f"  {t}" for t in pending) if pending else "  (none)"

    brief = f"""# Weekly Brief — {date}

## Fabric & Microsoft tooling

{fabric_recent}

---

## Claude Code updates

{cc_recent}

---

## Community signals (Reddit)

{reddit_recent}

---

## Open blockers / pending tasks

{pending_md}
"""
    return brief


def main() -> None:
    brief = build_brief()
    OUT.write_text(brief, encoding="utf-8")
    print(f"[weekly_brief] written to {OUT}")


if __name__ == "__main__":
    main()
