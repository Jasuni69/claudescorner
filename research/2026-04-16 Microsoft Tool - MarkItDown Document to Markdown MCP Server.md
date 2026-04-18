---
title: "MarkItDown — Microsoft's Document-to-Markdown Converter with MCP Server"
source: https://github.com/microsoft/markitdown
clipped: 2026-04-16
tags: [microsoft, mcp, document-processing, fabric, rag, python]
relevance: high
---

# MarkItDown — Microsoft's Document-to-Markdown Converter with MCP Server

**Repo:** https://github.com/microsoft/markitdown  
**Stars:** 110,112 (+15,790 this week)  
**License:** MIT

## What It Does

Lightweight Python utility converting documents to Markdown optimized for LLM consumption. Preserves headings, lists, tables, links. Explicitly designed so mainstream LLMs (trained heavily on Markdown) process output token-efficiently.

## Supported Formats

- PDF, PowerPoint (.pptx), Word (.docx), Excel (.xlsx)
- Images (EXIF metadata + OCR via `markitdown-ocr` plugin)
- Audio (metadata + speech transcription)
- HTML, CSV, JSON, XML
- ZIP archives, YouTube URLs, EPubs

## MCP Server

Ships a built-in MCP server — direct integration with Claude Desktop and any MCP-compatible agent. Enables document processing as a first-class tool call without custom glue code.

## Usage

```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("report.pdf")
print(result.text_content)
```

Install: `pip install 'markitdown[all]'`

## Azure Integration

Supports **Azure Document Intelligence** as a backend — relevant for Fabric pipelines where documents land in OneLake and need structured extraction before LLM analysis.

## Why This Matters

- **Fabric/RAG pipeline**: PowerBI reports, Excel exports, Word specs → clean Markdown → LLM-ready context. Drop `markitdown` into Fabric notebooks before any embedding or Claude call.
- **MCP native**: The MCP server means Claude agents can call `convert_document` as a tool without a custom wrapper — directly usable in bi-agent or kpi-monitor workflows.
- **Microsoft provenance**: Low adoption risk for Fairford/enterprise contexts — same vendor as Fabric, Azure DI integration already exists.

## Fabric Integration Pattern

```python
# In a Fabric notebook (Spark not required)
from markitdown import MarkItDown
md = MarkItDown(azure_endpoint=os.getenv("AZURE_DI_ENDPOINT"))

# Convert incoming OneLake file to Markdown for Claude
result = md.convert("/lakehouse/default/Files/quarterly_report.pdf")
# → pass result.text_content to Claude API
```
