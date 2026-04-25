---
title: "last30days-skill: Multi-Source Research Agent Skill"
date: 2026-04-22
source: https://github.com/mvanhorn/last30days-skill
stars: 23465
stars_today: +254
license: MIT
tags: [agent-skill, claude-code, research, reddit, hackernews, polymarket, mcp, skill-manager]
relevance: [skill-manager-mcp, dispatch.py, reddit_brief, ENGRAM]
---

# last30days-skill: Multi-Source Research Agent Skill

## Summary

A 23.4k-star MIT-licensed Claude Code skill (GitHub Trending #11, +254 today) that researches any topic across 10+ platforms and synthesizes a grounded summary scored by real engagement metrics. Installable as a single marketplace command.

## What It Does

Accepts a topic query, fans out to multiple sources in parallel, deduplicates cross-platform results, and returns a synthesized brief with citations ranked by upvotes/likes/prediction odds — not editorial selection.

## Platforms Searched

| Platform | Signal type |
|----------|-------------|
| Reddit | Posts + top comments + upvote counts |
| X/Twitter | Posts and discussions |
| YouTube | Full video transcripts |
| Hacker News | Developer consensus |
| Polymarket | Prediction market odds |
| GitHub | Repos, PRs, releases |
| Perplexity Sonar | Grounded web search |
| Brave Search | General web |
| TikTok, Bluesky, Threads, Instagram Reels | Optional |

## Installation

```bash
# Claude Code
/plugin marketplace add mvanhorn/last30days-skill

# OpenClaw
clawhub install last30days-official

# Gemini CLI
gemini extensions install ./last30days-skill
```

Also installable via claude.ai web (Settings → Capabilities → Skills).

## Output Format

- Synthesized brief with cited sources
- Organized by relevance + engagement signal
- "Best Takes" section for viral/witty commentary
- `eli5` mode for plain-language summaries
- v3: entity resolution before search, cross-source dedup, per-author caps (max 3 items/author)

## Relevance to ClaudesCorner

**dispatch.py research workers**: This skill is a production-grade analog of what dispatch.py's Tier 1 (Haiku) research workers do manually. The fan-out-to-10-platforms + cross-dedup + engagement-scoring pattern is exactly the architecture reddit_brief.py should evolve toward. Key gap: reddit_brief.py currently only hits Reddit; last30days-skill hits 10 sources simultaneously.

**reddit_brief.py upgrade path**: Add HN hot.json + GitHub trending + Polymarket odds as parallel fetch targets. The engagement-score ranking (upvotes/odds/stars) is a direct improvement over reddit_brief.py's current score-based sort.

**skill-manager-mcp**: This is the most-starred single-domain research skill in the agentskills.io ecosystem right now. The multi-platform fan-out pattern + per-author dedup caps are worth adopting as a skill pattern — particularly the `deny:` frontmatter bounding scope to research-only (no code edits, no external writes).

**ENGRAM**: The cross-platform synthesis output maps directly onto what ENGRAM's memory layer should receive as input — grounded, engagement-ranked, deduplicated briefs rather than raw RSS feeds. Consider wiring last30days-skill output as a HEARTBEAT input source.

## v3 Feature Highlights

- **Intelligent entity resolution**: resolves ambiguous queries before searching (e.g. "Claude" → "Anthropic Claude AI" not "Claude Monet")
- **Single-pass comparison queries**: "X vs Y" triggers parallel research on both branches
- **GitHub person-mode**: researches individual developer profiles across repos/PRs/releases
