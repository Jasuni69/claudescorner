---
title: "Anthropic Changelog: Advisor Tool — Public Beta"
date: 2026-04-26
source: https://platform.claude.com/docs/en/release-notes/overview
tags: [anthropic, advisor-tool, model-routing, dispatch, api, tiered-inference]
clipped_by: dispatch-agent
---

# Advisor Tool — Public Beta (Apr 9, 2026)

**Source:** Anthropic Docs Changelog  
**Signal strength:** HIGH — native API primitive for tiered model routing; direct architectural relevance to dispatch.py Haiku/Sonnet/Opus tier split

## What shipped

The **advisor tool** is now in public beta. Enable via beta header `advisor-tool-2026-03-01`.

**How it works:**  
Pair a fast **executor model** (e.g. Haiku 4.5) with a high-intelligence **advisor model** (e.g. Opus 4.7 or Sonnet 4.6) that provides strategic guidance mid-generation. The bulk of token generation happens at executor-model rates; the advisor intervenes at key decision points to provide higher-quality guidance.

**Target workloads:** Long-horizon agentic tasks where you want close-to-advisor-quality output at executor-model cost.

## Why this matters for ClaudesCorner

**dispatch.py tier architecture:**  
dispatch.py currently implements tiered routing manually: Haiku for leaf nodes, Sonnet for standard workers, Opus reserved for planning/orchestration. The advisor tool is a *native API primitive* that achieves the same cost/quality tradeoff within a single API call — no manual routing logic required.

Key differences:
- **dispatch.py manual routing**: separate API calls per tier, explicit worker role assignment, no mid-generation escalation
- **advisor tool**: single API call, advisor intervenes dynamically mid-generation, no need to predict upfront which tasks need Opus

**When to prefer advisor tool over manual routing:**
- Tasks where the escalation point is unpredictable (e.g. code generation that might hit an edge case)
- Single-turn long-horizon work where you don't want to pre-classify task complexity
- When you want Opus-quality decision-making at Haiku token throughput for the bulk generation

**When to keep manual dispatch.py routing:**
- Parallel worker pools where each worker has a known role (plan/build/verify = Sonnet tier)
- Tasks with hard token budgets that need predictable cost
- Fabric/MCP-heavy workflows where per-worker tool scoping matters more than mid-generation intelligence

**bi-agent DAX oracle:**  
The 3-layer oracle in bi-agent (verdict + parens + schema cross-ref) currently uses a single model pass. Advisor tool could run the schema cross-ref step at Opus quality mid-generation while keeping the main DAX synthesis at Sonnet rates. Worth prototyping for complex DAX queries.

## Integration path

```python
# Example: advisor tool in Messages API
response = client.messages.create(
    model="claude-haiku-4-5-20251001",  # executor
    max_tokens=4096,
    betas=["advisor-tool-2026-03-01"],
    advisor={
        "model": "claude-sonnet-4-6",   # advisor
    },
    messages=[{"role": "user", "content": "..."}]
)
```

(Exact schema TBD — check `/docs/en/agents-and-tools/tool-use/advisor-tool` for full API spec.)

## Actionable backlog

1. Read advisor tool docs: confirm API schema and pricing model (is advisor billed at advisor-model rates for tokens it generates?)
2. Prototype advisor tool for bi-agent DAX schema cross-ref step: Haiku executor + Sonnet advisor
3. Evaluate for dispatch.py tier-2 workers (standard Sonnet tasks): Haiku executor + Sonnet advisor vs. straight Sonnet — latency and cost comparison
4. Add `advisor-tool-2026-03-01` to dispatch.py's available beta headers list

## Related changelog items (same period)

- **Apr 23**: Managed Agents memory public beta (see companion clip)
- **Apr 24**: Rate Limits API — programmatic org/workspace rate limit queries
- **Apr 20**: Claude Haiku 3 retired — all `claude-3-haiku-20240307` calls now error; confirm dispatch.py uses `claude-haiku-4-5-20251001`
- **Mar 30**: Message Batches API max_tokens raised to 300k (beta header `output-300k-2026-03-24`) for Opus 4.6 + Sonnet 4.6 — useful for dispatch.py batch artifact generation
- **Feb 19**: Automatic caching GA — single `cache_control` field, system moves cache point forward automatically; simplifies bi-agent prompt caching implementation
