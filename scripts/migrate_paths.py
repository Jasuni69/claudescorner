"""
migrate_paths.py — Run AFTER renaming "ClaudesCorner" to "ClaudesCorner"
Replaces all path references across configs, scripts, and skills.
Run from any directory: python E:\2026\ClaudesCorner\scripts\migrate_paths.py
"""

import os
import json
from pathlib import Path

OLD = "E:\\2026\\ClaudesCorner"
NEW = "E:\\2026\\ClaudesCorner"
OLD_POSIX = "E:/2026/ClaudesCorner"
NEW_POSIX = "E:/2026/ClaudesCorner"

HOME = Path(os.environ["USERPROFILE"])
CLAUDE_DIR = HOME / ".claude"

# Work from whichever path currently exists
BASE = Path(NEW) if Path(NEW).exists() else Path(OLD)

TARGETS = [
    # Claude CLI configs
    CLAUDE_DIR / "settings.json",
    CLAUDE_DIR / "settings.local.json",
    CLAUDE_DIR / "CLAUDE.md",
    # Skills / commands
    *list((CLAUDE_DIR / "commands").glob("*.md")),
    # Scheduled tasks
    *list((CLAUDE_DIR / "scheduled-tasks").rglob("*.md")),
    *list((CLAUDE_DIR / "scheduled-tasks").rglob("*.json")),
    # Tasks / teams
    *list((CLAUDE_DIR / "tasks").rglob("*.json")),
    *list((CLAUDE_DIR / "teams").rglob("*.json")),
    # Hooks
    Path("C:/claude-hooks/on_stop.py"),
    # Scripts
    *list((BASE / "scripts").glob("*.py")),
    *list((BASE / "scripts").glob("*.ps1")),
    *list((BASE / "scripts").glob("*.bat")),
    # Core
    *list((BASE / "core").glob("*.md")),
    *list((BASE / "core").glob("*.json")),
    # Memory
    BASE / "MEMORY.md",
    *list((BASE / "memory").glob("*.md")),
    # Journal
    *list((BASE / "journal").glob("*.md")),
]

replaced = 0
for path in TARGETS:
    if not path.exists():
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        new_text = text.replace(OLD, NEW).replace(OLD_POSIX, NEW_POSIX)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"  updated: {path}")
            replaced += 1
    except Exception as e:
        print(f"  ERROR {path}: {e}")

print(f"\nDone. {replaced} files updated.")
