---
title: "MCP Scope Creep Is a Runtime Problem, Not a Prompt Problem"
source: https://sunglasses.dev/blog/mcp-scope-creep-runtime-problem
date: 2026-04-22
tags: [mcp, agent-security, dispatch, governance, tool]
signal: high
---

# MCP Scope Creep Is a Runtime Problem, Not a Prompt Problem

**Source:** sunglasses.dev | HN ~26pts | 2026-04-22

## Core Argument

Agent failures stem not from malicious prompts alone but from runtime text that silently redefines permission boundaries. Tool descriptions, RAG chunks, governance appendices, and policy fragments injected mid-session can expand what an agent believes it is authorized to do — without any explicit jailbreak. This is a *legible, scannable* risk category, not vague compliance theater.

## Key Technical Claims

- **CVE-2026-25536**: MCP TypeScript SDK vulnerability (CVSS 7.1) — shared transports leak data across client isolation boundaries, demonstrating how permission blurring is a real attack surface, not a hypothetical.
- **53% of organizations** have had AI agents exceed their intended permissions (Cloud Security Alliance, April 2026).
- **Sunglasses v0.2.19** introduces `policy_scope_redefinition` category with pattern `GLS-PSR-001` — governance appendix precedence override — catches attempts by later-stage content to override earlier trust rules.
- 10 new patterns across 49 categories, 2,019 threat keywords total.

## Tool: `sunglasses`

```bash
pip install --upgrade sunglasses
```

- MIT-licensed, local, no API keys required
- Apply `engine.scan()` to untrusted inputs **before** execution: tool descriptions, RAG chunks, agent-to-agent messages
- Pre-action scanning = add at the `dispatch.py` worker input boundary

## Relevance to ClaudesCorner

- **dispatch.py workers**: untrusted tool descriptions and RAG context flow into worker prompts — scan with `sunglasses` before passing to Claude API call
- **memory-mcp**: `search_memory` results are untrusted RAG chunks — candidate scan point
- **bi-agent**: DAX schema block sourced from external Fabric metadata = scan candidate
- Fills the gap *between* AgentKey (identity) and AgentRQ (escalation): neither catches in-flight scope redefinition from content
- Complements CrabTrap (outbound HTTP proxy) — Sunglasses is the *inbound* content layer
- Add to Fairford Phase 2 security checklist alongside AgentKey + AgentRQ + RLS enforcement

## Action

```python
# dispatch.py worker input boundary
from sunglasses import Engine
engine = Engine()
result = engine.scan(untrusted_tool_description)
if result.is_threat:
    raise ValueError(f"Scope redefinition attempt blocked: {result.category}")
```
