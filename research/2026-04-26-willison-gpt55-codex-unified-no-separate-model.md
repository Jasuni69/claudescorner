---
title: "Willison/Huet — GPT-5.5 Unified: No Separate Codex Model"
date: 2026-04-26
source: https://simonwillison.net/2026/Apr/25/romain-huet/
tags: [openai, gpt-5.5, model-routing, dispatch, competitive-signal]
relevance: high
---

# GPT-5.5 Unified: No Separate Codex Model

**Source:** Simon Willison quoting Romain Huet (OpenAI), April 25 2026
**Signal:** OpenAI model strategy — dispatch.py multi-provider routing implications

## Core quote

> "Since GPT-5.4, we've unified Codex and the main model into a single system, so there's no separate coding line anymore."
> — Romain Huet, OpenAI (via Willison's blog)

## What this means

OpenAI has merged its dedicated coding model (Codex) into the main GPT system starting with GPT-5.4. There is no separate coding-specialized GPT variant — GPT-5.5 is monolithic. The unified model "demonstrates strong gains in agentic coding, computer use, and any task on a computer."

## Implications for dispatch.py and Fairford

**Model routing:** Any dispatch.py multi-provider routing logic that assumes a distinct OpenAI coding endpoint (e.g., `codex-latest` or similar) is now moot. GPT-5.5 is the single model for all task types — there is no "coding tier" to route to separately from the "general tier."

**Competitive framing:** Anthropic still maintains the Haiku/Sonnet/Opus tier split for cost/capability routing. GPT-5.5's single-model approach makes OpenAI less suited to the tiered dispatch.py architecture (cheap leaf-node + expensive orchestrator). Sonnet 4.6 default remains correct.

**Prompt incompatibility stands:** Willison's earlier note that GPT-5.5 requires full re-tuning (not drop-in replacement) is reinforced — the unified architecture is a new model family, not an upgrade of Codex patterns.

**K2VV ToolCall benchmark still required** before routing any Fairford work to GPT-5.5. The unification does not resolve tool-call serialization compatibility.

## Action items

- No change to dispatch.py — Sonnet 4.6 default confirmed; no OpenAI coding-specific route to add
- If evaluating GPT-5.5 as fallback: treat as monolithic general model, not coding specialist
- Update any reference to `codex-latest` or "OpenAI coding model" in routing logic — the endpoint is simply GPT-5.5
