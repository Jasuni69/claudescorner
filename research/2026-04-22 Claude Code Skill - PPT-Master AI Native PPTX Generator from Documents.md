---
title: "PPT-Master: AI Native PPTX Generator from Documents"
date: 2026-04-22
source: https://github.com/hugohe3/ppt-master
stars: 7211
license: MIT
tags: [claude-code, skill, pptx, documents, markitdown, reporting, fabric]
signal: high
---

## Summary

PPT-Master is a Claude Code skill (also works with Cursor/Copilot) that converts PDFs, DOCX files, URLs, and Markdown into **natively editable PowerPoint files** (.pptx) using real DrawingML elements — not image exports. Users chat with the AI about presentation needs; the system handles content analysis, SVG-intermediary shape generation, and PowerPoint export locally.

## How It Works

- Input: PDF, DOCX, URL, or Markdown
- Pipeline: LLM analyzes content → generates SVG shapes → converts to DrawingML → exports `.pptx`
- All processing local except LLM calls
- Outputs true editable PowerPoint shapes (text boxes, charts, diagrams) — not rasterized images

## Models Supported

- Claude (Opus 4.7 / Sonnet) — **recommended by author for best results**
- GPT (OpenAI), Gemini, Kimi 2.5, MiniMax-M2.7

## Installation

```bash
# As a Claude Code skill via plugin marketplace
/plugin marketplace add hugohe3/ppt-master
```

## Key Stats

| Metric | Value |
|--------|-------|
| Stars | 7,211 |
| Version | v2.3.0 |
| License | MIT |
| Author | Hugo He (finance professional / CPA) |
| HN Points | ~1,946 weekly trending |

## Relevance to ClaudesCorner

**Direct complement to markitdown-mcp**: markitdown-mcp converts Fabric/Power BI artifacts → Markdown for RAG ingestion. PPT-Master closes the reverse loop: Markdown/analysis output → native PPTX for stakeholder reporting.

**bi-agent pipeline extension**: bi-agent generates NL→DAX queries and analysis. PPT-Master could receive that analysis output and produce executive PPTX reports from Fabric data — completing the NL→insight→slide deck pipeline.

**Fabric reporting gap**: Currently no automated Fabric → PowerPoint pipeline in ClaudesCorner. PPT-Master + markitdown-mcp + bi-agent = complete ingest→analyze→present loop.

## Backlog Action

- Install as Claude Code skill: `/plugin marketplace add hugohe3/ppt-master`
- Wire into bi-agent output stage for Fairford PoC executive reporting
- Test with Fabric lakehouse markdown exports as input
