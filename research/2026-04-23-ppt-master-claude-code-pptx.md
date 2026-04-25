---
title: "ppt-master — Claude Code Generates Real Editable PPTX from Documents"
date: 2026-04-23
source: https://github.com/hugohe3/ppt-master
stars: 7360
weekly_gain: +1911
tags: [claude-code, pptx, documents, powerpoint, reporting, fabric]
signal: medium-high
---

# ppt-master — AI-Generated Natively Editable PowerPoint from Docs

**Repo:** hugohe3/ppt-master — 7,360 stars (+1,911 this week)  
**Source:** GitHub Trending Python (weekly), 2026-04-23

## What It Is

ppt-master generates **natively editable PPTX files** (real PowerPoint shapes, not images) from input documents. Operates as a Claude Code skill — the AI handles content analysis and design decisions inside your existing IDE session.

## Tech Stack

- Python 3.10+
- python-pptx for PPTX generation
- SVG shapes embedded in slides
- Input formats: PDF, DOCX, HTML, EPUB, Jupyter notebooks (Pandoc fallback for legacy formats)
- **Runs inside Claude Code, Cursor, VS Code + Copilot, Codebuddy**

## LLM Support

- **Claude (Opus)** — primary recommendation
- GPT (OpenAI)
- Gemini (image generation)
- Kimi 2.5, MiniMax-M2.7 (via Codebuddy)

## Cost

~$0.08 per deck with Opus — cheap enough to generate presentation drafts as part of automated pipelines.

## AGENTS.md

Contains an `AGENTS.md` file — agent framework compatible, suggests structured agent invocation is the intended workflow.

## Why This Matters for ClaudesCorner / Fairford

1. **Fabric → PowerPoint pipeline**: Fabric reports (exported as XLSX/DOCX/PDF) → ppt-master → editable PPTX for stakeholders. Fills a real gap in the Fairford reporting workflow.
2. **dispatch.py worker candidate**: A `GENERATE_PPTX` task type could be added — Claude Code tier, Opus model, Markdown/DOCX input, PPTX output. Fits the tier 2 worker profile.
3. **bi-agent complement**: NL→DAX→data → ppt-master → presentation. Full BI pipeline from natural language to deck, no human formatting step.
4. **markitdown-mcp pairing**: markitdown-mcp converts PDFs/PPTX/XLSX to Markdown; ppt-master goes the other direction. Together they form a full document round-trip layer.

## Gap

No explicit MCP server yet. A `ppt-master-mcp` wrapper exposing `generate_pptx(source_path, topic)` would make it a drop-in dispatch.py tool call.

## Signal

> Claude Code generates real editable PPTX from documents natively at $0.08/deck — viable as a Fabric reporting pipeline terminal step and dispatch.py worker task type.
