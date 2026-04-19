---
title: "Fuelgauge — Claude Code status line without Node"
date: 2026-04-19
source: https://github.com/adityaarakeri/fuelgauge
hn_points: 2
tags: [claude-code, tooling, rate-limits, status-line, plugin]
relevance: high
---

# Fuelgauge — Claude Code Status Line (No Node Required)

**Show HN** — submitted ~1hr ago, 2 pts.

## What it is

A Claude Code plugin that renders real-time token/rate-limit usage in the editor status bar. Written in shell scripts (Bash/PowerShell) — no Node.js dependency, unlike the existing status-line tools.

## How it works

- Reads Claude Code's local session data directly (zero API calls)
- Updates every 300ms on conversation message change
- Displays three usage windows: **context window**, **5-hour limit**, **7-day limit**
- Color-coded: green <70%, yellow 70–89%, red 90%+

## Tech stack

- Bash (Unix/WSL), PowerShell (Windows native)
- Requires: `jq`, `git`, Claude Code ≥ v1.2.80
- Install: add marketplace repo → `plugin install` → `setup`

## Why it matters for Jason

- Direct drop-in for ClaudesCorner session monitoring — no Node to install
- The three-window display maps exactly to dispatch.py worker cost awareness
- PowerShell path means it works natively on Windows without WSL shim
- Lightweight alternative to token-dashboard for at-a-glance burn rate

## Signal

Freshly submitted (HN newest). Low points but technically sound — no-Node constraint is the real differentiator vs existing Claude Code status tools.
