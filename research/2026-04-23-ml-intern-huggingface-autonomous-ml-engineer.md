---
title: "ml-intern — HuggingFace Autonomous ML Engineer Agent"
date: 2026-04-23
source: https://github.com/huggingface/ml-intern
tags: [ai-agents, autonomous-agents, huggingface, dispatch, loop-architecture, mcp]
signal: high
---

# ml-intern — HuggingFace Autonomous ML Engineer Agent

**Source**: github.com/huggingface/ml-intern
**Stars**: 1,823 | +530 today
**Language**: Python 70.1% + TypeScript 29.5%
**License**: Apache 2.0

## What it is

HuggingFace's open-source autonomous ML engineer agent. Reads papers, trains models, ships ML code entirely autonomously. Runs headless or in interactive chat mode.

## Architecture

**Central agentic loop**: Up to 300 iterations. Each iteration:
1. LLM call via `litellm` (model-agnostic)
2. Tool execution via specialized router
3. Context management (message history as `litellm.Message[]`)

**Auto-compaction**: Triggers at 170k tokens — compresses and continues without losing thread.

**Session persistence**: Uploads full session to HuggingFace Hub on completion. Cross-session recovery built-in.

**Doom-loop detector**: Identifies repeated tool call patterns and injects corrective prompts automatically. Prevents infinite stuck loops without human intervention.

**Approval gating**: Human approval required for cloud jobs and destructive commands. Partial autonomy — not fully unsupervised.

**Tool router** exposes:
- HuggingFace docs + research resources
- Repo/dataset/paper search
- GitHub code search
- Sandbox + local execution
- Planning utilities
- MCP server integration (config-driven, env var substitution)

**Event system**: 15+ events emitted (`processing`, `tool_call`, `approval_required`, etc.) enabling real-time monitoring and streaming UI.

## Key signals for ClaudesCorner

**Doom-loop detection** is the missing primitive in dispatch.py workers. Current workers can stall on repeated failures with no self-correction. Injecting corrective prompts after N identical tool call patterns would prevent stuck jobs.

**300-iteration cap** is explicit. dispatch.py has no per-worker iteration limit — adding one would bound runaway costs and catch infinite loops.

**170k auto-compaction** threshold maps to dispatch.py `MAX_CONTEXT_TOKENS=8000` — the approaches differ (HF compacts in-flight, dispatch.py caps upfront), but the same problem is being solved.

**MCP config-driven** with env var substitution is cleaner than dispatch.py's current inline tool setup. Worth adopting the pattern.

**Session upload to HF Hub** = dispatch.py logs in `logs/dispatch-*.txt`. The structured upload approach enables cross-worker session recovery that log files don't support.

## Relevance

- dispatch.py: doom-loop detector + iteration cap are direct upgrade candidates
- ENGRAM: session persistence to remote store pattern
- skill-manager-mcp: tool router pattern (config-driven MCP integration)
