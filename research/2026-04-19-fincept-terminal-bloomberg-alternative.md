---
title: "FinceptTerminal — Open-Source Bloomberg Alternative with 37 AI Agents"
date: 2026-04-19
source: https://github.com/Fincept-Corporation/FinceptTerminal
stars: 5578
stars_delta_today: +1169
tags: [finance, ai-agents, mcp, fabric, trading, multi-agent, claude]
signal: high
relevance: Fairford PoC, fabric-mcp, bi-agent, multi-agent financial workflows
---

## Summary

FinceptTerminal is a native C++20 desktop application — open-source Bloomberg alternative — combining professional financial analytics with a multi-agent AI layer. **+1,169 stars today** (GitHub trending #1 Python, though the terminal itself is C++).

## Key Capabilities

- **37 agents** across investor personas (Buffett, Graham, Lynch, Munger, Klarman, Marks), economic analysis, and geopolitical frameworks
- **Multi-provider LLM support**: OpenAI, Anthropic/Claude, Gemini, Groq, DeepSeek, MiniMax, OpenRouter, local Ollama
- **100+ data connectors**: DBnomics, Polygon, Kraken, Yahoo Finance, FRED, IMF, World Bank, AkShare
- **18 quantitative modules** via QuantLib: DCF, portfolio optimization, VaR, Sharpe
- **16 broker integrations**: IBKR, Alpaca, Zerodha, Saxo, plus crypto via Kraken/HyperLiquid WebSocket
- **MCP node editor** for automation pipeline authoring — explicit MCP tool integration mentioned
- Embedded Python for analytics computations

## Licensing

Dual: AGPL-3.0 (open-source) + commercial license. University pricing $799/month for 20 accounts.

## Relevance to Jason's Work

- **Fairford PoC**: The 37-agent investor persona architecture is a direct reference pattern for the Fairford signal generation layer — each persona = a specialized bi-agent variant querying Fabric data.
- **fabric-mcp gap**: No Fabric/Power BI connector exists — the node editor + MCP integration is an obvious insertion point for fabric-mcp as a data source node.
- **bi-agent complement**: FinceptTerminal handles portfolio analytics; bi-agent handles NL→DAX over Fabric models — combining them closes the analytics → BI reporting loop.
- **FinRL-Trading parallel**: Both are agentic quant platforms; FinceptTerminal is the richer UI/terminal layer, FinRL-Trading is the pure algorithmic execution layer. They're composable, not competing.
- The explicit MCP integration in the node editor validates the fabric-mcp abstraction pattern as the right integration surface.
