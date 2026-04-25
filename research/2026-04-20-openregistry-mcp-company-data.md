---
title: "OpenRegistry — MCP Server for 27 National Company Registries"
source: https://github.com/sophymarine/openregistry
clipped: 2026-04-20
hn_points: 1
tags: [mcp, kyc, fairford, company-data, fabric, due-diligence]
---

# OpenRegistry — MCP for Global Company Registry Search

**Source:** https://github.com/sophymarine/openregistry  
**HN:** https://news.ycombinator.com/newest (2026-04-20, Show HN)  
**MCP endpoint:** `https://openregistry.sophymarine.com/mcp`

## What It Does

Free remote MCP server giving AI agents real-time read access to **27 national company registries** via a single OAuth 2.1 authenticated endpoint. No pre-shared API keys. Compatible with Claude Code, Claude Desktop, Cursor, Cline, and any MCP client.

## Registries Covered

- UK Companies House
- France RNE/INSEE
- Germany Handelsregister
- Italy InfoCamere (EU BRIS)
- Spain BORME
- Poland KRS
- Korea OpenDART
- Canada CBCA
- 10 US state registries

## Technical Design

- Returns **unmodified government registry responses** — field names, status values, and raw filing bytes (XHTML iXBRL / PDF / XBRL) preserved exactly as emitted by each government system
- Jurisdiction identifiers + company IDs included, enabling reconstruction of official government URLs for audit trails
- Enterprise tier adds synthesized `source_url`, `registry_url`, `data_license` fields
- Auth: OAuth 2.1, no API keys required at free tier

## Use Cases

- KYC and cross-border due diligence
- Beneficial ownership chain mapping
- Director screening and PEP identification
- Company financial data retrieval (XBRL/iXBRL)
- AML compliance and shell company detection
- Competitor intelligence

## Relevance to ClaudesCorner

- **Fairford Holdings PoC**: direct drop-in for the KYC/due-diligence signal layer — agents can query beneficial ownership chains across 7 EU jurisdictions + UK + US without scraping; fabric-mcp can pipe results into Fabric lakehouses
- **fabric-mcp**: OpenRegistry → fabric-mcp → Power BI = full compliance reporting pipeline; no custom scraping needed
- **bi-agent**: NL query → OpenRegistry MCP → DAX → Fabric report is a complete Fairford workflow
- **dispatch.py**: can spawn a worker that does `openregistry.search(company_name)` as a pre-filter for any investment/counterparty task
- Gap: free tier lacks `source_url` audit field — enterprise tier needed for Fairford compliance use (audit trails required)
