---
title: "Memsearch — Markdown-First Cross-Platform Agent Memory"
date: 2026-04-25
source: https://github.com/zilliztech/memsearch
stars: 1381
license: MIT
tags: [agent-memory, markdown, vector-search, milvus, engram, memory-mcp, multi-platform]
relevance: high
---

# Memsearch — Markdown-First Cross-Platform Agent Memory

**1.4k stars · MIT · Python 63% / Shell 25% / TypeScript 12%**
By Zilliz (Milvus maintainers)

## What it is

Semantic memory infrastructure for AI coding agents. Markdown files are the source of truth; Milvus vector DB is a rebuildable shadow index. One memory store, accessible from Claude Code, OpenClaw, OpenCode, and Codex CLI simultaneously.

## Architecture

```
Plugins (Claude Code / OpenClaw / OpenCode / Codex)
    ↓
CLI / Python API (index, search, expand, watch)
    ↓
Core: Chunker → Embedder → Milvus
    ↓
Markdown Files (source of truth, human-editable)
```

- **File watcher** — detects markdown changes in real-time; SHA-256 content hashing skips unchanged files
- **Hybrid search** — dense vector embeddings + BM25 sparse search with RRF reranking
- **3-layer progressive retrieval**: semantic chunks → full section expansion → raw transcript

## Embedding options
- Default: ONNX bge-m3 (local, free, ~558 MB)
- Alternatives: OpenAI, Ollama, Google, Voyage, Jina, Mistral

## Python API

```python
mem = MemSearch(paths=["./memory"])
await mem.index()
results = await mem.search("dispatch worker patterns", top_k=3)
chunk = await mem.expand(results[0].hash)
```

## Agent memory cycle

1. Plugin captures conversation turn
2. LLM summarizes turn → appends to daily `.md` file
3. File watcher triggers re-index (chunking + embedding)
4. Next query: hybrid search → expand → inject context

## Signal for ClaudesCorner

**Validates ClaudesCorner's daily markdown log pattern** (`memory/YYYY-MM-DD.md`) as the correct architecture: markdown-as-source-of-truth + vector index as cache is exactly what `projects/brain-memory/` implements. Key gaps memsearch fills that memory-mcp doesn't yet have:

1. **Cross-platform sync** — same memory readable from Claude Code + OpenClaw + OpenCode + Codex via platform plugins; memory-mcp is Claude-Code-only
2. **BM25+vector hybrid with RRF reranking** — memory-mcp uses all-MiniLM-L6-v2 dense-only; RRF fusion is the missing upgrade
3. **SHA-256 delta indexing** — skip-unchanged optimization; brain-memory/index_all.py re-indexes everything

**Actionable**: add RRF hybrid search to brain-memory/src/vectordb.py; adopt SHA-256 content-hash delta in index_all.py to cut reindex time; evaluate memsearch as cross-platform plugin layer above memory-mcp for ENGRAM v2.
