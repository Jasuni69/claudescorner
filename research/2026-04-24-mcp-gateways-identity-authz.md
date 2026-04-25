---
title: "MCP Gateways Aren't Enough — Agents Need Identity, Authorization, and Proof"
source: https://www.diagrid.io/blog/why-mcp-gateways-are-not-enough
date: 2026-04-24
tags: [mcp, security, identity, authorization, agents, spiffe, opa]
---

# MCP Gateways Aren't Enough — Agents Need Identity, Authorization, and Proof

**Source:** Diagrid Engineering Blog | HN newest (1pt at clip time — early signal)

## Core Argument

MCP gateways (routing + basic access control) leave three critical security gaps for enterprise AI agents:

1. **No cryptographic agent identity** — shared API keys cannot distinguish which agent made a call
2. **No zero-trust workflow authorization** — no mechanism to enforce deny-by-default per-tool policies
3. **No tamper-evident execution proof** — downstream services cannot verify that required approval steps occurred

## Proposed Architecture

### Layer 1: Agent Identity via SPIFFE
- Issue each agent a short-lived X.509 SVID (SPIFFE Verifiable Identity Document)
- Replaces shared API keys with per-agent cryptographic identity
- Enables attribution at the individual agent level, not just "the agent pool"

### Layer 2: Zero-Trust Authorization via OPA
- Deny-by-default policies: specify which agents can invoke which MCP tools
- Policy engine (Open Policy Agent) evaluates requests against signed identity + role
- Middleware hooks in MCP server for per-tool auth checks before execution

### Layer 3: Cryptographically Verifiable Workflow History
- Each workflow step appends a signed record to an execution chain
- Downstream tools receive the chain and verify required prior steps occurred
- Example: payment tool refuses to execute unless signed chain proves human approval happened upstream
- "Durable MCP tool calls" that survive failures and resume with intact proof chain

## Signal for ClaudesCorner

**Why this matters for dispatch.py:**
- dispatch.py workers currently have no cryptographic identity — they authenticate as "the Claude process" with an API key
- CrabTrap filters outbound calls but cannot verify *which worker* made them
- AgentKey adds identity + revocation but doesn't issue SPIFFE certs
- The "signed workflow history" pattern is the missing verify oracle at the infrastructure level — not just at the prompt level (current approach)

**Relationship to existing governance stack:**
```
Current:  AgentKey (identity) → CrabTrap (outbound) → AgentRQ (escalation)
Proposed: SPIFFE (crypto identity) → OPA (per-tool authz) → signed chain (proof)
```
The Diagrid model is more rigorous but heavier. For Fairford Phase 2, the signed execution chain matters most — payment/data-write tools need proof-of-approval.

**fabric-mcp relevance:**
- fabric-mcp currently has no per-tool authorization — any caller with the MCP connection can invoke any Fabric dataset
- Adding OPA middleware to fabric-mcp would enforce: "only bi-agent workers may call `query_dataset`, only after schema validation step signed"

**MCP gateway products mentioned:**
- Diagrid's own Conductor (MCP-native workflow engine) implements these patterns
- Compatible with any MCP server via middleware hooks — not Diagrid-specific

## Key Quote

> "Workflow history itself becomes a cryptographically verifiable input to authorization — not a log you inspect after the fact, but a live gate that upstream steps must have signed."

## Priority

**Medium** — architecturally correct but heavyweight for current ClaudesCorner scale. Revisit when ENGRAM goes multi-tenant or Fairford Phase 2 requires payment-adjacent tool calls.

**Immediate action:** Add note to fabric-mcp backlog to add per-caller scoping (even basic: env-var caller ID) before Fairford Phase 2.
