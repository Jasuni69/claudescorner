---
title: "tradingview-mcp — AI Trading Intelligence MCP Server for Claude"
date: 2026-04-16
source: https://github.com/atilaahmettaner/tradingview-mcp
tags: [mcp, claude-desktop, trading, technical-analysis, financial-ai]
relevance: high
---

## Summary

An MCP server that turns Claude into a trading analyst. 30+ tools covering backtesting, real-time pricing, technical indicators, sentiment, news, and multi-exchange screening. No API keys required for core functionality.

## Tools Exposed

**Backtesting:**
- `backtest_strategy` — RSI, Bollinger Bands, MACD, EMA Cross, Supertrend, Donchian; returns Sharpe, Calmar, win rate, drawdown
- `compare_strategies` — ranks all six against a symbol

**Market Data:**
- `yahoo_price` — real-time quotes, 52-week range, market state
- `market_snapshot` — S&P 500, NASDAQ, VIX, crypto, FX

**Technical Analysis:**
- `get_technical_analysis` — 30+ indicators with BUY/SELL/HOLD signals
- `get_candlestick_patterns` — 15-pattern detector
- `get_multi_timeframe_analysis` — weekly → 15m alignment

**Sentiment + News:**
- `market_sentiment` — Reddit (r/stocks, r/crypto, r/investing) bullish/bearish scoring
- `financial_news` — Reuters, CoinDesk, CoinTelegraph RSS
- `combined_analysis` — merges technicals + sentiment + news

**Screening:**
- `screen_stocks` — 20+ filter criteria, multi-exchange
- `scan_by_signal` — oversold, trending, breakout

## Data Sources

Yahoo Finance, TradingView indicators, Reddit, RSS feeds, Binance/KuCoin/Bybit/MEXC, EGX (Egyptian Exchange).

## Claude Desktop Install

```json
{
  "mcpServers": {
    "tradingview": {
      "command": "/path/to/uvx",
      "args": ["--from", "tradingview-mcp-server", "tradingview-mcp"]
    }
  }
}
```

No API keys needed. MIT licensed.

## Notable Design Decisions

- **Six fixed strategies** — intentional scope limit; prevents analysis paralysis, ensures comparable backtests
- **Commission + slippage simulation** — realistic trading costs baked into backtesting
- **OpenClaw integration** — routes Telegram/WhatsApp/Discord through Claude → MCP server via Python wrapper
- Walk-forward validation and paper trading still on roadmap

## Relevance to Jason's Work

**Fairford/Clementine:** This is a drop-in Claude-native financial research layer. Could augment the Fabric KPI monitor — when a KPI threshold fires, an agent call to `combined_analysis` gives instant context (technicals + news + sentiment) without leaving Claude.

**Engram/MCP ecosystem:** Good reference implementation for how to structure a 30-tool MCP server with no-auth data sources. Pattern worth studying for any future Claude Code MCP work.

**Pairing with Kronos:** tradingview-mcp handles real-time signals and sentiment; Kronos handles forecast horizon. Together they form a complete signal stack callable from a single Claude session.

## Links

- GitHub: https://github.com/atilaahmettaner/tradingview-mcp
- Stars this week: ~475 (GitHub trending Python, 2026-04-16)
