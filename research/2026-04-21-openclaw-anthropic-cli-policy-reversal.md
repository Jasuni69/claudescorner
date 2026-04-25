---
title: "Anthropic Re-Sanctions OpenClaw CLI Reuse (claude -p)"
date: 2026-04-21
source: https://docs.openclaw.ai/providers/anthropic
hn_url: https://news.ycombinator.com/newest
points: 2
tags: [anthropic, openclaw, claude-cli, dispatch, auth]
---

# Anthropic Re-Sanctions OpenClaw CLI Reuse

Anthropic staff explicitly told the OpenClaw team that OpenClaw-style Claude CLI reuse (`claude -p`) is **allowed again**. OpenClaw now treats this as sanctioned usage.

## What Changed

Previously restricted. Now: Anthropic staff communicated directly that this approach is permissible. OpenClaw docs updated to reflect the reversal. Policy holds "unless Anthropic publishes a new policy change."

## Key Rules

- **Sanctioned**: CLI reuse and `claude -p` usage on hosts where Claude CLI is already configured.
- **Preferred for production**: API keys remain "the clearest and most predictable production path" for long-lived gateway hosts (explicit server-side billing control).
- **Legacy token limitation**: `sk-ant-oat-*` tokens get context-1m beta requests rejected. OpenClaw warns + falls back to standard windows.
- **Public alignment**: Anthropic's Claude Code docs document `claude -p` directly — reinforces sanction.

## Signal for ClaudesCorner

dispatch.py workers currently assume API key auth. The re-sanctioned `claude -p` CLI path means:
- Workers could authenticate via CLI session on machines where Claude Code is already logged in — zero credential management overhead.
- Relevant for local dispatch runs where `ANTHROPIC_API_KEY` isn't set but Claude CLI is.
- API keys still preferred if dispatch is running headless/unattended or as a scheduled task.

**Action candidate**: Add CLI-auth fallback note to dispatch.py worker docs; evaluate `claude -p` as fallback for Tier 1 (Haiku) workers where API cost is the concern.
