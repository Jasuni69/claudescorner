---
title: "Hermes Agent — Self-Improving Skills and MCP Integration"
date: 2026-04-16
source: https://github.com/NousResearch/hermes-agent
tags: [agent-framework, skills, mcp, self-improvement, nous-research]
relevance: high
---

## Summary

NousResearch/hermes-agent — 91k GitHub stars (+53k this week). Self-improving AI agent framework with closed-loop skill creation, cross-platform deployment, MCP support, and the agentskills.io open standard.

## Key Technical Points

- **Closed-loop learning**: Agent creates skills from experience, refines them during use, consolidates memory periodically — no manual configuration required
- **MCP-native**: 40+ built-in tools plus MCP server support for extended capabilities
- **agentskills.io standard**: Open skill format promoting ecosystem compatibility between agent frameworks
- **Multi-platform**: Terminal, Telegram, Discord, Slack, WhatsApp, Signal, email — same agent, any surface
- **Distributed execution**: Local, Docker, SSH, serverless (Daytona, Modal) — environments hibernate when idle for cost efficiency
- **Subagent spawning**: Parallel work via subagents, Python script execution via RPC
- **Model-agnostic**: Nous Portal, OpenRouter (200+ models), OpenAI, Anthropic, Hugging Face, self-hosted

## Why It Matters for Jason

1. **agentskills.io** — if skills become a cross-framework standard, ENGRAM's skill packaging could target this format for broader adoption
2. **Closed-loop skill creation** is exactly what the `continuous-learning` skill + `feedback_flywheel.py` implements locally — Hermes has commercialized this pattern at scale
3. **MCP-native from day one** validates Jason's infrastructure bet on MCP as the integration layer
4. The 53k-star weekly spike suggests the self-improving agent space is breaking into mainstream — timing for ENGRAM positioning

## Architecture Notes

Python 93.2%, TypeScript for gateways. Modular: agent logic / messaging gateways / skills / tools / testing. Cron scheduler built-in for autonomous operation.

## ENGRAM Relevance

Hermes is the closest public analog to what ENGRAM is trying to package. Key differentiator: ENGRAM targets Claude Code specifically + Obsidian/memory architecture. Hermes is model-agnostic and platform-broad. Different audiences — Hermes for general deployment, ENGRAM for Claude Code power users wanting persistent identity.
