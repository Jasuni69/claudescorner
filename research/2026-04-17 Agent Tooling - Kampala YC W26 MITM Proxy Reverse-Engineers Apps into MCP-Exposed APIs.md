---
title: "Kampala (YC W26) — MITM Proxy That Reverse-Engineers Apps into MCP-Exposed APIs"
date: 2026-04-17
source: https://www.zatanna.ai/kampala
hn: https://news.ycombinator.com/item?id=47794514
hn_points: 69
tags: [mcp, agent-tooling, reverse-engineering, proxy, automation]
relevance: mcp-tools, agent-access, legacy-integration
---

## Summary

Kampala is a man-in-the-middle proxy that intercepts network traffic from websites, mobile apps, and desktop apps — then generates runnable APIs or MCP-exposed tools from the captured calls. Built by YC W26 batch.

## How It Works

1. MITM proxy captures HTTP/2, WebSocket, gRPC traffic without modifying TLS/HTTP2 fingerprints
2. Leverages existing session tokens and anti-bot cookies — avoids browser automation fragility
3. Two generation paths:
   - **Agent-driven**: describe the workflow in a prompt → Kampala generates the script
   - **Manual record**: record workflow manually → AI generates code from the capture
4. Exports as runnable APIs or hosts them directly
5. **MCP interface**: manually recorded workflows auto-expose as MCP tool actions → Claude Code can call them directly

## Use Cases

- Legacy dashboard reconciliation (insurance payer systems, property management billing)
- Internal integration workflows where no official API exists
- Enterprise automation without scraping risk

## HN Signal

- Top comment: "Downloaded the network tab as a HAR file, asked Claude to analyze and document the APIs as an OpenAPI JSON. Worked amazing." — suggests the DIY path is already viable for simple cases; Kampala's value is the live session token reuse + MCP wrapping
- **Limitations noted**: SSL pinning breaks mobile apps; session re-auth mid-script is the main bottleneck; HTTP/3 + TCP fingerprinting not yet supported

## Relevance to Jason's Work

- **MCP gap-filler**: any internal tool (Fabric portal, Power BI admin, legacy ERP) with no public API becomes an MCP-callable tool via one recorded session
- **bi-agent**: could expose Power BI dataset refresh / workspace management endpoints that aren't in the REST API docs
- **Clementine / Fairford**: legacy insurance/finance systems are exactly Kampala's stated target market
- Watch: MCP interface means Claude Code can use Kampala-generated tools without custom SDK work
