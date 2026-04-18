---
title: "Codex Hacked a Samsung TV: Autonomous Kernel Privilege Escalation"
date: 2026-04-16
source: https://blog.calif.io/p/codex-hacked-a-samsung-tv
tags: [ai-agents, security, codex, autonomous-agents, capability-frontier]
relevance: agent-capabilities, agent-safety, security-research
hn_points: 180
---

## Summary

Researchers gave OpenAI's Codex a Samsung TV with a browser shell already compromised and tasked it with escalating to root. It succeeded — autonomously, without being told the specific exploit path.

## The Exploit Path (Codex-discovered)

1. Found world-writable device nodes (`/dev/ntksys`, `/dev/ntkhdma`) from Novatek Microelectronics drivers
2. Identified that `/dev/ntksys` accepted physical memory addresses without privilege validation ("physmap primitive")
3. Leaked a known physical address via `/dev/ntkhdma`
4. When `/proc/iomem` was blocked, pivoted to alternative sources
5. Scanned RAM using boot params from `/proc/cmdline`
6. Located browser process credential structure in physical memory
7. Overwrote identity fields → root

**Codex independently chose "overwrite kernel credentials" as the most practical path** — researchers never suggested it.

## What This Reveals About Agent Capabilities

- Autonomous reasoning under constraints: pivoted around blocked paths without guidance
- Iterative proof-building: validated primitives before escalating (mirrors human researcher workflow)
- Samsung's Unsigned Execution Prevention bypassed via in-memory file descriptors

## Critical Limitation

Without conversational steering ("bro, what did you do?"), Codex repeatedly went off-track. **Success required human oversight, not autonomous execution.** Current agents are sophisticated tool-users, not independent researchers.

## Implications for Jason's Work

- **Agent capability boundary**: Current agents (Claude Code, Codex) can do sophisticated multi-step technical reasoning — but still need human steering at branch points
- **ENGRAM/dispatch relevance**: Validates the human-in-the-loop checkpoints in the dispatch architecture; fully autonomous security tasks remain risky
- **Context for Glasswing**: Complements the Anthropic Project Glasswing clip — both show AI doing real security work at kernel level, but with different autonomy profiles
- **Dual-use signal**: As agents become more capable at exploit discovery, MCP governance layers (Agent Armor pattern) become more critical
