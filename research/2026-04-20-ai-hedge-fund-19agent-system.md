---
title: "ai-hedge-fund — 19-Agent Financial Multi-Agent System (Coordinator/Validator Pattern)"
date: 2026-04-20
source: https://github.com/virattt/ai-hedge-fund
stars: 56446
stars_gained_weekly: 4458
tags: [financial-ai, multi-agent, coordinator-pattern, fabric, fairford, mcp-opportunity]
signal: high
---

# ai-hedge-fund — 19-Agent Financial Multi-Agent System

**Repo:** virattt/ai-hedge-fund | 56.4k stars | +4,458 this week | MIT

## What It Is

Proof-of-concept multi-agent system for AI-driven financial analysis. 19 specialized agents organized in three tiers: investor persona agents generate independent signals, analysis agents produce domain-specific reports, and infrastructure agents gate decisions through risk management before final execution. Explicitly educational — no live trading.

## Agent Architecture (3 Tiers)

### Tier 1 — Investor Persona Agents (13)
Simulate famous investor strategies as independent signal generators:
- **Value:** Aswath Damodaran, Ben Graham, Charlie Munger, Michael Burry, Mohnish Pabrai
- **Growth:** Cathie Wood, Phil Fisher, Peter Lynch
- **Macro/Contrarian:** Nassim Taleb, Stanley Druckenmiller, Bill Ackman
- **Regional:** Rakesh Jhunjhunwala
- **Foundational:** Warren Buffett

### Tier 2 — Analysis Agents (4)
Independent signal generation by domain:
- Valuation Agent
- Sentiment Agent
- Fundamentals Agent
- Technicals Agent

### Tier 3 — Infrastructure Agents (2)
- **Risk Manager** — enforces position limits, computes risk metrics across all signals
- **Portfolio Manager** — final decision synthesizer; aggregates all tier 1 + tier 2 signals through tier 3 risk gate

## Coordination Model

Agents generate independent signals → Portfolio Manager synthesizes via risk-managed consensus. Classic fan-out/fan-in coordinator pattern: no single agent has final authority, risk gate is mandatory chokepoint.

## LLM Support

- **Primary:** OpenAI (gpt-4o, gpt-4o-mini)
- **Alternatives:** Anthropic (Claude), Groq, DeepSeek, Ollama (local)
- Financial data via Financial Datasets API

## CLI

```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01
poetry run python src/backtester.py --ticker AAPL --start-date 2023-01-01 --end-date 2024-01-01
```

## Relevance to ClaudesCorner

**dispatch.py topology parallel:**
- 3-tier structure (investor/analysis/infrastructure) maps directly to dispatch.py worker tiers: leaf workers → aggregator → gatekeeper before output
- Risk Manager as mandatory chokepoint = verify oracle pattern; this is the `verify:` step missing from current dispatch.py workers
- Portfolio Manager consensus = the "coordinator synthesizes parallel worker outputs" pattern that dispatch.py v2 needs

**Fairford / fabric-mcp gap:**
- No MCP integration — all agents use direct LLM API calls
- Clear insertion point: wire fabric-mcp as the data connector (Fabric lakehouse → financial data) and expose investor agent outputs as MCP tools
- Kronos (see companion clip) fills the missing quantitative signal layer — investor persona agents currently use LLM judgment, not learned market models

**ENGRAM parallel:**
- Each investor persona agent is a SOUL.md sub-agent boundary: isolated identity, independent reasoning, scoped to one domain
- The 13 persona agents = ROLE.md-per-agent pattern from OpenClaw memory degradation reference

## Action Items

- [ ] Extract coordinator/validator pattern into dispatch.py v2 design doc — risk-gate chokepoint as verify oracle
- [ ] Map fabric-mcp Fairford Phase 2 data flow: Fabric lakehouse → ai-hedge-fund analysis agents → Portfolio Manager → Fabric output table
- [ ] Evaluate replacing Financial Datasets API dependency with fabric-mcp `query_lakehouse` tool
