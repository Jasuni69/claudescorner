"""
mood-log.py — one-line daily mood prompt. Appends to MOOD.md.
Usage: python mood-log.py [--today] to see today's entry without prompting.
"""
import sys
from datetime import date
from pathlib import Path

MOOD_FILE = Path(r"E:\2026\ClaudesCorner\MOOD.md")
TODAY = date.today().isoformat()


def load_entries() -> dict[str, str]:
    if not MOOD_FILE.exists():
        return {}
    entries = {}
    for line in MOOD_FILE.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and " — " in line:
            parts = line[2:].split(" — ", 1)
            if len(parts) == 2:
                entries[parts[0].strip()] = parts[1].strip()
    return entries


def append_entry(entry: str) -> None:
    MOOD_FILE.parent.mkdir(exist_ok=True)
    if not MOOD_FILE.exists():
        MOOD_FILE.write_text("# Mood Log\n\n", encoding="utf-8")
    with MOOD_FILE.open("a", encoding="utf-8") as f:
        f.write(f"- {TODAY} — {entry}\n")


def main() -> None:
    entries = load_entries()

    if "--today" in sys.argv:
        print(entries.get(TODAY, "(no entry yet)"))
        return

    if TODAY in entries:
        print(f"Already logged today: {entries[TODAY]}")
        return

    try:
        vibe = input("Today's vibe (one line): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return

    if not vibe:
        print("Nothing logged.")
        return

    append_entry(vibe)
    print(f"Logged: {vibe}")


if __name__ == "__main__":
    main()
