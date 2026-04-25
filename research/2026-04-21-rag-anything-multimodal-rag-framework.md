---
title: "RAG-Anything: All-in-One Multimodal RAG Framework"
date: 2026-04-21
source: https://github.com/HKUDS/RAG-Anything
stars: 16400
trending: +245 today
tags: [rag, multimodal, knowledge-graph, fabric, mcp, research]
relevance: [fabric-mcp, markitdown-mcp, memory-mcp, bi-agent]
---

# RAG-Anything — All-in-One Multimodal RAG Framework

**Repo:** HKUDS/RAG-Anything | 16.4k stars | Apache-2.0 | +245 stars today  
**From:** Same org as DeepTutor (HKUDS)

## What It Does

End-to-end multimodal RAG pipeline that processes PDFs, Office docs (DOCX/PPTX/XLSX), images, tables, equations, and charts through a unified interface. Built on top of LightRAG, it adds a knowledge graph layer with cross-modal relationship discovery.

## 5-Stage Pipeline

1. **Document Parsing** — MinerU-based extraction with adaptive decomposition per format
2. **Multi-Modal Content Understanding** — Concurrent dedicated pipelines per content type
3. **Multimodal Analysis Engine** — Vision models for images, statistical pattern recognition for tables, LaTeX for equations
4. **Knowledge Graph Index** — Multi-modal entity extraction + cross-modal relationship mapping + weighted relevance scoring
5. **Modality-Aware Retrieval** — Vector-graph fusion with adaptive ranking

## Key Differentiators vs Conventional RAG

- Hybrid graph+vector retrieval (not just cosine similarity)
- Single unified interface vs multiple specialized tools
- Tables and equations are first-class content types (not stripped or ignored)
- MinerU parser handles complex PDF layouts that markitdown struggles with
- VLM-Enhanced Query mode for visual-textual integration in one pass

## Relevance to ClaudesCorner

| Concern | This Repo |
|---|---|
| Fabric RAG ingestion | Drop-in upgrade over markitdown-mcp for scanned/complex docs |
| markitdown-mcp gap | MinerU handles layouts markitdown can't (multi-column, equation-heavy) |
| memory-mcp retrieval | Graph+vector fusion pattern = ENGRAM v2 backend candidate alongside Cognee |
| bi-agent schema blocks | Table analyzer extracts structured data from XLSX/PPTX = DAX schema input |

## Installation

```bash
pip install rag-anything
# Optional: LibreOffice for Office format support
```

Async-first design. OpenAI API integration examples provided. Python 3.10+.

## Signal

**HKUDS also built DeepTutor** (20.1k stars, SKILL.md validation). RAG-Anything is the retrieval infrastructure complement — DeepTutor is the skill layer, RAG-Anything is the knowledge layer. Together they form a complete agent knowledge stack from HKUDS.

Technical report: arXiv:2510.12323
