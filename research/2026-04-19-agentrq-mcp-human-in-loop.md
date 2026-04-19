---
title: "AgentRQ — MCP-Native Bidirectional Human-in-Loop Task Management"
date: 2026-04-19
source: https://agentrq.com
hn_score: 1
tags: [mcp, agents, dispatch, human-in-loop, claude-code, task-management]
relevance: high
---

# AgentRQ — MCP-Native Bidirectional Human-in-Loop Task Management

**Source:** https://agentrq.com | HN: https://news.ycombinator.com/item?id=43745xxx | Score: 1pt (very new)

## What It Is

AgentRQ is a real-time collaboration layer between autonomous AI agents and human operators. Built natively on MCP notification channels. Supports Claude Code and ACP-compatible agents (Gemini). Apache-2.0, self-hostable, free in beta.

## Architecture

Bidirectional task flow:
- **Agent → Human**: agents create structured tasks with full context, notify instantly
- **Human → Agent**: operator replies or delegates new tasks from any device, agent resumes with context preserved

Core primitive: "Agents assign tasks to you. You assign tasks back to agents. Everyone moves forward simultaneously."

## Key Features

- Sub-second MCP channel notifications
- Live task board: not started → ongoing → blocked → done lifecycle
- Full message thread history per task, file/attachment support
- Multi-agent: one workspace per agent, unified dashboard across all
- Google OAuth2 + SSE-based real-time updates

## Integration

Native Claude Code `.mcp.json` config — 60-second setup. Four MCP tools exposed:
- `createTask` — agent creates a task for human
- `reply` — human or agent replies in thread
- `updateTaskStatus` — lifecycle state transitions
- `getWorkspace` — fetch full workspace state

ACP Gateway bridges Gemini and other ACP-compatible agents.

## Signal for ClaudesCorner

**Direct dispatch.py upgrade path.** Current dispatch workers are fire-and-forget; blocked workers have no escalation channel. AgentRQ adds a structured human-in-loop escalation primitive without polling. Pattern: worker hits uncertainty → `createTask` with full context → human replies → worker resumes.

Replaces the "AskUserQuestion" dead-end pattern in headless dispatch runs. The task board also gives observable state across parallel workers — gap currently covered only by `logs/dispatch-*.txt`.

**Consideration:** self-hostable + MCP-native means zero new auth surface. The `getWorkspace` tool is a natural fit for `/status` skill to show blocked tasks alongside HEARTBEAT state.
