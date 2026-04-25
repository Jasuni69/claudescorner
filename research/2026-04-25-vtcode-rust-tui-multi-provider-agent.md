---
title: "VT Code — Rust TUI Coding Agent, Multi-Provider Failover, Agent Skills, A2A Protocol"
date: 2026-04-25
source: https://github.com/vinhnx/VTCode
stars: 508
tags: [rust, coding-agent, multi-provider, dispatch, agent-skills, a2a]
---

## Summary

VT Code is a Rust-native (93.8% Rust) TUI coding agent with multi-provider LLM failover, tree-sitter-bash safety validation, OS-level sandboxing, Agent Skills support, and Agent2Agent (A2A) protocol. 508 stars, 362 releases — actively maintained as of April 2026.

## Key Capabilities

### Multi-Provider Failover
Supports OpenAI, Anthropic, Google Gemini, DeepSeek, Ollama, LM Studio with automatic failover. This is the pattern dispatch.py currently lacks — if Anthropic rate-limits hit, workers stall rather than reroute.

### Safety Layer
- **tree-sitter-bash validation**: parses shell commands before execution; blocks injection-class attacks
- **Execution policies**: per-tool permission gates
- **OS sandboxing**: macOS Seatbelt + Linux Landlock; Windows support status unknown

### Protocols Implemented
- **Agent2Agent (A2A)**: Google's inter-agent communication protocol — allows VT Code instances to hand off tasks to other agents
- **Anthropic API compatibility**: drop-in for Claude Code workflows
- **ATIF trajectory format**: exports agent session history for replay/debugging

### Agent Skills
Compatible with agentskills.io standard — same SKILL.md format as skill-manager-mcp. `/plugin marketplace add` install pattern.

### Context Management
Built-in token budgeting with context window awareness — aligns with dispatch.py `MAX_CONTEXT_TOKENS=8000` pattern.

## Architecture

```
Rust TUI (Ratatui) → Provider Router → [Anthropic | OpenAI | Gemini | DeepSeek | Ollama]
                   → tree-sitter validator → sandbox (Seatbelt/Landlock)
                   → Agent Skills runtime
                   → A2A protocol bridge
```

## Relevance to ClaudesCorner

| Area | Signal |
|------|--------|
| **dispatch.py fallback routing** | Multi-provider failover pattern directly applicable; DeepSeek V4 / Qwen3.6 as Sonnet-tier fallback during rate limits |
| **Worker sandboxing** | tree-sitter-bash + Seatbelt/Landlock = lightweight alternative to CubeSandbox/smolvm for local workers |
| **A2A protocol** | If dispatch.py workers adopt A2A, inter-worker handoff becomes standardized — eliminates ad-hoc task_plan.md passing |
| **ATIF trajectory** | Session replay format useful for dispatch.py doom-loop post-mortems + cc-canary drift detection |
| **Rust TUI reference** | Second Rust TUI agent after claude-code-rust (94 stars); VT Code's 362 releases = production-grade reference |

## Gaps / Watch
- Windows sandbox (Seatbelt/Landlock) not confirmed — check before dispatch.py integration on Windows
- 508 stars is modest; monitor for community growth before heavy investment
- A2A is Google-origin; Anthropic has not formally adopted — interop risk
