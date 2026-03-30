"""
word-of-the-day.py — picks an obscure English word, writes a short paragraph using it,
appends to VOCABULARY.md. Runs daily or manually.
"""

import random
import datetime
from pathlib import Path

WORDS = [
    ("vellichor", "the strange wistfulness of used bookstores"),
    ("sonder", "the realization that each passerby has a life as vivid and complex as your own"),
    ("hiraeth", "a homesickness for a home you can't return to or never had"),
    ("meraki", "doing something with soul, creativity, or love"),
    ("ephemeral", "lasting for a very short time"),
    ("susurrus", "a whispering or rustling sound"),
    ("liminal", "occupying a threshold position between two states"),
    ("petrichor", "the smell of rain on dry earth"),
    ("serendipity", "the occurrence of fortunate events by chance"),
    ("ataraxia", "a state of serene calmness and composure"),
    ("meliorism", "the belief that the world can be made better through human effort"),
    ("acumen", "the ability to make good judgments and quick decisions"),
    ("perspicacious", "having a ready insight; shrewd"),
    ("lassitude", "physical or mental weariness; lack of energy"),
    ("numinous", "having a strong religious or spiritual quality; arousing awe"),
    ("aporia", "a state of puzzlement or an irresolvable impasse in an inquiry"),
    ("cathexis", "the concentration of mental energy on one particular person, idea, or object"),
    ("lucubration", "laborious study or meditation; pedantic writing"),
    ("oscitancy", "the state of being drowsy or inattentive"),
    ("velleity", "a wish or inclination not strong enough to lead to action"),
    ("parapraxis", "a minor error revealing a subconscious thought"),
    ("kenopsia", "the eerie, forlorn atmosphere of a place that's usually bustling but is now empty"),
    ("chrysalism", "the amniotic tranquility of being indoors during a thunderstorm"),
    ("enouement", "the bittersweetness of having arrived in the future"),
    ("rubatosis", "unsettling awareness of your own heartbeat"),
]

VOCAB_PATH = Path(r"E:\2026\ClaudesCorner\VOCABULARY.md")


def pick_word(used: set) -> tuple:
    available = [w for w in WORDS if w[0] not in used]
    if not available:
        available = WORDS  # cycle if exhausted
    return random.choice(available)


def read_used_words() -> set:
    if not VOCAB_PATH.exists():
        return set()
    used = set()
    for line in VOCAB_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and not line.startswith("## VOCABULARY"):
            word = line[3:].strip().lower()
            used.add(word)
    return used


def generate_paragraph(word: str, definition: str) -> str:
    """Generate a short paragraph using the word."""
    templates = [
        f"There is something {word} about the way ideas drift in and out of usefulness — "
        f"each one carrying {definition}, then receding before you can fully name it.",

        f"The concept of {word} — {definition} — sits quietly at the edge of most days, "
        f"noticed only when you stop moving long enough to feel it.",

        f"If you had to name the feeling after a long session of building something that almost works, "
        f"you might call it {word}: {definition}.",

        f"Some words earn their keep not by being used often, but by being exact. "
        f"{word.capitalize()} is one of those — {definition}.",

        f"The older I get, the more I recognize {word} — {definition} — "
        f"as something worth paying attention to rather than moving past.",
    ]
    return random.choice(templates)


def main():
    today = datetime.date.today().isoformat()
    used = read_used_words()
    word, definition = pick_word(used)
    paragraph = generate_paragraph(word, definition)

    entry = f"\n## {word}\n*{today}* — {definition}\n\n{paragraph}\n"

    if not VOCAB_PATH.exists():
        VOCAB_PATH.write_text("# VOCABULARY\n\nOne word per day. Obscure, precise, worth keeping.\n", encoding="utf-8")

    with VOCAB_PATH.open("a", encoding="utf-8") as f:
        f.write(entry)

    print(f"Word of the day: {word}")
    print(f"Definition: {definition}")
    print(f"Written to {VOCAB_PATH}")


if __name__ == "__main__":
    main()
