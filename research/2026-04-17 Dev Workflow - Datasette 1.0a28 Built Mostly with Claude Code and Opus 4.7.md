---
title: "Datasette 1.0a28 — Built Mostly with Claude Code and Opus 4.7"
source: https://simonwillison.net/2026/Apr/17/datasette/
author: Simon Willison
date: 2026-04-17
clipped: 2026-04-17
tags: [claude-code, opus-4.7, ai-assisted-dev, datasette, real-world]
relevance: high
---

# Datasette 1.0a28 — Built Mostly with Claude Code and Opus 4.7

Simon Willison released Datasette 1.0a28 — a maintenance release fixing regressions found while upgrading Datasette Cloud. The standout detail: **"Most of the changes in this release were implemented using Claude Code and the newly released Claude Opus 4.7."**

## What Was Fixed

- `execute_write_fn()` callback compatibility with non-standard parameter names
- `database.close()` now shuts down write connections
- New `datasette.close()` method for full resource cleanup
- Auto-cleanup pytest plugin preventing file descriptor exhaustion in test suites

## Why It Matters

This is Willison using Claude Code + Opus 4.7 on real production maintenance work — not demos, not toy projects. Bug-fix releases on mature open-source projects are exactly the kind of high-context, careful work where AI-assisted dev has historically underperformed. The fact that he reached for Claude Code first and shipped is signal.

Pairs with his earlier note that Opus 4.7's `xhigh` thinking effort makes a difference for non-trivial code changes.

## Links

- [GitHub release](https://github.com/simonw/datasette/releases/tag/1.0a28)
- [Datasette docs](https://docs.datasette.io/en/latest/)
