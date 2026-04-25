---
title: "Hermes Agent — 102k Stars, Self-Improving Loop, MCP + agentskills.io"
date: 2026-04-20
source: https://github.com/NousResearch/hermes-agent
stars: 102158
weekly_gain: 38194
tags: [ai-agents, skills, memory, mcp, engram, self-improvement]
relevance: high
---

# Hermes Agent (NousResearch) — 102k Stars

**+38,194 stars this week** — largest weekly gain on GitHub trending today.

## What It Is

Self-improving AI agent by Nous Research. "The only agent with a built-in learning loop." Autonomous skill creation, knowledge persistence, adaptive user modeling across sessions.

## Key Features

- **Autonomous skill generation** — after completing complex tasks, generates and stores reusable skills; compatible with agentskills.io open standard
- **5-layer memory**: persistent user profile, FTS5 session search with LLM summarization, cross-session recall, trajectory compression for training
- **Honcho dialectic user modeling** — adapts to individual user patterns over time
- **MCP compatible** — plugs into MCP servers for extended capabilities
- **Subagent spawning** — parallel workstreams via sub-agent dispatch
- **Multi-platform**: Telegram, Discord, Slack, WhatsApp, Signal, CLI
- **40+ tool integrations** — cron scheduling, terminal execution (local/Docker/SSH/Daytona/Modal)
- **Model-agnostic**: Nous Portal, OpenRouter (200+ models), NVIDIA NIM, OpenAI, Anthropic, custom endpoints

## Architecture Patterns

- RPC-based tool invocation from Python scripts
- Trajectory compression → training data for tool-calling fine-tunes
- Batch generation for research workflows
- Context files shape multi-turn conversations
- Serverless hibernation on Daytona/Modal

## Relevance to ClaudesCorner

| Hermes | ClaudesCorner analog |
|--------|---------------------|
| Autonomous skill generation | skill-manager-mcp + PostToolUse hook |
| FTS5 + LLM summary cross-session recall | memory-mcp vectordb (all-MiniLM-L6-v2) |
| agentskills.io standard | SKILL.md YAML frontmatter format |
| Sub-agent spawning | dispatch.py parallel workers |
| MCP integration | fabric-mcp, windows-mcp, deadlines-mcp |
| Honcho user modeling | SOUL.md + daily logs |

**Key gap**: Hermes has no MCP-native fabric/BI layer — fabric-mcp is differentiated.  
**Key gap**: Hermes skill store is file-based; skill-manager-mcp adds semantic search via vectordb.  
**Action**: Adopt agentskills.io SKILL.md format as canonical skill frontmatter in skill-manager-mcp — Hermes + anthropics/skills converge on same spec.

## License

MIT — 508+ contributors, active Discord.
