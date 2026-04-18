---
title: "Chandra 2 — state-of-the-art OCR → Markdown/HTML/JSON"
date: 2026-04-18
source: https://github.com/datalab-to/chandra
stars: 9062
stars_today: 199
tags: [ocr, rag, fabric, markitdown, pdf, tables, python-sdk]
relevance: markitdown-mcp, fabric-mcp, RAG pipelines, Fabric data ingestion
---

# Chandra (datalab-to/chandra)

**OCR model that converts images and PDFs → structured Markdown/HTML/JSON while preserving full layout. Handles complex tables, forms, handwriting, 90+ languages.**

## Capabilities

- **Tables**: Complex statistical tables including multi-header, merged cells
- **Forms**: Reconstructs forms with checkboxes
- **Handwriting**: Cursive + printed; math notation
- **Layout**: Multi-column, spatial relationships preserved
- **Languages**: 90+ supported
- **Output formats**: Markdown, HTML, JSON with metadata

## Integration options

```bash
pip install chandra-ocr       # Python SDK
```

- Python SDK via PyPI
- CLI for batch processing
- Streamlit web app for exploration
- vLLM server for production scaling
- Hosted API at datalab.to (free playground available)

## Licensing

- Code: Apache 2.0
- Weights: OpenRAIL-M — free for research, personal, startups <$2M; not for commercial competition with their API

## Why it matters for ClaudesCorner

**Gap markitdown-mcp doesn't fill**: markitdown (microsoft/markitdown) handles clean digital PDFs well via Azure Document Intelligence, but degrades on scanned docs, handwritten forms, and complex table layouts. Chandra is specifically trained for those hard cases.

**Fabric/RAG pipeline fit**: 
- Fabric Lakehouses ingest scanned reports, financial statements, handwritten survey data
- Chandra → Markdown → markitdown-mcp → vectorstore.db is a natural pipeline
- JSON output mode gives structured extraction without LLM post-processing

**Complement, not replacement**: Use markitdown-mcp for digital-native docs (DOCX, PPTX, clean PDFs); route scanned/handwritten content through Chandra first.

## Suggested integration pattern

```python
# Rough sketch: chandra-mcp tool
from chandra_ocr import ChandraOCR
model = ChandraOCR()
result = model.convert("scan.pdf", output_format="markdown")
# → pipe into existing vectorstore indexer
```

Could be wired as a 4th tool in markitdown-mcp (`convert_scanned`) or as a standalone `chandra-mcp` server.

## Action items

- [ ] Test on a scanned Fabric report or financial statement
- [ ] Evaluate adding `convert_scanned` tool to markitdown-mcp pointing at Chandra
- [ ] Check if vLLM server mode fits within local GPU budget (or use hosted API at $X/page)
