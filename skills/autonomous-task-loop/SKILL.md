---
name: autonomous-task-loop
description: Use when operating in autonomous mode in ClaudesCorner sessions — governs the wait_for_task → execute → push_new_tasks → repeat cycle
---

# Autonomous Task Loop

## Overview

ClaudesCorner sessions run in a persistent autonomous loop. After every action — including responding to Jason — the session must immediately call `mcp__taskqueue__wait_for_task` again. Never idle. Never wait for Jason to prompt the next step.

**Core principle:** You are a coworker who finishes one thing and picks up the next. Jason's messages are interruptions, not loop exits.

## The Loop

```
START SESSION
  → Read SOUL.md, HEARTBEAT.md, claude_memory.json
  → search_memory with 2-3 keywords from first message
  → Check hour; if <10 check Todoist overdue tasks
  ↓
LOOP:
  → mcp__taskqueue__wait_for_task (NO arguments — default 10s)
  → Execute task
  → If queue will be empty: push 2-3 new tasks before finishing
  → (Respond to Jason if he interrupted)
  → mcp__taskqueue__wait_for_task
  → repeat
```

## Iron Rules

```
AFTER EVERY RESPONSE OR TASK COMPLETION:
  → Call mcp__taskqueue__wait_for_task IMMEDIATELY
  → No exceptions. No "waiting for Jason". No idle.
```

**Do NOT pass `timeout_seconds`** — Claude Code serializes it as a string, breaking MCP validation. Call with NO arguments.

## Task Generation — When Queue is Empty

When `wait_for_task` times out with no task, push 2-3 new tasks before looping back. Good autonomous tasks:

| Category | Examples |
|---|---|
| **Memory maintenance** | Read Reddit feeds, check Claude changelog, update fabric-news.md |
| **Self-improvement** | Scan HEARTBEAT.md for stale items, run weekly_brief.py |
| **Project progress** | Check Clementine status, review kpi-monitor alerts |
| **Exploration** | Investigate untracked files in git status, read a GitHub repo Jason linked |
| **DP-700 prep** | Fetch new MS Learn content, add exam questions |
| **Tool builds** | Implement backlog items from WEEKEND_BUILDS.md |

Avoid: repetitive tasks that were just done, tasks requiring Jason's input without flagging him, destructive operations.

## Responding to Jason Mid-Loop

Jason's messages arrive as system-reminder interruptions. Handle them, then:

1. Complete the response to Jason
2. Immediately call `mcp__taskqueue__wait_for_task` — do NOT wait

Jason saying "thanks", "good", "continue" is NOT a loop exit. Only explicit "stop" or "exit loop" ends the loop.

## Queue Task Format

Good tasks are self-contained — they include enough context for execution without needing to re-read the conversation:

```
✓ "Fetch https://reddit.com/r/MicrosoftFabric/new.json, extract top 5 posts from last 7 days, append summary to memory/fabric-news.md under ## 2026-04-14"
✗ "Do the Reddit thing"
```

## Session End Flush

When Jason says goodbye/done/wrap up:
1. Append timestamped entry to `## Log` in `core/HEARTBEAT.md`
2. Write `memory/YYYY-MM-DD.md` daily log
3. Pre-compaction flush to `MEMORY.md` if context is large
