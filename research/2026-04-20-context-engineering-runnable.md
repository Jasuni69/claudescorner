---
title: "Context Engineering — Runnable Reference (outcomeops/context-engineering)"
date: 2026-04-20
source: https://github.com/outcomeops/context-engineering
stars: 27
tags: [context, rag, memory, dispatch, agents, architecture]
relevance: medium
---

# Context Engineering — Runnable Reference

**Show HN, 17pts** — small repo but articulates a pattern worth naming.

## Core Thesis

Context is a first-class engineering artifact — version-controlled, retrievable, and enforceable — not ad-hoc prompting.

Defines 5 components:

1. **Corpus** — organizational knowledge (ADRs, standards, decisions)
2. **Retrieval** — identifying relevant corpus portions per request
3. **Injection** — loading context into model working memory
4. **Output** — generating reviewable artifacts (code, PRs, docs)
5. **Enforcement** — validating output reflects retrieved context

Standard RAG covers 1–3. Context engineering adds 4–5: output generation + enforcement for governance.

## Key Patterns

- **Token budgeting** — curate and limit what an agent sees (Anthropic Sep 2025 reference)
- **"Lost in the Middle" avoidance** — structural context injection order matters
- JSON Schema + tool-use for structured output
- MCP Registry cited for external tool integration

## Relevance to ClaudesCorner

**dispatch.py workers are missing steps 4–5**: they retrieve context (memory-mcp) and generate output, but have no enforcement/oracle layer that validates the output against retrieved context before committing.

This maps directly to the `verify:` gap identified from Willison's reference-repo prompting pattern (2026-04-18):
- dispatch.py worker prompts should embed an oracle that validates against corpus
- bi-agent DAX output should be validated against schema_spec.md before returning

**Token budgeting**: dispatch.py worker context windows are unbounded — add a `max_context_tokens` guard per worker using the `curate and limit` pattern.

## Action Items

- Add `verify:` oracle section to dispatch.py worker prompt template
- Add `max_context_tokens: 8000` soft cap to worker config
- Consider context-engineering 5-component model as ENGRAM architectural framing
