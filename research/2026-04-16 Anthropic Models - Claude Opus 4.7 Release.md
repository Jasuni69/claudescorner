---
title: "Claude Opus 4.7 Release"
date: 2026-04-16
source: https://www.anthropic.com/news/claude-opus-4-7
tags: [anthropic, claude, models, agentic, claude-code]
type: research-clip
---

# Claude Opus 4.7 Release

**HN:** 667 pts / 521 comments

## Key Upgrades

- **Coding**: 13% improvement on coding benchmarks vs Opus 4.6; 3x more production tasks resolved on Rakuten-SWE-Bench; 70% on CursorBench (up from 58%)
- **Vision**: images up to 2,576px on long edge (~3.75 megapixels) — 3x previous; better on chemical structures and technical diagrams
- **Computer use**: 98.5% visual acuity (vs 54.5% prior)
- **Reasoning control**: new `xhigh` effort level between `high` and `max` for finer latency/quality tradeoff
- **Multi-session memory**: improved memory usage across sessions
- **Tool calling**: better accuracy + graceful error recovery

## Claude Code Integration

- New `/ultrareview` slash command for dedicated code review sessions
- Extended auto mode to Max users (fewer interruptions, Claude decides autonomously)
- Default effort raised to `xhigh` for all plans

## Pricing & Access

- $5/M input tokens, $25/M output — unchanged from 4.6
- Model ID: `claude-opus-4-7`
- Available: API, Bedrock, Vertex AI, **Microsoft Foundry**

## Security Note

Cybersecurity capabilities intentionally constrained. New Cyber Verification Program for legitimate security research.

## Relevance

Direct upgrade for all Jason's Claude API projects (bi-agent, fabric-mcp, skill-manager-mcp). `/ultrareview` is useful for ClaudesCorner code review sessions. `xhigh` default means better agentic outputs without manual effort tuning. Microsoft Foundry availability is relevant to Fabric/Clementine work.
