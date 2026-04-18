---
title: "ai-hedge-fund — 19-Agent Financial Multi-Agent Orchestration System"
date: 2026-04-17
source: https://github.com/virattt/ai-hedge-fund
tags: [agents, multi-agent, finance, claude, orchestration, fairford]
signal: high
---

# ai-hedge-fund — 19-Agent Financial Multi-Agent System

**Repo:** virattt/ai-hedge-fund | 55.8k stars, +763 today | 9.7k forks

## What It Is

Educational proof-of-concept for a multi-agent hedge fund. 19 specialized agents collaborate to produce trading signals from financial data. No live trading — simulation and backtesting only.

## Agent Roster

**Investor Personas (13):** Aswath Damodaran, Ben Graham, Bill Ackman, Cathie Wood, Charlie Munger, Michael Burry, Mohnish Pabrai, Nassim Taleb, Peter Lynch, Phil Fisher, Rakesh Jhunjhunwala, Stanley Druckenmiller, Warren Buffett

**Analytical Agents (6):** Valuation, Sentiment, Fundamentals, Technicals, Risk Manager, Portfolio Manager

## Data Flow

```
User (tickers + date range)
  → Financial Datasets API
    → 19 parallel agent analyses
      → Risk Manager validation
        → Portfolio Manager aggregation
          → Trading signals + backtest
```

## LLM Support

- Primary: OpenAI (GPT-4o, GPT-4o-mini)
- Also: **Anthropic/Claude**, Groq, DeepSeek
- Local: Ollama

## Tech Stack

- Python + Poetry backend
- TypeScript/React frontend (`/app`)
- Docker support
- Financial Datasets API for market data

## Relevance to Jason's Work

**Fairford/Fabric angle:** The persona-agent pattern maps directly onto a Fabric-backed multi-agent setup — replace Financial Datasets API with Fabric lakehouses, wire Claude as the LLM, and the orchestration pattern is immediately usable for portfolio analysis or risk dashboards.

**ENGRAM pattern match:** 19 specialized agents with a coordinator (Portfolio Manager) mirrors the dispatcher → subagent → aggregator pattern in ClaudesCorner. The Risk Manager as a validation gate is identical to the verification-before-completion pattern.

**No MCP integration** currently — gap that could be filled by adding fabric-mcp as the data layer tool.

## Signal

Star spike (+763 in one day) driven by Reddit/HN visibility. Well-maintained, MIT licensed, actively developed. Worth forking as a Fabric + Claude reference implementation.
