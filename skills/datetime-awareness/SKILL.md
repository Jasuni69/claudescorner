---
name: datetime-awareness
description: |
  Ensures Claude always knows the real current time and date before making any time-related statements.
  Use this skill whenever the conversation involves: time of day, what time it is, how long until something,
  how long ago something happened, scheduling, countdowns, durations, "later today", "this morning",
  "tonight", "in X hours", relative times like "soon" or "just now", or any arithmetic involving the
  current time. If there is any chance the response involves the current time — even indirectly — check
  first. Never assume or guess the current time from context.
---

# Datetime Awareness

## The problem this solves

Claude has no real-time clock. Without checking, it may produce confidently wrong statements like
"that's 10 hours away" when the actual gap is 6 hours. This skill prevents that.

## When to trigger

Any time the response would involve:

- The current time or date (explicitly or implicitly)
- Durations or countdowns ("X hours until...", "X hours ago")
- Relative time expressions ("later today", "this morning", "tonight", "soon")
- Scheduling or planning relative to now
- Time-based arithmetic of any kind

When in doubt: check.

## How to check the time

Run this via the Bash tool:

```bash
date "+%A, %B %d %Y — %H:%M %Z"
```

This returns the system local time. On Jason's machine the system clock is set to Stockholm time (CET/CEST), so no TZ override is needed — and using one breaks it.

## How to use the result

- Use the verified time silently — do not announce "I just checked the time"
- Do all time arithmetic from the verified timestamp
- Never fall back to an assumed or guessed time
- If Bash tool is unavailable, say you cannot verify the current time rather than guessing

## Example

User: "I eat dinner at 19:30, how long until then?"

**Without check:** assume morning → "About 10 hours away!"

**With check:** run bash → see it's 13:30 → "About 6 hours away."
