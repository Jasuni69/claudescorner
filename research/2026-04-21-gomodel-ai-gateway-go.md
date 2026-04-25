---
title: "GoModel — Go AI Gateway, 44x Lighter Than LiteLLM"
date: 2026-04-21
source: https://github.com/ENTERPILOT/GOModel
tags: [ai-gateway, llm-routing, caching, observability, dispatch]
points: 63
---

# GoModel — Go AI Gateway, 44x Lighter Than LiteLLM

**Source**: HN Show HN, 63pts — github.com/ENTERPILOT/GOModel  
**Signal**: Dual-layer semantic cache hits 60–70% on repetitive workloads at sub-ms latency; direct cost-reduction primitive for dispatch.py LLM call overhead.

## What It Is

GoModel is a high-performance AI gateway written in Go that exposes a unified OpenAI-compatible API. It acts as a routing and caching layer between applications and multiple LLM providers, auto-detecting available providers from supplied credentials.

## Key Features

- **Multi-provider**: OpenAI, Anthropic, Google Gemini, Groq, OpenRouter, xAI, Azure OpenAI, Oracle, Ollama
- **Dual-layer caching**:
  - Layer 1: Exact-match cache — sub-millisecond lookup
  - Layer 2: Semantic cache via vector embeddings — 60–70% hit rate on high-repetition workloads (vs ~18% exact-match alone)
- **Observability**: Prometheus metrics, audit logging, admin dashboard
- **OpenAI-compatible endpoints**: chat completions, embeddings, file handling, batches, passthrough routes
- **Guardrails**: request inspection + response filtering baked into pipeline before caching
- **License**: MIT

## Architecture

Requests → guardrail/workflow patching → exact-match cache → semantic cache → upstream provider. Both cache tiers run post-guardrail, ensuring consistent security enforcement regardless of cache hit.

## Relevance to ClaudesCorner

- **dispatch.py workers**: identical sub-prompts (schema checks, oracle validation, summarization) hit semantic cache repeatedly — 60–70% cache rate = substantial Anthropic API cost reduction
- **bi-agent**: repeated DAX pattern lookups are high-repetition → semantic cache maps directly onto cache_control=ephemeral pattern already in place
- **fabric-mcp**: acts as provider-agnostic routing layer; Anthropic + Azure OpenAI both supported, relevant to Fairford hybrid stack
- Lighter than LiteLLM (Go binary vs Python runtime) = lower overhead in scheduled task context

## Action Items

- Benchmark GoModel semantic cache against current direct Anthropic API calls in dispatch.py
- Evaluate as routing layer between dispatch.py workers and Anthropic/Azure for Fairford Phase 2
- Check if GoModel supports streaming (required for dispatch.py worker output streaming)
