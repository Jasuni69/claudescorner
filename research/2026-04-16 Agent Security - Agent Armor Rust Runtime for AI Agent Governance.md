---
title: "Agent Armor — Rust Runtime for AI Agent Governance"
date: 2026-04-16
source: https://github.com/EdoardoBambini/Agent-Armor-Iaga
tags: [agents, security, mcp, claude-code, governance, rust]
relevance: high
---

# Agent Armor — Rust Runtime for AI Agent Governance

## What It Is

Agent Armor is an open-core Rust runtime (built on Axum) that sits between AI agent frameworks and their tools, providing governance, auditing, and policy enforcement before any action executes. Written as an MCP proxy/server, it integrates directly with agent frameworks like Claude Code, LangChain, and CrewAI.

## Problem It Solves

As agents gain shell, filesystem, database, and API access, there is no governance layer controlling what they actually execute. Agent Armor fills this gap with an 8-layer pipeline that returns `allow`, `review`, or `block` on every agent action.

## Key Capabilities

- **8-layer governance pipeline**: deep packet inspection, taint analysis, identity verification, risk scoring, policy evaluation
- **Response security scanning**: detects leaked credentials and PII in tool outputs
- **Per-agent rate limiting** and behavioral fingerprinting
- **Threat intelligence integration** via webhook and SSE
- **Live operator dashboard**: audit browsing, review queues, runtime controls
- **Structured logging** with correlation IDs
- **Storage**: SQLite default, PostgreSQL optional

## MCP Integration

Runs as an MCP proxy/server — drop-in layer between Claude Code and its tools. 129 tests including live HTTP end-to-end verification.

## Relevance to Jason's Work

- Directly applicable to Claude Code sessions that touch production systems (Fabric, Clementine)
- Audit trail solves the "what did the agent actually do" problem
- MCP proxy mode means zero framework changes required
- Open-core: enterprise features (SSO, RBAC, SIEM) excluded from community release — monitor for paid tier

## Signal

v0.3.0 community release. Watch for adoption by openclaw/claude-code communities as agent surface area grows.