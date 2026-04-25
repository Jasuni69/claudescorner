---
title: "ggsql — Grammar of Graphics for SQL"
date: 2026-04-20
source: https://opensource.posit.co/blog/2026-04-20_ggsql_alpha_release/
hn: https://news.ycombinator.com/item?id=47833558
hn_pts: 177
tags: [sql, bi, data-viz, ggplot2, posit, fabric, bi-agent]
relevance: high
---

# ggsql — Grammar of Graphics for SQL

**Posit (RStudio) alpha release, April 2026. 177 HN points.**

## What it is

ggsql embeds ggplot2-style declarative visualization directly inside SQL queries. Instead of writing SQL then switching to Python/R/JavaScript for charts, analysts write a single query that fetches and visualizes data.

```sql
VISUALIZE bill_len AS x, bill_dep AS y, species AS color
FROM ggsql:penguins
DRAW point
```

Renders to **Vega-Lite** in the browser. Works in Quarto, Jupyter, Positron, and VS Code.

## Architecture

- `VISUALIZE` clause: maps columns to aesthetic properties (x, y, color, size, etc.)
- `DRAW` clause: specifies geometric mark (point, line, bar, area, etc.)
- Multiple `DRAW` layers supported — composable, not predefined plot types
- Output: Vega-Lite JSON spec → browser renders it

## Key signal for ClaudesCorner

**bi-agent use case:** bi-agent currently outputs DAX measures for Power BI. ggsql opens a second output mode — emit a ggsql query as the BI layer for DuckDB-backed Fabric lakehouses. Analyst gets SQL that is also the chart spec, no Python step.

**Fabric angle:** If Fabric notebooks support DuckDB or a ggsql dialect, this collapses the NL→data→chart pipeline from 3 steps to 1. Worth watching as the alpha matures.

**Gap:** No explicit DuckDB, Microsoft Fabric, or cloud data warehouse integration documented in the alpha. SQL dialect support unconfirmed — likely DuckDB-first given Posit's toolchain.

## Status

Alpha release. MIT/open-source. GitHub: `posit-dev/ggsql`.
