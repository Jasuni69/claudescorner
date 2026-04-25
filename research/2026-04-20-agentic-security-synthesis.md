---
title: "Agentic Security Synthesis: SoK vectors + dispatch.py exposure"
date: 2026-04-20
tags: [security, dispatch, agentkey, agentrq, verify-oracle]
sources:
  - research/2026-04-20-sok-agentic-commerce-security.md
  - research/2026-04-20-browser-use-agent-captcha.md
---

# Agentic Security Synthesis

## 1. SoK Vectors That Apply to dispatch.py Workers

Of the 12 cross-layer vectors, five land directly on dispatch.py:

| Vector | Dimension | How it hits dispatch.py |
|--------|-----------|------------------------|
| Prompt injection | Agent integrity | Worker prompts built from `tasks.json` fields — malicious task content injects into system prompt |
| Goal drift | Agent integrity | Long-horizon tasks across 3 parallel workers lose original objective without a terminal assertion |
| Replay attacks | Transaction auth | Completed task IDs not invalidated — a requeued task re-executes with old context |
| Unverified sub-agent spawning | Inter-agent trust | Workers can spawn `Agent(...)` calls with no identity check on the spawned subagent |
| Unsigned delegation | Transaction auth | fabric-mcp tool calls carry no per-call authorization token — worker credentials are ambient |

Vectors in dimensions 4–5 (market manipulation, regulatory) don't apply at current scope.

## 2. AgentKey + AgentRQ Gap Coverage

**Closes:** unsigned delegation (AgentKey per-credential governance), unverified spawning (AgentKey identity at handoff), replay attacks (AgentKey append-only audit log enables dedup).

**Partial:** goal drift — AgentRQ escalation catches it only if the worker self-identifies drift; no automatic terminal assertion.

**Open:** prompt injection. Neither tool sanitizes task payload before it enters worker context.

## 3. Concrete Hardening Action for the Verify Oracle

Add a **terminal assertion check** to every dispatch.py worker: after the task body executes, inject a fixed closing prompt — `"State in one sentence what you did. Does this match the original task: {task_description}? Answer YES or NO."` — and gate success on a YES response. This turns the verify oracle into a goal-drift detector at zero additional latency cost (same Claude call, just a suffix prompt).
