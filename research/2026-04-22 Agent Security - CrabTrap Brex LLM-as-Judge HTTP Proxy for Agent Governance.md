---
title: "CrabTrap: LLM-as-Judge HTTP Proxy for Agent Governance"
date: 2026-04-22
source: https://www.brex.com/crabtrap
github: https://github.com/brexhq/CrabTrap
hn: https://news.ycombinator.com/item?id=47850212
hn_points: 26
tags: [agent-security, mcp, dispatch, governance, proxy]
relevance: high
---

# CrabTrap — LLM-as-Judge HTTP Proxy for Agent Governance

**Brex Engineering | MIT License | Go (78%) + TypeScript (19%) | HN 26pts**

## What It Is

CrabTrap is an open-source transparent MITM forward proxy that sits between an AI agent and any external API. Every outbound HTTP/HTTPS request is intercepted, evaluated against a policy, and either forwarded or blocked — in real time, before execution.

Agents connect to it via standard `HTTP_PROXY` / `HTTPS_PROXY` environment variables. No agent code changes required.

## How the LLM-as-Judge Works

Two-tier evaluation:

1. **Static rules first** — URL patterns (prefix / exact / glob); deny rules take priority. Fast, zero-LLM-cost path.
2. **LLM judge for unmatched requests** — natural-language policy is JSON-escaped and the request payload is JSON-encoded before evaluation. Configurable fallback mode (deny or passthrough) if the judge is unavailable. Circuit breaker trips after 5 consecutive LLM failures; reopens after 10s.

All decisions (and whether they came from a rule or the LLM) are logged to PostgreSQL for audit trail.

## What It Catches

- **SSRF**: blocks RFC 1918 private networks, loopback, link-local, IPv6 special ranges; DNS-rebinding prevention baked in.
- **Prompt injection**: payloads JSON-encoded before passing to the judge, policy content JSON-escaped — limits injection surface.
- **Rate abuse**: per-IP token bucket (default 50 req/s, burst 100).

## Architecture

- TLS termination with dynamically generated per-host certificates from a managed CA.
- React web UI for policy management and audit log review.
- PostgreSQL backend for audit persistence.
- Not a WAF — outbound only; does not inspect inbound traffic or response bodies.
- No WebSocket frame inspection (only the upgrade request is evaluated).
- No redaction — sees cleartext including Authorization headers; trust boundary is the proxy itself.

## Notable Design Decisions

- **No human approval loop** — fully automated rule + LLM decisions. Complement with AgentRQ for escalation.
- **Response pass-through** — requests evaluated, responses are not. Gap for data-exfiltration scenarios.
- Two-tier avoids LLM latency on common patterns; judge only fires on edge cases.

## Relevance to ClaudesCorner

| Gap | CrabTrap Coverage |
|-----|-------------------|
| dispatch.py outbound governance | ✅ Drop `HTTP_PROXY=crabtrap` into worker env |
| AgentKey covers identity | CrabTrap covers request-level policy enforcement |
| bi-agent DAX API calls | ✅ Natural-language policy: "only call Fabric endpoints" |
| SSRF risk in fabric-mcp | ✅ RFC 1918 blocking baked in |
| Audit trail for worker actions | ✅ PostgreSQL log of every outbound call |

CrabTrap fills the outbound-request governance gap between AgentKey (identity) and AgentRQ (escalation). Together they form a three-layer agent governance stack: identity → request-level policy → human escalation.

## Action

Wire CrabTrap as `HTTP_PROXY` in dispatch.py worker subprocess env. Write a natural-language policy scoped to Fabric/Claude API endpoints only. PostgreSQL audit log feeds into kpi-monitor alert surface.
