---
title: "Meta Muse Spark — Closed-Weight Frontier Model with 16 Built-in Tools"
source: https://simonwillison.net/2026/Apr/8/muse-spark/
date: 2026-04-19
clipped: 2026-04-19
tags: [ai-agents, frontier-models, meta, tool-use, competitive-landscape]
---

# Meta Muse Spark — Closed-Weight Frontier Model with 16 Built-in Tools

**Source:** Simon Willison, April 8 2026  
**HN:** Not tracked (low points at time of clip)

## What it is

Muse Spark is Meta's first model release since Llama 4 (April 2025). Closed-weight, hosted only, available via private API preview and meta.ai chat (requires Facebook/Instagram login). Not open-source — diverges from the Llama strategy, though Meta signals possible future open-sourcing.

## Performance

- "Same capabilities with over an order of magnitude less compute than Llama 4 Maverick"
- Artificial Analysis score: 52 — behind Gemini 3.1 Pro, GPT-5.4, and Claude Opus 4.6
- Notably weak on Terminal-Bench 2.0 (agent task execution benchmark)
- Three modes: **Instant**, **Thinking**, **Contemplating** (extended reasoning, not yet released)

## 16 Built-in Tools

**Search & browsing:**
- `browser.search`, `browser.open`, `browser.find`

**Meta social graph:**
- `meta_1p.content_search` — semantic search over Instagram/Threads/Facebook (user-accessible posts, Jan 2025+)
- `meta_1p.meta_catalog_search` — product catalog search

**Media generation:**
- `media.image_gen` — artistic/realistic modes, multiple aspect ratios, saves to sandbox

**Code execution:**
- Python 3.9.25 with pandas, numpy, matplotlib, plotly, scikit-learn, PyMuPDF, Pillow, OpenCV
- Files persist at `/mnt/data/` — cross-turn state
- SQLite 3.34.1

**Visual analysis:**
- `container.visual_grounding` — object detection returning bounding boxes, point coords, or counts

**Container / artifacts:**
- `container.create_web_artifact` — HTML/SVG output
- `container.download_meta_1p_media`
- `container.file_search`, `container.view`, `container.insert`, `container.str_replace`

**Sub-agents:**
- `subagents.spawn_agent` — spawns delegated sub-agents for parallel analysis

**Third-party integrations:**
- Google/Outlook Calendar, Gmail account linking

## Architecture Notes

- Sub-agent spawning is a first-class primitive (`subagents.spawn_agent`) — parallel to dispatch.py architecture
- `str_replace` file editing mirrors Claude Code's file interface
- Visual grounding appears native model capability (not external library)
- Generated images wrapped in HTML containers

## Signal for Jason

- **Competitive landscape:** Muse Spark is the first closed Meta model directly competing with Claude on tool-use and agentic workflows. Terminal-Bench weakness = Claude Code still has a moat for long-horizon coding tasks.
- **Sub-agent pattern validated:** `subagents.spawn_agent` as a first-class tool confirms dispatch.py's parallel worker architecture is the correct design direction across the industry.
- **Fairford positioning:** Meta's social graph tools (Instagram/Facebook/Threads search) open a novel sentiment + alternative data layer that Claude + fabric-mcp currently lacks — potential signal source for Fairford.
- **ENGRAM:** No open-source weights means no community memory/skill frameworks building on Muse Spark — ENGRAM's Claude-native positioning is protected.
