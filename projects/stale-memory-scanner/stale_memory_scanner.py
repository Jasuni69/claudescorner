"""stale_memory_scanner.py -- flag stale project-state entries in memory/*.md files.

Usage:
    python stale_memory_scanner.py [--days N] [--out FILE] [--memory-dir DIR]

Reads all *.md files in the memory dir, identifies entries older than N days
(default 30) that reference transient project state (not permanent facts),
and produces a pruning-candidate report.

Exit codes: 0 = nothing stale, 1 = stale entries found.
"""

import re
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

MEMORY_DIR = Path(r"E:\2026\ClaudesCorner\memory")

# Keywords that suggest transient project state (vs durable facts)
STATE_KEYWORDS = [
    "blocked", "pending", "running", "active", "in progress",
    "built", "created", "deployed", "fixed", "resolved",
    "wired", "scheduled", "waiting", "next step", "todo",
    "phase 1", "phase 2", "phase 3", "v1", "v2", "v3",
    "sprint", "pr #", "pull request", "issue #",
]

# Keywords that suggest a durable fact (lower priority for pruning)
FACT_KEYWORDS = [
    "always", "never", "prefer", "rule:", "note:", "fact:",
    "token", "api", "endpoint", "url", "path:", "config",
    "password", "credential", "key:", "format:", "pattern:",
]

DATE_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
DATE_HEADER_RE = re.compile(r"^#{1,3}\s+(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def parse_file_date(path: Path) -> date | None:
    m = DATE_FILENAME_RE.match(path.name)
    if m:
        try:
            return date.fromisoformat(m.group(1))
        except ValueError:
            return None
    return None


def extract_dated_sections(text: str) -> list[tuple[date, str]]:
    """Split a file into (date, section_text) pairs using ## YYYY-MM-DD headers."""
    matches = list(DATE_HEADER_RE.finditer(text))
    if not matches:
        return []
    sections = []
    for i, m in enumerate(matches):
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((d, text[start:end]))
    return sections


def is_state_heavy(text: str) -> bool:
    lower = text.lower()
    state_hits = sum(1 for kw in STATE_KEYWORDS if kw in lower)
    fact_hits = sum(1 for kw in FACT_KEYWORDS if kw in lower)
    return state_hits > fact_hits and state_hits >= 2


def scan_memory(memory_dir: Path, cutoff: date) -> list[dict]:
    """Return list of stale candidate entries."""
    candidates = []

    for path in sorted(memory_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")

        file_date = parse_file_date(path)

        if file_date:
            # Date-named daily log file
            if file_date < cutoff and is_state_heavy(text):
                candidates.append({
                    "file": path.name,
                    "date": file_date,
                    "reason": "daily log older than cutoff with project-state content",
                    "preview": text[:300].strip(),
                })
        else:
            # Non-date-named file: look for dated sections
            sections = extract_dated_sections(text)
            if sections:
                stale_sections = [(d, s) for d, s in sections if d < cutoff and is_state_heavy(s)]
                if stale_sections:
                    candidates.append({
                        "file": path.name,
                        "date": min(d for d, _ in stale_sections),
                        "stale_sections": len(stale_sections),
                        "total_sections": len(sections),
                        "reason": f"{len(stale_sections)}/{len(sections)} sections stale",
                        "preview": stale_sections[0][1][:300].strip(),
                    })
            else:
                # No date headers: check file mtime as proxy
                mtime = date.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff and is_state_heavy(text):
                    candidates.append({
                        "file": path.name,
                        "date": mtime,
                        "reason": "undated file, mtime older than cutoff, state-heavy content",
                        "preview": text[:300].strip(),
                    })

    return sorted(candidates, key=lambda c: c["date"])


def build_report(candidates: list[dict], cutoff: date, days: int) -> str:
    today = date.today().isoformat()
    lines = [
        f"# Stale Memory Scan — {today}",
        f"",
        f"Cutoff: {cutoff.isoformat()} (entries older than {days} days)",
        f"Candidates: {len(candidates)}",
        "",
    ]

    if not candidates:
        lines.append("No stale project-state entries found. Memory looks clean.")
        return "\n".join(lines)

    lines.append("## Pruning Candidates\n")
    for c in candidates:
        lines.append(f"### `{c['file']}`")
        lines.append(f"- **Date:** {c['date']}")
        lines.append(f"- **Reason:** {c['reason']}")
        if "stale_sections" in c:
            lines.append(f"- **Stale sections:** {c['stale_sections']} of {c['total_sections']}")
        lines.append(f"- **Preview:**")
        lines.append(f"  ```")
        for preview_line in c["preview"].splitlines()[:6]:
            lines.append(f"  {preview_line}")
        lines.append(f"  ```")
        lines.append("")

    lines += [
        "## Suggested Actions",
        "",
        "- Daily logs older than 30 days: safe to delete if summarised in MEMORY.md",
        "- Non-date files with stale sections: review and remove or archive outdated sections",
        "- Undated state-heavy files: check if content is still accurate before keeping",
        "",
        "> Run: python stale_memory_scanner.py --out pruning-report.md",
    ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan memory/*.md for stale project-state entries")
    parser.add_argument("--days", type=int, default=30, help="Age threshold in days (default: 30)")
    parser.add_argument("--out", help="Write report to this file instead of stdout")
    parser.add_argument("--memory-dir", default=str(MEMORY_DIR), help="Memory directory to scan")
    args = parser.parse_args()

    memory_dir = Path(args.memory_dir)
    if not memory_dir.exists():
        print(f"Error: memory dir not found: {memory_dir}", file=sys.stderr)
        sys.exit(2)

    cutoff = date.today() - timedelta(days=args.days)
    candidates = scan_memory(memory_dir, cutoff)
    report = build_report(candidates, cutoff, args.days)

    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Report written to {args.out} ({len(candidates)} candidates)")
    else:
        sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()

    sys.exit(1 if candidates else 0)


if __name__ == "__main__":
    main()
