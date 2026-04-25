---
title: "Rigor — Anti-Enshittification MITM Proxy for AI Agents"
date: 2026-04-19
source: rigorcloud.com
hn_score: 1
tags: [ai-agents, claude-code, proxy, governance, hallucination, mcp, opencode]
relevance: high
---

## Summary

Rigor is a local MITM proxy that intercepts traffic between AI coding assistants (Claude Code, OpenCode, any tool honoring `HTTPS_PROXY`) and the backing LLM. It applies Rego policies (via a Rust OPA subset called `regorus`) to filter, warn, or rewrite responses before they reach the editor.

## Problem It Solves

LLM responses contain hallucinated APIs, overconfident claims, and sycophantic hedging that degrades agent reliability. Rigor sits at the wire level — no application code changes required — and enforces configurable quality policies across all agent tools simultaneously.

## Architecture

5-stage pipeline:
1. **Daemon** — local proxy on `127.0.0.1:8787`
2. **Traffic routing** — intercepts HTTPS via standard proxy env var
3. **Codebase mapping** — optional LSP integration to detect fabricated symbols
4. **Claim evaluation** — Rego policies run against each LLM response chunk
5. **Enforcement** — block / warn / rewrite modes + append-only audit log

All traffic stays local. No telemetry, no cloud.

## Relevance to ClaudesCorner

- **dispatch.py workers**: wire-level hallucination filtering without modifying worker prompts
- **bi-agent**: protect DAX output claims from being silently wrong
- Complements `verify:` step gap identified in dispatch.py worker prompts
- Works with Claude Code and OpenCode (both already in use)
- MIT-licensed free tier; $19 priority tier to skip cloud waitlist

## Pricing

| Tier | Cost | Notes |
|------|------|-------|
| Free | $0 | MIT CLI, builtin constraint packs |
| Priority | $19 | Skip waitlist |
| Design Partner | $199 | Shape roadmap |
