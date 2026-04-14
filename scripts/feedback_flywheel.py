"""
feedback_flywheel.py — weekly retrospective script

Scans recent daily memory logs for recurring corrections, patterns,
and things that went wrong. Produces a summary prompt for Claude to
codify durable lessons into SOUL.md Preferences or new skills.

Usage:
    python scripts/feedback_flywheel.py [--days 14]

Output:
    memory/flywheel-YYYY-MM-DD.md  — ready-to-review summary
"""
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
MEMORY_DIR = BASE / "memory"
SOUL = BASE / "core" / "SOUL.md"
SELF_IMPROVEMENT = BASE / "core" / "SELF_IMPROVEMENT.md"

# Keywords that signal corrections, failures, or lessons
CORRECTION_PATTERNS = [
    r"\bfixed\b", r"\bbug\b", r"\bwrong\b", r"\bchanged approach\b",
    r"\bblocker\b", r"\bworkaround\b", r"\bbroken\b", r"\bfailed\b",
    r"\bincorrect\b", r"\bmistake\b", r"\bshould have\b", r"\bdon't\b",
    r"\bnever\b", r"\bavoid\b", r"\broot cause\b", r"\btypo\b",
]
CORRECTION_RE = re.compile("|".join(CORRECTION_PATTERNS), re.IGNORECASE)


def collect_daily_logs(days: int) -> list[tuple[str, str]]:
    """Return list of (date_str, content) for recent daily logs."""
    results = []
    cutoff = datetime.now() - timedelta(days=days)
    for f in sorted(MEMORY_DIR.glob("20*.md"), reverse=True):
        try:
            date = datetime.strptime(f.stem, "%Y-%m-%d")
        except ValueError:
            continue
        if date < cutoff:
            break
        results.append((f.stem, f.read_text(encoding="utf-8")))
    return results


def extract_corrections(logs: list[tuple[str, str]]) -> list[dict]:
    """Pull lines containing correction signals from daily logs."""
    hits = []
    for date, content in logs:
        for i, line in enumerate(content.splitlines()):
            if CORRECTION_RE.search(line) and len(line.strip()) > 20:
                hits.append({"date": date, "line": line.strip()})
    return hits


def extract_preferences() -> list[str]:
    """Read current SOUL.md Preferences section."""
    text = SOUL.read_text(encoding="utf-8")
    in_prefs = False
    prefs = []
    for line in text.splitlines():
        if "## Preferences I" in line:
            in_prefs = True
            continue
        if in_prefs and line.startswith("##"):
            break
        if in_prefs and line.strip():
            prefs.append(line.strip())
    return prefs


def write_flywheel_report(days: int) -> Path:
    logs = collect_daily_logs(days)
    corrections = extract_corrections(logs)
    prefs = extract_preferences()
    today = datetime.now().strftime("%Y-%m-%d")
    out = MEMORY_DIR / f"flywheel-{today}.md"

    lines = [
        f"# Feedback Flywheel — {today}",
        f"\nScanned last {days} days across {len(logs)} daily log(s).",
        f"Found {len(corrections)} correction signals.\n",
        "---\n",
        "## Corrections & Lessons\n",
    ]

    if not corrections:
        lines.append("_No corrections found in this period._\n")
    else:
        for c in corrections:
            lines.append(f"- `{c['date']}` {c['line']}")
        lines.append("")

    lines += [
        "---\n",
        "## Current SOUL.md Preferences\n",
    ]
    for p in prefs:
        lines.append(p)

    lines += [
        "",
        "---\n",
        "## Action Prompt\n",
        "Review the corrections above. For each recurring pattern:\n",
        "1. If it's a new durable rule → add to SOUL.md `## Preferences I've Learned`",
        "2. If it's a skill gap → add to SELF_IMPROVEMENT.md",
        "3. If it's already in SOUL.md → verify it's still accurate\n",
        "Delete this file after acting on it.\n",
    ]

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Flywheel report written to {out}")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14)
    args = parser.parse_args()
    write_flywheel_report(args.days)
