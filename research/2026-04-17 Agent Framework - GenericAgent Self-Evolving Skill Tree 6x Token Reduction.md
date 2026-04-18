---
title: "GenericAgent — Self-Evolving Agent with 5-Layer Memory and 6x Token Reduction"
date: 2026-04-17
source: https://github.com/lsdefine/GenericAgent
tags: [agent-framework, memory, skill-tree, token-efficiency, self-evolving]
relevance: high
---

# GenericAgent — Self-Evolving Agent with 5-Layer Memory and 6x Token Reduction

**Repo:** github.com/lsdefine/GenericAgent | MIT | 2,890 stars (+872 today)

## What It Does

Minimal autonomous agent (~3K LOC core) that grants LLMs full system-level control via 9 atomic tools + ~100-line agent loop. Supports browser automation, terminal, file management, keyboard/mouse, screen vision, and ADB (mobile).

The defining feature: **self-evolution**. When the agent solves a new task, it crystallizes the execution path into a reusable **Skill** stored in layered memory. Subsequent similar tasks invoke the Skill directly — one-line activation instead of full re-exploration.

## Memory Architecture (5 Layers)

| Layer | Content |
|---|---|
| L0 | Meta rules and system constraints |
| L1 | Insight index for fast routing/recall |
| L2 | Global facts from long-term operation |
| L3 | Task Skills and standard operating procedures |
| L4 | Session archives for long-horizon recall |

## Token Efficiency

Claims **6x less token consumption** vs comparable frameworks by keeping context under 30K (vs 200K–1M for others). Only the right knowledge is loaded per task — less noise, fewer hallucinations.

## 9 Atomic Tools

`code_run`, `file_read`, `file_write`, `file_patch`, `web_scan`, `web_execute_js`, `ask_user`, + 2 memory management tools.

## Notable

- Self-bootstrapping: repo itself was built autonomously by GenericAgent — author never opened a terminal
- Real browser injection preserves login sessions (no sandboxing)
- Dynamic capability extension via runtime code + package install
- Bot frontends: WeChat, Telegram, QQ, Lark, DingTalk, WeCom
- Supports Claude, Gemini, Kimi, MiniMax via API keys

## Relevance to Jason's Work

Direct parallel to **ENGRAM** — same 5-layer memory concept, same skill-crystallization pattern. GenericAgent proves the architecture at scale (production usage, self-bootstrapped). Key differences: GenericAgent is standalone Python; ENGRAM is Claude Code-native with MCP. Worth monitoring for ideas on L1 insight indexing and the skill promotion heuristics.
