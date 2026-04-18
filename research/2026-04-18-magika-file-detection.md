---
title: "Magika — AI-Powered File Type Detection at Agent Scale"
source: https://github.com/google/magika
author: Google
date: 2026-04-18
clipped: 2026-04-18
tags: [file-detection, ai-tools, agents, mcp-opportunity, security, google]
relevance: medium-high
stars: 15614
stars_today: +956
---

## Summary

Google's Magika uses a custom deep-learning model (~few MB) to identify 200+ file content types with ~99% precision/recall at ~5ms per file. Trained on 100M files. Deployed internally at Google for security routing. Available as Python lib, CLI (Rust), JS/npm, Go/Rust bindings.

## Key Technical Facts

- **Model size**: A few MB — agent-embeddable, no heavy runtime
- **Speed**: ~5ms/file on single CPU; inference time constant regardless of file size (reads limited header bytes)
- **Accuracy**: ~99% average precision and recall on test set
- **Formats**: 200+ types — binary + text; handles truncated/ambiguous files
- **Confidence modes**: high-confidence / medium-confidence / best-guess
- **Batch mode**: recursive directory scan, JSON/JSONL output

## No MCP Integration Yet

README has zero mention of MCP. This is a gap — Magika as an MCP tool would let agents:
- Classify uploaded/received files before routing
- Validate Fabric pipeline ingestion (detect misnamed CSVs, malformed Parquet, etc.)
- Gate markitdown-mcp conversion (only feed supported formats)

## Relevance to ClaudesCorner

| Use case | Where |
|---|---|
| Fabric ingestion guard | kpi-monitor / fabric-mcp: validate file types before lakestore write |
| markitdown-mcp pre-filter | wrap magika check before convert_file to avoid failed conversions |
| dispatch.py attachment routing | classify any file artifact before dispatching to correct worker |
| `magika-mcp` tool | 3-tool server: `detect_file`, `detect_bytes`, `batch_detect` — wraps Python lib |

## Action

Low-effort MCP wrapper opportunity: `projects/magika-mcp/server.py` — 3 tools using `magika` Python lib. Pairs cleanly with markitdown-mcp as a pre-filter stage.
