---
title: "DeerFlow — ByteDance Long-Horizon SuperAgent Harness"
date: 2026-04-19
source: https://github.com/bytedance/deer-flow
tags: [multi-agent, orchestration, memory, sandboxing, MCP, claude, langraph, dispatch]
stars: 62649
stars_today: 214
relevance: high
---

## Summary

DeerFlow is ByteDance's open-source "SuperAgent harness" for long-horizon autonomous tasks (minutes to hours). Hierarchical agent orchestration with persistent memory, sandboxed execution, MCP native tool support, and multi-channel message routing. MIT license. Actively maintained (v2.0 rewrite).

## Architecture

**Agent hierarchy:** Lead coordinator spawns specialized sub-agents dynamically based on task complexity. Framework manages lifecycle.

**Memory:** Long-term persistent memory across sessions — agents retain context and learned patterns from previous runs.

**Sandboxing (3 modes):**
- Local execution
- Docker containers
- Kubernetes pods via provisioner service

**Message routing:** Telegram, Slack, Feishu/Lark, WeChat, WeCom — no public IP required.

**MCP:** Full MCP server support with HTTP/SSE transports and token refresh flows.

## Tech Stack

- Python 3.12+, LangGraph (agent runtime), LangChain
- Node.js 22+ React frontend
- Models: OpenAI, Anthropic Claude, Gemini, DeepSeek, Qwen, vLLM, OpenRouter
- Docker/Kubernetes for sandboxed execution

## Relevance to ClaudesCorner

**dispatch.py upgrade path:** DeerFlow's lead-coordinator + dynamic sub-agent spawning is the multi-worker pattern dispatch.py implements manually. Key gaps in current dispatch.py that DeerFlow solves:
- No persistent cross-run memory (currently just tasks.json + logs)
- No sandboxed execution (workers run in-process, security gap identified earlier)
- No dynamic worker spawning based on task complexity

**smolvm complement:** DeerFlow's Docker/K8s sandbox modes + smolvm (<200ms VM coldstart) are two approaches to the same isolation problem. smolvm fits lightweight dispatch workers; DeerFlow's model fits heavier research tasks.

**ENGRAM parallel:** DeerFlow's persistent memory layer is structurally identical to ENGRAM's memory-mcp. DeerFlow is a more production-hardened reference implementation.

**fabric-mcp opportunity:** No Fabric/Power BI integration in DeerFlow — MCP tool layer means fabric-mcp drops straight in.

## Action Items

- Review DeerFlow's LangGraph worker-spawning pattern for dispatch.py v2 design
- Evaluate Docker sandbox mode as replacement for bare worker subprocess execution
- `deer-flow` message routing (Slack gateway) = agent escalation channel missing from current stack
