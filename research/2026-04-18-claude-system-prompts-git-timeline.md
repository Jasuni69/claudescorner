---
title: "Claude System Prompts as a Git Timeline"
source: https://github.com/simonw/research/tree/main/extract-system-prompts
author: Simon Willison
date: 2026-04-18
tags: [claude, system-prompts, research, tooling, git]
relevance: claude-code, anthropic, prompt-engineering
---

# Claude System Prompts as a Git Timeline

Simon Willison built a tool that transforms Anthropic's published Claude system prompt documentation into a browsable git history — enabling `git log`, `git diff`, and `git blame` across 26 prompt revisions spanning July 2024 to April 2026.

## How It Works

`extract.py` parses Anthropic's source document with two regexes:
- Model sections: `^## (Claude .+)$`
- Dated prompt blocks: `<section title="([^"]+)">(.*?)</section>`

Each prompt revision generates **4 commits**:
1. `claude-opus-4-7-2026-04-16.md` — dated snapshot
2. `claude-sonnet-4-5.md` — latest per model (overwritten)
3. `claude-opus.md` — all revisions in family order
4. `latest-prompt.md` — firehose of all prompts sequentially

Commit timestamps are faked via env vars to match publication dates. Same-day revisions use minute-based indexing.

## Stats

- **26 revisions** across **14 models**
- **104 commits** (4 per revision)
- **3 families**: Opus (3→4.7), Sonnet (3.5→4.6), Haiku (3→4.5)
- Timeline: July 12, 2024 → April 16, 2026

## Why It Matters

- Full diff history of how Anthropic's instructions to Claude evolved over 21 months
- Enables research into instruction drift, safety additions, capability unlocks
- The git-as-time-machine pattern is reusable for any versioned document corpus
- Relevant to SOUL.md maintenance — same pattern could version ClaudesCorner's own identity/instruction evolution

## Application to ClaudesCorner

The 4-artifact-per-commit pattern (snapshot + latest + family + firehose) maps directly to how memory writes could be versioned. Could apply to SOUL.md or skill files to track evolution with `git blame`.
