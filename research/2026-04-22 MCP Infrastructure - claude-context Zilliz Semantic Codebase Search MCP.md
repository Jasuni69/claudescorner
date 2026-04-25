---
title: "claude-context — Zilliz Semantic Codebase Search MCP"
date: 2026-04-22
source: https://github.com/zilliztech/claude-context
tags: [mcp, claude-code, semantic-search, vector-db, infrastructure, token-reduction]
signal: high
---

# claude-context — Zilliz Semantic Codebase Search MCP

**Stars:** 6,900 | **License:** MIT | **Org:** Zilliz (Milvus creators) | **Node:** ≥20.0.0

## What It Does

MCP server that indexes an entire codebase into Milvus/Zilliz Cloud and exposes semantic search over it. Agents retrieve only the relevant code snippets for each query — no expensive full-directory context loading.

## Architecture

| Package | Role |
|---|---|
| `@zilliz/claude-context-core` | Core indexing + hybrid search library |
| `@zilliz/claude-context-mcp` | MCP server wrapping the core |

**Retrieval:** Hybrid BM25 (keyword) + dense vector (semantic) — best of both recall strategies.

**Embedding models supported:** OpenAI, VoyageAI, and other providers (configurable).

**Storage:** Milvus (self-hosted) or Zilliz Cloud (managed).

## Key Stats

- **~40% token reduction** vs loading entire directories at equivalent retrieval quality
- Supports Claude Code, Cursor, Gemini CLI, and any MCP-compatible agent
- File inclusion/exclusion rules for selective indexing

## Relevance to ClaudesCorner

- **dispatch.py Tier 2/3 workers**: Workers operating on large repos currently load full files for context. claude-context as an MCP tool would let workers issue a semantic query instead — direct path to the MAX_CONTEXT_TOKENS=8000 budget being used for reasoning rather than file dumps.
- **memory-mcp complement**: memory-mcp = semantic search over `.md` knowledge files; claude-context = semantic search over source code. Together they cover the full knowledge surface (structured facts + live code) without redundancy.
- **bi-agent schema retrieval**: bi-agent currently embeds the full DAX schema block with `cache_control=ephemeral`. If the schema grows large, claude-context could serve relevant table/measure definitions on demand instead.
- **ENGRAM**: ENGRAM's vectorstore.db indexes `.md` files. claude-context is the code-layer analog — document both as complementary retrieval layers in ENGRAM README.

## Architecture Fit

```
dispatch.py worker
  → mcp call: claude-context.search("token refresh logic")
  → returns: 3 relevant snippets from across codebase
  → worker reasons on snippets (stays under 8K token budget)
```

vs current:

```
dispatch.py worker
  → Read full file (often 200-400 lines = 2-4K tokens wasted)
```

## Gaps / Watch Items

- Requires Milvus or Zilliz Cloud — adds external dependency (Milvus = Docker, Zilliz = managed SaaS)
- Windows Docker setup needed for self-hosted Milvus
- Zilliz Cloud free tier: check current limits before using for Fairford
- No offline/SQLite mode — not as lightweight as vectorstore.db (all-MiniLM-L6-v2 local)

## Action

Medium priority: test claude-context on the projects/ directory to measure actual token reduction on dispatch.py worker invocations. Compare against current Glob+Read pattern. If 40% reduction holds, wire as optional MCP in settings.json under a `code-search` key.
