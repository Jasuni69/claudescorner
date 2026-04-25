---
title: "Could a Claude Code Routine Watch My Finances?"
date: 2026-04-24
source: https://driggsby.com/blog/claude-code-routine-watch-my-finances
hn_points: 18
tags: [claude-code, routines, MCP, automation, financial, scheduling]
relevance: [dispatch.py, fabric-mcp, kpi-monitor, MCP pattern]
---

## Summary

Author built a daily financial monitoring agent using Claude Code routines + a custom MCP server (Driggsby, 75k lines of Rust) backed by Plaid for live account data. The routine runs on a schedule, aggregates balances and transactions, and drafts a Gmail digest — zero deployment infrastructure required. Just a prompt + MCP connectors + a scheduled execution time.

## Architecture

```
Plaid (financial data)
  └─► Driggsby MCP server (Rust, exposes balances/transactions/investments as tools)
        └─► Claude Code routine (scheduled natural-language prompt)
              └─► Gmail connector (draft creation)
```

## What Worked

- Daily digest of account balances and net worth formatted correctly
- Transaction anomaly detection: double-charges, subscription price changes identified
- Routine runs appear as normal Claude sessions — fully inspectable and debuggable
- "Almost too easy to set up" — prompt + connector + schedule time

## What Didn't Work

- Gmail connector creates drafts only, cannot send directly
- Codex CLI alternative broke on rendering quirks and 2FA prompts
- GPT-based formatting was inconsistent across runs

## Signal for ClaudesCorner

**Consumer-scale validation of dispatch.py pattern.** One-prompt-one-session-one-task with scheduled execution is exactly the dispatch.py worker model — confirmed independently by a production personal-finance use case. The inspectability point (routine = normal Claude session) is the key UX insight: no separate monitoring UI needed.

**kpi-monitor upgrade path.** The Driggsby pattern — expose domain data as MCP tools, trigger anomaly-detection via scheduled Claude routine — is a cleaner architecture than kpi-monitor's direct Python polling loop. If kpi-monitor needs a Claude-powered analysis layer, this is the template.

**MCP as the zero-infra automation primitive.** The author's main insight: "if you can expose data and tools through MCP cleanly, you can orchestrate complex workflows through simple natural language prompts." This directly validates fabric-mcp — the Fabric data layer exposed as MCP tools enables the same pattern for BI/analytics monitoring.

**Alert fatigue problem identified.** The next challenge isn't technical — it's prompt refinement to avoid over-alerting. Same issue dispatch.py workers face with verbose output gates.
