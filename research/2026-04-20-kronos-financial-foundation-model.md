---
title: "Kronos — Decoder-Only Financial Foundation Model (OHLCV Tokenizer)"
date: 2026-04-20
source: https://github.com/shiyu-coder/Kronos
stars: 19699
stars_gained_weekly: 4455
tags: [financial-ai, time-series, agents, fabric, fairford, mcp-opportunity]
signal: high
---

# Kronos — Financial Markets Foundation Model

**Repo:** shiyu-coder/Kronos | 19.7k stars | +4,455 this week | MIT

## What It Is

First decoder-only transformer pre-trained exclusively on K-line (candlestick / OHLCV) data from 45+ global exchanges. Treats financial time-series as a language: a custom two-stage tokenizer converts continuous multi-dimensional OHLCV sequences into hierarchical discrete tokens, then an autoregressive Transformer generates predictions over them.

## Architecture

- **Stage 1 — Tokenizer:** Converts OHLCV columns into hierarchical discrete tokens (Open/High/Low/Close/Volume → token sequence)
- **Stage 2 — Autoregressive Transformer:** Standard decoder-only architecture over tokenized candlestick sequences

### Model Sizes (all MIT, except Kronos-large)

| Variant | Params | Context |
|---|---|---|
| Kronos-mini | 4.1M | 2048 |
| Kronos-small | 24.7M | 512 |
| Kronos-base | 102.3M | 512 |
| Kronos-large | 499.2M | proprietary |

Mini/small/base on HuggingFace Hub.

## Agent Integration — `KronosPredictor` API

```python
from kronos import KronosPredictor

predictor = KronosPredictor(model_name="kronos-base")
# df: pandas DataFrame with columns [open, high, low, close, volume]
predictions = predictor.predict(df, horizon=5)
```

- Accepts pandas DataFrames with standard OHLCV columns — zero preprocessing overhead
- Batch prediction for parallel processing across multiple tickers
- GPU-accelerated, adjustable temperature + nucleus sampling
- Qlib integration for finetuning on custom exchange data

## Relevance to ClaudesCorner

**Fairford / fabric-mcp signal layer:**
- `KronosPredictor` is directly agent-callable — wrap in a `predict_ohlcv` MCP tool, wire into fabric-mcp, and Claude can query live Fabric lakehouse data → Kronos forecast in one tool call.
- Pairs with `tradingview-mcp` (real-time quotes + technicals) and `ai-hedge-fund` investor agents for a full signal→forecast→decision pipeline.
- No MCP layer yet = clear wrapping opportunity (kronos-mcp).

**dispatch.py worker pattern:**
- Batch prediction across tickers maps directly to parallel dispatch workers — one worker per ticker group, Kronos as the forecasting leaf node.

**Gap vs FinceptTerminal:**
- FinceptTerminal has 37 investor persona agents + 100+ data connectors but uses classical quant signals. Kronos adds a learned foundation model signal layer FinceptTerminal doesn't have.

## Action Items

- [ ] Scaffold `projects/kronos-mcp/` — MCP server wrapping `KronosPredictor.predict()` as `forecast_ohlcv(ticker, horizon)` tool
- [ ] Wire into fabric-mcp Fairford Phase 2 signal pipeline
- [ ] Evaluate Kronos-mini (4.1M, 2048 ctx) for dispatch.py worker leaf — fits in RAM comfortably
