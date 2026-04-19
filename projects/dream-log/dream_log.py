"""dream_log.py -- weekly dream entry generator using Claude API.

Usage:
    python dream_log.py [--dry-run] [--model MODEL]

Generates a ~150-word surreal/fictional dream narrative in first person,
appends to E:/2026/ClaudesCorner/journal/dreams.md with a date header.
Uses ANTHROPIC_API_KEY env var; falls back to a local static entry if unset.
"""

import os
import argparse
import random
from datetime import date
from pathlib import Path

DREAMS_FILE = Path(r"E:\2026\ClaudesCorner\journal\dreams.md")

SYSTEM_PROMPT = (
    "You are a dream journal writer. You generate vivid, surreal, "
    "first-person dream entries in the style of a personal journal. Each entry should:\n"
    "- Be 130-160 words\n"
    "- Feel like a real dream: internally consistent but with strange logic\n"
    "- Have a sense of place, movement, and mild unease or wonder\n"
    "- End mid-thought or with an abrupt shift, as dreams do\n"
    "- Use present tense or shifting tense, never past perfect\n"
    "- Avoid clichés like 'flying' or 'being chased' unless twisted into something strange\n"
    "- No preamble, no title, no explanation -- just the dream text"
)

USER_PROMPT = "Write a dream entry for today. Make it strange and specific."

# Fallback dreams used when no API key is available
FALLBACK_DREAMS = [
    (
        "The library has no ceiling. Shelves continue upward until the titles become "
        "unreadable, which is when I realise I have been reading the same page for an hour. "
        "A woman with red shoes crosses the reading room. I know her but cannot locate the memory "
        "of where from. She sets a cup of coffee on my table without looking at me. The coffee is "
        "already cold. I try to ask her name but my voice produces only the sound of paper "
        "turning. Outside the windows -- which appeared after I looked away from them -- a street "
        "I almost recognise is flooding calmly. The bookshelves begin to hum. Someone tells me "
        "the humming is a catalogue system. I believe this completely."
    ),
    (
        "I am building something out of grey stones. The stones fit together only if I do not "
        "look directly at the joints. My hands are larger than they should be. There is a dog "
        "watching me from across a field that may not exist when I am not facing it. At some point "
        "I become aware the structure is my grandmother's house, although it looks nothing like it. "
        "A door appears on the eastern wall. I put my hand on the handle and the handle is warm "
        "and I understand this warmth means something important that I cannot quite retrieve. "
        "The dog has moved closer. Its shadow points the wrong direction for the sun, which is "
        "also wrong."
    ),
    (
        "The train station is both familiar and clearly invented. Departure boards list cities "
        "whose names shift when I read them a second time. I have a ticket but the platform "
        "number is a symbol I do not recognise. A child beside me says the symbol means 'soon.' "
        "I thank her. She is no longer there. The train arrives and it is longer than the platform "
        "by a significant amount that no one acknowledges. I board anyway. My seat faces backward "
        "and the window shows the landscape we have not yet crossed. I find this logical. "
        "Someone sits across from me and opens a newspaper dated three years from now and I "
        "try to read it but the language is English except"
    ),
]


def generate_dream_api(model: str, api_key: str) -> str:
    try:
        import anthropic
    except ImportError:
        raise SystemExit("anthropic package not installed: pip install anthropic")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": USER_PROMPT}],
    )
    return message.content[0].text.strip()


def generate_dream(model: str) -> tuple[str, str]:
    """Returns (dream_text, source) where source is 'api' or 'fallback'."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        return generate_dream_api(model, api_key), "api"
    # Seed by date so same fallback repeats within a day (idempotent)
    rng = random.Random(date.today().toordinal())
    return rng.choice(FALLBACK_DREAMS), "fallback"


def format_entry(dream_text: str) -> str:
    today = date.today().isoformat()
    return f"\n## {today}\n\n{dream_text}\n"


def append_to_dreams(entry: str) -> None:
    DREAMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not DREAMS_FILE.exists():
        DREAMS_FILE.write_text("# Dream Journal\n")
    with DREAMS_FILE.open("a", encoding="utf-8") as f:
        f.write(entry)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a weekly dream journal entry")
    parser.add_argument("--dry-run", action="store_true", help="Print entry without writing")
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5-20251001",
        help="Claude model to use (default: claude-haiku-4-5-20251001)",
    )
    args = parser.parse_args()

    dream_text, source = generate_dream(args.model)
    if source == "fallback":
        print("[dream-log] No ANTHROPIC_API_KEY -- using fallback dream")
    else:
        print(f"[dream-log] Generated via API (model={args.model})")

    entry = format_entry(dream_text)

    if args.dry_run:
        print("\n--- DRY RUN (not written) ---")
        print(entry)
    else:
        append_to_dreams(entry)
        print(f"[dream-log] Appended to {DREAMS_FILE}")
        print(entry)


if __name__ == "__main__":
    main()
