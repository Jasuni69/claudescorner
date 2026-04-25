---
title: "poly_data — Polymarket Trade Data Pipeline"
date: 2026-04-21
source: https://github.com/warproxxx/poly_data
tags: [polymarket, prediction-markets, alternative-data, fairford, fabric, kronos]
stars: 1382
weekly_gain: 487
license: GPL-3.0
---

# poly_data — Polymarket Trade Data Pipeline

**Repo:** warproxxx/poly_data (~1.4k stars, +487 this week) · GPL-3.0

## What it does

End-to-end data pipeline for Polymarket: fetches market metadata, scrapes order-filled events via Goldsky GraphQL subgraph, and transforms raw events into structured trade datasets.

## Key features

- **Resumable pipeline:** all stages checkpoint and resume automatically
- **Missing market discovery:** auto-detects and backfills markets absent from initial fetch
- **Error handling:** retries, rate-limit detection, graceful fallbacks
- **Stack:** Python + Polars + Pandas; GraphQL (Goldsky) + REST (Polymarket API)
- No agent/MCP layer yet

## Relevance to ClaudesCorner

| Angle | Detail |
|---|---|
| Fairford signal layer | Prediction-market order flow = alternative data signal; pairs with Kronos (OHLCV) + FinceptTerminal (37 investor-persona agents) + ai-hedge-fund (19-agent 3-tier) |
| fabric-mcp insertion | Polymarket trade data → Fabric lakehouse → bi-agent DAX queries over prediction-market sentiment |
| Structured + resumable | Pipeline design matches dispatch.py checkpoint pattern; direct code reference for long-running worker robustness |
| GPL-3.0 note | Cannot include verbatim in MIT-licensed ENGRAM; use as data source only, wrap with MIT adapter |

## Signal

> Polymarket order-flow pipeline with Goldsky GraphQL backend + Polars processing = structured prediction-market alternative data layer; completes the Kronos→prediction-market signal stack for Fairford Phase 2.

## Action items

- Evaluate as Fabric lakehouse data source alongside Kronos for Fairford PoC Phase 2
- Benchmark prediction-market sentiment vs OHLCV signal quality on backtested Fairford use case
- Note GPL-3.0: keep as external dependency, do not inline into ENGRAM
