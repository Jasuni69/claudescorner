---
title: "FinRL-Trading (FinRL-X) — AI-Native Quantitative Trading Infrastructure"
source: https://github.com/AI4Finance-Foundation/FinRL-Trading
author: AI4Finance Foundation
date: 2026-04-19
clipped: 2026-04-19
tags: [trading, agents, reinforcement-learning, fabric, bi-agent, fairford]
stars: 3002
today_gain: +12
relevance: medium-high
---

# FinRL-Trading — AI-Native Modular Quant Infrastructure

3k-star Apache-2.0 framework unifying data acquisition, strategy design, backtesting, and live execution under a **weight-centric interface**. Successor to the original FinRL project, explicitly designed for the LLM/agentic era.

## Architecture

Single mathematical contract: `w_t = R(T(A(S(X_≤t))))`

| Layer | Function |
|-------|----------|
| **S** — Stock selection | ML-based fundamental scoring (quarterly rebalance) |
| **A** — Portfolio allocation | DRL or classical (equal-weight, min-variance, mean-variance) |
| **T** — Timing adjustment | Weekly/daily regime detection |
| **D** — Risk overlay | Pre-trade checks, drawdown controls |

**Data**: Yahoo Finance, FMP, WRDS; SQLite caching  
**Backtest**: bt-powered engine, multi-benchmark comparison  
**Execution**: Alpaca integration (paper + live), multi-account support

## Performance (backtest Jan 2018 – Oct 2025)

- Adaptive Rotation Sharpe: **1.10** vs 0.81 QQQ, 0.72 SPY
- Calmar: **1.04** vs 0.56 QQQ
- Paper trading Oct 2025 – Mar 2026: **+19.76%**, Sharpe **1.96**

## LLM / Agent integration status

- Weight-centric interface is naturally MCP-compatible — any agent that outputs a weight vector can plug in
- No built-in LLM layer yet = **integration opportunity**
- Pydantic + env-var config supports dynamic prompt/model injection
- Sentiment preprocessing module ready for NLP signal enrichment

## Relevance to ClaudesCorner

- **bi-agent**: NL→DAX generator could extend to NL→portfolio-weight if Fabric data is piped in
- **Fairford PoC**: Fabric as data backbone → FinRL-X as strategy layer → Alpaca as execution = full signal→execution stack
- Pairs with Kronos (decoder-only time-series model) and tradingview-mcp for complete agent signal stack
- Gap vs. ai-hedge-fund (55k stars): FinRL-X has production-grade backtesting + live execution; ai-hedge-fund has richer agent personas but no MCP layer

## Action

Consider wrapping FinRL-X's weight-centric interface as an MCP tool — `allocate_portfolio(tickers, signals)` → weight vector → Alpaca order. Closes the Fairford execution loop without needing to rebuild the strategy engine.
