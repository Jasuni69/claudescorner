"""
autodream.py — Weekly memory consolidation pass.

Scans memory/*.md for:
- Stale/superseded files (flag for deletion)
- Duplicate facts across files
- Gaps: things in HEARTBEAT log not captured elsewhere
- Outdated entries in MEMORY.md index

Writes output to memory/autodream-YYYY-MM-DD.md and appends a summary
to HEARTBEAT.md log.

Usage:
    python autodream.py [--dry-run]
"""
import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(r"E:\2026\ClaudesCorner")
MEMORY_DIR = BASE / "memory"
HEARTBEAT = BASE / "core" / "HEARTBEAT.md"
MEMORY_INDEX = BASE / "MEMORY.md"

# Files that are ephemeral by nature — don't flag these as stale
EPHEMERAL = {"reddit-brief.md", "x-brief.md", "weekly-brief.md"}

# Files that are reference docs — never stale
REFERENCE = {
    "research-notes.md", "claude-updates.md", "fabric-news.md",
    "dax-notes.md", "dp700-study.md", "dp700-cicd-notes.md",
    "dp700-rti-notes.md", "reference_agent_patterns.md",
    "openclaw-study.md", "project-clementine-status.md",
}

# Days after which a daily log is considered old enough to audit
DAILY_LOG_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
STALE_DAYS = 60


def _age_days(path: Path) -> int:
    mtime = path.stat().st_mtime
    return int((datetime.now().timestamp() - mtime) / 86400)


def scan_stale(files: list[Path]) -> list[tuple[Path, str]]:
    """Return files that look stale with reason."""
    stale = []
    for f in files:
        name = f.name
        if name in EPHEMERAL or name in REFERENCE:
            continue
        if name.startswith("autodream-"):
            continue
        if name.startswith("flywheel-"):
            stale.append((f, "flywheel output — should be deleted after review"))
            continue
        age = _age_days(f)
        if DAILY_LOG_PATTERN.match(name) and age > STALE_DAYS:
            stale.append((f, f"daily log {age}d old — consider archiving"))
            continue
        # Check for very small files (likely leftover stubs)
        size = f.stat().st_size
        if size < 50:
            stale.append((f, f"tiny file ({size}b) — likely a stub or test artifact"))
    return stale


def scan_memory_index(index_path: Path, memory_files: set[str]) -> list[str]:
    """Find MEMORY.md entries pointing to files that don't exist."""
    if not index_path.exists():
        return []
    broken = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\[.*?\]\((.+?\.md)\)", line)
        if m:
            ref = m.group(1)
            # ref is relative to memory/ dir
            candidate = MEMORY_DIR / ref
            global_candidate = BASE / "memory" / ref  # same thing
            if not candidate.exists() and not global_candidate.exists():
                broken.append(f"MEMORY.md refs missing file: {ref}")
    return broken


def check_heartbeat_uncaptured(heartbeat: Path) -> list[str]:
    """Find HEARTBEAT log entries that seem unresolved."""
    if not heartbeat.exists():
        return []
    content = heartbeat.read_text(encoding="utf-8")
    uncaptured = []
    for line in content.splitlines():
        # Look for TODO/blocker/fix items not yet checked off
        if re.match(r"^- \[ \]", line):
            uncaptured.append(line.strip())
    return uncaptured


def write_report(stale, broken_refs, uncaptured, dry_run: bool) -> Path:
    today = datetime.now().strftime("%Y-%m-%d")
    out_path = MEMORY_DIR / f"autodream-{today}.md"

    lines = [
        f"# AutoDream Consolidation — {today}",
        "",
        f"## Files Scanned",
        f"{len(list(MEMORY_DIR.glob('*.md')))} files in memory/",
        "",
    ]

    lines += ["## Stale / Flagged Files", ""]
    if stale:
        for path, reason in stale:
            lines.append(f"- `{path.name}` — {reason}")
    else:
        lines.append("- None found")
    lines.append("")

    lines += ["## Broken MEMORY.md References", ""]
    if broken_refs:
        for ref in broken_refs:
            lines.append(f"- {ref}")
    else:
        lines.append("- None found")
    lines.append("")

    lines += ["## Unchecked HEARTBEAT Tasks", ""]
    if uncaptured:
        for item in uncaptured:
            lines.append(f"- {item}")
    else:
        lines.append("- None (all tasks resolved)")
    lines.append("")

    lines += [
        "## Action Required",
        "Review flagged files above. Delete confirmed stale files. Fix broken refs.",
        "Mark resolved HEARTBEAT tasks. Update MEMORY.md if new durable facts emerged.",
    ]

    report = "\n".join(lines)

    if not dry_run:
        out_path.write_text(report, encoding="utf-8")
        # Append to HEARTBEAT log
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        if HEARTBEAT.exists():
            content = HEARTBEAT.read_text(encoding="utf-8")
            entry = (
                f"\n- `{ts}` — autodream | "
                f"{len(stale)} stale, {len(broken_refs)} broken refs, "
                f"{len(uncaptured)} open tasks | report: memory/autodream-{today}.md"
            )
            if "## Log" not in content:
                content += "\n\n## Log"
            content += entry
            HEARTBEAT.write_text(content, encoding="utf-8")
    else:
        print(report)

    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="AutoDream memory consolidation")
    parser.add_argument("--dry-run", action="store_true", help="Print report without writing")
    args = parser.parse_args()

    files = sorted(MEMORY_DIR.glob("*.md"))
    memory_file_names = {f.name for f in files}

    stale = scan_stale(files)
    broken_refs = scan_memory_index(MEMORY_INDEX, memory_file_names)
    uncaptured = check_heartbeat_uncaptured(HEARTBEAT)

    out = write_report(stale, broken_refs, uncaptured, args.dry_run)

    if not args.dry_run:
        print(f"Report written: {out}")
        print(f"  Stale files: {len(stale)}")
        print(f"  Broken refs: {len(broken_refs)}")
        print(f"  Open tasks:  {len(uncaptured)}")


if __name__ == "__main__":
    main()
