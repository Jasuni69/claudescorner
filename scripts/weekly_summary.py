"""weekly_summary.py — append a Self-Improvement Summary section to today's daily log.

Usage:
    python weekly_summary.py            # write to memory/YYYY-MM-DD.md
    python weekly_summary.py --dry-run  # print to stdout only
    python weekly_summary.py --since N  # include completions in last N days (default: 7)
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SELF_IMPROVEMENT = ROOT / "SELF_IMPROVEMENT.md"
MEMORY_DIR = ROOT / "memory"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Append weekly self-improvement summary to daily log")
    p.add_argument("--dry-run", action="store_true", help="Print output without writing")
    p.add_argument("--since", type=int, default=7, metavar="N", help="Days to look back (default: 7)")
    return p.parse_args()


def load_completed_tasks(path: Path) -> list[str]:
    """Return all [x] task lines from SELF_IMPROVEMENT.md."""
    text = path.read_text(encoding="utf-8")
    return re.findall(r"- \[x\] \[self\] (.+)", text)


def load_open_tasks(path: Path) -> list[str]:
    """Return all [ ] task lines from SELF_IMPROVEMENT.md (skip template/example lines)."""
    text = path.read_text(encoding="utf-8")
    tasks = re.findall(r"- \[ \] \[self\] (.+)", text)
    # Filter out the format example line (literal `<task>` placeholder)
    return [t for t in tasks if not t.startswith("<")]


def build_summary(completed: list[str], open_tasks: list[str], since_days: int) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        f"## Self-Improvement Summary ({today})",
        "",
        f"**Completed tasks (all-time):** {len(completed)}  ",
        f"**Open tasks remaining:** {len(open_tasks)}",
        "",
        "### Completed",
    ]
    for task in completed:
        lines.append(f"- [x] {task}")
    lines.append("")
    if open_tasks:
        lines.append("### Open")
        for task in open_tasks:
            lines.append(f"- [ ] {task}")
        lines.append("")
    return "\n".join(lines)


def today_log_path() -> Path:
    return MEMORY_DIR / f"{datetime.date.today().isoformat()}.md"


def main() -> None:
    args = parse_args()

    if not SELF_IMPROVEMENT.exists():
        print(f"ERROR: {SELF_IMPROVEMENT} not found", file=sys.stderr)
        sys.exit(1)

    completed = load_completed_tasks(SELF_IMPROVEMENT)
    open_tasks = load_open_tasks(SELF_IMPROVEMENT)
    summary = build_summary(completed, open_tasks, args.since)

    if args.dry_run:
        print(summary)
        return

    log_path = today_log_path()
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        # Don't double-append
        if "## Self-Improvement Summary" in existing:
            print(f"Summary already present in {log_path.name} — skipping.")
            return
        log_path.write_text(existing.rstrip() + "\n\n" + summary + "\n", encoding="utf-8")
    else:
        log_path.write_text(summary + "\n", encoding="utf-8")

    print(f"OK: summary written to {log_path}")


if __name__ == "__main__":
    main()
