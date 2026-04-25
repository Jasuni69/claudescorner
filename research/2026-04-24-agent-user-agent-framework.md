---
title: "What's Missing in the Agentic Story — User Agent Framework"
date: 2026-04-24
source: https://www.mnot.net/blog/2026/04/24/agents_as_collective_bargains
author: Mark Nottingham (IETF Chair)
tags: [ai-agents, governance, trust, mcp, standards, dispatch]
signal: high
---

# What's Missing in the Agentic Story

**Source:** mnot.net — Mark Nottingham (IETF Chair / former W3C TAG)
**HN points:** 2 (early; Nottingham is high-credibility, low-viral)
**Date clipped:** 2026-04-24

## Core Argument

AI agents lack the **standardized user-agent trust framework** that makes browsers trustworthy intermediaries between users and services. Without W3C/IETF-style standards that embed checks and balances on both parties, agentic AI will either sprawl as opaque untrustworthy tools or get locked inside proprietary platforms.

## Key Technical Points

1. **Missing user-agent role**: Browsers operate within W3C/IETF standards that constrain how sites can use user data. Agents have no equivalent — "the agent could be doing *anything*" with data it retrieves. No standardized behavioral expectations exist.

2. **Trust asymmetry**: Data providers can't trust agents. Unlike browsers which provide "rough guide rails around how a Web site's data is used," agents offer no verifiable constraints — the same gap CrabTrap + AgentKey are patching locally.

3. **Permission model is architectural, not policy**: If agents can request arbitrary permissions, constant permission-bugging is guaranteed regardless of policy. The problem must be solved at the protocol/standard layer, not per-agent config.

4. **Legibility gap**: Users can't form mental models of agent behavior the way they can for browsers. This is a prerequisite for trust at scale.

## Actionable Signal for ClaudesCorner

- **Validates AgentKey + CrabTrap + AgentRQ stack**: The local governance stack (identity + outbound filtering + human escalation) is the right pattern while standards are absent — exactly what Nottingham argues needs to exist at the protocol level.
- **dispatch.py worker scope**: `deny:` frontmatter in worker system prompts is a first-order implementation of "standardized tool constraints." The pattern is architecturally correct.
- **ENGRAM positioning**: A portable agent harness with explicit permission boundaries (SOUL.md + deny: clauses) is a pre-standards implementation of what Nottingham says must exist. This is an ENGRAM README framing opportunity.
- **Fairford implication**: Enterprise customers (Fairford) will eventually require formal agent governance. Building it now via AgentKey + CrabTrap + FABRIC_CALLER_TOKEN bearer check positions ahead of the compliance curve.

## Quote

> "Without a well-defined user agent role backed up by transparent, public standards that embed checks and balances on both parties, we're pretty much guaranteed a world where agents constantly bug us for permissions."
