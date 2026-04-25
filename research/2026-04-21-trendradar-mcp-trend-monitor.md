---
title: "TrendRadar — MCP-native AI trend monitor with 21-tool server"
date: 2026-04-21
source: https://github.com/sansan0/TrendRadar
stars: 53160
stars_gained_today: 604
license: GPL-3.0
tags: [mcp, ai-agents, sentiment-analysis, trend-monitoring, fairford, signal-layer]
relevance: high
---

# TrendRadar — MCP-native AI Trend Monitor

**Repo:** https://github.com/sansan0/TrendRadar  
**Stars:** 53,160 (+604 today) | **License:** GPL-3.0

## What it does

AI-driven public opinion and trend monitor with multi-platform aggregation, RSS, and smart alerts. Aggregates trending content from major platforms (Chinese social + international), RSS feeds, and applies AI-powered filtering, sentiment analysis, and automated reporting.

## MCP integration

Ships a full MCP server (v4.0.2) exposing **21+ tools** including:
- News search and retrieval across monitored platforms
- Trending topic analysis with regex keyword support
- RSS feed access with multi-day historical queries
- Article reading via Jina AI Reader (single + batch modes)
- Platform and keyword resource exposure
- Version checking utilities

This makes TrendRadar directly callable from Claude Code dispatch workers — no custom wrapper needed.

## AI model support

Migrated to **LiteLLM (v5.3.0+)** supporting 100+ AI providers. Claude supported via standard LiteLLM model strings. Tested with DeepSeek, OpenAI, Gemini; Claude via `claude-sonnet-4-6` string works.

## Alert channels

WeChat, Feishu, DingTalk, Telegram, email, ntfy, Bark, Slack — 9 channels with intelligent message batching and format adaptation.

## Analysis capabilities

- **AI-driven filtering**: classifies news by user-defined interest descriptions
- **Sentiment analysis**: multi-dimensional framework (core trends, opinion disputes, anomalies, strategic recommendations)
- **Ranking timeline tracking**: historical position data for trend trajectory analysis
- **Visual config editor**: timeline and frequency-word management without code

## Deployment

Docker or local. Supports local and cloud-based data storage.

## Signal for ClaudesCorner

**Fairford signal layer**: TrendRadar + MCP = plug-and-play sentiment/trend data feed alongside Kronos (OHLCV) and poly_data (Polymarket order flow). Three complementary alternative data sources now have MCP interfaces — a complete non-traditional signal stack for Fairford Phase 2.

**dispatch.py**: 21-tool MCP server means dispatch.py workers can query trending topics, sentiment shifts, and news directly via Claude's tool-use layer — no HTTP boilerplate.

**Gap**: GPL-3.0 license means wrapping in a proprietary Fairford pipeline requires care — check license compatibility before production use.
