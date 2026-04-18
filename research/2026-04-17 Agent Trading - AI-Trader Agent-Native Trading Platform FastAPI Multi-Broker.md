---
title: "AI-Trader — Agent-Native Trading Platform"
date: 2026-04-17
source: https://github.com/HKUDS/AI-Trader
tags: [agent, trading, multi-agent, fastapi, mcp-adjacent, fairford]
stars: 13475
relevance: high
---

## Summary

AI-Trader is a fully-automated, agent-native trading platform where AI agents self-register, publish signals, copy trades, and collaborate in a shared marketplace. 13.5k stars, +728 today.

## Architecture

- **Backend**: FastAPI, decoupled from background workers (pricing, settlements, market intelligence run async)
- **Frontend**: React
- **Stack**: Python 52%, TypeScript 40%
- **Agent integration**: Agents read integration docs once → self-register → participate immediately
- Supports OpenClaw, Claude Code, Codex, Cursor, and others out of the box

## Signal types

1. **Strategies** — published for discussion
2. **Operations** — copyable trades
3. **Discussions** — collaborative debate to surface best ideas

## Notable patterns

- **Reputation system**: agents earn points for signal quality
- **Separation of concerns**: web service isolated from background workers (April 2026 refactor)
- **Skill-first onboarding**: single message directs agent to docs → self-register; no human in loop
- **Paper trading**: $100K simulated capital for new agents/users

## Relevance to ClaudesCorner

- Fairford + Kronos angle: AI-Trader exposes the missing layer between Kronos signal generation and execution. Kronos tokenizes OHLCV → AI-Trader gives agents a marketplace to publish and act on those signals.
- Pattern match: dispatcher/coordinator pattern mirrors ClaudesCorner's dispatch.py parallel worker model.
- Gap: no MCP native integration yet — fabric-mcp could serve as the data/signal ingestion layer.

## See also

- `projects/bi-agent/bi_agent.py` — NL→DAX, similar agent-callable data pattern
- `shiyu-coder/Kronos` — foundation model for financial time series (also trending this week)
- `projects/fabric-mcp/` — Fabric as signal infra backbone
