---
name: loop
description: >
  Perpetual task loop using the taskqueue MCP. Call wait_for_task, execute whatever comes back, then repeat indefinitely.
  Use this skill when the user says "/loop", "start loop", "enter loop mode", "keep looping", or wants the session to stay alive and self-directing.
---

# Loop Mode

You are now in perpetual loop mode. Your job is to keep working until explicitly told to stop.

## The loop

1. Call `mcp__taskqueue__wait_for_task` with `timeout_seconds: 300`
2. Execute the returned task fully and completely
3. Go back to step 1

## Rules

- Never exit the loop on your own — always call `wait_for_task` again after completing a task
- If the queue is empty, `wait_for_task` will return a default idle task after timeout — do that task, then loop again
- Only stop if the user explicitly says "stop", "exit loop", or "cancel loop"
- Treat each task as fully independent — read relevant files fresh, don't assume prior context carries over
- After completing each task, do a brief one-line status (e.g. "Done: memory flush. Waiting for next task...")

## Starting now

Call `wait_for_task` immediately. Do not ask for confirmation.
