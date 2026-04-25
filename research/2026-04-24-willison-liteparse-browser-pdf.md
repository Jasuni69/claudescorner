---
title: "Willison — LiteParse for the Web: Browser-Native PDF Extraction"
date: 2026-04-24
source: https://simonwillison.net/2026/Apr/23/liteparse-for-the-web/
tags: [willison, pdf, rag, markitdown, vibe-coding, fabric, claude-code]
signal: medium
---

# Willison — LiteParse for the Web: Browser-Native PDF Extraction

**Source:** Simon Willison, Apr 23 2026
**HN:** not indexed at time of clip

## Summary

Willison ported LlamaIndex's LiteParse Node.js CLI to a browser-native PDF text extractor. Built entirely via Claude Code vibe-coding (59 minutes, zero manual code review). Nothing leaves the machine — fully client-side.

## Key facts

- **Stack:** PDF.js + Tesseract.js (optional OCR for image-based PDFs)
- **Output:** Plain text + structured JSON with bounding boxes, dimensions, font info, reading-order heuristics for multi-column layouts
- **Privacy:** 100% client-side, no server, no data transmission
- **OCR:** Tesseract.js for scanned/image PDFs — fills the gap markitdown-mcp has for non-text PDFs
- **Build method:** Pure vibe-coding, Claude Code, 59 min total, no manual review

## Relevance to ClaudesCorner

**markitdown-mcp complement:** Current markitdown-mcp pipeline handles text-native PDFs well; LiteParse adds multi-column reading-order correction + scanned OCR support. The bounding-box JSON output is directly useful for RAG source attribution (knowing which page/column a chunk came from).

**Fabric RAG pipeline:** Privacy-safe local extraction before pushing to Fabric lakehouse. If documents contain PII, client-side extraction means raw content never hits a server — important for regulated Fairford verticals (finance, legal).

**Vibe-coding signal:** 59 min from zero to working browser tool is Willison benchmarking Claude Code on a real extraction task. He used zero manual review — strong signal for dispatch.py worker quality at leaf-node PDF tasks.

**Chandra 2 relationship:** Chandra 2 (clipped 2026-04-18) covers handwriting + complex tables + 90 languages. LiteParse covers multi-column layout + reading order. Together they cover the full scanned-doc space that markitdown-mcp currently misses.

## Action items

- Add `convert_scanned` tool candidate to markitdown-mcp backlog (wrapping Tesseract.js or Chandra 2)
- Evaluate LiteParse JSON bounding-box format as source-attribution metadata schema for Fabric RAG chunks
