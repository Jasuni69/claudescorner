---
title: "Agent Vault — Open-Source Credential Proxy for AI Agents"
source: https://github.com/Infisical/agent-vault
hn: https://news.ycombinator.com/item?id=43803000
date: 2026-04-24
points: 61
tags: [agents, security, credentials, dispatch, infisical]
---

# Agent Vault — Open-Source Credential Proxy for AI Agents

**Source:** GitHub (Infisical) | HN #10 today, 61 pts | 20 comments

## Summary

Agent Vault is an open-source HTTP credential proxy that sits between AI agents and the APIs they call. Instead of giving agents direct access to secrets, it injects credentials at the network layer — agents connect via a local HTTP proxy endpoint, and Agent Vault rewrites requests with the appropriate secrets before forwarding them. Credentials are encrypted at rest with AES-256-GCM. All requests are logged with a full audit trail.

Built by Infisical (the open-source secrets management platform). Written in Go + TypeScript. 363 GitHub stars at time of clip.

## Architecture

- Agents point `HTTP_PROXY` / `HTTPS_PROXY` to Agent Vault's local endpoint
- No code changes required in agents — works with Claude Code, Cursor, custom Python/TS scripts, any HTTP-based agent
- Credentials stored encrypted (AES-256-GCM), never exposed in plaintext to agents
- Request log captures: agent ID, timestamp, target URL, injected credential ID — enables revocation auditing
- Self-hostable, MIT-adjacent license

## Signal for ClaudesCorner

**Relationship to existing stack:**
- Complements AgentKey (identity layer) with a different architectural approach: network proxy vs. identity certificate
- AgentKey = who the agent is; Agent Vault = what secrets it can use
- CrabTrap = what it can call outbound; Agent Vault = with what credentials
- Together: AgentKey (identity) + Agent Vault (credential injection) + CrabTrap (outbound filtering) + AgentRQ (escalation) = complete dispatch.py worker governance stack

**Immediate applicability:**
- dispatch.py workers currently carry credentials via environment variables — Agent Vault would remove secrets from the process environment entirely
- The `HTTP_PROXY` injection model is zero-code for dispatch.py workers (CrabTrap already uses this pattern)
- Audit log fills the "which worker called which API with which key" gap not covered by CrabTrap's URL-level log

**Gap vs AgentKey:**
- Agent Vault does not issue cryptographic agent identity (no SPIFFE/X.509)
- AgentKey handles revocation UX + tool catalog; Agent Vault handles the actual secret injection
- Both needed; neither replaces the other

## Action Items

- [ ] Evaluate combining Agent Vault + CrabTrap as a two-layer proxy stack: Agent Vault injects creds, CrabTrap filters destinations
- [ ] Check if Agent Vault supports per-worker credential scoping (different API keys per dispatch.py worker tier)
- [ ] Monitor Infisical's MCP integration roadmap — they already have secrets MCP in main Infisical product
