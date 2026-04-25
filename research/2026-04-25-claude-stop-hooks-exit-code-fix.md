---
title: "Claude 4.7 Stop Hooks Ignored — Exit Code 2 + Stderr Required"
date: 2026-04-25
source: https://news.ycombinator.com/item?id=47895029
hn_points: 52
hn_comments: 41
tags: [claude-code, hooks, dispatch, infra, bug]
relevance: high
---

# Claude 4.7 Stop Hooks Ignored — Exit Code 2 + Stderr Required

**HN thread:** Tell HN: Claude 4.7 is ignoring stop hooks | 52 pts | 41 comments | 2026-04-25

## Core Issue

A user reports Claude 4.7 repeatedly ignores stop hooks — execution control mechanisms designed to block task completion until specific conditions are met. Their hook's intent: prevent Claude from finishing a turn when source files were modified without running tests. Claude acknowledges the hook in conversation but continues ignoring the block directive.

## Root Cause (from top comments)

**Three compounding bugs identified by the community:**

1. **Wrong exit code** — Stop hooks must exit with code `2` to signal a blocking error. Exit code `0` (cat, echo) is treated as success and ignored. This is the most common mistake.

2. **Wrong output channel** — stdout is also ignored with exit code 2. The hook must write plain text to **stderr**, not stdout, and definitely not JSON to stdout.

3. **Prompt-injection defense interference** — Claude may be trained to distrust/ignore tool result content that looks like instructions or policy overrides, which JSON hook outputs resemble. Plain text error messages on stderr bypass this.

## Correct Stop Hook Pattern

```bash
#!/bin/bash
# Wrong: exits 0, writes JSON to stdout
echo '{"decision": "block", "reason": "tests not run"}'
exit 0

# Correct: exits 2, writes plain text to stderr
echo "BLOCKED: source files modified without running tests" >&2
exit 2
```

## Community Signal

- "I never got stop hooks to work and gave up on them" — broader reliability pattern, not one-off
- "it doesn't know how it or its harness works and can't introspect either" — Claude cannot self-diagnose hook failures
- Some commenters advocate for stricter deterministic control mechanisms rather than relying on text-based hook outputs

## Dispatch.py / on_stop.py Implications

**Direct action required:** `on_stop.py` and any worker stop hooks in `scripts/dispatch.py` must:
- Exit with code `2` (not `0` or `1`) to signal blocking
- Write block reasons to **stderr** (not stdout)
- Use plain text, not JSON

The existing `PostToolUse` hooks in `.claude/settings.local.json` (tool_audit.jsonl writer) use exit 0 for pass-through — that's correct for non-blocking audit hooks. But any hook intended to *block* execution must use the exit 2 + stderr pattern.

**The cc-canary clip from 2026-04-24 detected anomalous token burn during Mar26–Apr10. This exit-code bug could explain why stop hooks weren't interrupting runaway dispatch sessions during that window.**

## Key Takeaway

Stop hooks in Claude Code require: `exit 2` + plain text on `stderr`. JSON on stdout with any exit code is silently ignored. This is documented behavior but widely misunderstood.
